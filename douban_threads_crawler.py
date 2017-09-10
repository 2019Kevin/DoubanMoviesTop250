import queue
import threading
import time
import numpy as np
from downloader import Downloader
from bs4 import BeautifulSoup
from scrape_back import GetDetailInfo
from mongo_cache import MongoCache



# 返回链表页html中所有详情页的链接
def get_links(html):
    soup = BeautifulSoup(html, "lxml")
    links = soup.select('#content > div > div.article > ol li div.item > div.info > div.hd > a')
    url_all = set()
    for link in links:
        url = link.get('href')
        url_all.add(url)
    if url_all == set():
        return None
    else:
        return url_all


def threaded_crawler(delay=2, scrape_callback=None, cache=None, max_threads=5):
    form_url = 'https://movie.douban.com/top250?start={}&filter='
    seed_url = form_url.format(0)

    crawl_queue = queue.deque([seed_url])
    seen = set(seed_url)
    D = Downloader(delay=delay, cache=cache)

    def process_queue():
        stop = 0
        page_size = 0
        while True:
            try:
                url = crawl_queue.pop()
            except IndexError:
                break                                                                      # 爬虫队列为空, 该分类已经全部爬取。
            else:
                html = D(url)
                if html is None:                                                           # 如果链表页为空, 直接跳过
                    pass
                else:
                    if scrape_callback and 'top250' not in url:               # 该url是对应详情页
                        try:
                            s = scrape_callback()
                            s(url, html)
                        except Exception as e:
                            print('Error in callback for: {}: {}'.format(url, e))
                    if 'top250' in url:                                      # 该url是对应链表页
                        links = get_links(html)                                           # 如果链表页下的所有详情页的url不为空
                        if links is not None:
                            for link in links:
                                if link not in seen:
                                    seen.add(link)
                                    crawl_queue.append(link)                              # 将详情页的url加到爬虫队列中
                        else:
                            stop = 1                                                      # 该链表页下的所有详情页为空, 不再增加链表页
                if 'top250' in url and stop == 0:
                    page_size += 25
                    next_link = form_url.format(page_size)
                    if next_link not in seen:
                        seen.add(next_link)
                        crawl_queue.append(next_link)
    # 等待所有的下载线程结束
    threads = []
    while threads or crawl_queue:
        for thread in threads:
            if not thread.is_alive():
                # 移除已经停止的进程
                threads.remove(thread)
        while len(threads) < max_threads and crawl_queue:
            # 开始更多的线程
            thread = threading.Thread(target=process_queue)
            thread.setDaemon(True)
            thread.start()
            threads.append(thread)
        time.sleep(np.random.randint(6, 12))



if __name__ == '__main__':
    Scrape_Back = GetDetailInfo
    Cache = MongoCache()
    Cache.clear()
    threaded_crawler(scrape_callback=Scrape_Back, cache=Cache)
