import re
import os
from typing import List, Set
from dataclasses import dataclass
from core.config_manager import config_manager
from utils.error_handler import handle_errors, ErrorHandler
from utils.backup_manager import backup_manager


@dataclass
class NewsData:
    title: str
    url: str
    date: str
    index: int = 0

    def __hash__(self):
        return hash((self.title, self.url, self.date))


class NewsExtractor:
    def __init__(self):
        self.base_dir = os.path.dirname(__file__)
        self.html_path = os.path.join(
            config_manager.get_output_dir("html"),
            "news_page.html"
        )
        self.output_dir = config_manager.get_output_dir("data")
        self.output_path = os.path.join(
            self.output_dir,
            "news.txt"
        )

    def load_existing_data(self) -> List[NewsData]:
        """加载已存在的数据"""
        if not os.path.exists(self.output_path):
            return []

        try:
            with open(self.output_path, "r", encoding="utf-8") as f:
                content = f.read()

            items = []
            pattern = re.compile(r'\d{4}-(.+?)-\[(.+?)\]-\((https://.+?)\)')

            for match in pattern.findall(content):
                title = match[0].strip()
                date = match[1]
                url = match[2]
                items.append(NewsData(title=title, url=url, date=date))

            print(f"[INFO] 已加载 {len(items)} 条旧数据")
            return items

        except Exception as e:
            print(f"[WARN] 加载旧数据失败: {e}")
            return []

    def get_existing_urls(self) -> Set[str]:
        """获取已存在的URL集合"""
        existing_data = self.load_existing_data()
        return {item.url for item in existing_data}

    def extract_news(self, html_content: str = None, incremental: bool = False) -> List[NewsData]:
        if html_content is None:
            if not ErrorHandler.validate_file_exists(self.html_path):
                return []

            with open(self.html_path, "r", encoding="utf-8") as f:
                html_content = f.read()

        pattern = re.compile(
            r'<li class="news__item[^"]*">\s*<a href="(/main/news/detail/\d+)"[^>]*class="news__title[^"]*"[^>]*>'
            r'.*?<h3[^>]*title="([^"]*)"[^>]*>([^<]+)</h3>.*?'
            r'<div class="news__date">([^<]+)</div>',
            re.DOTALL
        )

        items = []
        for match in pattern.findall(html_content):
            url_path = match[0]
            title_attr = match[1]
            title_text = match[2].strip()
            date = match[3].strip()

            url = f"https://ys.mihoyo.com{url_path}"
            title = title_attr if title_attr else title_text
            title = re.sub(r'\s+', ' ', title)

            if not any(item.title == title and item.url == url and item.date == date for item in items):
                items.append(NewsData(title=title, url=url, date=date))

        if not items:
            print("[WARN] 使用宽松模式重新匹配")
            pattern_loose = re.compile(
                r'<li class="news__item[^"]*">.*?'
                r'<a href="(/main/news/detail/\d+)"[^>]*class="news__title[^"]*"[^>]*>'
                r'.*?<h3[^>]*>([^<]+)</h3>.*?'
                r'<div class="news__date">([^<]+)</div>',
                re.DOTALL
            )

            for match in pattern_loose.findall(html_content):
                url_path = match[0]
                title_text = match[1].strip()
                date = match[2].strip()

                url = f"https://ys.mihoyo.com{url_path}"
                title = re.sub(r'\s+', ' ', title_text)

                if not any(item.title == title and item.url == url and item.date == date for item in items):
                    items.append(NewsData(title=title, url=url, date=date))

        # 增量合并模式
        if incremental and config_manager.get("incremental_settings.merge_data", True):
            existing_data = self.load_existing_data()
            items = self._merge_data(existing_data, items)
            print(f"[INFO] 增量合并完成，共 {len(items)} 条数据")

        items = sorted(set(items), key=lambda x: x.date, reverse=True)

        for idx, item in enumerate(items, 1):
            item.index = idx

        print(f"[INFO] 成功提取 {len(items)} 条新闻")

        if items:
            print(f"[INFO] 第一条新闻: {items[0].date} - {items[0].title}")
            print(f"[INFO] 最后一条新闻: {items[-1].date} - {items[-1].title}")

        return items

    def _merge_data(self, old_data: List[NewsData], new_data: List[NewsData]) -> List[NewsData]:
        """合并新旧数据"""
        # 使用URL作为唯一标识去重
        merged = {item.url: item for item in old_data}

        # 新数据覆盖旧数据（保持最新）
        for item in new_data:
            merged[item.url] = item

        return list(merged.values())

    def save_news_data(self, news_data: List[NewsData]) -> bool:
        if not ErrorHandler.validate_directory_exists(self.output_dir):
            return False

        # 备份旧数据
        if config_manager.get("backup_settings.enabled", True) and os.path.exists(self.output_path):
            backup_manager.create_backup(self.output_path)

        lines = []
        for item in news_data:
            lines.append(f"{item.index:04d}-{item.title}-[{item.date}]-({item.url})")

        try:
            with open(self.output_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            return True
        except Exception as e:
            print(f"[ERROR] 保存新闻数据失败: {e}")
            return False


@handle_errors
def run(incremental: bool = False):
    """运行新闻提取，支持增量模式"""
    mode = "增量" if incremental else "全量"
    print(f"\n[START] {mode}提取新闻数据")

    extractor = NewsExtractor()
    news_data = extractor.extract_news(incremental=incremental)

    if not news_data:
        print("[ERROR] 未找到新闻数据或HTML文件不存在")
        return

    if extractor.save_news_data(news_data):
        print(f"[OK] 完成！共 {len(news_data)} 条新闻")
        print(f"[OK] 已保存到：{extractor.output_path}")
    else:
        print("[ERROR] 保存新闻数据失败")


if __name__ == "__main__":
    run()
