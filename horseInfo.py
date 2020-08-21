# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
import time
import urllib.robotparser
import sys

# self made
import manage_mysql

def main(page,ageFrom,ageTo,active,year):

    if active == 1:
        activeFlg='active_horse=1'
    elif active == 0:
        activeFlg='cancell_horse=2'
    elif active == 9:
        activeFlg='horse='

    url="https://www.keibalab.jp/db/search/?search_string=&category=horse&category=horse&detail=1&age_from="+str(ageFrom)+"&age_to="+str(ageTo)+"&sort_list=1&"+activeFlg+"&page="+str(page)
    user_agent='xxx'
    headers={'User-Agent':user_agent}
    keibaLab=requests.get(url, headers=headers)
    keibaLab_soup=BeautifulSoup(keibaLab.content, 'lxml')
    horses=keibaLab_soup.find_all('a',href=re.compile('/horse/'))

    if len(horses) == 0:
        print('!!! No target !!!')
        sys.exit()

    horseNameList=[]
    horseCodeList=[]
    for item in horses:
        horseNameList.append(item.text)
        horse_code=item.attrs['href']
        horseCodeList.append(horse_code.split('/')[3])
    sexAge=keibaLab_soup.select('.age')
    sexList=[]
    ageList=[]
    for item in sexAge:
        if item.text != '性齢':
            sexList.append(item.text[0])
            ageList.append(item.text[1])
    father=keibaLab_soup.select('td[class="father"]')
    fatherList=[]
    fatherCodeList=[]
    for item in father:
        fatherList.append(item.text.replace('\n',''))
        if item.a is not None:
            fatherCode=item.a.attrs['href']
            fatherCode=fatherCode.split('/')
            fatherCodeList.append(fatherCode[3])
        else:
            fatherCodeList.append('')
    fatherLine=keibaLab_soup.select('.fline')
    fatherLineList=[]
    for item in fatherLine:
        if item.text != '父系':
            fatherLineList.append(item.text)
    mother=keibaLab_soup.select('.mother')
    motherList=[]
    for item in mother:
        item=item.text.replace('\n','')
        if item != '母':
            motherList.append(item)
    bmsLine=keibaLab_soup.select('.mondad')
    bmsList=[]
    bmsLineList=[]
    i=0
    for item in bmsLine:
        item = item.text.replace('\n','')
        if i%2 == 0:
            bmsList.append(item)
        else:
            bmsLineList.append(item)
        i+=1
    bms=keibaLab_soup.select('td[class="mondad"]')
    bmsCodeList=[]
    for item in bms:
        if item.a is not None:
            bmsCode=item.a.attrs['href']
            bmsCode=bmsCode.split('/')
            bmsCodeList.append(bmsCode[3])
        else:
            bmsCodeList.append('')
    trainer=keibaLab_soup.select('.trainer')
    trainerList=[]
    trainerCodeList=[]
    for item in trainer:
        trainerList.append(item.text.replace('\n',''))
        trainerCode=item.a.attrs['href']
        trainerCode=trainerCode.split('/')
        trainerCodeList.append(trainerCode[3])
    owner=keibaLab_soup.select('.owner')
    ownerList=[]
    ownerCodeList=[]
    for item in owner:
        if item.text != '馬主':
            ownerList.append(item.text.replace('\n',''))
            ownerCode=item.a.attrs['href']
            ownerCode=ownerCode.split('/')
            ownerCodeList.append(ownerCode[3])
    producer=keibaLab_soup.select('.producer')
    producerList=[]
    producerCodeList=[]
    for item in producer:
        if item.text != '生産者':
            producerList.append(item.text.replace('\n',''))
            producerCode=item.a.attrs['href']
            producerCode=producerCode.split('/')
            producerCodeList.append(producerCode[3])

    for i in range(len(horseNameList)):
        conn = manage_mysql.connect()
        c = conn.cursor()
        sql='SELECT count(*) from horseInfo where horse_code = "'+horseCodeList[i]+'"'
        c.execute(sql)
        result=c.fetchall()
        result=result[0][0]
        if result == 0:
            print(horseNameList[i])
            value="'"+horseNameList[i]+"'"
            value+=",'"+horseCodeList[i]+"'"
            value+=",'"+sexList[i]+"'"
            value+=",'"+str(year-int(ageList[i]))+"'"
            value+=",'"+fatherList[i]+"'"
            value+=",'"+fatherCodeList[i]+"'"
            value+=",'"+fatherLineList[i]+"'"
            value+=",'"+motherList[i]+"'"
            value+=",'"+bmsList[i]+"'"
            value+=",'"+bmsCodeList[i]+"'"
            value+=",'"+bmsLineList[i]+"'"
            value+=",'"+trainerList[i]+"'"
            value+=",'"+trainerCodeList[i]+"'"
            value+=",'"+ownerList[i]+"'"
            value+=",'"+ownerCodeList[i]+"'"
            value+=",'"+producerList[i]+"'"
            value+=",'"+producerCodeList[i]+"'"
            c.execute("INSERT INTO horseInfo VALUES ("+value+");")
        conn.commit()
        conn.close()



def weekly(year,age,pages):

    for i in range(pages):
        print(i+1)
        main(i+1,age,age,1,year)
        time.sleep(2)


if __name__ == '__main__':

    year=2020
    ageFrom=2
    ageTo=2

    # active=0 # disactive
    active=1 # active
    # active=9 # all

    for i in range(600):
        print(i+1)
        main(i+1,ageFrom,ageTo,active,year)
        time.sleep(2)
