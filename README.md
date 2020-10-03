# Spider
# 这是一个关于解决JSL反爬虫机制的案例

pip install -r  requirements.txt 
# 国内可以使用豆瓣加速 后加 -i http://pypi.douban.com/simple --trusted-host pypi.douban.com

执行 python3 spider_cnvd_content.py
输入想要爬取相关数据的关键字即可获得爬虫的结果, 经过测试发现JSL反爬虫机制, 执行此案例时最好有sleep的过程, sleep在5s左右为佳,比较稳定不会被封锁,.如果不加sleep会被关在小黑屋至少半天!!!

