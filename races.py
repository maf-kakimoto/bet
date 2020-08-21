# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
import codecs
import time
import os
import sys

# self-made
import conversion


def basicInfo(raceID):

    raceInfo={'year':raceID['year'],'holding':raceID['date'],'courseNum':raceID['courseNum'],'No':raceID['No'],'courseNum':raceID['courseNum'],
            'raceName':'','road':'','distance':'','outFlg':'0','condition':'','age':'','class':'','loaf':'','number':'',
            'date':'','weather':'0','sex':'0','jump_flg':'0'}
    netkeiba = requests.get('https://db.netkeiba.com/race/'+raceID['year']+raceID['courseNum']+raceID['date']+raceID['No']+'/')
    netkeiba_soup = BeautifulSoup(netkeiba.content, 'lxml')

    print('https://db.netkeiba.com/race/'+raceID['year']+raceID['courseNum']+raceID['date']+raceID['No']+'/')

    title=netkeiba_soup.select_one('title')
    title=title.text
    title=title.translate(str.maketrans({'｜':',', '|':',', ' ':None}))
    title=title.split(',')
    name=title[0]
    raceInfo['raceName'] = name
    raceInfo['date'] = title[1].translate(str.maketrans({'年':'-','月':'-','日':None}))

    basic_data=netkeiba_soup.select_one('.racedata')
    basic_data=basic_data.span.text
    basic_data=basic_data.translate(str.maketrans({'\xa0':'',' ':''}))
    basic_data=basic_data.split('/')
    road=basic_data[0][0]
    raceInfo['road']=conversion.roadbed_flg(road)
    raceInfo['distance'] = re.sub('\\D','',basic_data[0])
    if '外' in basic_data[0]:
        raceInfo['outFlg'] = '1'
    condition = basic_data[2].split(':')[1]
    raceInfo['condition']=conversion.condition_flg(condition)
    weather = basic_data[1].split(':')[1]
    if weather == '晴':
        raceInfo['weather'] = '0'
    elif weather == '曇':
        raceInfo['weather'] = '1'
    elif weather == '雨':
        raceInfo['weather'] = '2'
    elif weather == '小雨':
        raceInfo['weather'] = '3'
    elif weather == '雪':
        raceInfo['weather'] = '4'
    elif weather == '小雪':
        raceInfo['weather'] = '5'

    detail_data=netkeiba_soup.select_one('.smalltxt')
    detail_data=detail_data.text
    if '2歳' in detail_data:
        raceInfo['age'] = '2'
    elif '3歳以上' in detail_data:
        raceInfo['age'] = '3+'
    elif '3歳' in detail_data:
        raceInfo['age'] = '3'
    elif '4歳以上' in detail_data:
        raceInfo['age'] = '4+'
    else:
        raceInfo['age'] = '9'
    if '新馬' in detail_data:
        raceInfo['class'] = '9'
    elif '未勝利' in detail_data:
        raceInfo['class'] = '0'
    elif '500万下' in detail_data:
        raceInfo['class'] = '1'
    elif '1000万下' in detail_data:
        raceInfo['class'] = '2'
    elif '1600万下' in detail_data:
        raceInfo['class'] = '3'
    elif 'オープン' in detail_data:
        raceInfo['class'] = '4'
    else:
        raceInfo['class'] = '9'
    if '馬齢' in detail_data:
        raceInfo['loaf'] = '0'
    elif '定量' in detail_data:
        raceInfo['loaf'] = '1'
    elif '別定' in detail_data:
        raceInfo['loaf'] = '2'
    elif 'ハンデ' in detail_data:
        raceInfo['loaf'] = '3'
    if '混' in detail_data:
        raceInfo['sex'] = '0'
    elif '牡' in detail_data:
        raceInfo['sex'] = '1'
    elif '牝' in detail_data:
        raceInfo['sex'] = '2'

    if '障害' in detail_data:
        raceInfo['jump_flg']='1'

    rank=netkeiba_soup.select('a[href^="/horse/"]')
    raceInfo['number']=str(len(rank))

    return netkeiba_soup, raceInfo


def horseList(netkeiba_soup,raceInfo,out):


    columnList=['rank','gate','horseName','horse_code','sex','age','loaf','jockey','jockey_code','jockey_handicap','additional_handicap',
            'weight','weightDiff','time','diff','popularity','odds','last','last_rank','corner','trainer','trainer_code','belongs',
            'owner','owner_code','comment','prize','tansho','fukusho']
    for key in columnList:
        if key == 'fukusho':
            out.write(key+'\n')
        else:
            out.write(key+',')

    payout=netkeiba_soup.select_one('.pay_table_01')
    payout=re.sub(r',','',str(payout))
    payout=re.sub(r'<br/>','/',str(payout))
    payout=BeautifulSoup(payout,'lxml')
    payout=payout.select('.txt_r')
    tansho = payout[0].text
    fukusho = payout[2].text.split('/')

    horseInfoList=netkeiba_soup.select_one('.race_table_01')
    horseInfoList=re.sub(r',','',str(horseInfoList))
    horseInfoList=re.sub(r'</tr>',',',str(horseInfoList))
    horseInfoList = horseInfoList.split(',')

    i=0
    winner_time=0
    for horseInfo in horseInfoList:

        horseInfoDict={}
        if i != 0 and i <= int(raceInfo['number']):
            horseInfo=BeautifulSoup(horseInfo,'lxml')
            txt_r=horseInfo.select('.txt_r')
            txt_r_list=[]
            for txt_r_item in txt_r:
                txt_r_list.append(txt_r_item.text)
            horseInfoDict['rank']=txt_r_list[0]
            horseInfoDict['gate']=txt_r_list[1]
            if txt_r_list[2] != '':
                time=txt_r_list[2].split(':')
                horseInfoDict['time']=str(float(time[0])*60+float(time[1]))
                if i == 1:
                    winner_time=float(horseInfoDict['time'])
                horseInfoDict['diff']=str(round(float(horseInfoDict['time']) - winner_time,1))
            else:
                horseInfoDict['time']='-'
                horseInfoDict['diff']='-'
            horseInfoDict['odds']=txt_r_list[3]
            horseInfoDict['prize']=txt_r_list[4]
            if horseInfoDict['prize'] == '':
                horseInfoDict['prize']='0'

            horse=horseInfo.select_one('a[href^="/horse/"]')
            horseInfoDict['horseName']=horse.text
            horse_code=horse.attrs['href']
            horseInfoDict['horse_code']=horse_code.split('/')[2]

            txt_c=horseInfo.select('.txt_c')
            txt_c_list=[]
            for txt_c_item in txt_c:
                txt_c_list.append(txt_c_item.text)
            sex=txt_c_list[0][0]
            horseInfoDict['sex']=conversion.sex_flg(sex)
            horseInfoDict['age']=txt_c_list[0][1:]
            horseInfoDict['loaf']=txt_c_list[1]

            jockey=horseInfo.select_one('a[href^="/jockey/"]')
            horseInfoDict['jockey']=jockey.text
            jockey_code=jockey.attrs['href']
            horseInfoDict['jockey_code']=jockey_code.split('/')[2]
            horseInfoDict['jockey_handicap']='-'
            horseInfoDict['additional_handicap']='-'

            r1ml=horseInfo.select('.r1ml')
            r2ml=horseInfo.select('.r2ml')
            r3ml=horseInfo.select('.r3ml')
            bml=horseInfo.select('.bml')
            if len(r1ml)>0:
                for ml_item in r1ml:
                    if len(ml_item.text) == 4:
                        horseInfoDict['last']=ml_item.text
                        horseInfoDict['last_rank']='1'
                    elif len(ml_item.text) < 3:
                        horseInfoDict['popularity']=ml_item.text
            if len(r2ml)>0:
                for ml_item in r2ml:
                    if len(ml_item.text) == 4:
                        horseInfoDict['last']=ml_item.text
                        horseInfoDict['last_rank']='2'
                    elif len(ml_item.text) < 3:
                        horseInfoDict['popularity']=ml_item.text
            if len(r3ml)>0:
                for ml_item in r3ml:
                    if len(ml_item.text) == 4:
                        horseInfoDict['last']=ml_item.text
                        horseInfoDict['last_rank']='3'
                    elif  len(ml_item.text) < 3:
                        horseInfoDict['popularity']=ml_item.text
            if len(bml)>0:
                for ml_item in bml:
                    if len(ml_item.text) == 4:
                        horseInfoDict['last']=ml_item.text
                        horseInfoDict['last_rank']='-'
                    elif len(ml_item.text) < 3 and ml_item.text != '\n':
                        horseInfoDict['popularity']=ml_item.text
            if 'last' not in horseInfoDict or 'last_rank' not in horseInfoDict:
                horseInfoDict['last']='-'
                horseInfoDict['last_rank']='-'

            td=horseInfo.select('td')
            td_list=[]
            for td_item in td:
                if '-' in td_item.text or '(' in td_item.text:
                    td_list.append(td_item.text.translate(str.maketrans({'(':',',')':','})))
            if len(td_list) == 2:
                horseInfoDict['corner']=td_list[0]
                horseInfoDict['weight']=td_list[1].split(',')[0]
                horseInfoDict['weightDiff']=td_list[1].split(',')[1]
            else:
                horseInfoDict['corner']='-'
                horseInfoDict['weight']='-'
                horseInfoDict['weightDiff']='-'

            trainer=horseInfo.select_one('a[href^="/trainer/"]')
            horseInfoDict['trainer']=trainer.text
            trainer_code=trainer.attrs['href']
            horseInfoDict['trainer_code']=trainer_code.split('/')[2]

            txt_l=horseInfo.select('.txt_l')
            horseInfoDict['belongs']=conversion.belongs_flg(txt_l[2].text)

            owner=horseInfo.select_one('a[href^="/owner/"]')
            horseInfoDict['owner']=owner.text
            owner_code=owner.attrs['href']
            horseInfoDict['owner_code']=owner_code.split('/')[2]

            horseInfoDict['comment']='0'
            for txt_c_item in txt_c:
                if txt_c_item.a != None and 'data-theme' in txt_c_item.a.attrs and txt_c_item.a.attrs['data-theme'] == '07004':
                    horseInfoDict['comment']='1'

            if horseInfoDict['rank'] == '1':
                horseInfoDict['tansho']=tansho
            else:
                horseInfoDict['tansho']='0'

            if horseInfoDict['rank'] == '1':
                horseInfoDict['fukusho']=fukusho[0]
            elif horseInfoDict['rank'] == '2' and len(fukusho)>1:
                horseInfoDict['fukusho']=fukusho[1]
            elif horseInfoDict['rank'] == '3' and len(fukusho)>2:
                horseInfoDict['fukusho']=fukusho[2]
            else:
                horseInfoDict['fukusho']='0'

            for key in columnList:
                if key == 'fukusho':
                    out.write(horseInfoDict[key]+'\n')
                else:
                    out.write(horseInfoDict[key]+',')

        i+=1


def makeFiles(courseNum,year,raceDate,raceNo):

    raceID={'year':str(year),'date':raceDate,'courseNum':courseNum,'No':raceNo}
    netkeiba_soup, raceInfo = basicInfo(raceID)

    if raceInfo != '' and raceInfo['jump_flg'] == '0':

        fileName = raceInfo['year']+raceInfo['courseNum']+raceInfo['holding']+raceInfo['No']+'_'
        fileName += raceInfo['road']+'_'
        fileName += raceInfo['distance']+'_'
        fileName += raceInfo['outFlg']+'_'
        fileName += raceInfo['condition']+'_'
        fileName += raceInfo['age']+'_'
        fileName += raceInfo['class']+'_'
        fileName += raceInfo['sex']+'_'
        fileName += raceInfo['loaf']+'_'
        fileName += raceInfo['number']+'_'
        fileName += raceInfo['weather']+'_'
        fileName += raceInfo['date']

        path = 'race_database/'+raceInfo['courseNum']+'/'+raceInfo['year']+'/'+raceInfo['holding']+'/'
        os.makedirs(path, exist_ok=True)
        out=codecs.open(path+fileName+'.csv','w','utf-8')
        horseList(netkeiba_soup,raceInfo,out)
        out.close()

        time.sleep(2)


def weekly(year,holdings):

    for courseNum in holdings:
        for i in range(12):
            raceNo=str('{0:02d}'.format(i+1))
            makeFiles(courseNum,year,holdings[courseNum],raceNo)


if __name__ == '__main__':

    # '01':'札幌','02':'函館','03':'福島','04':'新潟','05':'東京','06':'中山','07':'中京','08':'京都','09':'阪神','10':'小倉'
    courseNum='04'

    for year in range(2020,2021):
        for k in range(1,2): # holding_times
            for j in range(4,6): # holding_day
                raceDate=str('{0:02d}'.format(k+1))+str('{0:02d}'.format(j+1))
                for i in range(12): # raceNo
                    raceNo=str('{0:02d}'.format(i+1))
                    makeFiles(courseNum,year,raceDate,raceNo)
