import qrcode
from pyzbar.pyzbar import decode
from PIL import Image

def decode_qr_from_file(file_path):
    """이미지 파일에서 QR 코드를 스캔하여 디코딩"""
    img = Image.open(file_path)
    return decode(img)

def decode_qr_from_pil(pil_image):
    """PIL Image 객체에서 QR 코드 스캔하여 디코딩"""
    return decode(pil_image)

def create_qr_code(data, save_path=None):
    """QR 코드 생성 (필요 시)"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    if save_path:
        img.save(save_path)

    return img
