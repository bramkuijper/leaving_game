#!/usr/bin/env python3
import numpy as np
import datetime

exe="./iterate_popgen.py"

date = datetime.datetime.now()
base_name = "sim_popgen_leaving_" +\
        f"{date:%d}_{date:%m}_{date:%Y}_{date:%H}{date:%M}{date:%S}"

l1 = list(np.linspace(start=0.01,stop=0.99,num=100))
l2 = list(np.linspace(start=0.01,stop=0.99,num=100))

m = [ 1, 10, 30, 50 ]

valone = [0.5]
vstay = [0.9]
vgroup = [1.0]

double = [1]

ctr = 1
for l1i in l1:
    for l2i in l2:
        for mi in m:
            for valone_i in valone:
                for vstay_i in vstay:
                    for vgroup_i in vgroup:
                        for double_i in double:
                            print(f"{exe} {l1i} {l2i} {mi} {valone_i} {vgroup_i} {vstay_i} {double_i} {base_name}_{ctr}.csv")
                            ctr += 1
