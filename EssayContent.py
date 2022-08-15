import json
import uuid

import psycopg2
from bs4 import BeautifulSoup, Tag, NavigableString

conn = psycopg2.connect(database="pie", user="pg", password="123456", host="192.168.225.142", port="5432")
cur_conn = conn.cursor()


def extract_content():
    cur_conn.execute(
        """
            select 
                essay_id,
                html,
                page
            from
                pie.essay_html
        """
    )
    rows = cur_conn.fetchall()
    for row in rows:
        get_content(essay_id=row[0], html=row[1], page=row[2])


def get_content(essay_id, html, page):
    soup = BeautifulSoup(html, 'html.parser')
    posts = soup.find_all('div', attrs={'class': 'l_post'})
    for i in range(0, len(posts), 1):
        author = posts[i].find('a', attrs={'class': 'p_author_name'}).text
        content = ''
        contents = posts[i].find('div', attrs={'class': 'd_post_content'}).contents
        for c in contents:
            if type(c) == NavigableString:
                content += c
            if type(c) == Tag and c.has_attr('src'):
                content += '<img src="' + c['src'] + '"/>'
        tail_info = posts[i].find_all('span', attrs={'class': 'tail-info'})
        create_time = tail_info[len(tail_info) - 1].text
        index = i + page * 100
        print('author:' + author + ';content:' + content + ';create_time:' + create_time + ';index:' + str(index))
        save_content(essay_id=essay_id, content=content, author=author, order=index, create_time=create_time)


def save_content(essay_id, content, author, order, create_time):
    cur_conn.execute(
        """
            insert into pie.essay_content
            (
                id,
                content,
                author,
                essay_id,
                create_time,
                content_order
            )
            values
            (
                %s, %s, %s, %s, to_timestamp(%s, 'yyyy-MM-dd hh24:mi'), %s
            )
        """,
        [
            ''.join(str(uuid.uuid4()).split('-')),
            content,
            author,
            essay_id,
            create_time,
            order
        ]
    )
    conn.commit()


if __name__ == '__main__':
    extract_content()
