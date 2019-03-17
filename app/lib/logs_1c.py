# -*- coding: utf-8 -*-

import re
import logging
from logging.handlers import RotatingFileHandler
import configparser
import os
import json
from os import path
import time

# настройка логгирования
logger = logging.getLogger("logs_1c")
logger.setLevel(logging.INFO)

formatter_err = logging.Formatter("[%(asctime)s] [LINE:%(lineno)d] %(levelname)s - %(message)s", datefmt = '%Y-%m-%d %H:%M:%S')
formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s", datefmt = '%Y-%m-%d %H:%M:%S')
# create console handler and set level to info
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)

handler.setFormatter(formatter)
logger.addHandler(handler)

sett_filename = "logs_1c.conf"
if os.path.exists(os.path.join("/usr/local/etc/1c_logs", sett_filename)):
    sett_filename = os.path.join("/usr/local/etc/1c_logs", "logs_1c.conf")
if os.path.exists(sett_filename):
    config = configparser.ConfigParser()
    config.read(sett_filename)
else:
    raise RuntimeError("Not find file conf {}".format(sett_filename))

if config.has_option("GLOBAL", "dirlog"):
    dirlog = config.get("GLOBAL", "dirlog")
    log_filename = os.path.join(dirlog, 'logs_1c.log')
    logerr_filename = os.path.join(dirlog, 'logs_1c_err.log')
else:
    log_filename = "logs_1c.log"
    logerr_filename = 'logs_1c_err.log'


# create error file handler and set level to error
handler2 = RotatingFileHandler(logerr_filename, mode = 'a', maxBytes = 10485760, backupCount = 10, encoding = None, delay = 0)
handler2.setLevel(logging.ERROR)
handler2.setFormatter(formatter_err)
logger.addHandler(handler2)

handler3 = RotatingFileHandler(log_filename, mode = 'a', maxBytes = 10485760, backupCount = 10, encoding = None, delay = 0)
if config.has_option("GLOBAL", "debug"):
    if config.getboolean("GLOBAL", "debug"):
        handler3.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    else:
        handler3.setLevel(logging.INFO)
else:
    handler3.setLevel(logging.INFO)
handler3.setFormatter(formatter)
logger.addHandler(handler3)

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
    dbname = ""
    logsdir = ""
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
    runloglastpos = True
    sincedata = {}
    lgf_loaded = False


    def __init__(self, dbname, logsdir):
        self.dbname = dbname
        self.logsdir = logsdir

        if self.dbname == "":
            raise RuntimeError("Empty dbname (indexname_default)")

        if config.has_option("LOGS", "runloglastpos"):
            self.runloglastpos = config.getboolean("GLOBAL", "runloglastpos")

        if config.has_option("LOGS", "dirsince"):
            self.sincefilename = os.path.join(config.get("GLOBAL", "dirsince"), dbname + ".since")
        else:
            self.sincefilename = dbname + ".since"

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



    #  добавление новой записи в словарь
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

    # загрузка словаря данных
    def lgf_load(self, filename):
        try:
            statbuf = os.stat(filename)
            file_ts_mod = statbuf.st_mtime
            f_since = self.since_find("1cv8")
            if f_since != []:
                stat_ts_mod = f_since[1]
                if self.lgf_loaded  and (stat_ts_mod >= file_ts_mod):
                    return True
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
                            elif re.fullmatch(pattern_lgf_1, line) != None:
                                self.lgf_add_dict(re.split(r',"|",|,', line[1:-1]))
                            elif re.fullmatch(pattern_lgf_2, line) != None:
                                self.lgf_add_dict(str(line[1:-1]).split(','))

                            else:
                                logger.error('Error load lgf-file {}, line: {}'.format(filename, line))
                                return False

        except Exception:
            logger.error('Error load lgf-file {}'.format(filename), exc_info=True)
            return False
        self.sincedata["1cv8"] = [0, file_ts_mod]
        self.since_save
        self.lgf_loaded = True
        logger.info("{} Load {}".format(self.dbname, filename))
        return True

    def message_add(self, rec_id, mess):
        logger.debug("{} {} {}".format(self.dbname, rec_id, message))


    def scan_file(self, fn_name):

        # разбор строки по полям
        # 1 - it {243391c7248f0,786be},4,2,1,14308,4,I,"",0,
        # 2 - it {243391c7248f0,786be},4,2,1,14308,4,I,"sdfsdfsdfsdfsd...
        # 3 - it {"U"},"",1,1,0,2,0,
        # 4 - it {"S","Обработки.ЖурналДокументовВнутреннегоТовародвижения.СформироватьГиперссылкуКОформлениюФоновоеЗадание"},"",1,1,0,716,0,
        # 5 - it {"R",971:811200505680a44e11e93552811c5926},"Сборка (разборка) товаров 0000-001512 от 21.02.2019 0:00:07",1,1,0,715,0,
        # 6 - it "",1,9,0,107,0,
        # 7 - it {"N",5660},"",1,2,0,248,0,
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
                logger.error('Error 1 - неполный массив данных {}, а ожидалось {}: {} \n'.format(i, lenarr, l))
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
                #logger.info("start check file: {}. save mod {}, file mod  {}".format(fn_name0, stat_ts_mod, file_ts_mod))
                if stat_ts_mod >= file_ts_mod:
                    return True
            else:
                line_begin = 2

        else:
            line_begin = 2
        logger.info("{} start check file: {}. Position {}".format(self.dbname, fn_name0, line_begin))
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
                                            logger.error('{} Error 1: {} \nMessage: {}'.format(self.dbname, line, message))
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
                                            logger.error('{} Error 1: {} \nMessage: {}'.format(self.dbname, line, message))
                                            res = False
                                            break
                                    elif re.fullmatch(pattern_0, line) == None:
                                        message = message + line
                                        mess_multiline = mess_multiline + line
                                        comm_multiline = comm_multiline + line
                                    else:
                                        logger.error('{} Error 1 line (find begin pattern, but close pattern 1 not run): .*",\n: {} \nMessage: {}'.format(self.dbname, line, message))
                                        res = False
                                        break


                            elif mi == 2:
                                s = line[2]
                                if s in ["U", "S", "R", "N", "D"]:
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
                                    elif s == "N":
                                        if not line_to_arr(mess, line[1:-2], 5, 7):
                                            res = False
                                            break
                                    elif s == "D":
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
                                else:
                                    raise RuntimeError("{} Unknown type {} - expect [U,S,R,P,N,D]".format(self.dbname, line[2]))


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
                                mess_multiline = mess_multiline + s

                            elif mi == 4:
                                if re.fullmatch(pattern_4, line) != None:
                                    message = message + line[:-1]
                                    mi = 5
                                else:
                                    logger.error('{} Error 4: {} \nMessage: {}'.format(self.dbname, line, message))
                                    res = False
                                    break
                            elif mi == 5:
                                if re.fullmatch(pattern_5, line) != None:
                                    message = message + line[:-1]
                                    len_figure = 0
                                    self.message_add("{}_{}".format(fn_name_2_since, i), mess)
                                    mess.clear()
                                    if self.runloglastpos:
                                        self.sincedata[fn_name_2_since] = [i, file_ts_mod]
                                    res = True
                                    logger.debug('{} {}: {}'.format(self.dbname, j, message))
                                else:
                                    logger.error('{} Error 5: {} \nMessage: {}'.format(self.dbname, line, message))
                                    res = False
                                    break

        except Exception:
            logger.error(str(Exception))
            logger.exception()
            res = False
        finally:
            if not res:
                f_since = self.since_find(fn_name_2_since)
                if i > f_since[0]:
                    self.sincedata[fn_name_2_since] = [f_since[0], 0.0]
                else:
                    self.sincedata[fn_name_2_since] = [f_since[0], file_ts_mod]
                    res = True
            self.since_save()
            if self.runloglastpos and j > 0:
                logger.info("{} Load {}, current line {}".format(self.dbname, fn_name, i))
        return res

    # Сканирование каталога с файлами логгирования
    def scandirs(self):
        try:
            res = True
            logger.info("Start scaning {}".format(self.logsdir))
            
            # Ищем словарь данных
            for fn_name in os.listdir(logsdir):
                if fn_name.endswith(".lgf"):
                    self.lgf_load(os.path.join(self.logsdir, fn_name))
            # Ищем логи
            for fn_name in os.listdir(name):
                if fn_name.endswith(".lgp"):
                    if not self.scan_file(os.path.join(self.logsdir, fn_name)):
                        res = False
                    
            
        except Exception:
            logger.error("{} Error scan files".format(self.dbname), exc_info=True)
        finally:
            return res


class multilogs(object):
    logsdir = ""
    rescan = False
    rescan_sleep = 5
    debug = False
    multidb = False
    logs = []
    dbname = ""

    def __init__(self):
        if config.has_option("GLOBAL", "dirdata"):
            self.logsdir = config.get("GLOBAL", "dirdata")
        if config.has_option("GLOBAL", "rescan"):
            self.rescan = config.get("GLOBAL", "rescan")
        if config.has_option("GLOBAL", "rescan_sleep"):
            self.rescan_sleep = config.getint("GLOBAL", "rescan_sleep")
        if config.has_option("GLOBAL", "multidb"):
            self.multidb = config.getboolean("GLOBAL", "multidb")
        if config.has_option("GLOBAL", "indexname_default"):
            self.dbname = config.get("GLOBAL", "indexname_default")

        if not self.multidb and self.dbname == "":
            raise RuntimeError("Not indexname_default in conf for mode MULTIDB")

    # Функция добавления DB логгирования
    def logs_add(self, dbname, dirname):
        pass

    # ФОРМИРОВАНИЕ списка объектов логгирования
    def logs_build(self):
        if self.multidb:
            for f in os.listdir(self.logsdir):
                if os.path.isdir(os.path.join(self.logsdir, f)):
                    s = os.path.join(self.logsdir, f + "/1Cv8Log")
                    if os.path.exists(s):
                        self.logs_add(f, s)
        else:
            self.logs_add(self.dbname, self.logsdir)
