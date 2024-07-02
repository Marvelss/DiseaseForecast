"""
@Author : SakuraFox
@Time: 2024-07-02 9:34
@File : FeatureCalculationMethodFacet.py
@Description : 面状特征计算方法
"""
from datetime import datetime

import numpy as np
import pandas as pd
import glob
import os

from tqdm import trange
import rasterio


class FeatureCalculationMethodFacet:
    def __init__(self):
        pass

    @staticmethod
    def generate_tif(result_array, template_tif_path, saved_path):
        """

        :param result_array: 输出像素数据,二维数据
        :param template_tif_path: 模板tif文件路径,主要用于获取tif图像属性
        :param saved_path: 保存tif文件路径
        :return:
        """
        # 打开已有tif文件
        with rasterio.open(template_tif_path) as src:
            # 获取空间参考系统
            crs_template = src.crs
            # 获取转换矩阵
            transform_template = src.transform
            # 获取二维数组的形状和数据类型：
            height, width = result_array.shape
            data_type = result_array.dtype
        # 定义空间参考系统和转换矩阵：
        crs = crs_template  # 使用模板空间参考系统
        transform = transform_template  # 使用模板转换矩阵
        # 创建输出文件并写入数据：
        with rasterio.open(saved_path, 'w', driver='GTiff', height=height, width=width, count=1, dtype=data_type,
                           crs=crs,
                           transform=transform,
                           nodata=0) as dst:
            dst.write(result_array, 1)
        print('保存成功,路径为:{}'.format(os.path.join(os.getcwd(), saved_path)))

    # 时空抽取
    @staticmethod
    def spatiotemporalExtraction(param):
        print('----测试----------')
        print(param)
        temperatureDir = param[0]
        extractDir = param[1]
        templateFile = param[2]
        threshold = int(param[3])
        duration = int(param[4])
        mode = param[5]
        saved_path1 = param[6]

        # ['气象数据', '待抽取特征文件.tif',
        #  '模板文件.tif', '50', '1',
        #  '平均值', ' 'spatiotemporalExtraction.tif']
        def accumulate_values(arr, target_sum):
            print('获取起点日期中...')
            x_dim, y_dim, z_dim = arr.shape
            # 输出day of year起始数组
            result = np.zeros((x_dim, y_dim), dtype=arr.dtype)
            # result = np.full((x_dim, y_dim), np.nan, dtype=arr.dtype)
            # 按照z轴对每个像素点累加
            cumulative_sum = np.cumsum(arr, axis=2)
            # 找到第一个大于150的z轴值,也就是初始温度
            for i in trange(cumulative_sum.shape[0]):
                for j in range(cumulative_sum.shape[1]):
                    # if i == 909 and j == 116:
                    #     print(cumulative_sum[i, j])
                    # time.sleep(20)
                    idx = np.argmax(cumulative_sum[i, j] >= target_sum)
                    if idx != 0:
                        result[i, j] = idx + 1
            # result = np.where(result == 0, -9999, result)
            return result

        def space_time_extract(template_tif_path, temperature_dir, cumulated_temperature, durationTemp):
            """
            :param template_tif_path: 模板tif文件路径,主要用于获取tif图像属性
            :param temperature_dir: 包含全部气象或遥感等数据的文件夹路径
            :param cumulated_temperature: 达到病害敏感时段起点的活动积温
            :param durationTemp: 抽取天数
            :return: result: 输出结果,二维数据
            """
            template_data = rasterio.open(template_tif_path)
            rows = template_data.width
            cols = template_data.height
            template_list = np.transpose(template_data.read(1))
            template_data.close()
            # 获取该文件夹下所有tif文件(得按照一年中的第几天的大小一次排序)
            tif_files = glob.glob(temperature_dir + '/*.tif')
            # z轴为现存数据天数，通过文件个数确定
            days_max = len(tif_files)
            # 汇聚全部气象数据数组
            temperature = np.zeros((rows, cols, days_max), dtype=np.float32)
            x, y = template_list.shape
            # 输出图层
            result = np.zeros((rows, cols), dtype=np.float32)
            print('获取全部气象数据中...')
            # time.sleep(1)
            # 获取366天气象数据
            for z in trange(days_max):
                file = tif_files[z]
                dataset = rasterio.open(file)
                pixel_value = dataset.read(1)
                # 对pixel_value进行转置
                pixel_value = np.transpose(pixel_value)
                # 读取像素的数据,将二维矩阵赋值给三维矩阵中的每个z维度
                temperature[:, :, z] = pixel_value
                dataset.close()
            # 获取起点日期
            doy_list = accumulate_values(temperature, cumulated_temperature)

            # 转置结果
            doy_list_result = np.transpose(doy_list)
            print('生成DOY图像')
            FeatureCalculationMethodFacet.generate_tif(doy_list_result, template_tif_path, saved_path2)

            print(doy_list[116, 909])
            print(doy_list[216, 909])
            print(doy_list[316, 909])
            print(doy_list[416, 909])
            print(doy_list[516, 909])
            print('获取输出tif图数据中...')
            # time.sleep(1)
            # 遍历每个像素
            for i in trange(x):
                for j in range(y):
                    # 累积温度
                    accumulate_temperature = 0
                    # 空值跳过
                    if doy_list[i, j] == 0:
                        continue
                    for offset in range(durationTemp):
                        # 累积温度
                        # 该方式可能也可以使用
                        # cumulative_sum = np.cumsum(arr, axis=2)
                        accumulate_temperature = accumulate_temperature + temperature[
                            i, j, int(doy_list[i, j]) + offset]
                    # 输出总累积温度
                    result[i, j] = accumulate_temperature
                    # 输出总平均温度
                    # result[i, j] = accumulate_temperature / durationTemp
            transpose_result = np.transpose(result)
            return transpose_result

        rootPath = os.path.join(os.getcwd(), 'resource', 'surfaceProcessData')
        temperatureDir = os.path.join(rootPath, '时空抽取测试数据集', 'tif_250m')
        # extractDir = temperatureDir
        templateFile = os.path.join(temperatureDir, 'T20200101.tif')
        # threshold = 150
        # duration = 10
        # mode = '平均值'
        saved_path1 = os.path.join(
            rootPath,
            'resultData',
            'SpatiotemporalExtractionResult.tif')
        saved_path2 = os.path.join(
            rootPath,
            'resultData',
            'DayOfYear-ActiveAccumulatedTemperature.tif')
        result1 = space_time_extract(templateFile, temperatureDir, threshold, duration)
        FeatureCalculationMethodFacet.generate_tif(result1, templateFile, saved_path1)
        resultPathList = [saved_path1, saved_path2]
        return resultPathList

    # 计算降雨日数
    def rainfallDaysAccumulation(self, inputFields, param):
        # 复制新的变量
        print('===========接收参数===========')
        print(param)
        print(inputFields)
        startMD = param[0]
        tempS = startMD.split('-')
        startM, startD = int(tempS[1]), int(tempS[2])
        endMD = param[1]
        tempE = endMD.split('-')
        endM, endD = int(tempE[1]), int(tempE[2])
        rule = param[2]
        minNum = param[3]
        newColumn = str(startM) + '-' + str(startD) + '_' + str(endM) + '-' + str(endD) + '_' + '降雨日数'
        # duration = param[0][4]  # 暂未使用,默认1天
        # print(self.fieldName)
        if rule == '单日降水量':
            # 转换DayOfYear为日期
            self.dataFrame['日期'] = pd.to_datetime(
                self.dataFrame['年'].astype(str) +
                self.dataFrame['DayOfYear'].astype(str), format='%Y%j')
            # 根据上级单位、测报站点、年分类
            grouped = self.dataFrame.groupby(['上级单位', '测报站点', '年'])
            for (key, group) in grouped:
                start_date_range = datetime(key[2], startM, startD)
                end_date_range = datetime(key[2], endM, endD)
                rainy_days_count = len(
                    group[
                        (group['日期'] >= start_date_range) &
                        (group['日期'] <= end_date_range) &
                        (group[inputFields[0]] >= float(minNum))]
                )
                # print('==========具体明细==========')
                # print(group[
                #         (group['日期'] >= start_date_range) &
                #         (group['日期'] <= end_date_range) &
                #         (group[inputFields[0]] >= float(minNum))])
                # print(f'长度{rainy_days_count}')
                # Assign the calculated rainy days count to the '降雨日数' column within the specified date range
                mask = (self.dataFrame['上级单位'] == key[0]) & (self.dataFrame['测报站点'] == key[1]) & (
                        self.dataFrame['日期'] >= start_date_range) & (
                               self.dataFrame['日期'] <= end_date_range)
                self.dataFrame.loc[mask, newColumn] = rainy_days_count

            # # 删除还没生成的字段
            # tempReservedField = [field for field in self.reservedField if field in self.dataFrame.columns]
            # print(f'==============降雨日数-筛选特征{tempReservedField}================')
            # tempData = self.dataFrame[list(set(tempReservedField + ['降雨日数']))]
            # 删除'月','旬' '日期'字段
            self.dataFrame = self.dataFrame.drop(['日期'], axis=1)
            return self.dataFrame, newColumn

    # 基于活动积温的生育期计算
    def growthPeriodCalculation(self, inputFields, param):
        # 复制新的变量
        print('===========接收参数===========')
        print(param)
        print(inputFields)
        growthPeriod = param[0]
        start_day = param[1]
        end_day = param[2]
        threshold = int(param[3])
        # 根据上级单位、测报站点、年分类
        self.dataFrame['日期'] = pd.to_datetime(
            self.dataFrame['年'].astype(str) + self.dataFrame['DayOfYear'].astype(str), format='%Y%j')

        # 转换日期到年内的日期格式，忽略年份
        self.dataFrame['年内日期'] = self.dataFrame['日期'].dt.strftime('%m-%d')

        # 过滤数据，只保留在指定日期范围内的记录
        date_filter = (self.dataFrame['年内日期'] >= start_day) & (self.dataFrame['年内日期'] <= end_day)
        filtered_df = self.dataFrame.loc[date_filter]

        grouped = filtered_df.groupby(['上级单位', '测报站点', '年'])
        for (key, group) in grouped:

            # Calculate the cumulative temperature for each day in the range
            group['累计温度'] = np.cumsum(group['温度'])
            mask = group['累计温度'] >= threshold
            if mask.any():
                # 获取mask为True的行索引
                true_indices = group[mask].index[0]
                # 获取true_indices对应的DayOfYear值
                doy = group.loc[true_indices, 'DayOfYear']
                # 为该组的'上级单位', '测报站点', '年'赋值
                self.dataFrame.loc[(self.dataFrame['上级单位'] == key[0]) &
                                   (self.dataFrame['测报站点'] == key[1]) &
                                   (self.dataFrame['年'] == key[2]), growthPeriod] = doy
        self.dataFrame = self.dataFrame.drop(['日期'], axis=1)

        return self.dataFrame, growthPeriod
