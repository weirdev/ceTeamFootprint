from matplotlib import pyplot as plt
import pickle
import numpy as np
from statistics import median
import csv
import datetime
from scipy import stats
from mpl_toolkits.mplot3d import Axes3D


def tf_teampatientcounts():
    with open("../data/teampatientcounts/teampatientcounts.pickle", "rb") as infile:
        tpc = pickle.load(infile)
    for pc in tpc:
        pc[0] = datetime.datetime.strptime(pc[0], "%m %d %Y %H %M %S")
    x = 0
    teams = "ABCD"
    for t in tpc:
        print(x)
        teamapc = t[1]
        print(len(teamapc))
        print(sum(teamapc)/len(teamapc))
        plt.plot(range(len(teamapc)), teamapc)
        plt.title("Team " + teams[x])
        dateinterval = len(teamapc) // 9
        plt.xticks(range(0,len(teamapc),dateinterval), 
                [datetime.datetime.strftime(t[0] + datetime.timedelta(a), "%m/%d/%Y")
                 for a in range(0,len(teamapc),dateinterval)], rotation=40)
        plt.show()
        x += 1

def staylengths():
    with open("../data/micustaylengths.pickle", "rb") as infile:
        stays = pickle.load(infile)
    print(max(stays))
    plt.hist(stays, bins=np.arange(0,15,.25))
    plt.show()

def inouttake():
    with open("../data/micuinouttakes.pickle", "rb") as infile:
        loads = pickle.load(infile)
    print(len(loads))
    plt.plot(range(len(loads)), loads)
    plt.axis([None,None,0,28])
    plt.show()

def micuoutvs6rcinloadratings():
    with open("../data/micuto6rcwetransferswithratings.pickle", "rb") as infile:
        transfers = pickle.load(infile, encoding="bytes")
    miculr = []
    sixrclr = []
    colors = []
    for i, t in enumerate(transfers):
        colors.append(0)
        miculr.append(t[b"srcloadrate"])
        sixrclr.append(t[b"dstloadrate"])
        if t[b"srcloadrate"] > 1:
            j = i
            for j, t2 in enumerate(transfers[i:]):
                if t2[b"srcloadrate"] <= 1:
                    break
            colors[i] = j
        if t[b"dstloadrate"] > 1:
            j = i
            for j, t2 in enumerate(transfers[i:]):
                if t2[b"dstloadrate"] <= 1:
                    break
            if colors[i] == 0:
                colors[i] = j
            else:
                colors[i] = (colors[i] + (j)) / 2
    largest = max(colors)
    print(largest)
    if largest > 0:
        for i, v in enumerate(colors):
            colors[i] = v / largest
    print(sum(miculr)/len(miculr))
    print(sum(sixrclr)/len(sixrclr))
    plt.scatter(miculr, sixrclr, c=colors)
    plt.show()

def micuvsotherunitsloadratings(plotaverages=False):
    with open("../data/micutoalldststransferswithratings.pickle", "rb") as infile:
        transfers = pickle.load(infile, encoding="bytes")
    with open("../data/units.tsv") as unitstsv:
        units = list(csv.reader(unitstsv, delimiter='\t'))
        unitdict = {}
        for i in range(1, len(units)):
            unitdict[int(units[i][0])] = units[i][1]
    transfersbydst = {}
    for t in transfers:
        try:
            transfersbydst[t[b"dstuid"]].append(t)
        except KeyError:
            transfersbydst[t[b"dstuid"]] = [t]
    if plotaverages:
        micuavgs = []
        otheravgs = []
        labels = []
    for dstuid in transfersbydst:
        if dstuid == None:
            continue
        print("MICU v. {} load rates".format(unitdict[dstuid]))
        miculr = []
        dstlr = []
        for t in transfersbydst[dstuid]:
            miculr.append(t[b"srcloadrate"])
            dstlr.append(t[b"dstloadrate"])
        print(sum(miculr)/len(miculr))
        print(sum(dstlr)/len(dstlr))
        if not plotaverages:
            plt.scatter(miculr, dstlr)
            plt.title("MICU v. {} load rates".format(unitdict[dstuid]))
            plt.show()
        if plotaverages:
            micuavgs.append(sum(miculr)/len(miculr))
            otheravgs.append(sum(dstlr)/len(dstlr))
            labels.append(unitdict[dstuid])
        print()
    if plotaverages:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        plt.scatter(micuavgs, otheravgs)
        for i in range(len(labels)):
            ax.annotate(labels[i], xy=(micuavgs[i], otheravgs[i]))
        plt.show()

def micuvsotherunitswith6rcewloadratings(plotaverages=False):
    with open("../data/micutoalldststransferswith6rcratings.pickle", "rb") as infile:
        transfers = pickle.load(infile, encoding="bytes")
    with open("../data/units.tsv") as unitstsv:
        units = list(csv.reader(unitstsv, delimiter='\t'))
        unitdict = {}
        for i in range(1, len(units)):
            unitdict[int(units[i][0])] = units[i][1]
    transfersbydst = {}
    for t in transfers:
        try:
            transfersbydst[t[b"dstuid"]].append(t)
        except KeyError:
            transfersbydst[t[b"dstuid"]] = [t]
    if plotaverages:
        micuavgs = []
        otheravgs = []
        labels = []
    for dstuid in transfersbydst:
        if dstuid == None:
            continue
        print("MICU v. {} load rates".format(unitdict[dstuid]))
        miculr = []
        dstlr = []
        colors = []
        for t in transfersbydst[dstuid]:
            miculr.append(t[b"srcloadrate"])
            dstlr.append(t[b"dstloadrate"])
            colors.append((t[b"6rcwloadrate"]+t[b"6rceloadrate"])/2)
        print(sum(miculr)/len(miculr))
        print(sum(dstlr)/len(dstlr))
        print(sum(colors)/len(colors))
        if not plotaverages:
            plt.scatter(miculr, dstlr, c=colors)
            plt.title("MICU v. {} load rates".format(unitdict[dstuid]))
            plt.show()
        if plotaverages:
            micuavgs.append(sum(miculr)/len(miculr))
            otheravgs.append(sum(dstlr)/len(dstlr))
            labels.append(unitdict[dstuid])
        print()
    if plotaverages:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        plt.scatter(micuavgs, otheravgs)
        for i in range(len(labels)):
            ax.annotate(labels[i], xy=(micuavgs[i], otheravgs[i]))
        plt.show()

def footprints():
    with open("../data/footprintmstdailyweightsbyteamnowhitelist.pickle", "rb") as data:
        data = pickle.load(data)
    teams = "ABCD"
    # Team D's records start later so align right
    originalteamDlen = len(data[3])
    data[3][:0] = [0] * (len(data[0]) - len(data[3]))
    for i in range(4):
        plt.plot(range(len(data[i])), data[i], label="Team {}".format(teams[i]))
        # Remove extra zeros from team D's data so average is unchanged
        if i == 3:
            data[3][:-1*originalteamDlen] = []
        print("Team {team} average = {avg}".format(team=teams[i], avg=sum(data[i])/len(data[i])))
    plt.xlabel("Days")
    plt.ylabel("MST weight (cost)")
    plt.legend()
    plt.show()

def teamprintvteamprint():
    with open("../data/footprintmstdailyweightsbyteamnowhitelist.pickle", "rb") as data:
        data = pickle.load(data)
    teams = "ABCD"
    maxlen = min(len(data[0]), len(data[1]))
    plt.title("Team {} v Team {}".format(teams[0], teams[1]))
    plt.scatter(data[0][:maxlen], data[1][:maxlen])

    # calc the trendline
    z = np.polyfit(data[0][:maxlen], data[1][:maxlen], 1)
    p = np.poly1d(z)
    plt.plot(data[0][:maxlen],p(data[0][:maxlen]),"r--")
    # the line equation:
    print("y=%.6fx+(%.6f)"%(z[0],z[1]))
    # fit values, and mean
    yhat = p(data[0][:maxlen])                         # or [p(z) for z in x]
    ybar = np.sum(data[1][:maxlen])/len(data[1][:maxlen])          # or sum(y)/len(y)
    ssreg = np.sum((yhat-ybar)**2)   # or sum([ (yihat - ybar)**2 for yihat in yhat])
    sstot = np.sum((data[1][:maxlen] - ybar)**2)    # or sum([ (yi - ybar)**2 for yi in y])
    print("r^2={}".format(ssreg / sstot))

    plt.show()

def edgeweightdistribution():
    #plt.hist(stays, bins=np.arange(0,15,.25), alpha=0.5)
    with open("../data/footprintmstedgeweightsbyteam.pickle", "rb") as data:
        data = pickle.load(data)

    teams = "ABCD"
    bins = np.linspace(0, 90, 100)

    for i in range(4):
        mergeddata = []
        for d in data[i]:
            mergeddata.extend(d)
        plt.hist(mergeddata, bins, alpha=0.5, label="Team {}".format(teams[i]))
        plt.legend()
        plt.show()

def percentpercentpercent(removehighest, cutweight): # -> percent data points meeting criteria
    with open("../data/footprintmstedgeweightsbyteam.pickle", "rb") as data:
        data = pickle.load(data)

    teams = "ABCD"

    for i in range(4):
        print("Team {}".format(teams[i]))
        matchcount = 0
        print(sum([len(t) for t in data[i]])/len(data[i]))
        for tree in data[i]:
            ranked = sorted(tree)
            cutcount = removehighest*len(ranked)
            if cutcount % 1 > 0.5:
                cutcount = int(cutcount) + 1
            else:
                cutcount = int(cutcount)
            if cutcount != 0:
                cut = ranked[-1*cutcount:]
                if sum(cut) > sum(ranked) * cutweight:
                    matchcount += 1
        print("{res}% of trees had {rh}% of edges with at least {cutw}% of the total weight.".format(res = matchcount*100/len(data[i]), 
                    rh=removehighest*100, cutw=cutweight*100))

def percentpercentpercent3d(granularity): # -> percent data points meeting criteria
    with open("../data/footprintmstedgeweightsbyteam.pickle", "rb") as data:
        data = pickle.load(data)

    teams = "ABCD"
    xpoints = []
    ypoints = []
    zpoints = []
    for x in np.arange(0, 1, granularity):
        for y in np.arange(0, 1, granularity):
            i = 0
            matchcount = 0
            for tree in data[i]:
                ranked = sorted(tree)
                cutcount = x*len(ranked)
                if cutcount % 1 > 0.5:
                    cutcount = int(cutcount) + 1
                else:
                    cutcount = int(cutcount)
                if cutcount != 0:
                    cut = ranked[-1*cutcount:]
                    if sum(cut) > sum(ranked) * y:
                        matchcount += 1
            xpoints.append(x)
            ypoints.append(y)
            zpoints.append(matchcount/len(data[i]))

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(xpoints, ypoints, zpoints)
    plt.show()

def distalityvlos():
    with open("../data/visitdistalitybyteam.pickle", "rb") as data:
        distality = pickle.load(data)
    with open("../data/visitlength.pickle", "rb") as data:
        los = pickle.load(data)

    teams = "ABCD"
    for i in range(4):
        pairs = []
        for vid in distality[i]:
            pairs.append([distality[i][vid], los[vid]])
        plt.scatter([a[0] for a in pairs], [a[1]/(60*60*24) for a in pairs])
        print(sum([a[1]/(60*60*24) for a in pairs])/len(pairs))
        plt.title("Team {}".format(teams[i]))
        plt.show()

def relativedistalityvlos():
    with open("../data/relvisitdistalitybyteam.pickle", "rb") as data:
        distality = pickle.load(data)
    with open("../data/relvisitlength.pickle", "rb") as data:
        los = pickle.load(data)

    teams = "ABCD"
    for i in range(4):
        pairs = []
        for vid in distality[i]:
            pairs.append([distality[i][vid], los[vid]])
        plt.scatter([a[0] for a in pairs], [a[1]/(60*60*24) for a in pairs])
        print(sum([a[1]/(60*60*24) for a in pairs])/len(pairs))
        plt.title("Team {}".format(teams[i]))
        plt.show()

def distalityvlos():
    with open("../data/visitdistalitybyteam.pickle", "rb") as data:
        distality = pickle.load(data)
    with open("../data/visitlength.pickle", "rb") as data:
        los = pickle.load(data)

    teams = "ABCD"
    for i in range(4):
        pairs = []
        for vid in distality[i]:
            pairs.append([distality[i][vid], los[vid]])
        plt.scatter([a[0] for a in pairs], [a[1]/(60*60*24) for a in pairs])
        print(sum([a[1]/(60*60*24) for a in pairs])/len(pairs))
        plt.title("Team {}".format(teams[i]))
        plt.show()

def relativedistalityvlos():
    with open("../data/relvisitdistalitybyteam.pickle", "rb") as data:
        distality = pickle.load(data)
    with open("../data/deltarelvisitlength.pickle", "rb") as data:
        dlos = pickle.load(data)
    with open("../data/relvisitlength.pickle", "rb") as data:
        los = pickle.load(data)

    teams = "ABCD"
    for i in range(4):
        pairs = []
        print(min(los, key=lambda x: los[x]))
        maxlos = los[max(los, key=lambda x: los[x])]
        for vid in distality[i]:
            pairs.append([distality[i][vid], dlos[vid], los[vid]/maxlos])
        plt.scatter([a[0] for a in pairs], [a[1]/(60*60*24) for a in pairs], c=[a[2] for a in pairs])
        print(sum([a[1]/(60*60*24) for a in pairs])/len(pairs))
        plt.title("Team {}".format(teams[i]))
        plt.show()

def relativedistalityvdlostrend(spread=100, showerror=False):
    with open("../data/relvisitdistalitybyteam.pickle", "rb") as data:
        distality = pickle.load(data)
    with open("../data/deltarelvisitlength.pickle", "rb") as data:
        dlos = pickle.load(data)
    with open("../data/relvisitlength.pickle", "rb") as data:
        los = pickle.load(data)

    teams = "ABCD"
    for i in range(4):
        pairs = []
        print(min(los, key=lambda x: los[x]))
        maxlos = los[max(los, key=lambda x: los[x])]
        for vid in distality[i]:
            pairs.append([distality[i][vid], dlos[vid], los[vid]/maxlos])
        #plt.scatter([a[0] for a in pairs], [a[1]/(60*60*24) for a in pairs], c=[a[2] for a in pairs])
        pairs.sort(key=lambda x : x[0])
        smoothed = []
        stdev = []
        for j, v in enumerate(pairs):
            begin = j-(spread//2) if j>((spread//2)-1) else 0
            end = j+(spread//2) if j+(spread//2)<len(pairs) else len(pairs)-1
            smoothed.append(sum([a[1] for a in pairs[begin:end]])/(end-begin)/(60*60*24))
            stdev.append(np.std([a[1] for a in pairs[begin:end]])/(60*60*24))
        plt.scatter([a[0] for a in pairs], smoothed, c=[a[2]/max(pairs, key=lambda x:x[2])[2] for a in pairs])
        if showerror:
            plt.errorbar([a[0] for a in pairs], smoothed, stdev, alpha=0.1)
        plt.xlabel("Distality")
        plt.ylabel("los-xlos")
        print(sum([a[1]/(60*60*24) for a in pairs])/len(pairs))
        plt.title("Team {}".format(teams[i]))
        plt.show()


def mobilityvsxlos(graph=False):
    with open("../data/footprintmstdailyweightsbyteamnowhitelist.pickle", "rb") as data:
        weights = pickle.load(data)
    with open("../data/deltarelvisitlength.pickle", "rb") as data:
        dlos = pickle.load(data)
    

    firstdays = ["2004-11-14 11:39:59", "2004-12-19 09:32:59", "2004-11-15 12:38:59", "2004-12-30 12:13:59"]
    firstdays = [datetime.datetime.strptime(a, "%Y-%m-%d %H:%M:%S") for a in firstdays]
    
    # pick a year
    first = 2000
    last = first + 365
    teams = "ABCD"
    for i in range(4):
        print("Team {}".format(teams[i]))
        with open("../data/visitstartend"+teams[i]+".csv", "r") as data:
            visitstartend = list(csv.DictReader(data, ["vid", "adate", "ddate"]))
        visitstartend = { a["vid"] : {"adate" : datetime.datetime.strptime(a["adate"], "%Y-%m-%d %H:%M:%S"), "ddate" : datetime.datetime.strptime(a["ddate"], "%Y-%m-%d %H:%M:%S")} for a in visitstartend }
        # "smooth" the year (8 days)
        smoothed = []
        spread = 8
        weightsyear = weights[i][first:last]
        for j in range(len(weightsyear)-7):
            smoothed.append(sum(weightsyear[j:j+8])/(8))
        if graph:
            plt.title("Team {}".format(teams[i]))
            plt.plot(range(len(smoothed)), smoothed)
            plt.xticks(range(last-first)[::10], range(first, last)[::10], rotation=90)
            plt.xlabel("Day")
            plt.ylabel("Mst weight")
            plt.show()

        smoothed = [[v, j] for j,v in enumerate(smoothed)]
        ordered = sorted(smoothed, key=lambda x:x[0])
        top = [a[1]+first for a in ordered[-18:]]
        bottom = [a[1]+first for a in ordered[:18]]

        top = [firstdays[i] + datetime.timedelta(a) for a in top]
        bottom = [firstdays[i] + datetime.timedelta(a) for a in bottom]

        
        # Match time ranges to vids
        topvids = set()
        for week in top:
            for vid in visitstartend:
                if visitstartend[vid]["adate"] > week + datetime.timedelta(8):
                    continue
                elif visitstartend[vid]["ddate"] < week:
                    continue
                else:
                    topvids.add(vid)
        bottomvids = set()
        for week in bottom:
            for vid in visitstartend:
                if visitstartend[vid]["adate"] > week + datetime.timedelta(8):
                    continue
                elif visitstartend[vid]["ddate"] < week:
                    continue
                else:
                    bottomvids.add(vid)

        topdlos = [dlos[int(a)]/(24*60*60) for a in topvids if (int(a) in dlos)]
        bottomdlos = [dlos[int(a)]/(24*60*60) for a in bottomvids if (int(a) in dlos)]

        print(sum(topdlos)/len(topdlos))
        print(sum(bottomdlos)/len(bottomdlos))

        print(np.std(topdlos))

        print(stats.ttest_ind(topdlos, bottomdlos))
        #print(stats.wilcoxon(topdlos, bottomdlos))

def distalityoddsratios():
    with open("../data/relvisitdistalitybyteam.pickle", "rb") as data:
        distality = pickle.load(data)
    with open("../data/deltarelvisitlength.pickle", "rb") as data:
        dlos = pickle.load(data)
    with open("../data/relvisitlength.pickle", "rb") as data:
        los = pickle.load(data)

    teams = "ABCD"
    for i in range(4):
        print("Team {}".format(teams[i]))

        mindistality = distality[i][min(distality[i], key=lambda x: distality[i][x])]
        maxdistality = distality[i][max(distality[i], key=lambda x: distality[i][x])]

        # 10 bins of distality
        bins = np.linspace(mindistality, maxdistality, 11)
        errors = []
        for b in range(len(bins) - 1):
            section = {}
            for vid in distality[i]:
                if distality[i][vid] >= bins[b] and distality[i][vid] <= bins[b+1]:
                    section[vid] = distality[i][vid]
            try:
                meanerror = sum([dlos[vid] for vid in section]) / len(section) / (60*60*24)
            except:
                meanerror = 0
            errors.append(meanerror)
        print(bins)
        print("\n".join([str(e) for e in errors]))

def distancevlos():
    with open("../data/visitdistancebyteam.csv", "r") as data:
        reader = csv.reader(data)
        distance = {int(pair[0]): float(pair[1]) for pair in reader}
    with open("../data/deltarelvisitlength.pickle", "rb") as data:
        dlos = pickle.load(data)
    with open("../data/relvisitlength.pickle", "rb") as data:
        los = pickle.load(data)

    pairs = []
    print(min(los, key=lambda x: los[x]))
    maxlos = los[max(los, key=lambda x: los[x])]
    #los[vid]-dlos[vid]
    for vid in distance:
        pairs.append([distance[vid], dlos[vid], los[vid]/maxlos])
    plt.scatter([a[0] for a in pairs], [a[1]/(60*60*24) for a in pairs], c=[a[2] for a in pairs])
    print(sum([a[1]/(60*60*24) for a in pairs])/len(pairs))
    plt.show()

def distancevdlostrend(spread=100, showerror=False):
    with open("../data/visitdistancebyteam.csv", "r") as data:
        reader = csv.reader(data)
        distance = {int(pair[0]): float(pair[1]) for pair in reader}
    with open("../data/deltarelvisitlength.pickle", "rb") as data:
        dlos = pickle.load(data)
    with open("../data/relvisitlength.pickle", "rb") as data:
        los = pickle.load(data)

    pairs = []
    print(min(los, key=lambda x: los[x]))
    maxlos = los[max(los, key=lambda x: los[x])]
    for vid in distance:
        pairs.append([distance[vid], dlos[vid], los[vid]/maxlos])
    #plt.scatter([a[0] for a in pairs], [a[1]/(60*60*24) for a in pairs], c=[a[2] for a in pairs])
    pairs.sort(key=lambda x : x[0])
    smoothed = []
    stdev = []
    for j, v in enumerate(pairs):
        begin = j-(spread//2) if j>((spread//2)-1) else 0
        end = j+(spread//2) if j+(spread//2)<len(pairs) else len(pairs)-1
        smoothed.append(sum([a[1] for a in pairs[begin:end]])/(end-begin)/(60*60*24))
        stdev.append(np.std([a[1] for a in pairs[begin:end]])/(60*60*24))
    plt.scatter([a[0] for a in pairs], smoothed, c=[a[2]/max(pairs, key=lambda x:x[2])[2] for a in pairs])
    if showerror:
        plt.errorbar([a[0] for a in pairs], smoothed, stdev, alpha=0.1)
    plt.xlabel("Distance")
    plt.ylabel("los-xlos")
    print(sum([a[1]/(60*60*24) for a in pairs])/len(pairs))
    plt.show()


def relativedistalityvdlostrend_sedentrycutoff(sedcutoff, spread=100, showerror=False):
    with open("../data/relvisitdistalitybyteam.pickle", "rb") as data:
        distality = pickle.load(data)
    with open("../data/deltarelvisitlength.pickle", "rb") as data:
        dlos = pickle.load(data)
    with open("../data/relvisitlength.pickle", "rb") as data:
        los = pickle.load(data)
    with open("../data/sedentismteama.csv", "r") as data:
        reader = csv.reader(data)
        sedentism = {int(pair[0]): float(pair[1]) for pair in reader}

    teams = "ABCD"
    for i in range(1):
        pairs = []
        print(min(los, key=lambda x: los[x]))
        maxlos = los[max(los, key=lambda x: los[x])]
        for vid in distality[i]:
            if sedentism[vid] >= sedcutoff:
                pairs.append([distality[i][vid], dlos[vid], los[vid]/maxlos])
        #plt.scatter([a[0] for a in pairs], [a[1]/(60*60*24) for a in pairs], c=[a[2] for a in pairs])
        pairs.sort(key=lambda x : x[0])
        smoothed = []
        stdev = []
        for j, v in enumerate(pairs):
            begin = j-(spread//2) if j>((spread//2)-1) else 0
            end = j+(spread//2) if j+(spread//2)<len(pairs) else len(pairs)-1
            smoothed.append(sum([a[1] for a in pairs[begin:end]])/(end-begin)/(60*60*24))
            stdev.append(np.std([a[1] for a in pairs[begin:end]])/(60*60*24))
        plt.scatter([a[0] for a in pairs], smoothed, c=[a[2]/max(pairs, key=lambda x:x[2])[2] for a in pairs])
        if showerror:
            plt.errorbar([a[0] for a in pairs], smoothed, stdev, alpha=0.1)
        plt.xlabel("Distality")
        plt.ylabel("los-xlos")
        print(sum([a[1]/(60*60*24) for a in pairs])/len(pairs))
        plt.title("Cutoff {}".format(round(sedcutoff, 2)))
        plt.show()

if __name__ == "__main__":
    #percentpercentpercent(.1, .4)
    
    #percentpercentpercent3d(.1)
    #edgeweightdistribution()
    #distalityvlos()

    #relativedistalityvlos()
    #relativedistalityvdlostrend(200, False)

    #mobilityvsxlos(True)

    #distalityoddsratios()

    #distancevlos()
    #distancevdlostrend(200, False)

    relativedistalityvdlostrend_sedentrycutoff(0)
    for c in np.arange(0.7, 0.9, 0.1):
        relativedistalityvdlostrend_sedentrycutoff(c)
    relativedistalityvdlostrend_sedentrycutoff(0.99)

