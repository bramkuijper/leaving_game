#!/usr/bin/env python3

import os, re

first = True

for root, dirs, files in os.walk("."):

    for file in files:
        if re.search("sim_popgen_leaving", file) is not None:

            with open(os.path.join(root, file)) as f:
                fl = f.readlines()

                if first:
                    print("".join(fl))
                    first = False
                else:
                    print("".join(fl[2:]))


