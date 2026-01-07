#!/usr/bin/env python3
import sys
import pandas as pd

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

        mutant_types = [ 
                            [ self.parameters["mutant_size"], 0 ], # higher l1, unchanged l2
                            [ -self.parameters["mutant_size"], 0], # lower l1, unchanged l2
                            [ 0, self.parameters["mutant_size"]], # unchanged l1, higher l2
                            [ 0, -self.parameters["mutant_size"]] # unchanged l2, higher l2
                            ]

        if self.parameters["double_mutant"]:

            mutant_types2 = [
                                [ self.parameters["mutant_size"],self.parameters["mutant_size"]], # higher l1, higher l2
                                [ -self.parameters["mutant_size"],self.parameters["mutant_size"]], # lower l1, higher l2
                                [ self.parameters["mutant_size"],-self.parameters["mutant_size"]], # higher l1, lower l2
                                [ -self.parameters["mutant_size"],-self.parameters["mutant_size"]] # lower l1, lower l2
                                ]

            mutant_types = mutant_types + mutant_types2


        # now iterate over time and perform successive invasions
        # of different types
        for time in range(0, self.parameters["max_time"]):
            
            invasion_genotype_wins = None

            total_number_mutants = len(mutant_types)

            # data frame to bookkeep outcomes for 
            # all the different types of mutants that invaded
            invasion_outcomes_df = pd.DataFrame(
                    {
                        "l1l2" : [ 0.0 for i in range(0,total_number_mutants) ],
                        "L1l2" : [ 0.0 for i in range(0,total_number_mutants) ],
                        "l1L2" : [ 0.0 for i in range(0,total_number_mutants) ],
                        "L1L2" : [ 0.0 for i in range(0,total_number_mutants) ],
                        "maxt" : [ 0 for i in range(0,total_number_mutants) ],
                        "invasion_type" : [ 0 for i in range(0,total_number_mutants) ]
                    }
            )

            # go over all the different types of mutants and see
            # what happens
            for mutant_type_idx in range(0,total_number_mutants):

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
                L1 = self.clamp(l1 + mutant_types[mutant_type_idx][0],0.0,1.0)
                L2 = self.clamp(l2 + mutant_types[mutant_type_idx][1],0.0,1.0)



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
                        mutant_type_idx,list(range(0,6))] = g +\
                                [invasion_time, mutant_type_idx]
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
            # check if any of the non-mutant types is able to successfully invade
            # we can do so by filtering out the cases in which the resident won
            invasion_outcomes_df_only_mutant\
                    = invasion_outcomes_df.loc[invasion_outcomes_df.iloc[:,0] != "l1l2"]

            if invasion_outcomes_df_only_mutant.shape[0] < 1:
                # this condition would apply if the resident won in all cases
                # in which case we can stop the iteration
                break

            # finally then the winner, the one that fixes fastest
            invasion_winner = invasion_outcomes_df_only_mutant.loc[
                    invasion_outcomes_df_only_mutant["maxt"] == min(invasion_outcomes_df_only_mutant["maxt"]),"invasion_type"]

            selected_increment = mutant_types[invasion_winner.values[0]]

            # finally update the values based on this successful mutant
            l1 = self.clamp(l1 + selected_increment[0],0,1)
            l2 = self.clamp(l2 + selected_increment[1],0,1)

        # end for time
        return [l1,l2]

l1_init = float(sys.argv[1])
l2_init = float(sys.argv[2])
m = float(sys.argv[3])
valone = float(sys.argv[4])
vgroup = float(sys.argv[5])
vstay = float(sys.argv[6])
double_mutant = bool(sys.argv[7])
file = sys.argv[8]

contents = "valone;vgroup;vstay;m;double;l1_init;l2_init_i;l1;l2\n"

sim = LeavingGame(parameters = {"valone" : valone,
                                "vgroup" : vgroup,
                                "vstay" : vstay,
                                "m" : m,
                                "max_time" : 10000,
                                "max_invasion_time" : 10000,
                                "mutant_size" : 0.01,
                                "mutant_start_frequency" : 0.01,
                                "double_mutant" : double_mutant,
                                "l1_init" : l1_init,
                                "l2_init" : l2_init})

vals = sim.run()

contents += f"{valone};{vgroup};{vstay};{m};{double_mutant};{l1_init};{l2_init};{vals[0]};{vals[1]}\n"

with open(file,"w") as f:
    f.write(contents)


