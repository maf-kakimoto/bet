# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import chromedriver_binary

def odds(year,course,date,raceNo):

    options = Options()
    options.set_headless(True)
    # options.add_argument('--headless')
    driver = webdriver.Chrome(chrome_options=options)

    driver.get('https://race.netkeiba.com/odds/index.html?type=b1&race_id='+str(year)+course+date+raceNo+'&rf=shutuba_submenu')
    html = driver.page_source.encode('utf-8')
    driver.quit()
    odds_soup = BeautifulSoup(html, 'html.parser')
    popular=odds_soup.select('.Odds')
    tmpList=[]
    i=0
    for odds in popular:
        tmpList.append(odds.text)
        if odds.text == '---.-':
            tmpList.append(odds.text)
        i+=1
    oddsList=[]
    i=0
    for tmp in tmpList:
        if i%2 == 0:
            if tmp == '---.-':
                tmp = '999.9'
            oddsList.append(tmp)
        i+=1

    return oddsList
