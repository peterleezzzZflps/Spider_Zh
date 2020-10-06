import sqlite3


def conntect_spider_db(table):
    conn = sqlite3.connect('spider.db')

    print("连接数据库成功😄️")

    conn_db = conn.cursor()
    sql = "CREATE TABLE %s ('ID' INTEGER  PRIMARY KEY AUTOINCREMENT ,'url'    TEXT    NULL,'标题'    TEXT    NULL,'CNVD-ID' TEXT NULL," \
          "'公开日期' TEXT NULL,'危害级别' TEXT NULL,'影响产品' TEXT NULL,'CVE ID' TEXT NULL,'漏洞描述' TEXT NULL,'漏洞类型' TEXT NULL," \
          "'参考链接' TEXT NULL,'漏洞解决方案' TEXT NULL,'厂商补丁' TEXT NULL,'验证信息' TEXT NULL,'报送时间' TEXT NULL,'收录时间' TEXT NULL," \
          "'更新时间' TEXT NULL,'漏洞附件' TEXT NULL);" % table
    # 数据库插入数据时如果内容中携带有引号需要加两对引号标注 才可以正常的插入数据

    print(sql)
    try:
        conn_db.execute(sql)
    except sqlite3.OperationalError as e:
        pass
    print("%s表创建成功" % table)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    conntect_spider_db('sqlitedata_db')
