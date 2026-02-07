from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget,
    QHBoxLayout, QComboBox
)
from PyQt6.QtGui import QFont

class Ui_OTPApp(object):
    def setupUi(self, OTPApp: QWidget):
        OTPApp.setObjectName("OTPApp")
        OTPApp.setWindowTitle('멀티 사이트 OTP 관리자')
        OTPApp.setFont(QFont('맑은 고딕'))

        # 메인 레이아웃
        self.main_layout = QVBoxLayout(OTPApp)
        self.main_layout.setObjectName("main_layout")

        # 안내 라벨
        self.label = QLabel('사이트를 클릭하여 OTP를 생성하세요:', parent=OTPApp)
        self.main_layout.addWidget(self.label)

        # 정렬 순서 선택(콤보박스)
        self.sort_order = QComboBox(parent=OTPApp)
        self.sort_order.addItems(["오름차순 정렬", "내림차순 정렬"])
        self.main_layout.addWidget(self.sort_order)

        # 검색 창
        self.search_bar = QLineEdit(parent=OTPApp)
        self.search_bar.setPlaceholderText("검색...")
        self.main_layout.addWidget(self.search_bar)

        # 사이트 리스트
        self.site_list = QListWidget(parent=OTPApp)
        self.main_layout.addWidget(self.site_list)

        # OTP 표시 영역
        self.otp_code = QLineEdit(parent=OTPApp)
        self.otp_code.setReadOnly(True)
        self.main_layout.addWidget(self.otp_code)

        # 타이머 라벨
        self.timer_label = QLabel('', parent=OTPApp)
        self.main_layout.addWidget(self.timer_label)

        # 메시지 라벨
        self.message_label = QLabel('', parent=OTPApp)
        self.main_layout.addWidget(self.message_label)

        # 버튼 레이아웃
        self.btn_layout = QHBoxLayout()
        self.main_layout.addLayout(self.btn_layout)

        self.add_btn = QPushButton('사이트 추가', parent=OTPApp)
        self.btn_layout.addWidget(self.add_btn)

        self.update_btn = QPushButton('사이트 업데이트', parent=OTPApp)
        self.btn_layout.addWidget(self.update_btn)

        self.rename_btn = QPushButton('사이트 이름 변경', parent=OTPApp)
        self.btn_layout.addWidget(self.rename_btn)

        self.delete_btn = QPushButton('사이트 삭제', parent=OTPApp)
        self.btn_layout.addWidget(self.delete_btn)

        self.export_btn = QPushButton('데이터 내보내기', parent=OTPApp)
        self.btn_layout.addWidget(self.export_btn)

        self.import_btn = QPushButton('데이터 가져오기', parent=OTPApp)
        self.btn_layout.addWidget(self.import_btn)

        self.scan_qr_btn = QPushButton('QR 코드 스캔', parent=OTPApp)
        self.btn_layout.addWidget(self.scan_qr_btn)
