"""
新闻提取模块
支持原神、绝区零、星穹铁道的新闻数据提取
基于 content_v2_user 统一 API 架构生成的 HTML
"""

from .base import GameNewsBaseExtractor, NewsItem
from .genshin import GenshinNewsExtractor, run as run_extract_news_genshin
from .zzz import ZZZNewsExtractor, run as run_extract_news_zzz
from .starrail import SRNewsExtractor, run as run_extract_news_starrail

__all__ = [
    "GameNewsBaseExtractor",
    "NewsItem",
    "GenshinNewsExtractor",
    "ZZZNewsExtractor",
    "SRNewsExtractor",
    "run_extract_news_genshin",
    "run_extract_news_zzz",
    "run_extract_news_starrail",
]
