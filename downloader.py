# -*- coding:utf-8 -*-
from urllib.parse import urlsplit
import time
import socket
import requests
from datetime import datetime
import numpy as np

# 从浏览器中得到原始cookie信息
raw_cookies = 'bid=cAhIkqdtlWo; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1505036668%2C%22https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3DgOcY-TLarD9YR3RrqECfzhqLy6Rz3YUYFp7GH6ny9LTh2_bBu5Phlj5NIhrmEE0l%26wd%3D%26eqid%3Dfe6c7e6900017e000000000659b50978%22%5D; ll="118269"; _vwo_uuid_v2=4C998080FCC8AD546963E0642108A443|9cccf64eedc821f5e88742488a37046e; ps=y; ap=1; dbcl2="166463689:jvNK3bkP4gY"; ck=h8QU; _pk_id.100001.4cf6=3fc91b33414f72bb.1505036668.1.1505039435.1505036668.; _pk_ses.100001.4cf6=*; __utma=30149280.403903282.1505036668.1505036668.1505036668.1; __utmb=30149280.0.10.1505036668; __utmc=30149280; __utmz=30149280.1505036668.1.1.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utma=223695111.1622320984.1505036668.1505036668.1505036668.1; __utmb=223695111.0.10.1505036668; __utmc=223695111; __utmz=223695111.1505036668.1.1.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; push_noty_num=0; push_doumail_num=0'
cookies = {}
for line in raw_cookies.split(';'):
    key, value = line.split('=', 1)
    cookies[key] = value

# 发送请求表头
headers = dict()
headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
headers['Accept-Encoding'] = 'gzip, deflate, br'
headers['Accept-Language'] = 'zh-CN,zh;q=0.8'
headers['Connection'] = 'keep-alive'
headers['Host'] = 'movie.douban.com'
headers['Referer'] = 'https://www.douban.com/accounts/login?source=movie'
headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'


class Downloader:
    def __init__(self, delay=np.random.rand()*5, timout=60,cache=None):
        socket.setdefaulttimeout(timout)
        self.throttle = Throttle(delay)
        self.cache = cache


    def __call__(self, url):
        result = None
        if self.cache:
            try:
                result = self.cache[url]
            except KeyError:
                # 在缓存不存在url
                pass
        if result is None:
            #结果没有从缓存中得到，所以仍然需要被下载
            self.throttle.wait(url)
            result = self.download(url)
            if self.cache:
                #保存结果到缓存中
                self.cache[url] = result
        return result['html']


    def download(self, url, proxy=None, num_retries=3):
        print('Downloading:', url)
        html = None

        if proxy is None:                             # 当代理为空时,不使用代理来发送请求
            try:
                wb_data = requests.get(url, headers=headers, cookies=cookies, timeout=30)
                if wb_data.status_code == 200:        # 如果请求成功，并且返回正常值
                    html = wb_data.text
                    return  {'html': html}
                else:                                 # 如果请求成功，但是返回其他信息， 那么使用忽略这个url的访问
                    pass
            except Exception as e:                    # 如果请求发生异常，
                print(str(e))
                if num_retries > 0:
                    time.sleep(np.random.rand()*6)
                    print('获取信息出错， 5s后倒数第{:d}次重新尝试!'.format(num_retries) )
                    return self.download(url, num_retries-1)
        return {'html': html}

class Throttle:
    def __init__(self, delay):
        # 在两次相同域名之间设置延时
        self.delay = delay
        # 上次访问一个域名的时间戳
        self.domains = {}

    def wait(self, url):
        """如果域名最近被访问过,那么设置延时
        """
        domain = urlsplit(url).netloc
        last_accessed = self.domains.get(domain)
        if self.delay > 0 and last_accessed is not None:
            sleep_secs = self.delay - (datetime.now() - last_accessed).seconds
            if sleep_secs > 0:
                time.sleep(sleep_secs)
        self.domains[domain] = datetime.now()



























