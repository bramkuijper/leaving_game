#!/usr/bin/env python3
import sys
import pandas as pd
import numpy as np

import warnings


warnings.filterwarnings('error', category=FutureWarning)

class LeavingGame:

    def __init__(self, parameters):

        self.parameters  = parameters
        
    def clamp(self, val, min, max):

        if val < min:
            return(min)

        if val > max:
            return(max)

        return(val)

    def run(self):

        l1 = self.parameters["l1_init"]
        l2 = self.parameters["l2_init"]

        for time in range(0, self.parameters["max_time"]):
            
            mutant_increment = [ 
                                [ self.parameters["mutant_size"], 0 ],
                                [ -self.parameters["mutant_size"], 0],
                                [ 0, self.parameters["mutant_size"]],
                                [ 0, -self.parameters["mutant_size"]]
                                ]

            invasion_genotype_wins = None

            invasion_outcomes_df = pd.DataFrame(
                    {
                        "l1l2" : [ 0.0 for i in range(0,4) ],
                        "L1l2" : [ 0.0 for i in range(0,4) ],
                        "l1L2" : [ 0.0 for i in range(0,4) ],
                        "L1L2" : [ 0.0 for i in range(0,4) ],
                        "maxt" : [ 0 for i in range(0,4) ],
                        "invasion_type" : [ 0 for i in range(0,4) ]
                    }
            )

            for invasion_type in list(range(0,4)):

                g = [ 0.0, 0.0, 0.0, 0.0 ]
                gtplus1 = [ 0.0, 0.0, 0.0, 0.0 ]

                # initial frequencies of each of the four genotypes
                g[0] = (1.0 - self.parameters["mutant_start_frequency"]) * \
                           (1.0 - self.parameters["mutant_start_frequency"]);

                g[1] = (1.0 - self.parameters["mutant_start_frequency"]) * \
                           self.parameters["mutant_start_frequency"]

                g[2] = (1.0 - self.parameters["mutant_start_frequency"]) * \
                           self.parameters["mutant_start_frequency"]

                g[3] = self.parameters["mutant_start_frequency"] * \
                                self.parameters["mutant_start_frequency"]

                # phenotypes for this type of mutant
                l1 = l1
                l2 = l2
                L1 = self.clamp(l1 + mutant_increment[invasion_type][0],0.0,1.0)
                L2 = self.clamp(l2 + mutant_increment[invasion_type][1],0.0,1.0)



                for invasion_time in range(0, self.parameters["max_invasion_time"]):

                    avg_l1 = (g[0] + g[2]) * l1
                    avg_L1 = (g[1] + g[3]) * L1
                    avg_l2 = (g[0] + g[1]) * l2
                    avg_L2 = (g[2] + g[3]) * L2

#                    gtot = 0.0
#                    for g_idx in range(0,4):
#                        gtot += g[g_idx]
#
#                    if not abs(gtot - 1.0) <= 10^(-5):
#                        print(abs(gtot - 1.0))
#                        raise AssertionError("g does not sum to 1,  but to ",str(gtot))
                        
                    wearly = ((1.0 - (avg_l1 + avg_L1))**self.parameters["m"])\
                            * self.parameters["valone"]\
                            +(1.0 - (1.0 - (avg_l1 + avg_L1))**self.parameters["m"])\
                            * self.parameters["vgroup"]

                    wlate = ((avg_l1 + avg_L1)\
                            + (1.0 - (avg_l1 + avg_L1))\
                            * (1.0 - (avg_l2 + avg_L2)))**self.parameters["m"]\
                            * self.parameters["valone"]\
                            + (1.0 - ((avg_l1 + avg_L1)\
                            + (1.0 - (avg_l1 + avg_L1))\
                            * (1.0 - (avg_l2 + avg_L2)))**self.parameters["m"])\
                            *self.parameters["vgroup"]

                    wg = [0.0, 0.0, 0.0, 0.0]

                    wg[0] = l1 * wearly + (1.0 - l1) * l2 * wlate\
                            + (1.0 - l1) * (1.0 - l2) * self.parameters["vstay"]

                    wg[1] = L1 * wearly + (1.0 - L1) * l2 * wlate\
                            + (1.0 - L1) * (1.0 - l2) * self.parameters["vstay"]
                    
                    wg[2] = l1 * wearly + (1.0 - l1) * L2 * wlate\
                            + (1.0 - l1) * (1.0 - L2) * self.parameters["vstay"]
                    
                    wg[3] = L1 * wearly + (1.0 - L1) * L2 * wlate\
                            + (1.0 - L1) * (1.0 - L2) * self.parameters["vstay"]

                    wbar = 0.0
                    for g_idx in range(0,4):
                        gtplus1[g_idx] = g[g_idx] * wg[g_idx]
                        wbar += g[g_idx] * wg[g_idx];


                    converged = True

                    # normalize and check for convergence
                    for g_idx in range(0,4):
                        gtplus1[g_idx] = self.clamp(gtplus1[g_idx]/wbar,0.0,1.0)

                        if abs(gtplus1[g_idx] - g[g_idx]) >= 10**(-7):
                            converged=False
    
#                    print("wearly")
#                    print(wearly)
#                    print("wlate")
#                    print(wlate)
#                    print(g)
#                    print("wg")
#                    print(wg)
#                    print(gtplus1)
#                    sys.exit(1)

                    if converged:
                        break

                    for g_idx in range(0,4):
                        g[g_idx] = gtplus1[g_idx]

                # for this mutant, store the eventual genotype frequencies
                # the time of invasion and which allele was invaded
                # eventually the fasted invasion will be chosen here
                invasion_outcomes_df.iloc[
                        invasion_type,list(range(0,6))] = g + [invasion_time, invasion_type]
                # end for invasion time

            # end for invasion type
            
            # ok now find the largest value in the genotype 
            # frequency columns to see which genotype wins
            subinvasion = invasion_outcomes_df.iloc[:,range(0,4)]

            # select for each row which allele has won out
            invasion_winners = subinvasion.apply(
                    lambda s,n: pd.Series(s.nlargest(n).index), axis=1, n=1)

            # add this invasion winners column back to the original data frame
            # that contains the eventual genotype frequencies of all the genotypes
            # after successful invasion
            invasion_outcomes_df = pd.concat(
                    [invasion_winners,invasion_outcomes_df],axis=1)

            # which of all the mutations are the successful ones
            print(invasion_outcomes_df)
            sys.exit(1)
            invasion_outcomes_df_only_mutant\
                    = invasion_outcomes_df.loc[invasion_outcomes_df.iloc[:,0] != "l1l2"]

            if invasion_outcomes_df_only_mutant.shape[0] < 1:
                break

            # finally then the winner, the one that fixes fastest
            invasion_winner = invasion_outcomes_df_only_mutant.loc[
                    invasion_outcomes_df_only_mutant["maxt"] == min(invasion_outcomes_df_only_mutant["maxt"]),"invasion_type"]

            selected_increment = mutant_increment[invasion_winner.values[0]]

            # finally update the values based on this successful mutant
            l1 = self.clamp(l1 + selected_increment[0],0,1)
            l2 = self.clamp(l2 + selected_increment[1],0,1)

        # end for time
        return [l1,l2]

l1_init = float(sys.argv[1])
m = float(sys.argv[2])

valone=0.4
vgroup=1.0
vstay=0.9

print("valone;vgroup;vstay;m;l1_init;l2_init_i;l1;l2")

#for l2_init_i in list(np.linspace(0.01,0.99,num=100)):
for l2_init_i in [0.5]:
    sim = LeavingGame(parameters = {"valone" : valone,
                                    "vgroup" : vgroup,
                                    "vstay" : vstay,
                                    "m" : m,
                                    "max_time" : 10000,
                                    "max_invasion_time" : 10000,
                                    "mutant_size" : 0.01,
                                    "mutant_start_frequency" : 0.01,
                                    "l1_init" : l1_init,
                                    "l2_init" : l2_init_i})

    vals = sim.run()

    print(f"{valone};{vgroup};{vstay};{m};{l1_init};{l2_init_i};{vals[0]};{vals[1]}")
