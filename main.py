import requests
import json
import time
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import concurrent.futures
import yaml

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('subscription_backup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class Config:
    """配置数据类"""
    big_cat_id: int
    letter_filter: str
    status_id: int
    user_id: str
    token: str
    max_retries: int = 3
    retry_delay: int = 2
    max_workers: int = 5

    @classmethod
    def from_yaml(cls, path: str) -> 'Config':
        """从YAML文件加载配置"""
        with open(path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        return cls(**config_data)


class SubscriptionFetcher:
    """订阅数据获取类"""

    def __init__(self, config: Config):
        self.config = config
        self.session = requests.Session()
        self.base_url = "https://v3api.dmzj.com/UCenter/subscribe"

    def _get_page(self, page: int) -> Optional[List[Dict]]:
        """获取单页订阅数据"""
        params = {
            "type": self.config.big_cat_id,
            "letter": self.config.letter_filter,
            "sub_type": self.config.status_id,
            "page": page,
            "uid": self.config.user_id,
            "dmzj_token": self.config.token
        }

        for attempt in range(self.config.max_retries):
            try:
                response = self.session.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()

                if not data:
                    return None

                return data

            except requests.exceptions.RequestException as e:
                logger.warning(f"第 {attempt + 1} 次请求失败: {e}")
                if attempt < self.config.max_retries - 1:
                    time.sleep(self.config.retry_delay)
                else:
                    logger.error(f"页面 {page} 获取失败")
                    raise

    def get_all_subscriptions(self) -> List[Dict]:
        """获取所有订阅数据"""
        all_subscriptions = []
        page = 0

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            future_to_page = {}

            while True:
                future = executor.submit(self._get_page, page)
                future_to_page[future] = page

                if len(future_to_page) >= self.config.max_workers:
                    completed, _ = concurrent.futures.wait(
                        future_to_page.keys(),
                        return_when=concurrent.futures.FIRST_COMPLETED
                    )

                    for future in completed:
                        page_num = future_to_page[future]
                        try:
                            data = future.result()
                            if data is None:
                                return all_subscriptions

                            all_subscriptions.extend(data)
                            logger.info(f"已获取第 {page_num} 页，{len(data)} 条数据")
                            del future_to_page[future]
                        except Exception as e:
                            logger.error(f"处理页面 {page_num} 时发生错误: {e}")
                            return all_subscriptions

                page += 1


class SubscriptionConverter:
    """订阅数据转换类"""
    @staticmethod
    def convert_subscription(subscription: Dict) -> Dict:
        """转换单个订阅数据"""
        return {
            "source": "2884190037559093788",
            "url": f"/comic/comic_{subscription['id']}.json?version=2.7.019",
            "title": subscription["name"],
            "author": "漫画作者",
            "description": "（描述内容）",
            "genre": [],
            "status": 1 if subscription["status"] == "连载中" else 0,
            "thumbnailUrl": subscription["sub_img"],
            "dateAdded": str(subscription["sub_uptime"]),
            "chapters": [],
            "categories": ["1"],
            "viewerFlags": 0,
            "lastModifiedAt": str(subscription["sub_uptime"]),
            "favoriteModifiedAt": str(subscription["sub_uptime"])
        }

    @staticmethod
    def format_backup_data(subscriptions: List[Dict]) -> Dict:
        """格式化备份数据"""
        return {
            "backupManga": subscriptions,
            "backupCategories": [
                {
                    "name": "动漫之家",
                    "order": "1",
                    "flags": "4"
                }
            ],
            "backupSources": [
                {
                    "name": "本地图源",
                    "sourceId": "0"
                },
                {
                    "name": "动漫之家",
                    "sourceId": "2884190037559093788"
                }
            ],
            "backupExtensionRepo": [
                {
                    "baseUrl": "https://raw.githubusercontent.com/keiyoushi/extensions/repo",
                    "name": "Keiyoushi",
                    "website": "https://keiyoushi.github.io",
                    "signingKeyFingerprint": "9add655a78e96c4ec7a53ef89dccb557cb5d767489fac5e785d671a5a75d4da2"
                }
            ]
        }


class BackupManager:
    """备份管理类"""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_raw_data(self, data: List[Dict]):
        """保存原始数据"""
        output_path = self.output_dir / "all_subscriptions.json"
        self._save_json(data, output_path)
        logger.info(f"原始数据已保存至 {output_path}")

    def save_backup(self, data: Dict):
        """保存备份数据"""
        output_path = self.output_dir / "backup_data.json"
        self._save_json(data, output_path)
        logger.info(f"备份数据已保存至 {output_path}")

    @staticmethod
    def _save_json(data: Any, path: Path):
        """保存JSON数据"""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)


def main():
    try:
        # 加载配置
        config = Config.from_yaml('config.yaml')

        # 创建输出目录
        output_dir = Path('output')
        backup_manager = BackupManager(output_dir)

        # 获取订阅数据
        fetcher = SubscriptionFetcher(config)
        subscriptions = fetcher.get_all_subscriptions()

        if not subscriptions:
            logger.error("未获取到任何数据")
            return

        logger.info(f"共获取到 {len(subscriptions)} 条订阅数据")

        # 保存原始数据
        backup_manager.save_raw_data(subscriptions)

        # 转换并保存备份数据
        converter = SubscriptionConverter()
        converted_subscriptions = [
            converter.convert_subscription(sub) for sub in subscriptions
        ]
        backup_data = converter.format_backup_data(converted_subscriptions)
        backup_manager.save_backup(backup_data)

        logger.info("数据处理完成")

    except Exception as e:
        logger.exception(f"程序执行出错: {e}")


if __name__ == "__main__":
    main()
