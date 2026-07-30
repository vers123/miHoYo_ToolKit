import os
import sqlite3
import shutil
import tempfile
from typing import List, Dict, Optional
from pathlib import Path


def find_firefox_profile() -> Optional[str]:
    """查找 Firefox 默认配置文件路径"""
    appdata = os.environ.get("APPDATA", "")
    if not appdata:
        return None

    profiles_dir = os.path.join(appdata, "Mozilla", "Firefox", "Profiles")
    if not os.path.exists(profiles_dir):
        return None

    for entry in os.listdir(profiles_dir):
        entry_path = os.path.join(profiles_dir, entry)
        if os.path.isdir(entry_path) and ("default-release" in entry or "default" in entry):
            cookies_path = os.path.join(entry_path, "cookies.sqlite")
            if os.path.exists(cookies_path):
                return entry_path

    for entry in os.listdir(profiles_dir):
        entry_path = os.path.join(profiles_dir, entry)
        if os.path.isdir(entry_path):
            cookies_path = os.path.join(entry_path, "cookies.sqlite")
            if os.path.exists(cookies_path):
                return entry_path

    return None


def load_firefox_cookies(domain_filter: str = None) -> List[Dict[str, str]]:
    """
    从 Firefox 读取 cookie

    Args:
        domain_filter: 按域名过滤，例如 "weibo.com"

    Returns:
        Playwright 格式的 cookie 列表
    """
    profile_path = find_firefox_profile()
    if not profile_path:
        print("[WARN] 未找到 Firefox 配置文件")
        return []

    cookies_db = os.path.join(profile_path, "cookies.sqlite")
    if not os.path.exists(cookies_db):
        print("[WARN] Firefox cookie 数据库不存在")
        return []

    tmp_db = os.path.join(tempfile.gettempdir(), "firefox_cookies_tmp.sqlite")
    try:
        shutil.copy2(cookies_db, tmp_db)
    except Exception as e:
        print(f"[WARN] 复制 cookie 数据库失败: {e}")
        return []

    cookies = []
    try:
        conn = sqlite3.connect(tmp_db)
        cursor = conn.cursor()

        query = "SELECT name, value, host, path, expiry, isSecure, isHttpOnly, sameSite FROM moz_cookies"
        params = []

        if domain_filter:
            query += " WHERE host LIKE ?"
            params.append(f"%{domain_filter}%")

        cursor.execute(query, params)
        rows = cursor.fetchall()

        samesite_map = {0: "None", 1: "Lax", 2: "Strict"}

        for row in rows:
            name, value, host, path, expiry, is_secure, is_httponly, samesite = row

            if expiry is None or expiry <= 0:
                expires_val = -1
            else:
                if expiry > 1000000000000:
                    expires_val = int(expiry / 1000)
                else:
                    expires_val = int(expiry)

            same_site_str = samesite_map.get(samesite, "Lax")

            cookie = {
                "name": name,
                "value": value,
                "domain": host,
                "path": path,
                "expires": expires_val,
                "secure": bool(is_secure),
                "httpOnly": bool(is_httponly),
                "sameSite": same_site_str
            }
            cookies.append(cookie)

        conn.close()
    except Exception as e:
        print(f"[WARN] 读取 cookie 失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            if os.path.exists(tmp_db):
                os.remove(tmp_db)
        except:
            pass

    print(f"[INFO] 从 Firefox 加载了 {len(cookies)} 条 cookie" + (f" (域名: {domain_filter})" if domain_filter else ""))
    return cookies
