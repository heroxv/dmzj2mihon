import requests
import json
import time


def get_all_subscriptions(big_cat_id, letter_filter, status_id, user_id, token, max_retries=3, retry_delay=2):
    url = "https://v3api.dmzj.com/UCenter/subscribe"
    all_subscriptions = []
    page = 0

    while True:
        retries = 0
        while retries < max_retries:
            try:
                params = {
                    "type": big_cat_id,
                    "letter": letter_filter,
                    "sub_type": status_id,
                    "page": page,
                    "uid": user_id,
                    "dmzj_token": token
                }

                response = requests.get(url, params=params)

                if response.status_code == 200:
                    data = response.json()
                    if not data:
                        print(f"所有数据爬取完成，总页数：{page}")
                        return all_subscriptions

                    all_subscriptions.extend(data)
                    print(f"已爬取第 {page} 页，共 {len(data)} 条数据")
                    page += 1
                    break
                else:
                    print(f"请求失败，状态码: {response.status_code}")
                    retries += 1
                    if retries < max_retries:
                        print(f"重试第 {retries} 次...")
                        time.sleep(retry_delay)
                    else:
                        print(f"多次重试失败，停止爬取")
                        return all_subscriptions

            except requests.exceptions.RequestException as e:
                print(f"请求异常：{e}")
                retries += 1
                if retries < max_retries:
                    print(f"重试第 {retries} 次...")
                    time.sleep(retry_delay)
                else:
                    print(f"多次重试失败，停止爬取")
                    return all_subscriptions


def convert_subscription(subscription):
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


def format_backup_data(subscriptions):
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


def main():
    big_cat_id = 0
    letter_filter = "all"
    status_id = 1
    user_id = ""
    token = ""

    all_subscriptions = get_all_subscriptions(
        big_cat_id, letter_filter, status_id, user_id, token)

    if all_subscriptions:
        print(f"共获取到 {len(all_subscriptions)} 条订阅数据")
        with open("all_subscriptions.json", "w", encoding="utf-8") as f:
            json.dump(all_subscriptions, f, ensure_ascii=False, indent=2)
    else:
        print("未获取到任何数据")

    converted_subscriptions = [convert_subscription(
        sub) for sub in all_subscriptions]
    backup_data = format_backup_data(converted_subscriptions)

    with open('backup_data.json', 'w', encoding='utf-8') as output_file:
        json.dump(backup_data, output_file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
