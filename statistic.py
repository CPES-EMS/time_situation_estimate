import config
from config import search_connection
import datetime
from dateutil.relativedelta import relativedelta

def run(end_time,interval,segment):
    """
    主函数，进行告警特征统计
    :param end_time: 时间
    :param interval: 时间间隔，单位分钟，设为1则计算每分钟的告警统计量
    :param segment: 内外网，‘in’或者‘out’
    :return: None
    """
    end_time_formated=end_time[0:-2]+"00"

    end_time_struct=datetime.datetime.strptime(end_time_formated,'%Y-%m-%d %H:%M:%S')
    start_time_struct=end_time_struct+relativedelta(minutes=-1*interval)
    start_time_formated=datetime.datetime.strftime(start_time_struct,'%Y-%m-%d %H:%M:%S')

    count_alert, count_sip, count_dip, count_category=statistic(start_time_formated,end_time_formated,segment)
    save(end_time_formated,segment,count_alert,count_sip,count_dip,count_category)

def save(time_str,segment,count_alert,count_sip,count_dip,count_category):
    """
    用于保存结果
    :param time_str:时间
    :param segment: 内外网信息
    :param count_alert: 告警数量
    :param count_sip: 源IP数量
    :param count_dip: 目的IP数量
    :param count_category: 告警类型数量
    :return: None
    """

    table_name="`"+time_str[0:4]+time_str[5:7]+"`"

    sql="INSERT INTO" + table_name + " (time,segment,count_alert,count_sip,count_dip,count_category) VALUES (%s,%s,%s,%s,%s,%s);"
    args=(time_str,segment,count_alert,count_sip,count_dip,count_category)

    connection=config.save_connection()
    cursor=connection.cursor()
    cursor.execute(sql,args)
    connection.commit()

    pass

def statistic(start_time,end_time,segment):
    """
    统计开始时间到结束时间时间段中的告警特征
    :param start_time:开始时间
    :param end_time: 结束时间
    :param segment: 内外网
    :return: 告警数量，源Ip数量，目的Ip数量，告警类型数量
    """

    connection=search_connection()
    cursor=connection.cursor()

    start_table = start_time[0:7].replace('-', '')
    end_table = end_time[0:7].replace('-', '')
    segment_string="'"+segment+"'"

    if start_table == end_table:
        sql = "SELECT count(*),count(distinct sip),count(distinct dip),count(distinct category) FROM `" + start_table + "` WHERE receivetime>=" \
              + "'" + start_time + "'" + " and receivetime<" + "'" + end_time + "'" + "AND `in_or_out`=" + segment_string + ";"
    else:
        sql = "SELECT count(*),count(distinct sip),count(distinct dip),count(distinct category) FROM `" + start_table + "` WHERE receivetime>=" \
              + "'" + start_time + "'" + "AND `in_or_out`=" + segment_string + "UNION all SELECT count(*),count(distinct sip),count(distinct dip),count(distinct category) FROM `" \
              + end_table + "` WHERE receivetime<" + "'" + end_time + "'" + "AND `in_or_out`=" + segment_string +";"

    # print(sql)
    cursor.execute(sql)
    data=cursor.fetchall()
    # print(data)

    if len(data) == 1:
        count_alert=data[0][0]
        count_sip=data[0][1]
        count_dip=data[0][2]
        count_category=data[0][3]
    else:
        count_alert=data[0][0]+data[1][0]
        count_sip=data[0][1]+data[1][1]
        count_dip=data[0][2]+data[1][2]
        count_category=data[0][3]+data[1][3]

    return count_alert,count_sip,count_dip,count_category



