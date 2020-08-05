# -*- coding:utf-8 -*-
import requests
import json
from concurrent.futures.thread import ThreadPoolExecutor

weather = []
header = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9,en-CN;q=0.8,en;q=0.7",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Host": "toy1.weather.com.cn",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"
}
proxy = {
    "http": "221.229.196.93:25613"
}

def getCity():
    with open("../ChinaProvinceCity/SpiderForCity/data.json", "r") as f:
        data = json.load(f)
    return data

def inputCityWeatherID():
    data = getCity()
    for item in data:
        if item['province'] in ["台湾省", "香港特别行政区", "澳门特别行政区"]:
            continue
        province = {"province": item['province'], "cityList": []}
        for city in item['cityList']:
            if "胡杨河市" in city['city']:
                cityName = "胡杨"
            elif "河市" in city['city'] or "州市" in city['city']:
                cityName = city['city'].replace("市", "")
            elif "朝阳市" == city['city']:
                cityName = "朝阳"
            else:
                cityName = city['city'].replace("河市", "").replace("市",
                                                                                                             "").replace(
                    "鲜族自治州", "").replace("地区", "").replace("土家族苗族自治州", "").replace("林区", "").replace("土家族苗族自治州",
                                                                                                     "").replace("县",
                                                                                                                 "").replace(
                    "黎族自治", "").replace("黎族苗族自治", "").replace("州", "").replace("藏族羌族自治", "").replace("藏族自治",
                                                                                                     "").replace(
                    "彝族自治", "").replace("布依族苗族自治", "").replace("苗族侗族自治", "").replace("彝族自治", "").replace("哈尼族彝族自治",
                                                                                                         "").replace(
                    "壮族苗族自治", "").replace("傣族自治", "").replace("白族自治", "").replace("傣族景颇族自治", "").replace("傈僳族自治",
                                                                                                         "").replace(
                    "藏族自治",
                    "").replace(
                    "地区", "").replace("回族自治", "").replace("蒙古族藏族自治", "").replace("回族自治", "").replace("蒙古自治",
                                                                                                     "").replace(
                    "柯尔克孜自治", "").replace("哈萨克自治", "").replace("朝鲜族自治", "").replace("哈尼族", "").replace("蒙古族",
                                                                                                       "").replace(
                    "朝", "")
            url = "http://toy1.weather.com.cn/search?cityname=" + cityName
            response = requests.get(url=url, headers=header)
            result = response.text.replace("(", "").replace(")", "").replace("'", "")
            response.close()
            province['cityList'].append({"city": city['city'], "code": result[9:18], "areaList": []})
            for area in city['areaList']:
                url2 = "http://toy1.weather.com.cn/search?cityname=" + area['area'].replace("区", "").replace("县", "").replace("市", "").replace("自治", "").replace("满族自治县", "").replace("回族自治县", "")
                response2 = requests.get(url=url2, headers=header)
                result2 = response2.text.replace("(", "").replace(")", "").replace("'", "")
                province['cityList'][0]['areaList'].append({'area': area['area'], 'code': result2[9:18]})
        weather.append(province)
    for pro in ["台湾省", "香港特别行政区", "澳门特别行政区"]:
        province = {"province": pro, "cityList": []}
        p = requests.get(url="http://toy1.weather.com.cn/search?cityname="+pro.replace("省", "").replace("特别行政区", ""), headers=header)
        p_json = json.loads(p.text.replace("(", "").replace(")", ""))
        for city in p_json:
            index1 = str(city).find("~")
            index2 = str(city).find("~", index1 + 1)
            index3 = str(city).find("~", index2 + 1)
            if "巴西" not in str(city) and "山东" not in str(city) and "安徽" not in str(city):
                province['cityList'].append({"city": str(city)[index2+1:index3], "code": str(city)[9:18], "areaList": []})
                print(city)
        weather.append(province)
    with open("./data.json", "w") as f:
        f.write(str(weather).replace("'", "\""))



                # if response2.text != "[()]" and item['province'].replace("省", "").replace("自治区", "").replace("市", "").replace("壮族", "").replace("维吾尔", "").replace("回族", "") not in response2.text:
                #     print(area['area'],response2.text)



            # if cityName in result and item['province'].replace("省", "").replace("自治区", "").replace("市", "").replace("壮族", "").replace("维吾尔", "").replace("回族", "") in result:
            #     print("ok")
            # else:
            #     print(url)
            #     print(item['province'])


def pool():
    with ThreadPoolExecutor(max_workers=10) as pool:
        pool.submit(inputCityWeatherID)

if __name__ == '__main__':
    pool()