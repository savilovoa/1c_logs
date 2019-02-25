#!/bin/bash

pattern_0="\{\d{14},\w,"
pattern_1='\{\w+,\w+\},\d*,\d*,\d+,\d+,\d+,\w,".*",\d+,\n'
pattern_1_1='\{\w+,\w+\},\d*,\d*,\d+,\d+,\d+,\w,"[^"]*\n'
pattern_2='\{"\w"\},"\w*",\d+,\d+,\d+,\d+,\d+,\n'
pattern_4='\{\d+,\d+,\d+,\d+,\d+\}\n|\{0\}\n'
pattern_5='\},\n|\}\n'
pattern_b='\{|\}|"'
log_f=0
message=""
j=0
save_info=False
fn_name="in/2019022000099.lgp"
i=0
ii=1
while read LINE; do
  i=$(( ${i} + 1 ))
  if [ $i -gt 2 ]
  then
    if [ $log_f == 0 ]
    then
      echo $LINE | awk $pattern_0
    fi
    #echo $i "$LINE"
  fi

done < $fn_name
