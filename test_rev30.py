#!/usr/bin/python3
#apt-get install python3-bs4 python3-requests


#update url list

from bs4 import BeautifulSoup, SoupStrainer
import requests
import time
from os.path import basename
import csv
from multiprocessing import Pool

import logging

#DEBUG = True
DEBUG = False

if DEBUG: 
    logging_level=logging.DEBUG
else:
    logging_level=logging.INFO


logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
                            level=logging_level,
                            datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)










def popAndReturnFirstN(source_list, N=1):
    new_list = []
    for index in range(0, min(len(source_list), N)):
        new_list.append(source_list.pop(0))
    return new_list
 



logger.info('Start')




#https://stackoverflow.com/a/20760055
#import requests
#headers = {'User-Agent': 'Mozilla/5.0'}
#payload = {'username':'niceusername','password':'123456'}

#session = requests.Session()
#session.post('https://admin.example.com/login.php',headers=headers,data=payload)
# the session instance holds the cookie. So use it to get/post later.
# e.g. session.get('https://example.com/profile')


#headers = {
#    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36'
#}

def newSession(session):
    #load starting page no cookies

    url='http://timetable.student.curtin.edu.au/criteriaEntry.jsf'
    logger.info('First Page')
    logger.info('Downloading URL {}'.format(url))
    logger.info('session.cookies {}'.format(session.cookies))
    logger.info('session.headers {}'.format(session.headers))
    result = session.get(url)
    content = result.content
    logger.info('result {}'.format(result))
    logger.info('result.cookies {}'.format(result.cookies))
    logger.info('result.headers {}'.format(result.headers))
    logger.info('len(result.content) {}'.format(len(result.content)))
    logger.debug('result.content {}'.format(result.content))



    #soup = BeautifulSoup(content, 'lxml', parse_only=strainer)
    soup = BeautifulSoup(content, 'lxml')

    logger.info('get forms')
    formtags = soup.find_all("form")
    for form in formtags:
        #print(form)
        inputtags = form.find_all("input")
        for inputtag in inputtags:
            #print(inputtag)
            if inputtag.get('name') == "javax.faces.ViewState":
                viewStateValue = inputtag.get('value')
                logger.info('ViewState {}'.format(viewStateValue))
                return viewStateValue
            #print(tr.attrs['href'])
            #print(tr.text)


#https://stackoverflow.com/questions/20759981/python-trying-to-post-form-using-requests
#payload = {'username':'niceusername','password':'123456'}
#post('https://admin.example.com/login.php',headers=headers,data=payload)

def getUnitList(session, viewStateValue):
    #load search units
    payload = {'criteriaEntry':'criteriaEntry', 'criteriaEntry:timetableInitialised':'true', 'user':'', 'criteriaEntry:year':'2022', 'criteriaEntry:studyPeriod':'Semester 1', 'criteriaEntry:location':'Bentley Perth Campus', 'criteriaEntry:schoolDepartment':'0', 'criteriaEntry:filterUnitCodeOrTitle':'', 'javax.faces.ViewState':viewStateValue, 'javax.faces.source':'criteriaEntry:unitSearchButton', 'javax.faces.partial.event':'click', 'javax.faces.partial.execute':'criteriaEntry:unitSearchButton criteriaEntry', 'javax.faces.partial.render':'criteriaEntry:searchByUnitsDiv', 'javax.faces.behavior.event':'action', 'javax.faces.partial.ajax':'true'}

    url='http://timetable.student.curtin.edu.au/criteriaEntry.jsf'
    logger.info('Search for units')
    logger.info('Downloading URL {}'.format(url))
    logger.info('session.cookies {}'.format(session.cookies))
    logger.info('session.headers {}'.format(session.headers))
    result = session.post(url, data=payload)
    content = result.content
    logger.info('result {}'.format(result))
    logger.info('result.cookies {}'.format(result.cookies))
    logger.info('result.headers {}'.format(result.headers))
    logger.info('len(result.content) {}'.format(len(result.content)))
    logger.debug('result.content {}'.format(result.content))



    #soup = BeautifulSoup(content, 'lxml', parse_only=strainer)
    soup = BeautifulSoup(content, 'lxml')

    logger.info('get selects')
    selecttags = soup.find_all("select")
    for selecttag in selecttags:
        #print(selecttag)
        if selecttag.get('name') == "criteriaEntry:allUnits":
            optiontags = selecttag.find_all("option")
            unit_list = [(j.get('value'), j.text) for j in optiontags]
            logger.info('len(unit_list) {}'.format(len(unit_list)))
            logger.debug('unit_list {}'.format(unit_list))
            return unit_list
            #for optiontag in optiontags:
                #print(optiontag)
            #    code = optiontag.get('value')
            #    print(code)
            #    name = optiontag.text
            #    print(name)
                #print(tr.attrs['href'])
                #print(tr.text)
    




def addUnits(session, viewStateValue, units):
    #select then add	<option value="321381">PHTY7019 AMCC2</option>

    #maybe
    #  -H 'Faces-Request: partial/ajax' \

    #headers = {
    #    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36', 'Faces-Request': 'partial/ajax'
    #}
    units_params = [('criteriaEntry:allUnits', i) for i in units]
    payload = (('criteriaEntry', 'criteriaEntry'), ('criteriaEntry:timetableInitialised', 'true'), ('user', ''), ('criteriaEntry:year', '2022'), ('criteriaEntry:studyPeriod', 'Semester 1'), ('criteriaEntry:location', 'Bentley Perth Campus'), ('criteriaEntry:schoolDepartment', '0'), ('criteriaEntry:filterUnitCodeOrTitle', ''),
            *units_params,
            ('javax.faces.ViewState', viewStateValue), ('javax.faces.source', 'criteriaEntry:addButton'), ('javax.faces.partial.event', 'click'), ('javax.faces.partial.execute', 'criteriaEntry:addButton criteriaEntry'), ('javax.faces.partial.render', 'criteriaEntry:searchByUnitsDiv'), ('javax.faces.behavior.event', 'action'), ('javax.faces.partial.ajax', 'true'))

    logger.info('payload {}'.format(payload))

    url='http://timetable.student.curtin.edu.au/criteriaEntry.jsf'
    logger.info('Add units')
    logger.info('Downloading URL {}'.format(url))
    logger.info('session.cookies {}'.format(session.cookies))
    logger.info('session.headers {}'.format(session.headers))
    result = session.post(url , data=payload)
    content = result.content
    logger.info('result {}'.format(result))
    logger.info('result.cookies {}'.format(result.cookies))
    logger.info('result.headers {}'.format(result.headers))
    logger.info('len(result.content) {}'.format(len(result.content)))
    logger.debug('result.content {}'.format(result.content))


    #soup = BeautifulSoup(content, 'lxml', parse_only=strainer)
    soup = BeautifulSoup(content, 'lxml')





def viewTimeTable(session, viewStateValue):
    #view timetable



    payload = {
        
    'criteriaEntry':'criteriaEntry', 'criteriaEntry:timetableInitialised':'true', 'user':'', 'criteriaEntry:year':'2022', 'criteriaEntry:studyPeriod':'Semester 1', 'criteriaEntry:location':'Bentley Perth Campus', 'criteriaEntry:schoolDepartment':'0', 'criteriaEntry:filterUnitCodeOrTitle':'', 'criteriaEntry:timetableForUnitsButton':'View Timetable for Selected Units', 'javax.faces.ViewState':viewStateValue
    }
    url='http://timetable.student.curtin.edu.au/criteriaEntry.jsf'
    logger.info('view timetable')
    logger.info('Downloading URL {}'.format(url))
    logger.info('session.cookies {}'.format(session.cookies))
    logger.info('session.headers {}'.format(session.headers))
    result = session.post(url , data=payload)
    content = result.content
    logger.info('result {}'.format(result))
    logger.info('result.cookies {}'.format(result.cookies))
    logger.info('result.headers {}'.format(result.headers))
    logger.info('len(result.content) {}'.format(len(result.content)))
    logger.debug('result.content {}'.format(result.content))


    #soup = BeautifulSoup(content, 'lxml', parse_only=strainer)
    soup = BeautifulSoup(content, 'lxml')


    logger.info('get table')
    tabletags = soup.find_all("table")
    sessions = []
    for tabletag in tabletags:
    #    print(tabletag)
    #    print(tabletag.get('id'))
    #    if tabletag.get('class') == "unitList":

        if tabletag.get('id') is not None:
            if "unitDataTable" in tabletag.get('id'):
                logger.info('found table')
                
                #print(i.text)
                #for j in i.find_elements_by_tag_name("td"):
                #    print(j.text)
                trtags = tabletag.find_all("tr")
                for trtag in trtags:
                    comp_list = [td.text for td in trtag.find_all("td")]
                    if len(comp_list) >0:
                        #print(comp_list)
                        sessions.append(comp_list)
    return sessions
                
                





session = requests.Session()
ViewState = newSession(session)
unitList = getUnitList(session, ViewState)

#unitList = unitList[:15]

with open('units.csv', 'wt') as f:
    csv_writer = csv.writer(f)
    csv_writer.writerows(unitList)

with open('times.csv', 'wt') as f:
    csv_writer = csv.writer(f)
    while len(unitList) > 0:
        list_to_download =  popAndReturnFirstN(unitList, 8)

        print(list_to_download)

        codenums = [i for i, j in list_to_download]

        print(codenums)

        session = requests.Session()
        ViewState = newSession(session)
        getUnitList(session, ViewState)
        addUnits(session, ViewState, codenums)
        classTimes = viewTimeTable(session, ViewState)

        print(classTimes)
        csv_writer.writerows(classTimes)
        
        print('units left {}'.format(len(unitList)))
        #time.sleep(10)

exit()

#go back from timetable

"""
payload =  (('timetableByUnits', 'timetableByUnits'), ('criteriaEntry:timetableInitialised', 'true'), ('timetableByUnits:timetableGrid', ''),('timetableByUnits:j_idt134', '<< Back'), ('javax.faces.ViewState', '530295001369416814:6773285523807330885'))
url='http://timetable.student.curtin.edu.au/criteriaEntry.jsf'
logger.info('try to go back to units')
logger.info('Downloading URL ' + ''.join(url))
logger.info('session.cookies {}'.format(session.cookies))
logger.info('session.headers {}'.format(session.headers))
result = session.post(url , data=payload)
content = result.content
logger.info('result {}'.format(result))
logger.info('result.cookies {}'.format(result.cookies))
logger.info('result.headers {}'.format(result.headers))
logger.info('result.content {}'.format(result.content))


#soup = BeautifulSoup(content, 'lxml', parse_only=strainer)
soup = BeautifulSoup(content, 'lxml')
"""




"""

#clear units

payload = {
    
'criteriaEntry':'criteriaEntry', 'criteriaEntry:timetableInitialised':'true', 'user':'', 'criteriaEntry:year':'2021', 'criteriaEntry:studyPeriod':'Semester 2', 'criteriaEntry:location':'Bentley Perth Campus', 'criteriaEntry:schoolDepartment':'0', 'criteriaEntry:filterUnitCodeOrTitle':'', 'criteriaEntry:timetableForUnitsButton':'View Timetable for Selected Units', 'javax.faces.ViewState':viewStateValue
}
url='http://timetable.student.curtin.edu.au/criteriaEntry.jsf'
logger.info('clear units')
logger.info('Downloading URL {}'.format(url))
logger.info('session.cookies {}'.format(session.cookies))
logger.info('session.headers {}'.format(session.headers))
result = session.post(url , data=payload)
content = result.content
logger.info('result {}'.format(result))
logger.info('result.cookies {}'.format(result.cookies))
logger.info('result.headers {}'.format(result.headers))
logger.info('len(result.content) {}'.format(len(result.content)))
logger.debug('result.content {}'.format(result.content))


#soup = BeautifulSoup(content, 'lxml', parse_only=strainer)
soup = BeautifulSoup(content, 'lxml')
"""




#maybe
(('timetableByUnits', 'timetableByUnits'), ('criteriaEntry:timetableInitialised', 'true'), ('timetableByUnits:timetableGrid', ''),('timetableByUnits:j_idt134', '<< Back'), ('javax.faces.ViewState', '530295001369416814:6773285523807330885'))

#go back from timetable


(('timetableByUnits', 'timetableByUnits'), ('criteriaEntry:timetableInitialised', 'true'), ('timetableByUnits:timetableGrid', ''), ('timetableByUnits:timetableGrid_last_clicked_date', ''), ('timetableByUnits:timetableGrid_last_clicked_y', ''), ('timetableByUnits:unitDataList:0:unitDataTable:flattenedListCheckBoxHeader', 'on'), ('timetableByUnits:unitDataList:0:unitDataTable:0:flattenedListCheckBoxRow', 'true'), ('timetableByUnits:unitDataList:0:unitDataTable:1:flattenedListCheckBoxRow', 'true'), ('timetableByUnits:unitDataList:0:unitDataTable:2:flattenedListCheckBoxRow', 'true'), ('timetableByUnits:unitDataList:0:unitDataTable:3:flattenedListCheckBoxRow', 'true'), ('timetableByUnits:unitDataList:0:unitDataTable:4:flattenedListCheckBoxRow', 'true'), ('timetableByUnits:unitDataList:0:unitDataTable:5:flattenedListCheckBoxRow', 'true'), ('timetableByUnits:unitDataList:0:unitDataTable:6:flattenedListCheckBoxRow', 'true'), ('timetableByUnits:unitDataList:0:unitDataTable:7:flattenedListCheckBoxRow', 'true'), ('timetableByUnits:unitDataList:0:unitDataTable:8:flattenedListCheckBoxRow', 'true'), ('timetableByUnits:unitDataList:0:unitDataTable:9:flattenedListCheckBoxRow', 'true'), ('timetableByUnits:unitDataList:0:unitDataTable:10:flattenedListCheckBoxRow', 'true'), ('timetableByUnits:unitDataList:0:unitDataTable:11:flattenedListCheckBoxRow', 'true'), ('timetableByUnits:unitDataList:0:unitDataTable:12:flattenedListCheckBoxRow', 'true'), ('timetableByUnits:unitDataList:0:unitDataTable:13:flattenedListCheckBoxRow', 'true'), ('timetableByUnits:unitDataList:0:unitDataTable:14:flattenedListCheckBoxRow', 'true'), ('timetableByUnits:j_idt134', '<< Back'), ('javax.faces.ViewState', '530295001369416814:6773285523807330885'))


"""
'timetableByUnits=timetableByUnits&criteriaEntry:timetableInitialised=true&timetableByUnits:timetableGrid=&timetableByUnits:timetableGrid_last_clicked_date=&timetableByUnits:timetableGrid_last_clicked_y=&timetableByUnits:unitDataList:0:unitDataTable:flattenedListCheckBoxHeader=on&timetableByUnits:unitDataList:0:unitDataTable:0:flattenedListCheckBoxRow=true&timetableByUnits:unitDataList:0:unitDataTable:1:flattenedListCheckBoxRow=true&timetableByUnits:unitDataList:0:unitDataTable:2:flattenedListCheckBoxRow=true&timetableByUnits:unitDataList:0:unitDataTable:3:flattenedListCheckBoxRow=true&timetableByUnits:unitDataList:0:unitDataTable:4:flattenedListCheckBoxRow=true&timetableByUnits:unitDataList:0:unitDataTable:5:flattenedListCheckBoxRow=true&timetableByUnits:unitDataList:0:unitDataTable:6:flattenedListCheckBoxRow=true&timetableByUnits:unitDataList:0:unitDataTable:7:flattenedListCheckBoxRow=true&timetableByUnits:unitDataList:0:unitDataTable:8:flattenedListCheckBoxRow=true&timetableByUnits:unitDataList:0:unitDataTable:9:flattenedListCheckBoxRow=true&timetableByUnits:unitDataList:0:unitDataTable:10:flattenedListCheckBoxRow=true&timetableByUnits:unitDataList:0:unitDataTable:11:flattenedListCheckBoxRow=true&timetableByUnits:unitDataList:0:unitDataTable:12:flattenedListCheckBoxRow=true&timetableByUnits:unitDataList:0:unitDataTable:13:flattenedListCheckBoxRow=true&timetableByUnits:unitDataList:0:unitDataTable:14:flattenedListCheckBoxRow=true&timetableByUnits:j_idt134=<< Back&javax.faces.ViewState=530295001369416814:6773285523807330885' """


#https://stackoverflow.com/a/45306525
#data -- (optional) Dictionary or list of tuples [(key, value)] (will be form-encoded), bytes, or file-like object to send in the body of the Request.

# replace ", " with "), ("
# replace "':'" with "', '"

#add multiple units

{'criteriaEntry':'criteriaEntry', 'criteriaEntry:timetableInitialised':'true', 'user':'', 'criteriaEntry:year':'2021', 'criteriaEntry:studyPeriod':'Semester 2', 'criteriaEntry:location':'Bentley Perth Campus', 'criteriaEntry:schoolDepartment':'0', 'criteriaEntry:filterUnitCodeOrTitle':'', 'criteriaEntry:allUnits':'318509', 'criteriaEntry:allUnits':'321381', 'criteriaEntry:allUnits':'315560', 'javax.faces.ViewState':'-5340187164806647053:3851751676204638174', 'javax.faces.source':'criteriaEntry:addButton', 'javax.faces.partial.event':'click', 'javax.faces.partial.execute':'criteriaEntry:addButton criteriaEntry', 'javax.faces.partial.render':'criteriaEntry:searchByUnitsDiv', 'javax.faces.behavior.event':'action', 'javax.faces.partial.ajax':'true' }


#remove multiple units

{'criteriaEntry':'criteriaEntry', 'criteriaEntry:timetableInitialised':'true', 'user':'', 'criteriaEntry:year':'2021', 'criteriaEntry:studyPeriod':'Semester 2', 'criteriaEntry:location':'Bentley Perth Campus', 'criteriaEntry:schoolDepartment':'0', 'criteriaEntry:filterUnitCodeOrTitle':'', 'criteriaEntry:selectedUnits':'318509', 'criteriaEntry:selectedUnits':'321381', 'criteriaEntry:selectedUnits':'315560', 'javax.faces.ViewState':'-122641214671914646:749242592233144154', 'javax.faces.source':'criteriaEntry:removeButton', 'javax.faces.partial.event':'click', 'javax.faces.partial.execute':'criteriaEntry:removeButton criteriaEntry', 'javax.faces.partial.render':'criteriaEntry:searchByUnitsDiv', 'javax.faces.behavior.event':'action', 'javax.faces.partial.ajax':'true'}




#clear

{'criteriaEntry':'criteriaEntry', 'criteriaEntry:timetableInitialised':'true', 'user':'', 'criteriaEntry:year':'2021', 'criteriaEntry:studyPeriod':'Semester 2', 'criteriaEntry:location':'Bentley Perth Campus', 'criteriaEntry:schoolDepartment':'0', 'criteriaEntry:filterUnitCodeOrTitle':'', 'javax.faces.ViewState':'-122641214671914646:749242592233144154', 'javax.faces.source':'criteriaEntry:removeAllButton', 'javax.faces.partial.event':'click', 'javax.faces.partial.execute':'criteriaEntry:removeAllButton criteriaEntry', 'javax.faces.partial.render':'criteriaEntry:searchByUnitsDiv', 'javax.faces.behavior.event':'action', 'javax.faces.partial.ajax':'true' }













"""
add multiple units

  --data-raw 'criteriaEntry=criteriaEntry&criteriaEntry:timetableInitialised=true&user=&criteriaEntry:year=2021&criteriaEntry:studyPeriod=Semester 2&criteriaEntry:location=Bentley Perth Campus&criteriaEntry:schoolDepartment=0&criteriaEntry:filterUnitCodeOrTitle=&criteriaEntry:allUnits=318509&criteriaEntry:allUnits=321381&criteriaEntry:allUnits=315560&javax.faces.ViewState=-5340187164806647053:3851751676204638174&javax.faces.source=criteriaEntry:addButton&javax.faces.partial.event=click&javax.faces.partial.execute=criteriaEntry:addButton criteriaEntry&javax.faces.partial.render=criteriaEntry:searchByUnitsDiv&javax.faces.behavior.event=action&javax.faces.partial.ajax=true' \


remove multiple units

  --data-raw 'criteriaEntry=criteriaEntry&criteriaEntry:timetableInitialised=true&user=&criteriaEntry:year=2021&criteriaEntry:studyPeriod=Semester 2&criteriaEntry:location=Bentley Perth Campus&criteriaEntry:schoolDepartment=0&criteriaEntry:filterUnitCodeOrTitle=&criteriaEntry:selectedUnits=318509&criteriaEntry:selectedUnits=321381&criteriaEntry:selectedUnits=315560&javax.faces.ViewState=-122641214671914646:749242592233144154&javax.faces.source=criteriaEntry:removeButton&javax.faces.partial.event=click&javax.faces.partial.execute=criteriaEntry:removeButton criteriaEntry&javax.faces.partial.render=criteriaEntry:searchByUnitsDiv&javax.faces.behavior.event=action&javax.faces.partial.ajax=true' \




clear

  --data-raw 'criteriaEntry=criteriaEntry&criteriaEntry:timetableInitialised=true&user=&criteriaEntry:year=2021&criteriaEntry:studyPeriod=Semester 2&criteriaEntry:location=Bentley Perth Campus&criteriaEntry:schoolDepartment=0&criteriaEntry:filterUnitCodeOrTitle=&javax.faces.ViewState=-122641214671914646:749242592233144154&javax.faces.source=criteriaEntry:removeAllButton&javax.faces.partial.event=click&javax.faces.partial.execute=criteriaEntry:removeAllButton criteriaEntry&javax.faces.partial.render=criteriaEntry:searchByUnitsDiv&javax.faces.behavior.event=action&javax.faces.partial.ajax=true' \
"""










"""


add multiple units




curl 'http://timetable.student.curtin.edu.au/criteriaEntry.jsf' \
  -H 'Connection: keep-alive' \
  -H 'Pragma: no-cache' \
  -H 'Cache-Control: no-cache' \
  -H 'Faces-Request: partial/ajax' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36' \
  -H 'Content-type: application/x-www-form-urlencoded;charset=UTF-8' \
  -H 'Accept: */*' \
  -H 'Origin: http://timetable.student.curtin.edu.au' \
  -H 'Referer: http://timetable.student.curtin.edu.au/criteriaEntry.jsf' \
  -H 'Accept-Language: en-AU,en;q=0.9' \
  -H 'Cookie: JSESSIONID=917221c0466a80c49049d7856ff2' \
  --data-raw 'criteriaEntry=criteriaEntry&criteriaEntry:timetableInitialised=true&user=&criteriaEntry:year=2021&criteriaEntry:studyPeriod=Semester 2&criteriaEntry:location=Bentley Perth Campus&criteriaEntry:schoolDepartment=0&criteriaEntry:filterUnitCodeOrTitle=&criteriaEntry:allUnits=318509&criteriaEntry:allUnits=321381&criteriaEntry:allUnits=315560&javax.faces.ViewState=-5340187164806647053:3851751676204638174&javax.faces.source=criteriaEntry:addButton&javax.faces.partial.event=click&javax.faces.partial.execute=criteriaEntry:addButton criteriaEntry&javax.faces.partial.render=criteriaEntry:searchByUnitsDiv&javax.faces.behavior.event=action&javax.faces.partial.ajax=true' \
  --compressed \
  --insecure










remove multiple units


curl 'http://timetable.student.curtin.edu.au/criteriaEntry.jsf' \
  -H 'Connection: keep-alive' \
  -H 'Pragma: no-cache' \
  -H 'Cache-Control: no-cache' \
  -H 'Faces-Request: partial/ajax' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36' \
  -H 'Content-type: application/x-www-form-urlencoded;charset=UTF-8' \
  -H 'Accept: */*' \
  -H 'Origin: http://timetable.student.curtin.edu.au' \
  -H 'Referer: http://timetable.student.curtin.edu.au/timetableByUnits.jsf' \
  -H 'Accept-Language: en-AU,en;q=0.9' \
  -H 'Cookie: JSESSIONID=917221c0466a80c49049d7856ff2' \
  --data-raw 'criteriaEntry=criteriaEntry&criteriaEntry:timetableInitialised=true&user=&criteriaEntry:year=2021&criteriaEntry:studyPeriod=Semester 2&criteriaEntry:location=Bentley Perth Campus&criteriaEntry:schoolDepartment=0&criteriaEntry:filterUnitCodeOrTitle=&criteriaEntry:selectedUnits=318509&criteriaEntry:selectedUnits=321381&criteriaEntry:selectedUnits=315560&javax.faces.ViewState=-122641214671914646:749242592233144154&javax.faces.source=criteriaEntry:removeButton&javax.faces.partial.event=click&javax.faces.partial.execute=criteriaEntry:removeButton criteriaEntry&javax.faces.partial.render=criteriaEntry:searchByUnitsDiv&javax.faces.behavior.event=action&javax.faces.partial.ajax=true' \
  --compressed \
  --insecure














clear






curl 'http://timetable.student.curtin.edu.au/criteriaEntry.jsf' \
  -H 'Connection: keep-alive' \
  -H 'Pragma: no-cache' \
  -H 'Cache-Control: no-cache' \
  -H 'Faces-Request: partial/ajax' \
  -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36' \
  -H 'Content-type: application/x-www-form-urlencoded;charset=UTF-8' \
  -H 'Accept: */*' \
  -H 'Origin: http://timetable.student.curtin.edu.au' \
  -H 'Referer: http://timetable.student.curtin.edu.au/timetableByUnits.jsf' \
  -H 'Accept-Language: en-AU,en;q=0.9' \
  -H 'Cookie: JSESSIONID=917221c0466a80c49049d7856ff2' \
  --data-raw 'criteriaEntry=criteriaEntry&criteriaEntry:timetableInitialised=true&user=&criteriaEntry:year=2021&criteriaEntry:studyPeriod=Semester 2&criteriaEntry:location=Bentley Perth Campus&criteriaEntry:schoolDepartment=0&criteriaEntry:filterUnitCodeOrTitle=&javax.faces.ViewState=-122641214671914646:749242592233144154&javax.faces.source=criteriaEntry:removeAllButton&javax.faces.partial.event=click&javax.faces.partial.execute=criteriaEntry:removeAllButton criteriaEntry&javax.faces.partial.render=criteriaEntry:searchByUnitsDiv&javax.faces.behavior.event=action&javax.faces.partial.ajax=true' \
  --compressed \
  --insecure
"""
