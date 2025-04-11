import requests
import xml.etree.ElementTree as ET

# 构建请求
url = "https://restapi.amap.com/v3/direction/driving"
params = {
    "origin": "116.481028,39.989643",
    "destination": "116.465302,40.004717",
    "extensions": "all",
    "output": "xml",
    "key": "199e01334d40265440d6bbadd21f8015"
}

# 发送请求
response = requests.get(url, params=params)

# 解析 XML
root = ET.fromstring(response.text)

# 获取第一个路径方案
path = root.find(".//path")  # paths 下的第一个 path
steps = path.findall("steps/step")

print("导航路径如下：\n")

# 遍历每个 step（导航步骤）
for i, step in enumerate(steps, 1):
    road = step.find("road").text if step.find("road") is not None else "未知道路"
    instruction = step.find("instruction").text if step.find("instruction") is not None else "无指示"
    distance = step.find("distance").text if step.find("distance") is not None else "0"
    polyline = step.find("polyline").text if step.find("polyline") is not None else "无坐标"

    print(f"第 {i} 步：")
    print(f"  道路名称：{road}")
    print(f"  导航指示：{instruction}")
    print(f"  距离：{distance} 米")
    print(f"  坐标串：{polyline}")
    print()
