import requests
import json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# 测试用的标签ID
test_tag_id = 46  # 临床科室

# 尝试多种可能的接口格式
possible_urls = [
    f"https://www.lhqzy.com/news_data/data/news/list?tag_id={test_tag_id}",
    f"https://www.lhqzy.com/news_data/data/list?tag_id={test_tag_id}",
    f"https://www.lhqzy.com/news_data/tag/news_list/{test_tag_id}",
    f"https://www.lhqzy.com/news_data/tag/list/{test_tag_id}",
    f"https://www.lhqzy.com/news_data/data/tag_list/{test_tag_id}",
    f"https://www.lhqzy.com/news_data/data/news_list/{test_tag_id}",
    f"https://www.lhqzy.com/news_data/news/list?tag_id={test_tag_id}",
    f"https://www.lhqzy.com/news_data/data/index?tag_id={test_tag_id}",
    f"https://www.lhqzy.com/news_data/data/news?tag_id={test_tag_id}",
]

print("测试不同的接口格式...\n")
print("="*60)

for url in possible_urls:
    try:
        print(f"\n测试: {url}")
        resp = requests.get(url, headers=headers, timeout=5)
        
        if resp.status_code == 200:
            print(f"  ✅ 状态码: 200")
            try:
                data = resp.json()
                print(f"  📋 返回数据结构: {list(data.keys()) if isinstance(data, dict) else '列表'}")
                
                # 尝试找到文章列表
                if isinstance(data, dict):
                    for key in ['data', 'list', 'news_list', 'articles']:
                        if key in data and isinstance(data[key], list):
                            print(f"  📰 找到文章列表 (键: '{key}')，共 {len(data[key])} 篇")
                            if len(data[key]) > 0:
                                print(f"  第一篇文章: {json.dumps(data[key][0], ensure_ascii=False, indent=2)[:200]}")
                            break
                elif isinstance(data, list):
                    print(f"  📰 直接是文章列表，共 {len(data)} 篇")
                    if len(data) > 0:
                        print(f"  第一篇文章: {json.dumps(data[0], ensure_ascii=False, indent=2)[:200]}")
            except:
                print(f"  ⚠️  响应不是JSON格式")
                print(f"  内容预览: {resp.text[:200]}")
        else:
            print(f"  ❌ 状态码: {resp.status_code}")
            
    except Exception as e:
        print(f"  ❌ 错误: {e}")

print("\n" + "="*60)
print("\n提示：如果以上都不行，请在浏览器中点击一个标签，")
print("然后查看 Network 面板中的请求URL和参数")
