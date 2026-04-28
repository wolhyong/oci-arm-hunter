#!/usr/bin/env python3
"""
OCI ARM Instance Hunter
Oracle Cloud 무료 티어 ARM (Ampere A1) 인스턴스 자동 생성 스크립트
Capacity가 생길 때까지 자동으로 재시도합니다.
"""

import oci
import time
import os
import json
import logging
import sys
from datetime import datetime

# ─── 로깅 설정 ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("hunter.log", encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)


# ─── 설정 로드 ─────────────────────────────────────────────────────────────────
def load_config() -> dict:
    """환경 변수 또는 config.json에서 설정을 읽습니다."""
    # GitHub Actions Secrets → 환경 변수 우선
    cfg = {
        "tenancy_ocid":       os.environ.get("OCI_TENANCY_OCID", ""),
        "user_ocid":          os.environ.get("OCI_USER_OCID", ""),
        "fingerprint":        os.environ.get("OCI_FINGERPRINT", ""),
        "private_key":        os.environ.get("OCI_PRIVATE_KEY", ""),   # PEM 전체 내용
        "region":             os.environ.get("OCI_REGION", "ap-chuncheon-1"),
        "compartment_id":     os.environ.get("OCI_COMPARTMENT_ID", ""),
        "availability_domain":os.environ.get("OCI_AD", ""),            # 예) gDUK:AP-CHUNCHEON-1-AD-1
        "subnet_id":          os.environ.get("OCI_SUBNET_ID", ""),
        "image_id":           os.environ.get("OCI_IMAGE_ID", ""),      # Canonical Ubuntu ARM 이미지 OCID
        "ssh_public_key":     os.environ.get("OCI_SSH_PUBLIC_KEY", ""),
        # 인스턴스 스펙
        "instance_name":      os.environ.get("OCI_INSTANCE_NAME", "arm-free-instance"),
        "shape":              os.environ.get("OCI_SHAPE", "VM.Standard.A1.Flex"),
        "ocpus":              int(os.environ.get("OCI_OCPUS", "4")),
        "memory_gb":          int(os.environ.get("OCI_MEMORY_GB", "24")),
        "boot_volume_gb":     int(os.environ.get("OCI_BOOT_VOLUME_GB", "50")),
        # 재시도 설정
        "retry_interval_sec": int(os.environ.get("RETRY_INTERVAL_SEC", "60")),
        "max_retries":        int(os.environ.get("MAX_RETRIES", "0")),   # 0 = 무제한
        # 알림 (선택)
        "ntfy_topic":         os.environ.get("NTFY_TOPIC", ""),          # ntfy.sh 토픽
        "telegram_token":     os.environ.get("TELEGRAM_TOKEN", ""),
        "telegram_chat_id":   os.environ.get("TELEGRAM_CHAT_ID", ""),
    }

    # 로컬 개발: config.json 폴백
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "config.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            file_cfg = json.load(f)
        for k, v in file_cfg.items():
            if not cfg.get(k):   # 환경 변수가 없을 때만 덮어씀
                cfg[k] = v

    return cfg


# ─── OCI 클라이언트 생성 ────────────────────────────────────────────────────────
def build_oci_config(cfg: dict) -> dict:
    """OCI SDK config dict 반환. private key는 임시 파일 사용."""
    import tempfile

    key_file = None
    if cfg["private_key"]:
        # 환경 변수로 PEM 내용이 통째로 들어온 경우
        key_content = cfg["private_key"].replace("\\n", "\n")
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pem", mode="w")
        tmp.write(key_content)
        tmp.close()
        key_file = tmp.name
    else:
        key_file = os.path.expanduser("~/.oci/oci_api_key.pem")

    return {
        "tenancy": cfg["tenancy_ocid"],
        "user":    cfg["user_ocid"],
        "fingerprint": cfg["fingerprint"],
        "key_file": key_file,
        "region":  cfg["region"],
    }


# ─── 인스턴스 생성 시도 ─────────────────────────────────────────────────────────
def try_launch(compute_client: oci.core.ComputeClient, cfg: dict) -> bool:
    """
    인스턴스 생성을 한 번 시도합니다.
    성공 시 True, Out-of-Capacity면 False, 기타 예외는 재발생.
    """
    details = oci.core.models.LaunchInstanceDetails(
        availability_domain=cfg["availability_domain"],
        compartment_id=cfg["compartment_id"],
        display_name=cfg["instance_name"],
        shape=cfg["shape"],
        shape_config=oci.core.models.LaunchInstanceShapeConfigDetails(
            ocpus=cfg["ocpus"],
            memory_in_gbs=cfg["memory_gb"],
        ),
        source_details=oci.core.models.InstanceSourceViaImageDetails(
            image_id=cfg["image_id"],
            boot_volume_size_in_gbs=cfg["boot_volume_gb"],
        ),
        create_vnic_details=oci.core.models.CreateVnicDetails(
            subnet_id=cfg["subnet_id"],
            assign_public_ip=True,
        ),
        metadata={
            "ssh_authorized_keys": cfg["ssh_public_key"],
        },
        freeform_tags={"created_by": "oci-arm-hunter"},
    )

    try:
        resp = compute_client.launch_instance(details)
        log.info("✅ 인스턴스 생성 성공!")
        log.info("  OCID : %s", resp.data.id)
        log.info("  상태 : %s", resp.data.lifecycle_state)
        return True

    except oci.exceptions.ServiceError as e:
        if e.status == 500 and "Out of host capacity" in str(e.message):
            log.warning("⏳ 용량 부족 (Out of Capacity) — 재시도 대기 중...")
            return False
        elif e.status == 429:
            log.warning("⚠️  요청 한도 초과 (429) — 잠시 대기...")
            time.sleep(30)
            return False
        else:
            log.error("❌ 예상치 못한 OCI 오류: %s", e)
            raise


# ─── 알림 전송 ─────────────────────────────────────────────────────────────────
def notify(cfg: dict, message: str):
    """ntfy.sh / Telegram으로 성공 알림 전송."""
    import urllib.request
    import urllib.parse

    # ntfy.sh
    if cfg.get("ntfy_topic"):
        try:
            url = f"https://ntfy.sh/{cfg['ntfy_topic']}"
            req = urllib.request.Request(
                url, data=message.encode(), method="POST",
                headers={"Title": "OCI ARM 인스턴스 생성 완료 🎉"}
            )
            urllib.request.urlopen(req, timeout=10)
            log.info("📱 ntfy 알림 전송 완료")
        except Exception as ex:
            log.warning("ntfy 알림 실패: %s", ex)

    # Telegram
    if cfg.get("telegram_token") and cfg.get("telegram_chat_id"):
        try:
            text = urllib.parse.quote(f"🎉 OCI ARM 인스턴스 생성!\n{message}")
            url = (
                f"https://api.telegram.org/bot{cfg['telegram_token']}"
                f"/sendMessage?chat_id={cfg['telegram_chat_id']}&text={text}"
            )
            urllib.request.urlopen(url, timeout=10)
            log.info("📱 Telegram 알림 전송 완료")
        except Exception as ex:
            log.warning("Telegram 알림 실패: %s", ex)


# ─── 메인 루프 ─────────────────────────────────────────────────────────────────
def main():
    log.info("=" * 60)
    log.info("🤖 OCI ARM Instance Hunter 시작")
    log.info("=" * 60)

    cfg = load_config()

    # 필수 값 검증
    required = ["tenancy_ocid", "user_ocid", "fingerprint",
                "compartment_id", "availability_domain",
                "subnet_id", "image_id", "ssh_public_key"]
    missing = [k for k in required if not cfg.get(k)]
    if missing:
        log.error("❌ 필수 설정 누락: %s", missing)
        log.error("README.md를 참고해 환경 변수 또는 config.json을 설정하세요.")
        sys.exit(1)

    oci_config = build_oci_config(cfg)
    compute = oci.core.ComputeClient(oci_config)

    attempt     = 0
    max_retries = cfg["max_retries"]
    interval    = cfg["retry_interval_sec"]

    while True:
        attempt += 1
        log.info("─" * 40)
        log.info("시도 #%d  |  %s", attempt, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        success = try_launch(compute, cfg)
        if success:
            msg = f"시도 #{attempt} 만에 성공!\n{datetime.now()}"
            notify(cfg, msg)
            log.info("🏁 완료. 프로그램 종료.")
            sys.exit(0)

        if max_retries and attempt >= max_retries:
            log.error("최대 재시도 횟수(%d) 도달. 종료.", max_retries)
            sys.exit(2)

        log.info("⏱  %d초 후 재시도...", interval)
        time.sleep(interval)


if __name__ == "__main__":
    main()
