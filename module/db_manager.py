import sqlite3
import os
import sys

def get_db_path():
    """main.py 또는 실행 파일 기준으로 DB 경로 반환"""
    if getattr(sys, 'frozen', False):  # PyInstaller로 빌드된 실행 파일인 경우
        base_dir = os.path.dirname(sys.executable)
    else:  # 개발 중인 경우 (main.py 실행 경로 기준)
        base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    return os.path.join(base_dir, "otp_secrets.db")

DB_NAME = get_db_path()

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS secrets (
            id INTEGER PRIMARY KEY,
            site_name TEXT UNIQUE,
            secret_key TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_all_sites():
    """저장된 모든 사이트명 가져오기"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT site_name FROM secrets")
    sites = c.fetchall()
    conn.close()
    return sites

def get_secret_by_site(site_name):
    """특정 사이트의 secret_key 가져오기"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT secret_key FROM secrets WHERE site_name = ?", (site_name,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def insert_secret(site_name, secret_key):
    """새로운 사이트와 secret_key 저장"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO secrets (site_name, secret_key) VALUES (?, ?)",
              (site_name, secret_key))
    conn.commit()
    conn.close()

def update_secret(site_name, new_secret_key):
    """기존 사이트의 secret_key 변경"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE secrets SET secret_key = ? WHERE site_name = ?",
              (new_secret_key, site_name))
    conn.commit()
    conn.close()

def rename_site(old_site_name, new_site_name):
    """사이트 이름 변경"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE secrets SET site_name = ? WHERE site_name = ?",
              (new_site_name, old_site_name))
    conn.commit()
    conn.close()

def delete_site(site_name):
    """사이트 삭제"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM secrets WHERE site_name = ?", (site_name,))
    conn.commit()
    conn.close()

def get_all_secrets():
    """전체 secrets 테이블 데이터 반환"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM secrets")
    rows = c.fetchall()
    conn.close()
    return rows

def insert_multiple(data):
    """
    여러 개의 사이트/시크릿 데이터를 한꺼번에 추가
    data: [{'site_name': str, 'secret_key': str}, ...] 형태
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    for entry in data:
        try:
            c.execute("INSERT INTO secrets (site_name, secret_key) VALUES (?, ?)",
                      (entry["site_name"], entry["secret_key"]))
        except sqlite3.IntegrityError:
            # 이미 존재하는 site_name인 경우 무시하거나, 필요 시 업데이트 로직 추가 가능
            pass
    conn.commit()
    conn.close()
