# -*- coding:utf-8 -*-
import re

import requests
import json
from concurrent.futures.thread import ThreadPoolExecutor

plates = ['hb', 'db', 'hd', 'hz', 'hn', 'xb', 'xn', 'gat']
data = []
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9,en-CN;q=0.8,en;q=0.7",
    "Cache-Control": "max-age=0",
    "Host": "www.weather.com.cn",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36"
}
def inputCityWeatherID():
    response = ""
    for item in plates:
        response_plate = requests.get("http://www.weather.com.cn/textFC/" + item + ".shtml")
        response_plate.encoding = response_plate.apparent_encoding
        response = response_plate.text + response
    search = re.compile(r'<a href="http://www.weather.com.cn/weather/(.*).shtml" target="_blank">(.*?)</a>')
    result = search.findall(response)
    cities_tuple = set()
    for city in result:
        if city[1] != "详情":
            cities_tuple.add(city)

    # for province
    province = requests.get("http://www.weather.com.cn/data/city3jdata/china.html", headers=headers)
    province.encoding = province.apparent_encoding
    province_json = json.loads(province.text)
    for province_code, province_name in province_json.items():
        province_data = {"province": province_name, "province_prefix_code": province_code, "cityList": []}
        if str(province_code) in ["10101", "10102", "10103", "10104"]:
            province_data['cityList'].append({"city": province_name, "city_code": province_code + "0100",
                                              "old_url": "http://www.weather.com.cn/weather/" + province_code + "0100" + ".shtml",
                                              "new_url": "http://www.weather.com.cn/weathern/" + province_code + "0100" + ".shtml",
                                              "areaList": []})
        # for city
        for city in cities_tuple:
            # 北京、上海、天津、重庆的区县
            if city[0].startswith(province_code) and str(province_code) in ["10101", "10102", "10103", "10104"]:
                province_data['cityList'][0]['areaList'].append({"area": city[1], "area_code": city[0], "old_url": "http://www.weather.com.cn/weather/"+city[0]+".shtml", "new_url": "http://www.weather.com.cn/weathern/"+city[0]+".shtml", "townList": []})
            elif city[0].startswith(province_code):
                province_data['cityList'].append({"city": city[1], "city_code": city[0], "old_url": "http://www.weather.com.cn/weather/"+city[0]+".shtml", "new_url": "http://www.weather.com.cn/weathern/"+city[0]+".shtml", "areaList": []})
        data.append(province_data)

    # for distinct
    search2 = re.compile(r'<a href="/textFC/(.*?).shtml" target="_blank">(.*?)</a>')
    result2 = search2.findall(response)
    province_to_distinct_tuple = set()
    for city_to_distinct_url in result2:
        province_to_distinct_tuple.add(city_to_distinct_url[0])
    distincts_html_all = ""
    for pro in province_to_distinct_tuple:
        distincts = requests.get("http://www.weather.com.cn/textFC/"+pro+".shtml",headers=headers)
        distincts.encoding = distincts.apparent_encoding
        distincts_html_all = distincts_html_all + str(distincts.text)
    search3 = re.compile(r'<a href="http://www.weather.com.cn/weather/(.*).shtml" target="_blank">(.*?)</a>')
    result3 = search3.findall(distincts_html_all)
    distincts_tuple = set()
    for distinct in result3:
        if distinct[1] != "详情":
            distincts_tuple.add(distinct)
    # 北京、上海、天津、重庆特殊处理
    for province_for_dis in data:
        if str(province_for_dis["province_prefix_code"]) in ["10101", "10102", "10103", "10104"]:
            continue
        else:
            for city in province_for_dis['cityList']:
                for dis in distincts_tuple:
                    if dis[0].startswith(str(city['city_code'])[0:7]):
                        city['areaList'].append({"area": dis[1], "area_code": dis[0], "old_url": "http://www.weather.com.cn/weather/"+dis[0]+".shtml", "new_url": "http://www.weather.com.cn/weathern/"+dis[0]+".shtml", "townList": []})
    with open("data.json", "w") as f:
        f.write(str(data).replace("\'", "\""))

def town():
    with open("data.json",'r') as f:
        data = f.read()
    data_json = json.loads(data)
    for pro in data_json:
        for city in pro['cityList']:
            for dis in city['areaList']:
                dis_html = requests.get(dis['new_url'],headers=headers)
                dis_html.encoding = dis_html.apparent_encoding
                search_in_dis_html = re.compile('var villages = (.*)')
                result = search_in_dis_html.findall(dis_html.text)
                if result != ['[]\r'] and result != []:
                    print(result)
                    for town in json.loads(result[0]):
                            dis['townList'].append({"town": town['name'], "town_code": town['id'], "new_url": "http://forecast.weather.com.cn/town/weathern/"+town['id']+".shtml"})
    with open("data.json", "w") as f:
        f.write(str(data_json).replace("\'", "\""))
        print("ok")




def pool():
    with ThreadPoolExecutor(max_workers=10) as pool:
        pool.submit(town)

if __name__ == '__main__':
    pool()