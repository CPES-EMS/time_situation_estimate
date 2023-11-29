import pymysql

logging_path='ems_alert_count.log'
"""日志保存地址"""

bias=60
"""时间偏移量，单位秒，例如设置为60则统计一分钟的告警数据"""

def search_connection():
    """
    查询告警数据的数据库链接
    """
    connection = pymysql.connect(host='202.117.43.249', port=9906,
                           user='root', passwd='S6000#249', db='S6000C', charset='utf8mb4')
    return connection

def save_connection():
    """
    保存结果的数据库链接
    """
    connection=pymysql.connect(host='10.181.7.225', port=9980,
                           user='root', passwd='S6000#249', db='ems_alert_count', charset='utf8mb4')
    return connection

"""
保存结果的数据库表结构
"""
table_format=" (\
time    datetime    null,\
segment     text   null,\
count_alert     bigint   null,\
count_sip     bigint    null,\
count_dip     bigint    null,\
count_category     bigint    null\
);"
