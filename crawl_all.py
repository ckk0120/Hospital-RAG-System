import requests
import json
import time
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0"
}

# 首页接口
INDEX_API = "https://www.lhqzy.com/news_data/data/index"

# 详情接口前缀
DETAIL_API = "https://www.lhqzy.com/news_data/data/news/detail/"

# 获取首页数据
resp = requests.get(INDEX_API, headers=headers)

data = resp.json()["data"]

all_articles = []

# 所有栏目
sections = [
    ("hospital_news", "医院动态"),
    ("jkys_list", "健康养生"),
    ("ywgk_list", "院务公开"),
    ("djwh_list", "党建文化")
]

for section_name, section_title in sections:

    print(f"\n开始抓取栏目: {section_title}")

    # hospital_news 结构特殊
    if section_name == "hospital_news":
        news_list = data[section_name]["news_list"]
    else:
        news_list = data[section_name]

    for item in news_list:

        news_id = item["news_id"]

        detail_url = DETAIL_API + str(news_id)

        print(f"正在抓取: {item['title']}")

        try:

            detail_resp = requests.get(
                detail_url,
                headers=headers,
                timeout=10
            )

            detail_json = detail_resp.json()

            detail_data = detail_json["data"]

            html_content = detail_data["content"]

            # HTML转纯文本
            soup = BeautifulSoup(html_content, "html.parser")

            text = soup.get_text("\n", strip=True)

            article = {
                "news_id": news_id,
                "栏目": section_title,
                "标题": detail_data["title"],
                "发布时间": detail_data["add_time"],
                "正文": text
            }

            all_articles.append(article)

            time.sleep(0.5)

        except Exception as e:

            print(f"抓取失败: {news_id}")
            print(e)

# 保存
with open("hospital_articles.json", "w", encoding="utf-8") as f:

    json.dump(
        all_articles,
        f,
        ensure_ascii=False,
        indent=2
    )

print(f"\n抓取完成，共 {len(all_articles)} 篇文章")