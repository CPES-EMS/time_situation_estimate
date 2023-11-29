import datetime
from dateutil.relativedelta import relativedelta
import logging

import statistic
import time
import config

import schedule

logging.basicConfig(filename=config.logging_path,level=logging.INFO)

def get_table_name(current_time):
    """
    生成结果存储数据库表名
    :param current_time: 时间
    :return: 前一个月的表名，当前月份表名，后一个月的表名
    """

    date_current=datetime.datetime.strptime(current_time,'%Y-%m-%d %H:%M:%S')
    date_previous=date_current+relativedelta(months=-1)
    date_next=date_current+relativedelta(months=1)

    date_previous_str=datetime.datetime.strftime(date_previous,'%Y-%m-%d %H:%M:%S')
    date_next_str=datetime.datetime.strftime(date_next,'%Y-%m-%d %H:%M:%S')

    table_current="`"+current_time[0:4]+current_time[5:7]+"`"
    table_previous="`"+date_previous_str[0:4]+date_previous_str[5:7]+"`"
    table_next="`"+date_next_str[0:4]+date_next_str[5:7]+"`"

    return table_previous,table_current,table_next

def table_check():
    """
    检查用于存储结果的数据库表是否存在，不存在则创建，保证前后一个月都有数据库表
    """
    current = time.time()
    current_bias = current - config.bias
    time_bias_struct = time.localtime(current_bias)
    time_bias_str = time.strftime('%Y-%m-%d %H:%M:%S', time_bias_struct)

    table_previous, table_current, table_next=get_table_name(time_bias_str)

    table_create(table_previous)
    logging.info('Guarantee there is a table for the previous month.')
    table_create(table_current)
    logging.info('Guarantee there is a table for the current month.')
    table_create(table_next)
    logging.info('Guarantee there is a table for the next month.')


def table_create(table_name,table_format=config.table_format):
    """
    创建数据集表
    """

    connection=config.save_connection()
    cursor=connection.cursor()

    sql="create table if not exists "+table_name+table_format

    cursor.execute(sql)
    connection.commit()
    pass

def step():
    """
    主函数，每分钟运行一次，统计过去一分钟内网和外网告警数量、源ip数量、目的ip数量、告警类型数量
    """
    current = time.time()
    current_bias = current - config.bias
    time_bias_struct = time.localtime(current_bias)
    time_bias_str = time.strftime('%Y-%m-%d %H:%M:%S', time_bias_struct)

    try:
        statistic.run(time_bias_str,1,'in')
        statistic.run(time_bias_str,1,'out')
    except Exception as e:
        logging.error(e)

table_check()
logging.info(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+'\tTable Initialized.')

schedule.every().day.do(table_check)
logging.info(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+'\tTable Checked.')

schedule.every(1).minutes.do(step)

while True:
    schedule.run_pending()





