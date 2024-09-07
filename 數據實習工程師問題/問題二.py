import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# 設定要爬取的天數
days_to_check = 7
base_url = 'https://www.ptt.cc'
board_url = f'{base_url}/bbs/Gossiping/index.html'

# 設置 Cookie，通過年齡驗證
session = requests.Session()
session.cookies.set('over18', '1')

# 設定存檔目錄
if not os.path.exists('ptt_gossiping_posts'):
    os.makedirs('ptt_gossiping_posts')

# 計算從當前日期往前推的日期界限
today = datetime.today()
date_limit = today - timedelta(days=days_to_check)


# 函數：取得貼文列表頁面的 HTML
def get_page_html(url):
    res = session.get(url)
    return BeautifulSoup(res.text, 'html.parser')


# 函數：解析每篇文章內的內容
def parse_post_content(post_url):
    res = session.get(post_url)
    soup = BeautifulSoup(res.text, 'html.parser')

    meta_info = soup.find_all('span', class_='article-meta-value')

    # 檢查是否為正常文章，防止無作者文章出現問題
    if len(meta_info) < 4:
        return None

    # 取得文章基本資料
    author = meta_info[0].text
    title = meta_info[2].text
    post_time = meta_info[3].text
    category = title.split(']')[0] + ']' if ']' in title else '無分類'

    # 取得內文
    main_content = soup.find(id='main-content').text
    # 去除 meta 資訊
    main_content = main_content.split('※ 發信站')[0].split('\n', 1)[1]

    # 取得留言
    comments = []
    for comment in soup.find_all('div', class_='push'):
        comment_author = comment.find('span', class_='f3 hl push-userid').text.strip()
        comment_content = comment.find('span', class_='f3 push-content').text.strip()[1:]  # 去除冒號
        comment_time = comment.find('span', class_='push-ipdatetime').text.strip()
        comments.append({
            'author': comment_author,
            'content': comment_content,
            'time': comment_time
        })

    return {
        'author': author,
        'title': title,
        'time': post_time,
        'category': category,
        'content': main_content,
        'comments': comments
    }


# 函數：存取貼文及留言到檔案
def save_post(post_data, filename):
    with open(f'ptt_gossiping_posts/{filename}.txt', 'w', encoding='utf-8') as f:
        f.write(f"作者: {post_data['author']}\n")
        f.write(f"標題: {post_data['title']}\n")
        f.write(f"時間: {post_data['time']}\n")
        f.write(f"類別: {post_data['category']}\n")
        f.write(f"內文:\n{post_data['content']}\n\n")

        f.write(f"留言:\n")
        for comment in post_data['comments']:
            f.write(f"留言者: {comment['author']}, 時間: {comment['time']}\n")
            f.write(f"留言內容: {comment['content']}\n")
            f.write("-" * 50 + "\n")


# 開始爬取八卦版的貼文
def crawl_gossiping_posts():
    url = board_url
    while True:
        print(f'正在爬取: {url}')
        soup = get_page_html(url)

        # 解析每篇貼文
        for entry in soup.find_all('div', class_='r-ent'):
            try:
                title_tag = entry.find('a')
                if not title_tag:
                    continue

                post_url = base_url + title_tag['href']
                post_date_str = entry.find('div', class_='date').text.strip()

                # 將日期格式轉換
                post_date = datetime.strptime(f'{today.year}/{post_date_str}', '%Y/%m/%d')

                # 如果貼文日期超過限制，停止爬取
                if post_date < date_limit:
                    return

                # 解析貼文內容
                post_data = parse_post_content(post_url)
                if post_data:
                    filename = post_data['title'].replace('/', '_')
                    save_post(post_data, filename)
            except Exception as e:
                print(f'Error parsing post: {e}')

        # 找到上一頁的網址
        prev_page = soup.find('a', string='‹ 上頁')
        if prev_page:
            url = base_url + prev_page['href']
        else:
            break


# 執行爬取程式
crawl_gossiping_posts()
