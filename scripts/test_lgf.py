# -*- coding: utf-8 -*-
import re

filename = "../in/1cv8.lgf"

users = {}      #1
users_guid = {}
computers = {}  #2
appsname = {}   #3
events = {}     #4
metadata = {}   #5
metadata_guid = {}
servers = {}    #6
ports = {}      #7
portsadv = {}   #8

pattern_lgf_0 = r'\{\d+,"[^"]*",\d+\}'
pattern_lgf_1 = r'\{\d+,\w+-\w+-\w+-\w+-\w+,"[^"]*",\d+\}'
pattern_lgf_2 = r'\{\d+,\d+,\d+\}'

def add_item(a):
    dict_type = int(a[0])
    if len(a) > 3:
        key = a[3]
    else:
        key = a[2]
    if dict_type == 1:
        users[key] = a[2]
        users_guid[key] = a[1]
    elif dict_type == 2:
        computers[key] = a[1]
    elif dict_type == 3:
        appsname[key] = a[1]
    elif dict_type == 4:
        events[key] = a[1]
    elif dict_type == 5:
        metadata[key] = a[2]
        metadata_guid[key] = a[1]
    elif dict_type == 6:
        servers[key] = a[1]
    elif dict_type == 7:
        ports[key] = a[1]
    elif dict_type == 8:
        portsadv[key] = a[1]
                


try:
    with open(filename, "r", encoding="utf-8") as fp:
        for i, line in enumerate(fp):
            if i > 1:
                # убираем конец строки
                if line[len(line)-1] == '\n':
                    line = line[:-1]
                # проверка на четное кол-во скобок
                if len(re.findall(r'\{|\}', line)) % 2 == 0:
                    # убираем запятую
                    if line[len(line)-1] == ',':
                        line = line[:-1]                    
                    if re.fullmatch(pattern_lgf_0, line) != None:
                        add_item(re.split(r',"|",|,', line[1:-1]))
                        #print("Ok: ", m)
                    elif re.fullmatch(pattern_lgf_1, line) != None:
                        add_item(re.split(r',"|",|,', line[1:-1]))
                        #print("Ok: ", m)
                    elif re.fullmatch(pattern_lgf_2, line) != None:
                        add_item(str(line[1:-1]).split(','))
                        #print("Ok: ", m)
                
                    else:
                        print(line)
                    
                
                
except Exception as ex:
    print(str(ex))
finally:
    print(users)
    print(users_guid)
    