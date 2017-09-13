#!/usr/bin/python

import sys
import argparse
import pickle
import matplotlib.pyplot as plt

def footprints(datafile, smoothing, overlay, plotrange):
    with open(datafile, "rb") as data:
        data = pickle.load(data)
    teams = "ABCD"
    # Team D's records start later so align right
    originalteamDlen = len(data[3])
    data[3][:0] = [0] * (len(data[0]) - len(data[3]))

    if plotrange:
        ndata = [a[plotrange[0]:plotrange[1]] for a in data]
        data = ndata
    else:
        plotrange = [0, len(data)]

    def basicplot(alpha=1):
        for i in range(4):
            plt.plot(list(map(lambda x : x+plotrange[0], range(len(data[i])))), data[i], 
                        label="Team {}".format(teams[i]), alpha=alpha)
            if i == 3:
                print("Team {team} average = {avg}".format(team=teams[i], avg=sum(data[i])/originalteamDlen))
            else:
                print("Team {team} average = {avg}".format(team=teams[i], avg=sum(data[i])/len(data[i])))

    def smoothedplot():
        for i in range(4):
            smootheddata = []
            for j, val in enumerate(data[i]):
                begin = j - smoothing if j >= smoothing else 0
                smootheddata.append(sum(data[i][begin:j+1])/(j+1-begin))
            plt.plot(list(map(lambda x : x+plotrange[0], range(len(data[i])))), smootheddata, 
                        label="Team {} (smoothed)".format(teams[i]), linewidth=1.8)

    if smoothing != 0:
        if overlay:
            basicplot(alpha=.5)
        smoothedplot()
    else:
        basicplot()

    plt.xlabel("Days")
    plt.ylabel("MST weight (cost)")
    plt.legend()
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-wl", "--whitelist", help="use whitelist",
                            action="store_true")
    smoothing = parser.add_argument_group()
    smoothing.add_argument("-s", "--smoothing", type=int, default=0, const=7, action="store",
                            nargs='?', help="smooth plot over n days; defaults to 7")
    smoothing.add_argument("-o", "--overlay_smoothing",  action="store_true",
                            help="plot smoothed line over raw data")
    parser.add_argument('-r', "--range", nargs=2, type=int, 
                            help="specify a range of data to display in days '<begin> <end''")

    args = parser.parse_args()

    if args.whitelist:
        datafile = "../data/footprintmstdailyweightsbyteamwithwhitelist.pickle"
    else:
        datafile = "../data/footprintmstdailyweightsbyteamnowhitelist.pickle"

    footprints(datafile, args.smoothing, args.overlay_smoothing, args.range)