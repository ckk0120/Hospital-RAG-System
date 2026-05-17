import requests
import json
import time
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# 标签数据接口（获取标签树结构）
TAG_API = "https://www.lhqzy.com/news_data/tag/data"

# 根据标签ID获取文章列表的接口（需要确认具体接口）
# 假设格式为: https://www.lhqzy.com/news_data/tag/news_list/{tag_id}
TAG_NEWS_LIST_API = "https://www.lhqzy.com/news_data/tag/news_list/"

# 文章详情接口
DETAIL_API = "https://www.lhqzy.com/news_data/data/news/detail/"

print("="*60)
print("开始爬取标签文章数据...")
print("="*60)

try:
    # ========== 第一步：获取标签树结构 ==========
    print("\n[1/4] 正在获取标签树结构...")
    resp = requests.get(TAG_API, headers=headers, timeout=10)
    resp.raise_for_status()
    
    data = resp.json()
    tag_list = data.get('data', [])
    
    print(f"✅ 共找到 {len(tag_list)} 个一级标签")
    
    # 递归提取所有叶子节点标签（没有子节点的标签）
    def extract_leaf_tags(tags, parent_name=""):
        """递归提取所有叶子节点标签"""
        leaf_tags = []
        for tag in tags:
            current_path = f"{parent_name} > {tag['tag_name']}" if parent_name else tag['tag_name']
            
            if tag.get('hasChild') and tag.get('children'):
                # 有子节点，递归处理
                leaf_tags.extend(extract_leaf_tags(tag['children'], current_path))
            else:
                # 叶子节点，添加到列表
                leaf_tags.append({
                    'tag_id': tag['tag_id'],
                    'tag_name': tag['tag_name'],
                    'full_path': current_path
                })
        return leaf_tags
    
    leaf_tags = extract_leaf_tags(tag_list)
    print(f"✅ 共找到 {len(leaf_tags)} 个叶子标签（最终分类）")
    
    # 打印所有叶子标签
    print("\n📋 叶子标签列表：")
    for idx, tag in enumerate(leaf_tags, 1):
        print(f"  {idx}. {tag['full_path']} (ID: {tag['tag_id']})")
    
    # ========== 第二步：遍历每个标签，获取文章列表 ==========
    print(f"\n[2/4] 开始获取各标签下的文章...")
    print("-" * 60)
    
    all_articles = []
    total_news_count = 0
    
    for tag_idx, tag in enumerate(leaf_tags, 1):
        tag_id = tag['tag_id']
        tag_name = tag['tag_name']
        full_path = tag['full_path']
        
        print(f"\n[{tag_idx}/{len(leaf_tags)}] 正在获取标签 '{full_path}' 的文章列表...")
        
        try:
            # 尝试不同的接口格式
            news_list_url = f"{TAG_NEWS_LIST_API}{tag_id}"
            news_resp = requests.get(news_list_url, headers=headers, timeout=10)
            
            if news_resp.status_code != 200:
                print(f"   ⚠️  接口返回状态码: {news_resp.status_code}，跳过此标签")
                continue
            
            news_data = news_resp.json()
            
            # 尝试提取文章列表
            articles_in_tag = None
            if isinstance(news_data, dict):
                for key in ['data', 'list', 'news_list', 'articles', 'result']:
                    if key in news_data:
                        articles_in_tag = news_data[key]
                        break
            elif isinstance(news_data, list):
                articles_in_tag = news_data
            
            if not articles_in_tag or len(articles_in_tag) == 0:
                print(f"   ℹ️  此标签下没有文章")
                continue
            
            print(f"   ✅ 找到 {len(articles_in_tag)} 篇文章")
            total_news_count += len(articles_in_tag)
            
            # ========== 第三步：抓取每篇文章的详情 ==========
            for news_idx, news_item in enumerate(articles_in_tag, 1):
                if not isinstance(news_item, dict):
                    continue
                
                # 提取文章ID
                news_id = news_item.get('news_id') or news_item.get('id') or news_item.get('article_id') or news_item.get('nid')
                
                if not news_id:
                    print(f"   [{news_idx}/{len(articles_in_tag)}] ⚠️  未找到文章ID")
                    continue
                
                title = news_item.get('title', '无标题')
                print(f"   [{news_idx}/{len(articles_in_tag)}] 正在抓取: {title[:30]}...")
                
                try:
                    # 请求文章详情
                    detail_url = DETAIL_API + str(news_id)
                    detail_resp = requests.get(detail_url, headers=headers, timeout=10)
                    detail_resp.raise_for_status()
                    
                    detail_json = detail_resp.json()
                    detail_data = detail_json.get("data", {})
                    
                    # 提取HTML内容并转换为纯文本
                    html_content = detail_data.get("content", "")
                    if html_content:
                        soup = BeautifulSoup(html_content, "html.parser")
                        text = soup.get_text("\n", strip=True)
                    else:
                        text = ""
                    
                    # 构建文章对象
                    article = {
                        "news_id": news_id,
                        "标签路径": full_path,
                        "标签名称": tag_name,
                        "标题": detail_data.get("title", title),
                        "发布时间": detail_data.get("add_time") or news_item.get('add_time') or news_item.get('publish_time', ''),
                        "正文": text,
                        "原文链接": f"https://www.lhqzy.com/news/{news_id}.html"
                    }
                    
                    all_articles.append(article)
                    print(f"               ✅ 成功 (字数: {len(text)})")
                    
                except Exception as e:
                    print(f"               ❌ 失败: {str(e)[:50]}")
                
                # 避免请求过快
                time.sleep(0.3)
            
            # 标签间延迟
            time.sleep(0.5)
            
        except Exception as e:
            print(f"   ❌ 获取标签文章失败: {str(e)[:50]}")
            continue
    
    # ========== 第四步：保存结果 ==========
    print(f"\n[3/4] 保存数据...")
    output_file = "data/hospital_tag_articles.json"
    
    # 确保目录存在
    import os
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(
            all_articles,
            f,
            ensure_ascii=False,
            indent=2
        )
    
    # 打印统计信息
    print("\n" + "="*60)
    print("📊 爬取完成统计")
    print("="*60)
    print(f"📁 标签数量: {len(leaf_tags)} 个")
    print(f"📰 文章总数: {total_news_count} 篇")
    print(f"✅ 成功抓取: {len(all_articles)} 篇")
    print(f"❌ 失败: {total_news_count - len(all_articles)} 篇")
    print(f"💾 文件保存至: {output_file}")
    if all_articles:
        print(f"💾 文件大小: {os.path.getsize(output_file) / 1024:.2f} KB")
    print("="*60)

except requests.exceptions.RequestException as e:
    print(f"\n❌ 网络请求错误: {e}")
except json.JSONDecodeError as e:
    print(f"\n❌ JSON解析错误: {e}")
    if 'resp' in locals():
        print(f"响应内容: {resp.text[:500]}")
except Exception as e:
    print(f"\n❌ 发生未知错误: {e}")
    import traceback
    traceback.print_exc()
