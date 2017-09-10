import lxml.html
import numpy as np
from pymongo import MongoClient
from pprint import pprint


#添加一个回调函数类,解析详情页的数据信息，并且将数据信息保存到mongodb数据库中去
class GetDetailInfo:
    def __init__(self, client=None):
        self.client = MongoClient('localhost', 27017) if client is None else client
        self.db = self.client.dbMovies250


    def __call__(self, url, html):
        # 该url对应详情页的信息
        tree = lxml.html.fromstring(html)

        # 解析数据
        ID = url.split('/')[-2]  # 电影的ID
        try:  # 电影名称
            title = tree.cssselect('div#content h1 > span')[0].text_content()
        except Exception:
            title = ''
        try:
            ratingScore = tree.cssselect('div.rating_self.clearfix > strong.ll.rating_num')[0].text_content()              # 电影评分
            ratingPeople = tree.cssselect('div.rating_self.clearfix > div > div.rating_sum > a > span')[0].text_content()  # 评价人数
        except Exception:
            ratingScore = ''
            ratingPeople = ''
        try:
            pubDate = []
            td = tree.cssselect('div.subject.clearfix div#info span[property="v:initialReleaseDate"]')  # 上映日期
            for date in td:
                pubDate.append(date.text_content())
            if pubDate == []:
                pubDate = tree.cssselect('div#content h1 span.year')[0].text_content()
        except Exception:
            pubDate = ''
        try:  # 导演
            directors = tree.cssselect('div.subject.clearfix div#info span.attrs')[0].text_content()
        except Exception:
            directors = ''
        try:  # 编剧
            if tree.cssselect('div.subject.clearfix div#info span span.pl')[1].text_content() == "编剧":
                screenwriter = tree.cssselect('div.subject.clearfix div#info span.attrs')[1].text_content()
            else:
                screenwriter = ''
        except Exception:
            screenwriter = ''
        try:  # 主演
            actors = tree.cssselect('div.subject.clearfix div#info span.actor span.attrs')[0].text_content()
        except Exception:
            actors = ''
        try:  # 电影类型
            types = []
            td = tree.cssselect('div.subject.clearfix div#info span[property="v:genre"]')
            for type in td:
                types.append(type.text_content())
        except Exception:
            types = ''  # 片长
        try:
            totaltime = tree.cssselect('div.subject.clearfix div#info span[property="v:runtime"]')[0].text_content()
        except Exception:
            totaltime = ''  # 影片简介
        try:
            description = tree.cssselect('div#link-report.indent span.all.hidden')[0].text_content().strip().replace('\n', '').replace('\u3000', '')
        except Exception:
            try:
                description = tree.cssselect('div#link-report.indent span[property="v:summary"]')[0].text_content().strip().replace('\n', '').replace('\u3000', '')
            except Exception:
                description = ''
        try:                                                                                                         # 看过/想看/在看
            hobbies = []
            td = tree.cssselect('#subject-others-interests > div a')
            for interest in td:
                hobbies.append(interest.text_content())
        except Exception:
            hobbies = ''
        # 下面的这个内容解析还需看看是否正确。。。
        try:
            # 用正则表示式解析制片国家、地区
            info = tree.cssselect('#info')[0]
            released_area = re.findall(r'制片国家/地区: (.*?)(?=\n)', info.text_content())
        except Exception:
            released_area = ''

        data = {
            'id': ID, "Name": title, "rate_score": ratingScore,
            'rate_sum': ratingPeople, 'release_date': pubDate, 'director': directors, 'playwright': screenwriter,
            'actor': actors, 'type': types, 'interval': totaltime, 'content': description, 'hobbies': hobbies, "released_area": released_area,
        }
        pprint(data)                                                                              # 将每条文档插入到集合中
        self.db.movie_infos.insert_one(data)