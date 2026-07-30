import time
import html
from datetime import datetime
from playwright.sync_api import sync_playwright, Page, Browser
from core.scraper import BaseScraper, ScraperConfig
from core.config_manager import config_manager
from utils.error_handler import handle_errors, retry
from utils.har_loader import find_har_file, load_api_pattern_from_har, print_har_instructions
from extractors.news import NewsExtractor


class NewsScraper(BaseScraper):
    """原神新闻抓取器 - 基于API响应拦截 + HAR回退"""

    def __init__(self, incremental: bool = False):
        existing_urls = None
        if incremental and config_manager.get("incremental_settings.enabled", True):
            extractor = NewsExtractor()
            existing_urls = extractor.get_existing_urls()
            print(f"[INFO] 增量模式: 已存在 {len(existing_urls)} 条数据")

        scraper_config = ScraperConfig(
            url="https://ys.mihoyo.com/main/news",
            output_filename="news_page.html",
            headless=config_manager.get("headless", False),
            wait_seconds=config_manager.get("wait_seconds", 3),
            timeout=config_manager.get("timeout", 120000),
            user_agent=config_manager.get("user_agent"),
            browser_args=config_manager.get("browser_args", []),
            scroll_delay=config_manager.get("scroll_settings.delay", 2.0),
            incremental_mode=incremental,
            existing_urls=existing_urls,
            scraper_name="news",
            api_url_keywords=["newsList", "getNewsList", "news", "getList", "postList"],
            api_domain_filter="miyoushe.com",
            use_firefox_cookies=config_manager.get("miyoushe_settings.use_firefox_cookies", True),
        )
        super().__init__(scraper_config)

        self.url_selector_template = "a[href*='/main/news/detail/']"

    def _extract_items_from_api(self, data: dict) -> list:
        """从API响应中提取新闻列表"""
        news_list = []

        if not isinstance(data, dict):
            return news_list

        candidates = []
        if "data" in data:
            d = data["data"]
            if isinstance(d, dict):
                for key in ("list", "news", "items"):
                    if key in d:
                        candidates = d[key]
                        break
            elif isinstance(d, list):
                candidates = d
        elif "list" in data:
            candidates = data["list"]

        for item in candidates:
            if not isinstance(item, dict):
                continue

            news_id = item.get("id") or item.get("news_id") or item.get("post_id") or ""
            title = item.get("title") or item.get("subject") or ""
            date_str = item.get("start_time") or item.get("created_at") or item.get("date") or ""

            if not news_id or not title:
                continue

            if isinstance(date_str, (int, float)) and date_str > 1000000000:
                date_str = datetime.fromtimestamp(int(date_str)).strftime("%Y/%m/%d")
            elif not date_str:
                date_str = ""

            news_list.append({
                "id": str(news_id),
                "title": title,
                "date": str(date_str),
                "url": f"https://ys.mihoyo.com/main/news/detail/{news_id}"
            })

        return news_list

    def _build_html_from_api_data(self, items: list) -> str:
        """将API数据构建为HTML"""
        html_parts = ['<!DOCTYPE html><html lang="zh-cn"><head><meta charset="utf-8"><title>原神新闻</title></head><body>']
        html_parts.append('<ul class="news__list">')

        for item in items:
            news_id = item.get("id", "")
            title = item.get("title", "")
            date = item.get("date", "")
            url_path = f"/main/news/detail/{news_id}"

            safe_title = html.escape(title)
            safe_url = html.escape(url_path)
            safe_date = html.escape(date)

            html_parts.append(
                f'<li class="news__item">'
                f'<a href="{safe_url}" class="news__title">'
                f'<h3 title="{safe_title}">{safe_title}</h3>'
                f'</a>'
                f'<div class="news__date">{safe_date}</div>'
                f'</li>'
            )

        html_parts.append('</ul></body></html>')
        return ''.join(html_parts)

    def _process_page(self, page: Page) -> str:
        """处理页面：自动拦截API → 失败则HAR回退"""
        self._setup_api_interception(page)

        page.goto(self.config.url, timeout=self.config.timeout)
        page.wait_for_load_state("networkidle")
        time.sleep(self.config.wait_seconds)

        # 滚动触发API请求
        self._scroll_for_data(page)

        # 检查API数据
        if self._api_data:
            print(f"\n[OK] API拦截成功，共 {len(self._api_data)} 条新闻")
            return self._build_html_from_api_data(self._api_data)

        # API未获取到数据，检查HAR
        print("\n[WARN] 自动检测API未获取到数据")
        har_path = find_har_file(self.config.scraper_name)
        if har_path:
            print(f"[INFO] 检测到HAR文件: {har_path}")
            print("[INFO] 请删除HAR文件后重新运行，或手动检查API配置")
        else:
            print_har_instructions(
                self.config.scraper_name,
                self.config.url,
                ["bbs-api.miyoushe.com", "api.mihoyo.com"]
            )

        # 回退到DOM抓取
        print("[INFO] 回退到DOM抓取模式...")
        return page.content()

    def _scroll_for_data(self, page: Page) -> None:
        """滚动页面触发API请求"""
        scroll_delay = self.config.scroll_delay
        last_height = page.evaluate("document.body.scrollHeight")
        attempts = 0
        max_attempts = 5

        while not self._api_stop_requested:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(scroll_delay)

            try:
                load_more_selector = "li.news__more, li.recommend__more"
                locator = page.locator(load_more_selector)
                if locator.count() > 0 and locator.is_visible():
                    page.click(load_more_selector)
                    page.wait_for_timeout(2000)
            except Exception:
                pass

            new_height = page.evaluate("document.body.scrollHeight")

            if self._api_stop_requested:
                break

            if new_height == last_height:
                attempts += 1
                if attempts >= max_attempts:
                    print("[INFO] 页面高度不再变化，停止滚动")
                    break
            else:
                attempts = 0

            last_height = new_height


@handle_errors
@retry(max_attempts=config_manager.get("retry_settings.max_attempts", 3),
       delay=config_manager.get("retry_settings.delay", 2.0))
def run(incremental: bool = False):
    """运行新闻抓取，支持增量模式"""
    mode = "增量" if incremental else "全量"
    print(f"\n[START] {mode}抓取原神新闻页面")

    scraper = NewsScraper(incremental=incremental)
    html_content = scraper.run()

    if html_content:
        print("[OK] 原神新闻页面抓取完成")
        return html_content
    else:
        print("[ERROR] 原神新闻页面抓取失败")
        return None


if __name__ == "__main__":
    run()
