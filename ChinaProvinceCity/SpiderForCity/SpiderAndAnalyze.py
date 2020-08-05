import json

import requests
from lxml import etree

province = []

def getDate():
    url = "http://www.mca.gov.cn///article/sj/xzqh/2020/2020/202007170301.html"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en-CN;q=0.8,en;q=0.7",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Host": "www.mca.gov.cn",
        "Referer": "http://www.mca.gov.cn/article/sj/xzqh/2020/202007/20200700028728.shtml",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"
    }
    response = requests.get(url=url,headers=headers)
    return response

def analyzeDate():
    response = getDate()
    html = etree.HTML(response.text)
    provinceOrCity = html.xpath('//td[@class="xl704942"]/text()')
    countyOrDistrict = html.xpath('//td[@class="xl714942"]/text()')
    # there is something wrong in html
    countyOrDistrict.insert(len(countyOrDistrict)-1, "659010")
    # # for province
    # for i in range(0, len(provinceOrCity), 2):
    #     if str(provinceOrCity[i]).endswith("0000"):
    #         province.append({"code": provinceOrCity[i], "province": provinceOrCity[i+1], "cityList": []})
    # # for city

    allinfo = provinceOrCity+countyOrDistrict
    # for province
    for i in range(0,len(allinfo),2):
        if str(allinfo[i]).endswith("0000"):
            province.append({"code": allinfo[i], "province": allinfo[i+1], "cityList": []})
    # for city
    for item in province:
        # 北京、上海、天津、重庆 城市和省份名称一样
        if item['code'] in ['110000', '120000', '310000', '500000']:
            item['cityList'].append({'code': item['code'], 'city': item['province'], 'areaList': []})
        for i in range(0, len(allinfo), 2):
            if str(allinfo[i]).startswith(str(item['code'][0:2])) and (not str(allinfo[i]).endswith("0000")) and str(allinfo[i]).endswith("00"):
                item['cityList'].append({"code": allinfo[i], "city": allinfo[i+1], "areaList": []})
            # 不以00结尾的市
            if str(item['code']).startswith("65") and (int(allinfo[i]) in range(659001, 659011)):
                item['cityList'].append({"code": allinfo[i], "city": allinfo[i+1], "areaList": []})
            if str(item['code']).startswith("46") and (int(allinfo[i]) in range(469001, 469031)):
                item['cityList'].append({"code": allinfo[i], "city": allinfo[i+1], "areaList": []})
            if str(item['code']).startswith("42") and (int(allinfo[i]) in range(429004, 429022)):
                item['cityList'].append({"code": allinfo[i], "city": allinfo[i+1], "areaList": []})
            if str(item['code'])=="410000" and (allinfo[i]=="419001"):
                item['cityList'].append({"code": allinfo[i], "city": allinfo[i+1], "areaList": []})
    # for counties and districts
    for pro in province:
        for item in pro['cityList']:
            for i in range(0, len(allinfo), 2):
                # 前四位与市相同，后两位不为0（非北京、上海、天津、重庆），而且剔除不以00结尾的市，防止其放入城市的areaList中
                if str(allinfo[i])[0:4].startswith(str(item['code'])[0:4]) and (not str(allinfo[i]).endswith("00")) and (not (int(allinfo[i]) in range(659001, 659011))) and (not (int(allinfo[i]) in range(469001, 469031))) and (not (int(allinfo[i])==419001)) and (not (int(allinfo[i]) in range(429004, 429022))):
                    item["areaList"].append({"code": allinfo[i], "area": allinfo[i+1]})
                # 北京、上海、天津、重庆的区县都放入市中
                if str(item['code'])=="110000" and str(allinfo[i])[0:2]=="11" and (not str(allinfo[i]).endswith("00")):
                    item["areaList"].append({"code": allinfo[i], "area": allinfo[i+1]})
                if str(item['code'])=="120000" and str(allinfo[i])[0:2]=="12" and (not str(allinfo[i]).endswith("00")):
                    item["areaList"].append({"code": allinfo[i], "area": allinfo[i+1]})
                if str(item['code'])=="310000" and str(allinfo[i])[0:2]=="31" and (not str(allinfo[i]).endswith("00")):
                    item["areaList"].append({"code": allinfo[i], "area": allinfo[i+1]})
                if str(item['code'])=="500000" and str(allinfo[i])[0:2]=="50" and (not str(allinfo[i]).endswith("00")):
                    item["areaList"].append({"code": allinfo[i], "area": allinfo[i+1]})
    with open("data.json", "w") as f:
        f.write(str(province).replace("'", "\""))
        # json.dump(province,f)

if __name__ == '__main__':
        analyzeDate()