"""
新闻抓取模块
支持原神、绝区零、星穹铁道的新闻页面抓取
基于 content_v2_user 统一 API 架构
"""

from .base import GameNewsBaseScraper
from .genshin import GenshinNewsScraper, run as run_news_genshin
from .zzz import ZZZNewsScraper, run as run_news_zzz
from .starrail import SRNewsScraper, run as run_news_starrail

__all__ = [
    "GameNewsBaseScraper",
    "GenshinNewsScraper",
    "ZZZNewsScraper",
    "SRNewsScraper",
    "run_news_genshin",
    "run_news_zzz",
    "run_news_starrail",
]
