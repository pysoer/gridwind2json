import meteva.base as meb
import numpy as np
import json
import datetime

__version__ = "1.0.4"

all = ["Wind2Json"]

header = {
    "centerName": "CMA",
    "refTime": "2016-04-06T12:00:00.000Z",
    "parameterCategory": 2,
    "parameterNumber": 2,
    "parameterNumberName": "U-component_of_wind",
    "parameterUnit": "m.s-1",
    "dtime": 0,
    "nx": 360,
    "ny": 181,
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
    step: 抽稀步长，即经纬度分辨率，默认为0.1(数据量太大时流场会有偏差)
    """

    def __init__(self, gds_ip="", gds_port=8080, step=0.1):
        meb.gds_ip_port = (gds_ip, gds_port)
        self.step = step
        self.jsondata = None

    def grd2json(self, grd) -> None:
        self.jsondata = None
        m1 = grd.sel(
            level=grd.level.values[0],
            time=grd.time.values[0],
            dtime=grd.dtime.values[0],
        )
        # lat 方向需要反序
        m1 = m1.isel(lat=slice(None, None, -1))
        # 对数据进行抽稀，直到步长小于等于self.step
        while True:
            m1 = m1.isel(lon=slice(None, None, 2), lat=slice(None, None, 2))
            if m1.lon[1] - m1.lon[0] >= self.step:
                break
        dataU = m1.sel(member="udata0").values.flatten()
        dataV = m1.sel(member="vdata0").values.flatten()
        dataV = np.round(dataV, 1)
        dataU = np.round(dataU, 1)
        lo1, lo2 = [m1.lon.values.min(), m1.lon.values.max()]
        la1, la2 = [m1.lat.values.max(), m1.lat.values.min()]
        dx, dy = [m1.lon[1] - m1.lon[0], m1.lat[1] - m1.lat[0]]
        nx, ny = [m1.lon.shape[0], m1.lat.shape[0]]
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
        self.jsondata = [
            {"header": headerU, "data": dataU.tolist()},
            {"header": headerV, "data": dataV.tolist()},
        ]

    def decode_from_gds(self, path) -> None:
        """
        从GDS服务器读取数据进行解析
        """
        grd = meb.io.read_gridwind_from_gds(path)
        self.grd2json(grd)

    def decode_from_file(self, file) -> None:
        """
        从本地GDS文件读取数据进行解析
        """
        grd = meb.io.read_gridwind_from_gds_file(file)
        self.grd2json(grd)

    def __call__(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump(self.jsondata, f, ensure_ascii=False)
