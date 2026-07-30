from .user import UserScraper, run as run_user
from .baike import BaikeScraper, run as run_baike
from .news import NewsScraper, run as run_news
from .tutorial import TutorialScraper, run as run_tutorial
from .custom import CustomScraper, run as run_custom
from .weibo import WeiboScraper, run as run_weibo

__all__ = [
    "UserScraper",
    "BaikeScraper",
    "NewsScraper",
    "TutorialScraper",
    "CustomScraper",
    "WeiboScraper",
    "run_user",
    "run_baike",
    "run_news",
    "run_tutorial",
    "run_custom",
    "run_weibo",
]
