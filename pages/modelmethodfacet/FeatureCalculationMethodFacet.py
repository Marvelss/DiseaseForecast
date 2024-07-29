"""
@Author : SakuraFox
@Time: 2024-07-02 9:34
@File : FeatureCalculationMethodFacet.py
@Description : 面状特征计算方法
"""
from datetime import datetime

import numpy as np
import pandas as pd
import os

from osgeo import gdal
from tqdm import trange
import rasterio
import rpy2.robjects as robjects
from rpy2.robjects import pandas2ri
from rpy2.robjects.packages import importr


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
    def spatiotemporalExtraction(inputFileList, param):

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

        def space_time_extract(template_tif_path, temperatureFileList, featureFileList, cumulated_temperature,
                               durationTemp):
            """
            :param template_tif_path: 模板tif文件路径,主要用于获取tif图像属性
            :param temperatureFileList: 包含全部气象或遥感等数据的文件路径
            :param cumulated_temperature: 达到病害敏感时段起点的活动积温
            :param durationTemp: 抽取天数
            :return: result: 输出结果,二维数据
            """
            template_data = rasterio.open(template_tif_path[0])
            rows = template_data.width
            cols = template_data.height
            template_list = np.transpose(template_data.read(1))
            template_data.close()

            # 获取温度数据
            # 获取该文件夹下所有tif文件(得按照一年中的第几天的大小一次排序)
            tif_files = temperatureFileList
            # print(tif_files)

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
            # doy_list_result = np.transpose(doy_list)
            print('生成DOY图像')
            # FeatureCalculationMethodFacet.generate_tif(doy_list_result, template_tif_path[0], saved_path2)

            print(doy_list[116, 909])
            print(doy_list[216, 909])
            print(doy_list[316, 909])
            print(doy_list[416, 909])
            print(doy_list[516, 909])
            print('获取输出tif图数据中...')
            # time.sleep(1)

            # 获取特征所有数值
            tif_files = [0] * days_max
            # tif_files = 输入特征, 根据z赋值, 根据dayofyear赋值
            # 根据文件名中的 day_of_year 给 tif_files 赋值
            for file in featureFileList:
                fileT = os.path.basename(file)
                day_of_year = str(fileT).split('.')[0].split('_')[2]
                tif_files[int(day_of_year) - 1] = file  # day_of_year - 1 用于将 day_of_year 转换为0索引
            featureList = np.zeros((rows, cols, days_max), dtype=np.float32)
            for z in trange(days_max):
                file = tif_files[z]
                # 如果空则为0
                if file != 0:
                    dataset = rasterio.open(file)
                    pixel_value = dataset.read(1)
                    # 对pixel_value进行转置
                    pixel_value = np.transpose(pixel_value)
                    # 读取像素的数据,将二维矩阵赋值给三维矩阵中的每个z维度
                    featureList[:, :, z] = pixel_value
                    dataset.close()
                else:
                    featureList[:, :, z] = 0
            # 遍历特征抽取
            for i in trange(x):
                for j in range(y):
                    # 累积特征值
                    accumulate_value = 0
                    # 空值跳过
                    if doy_list[i, j] == 0:
                        continue
                    for offset in range(durationTemp):
                        # 累积特征值
                        # 该方式可能也可以使用
                        # cumulative_sum = np.cumsum(arr, axis=2)
                        accumulate_value = accumulate_value + featureList[
                            i, j, int(doy_list[i, j]) + offset]
                    # 输出总累积温度
                    # result[i, j] = accumulate_value
                    # 输出总平均温度
                    result[i, j] = accumulate_value / durationTemp
            transpose_result = np.transpose(result)
            return transpose_result

        rootPath = os.path.join(os.getcwd(), 'resource', 'surfaceProcessData')

        print('--------测试----------')
        print(param)
        temperature = param[0]
        extractFeatureList = eval(param[1])
        templateFile = param[2]
        threshold = int(param[3])
        duration = int(param[4])
        mode = param[5]

        # saved_path1 = param[6]

        # 起点温度暂时不保存
        # saved_path2 = os.path.join(
        #     rootPath,
        #     'resultData',
        #     'DayOfYear-ActiveAccumulatedTemperature.tif')

        def extract_info(filename):
            # 去掉文件扩展名
            base_name = filename.split('.')[0]
            # 根据'_'分割
            parts = base_name.split('_')
            temperature_type = parts[0]
            year = int(parts[1])
            day_of_year = int(parts[2])
            return temperature_type, year, day_of_year, filename

        temperatureFileListT = [file for file in inputFileList if temperature in file]

        # 提取文件信息
        file_info = [extract_info(file) for file in temperatureFileListT]

        # 按照 day_of_year 排序
        sorted_files = sorted(file_info, key=lambda x: x[2])
        # 提取排序后的温度文件名
        sorted_temperature_list = [file[3] for file in sorted_files]

        # 添加文件完整路径
        # 获取当前文件的目录
        current_file_dir = os.path.abspath(os.path.dirname(__file__))

        # 获取项目根目录，假设项目根目录在当前文件目录的上两级目录
        project_root = os.path.abspath(os.path.join(current_file_dir, '..', '..'))
        sorted_temperature_listT = [os.path.join(
            project_root, 'resource', 'uploadFileDir', file) for file in
            sorted_temperature_list]
        # print(sorted_temperature_listT)
        extractFeaturePathList = []

        for feature in extractFeatureList:
            featureFileListT = [file for file in inputFileList if feature in file]
            # 提取文件信息
            file_info = [extract_info(file) for file in featureFileListT]
            # 按照 day_of_year 排序
            sorted_files = sorted(file_info, key=lambda x: x[2])
            sorted_feature_list = [file[3] for file in sorted_files]
            # 添加文件完整路径
            current_file_dir = os.path.abspath(os.path.dirname(__file__))

            # 获取项目根目录，假设项目根目录在当前文件目录的上两级目录
            project_root = os.path.abspath(os.path.join(current_file_dir, '..', '..'))
            sorted_feature_listT = [os.path.join(
                project_root, 'resource', 'uploadFileDir', file) for file in
                sorted_feature_list]
            extractFeaturePathList.append(sorted_feature_listT)
        # print(f'======特征文件============:{extractFeaturePathList}')
        resultPathList = []
        for i in range(len(extractFeaturePathList)):
            result1 = space_time_extract(sorted_temperature_listT,
                                         sorted_temperature_listT, extractFeaturePathList[i],
                                         threshold, duration)
            saved_path = os.path.join(
                project_root, 'resource', 'surfaceProcessData',
                'resultData',
                f'{extractFeatureList[i]}_2015_SEResult.tif')
            FeatureCalculationMethodFacet.generate_tif(result1, extractFeaturePathList[i][0], saved_path)
            resultPathList.append(saved_path)
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

    # NDVI植被指数计算
    def onNDVI(self, methodParam):
        input_path, red, nir, output_path = (methodParam[0],
                                             methodParam[1],
                                             methodParam[2],
                                             methodParam[3])
        """
        :param input_path: 输入的栅格数据路径
        :param output_path: 输出的文件路径
        :param red: 红波段对应的波段数
        :param nir: 近红波段对应的波段数
        :return: 输出tif格式的NDVI计算结果图
        """
        ds = gdal.Open(input_path)  # 打开数据集dataset
        ds_width = ds.RasterXSize  # 获取数据宽度
        ds_height = ds.RasterYSize  # 获取数据高度
        ds_geo = ds.GetGeoTransform()  # 获取仿射地理变换参数
        ds_prj = ds.GetProjection()  # 获取投影信息
        # red是红波段对应的波段数
        array_red = ds.GetRasterBand(red).ReadAsArray(0, 0, ds_width, ds_height).astype(np.float64)
        # nir是近红波段对应的波段数
        array_nir = ds.GetRasterBand(nir).ReadAsArray(0, 0, ds_width, ds_height).astype(np.float64)
        # print("======归一化植被指数NDVI计算======")
        # 以数组的形式读取红波段和近红外波段
        b1 = array_nir - array_red
        b2 = array_nir + array_red
        # 计算NDVI
        NDVI_data = np.divide(b1, b2, out=np.zeros_like(b1), where=b2 != 0)
        # print("======生成输出文件======")
        driver = gdal.GetDriverByName('GTiff')  # 载入数据驱动，用于存储内存中的数组
        # 创建一个数组，宽高为原始尺寸
        ds_result = driver.Create(output_path, ds_width, ds_height, bands=1, eType=gdal.GDT_Float64)
        ds_result.SetGeoTransform(ds_geo)  # 导入仿射地理变换参数
        ds_result.SetProjection(ds_prj)  # 导入投影信息
        ds_result.GetRasterBand(1).SetNoDataValue(-9999)  # 将无效值设为9999
        ds_result.GetRasterBand(1).WriteArray(NDVI_data)  # 将NDVI的计算结果写入数组
        del ds_result  # 删除内存中的结果，否则结果不会写入图像中
        print("计算完成")

    # 景观指数计算
    def onLandscapeIndex(self, methodParam):
        a = methodParam[0]
        # 加载R的landscapemetrics包
        importr('landscapemetrics')
        # 读取本地数据
        # 相对路径
        path = 'fengtai2010.tif'
        # 绝对路径
        # path = r'E:\a_python\program\testPlatform\demo\demo140\fengtai2010.tif'
        # path = path.replace("\\", "/")  # 确保路径格式正确
        script = f'landscape <- terra::rast("{path}")'
        # 运行脚本
        robjects.r(script)
        # 运行R代码并获取结果
        robjects.r('enn_results4 <- lsm_c_lpi(landscape)')
        enn_results4 = robjects.r('enn_results4')

        # 启用pandas与rpy2之间的转换
        pandas2ri.activate()
        # 转换成pandas格式
        enn_results4_df = pandas2ri.rpy2py(enn_results4)
        # 打印结果数据框
        print(enn_results4_df)
        # 生成根据列名tif图
