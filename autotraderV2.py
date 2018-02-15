import urllib
import urllib.request
from bs4 import BeautifulSoup
from http.cookiejar import CookieJar
import pymysql
import sys
import threading

def connection_details(path):

     req = urllib.request.Request(path, headers={'User-Agent': 'Mozilla/5.0'})
     global cj; cj = CookieJar()
     global opener; opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
     global html; html = opener.open(req).read()
     global bsObj; bsObj = BeautifulSoup(html, 'lxml')

def gather_links():

    cur_list = []
    link_list = bsObj.findAll('div',{'class':'at_infoArea'})
    for link in link_list:
        if 'href' in link.a.attrs:
            cur_list.append(link.a.attrs['href'])
    return cur_list

def gather_details(path):

    req = urllib.request.Request(path, headers={'User-Agent': 'Mozilla/5.0'})

    veh_attr1 = []
    veh_attr2 = []
    counter = 0

    file = opener.open(req)
    lines = file.readlines()

    for line in lines:
        y = line.split()
        for veh in veh_attr:
            if veh in y: veh_attr1.append(y)
            if len(veh_attr1)==len(veh_attr): break
        else:
            continue
        break

    if len(veh_attr1[1]) == 3:
        veh_attr1[1][1] = veh_attr1[1][1] + b' ' + veh_attr1[1][2]
        del veh_attr1[1][2]
    if len(veh_attr1[1]) == 4:
        veh_attr1[1][1] = veh_attr1[1][1] + b' ' + veh_attr1[1][2] + b' ' + veh_attr1[1][3]
        del veh_attr1[1][2]; del veh_attr1[1][2]


    for data in veh_attr1:
        for sub_data in data:
            if counter % 2 != 0:
                text_format = sub_data.decode('utf8').replace(',','').replace(':','').replace("'",'')
                text_format = text_format.replace("'",'').strip()
                veh_attr2.append(text_format)
                counter += 1
            else:
                counter += 1
                continue

    print(veh_attr2)
    return veh_attr2


def SQL(sql_info):

    SQL_update = """INSERT INTO autotrader(make, model, year,
                price, used, addID, province) VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s') """ % tuple(sql_info)

    try:
        cursor = conn.cursor()
        cursor.execute(SQL_update)
        conn.commit()
    except:
        conn.rollback()

def new_thread(updated_path):
    sql_info = gather_details(updated_path)
    SQL(sql_info)


conn = pymysql.connect(user='root',host='localhost', database='test')
veh_attr = [b"'make':", b"'model':", b"'year':", b"'price':", b"'condition':", b"'adID':", b"'province':"]
main_path = 'http://www.autotrader.ca/cars/?prx=-1&loc=M9C+5J1&sts=New-Used&hprc=True&wcp=True&inMarket=basicSearch'
path_counter = 0


while True:

    connection_details(main_path + '&rcs=' + str(path_counter))
    update_path = gather_links()

    if len(update_path) < 1:
        conn.close()
        break

    for update in range(len(update_path)):
        thread = threading.Thread(target = new_thread, args = (update_path[update],))
        thread.start()


    path_counter += 15

sys.exit()
