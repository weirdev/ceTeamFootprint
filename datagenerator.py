import cetf
import dbcom
import pickle
import csv

"""def miculoads(tc):
    ul = tc.unitload(12)
    with open("data/miculoadstats.pickle", "wb") as outfile:
        pickle.dump(ul, outfile)

def unitloads(tc, uid):
    ul = tc.unitload(uid)
    with open("data/6RC/6rceloadstats.pickle", "wb") as outfile:
        pickle.dump(ul, outfile)
        
def micustaylengths(tc):
    stays = tc.staylength(12)
    with open("data/micustaylengths.pickle", "wb") as outfile:
        pickle.dump(stays, outfile)

def inouttake(tc, uid):
    loads = tc.dayloads(uid)
    with open("data/micuinouttakes.pickle", "wb") as outfile:
        pickle.dump(loads, outfile)

def micuto6rcweloadratings(tc):
    micu = tc.micumedteamtransferoutloadratings()
    micu6rcwe = tc.micudstloadratings(micu, [16, 39])
    with open("data/micuto6rcwetransferswithratings.pickle", "wb", 2) as outfile:
        pickle.dump(micu6rcwe, outfile)

def micutoallotherunits(tc):
    micu = tc.micumedteamtransferoutloadratings()
    micuother = tc.micudstloadratings(micu)
    with open("data/micutoalldststransferswithratings.pickle", "wb", 2) as outfile:
        pickle.dump(micuother, outfile)

def micutoallotherunitswith6rcloadratings(tc, medteamonly=True):
    if medteamonly:
        micu = tc.micumedteamtransferoutloadratings()
        micuother = tc.micudstwith6rcloadratings(micu)
        with open("data/micutoalldststransferswith6rcratings.pickle", "wb", 2) as outfile:
            pickle.dump(micuother, outfile)
    else:
        micu = tc.unitloadratings(12, entries=False, exits=True, medteamonly=False)
        micuother = tc.micudstwith6rcloadratings(micu)
        with open("data/micutoalldststransferswith6rcratingsallteams.pickle", "wb", 2) as outfile:
            pickle.dump(micuother, outfile)

"""

def teampatientcounts(tf):
    tpc = tf.teampatientcounts()
    for pc in tpc:
        pc[0] = pc[0].strftime("%m %d %Y %H %M %S")
    with open("data/teampatientcounts/teampatientcounts.pickle", "wb") as outfile:
        pickle.dump(tpc, outfile)

def mstweights(tf):
    mstw = tf.team_mstweights()
    with open("data/footprintmstdailyweightsbyteam.pickle", "wb") as outfile:
        pickle.dump(mstw, outfile)

def mstedgeweights(tf):
    mstew = tf.team_mstedgeweights()
    with open("data/footprintmstedgeweightsbyteam.pickle", "wb") as outfile:
        pickle.dump(mstew, outfile)

def visitdistality(tf):
    vd, vl = tf.team_patientdistality()
    with open("data/visitdistalitybyteam.pickle", "wb") as outfile:
        pickle.dump(vd, outfile)
    with open("data/deltavisitlength.pickle", "wb") as outfile:
        pickle.dump(vl, outfile)


def visitdistance(tf):
    vd = tf.teampaitentdistance()
    with open("data/visitdistancebyteam.csv", "w") as outfile:
        writer = csv.writer(outfile)
        for vid in vd[0]:
            writer.writerow([vid, vd[0][vid]])


def relativevisitdistality(tf):
    vd, vl = tf.team_patientdistality()
    with open("data/relvisitdistalitybyteam.pickle", "wb") as outfile:
        pickle.dump(vd, outfile)
    with open("data/deltarelvisitlength.pickle", "wb") as outfile:
        pickle.dump(vl, outfile)


def visitstartend(tf):
    visits = tf.visitaddate()
    teams = "ABCD"
    for i in range(4):
        with open("data/visitstartend"+teams[i]+".csv", "wb") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=["vid", "adate", "ddate"])
            writer.writerows(visits[i])


def healedrecords(tf):
    records = tf.healedmedteamrecords()
    with open("data/healedtransfers.csv", "wb") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=["tdate", "vid", "srcuid", "srcrid", "dstuid", "dstrid", "adate", "ddate", "svc", "xlos"])
        writer.writeheader()
        writer.writerows(records)


def sedentism(tf):
    sed = tf.sedentism()
    with open("data/sedentismteama.csv", "w") as outfile:
        writer = csv.writer(outfile)
        for vid in sed[0]:
            writer.writerow([vid, sed[0][vid]])

if __name__ == '__main__':
    with dbcom.DBCom() as db:
        ##with open("data/unitstoroom.pickle", "rb") as f:
        ##    tf = cetf.TeamFootprint(db, pickle.load(f))
        ##    mstweights(tf)

        #tf = cetf.TeamFootprint(db)
        #visitdistality(tf)

        #tf = cetf.TeamFootprint(db)
        #relativevisitdistality(tf)

        #tf = cetf.TeamFootprint(db)
        #visitstartend(tf)

        tf = cetf.TeamFootprint(db)
        sedentism(tf)

