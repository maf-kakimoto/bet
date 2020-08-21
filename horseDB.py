# -*- coding: utf-8 -*-

import time
import pandas as pd

# self-made
import manage_mysql

def horseDB(table,search):

    con = manage_mysql.connect()
    c = con.cursor()

    column=[]
    value=[]
    for i in range(len(search)):
        if i%2 == 0:
            column.append(search[i])
        else:
            value.append(search[i])

    sql='SELECT * FROM '+table+' where '

    for i in range(len(column)):
        if i != 0:
            sql+=' and '
        sql+=column[i]+' = "'+str(value[i])+'"'

    result = pd.read_sql(sql,con)

    con.close()

    return result


def fukusho(group,search,limit):

    sql='SELECT '+group+',count(*),sum(fukusho),sum(fukusho)/count(*) From mergedresult '

    if search['column'] == '':
        sql+='where '
        if limit != 0:
            ut=time.time()
            epoch=int(ut)-60*60*24*limit
        else:
            epoch=0
        sql+='epoch >= '+str(epoch)+' '

    elif search['column'] == 'sex':
        sql+='where '
        sql+=search['column']+' = "'+search['value']+'" '

    elif search['column'] == 'age':
        sql+='where '
        if search['value'] == 7:
            sql+='year - birth >= '+str(search['value'])+' '
        else:
            sql+='year - birth = '+str(search['value'])+' '

    elif search['column'] == 'road':
        sql+='where '
        value=search['value'].split("_")
        roadbed=value[1]
        roadCondition=value[2]
        if roadbed == 'turf':
            roadbed = '0'
        elif roadbed == 'dirt':
            roadbed = '1'
        sql+='roadbed = "'+roadbed+'" and '
        if roadCondition == 'good':
            sql+='(roadCondition = "0") '
        elif roadCondition == 'bad':
            sql+='(roadCondition = "1" or roadCondition = "2" or roadCondition = "3") '

    elif search['column'] == 'distance_category':
        sql+='where distance_category = "'
        value=search['value'].split("_")
        category=value[1]
        if category == 'sprint':
            category = '0'
        elif category == 'mile':
            category = '1'
        elif category == 'intermediate':
            category = '2'
        elif category == 'long':
            category = '3'
        elif category == 'extended':
            category = '4'
        sql+=category+'" '

    elif search['column'] == 'win_class':
        sql+='where '
        value=search['value'].split("_")
        grade=value[1]
        sql+=search['column']+' = "'+str(grade)+'" '

    elif search['column'] == 'track':
        sql+='where '
        track=search['value']
        track=track.split("_")
        course=track[1]
        roadbed=track[2]
        if roadbed == 'turf':
            roadbed = '0'
        elif roadbed == 'dirt':
            roadbed = '1'
        sql+='course = "'+course+'" and roadbed = "'+roadbed+'" '
        if len(track) == 4: # (04 or 08) and turf
            inout=track[3]
            if course == '04':
                if inout == 'in':
                    sql+=' and distance like "%in" '
                elif inout == 'out':
                    sql+=' and distance like "%out" '
            elif course == '08':
                if inout == 'in':
                    sql+=' and distance like "%in" '
                elif inout == 'out':
                    sql+=' and distance like "%out" '

    elif search['column'] == 'rotation_epoch':
        sql+='where '
        value=search['value'].split("_")
        rotationEpoch=value[2]
        if rotationEpoch == 'short': # threshold: 6weeks
            sql+=search['column']+' <= 60*60*24*7*6 and '+search['column']+' != 0 '
        elif rotationEpoch == 'long':
            sql+=search['column']+' > 60*60*24*7*6 '

    elif search['column'] == 'rotation_roadbed':
        sql+='where '
        value=search['value'].split("_")
        rotationRoadbed=value[2]
        if rotationRoadbed == 'toTurf':
            sql+=search['column']+' = 1 and roadbed = "0" '
        elif rotationRoadbed == 'toDirt':
            sql+=search['column']+' = 1 and roadbed = "1" '

    elif search['column'] == 'rotation_distance':
        sql+='where '
        value=search['value'].split("_")
        rotationDistance=value[2]
        if rotationDistance == 'shortening':
            sql+='distance/(distance-'+search['column']+') < 0.9 '
        elif rotationDistance == 'extension':
            sql+='distance/(distance-'+search['column']+') > 1.1 '

    sql+='GROUP BY '+group

    print(sql)

    con = manage_mysql.connect()
    result = pd.read_sql(sql,con)
    con.commit()
    con.close()

    return result
