import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class OutputDirs:
    html: str = "data/html"
    images: str = "data/images"
    data: str = "data/results"


@dataclass
class Filenames:
    user_html: str = "user_posts.html"
    baike_html: str = "character_list.html"
    image_urls: str = "image_urls.txt"
    posts_data: str = "posts.txt"
    weibo_html: str = "weibo_posts.html"
    weibo_data: str = "weibo.txt"


@dataclass
class ScrollSettings:
    delay: float = 2.0
    max_scroll_attempts: int = 50


@dataclass
class RetrySettings:
    max_attempts: int = 3
    delay: float = 2.0


@dataclass
class IncrementalSettings:
    """增量更新配置"""
    enabled: bool = True  # 是否启用增量更新
    stop_on_existing: bool = True  # 遇到已存在数据时停止滚动
    merge_data: bool = True  # 是否合并新旧数据


@dataclass
class BackupSettings:
    """备份配置"""
    enabled: bool = True  # 是否启用备份
    max_backups: int = 10  # 最大备份数量
    backup_dir: str = "data/backups"  # 备份目录


class ConfigManager:
    """配置管理器，负责配置文件的加载、保存和访问"""
    
    def __init__(self, config_file: str = "config.json") -> None:
        self.config_file: str = config_file
        self.base_dir: str = os.path.dirname(os.path.dirname(__file__))
        self.config_path: str = os.path.join(self.base_dir, config_file)
        
        self.default_config: Dict[str, Any] = self._get_default_config()
        self.config: Dict[str, Any] = self.default_config.copy()
        
        self.load_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "user_url": "https://www.miyoushe.com/ys/accountCenter/postList?id=75276539",
            "baike_url": "https://baike.mihoyo.com/ys/obc/channel/map/189/25",
            "weibo_url": "https://weibo.com/u/6593199887",
            "headless": False,
            "wait_seconds": 3,
            "timeout": 120000,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "output_dirs": asdict(OutputDirs()),
            "filenames": asdict(Filenames()),
            "browser_args": ["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"],
            "scroll_settings": asdict(ScrollSettings()),
            "retry_settings": asdict(RetrySettings()),
            "incremental_settings": asdict(IncrementalSettings()),
            "backup_settings": asdict(BackupSettings()),
            "weibo_settings": {
                "use_firefox_cookies": True
            },
            "miyoushe_settings": {
                "use_firefox_cookies": True
            }
        }
    
    def load_config(self) -> None:
        """加载配置文件"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    self._deep_update(self.config, user_config)
                print(f"[OK] 已加载配置文件: {self.config_path}")
            except json.JSONDecodeError as e:
                print(f"[WARN] 配置文件格式错误，使用默认配置: {e}")
            except IOError as e:
                print(f"[WARN] 读取配置文件失败，使用默认配置: {e}")
            except Exception as e:
                print(f"[WARN] 加载配置文件时发生未知错误，使用默认配置: {e}")
        else:
            print(f"[INFO] 配置文件不存在，创建默认配置: {self.config_path}")
            self.save_config()
    
    def save_config(self) -> None:
        """保存配置文件"""
        try:
            config_dir = os.path.dirname(self.config_path)
            if config_dir:
                os.makedirs(config_dir, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            print(f"[OK] 配置文件已保存: {self.config_path}")
        except IOError as e:
            print(f"[ERROR] 保存配置文件失败: {e}")
        except Exception as e:
            print(f"[ERROR] 保存配置文件时发生未知错误: {e}")
    
    def _deep_update(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """深度更新配置字典"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_update(target[key], value)
            else:
                target[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值，支持点号分隔的嵌套路径"""
        keys = key.split('.')
        value: Any = self.config
        try:
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            return value
        except Exception:
            return default
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值，支持点号分隔的嵌套路径"""
        keys = key.split('.')
        config = self.config
        try:
            for k in keys[:-1]:
                if k not in config or not isinstance(config[k], dict):
                    config[k] = {}
                config = config[k]
            config[keys[-1]] = value
        except Exception as e:
            print(f"[WARN] 设置配置失败: {e}")
    
    def get_output_dir(self, dir_type: str) -> str:
        """获取输出目录路径"""
        dir_path = self.get(f"output_dirs.{dir_type}")
        if not dir_path:
            dir_path = dir_type
        
        full_path = os.path.join(self.base_dir, dir_path)
        os.makedirs(full_path, exist_ok=True)
        return full_path
    
    def get_filename(self, file_type: str) -> str:
        """获取文件名"""
        return self.get(f"filenames.{file_type}", "")
    
    def get_scraper_config(self, url: str, output_filename: str) -> Dict[str, Any]:
        """获取抓取器配置"""
        return {
            "url": url,
            "output_filename": output_filename,
            "headless": self.get("headless", False),
            "wait_seconds": self.get("wait_seconds", 3),
            "timeout": self.get("timeout", 120000),
            "user_agent": self.get("user_agent"),
            "browser_args": self.get("browser_args", []),
            "scroll_delay": self.get("scroll_settings.delay", 2.0)
        }


config_manager = ConfigManager()
