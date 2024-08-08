"""
@Author : SakuraFox
@Time: 2024-07-02 9:34
@File : PretreatmentMethodFacet.py
@Description : 面状数据预处理方法
"""
import geopandas as gpd
import rasterio
import numpy as np
from osgeo import gdal, ogr
from pykrige.ok import OrdinaryKriging
from rasterio.mask import mask


class PretreatmentMethodFacet:
    def __init__(self):
        pass

    # 加工字段名称
    def getHandledField(self, fieldNameTemp):
        temp = fieldNameTemp.split('.')
        fieldName = temp[0]
        fileFormat = temp[1]
        # 若字段为原始数据
        if '_预' not in fieldName:
            return f"{fieldName}_预处理后" + '.' + fileFormat
        # 若字段已处理,则末尾数字+1
        if '_预' in fieldName:
            return (fieldName.split('后')[0] + '后' +
                    str(int(fieldName.split('后')[1]) + 1)) + '.' + fileFormat

    # 空间插值
    def spatialInterpolation(self, methodParam):
        """
        idw空间插值
        :param output_file:插值结果
        :param point_station_file: 矢量站点数据
        :return:
        """
        # output_file, point_station_file, attrName
        # print(f'========测试参数========{methodParam}')
        point_station_file = methodParam[0]
        attrName = methodParam[1]
        interpolationMethod = methodParam[2]
        outputBoundsTemp = methodParam[3].split(' ')
        outputFileTemp = methodParam[4]
        outputFile = outputFileTemp
        # print('============测试输入参数============')
        # print(point_station_file)
        # print(attrName)
        # print(interpolationMethod)
        # print(outputBoundsTemp)
        # print(outputFile)
        if interpolationMethod != '克里金插值':
            # 默认为反距离权重法
            algorithmTemp = 'invdist:power=3.6:smoothing=0.2:radius1=0.0:radius2=0.0:angle=0.0:max_points=0:min_points=0:nodata=-9999'
            # 代码调用outputBounds定义范围
            if interpolationMethod == '线性插值':
                algorithmTemp = 'linear:radius1=0.0:radius2=0.0:nodata=-9999'
            elif interpolationMethod == '最近邻插值':
                algorithmTemp = 'nearest:radius1=0.0:radius2=1.0:nodata=-9999'
            elif interpolationMethod == '移动平均法':
                algorithmTemp = 'average:radius1=0.0:radius2=0.0:nodata=-9999'
            opts = gdal.GridOptions(
                algorithm=algorithmTemp,
                format="GTiff", outputType=gdal.GDT_Float32, zfield=attrName,
                outputBounds=outputBoundsTemp)
            gdal.Grid(destName=outputFile, srcDS=point_station_file, options=opts)

        elif interpolationMethod == '克里金插值':
            # 1. 读取shp文件
            gdf = gpd.read_file(point_station_file)

            # 假设shp文件有名为'geometry'的列和需要插值的'values'列
            coordinates = np.array([(geom.x, geom.y) for geom in gdf.geometry])
            values = gdf[attrName].values

            # 2. 读取模板TIFF文件
            template_tif = methodParam[5]
            with rasterio.open(template_tif) as src:
                template_transform = src.transform
                template_crs = src.crs
                template_bounds = src.bounds
                template_shape = src.shape

            # 定义目标栅格的分辨率
            gridx = np.linspace(template_bounds.left, template_bounds.right, template_shape[1])
            gridy = np.linspace(template_bounds.bottom, template_bounds.top, template_shape[0])

            # 3. 执行克里金插值
            ok = OrdinaryKriging(
                coordinates[:, 0],
                coordinates[:, 1],
                values,
                variogram_model='linear',
                verbose=False,
                enable_plotting=False
            )
            z, ss = ok.execute('grid', gridx, gridy)

            # 5. 保存插值结果为TIFF文件
            output_tif = outputFileTemp

            with rasterio.open(
                    output_tif, 'w', driver='GTiff',
                    height=template_shape[0], width=template_shape[1],
                    count=1, dtype=z.dtype,
                    crs=template_crs,
                    transform=template_transform,
            ) as dst:
                dst.write(z, 1)
        return outputFileTemp

    def onResample(self, methodParam):  # 影像重采样
        """
        :param path_refer: 重采样参考文件路径
        :param path_resample: 需要重采样的文件路径
        :param out_path_resample: 重采样后的输出路径
        """
        path_resample = methodParam[0]
        interpolationMethod = methodParam[1]
        path_refer = methodParam[2]
        out_path_resample = self.getHandledField(methodParam[3])

        # path_refer, path_resample, out_path_resample
        ds_refer = gdal.Open(path_refer, gdal.GA_ReadOnly)  # 打开数据集dataset
        proj_refer = ds_refer.GetProjection()  # 获取投影信息
        trans_refer = ds_refer.GetGeoTransform()  # 获取仿射地理变换参数
        band_refer = ds_refer.GetRasterBand(1)  # 获取波段
        width_refer = ds_refer.RasterXSize  # 获取数据宽度
        height_refer = ds_refer.RasterYSize  # 获取数据高度
        bands_refer = ds_refer.RasterCount  # 获取波段数
        ds_resample = gdal.Open(path_resample, gdal.GA_ReadOnly)  # 打开数据集dataset
        proj_resample = ds_resample.GetProjection()  # 获取输入影像的投影信息
        driver = gdal.GetDriverByName('GTiff')  # 定义输出的数据资源
        ds_output = driver.Create(out_path_resample, width_refer, height_refer, bands_refer,
                                  band_refer.DataType)  # 创建重采样影像
        ds_output.SetGeoTransform(trans_refer)  # 设置重采样影像的仿射地理变换
        ds_output.SetProjection(proj_refer)  # 设置重采样影像的投影信息

        if interpolationMethod == '最近邻插值':
            gdal.ReprojectImage(ds_resample, ds_output, proj_resample, None, gdal.GRA_NearestNeighbour, 0.0, 0.0, )
        elif interpolationMethod == '双线性插值':
            gdal.ReprojectImage(ds_resample, ds_output, proj_resample, None, gdal.GRA_Bilinear, 0.0, 0.0, )
        elif interpolationMethod == '三次卷积插值':
            gdal.ReprojectImage(ds_resample, ds_output, proj_resample, None, gdal.GRA_Cubic, 0.0, 0.0, )
        elif interpolationMethod == '三次样条插值':
            gdal.ReprojectImage(ds_resample, ds_output, proj_resample, None, gdal.GRA_CubicSpline, 0.0, 0.0, )
        elif interpolationMethod == 'Lanczos重采样':
            gdal.ReprojectImage(ds_resample, ds_output, proj_resample, None, gdal.GRA_Lanczos, 0.0, 0.0, )
        elif interpolationMethod == '平均法':
            gdal.ReprojectImage(ds_resample, ds_output, proj_resample, None, gdal.GRA_Average, 0.0, 0.0, )
        elif interpolationMethod == '模式插值法':
            gdal.ReprojectImage(ds_resample, ds_output, proj_resample, None, gdal.GRA_Mode, 0.0, 0.0, )
        # 输入数据集、输出数据集、输入投影、参考投影、重采样方法(最邻近内插\双线性内插\三次卷积等)、回调函数
        # 确保 NoData 值正确设置
        nodata_value = 0
        for i in range(1, bands_refer + 1):
            band = ds_output.GetRasterBand(i)
            band_data = band.ReadAsArray()
            band_data[band_data == nodata_value] = nodata_value
            band.WriteArray(band_data)
        return out_path_resample

    def onClipRaster(self, methodParam):  # 影像重采样
        beClipFile = methodParam[0]
        templateShapeFile = methodParam[1]
        outputFile = self.getHandledField(methodParam[2])

        # 1. 读取行政区边界shapefile
        shapefile = templateShapeFile

        input_tif = beClipFile
        gdf = gpd.read_file(shapefile)

        # 2. 确保行政区边界的CRS与TIFF文件一致
        template_tif = input_tif
        with rasterio.open(template_tif) as src:
            tiff_crs = src.crs

        if gdf.crs != tiff_crs:
            gdf = gdf.to_crs(tiff_crs)
        # 4. 使用行政区边界进行裁剪
        # 如果shapefile包含多个几何体，可以选择一个或合并
        geometry = [gdf.geometry.union_all()]

        # 裁剪
        with rasterio.open(input_tif, nodata=-99) as src:
            out_image, out_transform = mask(src, geometry, crop=True)
            out_meta = src.meta

        # 更新裁剪后的元数据
        out_meta.update({
            "driver": "GTiff",
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform
        })

        # 4. 保存裁剪后的TIFF文件
        with rasterio.open(outputFile, 'w', **out_meta) as dst:
            dst.write(out_image)


# 剔除异常值
def outlierEliminator(self, methodParam):
    # 处理单个字段
    self.fieldName = self.fieldName[0]
    minNum, maxNum = float(methodParam[1]), float(methodParam[0])
    # 复制新的变量
    newDataFrame = self.dataFrame.copy()

    newDataColumn = self.getHandledField(self.fieldName)
    print(f'剔除异常值:{self.fieldName}-{newDataColumn}')
    newDataFrame[newDataColumn] = newDataFrame[self.fieldName]

    # 获取原始记录数
    lengthBefore = len(newDataFrame)
    # newDataFrame[self.fieldName] = newDataFrame[self.fieldName].clip(minNum, maxNum)
    newDataFrame = newDataFrame[
        (newDataFrame[self.fieldName] >= minNum) &
        (newDataFrame[self.fieldName] <= maxNum)]
    lengthAfter = len(newDataFrame)
    # 检查是否还有缺失值
    tempData = newDataFrame
    return tempData, str(lengthBefore - lengthAfter), lengthAfter, newDataColumn
