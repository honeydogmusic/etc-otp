# 개발 예정 사항

> 2026-02-07 코드 심층 분석 기반 작성

---

## 긴급

### BUG-01. QTimer 다중 생성으로 인한 타이머 경쟁
- **파일:** `main.py:112-115`
- **현상:** 사이트를 클릭할 때마다 새 QTimer 객체가 생성됨. 이전 타이머가 stop되지 않아 여러 타이머가 동시에 `remaining_time`을 감소시킴
- **재현:** 사이트 A 클릭 → 즉시 사이트 B 클릭 → 초가 2배 속도로 감소
- **수정 방향:** `__init__`에서 타이머를 한 번만 생성하고, `generate_otp_action()`에서는 stop/start만 호출

### SEC-01. 비밀 키 평문 DB 저장
- **파일:** `module/db_manager.py:50-51`
- **현상:** `otp_secrets.db`에 `secret_key`가 암호화 없이 평문으로 저장됨. DB 파일 탈취 시 모든 2FA 무력화
- **수정 방향:** `cryptography` Fernet 대칭 암호화 도입, 마스터 비밀번호 기반 키 파생(PBKDF2). 별도 UX 설계 필요 (앱 시작 시 마스터 비밀번호 입력 화면)

---

## 높음

### BUG-04. 삭제 시 확인 대화상자 없음
- **파일:** `main.py:176-183`
- **현상:** 삭제 버튼 클릭 시 즉시 삭제. 실수로 클릭하면 복구 불가
- **수정 방향:** `QMessageBox.question()`으로 삭제 확인

### BUG-05. JSON import 시 예외 처리 없음
- **파일:** `main.py:200-207`
- **현상:** 잘못된 JSON 파일 선택 시 `JSONDecodeError`, `KeyError`, `TypeError` 등으로 크래시
- **수정 방향:** try/except로 감싸고 사용자 안내 메시지 표시

### BUG-07. QR 이미지 파일 오류 미처리
- **파일:** `main.py:209-224`, `module/qr_handler.py:7`
- **현상:** 손상된 이미지 파일 선택 시 `PIL.UnidentifiedImageError` 크래시. QR 인식 결과 0건일 때 알림 없음
- **수정 방향:** try/except 추가, 디코딩 실패 시 "QR 코드를 인식하지 못했습니다" 메시지

### BUG-09. otpauth URI에 secret 파라미터 누락 시 오류
- **파일:** `module/otp_manager.py:4-14`
- **현상:** `otpauth://totp/example?issuer=Test` (secret 없음) 입력 시 전체 URI가 Base32로 전달되어 `binascii.Error` 발생
- **수정 방향:** `otpauth://`로 시작하면서 `secret` 파라미터 없으면 명시적 `ValueError` 발생

### SEC-02. JSON 내보내기 시 비밀 키 평문 노출
- **파일:** `main.py:185-198`
- **현상:** 내보낸 JSON 파일에 모든 시크릿이 평문으로 저장됨
- **수정 방향:** SEC-01 암호화 도입 후 함께 처리. 최소한 내보내기 시 경고 대화상자 표시

### SEC-05. 클립보드에 OTP 무기한 잔존
- **파일:** `main.py:100-101`
- **현상:** OTP가 클립보드에 복사된 후 자동으로 지워지지 않음
- **수정 방향:** OTP 만료 시 (`remaining_time <= 0`) `clipboard.clear()` 호출

---

## 중간

### PERF-01. DB 연결 반복 열기/닫기
- **파일:** `module/db_manager.py` 전체
- **현상:** 8개 함수 모두 매 호출마다 `sqlite3.connect()` / `conn.close()` 반복
- **수정 방향:** context manager 패턴 도입
  ```python
  @contextmanager
  def get_connection():
      conn = sqlite3.connect(DB_NAME)
      try:
          yield conn
          conn.commit()
      except Exception:
          conn.rollback()
          raise
      finally:
          conn.close()
  ```

### PERF-02. Python 측 정렬 대신 SQL ORDER BY 사용
- **파일:** `main.py:63-74`, `module/db_manager.py:28-35`
- **현상:** DB에서 정렬 없이 전체를 가져온 뒤 Python에서 `sorted()` 수행
- **수정 방향:** `get_all_sites(order='ASC')` → SQL에 `ORDER BY site_name` 포함

### REFACT-01. QR 스캔 처리 코드 중복
- **파일:** `main.py:214-223`, `main.py:255-262`
- **현상:** `scan_qr_code_from_file()`과 `scan_qr_from_clipboard()`에서 디코딩 후 처리 로직이 거의 동일
- **수정 방향:** `_process_decoded_qr(decoded_objects)` private 메서드로 추출

### REFACT-03. DB 함수 반복 패턴
- **파일:** `module/db_manager.py`
- **현상:** 8개 함수에서 connect → cursor → execute → commit → close 패턴 반복
- **수정 방향:** PERF-01의 context manager 도입으로 함께 해결

### REFACT-05. dark_mode 변수 값이 실제 상태와 역전
- **파일:** `main.py:45-46, 51-61`
- **현상:** `dark_mode = True` 초기화 → `toggle_dark_mode()` 호출 → 다크 스타일 적용 후 `False`로 변경. 실제로는 다크 모드인데 변수는 `False`
- **수정 방향:** `_apply_dark_mode()` / `_apply_light_mode()` 분리하거나, 토글 로직에서 변수 변경 순서 수정. 토글 버튼이 UI에 없으므로 토글 로직 자체를 제거하고 `_apply_dark_mode()`만 남기는 것도 방법

### SEC-04. 비밀 키 입력 시 유효성 검증 없음
- **파일:** `main.py:131-137`
- **현상:** 잘못된 Base32 문자열을 입력해도 저장됨. OTP 생성 시점에서야 오류 발생
- **수정 방향:** `add_site()` 시 `pyotp.TOTP(parse_secret(key)).now()` 호출로 사전 검증

### UX-05. Ctrl+V 오버라이드로 검색 바 붙여넣기 차단
- **파일:** `main.py:230-241`
- **현상:** 클립보드에 이미지가 있으면 검색 바에 포커스가 있어도 QR 스캔이 시작됨
- **수정 방향:** 포커스가 `search_bar`나 `QLineEdit` 위젯에 있을 때는 기본 동작 유지

---

## 낮음

### PERF-04. import time 중복
- **파일:** `main.py:3`, `main.py:104`
- **수정 방향:** 줄 104의 `import time` 삭제

### LINT-02. 미사용 코드 (dead code)
- **파일:** `module/qr_handler.py:1, 14-30`
- **현상:** `import qrcode`와 `create_qr_code()` 함수가 프로젝트 어디에서도 사용되지 않음
- **수정 방향:** 향후 사용 계획이 없으면 삭제

### LINT-01. 타입 힌트 부재
- **영향:** 전체 파일
- **수정 방향:** 주요 함수에 타입 힌트 추가
  ```python
  def get_secret_by_site(site_name: str) -> Optional[str]:
  def generate_otp(raw_secret: str) -> tuple[str, pyotp.TOTP]:
  ```

### UX-02. 작업 결과 피드백 부족
- **파일:** `main.py`
- **현상:** update, rename, delete, export, import 성공 시 사용자에게 알림 없음
- **수정 방향:** `message_label`에 결과 메시지 표시 + `QTimer.singleShot(3000, clear)`

### UX-03. OTP 만료 시 자동 갱신 없음
- **파일:** `main.py:120-126`
- **현상:** 타이머 0 도달 시 "새로 생성하세요" 메시지만 표시
- **수정 방향:** 만료 시 `generate_otp_action()` 자동 재호출

### UX-04. 사이트 미선택 시 무반응
- **파일:** `main.py:146-149, 159-162, 176-179`
- **현상:** 사이트를 선택하지 않고 버튼을 누르면 아무 반응 없음
- **수정 방향:** "사이트를 먼저 선택해주세요" 메시지 표시

### UX-06. 창 최소 크기 미설정
- **파일:** `ui_main.py`
- **수정 방향:** `OTPApp.setMinimumSize(500, 600)` 추가

### UX-07. 7개 버튼 한 줄 배치
- **파일:** `ui_main.py:48-71`
- **현상:** 창이 작으면 버튼 텍스트가 잘리거나 매우 좁아짐
- **수정 방향:** 2줄 배치 또는 QGridLayout 사용

---

## 참고: 긍정적 평가 항목

- **SQL 인젝션 방지:** 모든 쿼리에서 파라미터 바인딩(`?`) 사용 (SEC-03)
- **otpauth:// URI 지원:** Base32와 URI 모두 처리 가능한 유연한 설계
- **UI/로직 분리:** `ui_main.py`와 `main.py`로 레이아웃과 로직이 분리되어 있음
