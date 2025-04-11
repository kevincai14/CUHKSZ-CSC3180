
import requests

# 获取公网 IP
ip = requests.get("http://icanhazip.com").text.strip()
print("公网 IP:", ip)

# 获取位置信息
api_url = "https://restapi.amap.com/v3/ip"
params = {
    "key": "199e01334d40265440d6bbadd21f8015",  # 替换为你的 key
    "ip": ip
}
response = requests.get(api_url, params=params).json()
print("定位信息:", response)

# 获取经纬度范围
rectangle = response.get("rectangle", "")
if rectangle:
    lng1, lat1 = map(float, rectangle.split(";")[0].split(","))
    lng2, lat2 = map(float, rectangle.split(";")[1].split(","))
    center_lng = (lng1 + lng2) / 2
    center_lat = (lat1 + lat2) / 2

    # 请求静态地图
    map_api_url = "https://restapi.amap.com/v3/staticmap"
    map_params = {
        "location": f"{center_lng},{center_lat}",
        "zoom": "10",
        "size": "750*400",
        "markers": f"mid,,A:{center_lng},{center_lat}",
        "key": "199e01334d40265440d6bbadd21f8015"  # 替换为你的 key
    }

    map_resp = requests.get(map_api_url, params=map_params)

    # 显示地图
    from PIL import Image
    from io import BytesIO
    img = Image.open(BytesIO(map_resp.content))
    img.show()
