# -*- coding: utf-8 -*-

import sys
import re
import os
import time
import yaml
from datetime import datetime
import pandas as pd
import csv
import webbrowser

# self made
import cleansing
import basicInfo
import horseDB
import odds
import pycolor
import manage_mysql
import conversion


def target(holding,race_from,race_to,odds_flg,range_flg,condition_flg):

    con = manage_mysql.connect()
    c = con.cursor()
    columns=['horseName','horse_code','sex','horse_age','trainer_code','trainer_belongs','sire_code','bms_code','0_jockey','tansho','fukusho_lower','fukusho_upper',
            '0_course','0_holding','0_month','0_winClass','0_loafCondition','0_handicap','0_roadbed','0_distance','0_roadCondition','0_gate','0_rotation_epoch','0_rotation_roadbed','0_rotation_distance',
            '1_course','1_winClass','1_roadbed','1_distance','1_roadCondition','1_gate','1_rotation_epoch','1_rotation_roadbed','1_rotation_distance','1_raceCode',
            '2_course','2_winClass','2_roadbed','2_distance','2_roadCondition','2_gate','2_rotation_epoch','2_rotation_roadbed','2_rotation_distance','2_raceCode',
            '3_course','3_winClass','3_roadbed','3_distance','3_roadCondition','3_gate','3_rotation_epoch','3_rotation_roadbed','3_rotation_distance','3_raceCode',
            '4_course','4_winClass','4_roadbed','4_distance','4_roadCondition','4_gate','4_rotation_epoch','4_rotation_roadbed','4_rotation_distance','4_raceCode',
            '5_course','5_winClass','5_roadbed','5_distance','5_roadCondition','5_gate','5_raceCode']

    columnText=''
    for column in columns:
        if column == 'horseName':
            columnText+=column+' varchar(16),'
        elif column == 'horse_code' or column == 'sire_code' or column == 'bms_code':
            columnText+=column+' int,'
        elif 'raceCode' in column:
            columnText+=column+' char(12),'
        else:
            columnText+=column+' float,'
    columnText=columnText[:-1]
    c.execute('drop table target')
    c.execute('create table target ('+columnText+')')
    con.commit()
    con.close()

    for key in holding:

        courseNum=key

        for i in range(race_from,race_to):
            time.sleep(2)
            raceNo=str('{0:02d}'.format(i))

            raceID={'date':holding[key],'courseName':key,'courseNum':courseNum,'No':raceNo}
            netkeiba_soup, raceInfo = basicInfo.basicInfo(raceID,'shutuba',condition_switch)

            if raceInfo['road'] != '障':
                print(key, holding[key], raceNo)
                get_raceInfo(netkeiba_soup, raceInfo, holding[key], raceNo, odds_flg, range_flg)
                print()


def horseList(netkeiba_soup, raceInfo, key, raceNo, flg):

    year=raceInfo['date'].split('.')
    year=int(year[0])

    tansho_odds,fukusho_lower_odds,fukusho_upper_odds=[],[],[]
    if flg == '1':
        oddsList = odds.odds(year,raceInfo['courseNum'],key,raceNo)
        for i in range(int(raceInfo['number'])*2):
            if i < int(raceInfo['number']):
                if oddsList[i] == '---.-':
                    tansho_odds.append('999.9')
                else:
                    tansho_odds.append(oddsList[i])
            else:
                if oddsList[i] == '999.9':
                    fukusho_lower_odds.append('999.9')
                    fukusho_upper_odds.append('999.9')
                else:
                    odds_tmp= oddsList[i]
                    odds_tmp=odds_tmp.split('-')
                    odds_lower_tmp=odds_tmp[0].replace('\n','')
                    odds_upper_tmp=odds_tmp[1].replace('\n','')
                    fukusho_lower_odds.append(odds_lower_tmp)
                    fukusho_upper_odds.append(odds_upper_tmp)
    else:
        for i in range(int(raceInfo['number'])*2):
            if i < int(raceInfo['number']):
                tansho_odds.append('999.9')
            else:
                fukusho_lower_odds.append('999.9')
                fukusho_upper_odds.append('999.9')

    horseInfoList=netkeiba_soup.select('.HorseList')
    i=0
    horses=[]
    for horseInfo in horseInfoList:
        if i<int(raceInfo['number']):

            horseInfoDict={}

            horseInfoDict['gate']=i+1
            horseInfoDict['tansho_odds']=tansho_odds[i]
            horseInfoDict['fukusho_lower_odds']=fukusho_lower_odds[i]
            horseInfoDict['fukusho_upper_odds']=fukusho_upper_odds[i]

            horse_basic_info=horseInfo.select_one('.Horse02')
            horseName=horse_basic_info.text
            horseName=horseName.translate(str.maketrans({'\n':'',' ':''}))
            horse_basic_info=horse_basic_info.select_one('a')
            horse_code=horse_basic_info.attrs['href'].split('/')[4]
            horse_code=horse_code.translate(str.maketrans({'\n':'',' ':''}))
            if 'B' in horseName:
                horseName=horseName[:-1]
                blinker=True
            else:
                blinker=False
            horseInfoDict['blinker']=blinker
            trainer_basic_info=horseInfo.select_one('.Horse05')
            trainer_info=trainer_basic_info.text
            horseInfoDict['trainer_belongs']=conversion.belongs_flg(trainer_info)
            classJockey=horseInfo.select_one('.Jockey')
            classJockey_text=classJockey.text
            classJockey_text=classJockey_text.split('\n')
            jockeyCode=classJockey.a.attrs['href']
            jockeyCode=jockeyCode.split('/')
            jockeyCode=jockeyCode[4]
            age=classJockey_text[1]
            age=int(re.sub('\\D','',age))
            birth=year-age
            search=['name',horseName,'birth',birth]
            horseDBInfo=horseDB.horseDB('horseInfo',search)

            if horseDBInfo is not None:
                horseInfoDict['horseName']=horseDBInfo['name'].values[0]
                horseInfoDict['sex']=horseDBInfo['sex'].values[0]
                horseInfoDict['birth']=horseDBInfo['birth'].values[0]
                horseInfoDict['sire_code']=horseDBInfo['sire_code'].values[0]
                horseInfoDict['bms_code']=horseDBInfo['bms_code'].values[0]
                horseInfoDict['trainer_code']=horseDBInfo['trainer_code'].values[0]
                horseInfoDict['owner_code']=horseDBInfo['owner_code'].values[0]
                horseInfoDict['producer_code']=horseDBInfo['producer_code'].values[0]
                horseInfoDict['horse_code']=horse_code
                horseInfoDict['jockey']=classJockey_text[3]
                horseInfoDict['jockey_code']=jockeyCode
                horseInfoDict['loaf']=classJockey_text[4]

                pastList=horseInfo.select('.Past')

                if len(pastList) == 0:
                    horseInfoDict['debut']=1
                    horses.append(horseInfoDict)
                else:
                    horseInfoDict['debut']=0

                    j=0
                    for past in range(len(pastList)):
                        before=[]
                        beforeDict={}
                        beforeList=pastList[past]
                        data01=beforeList.select_one('.Data01')
                        data01=cleansing.cleansing02(data01)
                        data01=data01.split(',')
                        before += data01[1:4]
                        data02=beforeList.select_one('.Data02')
                        data02=cleansing.cleansing02(data02)
                        data02=data02.split(',')
                        if len(data01)>=17:
                            before += [data02[1],data01[16]]
                        else:
                            before += [data02[1],'']
                        data05=beforeList.select_one('.Data05')
                        data05=cleansing.cleansing02(data05)
                        data05=data05.split(',')
                        before += data05
                        data03=beforeList.select_one('.Data03')
                        data03=cleansing.cleansing02(data03)
                        data03=data03.split(',')
                        before += data03
                        data06=beforeList.select_one('.Data06')
                        data06=cleansing.cleansing02(data06)
                        data06=data06.split(',')
                        if len(data06)<3:
                            data06.insert(0,'')
                        before += data06
                        data07=beforeList.select_one('.Data07')
                        data07=cleansing.cleansing02(data07)
                        data07=data07.split(',')
                        before += data07
                        raceCode=beforeList.select_one('.Data02')
                        raceCode=raceCode.select_one('a')
                        raceCode=raceCode.attrs['href'].split('/')[4]
                        before.append(raceCode)

                        if before[2] != '取' and before[2] != '除' and before[2] != '中' and '障害' not in before[3]:
                            beforeDict['date']=before[0]
                            beforeDict['course']=before[1]
                            beforeDict['rank']=before[2]
                            beforeDict['name']=before[3]
                            beforeDict['class']=before[4]
                            beforeDict['detail']=before[5]
                            beforeDict['time']=before[6]
                            beforeDict['condition']=before[7]
                            beforeDict['number']=before[8]
                            beforeDict['position']=before[9]
                            beforeDict['popularity']=before[10]
                            beforeDict['jockey']=before[11]
                            beforeDict['loaf']=before[12]
                            beforeDict['way']=before[13]
                            beforeDict['last']=before[14]
                            beforeDict['weight']=before[15]
                            beforeDict['winner']=before[16]
                            beforeDict['raceCode']=before[17]
                            horseInfoDict['before'+str(j+1)]=beforeDict
                            j+=1
                    horses.append(horseInfoDict)
            i+=1
    return year,horses


def get_raceInfo(netkeiba_soup, raceInfo, key, raceNo, odds_flg, range_flg):
    print(raceInfo)
    road=conversion.roadbed_to_english(raceInfo['road'])
    course_features_key=raceInfo['course']+'_'+road+'_'+raceInfo['distance']
    if (raceInfo['course'] == '04' and raceInfo['distance'] == '2000') or (raceInfo['course'] == '08' and raceInfo['distance'] in ['1400','1600']):
        if raceInfo['outFlg'] == '0':
            course_features_key += '_in'
        elif raceInfo['outFlg'] == '1':
            course_features_key += '_out'

    f = open('./yml/course_features.yml', 'r')
    course_features = yaml.load(stream=f, Loader=yaml.SafeLoader)

    if not course_features[course_features_key]['target'] and range_flg == '1':
        print()
        print('!!!OUT OF SCOPE!!!')
        print()
        sys.exit()

    con = manage_mysql.connect()
    c = con.cursor()

    year,horses=horseList(netkeiba_soup, raceInfo, key, raceNo, odds_flg)

    fukushoDic={}
    course = raceInfo['courseNum']
    holding = key[2:4]
    roadbed = conversion.roadbed_flg(raceInfo['road'])
    distance = re.sub('\\D','',raceInfo['distance'])
    roadCondition = conversion.condition_flg(raceInfo['condition'])
    win_class=conversion.winClass_flg(raceInfo['class'])
    loafCondition=conversion.loafCondition_flg(raceInfo['loaf'])

    for horse in horses:

        dataset={}
        columns=['horseName','horse_code','sex','horse_age','trainer_code','trainer_belongs','sire_code','bms_code','0_jockey','tansho','fukusho_lower','fukusho_upper',
            '0_course','0_holding','0_month','0_winClass','0_loafCondition','0_handicap','0_roadbed','0_distance','0_roadCondition','0_gate','0_rotation_epoch','0_rotation_roadbed','0_rotation_distance',
            '1_course','1_winClass','1_roadbed','1_distance','1_roadCondition','1_gate','1_rotation_epoch','1_rotation_roadbed','1_rotation_distance','1_raceCode',
            '2_course','2_winClass','2_roadbed','2_distance','2_roadCondition','2_gate','2_rotation_epoch','2_rotation_roadbed','2_rotation_distance','2_raceCode',
            '3_course','3_winClass','3_roadbed','3_distance','3_roadCondition','3_gate','3_rotation_epoch','3_rotation_roadbed','3_rotation_distance','3_raceCode',
            '4_course','4_winClass','4_roadbed','4_distance','4_roadCondition','4_gate','4_rotation_epoch','4_rotation_roadbed','4_rotation_distance','4_raceCode',
            '5_course','5_winClass','5_roadbed','5_distance','5_roadCondition','5_gate','5_raceCode']

        for column in range(len(columns)):
            dataset[columns[column]]='null'

        dataset['0_course'] = course
        dataset['0_holding'] = holding
        dataset['0_roadbed'] = roadbed
        dataset['0_distance'] = distance
        dataset['0_roadCondition'] = roadCondition
        dataset['0_winClass']=win_class
        dataset['0_loafCondition']=loafCondition

        dataset['horseName'] = horse['horseName']
        dataset['horse_code'] = horse['horse_code']
        dataset['0_gate'] = horse['gate']
        dataset['trainer_code'] = horse['trainer_code']
        dataset['trainer_belongs'] = horse['trainer_belongs']
        dataset['sire_code'] = horse['sire_code']
        dataset['bms_code'] = horse['bms_code']
        dataset['sex']=conversion.sex_flg(horse['sex'])
        dataset['0_jockey'] = horse['jockey_code']
        dataset['horse_age'] = year-int(horse['birth'])

        dataset['0_month']=raceInfo['date']
        dataset['0_month']=dataset['0_month'].split(".")
        dataset['0_month']=int(dataset['0_month'][1])

        original_loaf=57
        if dataset['sex'] == '牝':
            original_loaf-=3
            if dataset['horse_age'] > 3 or (dataset['horse_age'] == 3 and month >= 10):
                original_loaf+=1
        else:
            if dataset['horse_age'] == 3 and dataset['0_month'] < 10:
                    original_loaf-=1
            elif dataset['horse_age'] == 2 and dataset['0_month'] >= 10:
                    original_loaf-=2
            elif dataset['horse_age'] == 2 and dataset['0_month'] < 10:
                    original_loaf-=3
        dataset['0_handicap'] = float(horse['loaf'])-original_loaf

        if horse['debut'] == 1:
            dataset['0_rotation_epoch']=0
            dataset['0_rotation_roadbed']=0
            dataset['0_rotation_distance']=0
        else:
            time_0=raceInfo['date']
            time_0=time_0.split(".")
            time_0=datetime(int(time_0[0]),int(time_0[1]),int(time_0[2]),0,0).strftime('%s')
            dataset['0_distance']=int(re.sub('\\D','',raceInfo['distance']))

            dataset['tansho'] = horse['tansho_odds']
            dataset['fukusho_lower'] = horse['fukusho_lower_odds']
            dataset['fukusho_upper'] = horse['fukusho_upper_odds']

            if 'before1' in horse:
                before1=horse['before1']
                dataset['1_course']=conversion.course_flg(before1['course'])
                dataset['1_gate']=int(re.sub('\\D','',before1['position']))
                dataset['1_roadCondition'] = conversion.condition_flg(before1['condition'])
                dataset['1_winClass']=0
                time_1=before1['date']
                time_1=time_1.split(".")
                time_1=datetime(int(time_1[0]),int(time_1[1]),int(time_1[2]),0,0).strftime('%s')
                dataset['0_rotation_epoch'] = int(time_0)-int(time_1)
                dataset['1_roadbed']=conversion.roadbed_flg(before1['detail'][0])
                if dataset['1_roadbed'] == dataset['0_roadbed']:
                    dataset['0_rotation_roadbed'] = 0
                else:
                    dataset['0_rotation_roadbed'] = 1
                dataset['1_distance']=before1['detail'][1:]
                dataset['1_distance']=int(re.sub('\\D','',dataset['1_distance']))
                dataset['0_rotation_distance'] = dataset['0_distance']-dataset['1_distance']
                dataset['1_raceCode']=before1['raceCode']
            if 'before2' in horse:
                before2=horse['before2']
                dataset['2_course']=conversion.course_flg(before2['course'])
                dataset['2_gate']=int(re.sub('\\D','',before2['position']))
                dataset['2_roadCondition'] = conversion.condition_flg(before2['condition'])
                dataset['2_winClass']=0
                time_2=before2['date']
                time_2=time_2.split(".")
                time_2=datetime(int(time_2[0]),int(time_2[1]),int(time_2[2]),0,0).strftime('%s')
                dataset['1_rotation_epoch'] = int(time_1)-int(time_2)
                dataset['2_roadbed']=conversion.roadbed_flg(before2['detail'][0])
                if dataset['2_roadbed'] == dataset['1_roadbed']:
                    dataset['1_rotation_roadbed'] = 0
                else:
                    dataset['1_rotation_roadbed'] = 1
                dataset['2_distance']=before2['detail'][1:]
                dataset['2_distance']=int(re.sub('\\D','',dataset['2_distance']))
                dataset['1_rotation_distance'] = dataset['1_distance']-dataset['2_distance']
                dataset['2_raceCode']=before2['raceCode']
            if 'before3' in horse:
                before3=horse['before3']
                dataset['3_course']=conversion.course_flg(before3['course'])
                dataset['3_gate']=int(re.sub('\\D','',before3['position']))
                dataset['3_roadCondition'] = conversion.condition_flg(before3['condition'])
                dataset['3_winClass']=0
                time_3=before3['date']
                time_3=time_3.split(".")
                time_3=datetime(int(time_3[0]),int(time_3[1]),int(time_3[2]),0,0).strftime('%s')
                dataset['2_rotation_epoch'] = int(time_2)-int(time_3)
                dataset['3_roadbed']=conversion.roadbed_flg(before3['detail'][0])
                if dataset['3_roadbed'] == dataset['2_roadbed']:
                    dataset['2_rotation_roadbed'] = 0
                else:
                    dataset['2_rotation_roadbed'] = 1
                dataset['3_distance']=before3['detail'][1:]
                dataset['3_distance']=int(re.sub('\\D','',dataset['3_distance']))
                dataset['2_rotation_distance'] = dataset['2_distance']-dataset['3_distance']
                dataset['3_raceCode']=before3['raceCode']
            if 'before4' in horse:
                before4=horse['before4']
                dataset['4_course']=conversion.course_flg(before4['course'])
                dataset['4_gate']=int(re.sub('\\D','',before4['position']))
                dataset['4_roadCondition'] = conversion.condition_flg(before4['condition'])
                dataset['4_winClass']=0
                time_4=before4['date']
                time_4=time_4.split(".")
                time_4=datetime(int(time_4[0]),int(time_4[1]),int(time_4[2]),0,0).strftime('%s')
                dataset['3_rotation_epoch'] = int(time_3)-int(time_4)
                dataset['4_roadbed']=conversion.roadbed_flg(before4['detail'][0])
                if dataset['4_roadbed'] == dataset['3_roadbed']:
                    dataset['3_rotation_roadbed'] = 0
                else:
                    dataset['3_rotation_roadbed'] = 1
                dataset['4_distance']=before4['detail'][1:]
                dataset['4_distance']=int(re.sub('\\D','',dataset['4_distance']))
                dataset['3_rotation_distance'] = dataset['3_distance']-dataset['4_distance']
                dataset['4_raceCode']=before4['raceCode']
            if 'before5' in horse:
                before5=horse['before5']
                dataset['5_course']=conversion.course_flg(before5['course'])
                dataset['5_gate']=int(re.sub('\\D','',before5['position']))
                dataset['5_roadCondition'] = conversion.condition_flg(before5['condition'])
                dataset['5_winClass']=0
                time_5=before5['date']
                time_5=time_5.split(".")
                time_5=datetime(int(time_5[0]),int(time_5[1]),int(time_5[2]),0,0).strftime('%s')
                dataset['4_rotation_epoch'] = int(time_4)-int(time_5)
                dataset['5_roadbed']=conversion.roadbed_flg(before5['detail'][0])
                if dataset['5_roadbed'] == dataset['4_roadbed']:
                    dataset['4_rotation_roadbed'] = 0
                else:
                    dataset['4_rotation_roadbed'] = 1
                dataset['5_distance']=before5['detail'][1:]
                dataset['5_distance']=int(re.sub('\\D','',dataset['5_distance']))
                dataset['4_rotation_distance'] = dataset['4_distance']-dataset['5_distance']
                dataset['5_raceCode']=before5['raceCode']

        key_text=''
        value_text=''
        i=0
        for key in dataset:
            key_text+=key+','
            if i == 0:
                value_text+='"'+dataset[key]+'",'
            else:
                value_text+=str(dataset[key])+','
            i+=1

        key_text=key_text[:-1]
        value_text=value_text[:-1]
        c.execute('insert into target ('+key_text+') values ('+value_text+')')

    con.commit()
    con.close()


def fukusho_pred():

    con = manage_mysql.connect()
    sql_race='select * from target;'
    df_race = pd.read_sql(sql_race,con)
    sql_gate='select * from fukushoGate;'
    df_gate = pd.read_sql(sql_gate,con)
    sql_belongs='select * from fukushoBelongs;'
    df_belongs = pd.read_sql(sql_belongs,con)
    sql_sire='select * from fukushoSire;'
    df_sire = pd.read_sql(sql_sire,con)
    sql_bms='select * from fukushoBms;'
    df_bms = pd.read_sql(sql_bms,con)
    con.close()

    for i in range(len(df_race)):

        upper=90
        lower=60
        ratio_upper=130
        ratio_lower=80

        comment={
                'position':'null','name':'null','belongs':'null',
                'sire_name':'null','sire_general':'null','sire_sex':'null','sire_age':'null','bms_name':'null','bms_general':'null',
                '0_gate':'null','1_gate':'null','2_gate':'null','3_gate':'null','4_gate':'null',
                '0_sire_class':'null','0_sire_track':'null','0_sire_roadCondition':'null','0_sire_distance':'null',
                '0_sire_rotation_epoch':'null','0_sire_rotation_roadbed':'null','0_sire_rotation_distance':'null',
                '0_bms_class':'null','0_bms_track':'null','0_bms_roadCondition':'null','0_bms_distance':'null',
                '0_bms_rotation_epoch':'null','0_bms_rotation_roadbed':'null','0_bms_rotation_distance':'null',
                '1_sire_class':'null','1_sire_track':'null','1_sire_roadCondition':'null','1_sire_distance':'null',
                '1_sire_rotation_epoch':'null','1_sire_rotation_roadbed':'null','1_sire_rotation_distance':'null',
                '1_bms_class':'null','1_bms_track':'null','1_bms_roadCondition':'null','1_bms_distance':'null',
                '1_bms_rotation_epoch':'null','1_bms_rotation_roadbed':'null','1_bms_rotation_distance':'null',
                '2_sire_class':'null','2_sire_track':'null','2_sire_roadCondition':'null','2_sire_distance':'null',
                '2_sire_rotation_epoch':'null','2_sire_rotation_roadbed':'null','2_sire_rotation_distance':'null',
                '2_bms_class':'null','2_bms_track':'null','2_bms_roadCondition':'null','2_bms_distance':'null',
                '2_bms_rotation_epoch':'null','2_bms_rotation_roadbed':'null','2_bms_rotation_distance':'null',
                '3_sire_class':'null','3_sire_track':'null','3_sire_roadCondition':'null','3_sire_distance':'null',
                '3_sire_rotation_epoch':'null','3_sire_rotation_roadbed':'null','3_sire_rotation_distance':'null',
                '3_bms_class':'null','3_bms_track':'null','3_bms_roadCondition':'null','3_bms_distance':'null',
                '3_bms_rotation_epoch':'null','3_bms_rotation_roadbed':'null','3_bms_rotation_distance':'null',
                '4_sire_class':'null','4_sire_track':'null','4_sire_roadCondition':'null','4_sire_distance':'null',
                '4_sire_rotation_epoch':'null','4_sire_rotation_roadbed':'null','4_sire_rotation_distance':'null',
                '4_bms_class':'null','4_bms_track':'null','4_bms_roadCondition':'null','4_bms_distance':'null',
                '4_bms_rotation_epoch':'null','4_bms_rotation_roadbed':'null','4_bms_rotation_distance':'null'
                }

        dataset=df_race.iloc[i]
        dataset=dataset.fillna('null')

        sire = df_sire[df_sire['code'].astype(int) == dataset['sire_code']]
        bms = df_bms[df_bms['code'].astype(int) == dataset['bms_code']]
        comment['position']=int(dataset['0_gate'])

        belongs = df_belongs[df_belongs['belongs'].astype(int) == dataset['trainer_belongs'].astype(int)]
        distanceKey = conversion.distance_key(int(dataset['0_distance']))

        course=str('{0:02d}'.format(int(dataset['0_course'])))
        if dataset['0_roadbed'] == 0:
            roadbed='turf'
        elif dataset['0_roadbed'] == 1:
            roadbed='dirt'
        trackKey = 'track_'+course+'_'+roadbed

        comment['name']=dataset['horseName']
        if len(sire['name']) > 0:
            comment['sire_name']=sire['name'].values[0]
            comment['sire_general']=sire['general_limit'].values[0]
            if dataset['sex'] == 0:
                sexKey='sex_male'
            elif dataset['sex'] == 1:
                sexKey='sex_female'
            elif dataset['sex'] == 2:
                sexKey='sex_gelding'
            if dataset['horse_age'] >= 7:
                ageKey='age_7over'
            else:
                ageKey='age_'+str(int(dataset['horse_age']))
            comment['sire_sex']=sire[sexKey].values[0]
            comment['sire_age']=sire[ageKey].values[0]
        else:
            comment['sire_name']='-'
            comment['sire_general']='-'
        if len(bms['name']) > 0:
            comment['bms_name']=bms['name'].values[0]
            comment['bms_general']=bms['general_limit'].values[0]
        else:
            comment['bms_name']='-'
            comment['bms_general']='-'

        for past in range(5):

            prev=str(past+1)+'_'
            past=str(past)+'_'
            if dataset[past+'course'] != 'null':
                course=str('{0:02d}'.format(int(dataset[past+'course'])))
            if dataset[past+'roadbed'] == 0:
                roadbed='turf'
            elif dataset[past+'roadbed'] == 1:
                roadbed='dirt'
            if dataset[past+'distance'] != 'null':
                distance=str(int(dataset[past+'distance']))
                gate_target = df_gate[(df_gate['course'] == course) & (df_gate['roadbed'] == roadbed) & (df_gate['distance'] == distance)]
                if dataset[past+'gate'] != 'null':
                    gate_column='gate_'+str('{0:02d}'.format(int(dataset[past+'gate'])))
                    if len(gate_target) != 0 and gate_target[gate_column].values[0] != 'null':
                        comment[past+'gate'] = gate_target[gate_column].values[0]

            distanceKey = conversion.distance_key(int(distance))
            if dataset[past+'roadCondition'] != 'null':
                if int(dataset[past+'roadCondition']) == 0:
                    roadConditionKey = 'road_'+roadbed+'_good'
                else:
                    roadConditionKey = 'road_'+roadbed+'_bad'
            if roadbed == 'turf' and (course == '04' or course == '08'): # とりあえず
                trackKey = 'track_'+course+'_'+roadbed+'_in'
            else:
                trackKey = 'track_'+course+'_'+roadbed
            if dataset[past+'rotation_epoch'] != 'null':
                if dataset[past+'rotation_epoch'] > 60*60*24*7*8: # 8週間以上を休み明けと定義
                    rotationEpochKey = 'rotation_epoch_long'
                elif dataset[past+'rotation_epoch'] == 0:
                    rotationEpochKey = 'null'
                else:
                    rotationEpochKey = 'rotation_epoch_short'

            rotationDistanceKey = 'null'
            if dataset[prev+'distance'] != 'null':
                distance_prev = dataset[prev+'distance']
                if int(distance)/distance_prev > 1.1:
                    rotationDistanceKey = 'rotation_distance_extension'
                elif int(distance)/distance_prev < 0.9:
                    rotationDistanceKey = 'rotation_distance_shortening'

            if dataset[past+'rotation_roadbed'] != 'null':
                if dataset[past+'rotation_roadbed'] == 1:
                    if roadbed == 'turf':
                        rotationRoadbedKey = 'rotation_roadbed_toTurf'
                    elif roadbed == 'dirt':
                        rotationRoadbedKey = 'rotation_roadbed_toDirt'
                else:
                    rotationRoadbedKey = 'null'

            if dataset[past+'winClass'] != 'null':
                class_key='grade_'+str(int(dataset[past+'winClass']))

            for target in ['sire_','bms_']:
                if target == 'sire_':
                    target_data = sire
                else:
                    target_data = bms

                if len(target) != 0:
                    if course != '99' and len(target_data[trackKey].values) > 0:
                        comment[past+target+'track'] = target_data[trackKey].values[0]
                    if len(target_data[roadConditionKey].values) > 0:
                        comment[past+target+'roadCondition'] = target_data[roadConditionKey].values[0]
                    if len(target_data[distanceKey].values) > 0:
                        comment[past+target+'distance'] = target_data[distanceKey].values[0]
                    if rotationEpochKey != 'null' and len(target_data[rotationEpochKey].values) > 0:
                        comment[past+target+'rotation_epoch'] = target_data[rotationEpochKey].values[0]
                    if len(target_data[class_key].values) > 0:
                        comment[past+target+'class'] = target_data[class_key].values[0]
                    if rotationRoadbedKey != 'null' and len(target_data[rotationRoadbedKey].values) > 0:
                        comment[past+target+'rotation_roadbed'] = target_data[rotationRoadbedKey].values[0]
                    if rotationDistanceKey != 'null' and len(target_data[rotationDistanceKey].values) > 0:
                        comment[past+target+'rotation_distance'] = target_data[rotationDistanceKey].values[0]

        comment_flg=0
        last_flg=0
        last_sum=0
        last_count=0
        corner_flg=0
        corner_sum=0
        corner_count=0
        for past in range(1,5):
            raceCode=dataset[str(past)+'_raceCode']
            if raceCode != 'null':
                last_count+=1
                corner_count+=1
                path = 'races/'+raceCode[4:6]+'/'+raceCode[:4]+'/'+raceCode[6:10]+'/'
                if os.path.exists(path):
                    files = os.listdir(path)
                    for file in files:
                        if raceCode in file:
                            fileName = file
                            number=int(fileName.split('_')[9])
                            f = open(path+fileName,'r')
                            reader = csv.DictReader(f)
                            for row in reader:
                                if str(row['horse_code']) == str(dataset['horse_code']):
                                    if row['last_rank'] == '-':
                                        last_rank=9
                                    else:
                                        last_rank=int(row['last_rank'])
                                    corner=row['corner'].split('-')
                                    if corner[0] != '':
                                        first_corner=float(corner[0])
                                    else:
                                        first_corner=18
                                    if past == 1 and row['comment'] == '1' and (float(row['diff']) < 0.5 or float(row['odds']) < 10.0):
                                        comment_flg=1
                                    if last_rank == 1:
                                        last_flg=1
                                        last_sum+=1
                                    corner_sum+=first_corner/number
                            f.close()
        if corner_count != 0 and corner_sum/corner_count < 0.25:
            corner_flg=1

        strong=0
        weak=0
        print_dic={}
        print_dic['position'] = str(comment['position'])+' '+comment['name']
        if comment['0_gate'] is not None and comment['0_gate'] != 'null':
            gate_0 = float(comment['0_gate'])
            if comment['1_gate'] is not None and comment['1_gate'] != 'null':
                gate_1 = float(comment['1_gate'])
                gate_ratio = round(100*gate_0/gate_1,1)
                if gate_0 > upper or gate_0 < lower or gate_ratio > ratio_upper or gate_ratio < ratio_lower:
                    print_dic['gate'] = str(gate_0)+'('+str(gate_ratio)+'%)'
                    if gate_0 > upper or gate_ratio > ratio_upper:
                        strong+=1
                    else:
                        weak+=1
            else:
                gate_ratio = '--.-'

        for print_target in ['sire','bms']:
            print_dic[print_target] = comment[print_target+'_name']
            for print_key in ['sex','age','class','track','roadCondition','distance','rotation_epoch','rotation_roadbed','rotation_distance']:
                if print_target == 'sire' and print_key in ['sex','age']:
                    if comment['sire_'+print_key] is not None and comment['sire_'+print_key] != 'null' and (float(comment['sire_'+print_key]) > upper or float(comment['sire_'+print_key]) < lower):
                        print_dic[print_key] = comment['sire_'+print_key]
                        if float(print_dic[print_key]) > upper:
                            strong+=1
                        else:
                            weak+=1
                elif print_key in ['class','track','roadCondition','distance','rotation_epoch','rotation_roadbed','rotation_distance']:
                    if comment['0_'+print_target+'_'+print_key] is not None and comment['0_'+print_target+'_'+print_key] != 'null':
                        value_0 = float(comment['0_'+print_target+'_'+print_key])
                        if comment['1_'+print_target+'_'+print_key] is not None and comment['1_'+print_target+'_'+print_key] != 'null':
                            value_1 = float(comment['1_'+print_target+'_'+print_key])
                            key_ratio = round(100*value_0/value_1,1)
                            if value_0 > upper or value_0 < lower or key_ratio > ratio_upper or key_ratio < ratio_lower:
                                print_dic[print_target+'_'+print_key] = str(value_0)+'('+str(key_ratio)+'%)'
                                if value_0 > upper or key_ratio > ratio_upper:
                                    strong+=1
                                else:
                                    weak+=1
                        else:
                            key_ratio = '--.-'

        sire_num=0
        bms_num=0
        for key in comment:
            if 'name' not in key and '0_' in key and comment[key] is not None and comment[key] != 'null':
                if 'sire' in key:
                    sire_num+=1
                elif 'bms' in key:
                    bms_num+=1

        if abs(strong-weak) > 1 or comment_flg == 1 or last_flg == 1 or corner_flg == 1 or sire_num < 4 or bms_num < 3:
            if strong - weak > 1:
                print(pycolor.pycolor.PURPLE+'@@@ HIGH Potential @@@')
            elif strong - weak < -1:
                print(pycolor.pycolor.GREEN+'xxx LOW Potential xxx')
            for print_key in print_dic:
                if print_key in ['position','sire','bms']:
                    print(print_key,print_dic[print_key])
                else:
                    print(' ',print_key,print_dic[print_key])
            print(pycolor.pycolor.END,end='')
            if last_flg == 1 or corner_flg == 1:
                print(pycolor.pycolor.RED+'<<< GOOD Performance >>>')
                if corner_flg == 1:
                    print('Good START:',str(round(100*corner_sum/corner_count,1))+'%')
                if last_flg == 1:
                    print('Good LAST:',str(last_sum)+'/'+str(last_count))
            print(pycolor.pycolor.END,end='')
            if comment_flg == 1 or sire_num < 4 or bms_num < 3:
                print(pycolor.pycolor.YELLOW+'!!! ATTENTION !!!')
                if sire_num < 4:
                    print('Lack of SIRE information')
                if bms_num < 3:
                    print('Lack of BMS information')
                if  comment_flg == 1:
                    url='https://db.netkeiba.com/race/'+dataset['1_raceCode']
                    print('Comment: '+url)
                    # webbrowser.open(url)
            print(pycolor.pycolor.END,end='')
        print('*')


if __name__ == '__main__':

    # '01':'札幌','02':'函館','03':'福島','04':'新潟','05':'東京','06':'中山','07':'中京','08':'京都','09':'阪神','10':'小倉'

    args = sys.argv
    holding_args=args[1]
    race_from=int(args[2])
    race_to=race_from
    mode_flg=0 # 0: threshold-mode, 1: all-mode
    odds_flg='0' # 0: off, 1: on
    range_flg='0' # 0: off, 1: on
    condition_switch='9' # 0: 良, 1: 稍, 2: 重, 3: 不, 9: None

    if holding_args == '1':
        holding={'01':'0202'}
    elif holding_args == '4':
        holding={'04':'0302'}
    elif holding_args == '10':
        holding={'10':'0202'}

    target(holding,race_from,race_to+1,odds_flg,range_flg,condition_switch)
    fukusho_pred()
