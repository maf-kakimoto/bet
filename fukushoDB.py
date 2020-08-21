# -*- coding: utf-8 -*-

import pandas as pd

# self made
import horseDB
import conversion
import manage_mysql


def updateDB(table,group,column,raceResults):

    if column == 'distance_extended' or 'track' in column:
        threshold = 50
    else:
        threshold = 100

    target=group.split('_')[0]
    dic=target+'_dic'

    for i in range(len(raceResults)):

        con = manage_mysql.connect()
        c = con.cursor()

        code=raceResults[group][i]
        count=raceResults['count(*)'][i]
        sumFukusho=raceResults['sum(fukusho)'][i]
        returnFukusho=raceResults['sum(fukusho)/count(*)'][i]

        sql='SELECT '+target+' FROM '+dic+' WHERE '+group+' = "'+code+'"'
        c.execute(sql)
        result=c.fetchone()
        if result is not None:
            name=result[0]

        insertFlg=countLine(table,code)
        insertFlg=insertFlg[0][0]
        if insertFlg == 0:
            if name != '' and code != '':
                sql='INSERT INTO '+table+' (name,code) values ("'+name+'","'+code+'")'
                c.execute(sql)

        if count > threshold:
            returnFukusho=round(returnFukusho,1)
            value=column+' = '+str(returnFukusho)
            sql='UPDATE '+table+' SET '+value+' WHERE code = "'+code+'"'
            c.execute(sql)

        con.commit()
        con.close()


def main(group,table):

    sex={'sex_male':'0','sex_female':'1','sex_gelding':'2'}
    age={'age_2':2,'age_3':3,'age_4':4,'age_5':5,'age_6':6,'age_7over':7}
    road=['road_turf_good','road_turf_bad','road_dirt_good','road_dirt_bad']
    distance=['distance_sprint','distance_mile','distance_intermediate','distance_long','distance_extended']
    grade=['grade_9','grade_0','grade_1','grade_2','grade_3','grade_4']
    track=[
    'track_01_turf','track_01_dirt',
    'track_02_turf','track_02_dirt',
    'track_03_turf','track_03_dirt',
    'track_04_turf_in','track_04_turf_out','track_04_dirt',
    'track_05_turf','track_05_dirt',
    'track_06_turf','track_06_dirt',
    'track_07_turf','track_07_dirt',
    'track_08_turf_in','track_08_turf_out','track_08_dirt',
    'track_09_turf','track_09_dirt',
    'track_10_turf','track_10_dirt'
    ]
    rotation_epoch=['rotation_epoch_short','rotation_epoch_long']
    rotation_roadbed=['rotation_roadbed_toTurf','rotation_roadbed_toDirt']
    rotation_distance=['rotation_distance_shortening','rotation_distance_extension']

    search={'column':'','value':''}
    raceResults=horseDB.fukusho(group,search,0)
    updateDB(table,group,'general_all',raceResults)

    search={'column':'','value':''}
    raceResults=horseDB.fukusho(group,search,365)
    updateDB(table,group,'general_limit',raceResults)

    for key in sex:
        search={'column':'sex','value':sex[key]}
        raceResults=horseDB.fukusho(group,search,0)
        updateDB(table,group,key,raceResults)

    for key in age:
        search={'column':'age','value':age[key]}
        raceResults=horseDB.fukusho(group,search,0)
        updateDB(table,group,key,raceResults)

    for key in road:
        search={'column':'road','value':key}
        raceResults=horseDB.fukusho(group,search,0)
        updateDB(table,group,key,raceResults)

    for key in distance:
        search={'column':'distance_category','value':key}
        raceResults=horseDB.fukusho(group,search,0)
        updateDB(table,group,key,raceResults)

    for key in grade:
        search={'column':'win_class','value':key}
        raceResults=horseDB.fukusho(group,search,0)
        updateDB(table,group,key,raceResults)

    if group == 'sire_code' or group == 'bms_code':
        for key in track:
            search={'column':'track','value':key}
            raceResults=horseDB.fukusho(group,search,0)
            updateDB(table,group,key,raceResults)
        for key in rotation_epoch:
            search={'column':'rotation_epoch','value':key}
            raceResults=horseDB.fukusho(group,search,0)
            updateDB(table,group,key,raceResults)
        for key in rotation_roadbed:
            search={'column':'rotation_roadbed','value':key}
            raceResults=horseDB.fukusho(group,search,0)
            updateDB(table,group,key,raceResults)
        for key in rotation_distance:
            search={'column':'rotation_distance','value':key}
            raceResults=horseDB.fukusho(group,search,0)
            updateDB(table,group,key,raceResults)



def gate():

    con = manage_mysql.connect()
    c = con.cursor()

    sql='DELETE from fukushoGate'
    c.execute(sql)
    con.commit()

    for i in range(18):
        sql='SELECT course,distance,roadbed,count(*),sum(fukusho),sum(fukusho)/count(*) '
        sql+='From mergedresult '
        sql+='where gate = '+str(i+1)+' and ranking <> "除外" and ranking <> "取消" '
        sql+='GROUP BY course, distance, roadbed'
        results = pd.read_sql(sql,con)
        column='gate_'+str('{0:02d}'.format(i+1))
        for i in range(len(results)):
            count=results['count(*)'][i]
            sumFukusho=results['sum(fukusho)'][i]
            returnFukusho=results['sum(fukusho)/count(*)'][i]
            if count > 100:
                returnFukusho=round(returnFukusho,1)

                sql='SELECT * FROM fukushoGate'
                sql+=' WHERE course = "'+results['course'][i]+'" and distance = "'+results['distance'][i]+'" and roadbed = "'+results['roadbed'][i]+'"'
                c.execute(sql)
                count=c.fetchall()

                if len(count) == 0:
                    sql='INSERT INTO fukushoGate (course, distance, roadbed) VALUE '
                    sql+='("'+results['course'][i]+'","'+results['distance'][i]+'","'+results['roadbed'][i]+'")'
                    c.execute(sql)
                    con.commit()

                sql='UPDATE fukushoGate SET '+column+' = '+str(returnFukusho)+' '
                sql+='WHERE course = "'+results['course'][i]+'" and distance = "'+results['distance'][i]+'" and roadbed = "'+results['roadbed'][i]+'"'
                c.execute(sql)
                con.commit()

    con.close()


def popularity():

    con = manage_mysql.connect()
    c = con.cursor()

    sql='DELETE from fukushoPopularity'
    c.execute(sql)
    con.commit()

    sql='SELECT popularity,count(*),sum(fukusho),sum(fukusho)/count(*) '
    sql+='From mergedresult '
    sql+='where ranking <> "除外" and ranking <> "取消" '
    sql+='GROUP BY popularity'
    results = pd.read_sql(sql,con)

    for i in range(len(results)):

        popularity=results['popularity'][i]
        count=results['count(*)'][i]
        sumFukusho=results['sum(fukusho)'][i]
        returnFukusho=results['sum(fukusho)/count(*)'][i]
        if count > 100:
            returnFukusho=round(returnFukusho,1)
            sql='INSERT INTO fukushoPopularity (popularity, popularityFukusho) VALUE '
            sql+='('+str(popularity)+', '+str(returnFukusho)+')'
            c.execute(sql)

    con.commit()
    con.close()


def odds():

    threshold=['1','2','4','7','10','15','20','30','50','70','100','150','200','10000']

    con = manage_mysql.connect()
    c = con.cursor()

    sql='DELETE from fukushoOdds'
    c.execute(sql)
    con.commit()

    for j in range(len(threshold)-1):

        sql='SELECT fukusho '
        sql+='From mergedresult '
        sql+='where odds >= '+threshold[j]+' and odds < '+threshold[j+1]+' and ranking <> "除外" and ranking <> "取消" '
        results = pd.read_sql(sql,con)
        count,sumFukusho=0,0.0
        for i in range(len(results)):
            sumFukusho+=float(results['fukusho'][i])
            count+=1
        returnFukusho=sumFukusho/count

        if count > 100:
            returnFukusho=round(returnFukusho,1)
            standardization=round(returnFukusho/72.3,2)
            sql='INSERT INTO fukushoOdds (odds, oddsFukusho, standardization) VALUE '
            sql+='('+str(threshold[j])+', '+str(returnFukusho)+', '+str(standardization)+')'
            c.execute(sql)

    con.commit()
    con.close()


def handicap():

    con = manage_mysql.connect()
    c = con.cursor()

    sql='DELETE from fukushoHandicap'
    c.execute(sql)
    con.commit()

    sql='SELECT handicap,roadbed,roadCondition,count(*),sum(fukusho),sum(fukusho)/count(*) '
    sql+='From mergedresult '
    sql+='where ranking <> "除外" and ranking <> "取消" '
    sql+='GROUP BY handicap,roadbed,roadCondition;'
    results = pd.read_sql(sql,con)

    for i in range(len(results)):

        handicap=str(results['handicap'][i])
        roadbed=results['roadbed'][i]
        roadCondition=results['roadCondition'][i]
        count=results['count(*)'][i]
        sumFukusho=results['sum(fukusho)'][i]
        returnFukusho=results['sum(fukusho)/count(*)'][i]
        if count > 100:
            returnFukusho=round(returnFukusho,1)
            sql='INSERT INTO fukushoHandicap (handicap,roadbed,roadCondition,fukushoHandicap) VALUE '
            sql+='('+handicap+',"'+roadbed+'","'+roadCondition+'",'+str(returnFukusho)+')'
            c.execute(sql)

    con.commit()
    con.close()


def belongs():

    con = manage_mysql.connect()
    c = con.cursor()

    sql='DELETE from fukushoBelongs'
    c.execute(sql)
    for belongs_item in range(3):
        sql='INSERT INTO fukushoBelongs (belongs) VALUE ("'+str(belongs_item)+'")'
        c.execute(sql)

    distance_category=['distance_sprint','distance_mile','distance_intermediate','distance_long','distance_extended']
    track=['track_01_turf','track_01_dirt','track_02_turf','track_02_dirt','track_03_turf','track_03_dirt']
    track.append(['track_04_turf','track_04_dirt','track_05_turf','track_05_dirt','track_06_turf','track_06_dirt'])
    track.append(['track_07_turf','track_07_dirt','track_08_turf','track_08_dirt'])
    track.append(['track_09_turf','track_09_dirt','track_10_turf','track_10_dirt'])

    sql='SELECT trainer_belongs,distance_category,count(*),sum(fukusho),sum(fukusho)/count(*) '
    sql+='From mergedresult '
    sql+='GROUP BY trainer_belongs,distance_category;'
    results = pd.read_sql(sql,con)

    for i in range(len(results)):

        belongs=results['trainer_belongs'][i]
        category=int(results['distance_category'][i])
        count=results['count(*)'][i]
        sumFukusho=results['sum(fukusho)'][i]
        returnFukusho=results['sum(fukusho)/count(*)'][i]
        if count > 100:
            returnFukusho=str(round(returnFukusho,1))
            sql='UPDATE fukushoBelongs SET '+distance_category[category]+' = '+returnFukusho
            sql+=' WHERE belongs = '+str(belongs)+';'
            c.execute(sql)

    sql='SELECT trainer_belongs,course,roadbed,count(*),sum(fukusho),sum(fukusho)/count(*) '
    sql+='From mergedresult '
    sql+='GROUP BY trainer_belongs,course,roadbed;'
    results = pd.read_sql(sql,con)

    for i in range(len(results)):
        belongs=results['trainer_belongs'][i]
        course=results['course'][i]
        if results['roadbed'][i] == '0':
            roadbed='turf'
        elif results['roadbed'][i] == '1':
            roadbed='dirt'
        count=results['count(*)'][i]
        sumFukusho=results['sum(fukusho)'][i]
        returnFukusho=results['sum(fukusho)/count(*)'][i]
        if count > 100:
            returnFukusho=str(round(returnFukusho,1))
            sql='UPDATE fukushoBelongs SET track_'+course+'_'+roadbed+' = '+returnFukusho
            sql+=' WHERE belongs = '+str(belongs)+';'
            c.execute(sql)

    con.commit()
    con.close()


def style():

    con = manage_mysql.connect()
    c = con.cursor()

    sql='DELETE from fukushoType'
    c.execute(sql)
    for type_item in ['start','last']:
        sql='INSERT INTO fukushoType (type) VALUE ("'+type_item+'")'
        c.execute(sql)

    conditions=['turf_good','turf_bad','dirt_good','dirt_bad']
    classes=['9','0','1','2','3']
    track=['track_01_turf','track_01_dirt','track_02_turf','track_02_dirt','track_03_turf','track_03_dirt']
    track.append(['track_04_turf','track_04_dirt','track_05_turf','track_05_dirt','track_06_turf','track_06_dirt'])
    track.append(['track_07_turf','track_07_dirt','track_08_turf','track_08_dirt'])
    track.append(['track_09_turf','track_09_dirt','track_10_turf','track_10_dirt'])

    for type_item in ['start','last']:
        sql='SELECT roadbed,roadCondition,count(*),sum(fukusho),sum(fukusho)/count(*) '
        sql+='From mergedresult '
        if type_item == 'start':
            sql+='Where 1st_corner between 0 and 0.25'
        else:
            sql+='Where last_rank in (1,2,3) and roadCondition in (0,1)'
        sql+='GROUP BY roadbed,roadCondition;'
        results = pd.read_sql(sql,con)

        for i in range(len(results)):
            roadbed = conversion.roadbed_to_english(results['roadbed'][i])
            if results['roadCondition'][i] == '0':
                roadCondition='good'
            elif results['roadCondition'][i] == '1':
                roadCondition='bad'
            count=results['count(*)'][i]
            sumFukusho=results['sum(fukusho)'][i]
            returnFukusho=results['sum(fukusho)/count(*)'][i]
            if count > 100:
                returnFukusho=str(round(returnFukusho,1))
                sql='UPDATE fukushoType SET '+roadbed+'_'+roadCondition+' = '+returnFukusho
                sql+=' WHERE type = "'+type_item+'";'
                c.execute(sql)

        sql='SELECT win_class,count(*),sum(fukusho),sum(fukusho)/count(*) '
        sql+='From mergedresult '
        if type_item == 'start':
            sql+='Where 1st_corner between 0 and 0.25'
        else:
            sql+='Where last_rank in (1,2,3) and roadCondition in (0,1)'
        sql+='GROUP BY win_class;'
        results = pd.read_sql(sql,con)

        for i in range(len(results)):
            win_class=results['win_class'][i]
            count=results['count(*)'][i]
            sumFukusho=results['sum(fukusho)'][i]
            returnFukusho=results['sum(fukusho)/count(*)'][i]
            if count > 100:
                returnFukusho=str(round(returnFukusho,1))
                sql='UPDATE fukushoType SET winClass_'+win_class+' = '+returnFukusho
                sql+=' WHERE type = "'+type_item+'";'
                c.execute(sql)

        sql='SELECT course,roadbed,count(*),sum(fukusho),sum(fukusho)/count(*) '
        sql+='From mergedresult '
        if type_item == 'start':
            sql+='Where 1st_corner between 0 and 0.25'
        else:
            sql+='Where last_rank in (1,2,3) and roadCondition in (0,1)'
        sql+='GROUP BY course,roadbed;'
        results = pd.read_sql(sql,con)

        for result in results:
            course=results['course'][i]
            if results['roadbed'][i] == '0':
                roadbed='turf'
            elif results['roadbed'][i] == '1':
                roadbed='dirt'
            count=results['count(*)'][i]
            sumFukusho=results['sum(fukusho)'][i]
            returnFukusho=results['sum(fukusho)/count(*)'][i]
            if count > 100:
                returnFukusho=str(round(returnFukusho,1))
                sql='UPDATE fukushoType SET track_'+course+'_'+roadbed+' = '+returnFukusho
                sql+=' WHERE type = "'+type_item+'";'
                c.execute(sql)

    con.commit()
    con.close()


def code(dic):

    con=manage_mysql.connect()
    c = con.cursor()
    sql='drop table if exists '+dic+'_dic;'
    c.execute(sql)
    sql='create table '+dic+'_dic (SELECT distinct '+dic+','+dic+'_code FROM mergedresult);'
    c.execute(sql)
    con.commit()
    con.close()


def delete(table):

    con = manage_mysql.connect()
    c = con.cursor()
    sql='DELETE from '+table
    c.execute(sql)
    con.commit()
    con.close()


def countLine(table,code):

    con = manage_mysql.connect()
    c = con.cursor()
    sql='SELECT count(*) from '+table+' where code = "'+code+'"'
    c.execute(sql)
    result=c.fetchall()
    con.commit()
    con.close()

    return(result)


def weekly():

    dic_list=['sire','bms','jockey','trainer','owner','producer']
    for i in range(len(dic_list)):
        code(dic_list[i])

    group_table={
    'sire_code':'fukushoSire',
    'bms_code':'fukushoBms',
    'producer_code':'fukushoBreeder',
    'owner_code':'fukushoOwner',
    'jockey_code':'fukushoJockey',
    'trainer_code':'fukushoTrainer'
    }

    for group in group_table:
        delete(group_table[group])
        main(group,group_table[group])

    gate()
    popularity()
    odds()
    handicap()
    belongs()
    style()


if __name__ == '__main__':

    dic_list=['sire','bms','jockey','trainer','owner','producer']
    for i in range(len(dic_list)):
        code(dic_list[i])

    group_table={
    'sire_code':'fukushoSire',
    'bms_code':'fukushoBms',
    'producer_code':'fukushoBreeder',
    'owner_code':'fukushoOwner',
    'jockey_code':'fukushoJockey',
    'trainer_code':'fukushoTrainer'
    }

    for group in group_table:
        delete(group_table[group])
        main(group,group_table[group])

    gate()
    popularity()
    odds()
    handicap()
    belongs()
    style()
