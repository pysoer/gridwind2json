import meteva.base as meb
import numpy as np
import json
import datetime

__version__ = "1.0.1"

all = ["Wind2Json"]

header = {
    "discipline": 0,
    "disciplineName": "Meteorological products",
    "gribEdition": 2,
    "gribLength": 77171,
    "center": 7,
    "centerName": "CMA",
    "subcenter": 0,
    "refTime": "2016-04-06T12:00:00.000Z",
    "significanceOfRT": 1,
    "significanceOfRTName": "Start of forecast",
    "productStatus": 0,
    "productStatusName": "Operational products",
    "productType": 1,
    "productTypeName": "Forecast products",
    "productDefinitionTemplate": 0,
    "productDefinitionTemplateName": "Analysis/forecast at horizontal level/layer at a point in time",
    "parameterCategory": 2,
    "parameterCategoryName": "Momentum",
    "parameterNumber": 2,
    "parameterNumberName": "U-component_of_wind",
    "parameterUnit": "m.s-1",
    "genProcessType": 2,
    "genProcessTypeName": "Forecast",
    "forecastTime": 0,
    "surface1Type": 103,
    "surface1TypeName": "Specified height level above ground",
    "surface1Value": 10.0,
    "surface2Type": 255,
    "surface2TypeName": "Missing",
    "surface2Value": 0.0,
    "gridDefinitionTemplate": 0,
    "gridDefinitionTemplateName": "Latitude_Longitude",
    "numberPoints": 65160,
    "shape": 6,
    "shapeName": "Earth spherical with radius of 6,371,229.0 m",
    "gridUnits": "degrees",
    "resolution": 48,
    "winds": "true",
    "scanMode": 0,
    "nx": 360,
    "ny": 181,
    "basicAngle": 0,
    "subDivisions": 0,
    "lo1": 0.0,
    "la1": 90.0,
    "lo2": 359.0,
    "la2": -90.0,
    "dx": 1.0,
    "dy": 1.0,
}


class Wind2Json:
    """
    decode CMA-GFS wind product data to leaflet-velocity json type

    解析CMA-GFS风场数据，生成leaflet-velocity需要的json格式数据

    参数：
    gds_ip: GDS数据服务器IP地址
    gds_port: 数据服务器端口号
    """

    def __init__(self, gds_ip="", gds_port=8080):
        meb.gds_ip_port = (gds_ip, gds_port)
        self.jsondata = None

    def grd2json(self, grd) -> dict:
        jsondata = None
        try:
            m1 = grd.sel(
                level=grd.level.values[0],
                time=grd.time.values[0],
                dtime=grd.dtime.values[0],
            )
            # lat 方向需要反序
            m1 = m1.isel(lat=slice(None, None, -1))
            dataU = m1.sel(member="udata0").values.flatten()
            dataV = m1.sel(member="vdata0").values.flatten()
            dataV = np.round(dataV, 1)
            dataU = np.round(dataU, 1)

            lo1, lo2 = [m1.lon.values.min(), m1.lon.values.max()]
            la1, la2 = [m1.lat.values.max(), m1.lat.values.min()]
            dx, dy = [m1.lon[1] - m1.lon[0], m1.lat[1] - m1.lat[0]]
            nx, ny = [m1.lon.shape[0], m1.lat.shape[0]]
            # print(lo1,lo2,la1,la2,dx,dy,nx,ny)
            header["lo1"] = np.round(lo1, 2).astype(float)
            header["lo2"] = np.round(lo2, 2).astype(float)
            header["la1"] = np.round(la1, 2).astype(float)
            header["la2"] = np.round(la2, 2).astype(float)
            header["dx"] = float(abs(np.round(dx, 2)))
            header["dy"] = float(abs(np.round(dy, 2)))
            header["nx"] = int(np.round(nx, 0).astype(int))
            header["ny"] = int(np.round(ny, 0).astype(int))
            header["numberPoints"] = nx * ny
            m1Time = m1.time.values.astype(str)[:19]
            dtimedelta = int(grd.dtime.values[0])
            refTime = datetime.datetime.strptime(
                m1Time, "%Y-%m-%dT%H:%M:%S"
            ) + datetime.timedelta(hours=dtimedelta)
            header["refTime"] = refTime.strftime("%Y/%m/%d %H:%M:%S")
            headerU = header.copy()
            headerU["parameterNumberName"] = "U-component_of_wind"
            headerU["parameterCategory"] = "2"
            headerU["parameterNumber"] = "2"
            headerV = header.copy()
            headerV["parameterNumberName"] = "V-component_of_wind"
            headerV["parameterCategory"] = "2"
            headerV["parameterNumber"] = "3"
            jsondata = [
                {"header": headerU, "data": dataU.tolist()},
                {"header": headerV, "data": dataV.tolist()},
            ]
        except:
            print("读取gds_wind数据失败")
        return jsondata

    def decode_from_gds(self, path) -> dict:
        """
        从GDS服务器读取数据进行解析
        """
        grd = meb.io.read_gridwind_from_gds(path)
        if grd is None:
            print("没有找到gds_wind数据")
            return None
        self.jsondata = self.grd2json(grd)

    def decode_from_file(self, file) -> dict:
        """
        从本地GDS文件读取数据进行解析
        """
        grd = meb.io.read_gridwind_from_gds_file(file)
        self.jsondata = self.grd2json(grd)

    def __call__(self, path: str) -> bool:
        with open(path, "w") as f:
            json.dump(self.jsondata, f, ensure_ascii=False)
