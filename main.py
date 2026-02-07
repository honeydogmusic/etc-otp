import sys
import json
import time


from PyQt6.QtWidgets import (
    QApplication, QWidget, QMessageBox, QInputDialog, QFileDialog
)
from PyQt6.QtCore import Qt, QTimer
from PIL import ImageQt

# 모듈 임포트
from module.db_manager import (
    init_db, get_all_sites, get_secret_by_site,
    insert_secret, update_secret, rename_site,
    delete_site, get_all_secrets, insert_multiple
)
from module.otp_manager import generate_otp
from module.qr_handler import decode_qr_from_file, decode_qr_from_pil

# 분리된 UI 모듈 임포트
from ui_main import Ui_OTPApp

class OTPApp(QWidget):
    def __init__(self):
        super().__init__()
        # 분리된 UI 세팅
        self.ui = Ui_OTPApp()
        self.ui.setupUi(self)

        # UI 설정 후, 필요한 시그널(이벤트) 연결
        self.ui.sort_order.currentIndexChanged.connect(self.load_sites)
        self.ui.search_bar.textChanged.connect(self.filter_sites)
        self.ui.site_list.clicked.connect(self.generate_otp_action)

        self.ui.add_btn.clicked.connect(self.add_site)
        self.ui.update_btn.clicked.connect(self.update_site)
        self.ui.rename_btn.clicked.connect(self.rename_site_action)
        self.ui.delete_btn.clicked.connect(self.delete_site_action)
        self.ui.export_btn.clicked.connect(self.export_data)
        self.ui.import_btn.clicked.connect(self.import_data)
        self.ui.scan_qr_btn.clicked.connect(self.scan_qr_code_from_file)

        # 다크 모드 설정
        self.dark_mode = True
        self.toggle_dark_mode()

        # 사이트 목록 로드
        self.load_sites()

    def toggle_dark_mode(self):
        if self.dark_mode:
            self.setStyleSheet(
                "QWidget { background-color: #121212; color: #ffffff; }\n"
                "QLineEdit, QListWidget { background-color: #1e1e1e; color: #ffffff; border: 1px solid #333333; }\n"
                "QPushButton { background-color: #2e2e2e; border: none; padding: 5px; }\n"
                "QPushButton:hover { background-color: #3e3e3e; }"
            )
        else:
            self.setStyleSheet("")
        self.dark_mode = not self.dark_mode

    def load_sites(self):
        """사이트 리스트 로드 및 정렬"""
        sites = get_all_sites()
        order = self.ui.sort_order.currentText()
        if order == "오름차순 정렬":
            sites = sorted(sites, key=lambda x: x[0])
        else:
            sites = sorted(sites, key=lambda x: x[0], reverse=True)

        self.ui.site_list.clear()
        for site in sites:
            self.ui.site_list.addItem(site[0])

    def filter_sites(self, text):
        """검색 필터링"""
        for i in range(self.ui.site_list.count()):
            item = self.ui.site_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def generate_otp_action(self):
        """리스트에서 사이트 클릭 시 OTP 생성"""
        selected_site = self.ui.site_list.currentItem()
        if selected_site:
            site_name = selected_site.text()
            raw_secret = get_secret_by_site(site_name)
            if not raw_secret:
                return

            try:
                otp_code, totp = generate_otp(raw_secret)
            except Exception as e:
                QMessageBox.critical(self, "에러", f"OTP 생성 중 오류가 발생했습니다: {e}")
                return

            self.ui.otp_code.setText(otp_code)

            # 클립보드 복사
            clipboard = QApplication.clipboard()
            clipboard.setText(otp_code)

            # 올바른 남은 시간 계산
            import time
            current_time = time.time()  # 현재 유닉스 타임스탬프 (초)
            cycle_length = totp.interval  # 보통 30초
            time_left = cycle_length - (current_time % cycle_length)

            self.remaining_time = int(time_left)
            self.ui.timer_label.setText(f"유효 시간: {self.remaining_time}초")

            # 타이머 스타트
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_timer)
            self.timer.start(1000)

            self.ui.message_label.setText(f"{site_name}의 OTP가 클립보드에 복사되었습니다.")
            QTimer.singleShot(3000, self.clear_message)

    def update_timer(self):
        self.remaining_time -= 1
        if self.remaining_time <= 0:
            self.timer.stop()
            self.ui.timer_label.setText("OTP가 만료되었습니다. 새로 생성하세요.")
        else:
            self.ui.timer_label.setText(f"유효 시간: {self.remaining_time}초")

    def clear_message(self):
        self.ui.message_label.clear()

    def add_site(self):
        site_name, ok = self.get_input("사이트 이름 입력")
        if not ok or not site_name:
            return
        secret_key, ok = self.get_input("비밀 키 (Base32 또는 otpauth://...) 입력")
        if not ok or not secret_key:
            return

        try:
            insert_secret(site_name, secret_key)
        except Exception:
            QMessageBox.warning(self, "오류", "이미 존재하는 사이트입니다.")

        self.load_sites()

    def update_site(self):
        selected_site = self.ui.site_list.currentItem()
        if not selected_site:
            return

        site_name = selected_site.text()
        new_secret_key, ok = self.get_input("새 비밀 키 입력 (Base32 또는 otpauth://...)")
        if not ok or not new_secret_key:
            return

        update_secret(site_name, new_secret_key)
        self.generate_otp_action()

    def rename_site_action(self):
        selected_site = self.ui.site_list.currentItem()
        if not selected_site:
            return

        old_site_name = selected_site.text()
        new_site_name, ok = self.get_input("새 사이트 이름 입력")
        if not ok or not new_site_name:
            return

        try:
            rename_site(old_site_name, new_site_name)
        except Exception:
            QMessageBox.warning(self, "오류", "이미 존재하는 사이트 이름입니다.")

        self.load_sites()

    def delete_site_action(self):
        selected_site = self.ui.site_list.currentItem()
        if not selected_site:
            return

        site_name = selected_site.text()
        delete_site(site_name)
        self.load_sites()

    def export_data(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "데이터 내보내기", "", "JSON 파일 (*.json)")
        if file_path:
            data = []
            rows = get_all_secrets()
            for row in rows:
                data.append({
                    "id": row[0],
                    "site_name": row[1],
                    "secret_key": row[2]
                })

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

    def import_data(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "데이터 가져오기", "", "JSON 파일 (*.json)")
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            insert_multiple(data)
            self.load_sites()

    def scan_qr_code_from_file(self):
        """파일로부터 QR 코드 스캔하여 사이트 추가"""
        file_path, _ = QFileDialog.getOpenFileName(self, "QR 코드 스캔", "", "Image Files (*.png *.jpg *.jpeg)")
        if file_path:
            decoded_objects = decode_qr_from_file(file_path)
            for obj in decoded_objects:
                secret_key = obj.data.decode("utf-8")
                # otpauth://... 일 경우 그대로 DB에 넣어도 문제 없음
                # generate_otp() 호출 시 parse_secret()에서 Base32를 뽑아냄
                site_name, ok = self.get_input("스캔된 QR 코드에서 사이트 이름 입력")
                if ok and site_name:
                    try:
                        insert_secret(site_name, secret_key)
                    except Exception:
                        QMessageBox.warning(self, "오류", "이미 존재하는 사이트입니다.")
            self.load_sites()

    def get_input(self, prompt):
        text, ok = QInputDialog.getText(self, "입력", prompt)
        return text, ok

    def keyPressEvent(self, event):
        """
        Ctrl+V(붙여넣기) 이벤트를 오버라이드하여
        클립보드에 이미지가 있을 경우 QR 코드로 인식해 사이트 추가.
        """
        # PyQt6에서는 Qt.Key.Key_V, Qt.KeyboardModifier.ControlModifier 형태로 접근
        if (event.key() == Qt.Key.Key_V and
            (event.modifiers() & Qt.KeyboardModifier.ControlModifier)):

            self.scan_qr_from_clipboard()
        else:
            super().keyPressEvent(event)

    def scan_qr_from_clipboard(self):
        """클립보드 이미지를 QR 코드로 인식"""
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()

        # 클립보드에 이미지가 있는지 확인
        if mime_data.hasImage():
            qimage = clipboard.image()
            if not qimage.isNull():
                pil_image = ImageQt.fromqimage(qimage)
                decoded_objects = decode_qr_from_pil(pil_image)
                if decoded_objects:
                    for obj in decoded_objects:
                        secret_key = obj.data.decode("utf-8")
                        site_name, ok = self.get_input("스캔된 QR 코드에서 사이트 이름 입력")
                        if ok and site_name:
                            try:
                                insert_secret(site_name, secret_key)
                            except Exception:
                                QMessageBox.warning(self, "오류", "이미 존재하는 사이트입니다.")
                    self.load_sites()
                else:
                    QMessageBox.information(self, "알림", "QR 코드를 인식하지 못했습니다.")
        else:
            QMessageBox.information(self, "알림", "클립보드에 이미지가 없습니다.")


if __name__ == '__main__':
    init_db()  # DB 초기화
    app = QApplication(sys.argv)
    ex = OTPApp()
    ex.show()
    sys.exit(app.exec())
