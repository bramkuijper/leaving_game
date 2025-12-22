#!/usr/bin/env python3
import numpy as np
import datetime

exe="./iterate_popgen.py"

date = datetime.datetime.now()
base_name = "sim_popgen_leaving_" +\
        f"{date:%d}_{date:%m}_{date:%Y}_{date:%H}{date:%M}{date:%S}"

l1 = list(np.linspace(start=0.01,stop=0.01,num=100))

m = [ 1, 10, 30, 50 ]

ctr = 1
for l1i in l1:
    for mi in m:
        print(f"{exe} {l1i} {mi} > {base_name}_{ctr}.csv")
        ctr += 1
