# -*- coding:utf-8 -*-
import json
import re

import requests
from datetime import datetime,date,time,timedelta
from lxml import etree

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

def getCityWeather(old_url,new_url,city):
    print(old_url, new_url)
    day_weather = {"city": city, "inputTime": datetime.now().strftime('%Y-%m-%d %H:%M'),
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

    # 日期=> 相对日期和绝对日期 //p[@class="date-info"]/text()
    relative_date_list = html.xpath('//p[@class="date-info"]/text()')
    day_weather_list = html.xpath('//p[@class="weather-info info-style"]/text()') + html.xpath('//p[@class="weather-info"]/text()')
    temperature_blue_sun_list = html.xpath('//div[@class="blueFor-container"]/script/text()')
    temperature_re = re.compile(r'\["(.+?)","(.+?)","(.+?)","(.+?)","(.+?)","(.+?)","(.+?)","(.+?)"\]')
    temperature = temperature_re.findall(temperature_blue_sun_list[0])
    blue_sun_re = re.compile(r'\["(.+?)","(.+?)","(.+?)","(.+?)","(.+?)","(.+?)","(.+?)"\]')
    blue_sun = blue_sun_re.findall(temperature_blue_sun_list[0])
    wind_html = html.xpath('//div[@class="wind-container"]')
    life_assistant_html = html.xpath('//div[@class="weather_shzs"]')
    # print(life_assistant_html[0].xpath('./ul/li/h2/text()'))
    # print(life_assistant_html[0].xpath('./div[1]/dl/dt/em/text()'))
    # print(life_assistant_html[0].xpath('./div[1]/dl/dd/text()'))
    list_index = 0
    for day in ["day-1","day0","day1","day2","day3","day4","day5","day6"]:
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
            day_weather['weather&otherData'][day]['life_assistant'] = "none"
        else:
            list = []
            for i in range(0,6):
                list.append({"assistant_type": life_assistant_html[0].xpath('./ul/li/h2/text()')[i].replace("·",""),"assistant_grade": life_assistant_html[0].xpath('./div['+str(list_index)+']/dl/dt/em/text()')[i],"assistant_description": life_assistant_html[0].xpath('./div['+str(list_index)+']/dl/dd/text()')[i].replace("。","")})
            day_weather['weather&otherData'][day]['life_assistant'] = list

        list_index += 1
    print(str(day_weather).replace("\'","\""))

getCityWeather("http://www.weather.com.cn/weather/101051101.shtml","http://www.weather.com.cn/weathern/101051101.shtml","鸡西")