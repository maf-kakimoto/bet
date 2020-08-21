# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
import time

# self made
import cleansing

def basicInfo(raceID,classify,condition_switch):
    raceInfo={'name':'','course':raceID["courseName"],'courseNum':raceID["courseNum"],'road':'','distance':'','outFlg':'0','condition':'','age':'','class':'','loaf':'','number':''}

    if classify == 'shutuba':
        url='https://race.netkeiba.com/race/shutuba_past.html?race_id=2020'+raceID['courseNum']+raceID['date']+raceID['No']+'&rf=shutuba'
    elif classify == 'result':
        url='https://race.netkeiba.com/race/result.html?race_id='+raceID['year']+raceID['courseNum']+raceID['date']+raceID['No']+'&rf=race_list'
    netkeiba = requests.get(url)
    netkeiba_soup = BeautifulSoup(netkeiba.content, "lxml")

    title=netkeiba_soup.select_one("title")
    for raceDate in title:
        raceDate=raceDate.split(" ")
        raceDate=raceDate[3]

    raceDate=raceDate.translate(str.maketrans({'年':'.','月':'.','日':None}))
    raceInfo['date']=raceDate
    raceName=netkeiba_soup.find_all("div",class_="RaceName")
    raceInfo['name']=cleansing.cleansing01(raceName)

    if raceInfo['name'] == '':
        return '',''

    raceData01=netkeiba_soup.select_one(".RaceData01")
    raceData01=raceData01.text
    raceData01=re.sub(r" ","",str(raceData01))
    raceData01=re.sub(r"\n","",str(raceData01))
    raceData01=raceData01.split("/")
    raceInfo['road']=raceData01[1][0]
    roadDinstance=raceData01[1]
    roadDinstance=roadDinstance.split("m")
    raceInfo['distance']=roadDinstance[0][1:]
    if '外' in raceData01[1]:
        raceInfo['outFlg']='1'
    if condition_switch != '9':
        raceInfo['condition']=condition_switch
    else:
        condition=raceData01[3]
        raceInfo['condition']=condition[3]

    raceData02=netkeiba_soup.find_all("div",class_="RaceData02")
    raceData02=re.sub(r"\n",",",str(raceData02))
    raceData02=cleansing.cleansing01(raceData02)
    raceData02=raceData02.split(",")
    raceInfo['age']=raceData02[4]
    raceClass=raceData02[5]
    raceClass = raceClass.translate(str.maketrans({'１':'1','２':'2'}))
    raceInfo['class']=re.sub('クラス', '', raceClass)

    raceInfo['loaf']=raceData02[8]
    number=raceData02[9]
    raceInfo['number']=number[:-1]

    return netkeiba_soup, raceInfo
