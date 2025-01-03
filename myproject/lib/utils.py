import logging
import time

import pandas as pd


# 返回当天日期日志名称 如20230509.log
def log_date_name():
    return time.strftime('%Y%m%d', time.localtime(time.time())) + '.log'


# 日志初始化设置
def setup_logging(logfile, loglevel=logging.INFO):
    """
    设置日志记录器，并添加文件处理器，将日志写入给定的文件中
    :param logfile: 日志文件路径
    :param loglevel: 日志级别，默认为INFO
    :return logger: 返回设置好的logger对象
    """
    # 日志格式设置
    logging.basicConfig(
        level=loglevel,
        format='%(asctime)s | %(filename)s[line:%(lineno)d] | %(levelname)s: %(message)s')

    # 存入模块和包都有一个__name__属性(也就是.py名称)
    logger = logging.getLogger(__name__)
    # Log等级总开关
    logger.setLevel(loglevel)
    # 第二步，创建一个handler，用于写入日志文件,a为追加模式
    fh = logging.FileHandler(logfile, mode='a')
    fh.setLevel(logging.INFO)  # 输出到file的log等级的开关
    # 第三步，定义handler的输出格式
    formatter = logging.Formatter("%(asctime)s | %(filename)s[line:%(lineno)d] | %(levelname)s: %(message)s")
    fh.setFormatter(formatter)
    # 第四步，将logger添加到handler里面
    logger.addHandler(fh)
    return logger


# 合并数组, 并排除数组
def mergeExcludeArray(list1, list2, list3, exclude=None):
    # 合并数组并去重
    merged_set = set().union(*[list1, list2, list3])
    # 排除指定元素
    if exclude is not None:
        merged_set.difference_update(exclude)
    # 返回合并后的列表
    return list(merged_set)


# 单个数组去重和排除
def filterUnique(NameList, exclude=None):
    # 如果有排除列表，过滤掉要排除的元素
    if exclude is not None:
        filtered_list = [item for item in NameList if item not in exclude]
    else:
        filtered_list = NameList

    # 使用 set 去重并返回列表
    return list(set(filtered_list))


# 表格数据转为json

def excelToJson(inputData, lonField, latField, valueField):
    """

    :param inputData: 输入excel表格
    :param lonField: 表格内经度字段名称
    :param latField: 表格内纬度字段名称
    :param valueField: 表格像元值字段名称
    :return: Json文件
    """
    df = inputData

    # Correctly parsed dataframe:
    #    GRID_CODE        lat         lon
    # 0         68  31.163856  119.668872
    # 1         68  31.163856  119.719872
    # 2         68  31.163856  119.736872

    # GeoJSON template
    geojson = {
        "type": "FeatureCollection",
        "crs": {
            "type": "name",
            "properties": {
                "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
            }
        },
        "features": [
            {
                "type": "Feature",
                "properties": {
                },
                "geometry": {
                }
            }
        ]
    }

    # Adding new features from the dataframe
    for _, row in df.iterrows():
        feature = {
            "type": "Feature",
            "properties": {
                '经度': row[lonField],
                '纬度': row[latField],
                valueField: row[valueField],
                # Assuming no magnitude data in the provided table
            },
            "geometry": {
                "type": "Point",
                "coordinates": [
                    row[lonField],
                    row[latField],
                    row[valueField]
                ]
            }
        }
        geojson['features'].append(feature)

    # Save to a GeoJSON file
    return geojson
