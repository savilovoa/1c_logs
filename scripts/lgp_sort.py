# -*- coding: utf-8 -*-

from datetime import datetime
import re

block_f = 0
t_f = False

pattern_0 = r"\{\d{14},\w,\n"
pattern_1 = r'\{\w+,\w+\},\d*,\d*,\d+,\d+,\d+,\w,".*",\d+,\n'
pattern_1_1 = r'\{\w+,\w+\},\d*,\d*,\d+,\d+,\d+,\w,"[^"]*\n'
pattern_2 = r'\{"\w"\},"\w*",\d+,\d+,\d+,\d+,\d+,\n'
pattern_4 = r'\{\d+,\d+,\d+,\d+,\d+\}\n|\{0\}\n'
pattern_5 = r'\},\n|\}\n'
pattern_b = r'\{|\}|"'
log_f = 0
message = ""
j = 0
save_info = False
fn_name = "in/20190221000000.lgp"
err = open("error", "w")
log = open("info.txt", "w")
m_i = [0,0,0,0]
comm = False
with open(fn_name, "r", encoding="utf-8") as fp:
    for i, line in enumerate(fp):
        #print(i, line)
        if i > 2:
            if log_f == 0:
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
                                print ('Error 1 line: ' + line)
                                err.write('Error 1 line: ' + line)
                                err.write(message + line)
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
                                m_i[0] = m_i[0] + 1
                                if m_i[0] < 5:
                                    save_info = True
                            else:
                                err.write('Error 1 line: ' + line)
                                err.write(message + line)
                                break                                
                        elif re.fullmatch(pattern_0, line) == None:
                            message = message + line
                        else: 
                            err.write('Error 1 line (find begin pattern, but close pattern 1 not run): '+ r'.*",\d,\n' + line)
                            err.write(message + line)
                            break                            
                        
                        
                elif mi == 2:
                    s = line[2]  
                    if s in ["U", "S", "R"]:
                        message = message + line[:-1]
                        mi = 4
                        if s == "S":
                            m_i[1] = m_i[1] + 1
                            if m_i[1] < 5:
                                save_info = True
                        elif s == "R":
                            m_i[3] = m_i[3] + 1
                            if m_i[3] < 5:
                                save_info = True
                                                    
                    elif line[2] == "P":
                        log_f = 2
                        mi = 3
                        comm = False
                        l = line[:3]                        
                        for a in line[3:]:
                            if a == '}':
                                log_f = 1
                                mi = 4
                                l = l + a
                            elif a == '{':
                                log_f += 1
                                l = l + '['
                            else:
                                l = l + a
                        message = message + l[:-1]
                        #print (log_f, l)
                elif mi == 3:
                    l = "" 
                    for m in re.finditer(pattern_b, line):
                        a = m.group()
                        if a == '}':
                            if not comm: 
                                log_f -= 1
                                if log_f == 1:
                                    mi = 4
                                    close_start = m.start()
                                    break
                        elif a == '{':
                            if not comm:
                                log_f += 1
                        elif a == '"':
                            comm = not comm
                                   
                    s  = re.sub(r'\{', "[", line)
                    s = re.sub(r'\}', "]", s)
                    if mi == 4:
                        s = s[:close_start] + '}\n'
                    message = message + s[:-1]
                    m_i[2] = m_i[2] + 1
                    if m_i[2] < 5:
                        save_info = True
                    #print (log_f, line[:-1])
                elif mi == 4:
                    if re.fullmatch(pattern_4, line) != None:
                        message = message + line[:-1]
                        mi = 5
                    else:
                        print ("Error line 4: " + line)
                        err.write('Error 4 line: ' + line)
                        err.write(message + line)
                        break
                elif mi == 5:
                    if re.fullmatch(pattern_5, line) != None:
                        message = message + line[:-1]
                        log_f = 0
                        if save_info:
                            save_info = False
                            log.write(message + '\n')
                        print ("{}: {}".format(j, message))
                    else:
                        print ("Error line 5: " + line)
                        err.write('Error 5 line: ' + line)
                        err.write(message + line)
                        break
err.close()
log.close()
                    
                                
                        
                    
                    
                
                
                
                

#s = "{20190221151624,N"
#i = re.fullmatch(r"\{\d{14},\w", s)
print(i)