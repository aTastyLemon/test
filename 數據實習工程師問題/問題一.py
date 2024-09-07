import requests
from bs4 import BeautifulSoup

# PPT 熱門看板的網址
url = 'https://www.ptt.cc/bbs/hotboards.html'

# 發送 GET 請求
response = requests.get(url)

# 使用 BeautifulSoup 解析 HTML
soup = BeautifulSoup(response.text, 'html.parser')

# 找到所有看板的列表
boards = soup.find_all('div', class_='b-ent')

# 遍歷每個看板並提取名稱與網址
for board in boards:
    board_name = board.find('div', class_='board-name').text
    board_url = 'https://www.ptt.cc' + board.find('a')['href']
    print(f'列表名稱: {board_name}')
    print(f'網址: {board_url}')