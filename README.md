# wind2json
decode CMA wind product data to leaflet-velocity json type

## 解析CMA-GFS/CMA-GD/CMA-SH地面和高空等模式资料风场数据，生成leaflet-velocity需要的json格式数据

## 需要安装`meteva`
```
pip install meteva
```

## what's leaflet-velocity

`leaflet-velocity` is here : https://github.com/onaci/leaflet-velocity

---

A plugin for Leaflet (v1.0.3, and v0.7.7) to create a canvas visualisation layer for direction and intensity of arbitrary velocities (e.g. wind, ocean current).

![Screenshot](https://github.com/onaci/leaflet-velocity/blob/master/screenshots/velocity.gif?raw=true)


## example:decode_from_gds
```python
from wind2json import Wind2Json
import datetime
filename = datetime.datetime.now().strftime("%y%m%d%H") + ".000"
path = f"GUANGZHOU_RUC/WIND/850/{filename}"
service = Wind2Json("10.1.20.100", 8080)
service.decode_from_gds(path)
service("wind.json")
```

## example:decode_from_file
```python
from wind2json import Wind2Json

path = f"24010123.001"
service = Wind2Json()
service.decode_from_file(path)
service(f"{path}.json")
```

