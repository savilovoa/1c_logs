# -*- coding: utf-8 -*-

import re
import logging


pattern_0 = r"\{\d{14},\w,\n"
pattern_1 = r'\{\w+,\w+\},\d*,\d*,\d+,\d+,\d+,\w,".*",\d+,\n'
pattern_1_1 = r'\{\w+,\w+\},\d*,\d*,\d+,\d+,\d+,\w,"[^"]*\n'
pattern_2 = r'\{"\w"\},"\w*",\d+,\d+,\d+,\d+,\d+,\n'
pattern_4 = r'\{\d+,\d+,\d+,\d+,\d+\}\n|\{0\}\n'
pattern_5 = r'\},\n|\}'
pattern_b = r'\{|\}|"'

class scan_1c_logs(object):
    def __init__(self, file_name):
        __init__(self)
        self.file_name = file_name
        
    def message_add(mess: str):
        pass
    
    def scan_file(fn_name: str):
        len_figure = 0
        comm = False
        message = ""
        j = 0
        mi = 0
        with open(fn_name, "r", encoding="utf-8") as fp:
            for i, line in enumerate(fp):
                if i > 2:
                    if len_figure == 0:
                        if re.fullmatch(pattern_0, line) != None:                        
                            j += 1
                            message = line[:-1]
                            log_f = 1
                            mi = 1
                    else:
                        if mi == 1:
                            mc = re.findall('"', line)
                            mc_len = len(mc)
                            mc_ch = len(mc) % 2                    
                            if not comm:
                                if mc_ch == 0:
                                    if re.fullmatch(pattern_1, line) != None:
                                        mi = 2
                                        message = message + line[:-1]
                                    elif re.fullmatch(pattern_1_1, line):
                                        comm = True
                                        message = message + line                                
                                    else:
                                        logging.error('Error 1: {} \nMessage: {}'.format(line, message))
                                        break
                                else:
                                    comm = True
                                    message = message + line                            
                            else:
                                mc = re.findall('"', line)
                                mc_len = len(mc)
                                mc_ch = len(mc) % 2
                                if (mc_ch != 0) and(mc_len != 0) : 
                                    if re.fullmatch(r'.*",\d+,\n', line) != None:
                                        comm = False
                                        mi = 2
                                        message = message + line[:-1]
                                    else:
                                        logging.error('Error 1: {} \nMessage: {}'.format(line, message))
                                        break                                
                                elif re.fullmatch(pattern_0, line) == None:
                                    message = message + line
                                else: 
                                    logging.error('Error 1 line (find begin pattern, but close pattern 1 not run): .*",\d,\n: {} \nMessage: {}'.format(line, message))
                                    break                            
                                
                                
                        elif mi == 2:
                            s = line[2]  
                            if s in ["U", "S", "R"]:
                                message = message + line[:-1]
                                mi = 4                                                   
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
                                s = s[:close_start] + '}\n'
                            message = message + s[:-1]                            
                        elif mi == 4:
                            if re.fullmatch(pattern_4, line) != None:
                                message = message + line[:-1]
                                mi = 5
                            else:
                                logging.error('Error 4: {} \nMessage: {}'.format(line, message))
                                break
                        elif mi == 5:
                            if re.fullmatch(pattern_5, line) != None:
                                message = message + line[:-1]
                                len_figure = 0
                                message_add(message)
                                logging.info('{}: {}'.format(j, message))                                                                
                            else:
                                logging.error('Error 5: {} \nMessage: {}'.format(line, message))
                                break
        
    

