# -*- coding:utf-8 -*-
import json
import re

import requests
from datetime import datetime,date,time,timedelta
from lxml import etree
from concurrent.futures.thread import ThreadPoolExecutor
from pymongo import MongoClient

client = MongoClient(host="localhost", port=27017)
client.admin.authenticate("admin", "admin")

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gbk",
    "Accept-Language": "zh-CN,zh;q=0.9,en-CN;q=0.8,en;q=0.7",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Host": "www.weather.com.cn",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36"
}

def getCityOrAreaWeather(*args):
    old_url, new_url, province, city = args[0]
    area = ""
    # print(old_url, new_url)
    day_weather = {"province": province, "city":city, "area": area, "old_url":old_url, "new_url": new_url,"inputTime": datetime.now().strftime('%Y-%m-%d %H:%M'),
                   "updateTime": "", "source": "中央气象台", "weather&otherData": {
            "day-1": {}, "day0": {}, "day1": {}, "day2": {}, "day3": {}, "day4": {}, "day5": {}, "day6": {}
        }}
    response_old = requests.get(url=old_url,headers=headers)
    response_old.encoding = response_old.apparent_encoding
    response_new = requests.get(url=new_url, headers=headers)
    response_new.encoding = response_new.apparent_encoding
    html = etree.HTML(response_new.text.replace('\u200b', "").replace('\xa0', ""))
    updateTime = html.xpath('//input[@id="update_time"]/@value')
    day_weather['updateTime'] = updateTime[0]

    hour_weather_re = re.compile(r'"7d":(.*?)}')
    hour_weather = hour_weather_re.findall(response_old.text)[0]
    hour_weather_json = json.loads(hour_weather)
    more_weather_re = re.compile(r'"od2":(.*)}};')
    more_weather = more_weather_re.findall(response_old.text)[0]
    more_weather_list = json.loads(more_weather.replace("od21","time").replace("od22","temperature").replace("od23","polar_coordinates_of_the_wind").replace("od24","wind_direction").replace("od25","wind_grade").replace("od26","rainfall").replace("od27","relative_humidity").replace("od28","air_quality").replace("\'","\""))
    # print(more_weather_list)

    old_html = etree.HTML(response_old.text)
    relative_date_list = html.xpath('//p[@class="date-info"]/text()')
    day_weather_list = html.xpath('//p[@class="weather-info info-style"]/text()') + html.xpath('//p[@class="weather-info"]/text()')
    temperature_blue_sun_list = html.xpath('//div[@class="blueFor-container"]/script/text()')
    temperature_re = re.compile(r'\["(.+?)","(.+?)","(.+?)","(.+?)","(.+?)","(.+?)","(.+?)","(.+?)"\]')
    temperature = temperature_re.findall(temperature_blue_sun_list[0])
    blue_sun_re = re.compile(r'\["(.+?)","(.+?)","(.+?)","(.+?)","(.+?)","(.+?)","(.+?)"\]')
    blue_sun = blue_sun_re.findall(temperature_blue_sun_list[0])
    wind_html = html.xpath('//div[@class="wind-container"]')
    life_assistant_html = html.xpath('//div[@class="weather_shzs"]')
    life_index_html = old_html.xpath('//ul[@class="clearfix"]')
    # print(life_assistant_html[0].xpath('./ul/li/h2/text()'))
    # print(life_assistant_html[0].xpath('./div[1]/dl/dt/em/text()'))
    # print(life_assistant_html[0].xpath('./div[1]/dl/dd/text()'))

    list_index = 0
    for day in ["day-1","day0","day1","day2","day3","day4","day5","day6"]:
        # 日期=> 相对日期和绝对日期 //p[@class="date-info"]/text()
        day_weather['weather&otherData'][day]['absolute_date'] = (datetime.now()+timedelta(days=int(day.replace("day","")))).strftime('%Y-%m-%d')
        day_weather['weather&otherData'][day]['relative_date'] = relative_date_list[list_index]
        # 天气
        day_weather['weather&otherData'][day]['weather'] = day_weather_list[list_index]
        day_weather['weather&otherData'][day]['day_weather'] = wind_html[list_index].xpath('../i[1]/@title')[0]
        day_weather['weather&otherData'][day]['event_weather'] = wind_html[list_index].xpath('../i[2]/@title')[0]
        # 温度+蓝天指数+日落日出
        day_weather['weather&otherData'][day]['day_temperature'] = temperature[0][list_index] + "℃"
        day_weather['weather&otherData'][day]['event_temperature'] = temperature[1][list_index] + "℃"
        if list_index == 0:
            day_weather['weather&otherData'][day]['sun_up'] = "none"
            day_weather['weather&otherData'][day]['sun_set'] = "none"
            day_weather['weather&otherData'][day]['blue_index'] = "none"
        else:
            day_weather['weather&otherData'][day]['sun_up'] = blue_sun[4][list_index-1]
            day_weather['weather&otherData'][day]['sun_set'] = blue_sun[5][list_index-1]
            day_weather['weather&otherData'][day]['blue_index'] = blue_sun[6][list_index-1]
        # wind
        day_weather['weather&otherData'][day]['day_wind_direction'] = wind_html[list_index].xpath('./i[1]/@title')[0]
        day_weather['weather&otherData'][day]['event_wind_direction'] = wind_html[list_index].xpath('./i[2]/@title')[0]
        day_weather['weather&otherData'][day]['wind_grade'] = wind_html[list_index].xpath('./../p[3]/text()')[0]
        # 生活助手 life_assistant
        if list_index == 0:
            day_weather['weather&otherData'][day]['life_assistant'] = []
        else:
            list = []
            for i in range(0,6):
                list.append({"assistant_type": life_assistant_html[0].xpath('./ul/li/h2/text()')[i].replace("·",""),"assistant_grade": life_assistant_html[0].xpath('./div['+str(list_index)+']/dl/dt/em/text()')[i],"assistant_description": life_assistant_html[0].xpath('./div['+str(list_index)+']/dl/dd/text()')[i]})
            day_weather['weather&otherData'][day]['life_assistant'] = list
        # 生活指数 life index
        list = []
        # print(life_index_html[0])
        if list_index != 0:
            for i in range(1, 7):
                # print(life_index_html[list_index].xpath('./li[6]//p/text()'))
                # print(old_url,life_index_html[list_index].xpath('./li[2]//span/em[@class="star"]'))
                if i != 2:
                    list.append({"life_index_type": life_index_html[list_index-1].xpath('./li['+str(i)+']//em/text()')[0].replace("健臻·",""),"life_index_grade": life_index_html[list_index-1].xpath('./li['+str(i)+']//span/text()')[0],"life_index_description": life_index_html[list_index-1].xpath('./li['+str(i)+']//p/text()')[0]})
                else:
                    list.append({"life_index_type": life_index_html[list_index-1].xpath('./li[2]//em/text()')[0].replace("健臻·",""),"star": len(life_index_html[list_index-1].xpath('./li[2]//span/em[@class="star"]')),"life_index_description": life_index_html[list_index-1].xpath('./li[2]//p/text()')[0]})
        # print(list)
        day_weather['weather&otherData'][day]['life_index'] = list

        # hour weather
        day_weather['weather&otherData'][day]['hour_weather'] = []
        if list_index == 0:
            pass
        else:
            today_hour_weather = hour_weather_json[list_index-1]
            # print(today_hour_weather)
            for item in today_hour_weather:
                search = re.compile(r'((?P<day>.*?)日(?P<hour>.*?)时),(.*?),(?P<weather>.*?),(?P<temperature>.*?),(?P<wind_direction>.*?),(?P<wind_grade>.*?),(?P<blue_index>.*)')
                search_result = search.search(item)
                # print(search_result.groupdict())
                search_dict = search_result.groupdict()
                day_weather['weather&otherData'][day]['hour_weather'].append({"time": datetime.now().strftime('%Y-%m-') + search_dict['day'] + " " + search_dict['hour'],"hour_weather": search_dict['weather'],"hour_temperature": search_dict['temperature'],"hour_wind_direction": search_dict['wind_direction'],"hour_wind_grade": search_dict['wind_grade'],"hour_blue_index": search_dict['blue_index']})
        # more_hour_weather 整点天气实况
        day_weather['weather&otherData'][day]['more_hour_weather'] = []
        if list_index == 1:
            for dict in more_weather_list:
                dict['time'] = datetime.now().strftime('%Y-%m-%d') + " " +dict['time']
                dict['temperature'] = dict['temperature'] + "℃"
                dict['polar_coordinates_of_the_wind'] = dict['polar_coordinates_of_the_wind'] + "°"
                dict['rainfall'] = dict['rainfall'] + "mm"
                dict['relative_humidity'] = dict['relative_humidity'] + "%"
                if dict['air_quality'] != "":
                    dict['air_quality'] = dict['air_quality'] + "μg/m3"
            day_weather['weather&otherData'][day]['more_hour_weather'] = more_weather_list
        list_index += 1
    # print(str(day_weather).replace("\'","\""))
    # print(str(day_weather).replace("\'","\""))
    # print(province)
    if area == "":
        print("->  " + province + " - " + city)
    else:
        print("->  " + province + " - " + city + " - " + area)
    client.Weather.City.insert_one(day_weather)
    print("ok")
def pool():
    city_list = []
    with open("../CityWeatherID_v2/data.json") as f:
        data = json.load(f)
    for province in data:
        for city in province['cityList']:
            city_list.append((city['old_url'],city['new_url'],province['province'],city['city']))
    with ThreadPoolExecutor(max_workers=20) as pool:
        pool.map(getCityOrAreaWeather,city_list)

if __name__ == '__main__':
    print("begin ...")
    pool()
    print("end ...")
    # getCityOrAreaWeather(("http://www.weather.com.cn/weather/101050801.shtml","http://www.weather.com.cn/weathern/101050801.shtml","伊春",""))
