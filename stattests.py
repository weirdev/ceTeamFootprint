import csv
import itertools
import pickle
import statistics
import sys

import numpy as np
import pandas
from scipy import stats

import tsvparse


def micuto6rcvsmicutoother_ttest(ignoreuids=[12, 4, 10, 5], medteamonly=True):
    if medteamonly:
        with open("micutoalldststransferswith6rcratings.pickle", "rb") as infile:
            transfers = pickle.load(infile, encoding="bytes")
    else:
        with open("micutoalldststransferswith6rcratingsallteams.pickle", "rb") as infile:
            transfers = pickle.load(infile, encoding="bytes")

    micuto6rc_loadrates = []
    micutoother_loadrates = []
    #micutoother_loadrates_w = []
    #micutoother_loadrates_e = []
    #micutoother_loadrates_max = []
    for t in transfers:
        if t[b"dstuid"] == 16 or t[b"dstuid"] == 39:
            micuto6rc_loadrates.append(t[b"dstloadrate"])
        elif t[b'dstuid'] not in ignoreuids:
            micutoother_loadrates.append((t[b"6rcwloadrate"]+t[b"6rceloadrate"])/2)
            #micutoother_loadrates_max.append(max(t[b"6rcwloadrate"], t[b"6rceloadrate"]))
            #micutoother_loadrates_w.append(t[b"6rcwloadrate"])
            #micutoother_loadrates_e.append(t[b"6rceloadrate"])
    dlos(sum(micuto6rc_loadrates)/len(micuto6rc_loadrates))
    dlos(sum(micutoother_loadrates)/len(micutoother_loadrates))
    #print(sum(micutoother_loadrates_w)/len(micutoother_loadrates_w))
    #print(sum(micutoother_loadrates_e)/len(micutoother_loadrates_e))
    #print(sum(micutoother_loadrates_max)/len(micutoother_loadrates_max))
    
    dlos(statistics.median(micuto6rc_loadrates))
    dlos(statistics.median(micutoother_loadrates))
    #print(statistics.median(micutoother_loadrates_w))
    #print(statistics.median(micutoother_loadrates_e))
    #print(statistics.median(micutoother_loadrates_max))
    
    dlos()

    dlos(stats.ttest_ind(micuto6rc_loadrates, micutoother_loadrates, equal_var=False))
    '''
    with open("micuto6rcvsmicutoother.csv", "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        for val in itertools.zip_longest(micuto6rc_loadrates, micutoother_loadrates, fillvalue=None):
            writer.writerow(val)
    '''

def topmicudestinationsand6rcloadby6rcload(ignoreuids=[12, 4, 10, 5, 34,36,39,14,15,169,175,95,7,38,80,74,191,192,11], cutoffs=[0,85,90,95,97,99],
                                           medteamonly=True):
    units = [[int(a[0]), a[1], a[2]] for a in tsvparse.simplereadin("units.tsv")[1:]]
    unames = {}
    for unit in units:
        unames[unit[0]] = unit[1]

    if medteamonly:
        with open("micutoalldststransferswith6rcratings.pickle", "rb") as infile:
            transfers = pickle.load(infile, encoding="bytes")
    else:
        with open("micutoalldststransferswith6rcratingsallteams.pickle", "rb") as infile:
            transfers = pickle.load(infile, encoding="bytes")

    for cutoff in cutoffs:
        micuto6rc_loadrates = []
        micutoother_loadrates = []
        destinations = {}
        dlos("-"*50)
        dlos("6RC load >{}%".format(cutoff))
        for t in transfers:
            if t[b"dstuid"] == 16 or t[b"dstuid"] == 39:
                if t[b"dstloadrate"] > cutoff/100:
                    micuto6rc_loadrates.append(t[b"dstloadrate"])
            elif t[b'dstuid'] not in ignoreuids:
                if (t[b"6rcwloadrate"]+t[b"6rceloadrate"])/2 > cutoff/100:
                    micutoother_loadrates.append((t[b"6rcwloadrate"]+t[b"6rceloadrate"])/2)
                    try:
                        destinations[t[b'dstuid']].append((t[b"6rcwloadrate"]+t[b"6rceloadrate"])/2)
                    except KeyError:
                        destinations[t[b'dstuid']] = [(t[b"6rcwloadrate"]+t[b"6rceloadrate"])/2]
        dlos("Mean 6RC load rates for MICU to 6RC:", end=" ")
        dlos(sum(micuto6rc_loadrates)/len(micuto6rc_loadrates))
        dlos("Mean 6RC load rates for MICU to other:", end=" ")
        dlos(sum(micutoother_loadrates)/len(micutoother_loadrates))
        dlos()

        totaltransfers = len(micuto6rc_loadrates) + sum([len(destinations[uid]) for uid in destinations])

        data = np.array(sorted([[unames[uid], len(destinations[uid]), len(destinations[uid])/totaltransfers, statistics.mean(destinations[uid])] for uid in destinations if uid != None]
                               + [["6RCW/E", len(micuto6rc_loadrates), len(micuto6rc_loadrates)/totaltransfers, statistics.mean(micuto6rc_loadrates)]], key = lambda x : x[1], reverse=True), ndmin=2)
        df = pandas.DataFrame(data, columns = ["Unit", "Transfer Count", "Transfer Proportion", "Avg 6RC load"])
        dlos(df)
        dlos("Total number of transfers examined: {}".format(len(micuto6rc_loadrates)+len(micutoother_loadrates)))
        dlos("Number of transfers to 6RCW/E: {}".format(len(micuto6rc_loadrates)))
        dlos("Proportion of transfers to 6RCW/E: {}".format(len(micuto6rc_loadrates)/(len(micuto6rc_loadrates)+len(micutoother_loadrates))))
        dlos("Number of transfers to other units: {}".format(len(micutoother_loadrates)))
        dlos("Proportion of transfers to other units: {}".format(len(micutoother_loadrates)/(len(micuto6rc_loadrates)+len(micutoother_loadrates))))
        dlos()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == "True":
            micuto6rcvsmicutoother_ttest(ignoreuids=[], medteamonly=True)
            topmicudestinationsand6rcloadby6rcload(medteamonly=True)
        else:
            micuto6rcvsmicutoother_ttest(ignoreuids=[], medteamonly=False)
            topmicudestinationsand6rcloadby6rcload(medteamonly=False)
