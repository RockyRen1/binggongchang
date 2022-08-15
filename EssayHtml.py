import psycopg2
import uuid
import requests
from bs4 import BeautifulSoup

conn = psycopg2.connect(database="pie", user="pg", password="123456", host="192.168.225.142", port="5432")
cur_conn = conn.cursor()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}


def get_html(essay_id, url):
    r = requests.get(url, headers=headers)
    r.encoding = 'utf-8'
    # 第一页
    save_content(essay_id=essay_id, html=r.text, page=1)
    # 获取总页数
    soup = BeautifulSoup(r.text, 'html.parser')
    jump_page_input = soup.find_all('input', attrs={'class': 'jump_input_bright'}, limit=1)
    if len(jump_page_input) > 0:
        page_max = jump_page_input[0]['max-page']
        for i in range(2, int(page_max) + 1, 1):
            r2 = requests.get(url + "?pn=" + str(i), headers=headers)
            r2.encoding = 'utf-8'
            save_content(essay_id=essay_id, html=r2.text, page=i)


def save_content(essay_id, html, page):
    cur_conn.execute(
        """
            insert into pie.essay_html
                (
                    id,
                    essay_id,
                    html,
                    page
                )
            values
                (
                    %s, %s, %s, %s
                )
        """,
        (
            ''.join(str(uuid.uuid4()).split('-')),
            essay_id,
            html,
            page
        )
    )
    conn.commit()


if __name__ == '__main__':
    cur_conn.execute(
        """
            select
                id,
                source_url
            from
                pie.essay
        """
    )
    rows = cur_conn.fetchall()
    for row in rows:
        get_html(essay_id=row[0], url=row[1])
    # get_html("0e0eccae250b4d559ac971570b66b5f1", "https://tieba.baidu.com/p/3161818344")
