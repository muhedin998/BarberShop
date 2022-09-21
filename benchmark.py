from __future__ import print_function
from datetime import date, datetime
import turtle
from xml.etree.ElementTree import TreeBuilder

start = datetime.now()
br = 0 

while True:
    br += 1
    print(br)
    if br ==1000000:
        end = datetime.now()
        rez = end - start
        print(f"time elapsed: {rez}")
        break