# -*- coding: utf-8 -*-

import re

def cleansing01(st):

    st=re.sub(r"<[^>]*?>","",str(st))
    st=re.sub(r"[\[\'\] ]","",str(st))
    st=re.sub(r"[\(\'\) ]","",str(st))
    st=re.sub(r"\n","",str(st))
    st=re.sub(r" ","",str(st))
    st=re.sub(r" ","",str(st))

    return st


def cleansing02(st):

    st=re.sub(r"<[^>]*?>","",str(st))
    st=re.sub(r" ",",",str(st))
    st=re.sub(r"\xa0",",",str(st))
    st=re.sub(r"\n",",",str(st))

    return st
