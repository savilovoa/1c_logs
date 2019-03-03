# -*- coding: utf-8 -*-

import re
import logging
import configparser
import os
import json
from os import path
import time





pattern_0 = r"\{\d{14},\w,\n"
pattern_1 = r'\{\w+,\w+\},\d*,\d*,\d+,\d+,\d+,\w,".*",\d+,\n'
pattern_1_1 = r'\{\w+,\w+\},\d*,\d*,\d+,\d+,\d+,\w,"[^"]*\n'
pattern_2 = r'\{"\w"\},"\w*",\d+,\d+,\d+,\d+,\d+,\n'
pattern_4 = r'\{\d+,\d+,\d+,\d+,\d+\}\n|\{0\}\n'
pattern_5 = r'\},\n|\}'
pattern_b = r'\{|\}|"'

pattern_lgf_0 = r'\{\d+,"[^"]*",\d+\}'
pattern_lgf_1 = r'\{\d+,\w+-\w+-\w+-\w+-\w+,"[^"]*",\d+\}'
pattern_lgf_2 = r'\{\d+,\d+,\d+\}'

class scan_1c_logs(object):
        
    info = False
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
    sincefilename = "since.dat"
    runloglastpos = True
    sincedata = {}
    logsdir = "../in"
        
    def __init__(self):        
        sett_filename = "logs_1c.conf"
        if os.path.exists(sett_filename):
            self.config = configparser.ConfigParser()
            self.config.read(sett_filename)
            if self.config.has_option("GLOBAL", "runloglastpos"):
                self.runloglastpos = self.config.getboolean("GLOBAL", "runloglastpos")
            if self.config.has_option("GLOBAL", "logsdir"):
                self.logsdir = self.config.get("GLOBAL", "logsdir")
        self.since_load()
        
            
    def since_load(self):
        if os.path.exists(self.sincefilename):
            with open(self.sincefilename, "r") as sincefile:
                js = sincefile.read()
                if js != "":
                    self.sincedata = json.loads(js)
                
    def since_find(self, filename):
        return dict(self.sincedata).setdefault(filename, [])
    
    def since_save(self):
        with open(self.sincefilename, "w") as sincefile:
            json.dump(self.sincedata, sincefile)




    def lgf_add_dict(self, a):
        dict_type = int(a[0])
        if len(a) > 3:
            key = a[3]
        else:
            key = a[2]
        if dict_type == 1:
            self.users[key] = a[2]
            self.users_guid[key] = a[1]
        elif dict_type == 2:
            self.computers[key] = a[1]
        elif dict_type == 3:
            self.appsname[key] = a[1]
        elif dict_type == 4:
            self.events[key] = a[1]
        elif dict_type == 5:
            self.metadata[key] = a[2]
            self.metadata_guid[key] = a[1]
        elif dict_type == 6:
            self.servers[key] = a[1]
        elif dict_type == 7:
            self.ports[key] = a[1]
        elif dict_type == 8:
            self.portsadv[key] = a[1]
    
    def lgf_load(self, filename:str):
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
                                self.lgf_add_dict(re.split(r',"|",|,', line[1:-1]))
                                #print("Ok: ", m)
                            elif re.fullmatch(pattern_lgf_1, line) != None:
                                self.lgf_add_dict(re.split(r',"|",|,', line[1:-1]))
                                #print("Ok: ", m)
                            elif re.fullmatch(pattern_lgf_2, line) != None:
                                self.lgf_add_dict(str(line[1:-1]).split(','))
                                #print("Ok: ", m)
                        
                            else:
                                logging.error('Error load lgf-file {}, line: {}'.format(filename, line))
                                return False                                                                           
                        
        except Exception as ex:
            logging.error('Error load lgf-file {}: {}'.format(filename, str(ex)))
            return False
        
        return True
    
    def message_add(self, mess):
        #print(mess)
        pass
    
    def scan_file(self, fn_name: str):
        
        # разбор строки по полям
        # 1 - it {243391c7248f0,786be},4,2,1,14308,4,I,"",0,
        # 2 - it {243391c7248f0,786be},4,2,1,14308,4,I,"sdfsdfsdfsdfsd...
        # 3 - it {"U"},"",1,1,0,2,0,
        # 4 - it {"S","Обработки.ЖурналДокументовВнутреннегоТовародвижения.СформироватьГиперссылкуКОформлениюФоновоеЗадание"},"",1,1,0,716,0,
        # 5 - it {"R",971:811200505680a44e11e93552811c5926},"Сборка (разборка) товаров 0000-001512 от 21.02.2019 0:00:07",1,1,0,715,0,
        # 6 - it "",1,9,0,107,0,
        def line_to_arr(m, l, matchtype, lenarr, hardcheck = True):
            i = 0
            if matchtype != 6:
                a = str(l).split("}")
                if matchtype in [1,2]:
                    a1 = str(a[0]).split(",")
                    for d in a1:
                        mess.append(d)
                        i += 1
                else:
                    mess.append(a[0])
                    i += 1
            else:
                a = ['', l]
            # here is the rest without the commas, dismantle what is left (тут остаток без кавычки, разбираем что осталось)
            if matchtype in[2]:
                a1 = str(a[1][1:]).split(",")
                for d in a1:
                    mess.append(d)                                            
                    i += 1
            # here it is necessary to cut between the outermost commas
            elif matchtype in [1,3,4,5,6]:
                # ищем первую кавычку
                s = a[1][1:]
                p1 = str(s).find('"')
                # find end commas
                p2 = len(s) - str(s[::-1]).find('"') - 1                
                if matchtype == 1:
                    # разбираем по полям
                    a3 = str(s[:p1-1]).split(",")
                    for d in a3:
                        mess.append(d)                                            
                        i += 1               
                # добавляем комментарий от первой кавычки до последней
                mess.append(s[p1+1:p2]) 
                i += 1
                a3 = str(s[p2+2:]).split(",")
                for d in a3:
                    mess.append(d)                                            
                    i += 1               
                    
                
            if i == lenarr:
                return True
            elif (i > lenarr) and (not hardcheck):
                return True
            else:
                logging.error('Error 1 - неполный массив данных {}, а ожидалось {}: {} \n'.format(i, lenarr, l))
                return False
            
        if self.runloglastpos:
            fn_name0 = path.basename(fn_name)
            fn_name_2_since = path.splitext(fn_name0)[0]
            statbuf = os.stat(fn_name)
            file_ts_mod = statbuf.st_mtime
            f_since = self.since_find(fn_name_2_since)

            if f_since != []:
                line_begin = f_since[0]
                stat_ts_mod = f_since[1]
                if stat_ts_mod >= file_ts_mod:
                    return True
            else:
                line_begin = 2
            
            
            
            
        else:
            line_begin = 2
        res = False
        len_figure = 0
        comm = False
        message = ""
        mess_multiline = ""
        mess = []
        j = 0
        mi = 0
        try:
            # mess - структура 
            # 0    - дата 14 цифр, 
            # 1    - транзакция "N" – "Отсутствует", "U" – "Зафиксирована", "R" – "Не завершена" и "C" – "Отменена";
            # 2, 3    - Транзакция в формате записи из двух элементов преобразованных в шестнадцатеричное число – первый – число секунд с 01.01.0001 00:00:00 умноженное на 10000, второй – номер транзакции;
            # 4    - пользователь
            # 5    - Компьютер – указывается номер в массиве компьютеров;
            # 6    - Приложение – указывается номер в массиве приложений;
            # 7    - Соединение – номер соединения;
            # 8    - Событие – указывается номер в массиве событий;
            # 9) Важность – может принимать четыре значения – "I" – "Информация", "E" – "Ошибки", "W" – "Предупреждения" и "N" – "Примечания";
            # 10) Комментарий – любой текст в кавычках;
            # 11) Метаданные – указывается номер в массиве метаданных;
            # 12) Данные – самый хитрый элемент, содержащий вложенную запись;
            # 13) Представление данных – текст в кавычках;
            # 14) Сервер – указывается номер в массиве серверов;
            # 15) Основной порт – указывается номер в массиве основных портов;
            # 16) Вспомогательный порт – указывается номер в массиве вспомогательных портов;
            # 17) Сеанс – номер сеанса;
            # 18) moremetadata
            with open(fn_name, "r", encoding="utf-8") as fp:
                for i, line in enumerate(fp):
                    if i > line_begin:
                        if len_figure == 0:
                            if re.fullmatch(pattern_0, line) != None:                        
                                j += 1
                                message = line[:-1]
                                len_figure = 1
                                mi = 1
                                a = str(line[1:-1]).split(",")
                                mess.append(a[0])
                                mess.append(a[1])
                        else:
                            if mi == 1:
                                mc = re.findall('"', line)
                                mc_len = len(mc)
                                mc_ch = len(mc) % 2                    
                                if not comm:
                                    if mc_ch == 0:
                                        # в одну строчку
                                        if re.fullmatch(pattern_1, line) != None:
                                            mi = 2
                                            message = message + line[:-1]
                                            if mc_len== 6:
                                                pass
                                            if not line_to_arr(mess, line[1:-2], 1, 10):
                                                res = False
                                                break
                                        # в несколько строчек        
                                        elif re.fullmatch(pattern_1_1, line):
                                            comm = True
                                            message = message + line                                
                                            mess_multiline = line                                            
                                            p1 = str(line[1:]).find('"')                                        
                                            comm_multiline = line[p1+1:]                                        
                                            if not line_to_arr(mess, line[1:p1], 2, 8):                                            
                                                res = False
                                                break
                                        else:
                                            logging.error('Error 1: {} \nMessage: {}'.format(line, message))
                                            res = False
                                            break
                                    else:
                                        comm = True
                                        message = message + line                            
                                        mess_multiline = line
                                        p1 = str(line[1:]).find('"')                                        
                                        comm_multiline = line[p1+1:]                                        
                                        if not line_to_arr(mess, line[1:p1], 2, 8):                                            
                                            res = False
                                            break
                                    
                                else:
                                    mc = re.findall('"', line)
                                    mc_len = len(mc)
                                    mc_ch = len(mc) % 2
                                    if (mc_ch != 0) and(mc_len != 0) : 
                                        if re.fullmatch(r'.*",\d+,\n', line) != None:
                                            comm = False
                                            mi = 2
                                            message = message + line[:-1]                                            
                                            p2 = len(line) - str(line[::-1]).find('"') - 1
                                            mess.append(comm_multiline + line[:p2-1])
                                            mess.append(line[p2+2:-2])
                                        else:
                                            logging.error('Error 1: {} \nMessage: {}'.format(line, message))
                                            res = False
                                            break                                
                                    elif re.fullmatch(pattern_0, line) == None:
                                        message = message + line
                                        mess_multiline = mess_multiline + line
                                        comm_multiline = comm_multiline + line
                                    else: 
                                        logging.error('Error 1 line (find begin pattern, but close pattern 1 not run): .*",\n: {} \nMessage: {}'.format(line, message))
                                        res = False
                                        break                            
                                    
                                    
                            elif mi == 2:
                                s = line[2]  
                                if s in ["U", "S", "R"]:
                                    message = message + line[:-1]
                                    mi = 4               
                                    if s == "U":
                                        if not line_to_arr(mess, line[1:-2], 3, 7):
                                            res = False
                                            break
                                    elif s == "S":
                                        if not line_to_arr(mess, line[1:-2], 4, 7):
                                            res = False
                                            break                         
                                    elif s == "R":
                                        if not line_to_arr(mess, line[1:-2], 5, 7):
                                            res = False
                                            break                         
                                        
                                elif line[2] == "P":
                                    len_figure = 2
                                    mi = 3
                                    comm = False
                                    l = line[:3]                        
                                    for a in line[3:]:
                                        if a == '}':
                                            len_figure = 1
                                            mi = 4
                                            l = l + a
                                        elif a == '{':
                                            len_figure += 1
                                            l = l + '['
                                        else:
                                            l = l + a
                                    message = message + l[:-1]
                                    mess_multiline = l
                                    
                            elif mi == 3:
                                l = "" 
                                for m in re.finditer(pattern_b, line):
                                    a = m.group()
                                    if a == '}':
                                        if not comm: 
                                            len_figure -= 1
                                            if len_figure == 1:
                                                mi = 4
                                                close_start = m.start()                                                   
                                                break
                                    elif a == '{':
                                        if not comm:
                                            len_figure += 1
                                    elif a == '"':
                                        comm = not comm
                                               
                                s  = re.sub(r'\{', "[", line)
                                s = re.sub(r'\}', "]", s)
                                if mi == 4:                                    
                                    mess.append(mess_multiline[1:])
                                    if not line_to_arr(mess, s[close_start+1:-2], 6, 6, False):
                                        res = False
                                        break                                    
                                message = message + s[:-1]                
                                
                            elif mi == 4:
                                if re.fullmatch(pattern_4, line) != None:
                                    message = message + line[:-1]
                                    mi = 5                                    
                                else:
                                    logging.error('Error 4: {} \nMessage: {}'.format(line, message))
                                    res = False
                                    break
                            elif mi == 5:
                                if re.fullmatch(pattern_5, line) != None:
                                    message = message + line[:-1]
                                    len_figure = 0
                                    self.message_add(mess)
                                    mess.clear()
                                    if self.runloglastpos:
                                        self.sincedata[fn_name_2_since] = [i, file_ts_mod] 
                                    res = True
                                    if self.info:
                                        logging.info('{}: {}'.format(j, message))                                                                
                                else:
                                    logging.error('Error 5: {} \nMessage: {}'.format(line, message))
                                    res = False
                                    break
                        
        except Exception as ex:
            logging.error(str(ex))    
            res = False
        finally:
            if self.runloglastpos and j > 0:
                self.since_save()
        return res
            
    def loads(self, logsdir="", rescan = False):
        if logsdir != "":
            self.logsdir = logsdir
        try:
            while True:
                print("Start scaning {}".format(self.logsdir))
                for fn_name in os.listdir(self.logsdir):
                #print(os.path.join(self.logsdir, fn_name))
                    if fn_name.endswith(".lgp"):
                        self.scan_file(os.path.join(self.logsdir, fn_name))
                if not rescan:
                    break
                time.sleep(5)

        except Exception as ex:
            logging.error(str(ex))
        
    
