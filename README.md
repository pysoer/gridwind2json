# CMAwind2leaflet-velocity
decode CMA-GFS wind product data to leaflet-velocity json type

## 解析CMA-GFS风场数据，生成leaflet-velocity需要的json格式数据
## 支持CMA-GFS 地面和高空，CMA-GD、SH等模式资料。
## 需要安装`meteva`
```
pip install meteva
```

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

