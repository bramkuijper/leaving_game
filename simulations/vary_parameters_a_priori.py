#!/usr/bin/env python3

import numpy as np
import datetime

pr_leave_early_init = list(np.linspace(start=0.01,stop=0.99,num=50))
pr_stay_init = list(np.linspace(start=0.01,stop=0.99,num=50))

v_stay = [0.5,0.1,0.9]
v_group = 1.0
v_alone = [0.5,0.9]

n_per_deme = [2,11,51];

date = datetime.datetime.now()
base_name = "sim_leaving_game_" +\
        f"{date:%d}_{date:%m}_{date:%Y}_{date:%H}{date:%M}{date:%S}"

ctr=0

type = "a_priori"
exe = {"a_priori" : "./leaving_game_a_priori.exe"}

for pr_leave_early_init_i in pr_leave_early_init:
    for pr_stay_init_i in pr_stay_init:
        for v_stay_i in v_stay:
            for v_alone_i in v_alone:
                for n_per_deme_i in n_per_deme:
                    ctr+=1
                    print(f"{exe[type]} " + \
                            f"{v_stay_i} " + \
                            f"{v_group} " + \
                            f"{v_alone_i} " + \
                            f"{pr_leave_early_init_i} " + \
                            f"{pr_stay_init_i} " + \
                            f"{n_per_deme_i} " + \
                            base_name + f"{ctr}"
                        ) 


                
