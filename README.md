# 米游社工具箱 / miHoYo ToolKit

> 基于 Playwright 的米游社 & 微博数据抓取工具

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Playwright-1.40%2B-45ba4b?logo=playwright&logoColor=white)](https://playwright.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Version](https://img.shields.io/badge/version-RV1.0.0-green)

**[快速开始](#快速开始)** ·
**[功能列表](#功能列表)** ·
**[配置说明](#配置说明)** ·
**[项目结构](#项目结构)**

[中文](#中文文档) / [English](#english-docs)

---

## ✨ 核心特性

- **API 拦截抓取** — 自动拦截浏览器 API 响应，绕过虚拟滚动，数据完整无遗漏
- **Firefox 免登录** — 读取 Firefox Cookie 自动注入，无需每次手动登录
- **HAR 智能回退** — API 检测失败时，自动指引提供 HAR 文件辅助分析
- **增量更新** — 检测已存在数据自动停止，支持合并与自动备份
- **模块化架构** — 抓取器 / 提取器分离，配置驱动，易于扩展

---

## 中文文档

### 快速开始

```bash
# 1. 克隆项目
git clone https://github.com/vers123/miHoYo_ToolKit.git
cd miHoYo_ToolKit

# 2. 创建并激活虚拟环境
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# 3. 安装依赖
pip install -r requirements.txt
playwright install chromium

# 4. 运行
python main.py
```

### 功能列表

程序启动后输入对应序号执行功能，输入 `0` 退出程序。

| 序号 | 功能 | 说明 |
| :---: | ------ | ------ |
| 1 | 抓取用户发帖主页 | 从米游社抓取指定用户的发帖记录 |
| 2 | 增量抓取用户发帖 | 增量更新用户发帖，自动备份旧数据 |
| 3 | 抓取角色图鉴页面 | 从米游社百科抓取角色图鉴信息 |
| 4 | 抓取原神新闻页面 | 从原神官网抓取新闻页面 |
| 5 | 增量抓取原神新闻 | 增量更新原神新闻，自动备份旧数据 |
| 6 | 抓取米游社教程页面 | 从米游社抓取教程页面 |
| 7 | 提取教程角色数据 | 从教程页面提取角色编号和名称 |
| 8 | 抓取自定义网站 | 抓取任意网站的HTML页面 |
| 9 | 提取图鉴图片链接 | 从抓取的图鉴页面提取角色图片链接 |
| 10 | 提取用户发帖时间 | 从用户主页提取发帖时间和标题 |
| 11 | 增量提取用户发帖 | 增量提取并合并新旧数据 |
| 12 | 提取原神新闻数据 | 从新闻页面提取标题和链接 |
| 13 | 增量提取新闻数据 | 增量提取并合并新旧数据 |
| 14 | 抓取微博用户主页 | 从微博抓取指定用户的发帖记录 |
| 15 | 增量抓取微博用户 | 增量更新微博用户发帖，自动备份旧数据 |
| 16 | 提取微博数据 | 从微博页面提取发帖时间和内容 |
| 17 | 增量提取微博数据 | 增量提取并合并新旧微博数据 |
| 18 | 查看备份文件 | 查看所有数据备份文件 |
| 19 | 恢复备份数据 | 从备份文件恢复数据 |
| 20 | 查看当前配置 | 显示当前的配置信息 |
| 21 | 修改配置参数 | 修改URL、超时时间等配置 |
| 22 | 重新加载配置 | 从配置文件重新加载配置 |
| 23 | 系统信息 | 显示系统环境和依赖信息 |
| 0 | 退出程序 | 退出米游社工具箱 |

### 配置说明

配置文件：`config.json`

```json
{
  "user_url": "https://www.miyoushe.com/ys/accountCenter/postList?id=75276539",
  "baike_url": "https://baike.mihoyo.com/ys/obc/channel/map/189/25",
  "weibo_url": "https://weibo.com/u/6593199887",
  "headless": false,
  "wait_seconds": 3,
  "timeout": 120000,
  "weibo_settings": { "use_firefox_cookies": true },
  "miyoushe_settings": { "use_firefox_cookies": true }
}
```

#### Cookie 免登录

在 Firefox 中登录米游社 / 微博后，程序自动读取 `cookies.sqlite` 并注入到 Playwright，无需手动登录。

#### HAR 回退

API 自动检测失败时，程序会打印详细步骤指引导出 HAR 文件。将 HAR 文件放入对应 `har/{scraper_name}/` 目录后重新运行即可。

> `har/` 目录及子目录会在首次使用时自动创建。

### 项目结构

```text
miHoYo_ToolKit/
├── main.py               # 主程序入口
├── config.json           # 配置文件
├── requirements.txt      # 依赖
├── core/                 # 核心模块
│   ├── scraper.py        # 抓取器基类（API拦截 + Cookie + HAR回退）
│   └── config_manager.py # 配置管理
├── fetchers/             # 抓取模块
│   ├── user.py           # 米游社用户发帖
│   ├── news.py           # 原神新闻
│   ├── weibo.py          # 微博用户主页
│   ├── baike.py          # 角色图鉴
│   ├── tutorial.py       # 教程页面
│   └── custom.py         # 自定义网站
├── extractors/           # 提取模块
│   ├── time.py           # 发帖时间
│   ├── news.py           # 新闻数据
│   ├── weibo.py          # 微博数据
│   ├── images.py         # 图片链接
│   └── tutorial.py       # 教程数据
├── utils/                # 工具模块
│   ├── cookie_loader.py  # Firefox Cookie 读取
│   ├── har_loader.py     # HAR 文件解析
│   ├── backup_manager.py # 备份管理
│   ├── error_handler.py  # 错误处理
│   └── logger.py         # 日志系统
├── tests/                # 测试
├── data/                 # 输出数据（自动创建）
└── logs/                 # 日志（自动创建）
```

### 测试

```bash
python -m unittest tests.test_extractors -v
```

---

## English Docs

### Quick Start

```bash
# 1. Clone
git clone https://github.com/vers123/miHoYo_ToolKit.git
cd miHoYo_ToolKit

# 2. Create & activate venv
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 4. Run
python main.py
```

### Feature List

Enter the corresponding number to execute. Enter `0` to exit.

| # | Feature | Description |
| :-: | --------- | ------------- |
| 1 | Fetch User Posts | Fetch user posts from miyoushe.com |
| 2 | Incremental Fetch User Posts | Incremental update with auto backup |
| 3 | Fetch Character Encyclopedia | Fetch character info from miHoYo Baike |
| 4 | Fetch Genshin News | Fetch news from Genshin official site |
| 5 | Incremental Fetch News | Incremental news update with auto backup |
| 6 | Fetch Tutorial Pages | Fetch tutorial pages from miyoushe.com |
| 7 | Extract Tutorial Data | Extract character IDs and names from tutorials |
| 8 | Fetch Custom Sites | Scrape HTML from any website |
| 9 | Extract Image URLs | Extract character image URLs from encyclopedia |
| 10 | Extract Post Timestamps | Extract post time and title from user profile |
| 11 | Incremental Extract Posts | Incremental extraction with data merge |
| 12 | Extract News Data | Extract titles and links from news pages |
| 13 | Incremental Extract News | Incremental extraction with data merge |
| 14 | Fetch Weibo Posts | Fetch user posts from weibo.com |
| 15 | Incremental Fetch Weibo | Incremental Weibo update with auto backup |
| 16 | Extract Weibo Data | Extract post time and content from Weibo |
| 17 | Incremental Extract Weibo | Incremental extraction with data merge |
| 18 | View Backups | View all data backup files |
| 19 | Restore Backup | Restore data from backup files |
| 20 | View Config | Display current configuration |
| 21 | Modify Config | Modify URLs, timeout and other settings |
| 22 | Reload Config | Reload configuration from file |
| 23 | System Info | Display system environment and dependencies |
| 0 | Exit | Exit the program |

### Configuration

Config file: `config.json`

```json
{
  "user_url": "https://www.miyoushe.com/ys/accountCenter/postList?id=75276539",
  "baike_url": "https://baike.mihoyo.com/ys/obc/channel/map/189/25",
  "weibo_url": "https://weibo.com/u/6593199887",
  "headless": false,
  "wait_seconds": 3,
  "timeout": 120000,
  "weibo_settings": { "use_firefox_cookies": true },
  "miyoushe_settings": { "use_firefox_cookies": true }
}
```

#### Cookie Auto-Login

Log in to miyoushe.com / weibo.com in Firefox, then the program reads `cookies.sqlite` and injects cookies into Playwright automatically.

#### HAR Fallback

When API auto-detection fails, the program prints step-by-step instructions to export a HAR file. Place it in the corresponding `har/{scraper_name}/` directory and re-run.

> The `har/` directory and subdirectories are created automatically on first use.

### Project Structure

Same as the Chinese section above — see [项目结构](#项目结构).

### Testing

```bash
python -m unittest tests.test_extractors -v
```

---

**RV1.0.0** · Licensed under [MIT](LICENSE) · Maintained by LingLan
