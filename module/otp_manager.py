import urllib.parse
import pyotp

def parse_secret(secret):
    """
    secret이 'otpauth://...' 형태라면 ?secret= 파라미터만 추출해서 반환.
    아니라면 그대로 반환.
    """
    if secret.startswith('otpauth://'):
        parsed = urllib.parse.urlparse(secret)
        query = urllib.parse.parse_qs(parsed.query)
        if 'secret' in query:
            return query['secret'][0]
    return secret

def generate_otp(raw_secret):
    """
    DB에 저장된 secret이 Base32가 아닌 'otpauth://...' 형태일 수도 있으므로,
    parse_secret()로 최종적인 Base32 시크릿만 추출한 뒤 TOTP 생성.
    """
    secret = parse_secret(raw_secret)
    totp = pyotp.TOTP(secret)
    return totp.now(), totp
