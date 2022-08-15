import psycopg2
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
import time
import uuid

options = webdriver.ChromeOptions()
options.add_experimental_option("debuggerAddress", "127.0.0.1:9777")
driver = webdriver.Chrome(options=options)

conn = psycopg2.connect(database="pie", user="pg", password="123456", host="192.168.225.142", port="5432")
cur_conn = conn.cursor()


def get_list(essay_type):
    driver.get("https://tieba.baidu.com/f?kw=%E9%A5%BC%E5%B7%A5%E5%8E%82&ie=utf-8&tab=good&cid=" + essay_type)
    time.sleep(2)
    elements = driver.find_elements(By.CLASS_NAME, "j_th_tit")
    if len(elements) == 0:
        return
    for i in range(len(elements)):
        if elements[i].get_property("title") is None or elements[i].get_property("title") == "":
            continue
        cur_conn.execute(
            """
                INSERT INTO pie.essay(
                    id,
                    title,
                    source_url,
                    type
                ) VALUES (
                    %s, %s, %s, %s
                )
            """,
            (
                ''.join(str(uuid.uuid4()).split('-')),
                elements[i].get_property("title"),
                elements[i].get_property("href"),
                essay_type
            )
        )
        conn.commit()


if __name__ == '__main__':
    try:
        driver.implicitly_wait(5)
        driver.maximize_window()
        # 1班级日记 2闲逼生活 3十八资源 4饼吧水库
        for i in range(1, 5, 1):
            get_list(str(i))
    except NoSuchElementException:
        print("error")
    finally:
        driver.quit()
        cur_conn.close()
        conn.close()