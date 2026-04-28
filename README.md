# 🤖 OCI ARM Instance Hunter

[🇰🇷 한국어](#-한국어) | [🇺🇸 English](#-english) | [🇯🇵 日本語](#-日本語) | [🇨🇳 简体中文](#-简体中文)

---

## 🇰🇷 한국어

Oracle Cloud 무료 티어 **Ampere A1 ARM 인스턴스** (4 OCPU / 24GB RAM) 를  
"Out of Capacity" 오류가 사라질 때까지 **GitHub Actions가 5분마다 자동 재시도**하는 도구입니다.

### 🏗 동작 방식
```
GitHub Actions (cron: */5 * * * *)
  └─ src/hunter.py 실행
       ├─ OCI API로 ARM 인스턴스 생성 시도
       ├─ Out of Capacity → 5분 뒤 재시도 (다음 Actions 실행)
       └─ 성공 → 알림 전송 + Workflow 자동 비활성화
```

### 📋 사전 준비
1. **OCI API 키 생성**: OCI 콘솔 -> 프로파일 -> API 키 추가 후 `.pem` 파일 저장.
2. **OCID 수집**: Tenancy, User, Compartment, Subnet, Image(Ubuntu ARM) OCID 수집.
3. **SSH 키**: 서버 접속을 위한 SSH 공개키 준비.

### 🚀 GitHub 설정
1. 이 저장소를 **Fork** 또는 **Clone** 후 Push 합니다.
2. **Settings > Secrets and variables > Actions**에서 아래 값들을 등록합니다:
   - `OCI_TENANCY_OCID`, `OCI_USER_OCID`, `OCI_FINGERPRINT`, `OCI_PRIVATE_KEY` (PEM 내용)
   - `OCI_REGION`, `OCI_COMPARTMENT_ID`, `OCI_AD`, `OCI_SUBNET_ID`, `OCI_IMAGE_ID`
   - `OCI_SSH_PUBLIC_KEY`, `OCI_INSTANCE_NAME`
3. **Actions** 탭에서 Workflow를 활성화(Enable)합니다.

---

## 🇺🇸 English

A tool that automatically retries creating an **Oracle Cloud Free Tier Ampere A1 ARM Instance** (4 OCPU / 24GB RAM) using **GitHub Actions every 5 minutes** until the "Out of Capacity" error is resolved.

### 🏗 How it Works
```
GitHub Actions (cron: */5 * * * *)
  └─ Run src/hunter.py
       ├─ Attempt to create ARM instance via OCI API
       ├─ Out of Capacity → Retry in 5 mins (Next Action run)
       └─ Success → Send notification + Auto-disable workflow
```

### 📋 Prerequisites
1. **Create OCI API Key**: OCI Console -> Profile -> API Keys -> Add API Key and save the `.pem` file.
2. **Collect OCIDs**: Collect OCIDs for Tenancy, User, Compartment, Subnet, and Image (Ubuntu ARM).
3. **SSH Key**: Prepare an SSH public key for instance access.

### 🚀 GitHub Setup
1. **Fork** or **Clone** this repository and push to your own.
2. Register the following in **Settings > Secrets and variables > Actions**:
   - `OCI_TENANCY_OCID`, `OCI_USER_OCID`, `OCI_FINGERPRINT`, `OCI_PRIVATE_KEY` (PEM content)
   - `OCI_REGION`, `OCI_COMPARTMENT_ID`, `OCI_AD`, `OCI_SUBNET_ID`, `OCI_IMAGE_ID`
   - `OCI_SSH_PUBLIC_KEY`, `OCI_INSTANCE_NAME`
3. **Enable** the workflow in the **Actions** tab.

---

## 🇯🇵 日本語

Oracle Cloud 無料ティアの **Ampere A1 ARM インスタンス** (4 OCPU / 24GB RAM) を、  
"Out of Capacity" エラーが解消されるまで **GitHub Actions が 5 分ごとに自動再試行**して作成するツールです。

### 🏗 動作原理
```
GitHub Actions (cron: */5 * * * *)
  └─ src/hunter.py を実行
       ├─ OCI API で ARM インスタンス作成を試行
       ├─ Out of Capacity → 5 分後に再試行 (次の Actions 実行)
       └─ 成功 → 通知送信 + ワークフローの自動無効化
```

### 📋 事前準備
1. **OCI API キーの作成**: OCI コンソール -> プロファイル -> API キー -> API キーの追加、`.pem` ファイルを保存。
2. **OCID の収集**: テ넌シー、ユーザー、コンパートメント、サブネット、イメージ (Ubuntu ARM) の OCID を取得。
3. **SSH キー**: インスタンス接続用の SSH 公開鍵を用意。

### 🚀 GitHub 設定
1. このリポジトリを **Fork** または **Clone** してプッシュします。
2. **Settings > Secrets and variables > Actions** で以下の値を登録します:
   - `OCI_TENANCY_OCID`, `OCI_USER_OCID`, `OCI_FINGERPRINT`, `OCI_PRIVATE_KEY` (PEM の内容)
   - `OCI_REGION`, `OCI_COMPARTMENT_ID`, `OCI_AD`, `OCI_SUBNET_ID`, `OCI_IMAGE_ID`
   - `OCI_SSH_PUBLIC_KEY`, `OCI_INSTANCE_NAME`
3. **Actions** タブでワークフローを有効化 (Enable) します。

---

## 🇨🇳 简体中文

这是一个使用 **GitHub Actions 每 5 分钟自动重试** 的工具，用于创建 Oracle Cloud 免费层级 **Ampere A1 ARM 实例** (4 OCPU / 24GB RAM)，直到解决 "Out of Capacity" 错误。

### 🏗 工作原理
```
GitHub Actions (cron: */5 * * * *)
  └─ 运行 src/hunter.py
       ├─ 通过 OCI API 尝试创建 ARM 实例
       ├─ Out of Capacity → 5 分钟后重试（下次 Action 运行）
       └─ 成功 → 发送通知 + 自动禁用工作流
```

### 📋 准备工作
1. **创建 OCI API 密钥**: OCI 控制台 -> 个人资料 -> API 密钥 -> 添加 API 密钥并保存 `.pem` 文件。
2. **收集 OCID**: 收集租户、用户、区间、子网和镜像 (Ubuntu ARM) 的 OCID。
3. **SSH 密钥**: 准备用于访问实例的 SSH 公钥。

### 🚀 GitHub 设置
1. **Fork** 或 **Clone** 此仓库并推送到您自己的仓库。
2. 在 **Settings > Secrets and variables > Actions** 中注册以下内容：
   - `OCI_TENANCY_OCID`, `OCI_USER_OCID`, `OCI_FINGERPRINT`, `OCI_PRIVATE_KEY` (PEM 内容)
   - `OCI_REGION`, `OCI_COMPARTMENT_ID`, `OCI_AD`, `OCI_SUBNET_ID`, `OCI_IMAGE_ID`
   - `OCI_SSH_PUBLIC_KEY`, `OCI_INSTANCE_NAME`
3. 在 **Actions** 选项卡中启用 (Enable) 工作流。
