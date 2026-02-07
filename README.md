# etc-otp

데스크톱 멀티 사이트 TOTP(Time-based One-Time Password) 관리 프로그램입니다.
여러 사이트의 OTP를 하나의 앱에서 관리하고, 클릭 한 번으로 코드를 생성 및 복사할 수 있습니다.

---

## 주요 기능

- **OTP 생성 및 자동 복사** — 사이트를 클릭하면 OTP가 생성되고 클립보드에 자동 복사됩니다
- **만료 타이머** — OTP 유효 시간을 실시간으로 표시합니다
- **QR 코드 스캔** — 이미지 파일 또는 클립보드 이미지(`Ctrl+V`)에서 QR 코드를 인식하여 사이트를 추가합니다
- **사이트 관리** — 추가, 수정, 이름 변경, 삭제 기능을 제공합니다
- **데이터 내보내기/가져오기** — JSON 파일을 통한 백업 및 복원을 지원합니다
- **검색 및 정렬** — 사이트 목록을 검색하고 오름차순/내림차순으로 정렬할 수 있습니다
- **다크 모드** — 기본으로 다크 모드가 적용되어 있습니다

---

## 사용자 가이드

### 설치 및 실행

#### 방법 1: 소스에서 직접 실행

```bash
# 저장소 클론
git clone https://github.com/<사용자명>/etc-otp.git
cd etc-otp

# 가상 환경 생성 및 활성화
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 의존성 설치
pip install -r requirements.txt

# 실행
python main.py
```

> **참고:** `pyzbar`는 시스템에 zbar 라이브러리가 필요합니다.
> - **Windows:** pyzbar 패키지에 DLL이 포함되어 있어 추가 설치가 필요 없습니다.
> - **macOS:** `brew install zbar`
> - **Linux:** `sudo apt install libzbar0`

#### 방법 2: 실행 파일 (EXE) 빌드

```bash
venv\Scripts\activate
pyinstaller --onefile --windowed main.py
```

빌드된 실행 파일은 `dist/main.exe`에 생성됩니다.

### 사용법

| 동작 | 설명 |
|------|------|
| **사이트 클릭** | OTP를 생성하고 클립보드에 복사합니다 |
| **사이트 추가** | 사이트 이름과 비밀 키(Base32 또는 `otpauth://` URI)를 입력합니다 |
| **QR 코드 스캔** | QR 이미지 파일을 선택하거나, QR 이미지를 복사한 후 `Ctrl+V`를 누릅니다 |
| **데이터 내보내기** | 모든 사이트 정보를 JSON 파일로 저장합니다 |
| **데이터 가져오기** | 내보낸 JSON 파일로부터 사이트를 복원합니다 |

### 데이터 저장 위치

OTP 비밀 키는 실행 파일(또는 `main.py`)과 같은 디렉토리의 `otp_secrets.db` (SQLite) 파일에 저장됩니다.

---

## 개발자 가이드

### 기술 스택

- **Python 3.12+**
- **PyQt6** — GUI 프레임워크
- **pyotp** — TOTP 코드 생성
- **pyzbar** — QR 코드 디코딩
- **qrcode** — QR 코드 생성
- **Pillow** — 이미지 처리 및 클립보드 이미지 변환
- **SQLite3** — 로컬 데이터베이스 (표준 라이브러리)

### 프로젝트 구조

```
etc-otp/
├── main.py                 # 진입점, 애플리케이션 로직 (OTPApp 클래스)
├── ui_main.py              # UI 레이아웃 정의 (Ui_OTPApp 클래스)
├── module/
│   ├── db_manager.py       # SQLite DB CRUD 함수
│   ├── otp_manager.py      # OTP 생성 및 otpauth:// URI 파싱
│   └── qr_handler.py       # QR 코드 인코딩/디코딩
├── requirements.txt        # Python 의존성 목록
├── otp_secrets.db          # SQLite 데이터베이스 (실행 시 자동 생성)
└── build/                  # PyInstaller 빌드 산출물
```

### 아키텍처

**UI와 로직의 분리:** `ui_main.py`는 위젯 배치만 담당하고, `main.py`의 `OTPApp` 클래스가 UI 인스턴스를 생성한 뒤 시그널/슬롯을 연결합니다.

**DB 계층:** `db_manager.py`의 각 함수는 독립적으로 SQLite 연결을 열고 닫습니다. 테이블 스키마:

```sql
CREATE TABLE secrets (
    id INTEGER PRIMARY KEY,
    site_name TEXT UNIQUE,
    secret_key TEXT
);
```

**OTP 생성 흐름:** DB에 저장된 `secret_key`가 Base32 문자열이든 `otpauth://` URI이든 상관없이, `otp_manager.parse_secret()`이 실제 Base32 시크릿을 추출한 후 `pyotp.TOTP`로 코드를 생성합니다.

### 개발 환경 설정

```bash
# 가상 환경 활성화
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 의존성 설치
pip install -r requirements.txt

# 앱 실행
python main.py
```

---

## 라이선스

MIT License
