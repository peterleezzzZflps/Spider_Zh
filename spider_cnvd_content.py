#!-*- coding: utf-8 -*-

import requests
import time
import random
import re
from Spider import spider_db
from lxml import etree


class Spider_Cnvd(object):

    def __init__(self, data, header_list, url, keyword):
        self.data = data
        self.header_list = header_list  # UA伪装
        self.url = url
        self.keyword = keyword  # 关键词
        self.cookies = self.get_cookies()  # 获取cookie
        self.count = 0  # 用作每一个cookie访问次数的计数器
        self.url_count = self.get_url_count()
        self.spider_main()  # 爬虫主线程

    def get_cookies(self):
        response = requests.get(url="https://www.cnvd.org.cn/flaw/list.htm?max=100&offset=0")  # 设置每次ChromeDriver访问的初始页面用来更新cookie，以绕过cnvd爬虫限制
        cookie = requests.utils.dict_from_cookiejar(response.cookies)  # 通过request内置方法获取cookie
        return cookie

    def spider_main(self):
        all_url_list = []
        print("正在获取关键字'%s'相关的记录地址, 请耐心等待..." % self.keyword)
        url_count = (int(self.url_count[0]) // 100) + 2
        for value in range(url_count):
            # 如果数据量过大, 获取所有的url最好也要加上 sleep
            if value > 5:
                time.sleep(random.randrange(2, 5))
            # 通过post方式获取ajax动态加载的数据
            response = requests.post(url=self.url+'/flaw/list.htm', headers=random.choice(self.header_list), data=self.data).text

            self.data['offset'] += 100
            tree = etree.HTML(response, )
            # 获取sqlite的所有数据页面的url地址
            page_url_list = tree.xpath("/html/body/div[4]/div[1]/div/div[1]/table//tbody//a/@href")

            all_url_list.extend(page_url_list)
        if int(self.url_count[0]) > 0:
            print("查询共{size}条记录, 爬虫准备中...".format(size=self.url_count[0]))
        else:
            print("未查到关键字'%s'相关记录" % self.keyword)
            exit()

        spider_db.conntect_spider_db(str(self.keyword + "data_db"))
        time.sleep(2)

        # print(all_url_list)  # 获得关键词相关的所有页面的url
        self.spider_content(all_url_list,)

    def spider_content(self, all_url_list,):  # 接收每个漏洞页面的url
        error_list = []

        for i in all_url_list:
            time.sleep(random.randrange(3, 5))  # 尽可能的速度慢一点, 因为快了的话 就真的封IP了 没有加sleep被封至少半天
            self.count += 1

            if self.count == 5:  # 每一个cookie访问次数的限制
                self.cookies = self.get_cookies()
                self.count = 0

            response = requests.get(url=self.url+i, headers=random.choice(self.header_list), cookies=self.cookies)

            if response.status_code > 400:  # 返回状态码大于400 说明报错了
                time.sleep(random.randrange(8, 13))
                error_list.append(i)
                continue

            tree = etree.HTML(response.text, )
            # xpath解析获取到所有的存放数据的tr标签
            page_text = tree.xpath("/html/body/div[4]/div[1]/div[1]/div[1]/div[2]/div[1]//tbody/tr")
            page_text.pop()  # 去除最后一行无用信息

            # xpath解析获取每个漏洞的title
            title = tree.xpath("/html/body/div[4]/div[1]/div[1]/div[1]/h1/text()")[0]

            # 数据库插入数据时如果内容中携带有引号需要加两对引号标注 才可以正常的插入数据
            if "'" in title:
                title = title.replace("'", "''")
            data_dic = {"标题": title, "url": self.url+i}

            for item in page_text:

                tr = item.xpath("./td")
                # 获取漏洞的属性
                field = tr[0].xpath("./text()")[0]
                # 获取漏洞对应属性的内容说明
                content = tr[1].xpath("normalize-space(string(.))")

                if "'" in content:
                    content = content.replace("'", "''")

                # 生成字典
                data_dic[field] = content

            # 页面数据中爬去过程中没有相应键值对的数据复制为空
            if 'CVE ID' not in data_dic:
                data_dic['CVE ID'] = ""
            print(data_dic)
            # 将字典传入connect_db函数, 入库
            self.connect_db(data_dic, )
        print("爬虫失败的地址 > ", error_list)
        # 如果爬去错误列表中无值 说明全部爬去成功, 如果有 需要重新爬取
        try:
            if error_list[0]:
                self.spider_content(error_list)
        except IndexError:  # 无数据时防止Indexerror报错
            pass

    def connect_db(self, data_dic, ):

        import sqlite3
        conn = sqlite3.connect('spider.db')

        print("连接数据库成功")

        conn_db = conn.cursor()
        # 生成插入数据的sql语句
        sql = "INSERT INTO %s ('url','标题','CNVD-ID', '公开日期', '危害级别', '影响产品', 'CVE ID', '漏洞描述'," \
              " '漏洞类型','参考链接', '漏洞解决方案', '厂商补丁','验证信息','报送时间','收录时间', '更新时间', '漏洞附件' ) " \
              "VALUES ('%s','%s', '%s', '%s', '%s', '%s', '%s', '%s','%s','%s', '%s', '%s', '%s', '%s', '%s', '%s','%s') ;"\
              % (str(self.keyword+"data_db"), data_dic["url"], data_dic['标题'], data_dic['CNVD-ID'], data_dic['公开日期'], data_dic['危害级别'], data_dic['影响产品'], data_dic['CVE ID'],
                data_dic['漏洞描述'], data_dic['漏洞类型'], data_dic['参考链接'], data_dic['漏洞解决方案'], data_dic['厂商补丁'], data_dic['验证信息'],
                data_dic['报送时间'], data_dic['收录时间'], data_dic['更新时间'], data_dic['漏洞附件'])
        print(sql)
        conn_db.execute("%s" % sql)
        # conn_db.execute("INSERT INTO test_cnvd(标题) VALUES (123);")
        conn.commit()
        print("数据插入成功")
        conn.close()

    def get_url_count(self):

        response = requests.post(url=self.url+'/flaw/list.htm?flag=true', data=self.data,
                                 headers=random.choice(self.header_list)).text
        # re正则获取关键字相关的url总数
        patten = '.*?共&nbsp;(.*?)&nbsp;条.*?'
        url_count = re.findall(patten, response, re.S)
        return url_count


if __name__ == "__main__":
    header_list = []
    for i in range(1, 10):
        header = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_%s) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36' % i,
            'X-Cache': 'hit',
        }
        header_list.append(header)
    keyword = input("请输入想要爬取的关键字>>").strip()

    data = {
        'keyword': keyword,
        'condition': 1,
        'keywordFlag': 0,
        'cnvdId': '',
        'cnvdIdFlag': 0,
        'baseinfoBeanbeginTime': '',
        'baseinfoBeanendTime': '',
        'baseinfoBeanFlag': 0,
        'refenceInfo': '',
        'referenceScope': -1,
        'manufacturerId': -1,
        'categoryId': -1,
        'editionId': -1,
        'causeIdStr': '',
        'threadIdStr': '',
        'serverityIdStr': '',
        'positionIdStr': '',
        'max': 100,
        'offset': 0,
        'flag': '[Ljava.lang.String;@132865ee',

    }
    # for i in range(2):
    #
    #     data['offset'] += 100

    """了解到cnvd最快速禁止的是cookie的访问, 一个cookie大概快速访问允许的次数在6-9次, 所以将每5次将从新获取一下cookie"""
    Spider_Cnvd(data=data, header_list=header_list, url='https://www.cnvd.org.cn', keyword=keyword)

