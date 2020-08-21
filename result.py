# -*- coding: utf-8 -*-

from datetime import datetime
import re
import csv
import os
import yaml

# self made
import manage_mysql
import conversion


def main(syllabaryDoc,year,courseNum,holding):

    if year == 'all':
        year_from = 2015
        year_to = 2021
    else:
        year_from = year
        year_to = year_from+1
    if courseNum == 'all':
        course_from = 0
        course_to = 10
    else:
        course_from = int(courseNum)-1
        course_to = course_from+1
    if holding == 'all':
        times_from = 0
        times_to = 5
        days_from = 0
        days_to = 12
    else:
        times_from = int(holding[0:2])-1
        times_to = times_from+1
        days_from = int(holding[2:4])-1
        days_to = days_from+1

    result={'course':'','year':'','holding':'','raceNo':'','roadbed':'','distance':'','distance_category':'','roadCondition':'',
            'age_class':'','win_class':'','sex_class':'','loafCondition':'','ranking':'','gate':'','horseName':'','horse_code':'',
            'sex':'','birth':'','age':'','loaf':'','jockey':'','jockey_code':'','jockey_handicap':'','additional_handicap':'','handicap':'',
            'rotation_epoch':'','rotation_roadbed':'','rotation_distance':'','time':'','diff':'','popularity':'','odds':'',
            'last':'','last_rank':'','corner':'','trainer':'','trainer_code':'','trainer_belongs':'','owner':'','owner_code':'',
            'weight':'','weightDiff':'','comment':'','prize':'','tansho':'','fukusho':'','epoch':'','number':'','weather':'','date':''}

    for l in range(course_from,course_to):
        result['course']='{0:02d}'.format(l+1)
        for year_item in range(year_from,year_to):
            result['year']=str(year_item)
            for k in range(times_from,times_to):
                for j in range(days_from,days_to):
                    result['holding']=str('{0:02d}'.format(k+1))+str('{0:02d}'.format(j+1))
                    path = 'races/'+result['course']+'/'+result['year']+'/'+result['holding']+'/'
                    print(path)
                    if os.path.exists(path):
                        files = os.listdir(path)
                        for file in files:
                            data = open(path+file,'r')
                            print(path,file)
                            fileItem=file.split('_')
                            reader = csv.DictReader(data)
                            result['raceNo']=fileItem[0][10:]
                            result['roadbed']=fileItem[1]
                            result['distance']=fileItem[2]
                            outFlg=fileItem[3]
                            if result['course'] == '04' and result['roadbed'] == '0' and result['distance'] == '2000':
                                    if outFlg == '0':
                                        result['distance']+='in'
                                    elif outFlg == '1':
                                        result['distance']+='out'
                            elif result['course'] == '08' and result['roadbed'] == '0' and result['distance'] in ['1400','1600']:
                                    if outFlg == '0':
                                        result['distance']+='in'
                                    elif outFlg == '1':
                                        result['distance']+='out'
                            result['roadCondition']=fileItem[4]
                            result['age_class']=fileItem[5]
                            result['win_class']=fileItem[6]
                            result['sex_class']=fileItem[7]
                            result['loafCondition']=fileItem[8]
                            result['number']=fileItem[9]
                            result['weather']=fileItem[10]
                            result['date']=fileItem[11].split('.')[0]
                            date=result['date'].split('-')
                            epoch=datetime(int(date[0]),int(date[1]),int(date[2].split('.')[0]),0,0).strftime('%s')
                            result['epoch']=epoch

                            for row in reader:

                                if str.isdecimal(row['rank']):

                                    category=str(re.sub('\\D','',result['distance']))
                                    result['distance_category']=conversion.distance_flg(category)
                                    result['ranking']=row['rank']
                                    result['gate']=row['gate']
                                    result['horseName']=row['horseName']
                                    result['horse_code']=row['horse_code']
                                    result['sex']=row['sex']
                                    result['birth']=str(int(result['year'])-int(row['age']))
                                    result['age']=row['age']
                                    result['loaf']=row['loaf']
                                    result['jockey']=row['jockey']
                                    result['jockey_code']=row['jockey_code']
                                    if row['jockey_handicap'] == '-':
                                        result['jockey_handicap']='0'
                                    else:
                                        result['jockey_handicap']=row['jockey_handicap']
                                    if row['jockey_handicap'] == '-':
                                        result['additional_handicap']='0'
                                    else:
                                        result['additional_handicap']=row['additional_handicap']
                                    result['handicap']=str(float(result['jockey_handicap'])+float(result['additional_handicap']))
                                    result['time']=row['time']
                                    result['diff']=row['diff']
                                    result['popularity']=row['popularity']
                                    result['odds']=row['odds']
                                    result['last']=row['last']
                                    result['last_rank']=row['last_rank']
                                    result['corner']=row['corner']
                                    corner_list=row['corner'].split('-')
                                    if len(corner_list) > 0 and corner_list[0] != '':
                                        result['1st_corner']=str(round(float(corner_list[0])/float(result['number']),3))
                                    else:
                                        result['1st_corner']='-'
                                    if len(corner_list) > 1 and corner_list[1] != '':
                                        result['2nd_corner']=str(round(float(corner_list[1])/float(result['number']),3))
                                    else:
                                        result['2nd_corner']='-'
                                    if len(corner_list) > 2 and corner_list[2] != '':
                                        result['3rd_corner']=str(round(float(corner_list[2])/float(result['number']),3))
                                    else:
                                        result['3rd_corner']='-'
                                    if len(corner_list) > 3 and corner_list[3] != '':
                                        result['4th_corner']=str(round(float(corner_list[3])/float(result['number']),3))
                                    else:
                                        result['4th_corner']='-'
                                    result['trainer']=row['trainer']
                                    result['trainer_code']=row['trainer_code']
                                    result['trainer_belongs']=row['belongs']
                                    result['owner']=row['owner']
                                    result['owner_code']=row['owner_code']
                                    result['weight']=row['weight']
                                    result['weightDiff']=row['weightDiff']
                                    result['comment']=row['comment']
                                    result['prize']=row['prize']
                                    result['tansho']=row['tansho']
                                    result['fukusho']=row['fukusho']

                                    column_txt=''
                                    value_txt=''
                                    for column in result:
                                        column_txt+=column+','
                                        value_txt+='"'+result[column]+'",'
                                    column_txt=column_txt[:-1]+''
                                    value_txt=value_txt[:-1]

                                    initial=result['horseName'][0]

                                    con = manage_mysql.connect()
                                    c = con.cursor()
                                    sql='INSERT INTO _raceResult_'+syllabaryDoc[initial]+' ('+column_txt+') VALUES ('+value_txt+');'
                                    c.execute(sql)
                                    con.commit()
                                    con.close()

                            data.close()


def rotation(syllabaryDoc,year,courseNum,holding):

    for initial in syllabaryDoc:

        con = manage_mysql.connect()
        c = con.cursor()
        sql='select * from _raceResult_'+syllabaryDoc[initial]
        if year == 'all':
            sql+=' order by horse_code,epoch asc;'
        else:
            sql+=' where course = '+courseNum+' and year = '+str(year)+' and holding = '+holding+' order by horse_code,epoch asc;'
        c.execute(sql)
        results=c.fetchall()

        last_code,last_birth,last_epoch,last_roadbed,last_distance = '',0,0,'',0
        for result in results:
            code = result['horse_code']
            epoch = int(result['epoch'])
            roadbed = result['roadbed']
            distance = int(re.sub('\\D','',result['distance']))
            if code != last_code:
                rotation_epoch,rotation_roadbed,rotation_distance=0,0,0
                print()
            else:
                rotation_epoch=epoch-last_epoch
                if roadbed != last_roadbed:
                    rotation_roadbed=1
                else:
                    rotation_roadbed=0
                rotation_distance=distance-last_distance

            print(result['horseName'])

            sql='UPDATE _raceResult_'+syllabaryDoc[initial]+' SET'
            sql+=' rotation_epoch='+str(rotation_epoch)
            sql+=',rotation_roadbed='+str(rotation_roadbed)
            sql+=',rotation_distance='+str(rotation_distance)
            sql+=' where year='+str(result['year'])+' and holding="'+result['holding']+'" and horse_code="'+code+'";'
            c.execute(sql)
            con.commit()

            last_code = code
            last_epoch = epoch
            last_roadbed = roadbed
            last_distance = distance

        con.close()



def merge(syllabaryDoc):

    con = manage_mysql.connect()
    c = con.cursor()
    sql='DELETE from raceResult;'
    c.execute(sql)

    for initial in syllabaryDoc:
        sql='INSERT INTO raceResult SELECT * FROM _raceResult_'+syllabaryDoc[initial]+';'
        c.execute(sql)
        con.commit()

    con.close()


def createTable(syllabaryDoc):

    for syllabary in syllabaryDoc:
        sql='drop table _raceResult_'+syllabaryDoc[syllabary]+';'
        c.execute(sql)
        sql='create table _raceResult_'+syllabaryDoc[syllabary]+' like raceResult;'
        c.execute(sql)


def delTable(syllabaryDoc):

    for syllabary in syllabaryDoc:
        sql='DELETE from _raceResult_'+syllabaryDoc[syllabary]+';'
        c.execute(sql)


def weekly(year,holdings):

    f = open('yml/syllabary.yml','r')
    syllabaryDoc = yaml.safe_load(f)
    syllabaryDoc = syllabaryDoc["syllabary"]
    f.close()

    for courseNum in holdings:
        main(syllabaryDoc,year,courseNum,holdings[courseNum])
        rotation(syllabaryDoc,year,courseNum,holdings[courseNum])

    merge(syllabaryDoc)


if __name__ == '__main__':

    f = open('yml/syllabary.yml','r')
    syllabaryDoc = yaml.safe_load(f)
    syllabaryDoc = syllabaryDoc["syllabary"]
    f.close()

    con = manage_mysql.connect()
    c = con.cursor()
    createTable(syllabaryDoc)
    delTable(syllabaryDoc)
    con.commit()
    con.close()

    main(syllabaryDoc,'all','all','all')
    rotation(syllabaryDoc,'all','all','all')
    merge(syllabaryDoc)
