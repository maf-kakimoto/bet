# -*- coding: utf-8 -*-

def roadbed_to_english(roadbed):

    if roadbed in ['芝','0']:
        roadbed_english='turf'
    elif roadbed in ['ダ','1']:
        roadbed_english='dirt'
    else:
        roadbed_english=roadbed

    return roadbed_english


def roadbed_flg(roadbed):

    if roadbed == '芝':
        flg = '0'
    elif roadbed == 'ダ':
        flg = '1'
    else:
        flg = '9'

    return flg


def condition_flg(condition):

    if condition == '良':
        flg = '0'
    elif condition in ['稍','稍重']:
        flg = '1'
    elif condition == '重':
        flg = '2'
    elif condition in ['不','不良']:
        flg = '3'
    else:
        flg = '9'

    return flg


def course_flg(course):

    courses={'札幌':'01','函館':'02','福島':'03','新潟':'04','東京':'05','中山':'06','中京':'07','京都':'08','阪神':'09','小倉':'10'}
    if course in courses:
        flg = courses[course]
    else:
        flg = '99'

    return flg


def distance_key(distance):

    if distance < 1400:
        key = 'distance_sprint'
    elif distance < 1900:
        key = 'distance_mile'
    elif distance < 2200:
        key = 'distance_intermediate'
    elif distance < 3000:
        key = 'distance_long'
    else:
        key = 'distance_extended'

    return key


def belongs_flg(belongs):

    if '美浦' in belongs or '[東]' in belongs:
        flg='0'
    elif '栗東' in belongs or '[西]' in belongs:
        flg='1'
    else:
        flg='2'

    return flg


def sex_flg(sex):

    if sex == '牡':
        flg = '0'
    elif sex == '牝':
        flg = '1'
    elif sex == 'セ':
        flg = '2'

    return flg


def winClass_flg(winClass):

    if winClass == '新馬':
        flg = '9'
    elif winClass == '未勝利':
        flg = '0'
    elif winClass in ['１勝','1勝']:
        flg = '1'
    elif winClass in ['２勝','2勝']:
        flg = '2'
    elif winClass in ['３勝','3勝']:
        flg = '3'
    elif winClass == 'オープン':
        flg = '4'

    return flg


def loafCondition_flg(loafCondition):

    if loafCondition == '馬齢':
        flg = '0'
    elif loafCondition == '定量':
        flg = '1'
    elif loafCondition == '別定':
        flg = '2'
    elif loafCondition == 'ハンデ':
        flg = '3'

    return flg


def distance_flg(distance):

    category={
    'sprint':['1000','1150','1200','1300'],
    'mile':['1400','1500','1600','1700','1800'],
    'intermediate':['1900','2000','2100'],
    'long':['2200','2300','2400','2500','2600'],
    'extended':['3000','3200','3400','3600']
    }

    if distance in category['sprint']:
        flg='0'
    elif distance in category['mile']:
        flg='1'
    elif distance in category['intermediate']:
        flg='2'
    elif distance in category['long']:
        flg='3'
    elif distance in category['extended']:
        flg='4'

    return flg
