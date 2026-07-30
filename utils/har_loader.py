"""HAR文件解析工具 - 从浏览器导出的HAR文件中提取API信息"""

import os
import json
from typing import List, Optional, Dict


# HAR文件存放根目录
HAR_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "har")


def get_har_dir(scraper_name: str) -> str:
    """获取抓取器对应的HAR文件目录"""
    return os.path.join(HAR_BASE_DIR, scraper_name)


def find_har_file(scraper_name: str) -> Optional[str]:
    """在 har/{scraper_name}/ 下查找HAR文件"""
    har_dir = get_har_dir(scraper_name)
    if not os.path.exists(har_dir):
        return None

    for filename in os.listdir(har_dir):
        lower = filename.lower()
        if lower.endswith('.har') or lower.endswith('.txt'):
            return os.path.join(har_dir, filename)
    return None


def parse_har_file(har_path: str) -> List[dict]:
    """解析HAR文件，返回所有entries（支持多个HAR拼接）"""
    with open(har_path, 'r', encoding='utf-8') as f:
        content = f.read()

    all_entries = []
    decoder = json.JSONDecoder()
    idx = 0
    while idx < len(content):
        try:
            obj, end_idx = decoder.raw_decode(content, idx)
            if 'log' in obj and 'entries' in obj['log']:
                all_entries.extend(obj['log']['entries'])
            idx = end_idx
            while idx < len(content) and content[idx] in ' \n\r\t':
                idx += 1
        except json.JSONDecodeError:
            idx += 1

    return all_entries


def extract_api_patterns(har_path: str, domain_keywords: List[str] = None) -> List[dict]:
    """从HAR文件中提取API模式

    返回: [{"url": "https://...", "method": "GET", "params": {...}, "has_json_response": True}]
    """
    entries = parse_har_file(har_path)
    patterns = []
    seen_urls = set()

    for entry in entries:
        req = entry.get('request', {})
        resp = entry.get('response', {})
        url = req.get('url', '')
        method = req.get('method', 'GET')

        if method != 'GET':
            continue

        if domain_keywords:
            if not any(kw in url for kw in domain_keywords):
                continue

        content = resp.get('content', {})
        mime_type = content.get('mimeType', '')
        has_text = 'text' in content

        if 'json' not in mime_type and not has_text:
            continue

        if url in seen_urls:
            continue
        seen_urls.add(url)

        params = {q['name']: q['value'] for q in req.get('queryString', [])}
        headers = {h['name'].lower(): h['value'] for h in req.get('headers', [])}

        patterns.append({
            'url': url,
            'method': method,
            'params': params,
            'headers': headers,
            'has_json_response': 'json' in mime_type,
            'status': resp.get('status', 0)
        })

    return patterns


def print_har_instructions(scraper_name: str, page_url: str, domain_keywords: List[str] = None):
    """打印获取HAR文件的步骤指引"""
    har_dir = get_har_dir(scraper_name)

    print("\n" + "=" * 70)
    print("[HAR] 自动检测API失败，请按以下步骤获取HAR文件：")
    print("=" * 70)
    print(f"""
步骤1: 打开 Firefox 浏览器
步骤2: 按 F12 打开开发者工具
步骤3: 切换到「网络」(Network) 面板
步骤4: 勾选「持续日志」(Persist Logs)
步骤5: 访问以下页面并滚动到底部:
       {page_url}
步骤6: 在网络面板中，找到返回帖子/新闻数据的JSON请求
       {"(域名包含: " + ", ".join(domain_keywords) + ")" if domain_keywords else ""}
步骤7: 右键该请求 → 「保存所有为HAR」(Save All As HAR)
步骤8: 将HAR文件保存到以下目录:
       {har_dir}
       (如果目录不存在，请手动创建)
步骤9: 保存后重新运行本抓取功能
""")
    print("=" * 70)

    os.makedirs(har_dir, exist_ok=True)
    print(f"\n[INFO] 已创建目录: {har_dir}")
    print(f"[INFO] 请将HAR文件放入上述目录后重新运行")
    print("=" * 70 + "\n")


def load_api_pattern_from_har(scraper_name: str, domain_keywords: List[str] = None) -> Optional[dict]:
    """从HAR文件加载API模式

    返回: {"url_pattern": "userPostList", "domain": "bbs-api.miyoushe.com", ...}
          或 None（如果没找到HAR文件）
    """
    har_path = find_har_file(scraper_name)
    if not har_path:
        return None

    print(f"[INFO] 找到HAR文件: {har_path}")
    patterns = extract_api_patterns(har_path, domain_keywords)

    if not patterns:
        print("[WARN] HAR文件中未找到匹配的API请求")
        return None

    json_patterns = [p for p in patterns if p['has_json_response']]
    if not json_patterns:
        json_patterns = patterns

    best = json_patterns[0]
    print(f"[INFO] 从HAR中识别到API: {best['url'][:100]}")

    from urllib.parse import urlparse
    parsed = urlparse(best['url'])
    path = parsed.path
    path_keyword = path.split('/')[-1] if path else ''

    return {
        'url_pattern': path_keyword,
        'full_url_template': best['url'],
        'domain': parsed.netloc,
        'params': best['params'],
        'headers': {k: v for k, v in best['headers'].items()
                     if k in ['ds', 'x-rpc-app_version', 'x-rpc-client_type',
                              'x-rpc-device_fp', 'x-rpc-device_id', 'referer', 'origin']}
    }
