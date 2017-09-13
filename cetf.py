#!/usr/bin/env python2

import datetime
import copy
import mst

class TeamFootprint(object):

    def __init__(self, db, unitstoroom=None):
        self.db = db
        # unitstoroom should be set if heal by room is desired
        # Otherwise there are erroneous transfers to room 0
        self.unitstoroom = unitstoroom
        self.visitlengths = dict()
        self.deltavisitlengths = dict()

    def createdictrecords(self, records, *args, **kwargs):
        dictrecords = []
        for record in records:
            dictrecord = {}
            for x in range(len(args)):
                dictrecord[args[x]] = record[x]
            for name, value in kwargs.items():
                dictrecord[name] = record[value]
            dictrecords.append(dictrecord)
        return dictrecords

    def healrecords(self, records):
        """Repairs records for each visitor making sure that each person's records make 'sense'"""
        firsttransfertime = records[0]["tdate"]
        healedrecords = []
        
        visits = {}
        for row in records:
            try:
                visits[row["vid"]].append(row)
            except KeyError:
                visits[row["vid"]] = [row]
        for vid in visits:
            changes = 0
            i = 1
            while i < len(visits[vid]):
                changes += 1
                # same source unit src1 == src2
                # destination equality not considered
                # original src -> dst1
                # original src -> dst2
                # remove earliest record
                # change to src -> dst2
                if visits[vid][i-1]["srcuid"] == visits[vid][i]["srcuid"]:
                    # if destinations also equal keep both records because person likely 
                    # still be in unit and losing record may affect amount of time it looks 
                    # like they have been in current unit if a "fill-in" record has to 
                    # be generated
                    if visits[vid][i-1]["srcuid"] != visits[vid][i-1]["dstuid"]:
                        del visits[vid][i-1]
                        i -= 1
                # same destination unit dst1 == dst2
                # elif because record could have already been removed above
                # original src1 -> dst
                # original src2 -> dst
                # remove second record because removing earlier record would break chain of transfers
                # change to src1 -> dst
                elif visits[vid][i-1]["dstuid"] == visits[vid][i]["dstuid"]:
                    del visits[vid][i]
                    i -= 1
                # destination unit doesnt correspond to next source unit
                elif visits[vid][i-1]["dstuid"] != visits[vid][i]["srcuid"]:
                    # create dummy transfer between destination and next source
                    # transfer time is exactly halfway between arrival
                    new_record = copy.copy(visits[vid][i-1])
                    new_record["tdate"] = visits[vid][i-1]["tdate"] + ((visits[vid][i]["tdate"] - visits[vid][i-1]["tdate"]) / 2)
                    new_record["srcuid"] = visits[vid][i-1]["dstuid"]
                    new_record["dstuid"] = visits[vid][i]["srcuid"]
                    visits[vid].insert(i, new_record)
                else:
                    changes -= 1
                i += 1
            # add new "dummy" transfer record for admission    
            new_record = copy.copy(visits[vid][0])
            # first transfer date after admission date?
            if visits[vid][0]["tdate"] > visits[vid][0]["adate"]:
                # record's transfer date will be admission date
                # unless admission date is before very first record transfer time
                if new_record["adate"] > firsttransfertime:
                    new_record["tdate"] = new_record["adate"]
                else:
                    new_record["tdate"] = firsttransfertime - datetime.timedelta(seconds=1)
            # First transfer before admission date
            else:
                # Make dummy transfer for one second before previous first transfer time
                new_record["tdate"] = new_record["tdate"] - datetime.timedelta(seconds=1)

            # record's transfer destination will be 
            # previous first record's transfer source
            new_record["dstuid"] = new_record["srcuid"]
            new_record["srcuid"] = None
            visits[vid].insert(0, new_record)

            # add new "dummy" transfer record for discharge
            new_record = copy.copy(visits[vid][-1])
            # last transfer date before discharge date?
            if visits[vid][-1]["tdate"] < visits[vid][-1]["ddate"]:
                # record's transfer date will be discharge date
                new_record["tdate"] = new_record["ddate"]
            # Last transfer after discharge date
            else:
                # Make dummy transfer for one second after previous last transfer time
                new_record["tdate"] = new_record["tdate"] + datetime.timedelta(seconds=1)
            
            # record's transfer source will be
            # previous last record's transfer destination
            new_record["srcuid"] = new_record["dstuid"]
            new_record["dstuid"] = None
            visits[vid].append(new_record)
            
            # Snippet below is for verifying that patient does not contribute to "drift" for a given uid
            #load = 0
            #for transfer in visits[vid]:
            #    if transfer["srcuid"] == 12:
            #        # patient left micu
            #        load -= 1
            #    if transfer["dstuid"] == 12:
            #        # patient entered micu
            #        load += 1
            #if load != 0:
            #    for t in visits[vid]:
            #        print(t)
            #    input()

            healedrecords.extend(visits[vid])

        healedrecords.sort(key=lambda x : x["tdate"])

        return healedrecords

    def healrecordsbyroom(self, records):
        """Repairs records for each visitor making sure that each person's records make 'sense'"""
        firsttransfertime = records[0]["tdate"]
        healedrecords = []
        
        visits = {}
        for row in records:
            badtransfer = False
            if self.unitstoroom is not None:
                if row["srcrid"] == 0:
                    try:
                        row["srcrid"] = self.unitstoroom[row["srcuid"]]
                    except:
                        badtransfer = True
                if row["dstrid"] == 0:
                    try:
                        row["dstrid"] = self.unitstoroom[row["dstuid"]]
                    except:
                        badtransfer = True
            if not badtransfer:
                # Only track certain units
                #if row["srcuid"] in (16,39,12,14,15) and row["dstuid"] in (16,39,12,14,15):
                try:
                    visits[row["vid"]].append(row)
                except KeyError:
                    visits[row["vid"]] = [row]

        for vid in visits:
            changes = 0
            i = 1
            while i < len(visits[vid]):
                changes += 1
                # same source unit src1 == src2
                # destination equality not considered
                # original src -> dst1
                # original src -> dst2
                # remove earliest record
                # change to src -> dst2
                if visits[vid][i-1]["srcrid"] == visits[vid][i]["srcrid"]:
                    # if destinations also equal keep both records because person likely 
                    # still be in unit and losing record may affect amount of time it looks 
                    # like they have been in current unit if a "fill-in" record has to 
                    # be generated
                    if visits[vid][i-1]["srcrid"] != visits[vid][i-1]["dstrid"]:
                        del visits[vid][i-1]
                        i -= 1
                # same destination unit dst1 == dst2
                # elif because record could have already been removed above
                # original src1 -> dst
                # original src2 -> dst
                # remove second record because removing earlier record would break chain of transfers
                # change to src1 -> dst
                elif visits[vid][i-1]["dstrid"] == visits[vid][i]["dstrid"]:
                    del visits[vid][i]
                    i -= 1
                # destination unit doesnt correspond to next source unit
                elif visits[vid][i-1]["dstrid"] != visits[vid][i]["srcrid"]:
                    # create dummy transfer between destination and next source
                    # transfer time is exactly halfway between arrival
                    new_record = copy.copy(visits[vid][i-1])
                    new_record["tdate"] = visits[vid][i-1]["tdate"] + ((visits[vid][i]["tdate"] - visits[vid][i-1]["tdate"]) / 2)
                    new_record["srcrid"] = visits[vid][i-1]["dstrid"]
                    new_record["srcuid"] = visits[vid][i-1]["dstuid"]
                    new_record["dstrid"] = visits[vid][i]["srcrid"]
                    new_record["dstuid"] = visits[vid][i]["srcuid"]
                    visits[vid].insert(i, new_record)
                else:
                    changes -= 1
                i += 1
            # add new "dummy" transfer record for admission    
            new_record = copy.copy(visits[vid][0])
            # first transfer date after admission date?
            if visits[vid][0]["tdate"] > visits[vid][0]["adate"]:
                # record's transfer date will be admission date
                # unless admission date is before very first record transfer time
                if new_record["adate"] > firsttransfertime:
                    new_record["tdate"] = new_record["adate"]
                else:
                    new_record["tdate"] = firsttransfertime - datetime.timedelta(seconds=1)
            # First transfer before admission date
            else:
                # Make dummy transfer for one second before previous first transfer time
                new_record["tdate"] = new_record["tdate"] - datetime.timedelta(seconds=1)

            # record's transfer destination will be 
            # previous first record's transfer source
            new_record["dstrid"] = new_record["srcrid"]
            new_record["dstuid"] = new_record["srcuid"]
            new_record["srcrid"] = None
            new_record["srcuid"] = None
            visits[vid].insert(0, new_record)

            # add new "dummy" transfer record for discharge
            new_record = copy.copy(visits[vid][-1])
            # last transfer date before discharge date?
            if visits[vid][-1]["tdate"] < visits[vid][-1]["ddate"]:
                # record's transfer date will be discharge date
                new_record["tdate"] = new_record["ddate"]
            # Last transfer after discharge date
            else:
                # Make dummy transfer for one second after previous last transfer time
                new_record["tdate"] = new_record["tdate"] + datetime.timedelta(seconds=1)
            
            # record's transfer source will be
            # previous last record's transfer destination
            new_record["srcrid"] = new_record["dstrid"]
            new_record["srcuid"] = new_record["dstuid"]
            new_record["dstrid"] = None
            new_record["dstuid"] = None
            visits[vid].append(new_record)
            
            # Snippet below is for verifying that patient does not contribute to "drift" for a given uid
            #load = 0
            #for transfer in visits[vid]:
            #    if transfer["srcuid"] == 12:
            #        # patient left micu
            #        load -= 1
            #    if transfer["dstuid"] == 12:
            #        # patient entered micu
            #        load += 1
            #if load != 0:
            #    for t in visits[vid]:
            #        print(t)
            #    input()


            self.visitlengths[vid] = (visits[vid][-1]["tdate"] - visits[vid][0]["tdate"]).total_seconds()
           
            # Actual visit length - expected visit length (delta-los)
            self.deltavisitlengths[vid] = (visits[vid][-1]["tdate"] - visits[vid][0]["tdate"]).total_seconds() - (visits[vid][0]["xlos"] * 60*60*24)
            healedrecords.extend(visits[vid])

        healedrecords.sort(key=lambda x : x["tdate"])

        return healedrecords
    
    def teampatientcounts(self):
        """Tracks the number of patients served by each team over the entire dataset."""
        teams = "ABCD"
        """
        +---------------------------+
        | svc                       |
        +---------------------------+
        | INPT GMED TEAM A DF30-B   |
        | INPT GMED TEAM C DF32-B   |
        | INPT GMED TEAM B DF31-B   |
        | INPT GMED TEAM D DF33-B** | <-- What's the difference here?
        | INPT GMED TEAM D DF33-B   |
        +---------------------------+
        """

        basequery = "select min(t.tdate), max(t.tdate), v.adate, v.ddate, v.vid, v.svc \
                from transfers t, visits v where t.vid = v.vid and v.svc like \
                '%MED TEAM {}%' group by v.vid;"

        
        dailypatientsbyteam = []
        for team in teams:
            visits = self.createdictrecords(self.db.query(basequery.format(team)),
                    "tdate_first", "tdate_last", "adate", "ddate", "svc")
        
            # Set adate = min(tdate_first, adate) and ddate = max(tdate_last, ddate)
            for v in visits:
                v["adate"] = min(v["tdate_first"], v["adate"])
                v["ddate"] = max(v["tdate_last"], v["ddate"])
            
            # Determine earliest and last date in set
            firstdatetime = min(visits, key=lambda x: x["adate"])["adate"]
            lastdatetime = max(visits, key=lambda x: x["ddate"])["ddate"]
            
            # Number of days spanned by set
            daycount = int((lastdatetime - firstdatetime).total_seconds() // 86400)
            
            # Loop through each visit incrementing number of patients being served
            # for the designated span
            patientsservedbyday = [0] * daycount
            for v in visits:
                firstdayservedindex = int((v["adate"] - firstdatetime).total_seconds() // 86400)
                daysserved = int((v["ddate"] - v["adate"]).total_seconds() // 86400)

                # I'm sure this was genius, but as soon as I remember why its so weird, I should probably document it here
                for x in range(min(firstdayservedindex + daysserved, daycount) -
                        firstdayservedindex):
                    patientsservedbyday[firstdayservedindex + x] += 1
                    
            dailypatientsbyteam.append([firstdatetime, patientsservedbyday])
            
        return dailypatientsbyteam

    def team_mstweights(self):
        """Generates minimum spanning trees every day for each team and records
        their weights."""
        teams = "ABCD"
        basequery = ' '.join(["select t.tdate, t.srcuid, t.srcrid, t.dstuid, t.dstrid, v.vid, v.adate, v.ddate",
                    "from transfers t, visits v where t.vid=v.vid and v.svc like '%MED TEAM {}%' order by t.tdate;"])
        
        mstweightsbyteam = []
        for team in teams:
            print(team)
            transfers = self.createdictrecords(self.db.query(basequery.format(team)),
                    "tdate", "srcuid", "srcrid", "dstuid", "dstrid", "vid", "adate", "ddate")
            transfers = self.healrecordsbyroom(transfers)

            firstdatetime = transfers[0]["tdate"]
            #print(firstdatetime)
            #continue
            #print(firstdatetime)
            # begin main loop
            cutoff = firstdatetime + datetime.timedelta(1)
            mstweightsbyday = []
            singledaymstweights = []
            curmstweight = 0
            minspantree = mst.mst(self.singleverttomany, self.alledges)
            day = 0
            for x, t in enumerate(transfers):
                while t["tdate"] >= cutoff:
                    timeweightedmstweight = 0
                    for i, (nextweight, date) in enumerate(singledaymstweights):
                        if i == 0:
                            continue
                        datediff = date - singledaymstweights[i-1][1]
                        # Find the portion of a day that this weight existed
                        daypart = datediff.total_seconds() / 86400
                        if daypart < 0:
                            print("daypart")
                            print(datediff)
                            print(date)
                            print(singledaymstweights[i-1][1])
                            print(i)
                        # We use the previous data point's weight as it is the true weight for the time before the current data point
                        timeweightedmstweight += (singledaymstweights[i-1][0] * daypart)
                    # Same calculation as above, but add remaining time from last data point to end of day
                    enddatediff = cutoff - singledaymstweights[-1][1]
                    enddaypart = enddatediff.total_seconds() / 86400
                    if enddaypart < 0:
                        print("enddaypart")
                    endweight = singledaymstweights[-1][0]
                    timeweightedmstweight += (endweight * enddaypart)

                    mstweightsbyday.append(timeweightedmstweight)
                    singledaymstweights = []
                    singledaymstweights.append((endweight, cutoff))
                    cutoff += datetime.timedelta(1)
                    day += 1
                
                #print(t["srcrid"], t["dstrid"])
                # Iteratively generate mst's
                # New vertex
                if t["srcrid"] is None:
                    minspantree.addvert(t["dstrid"])

                # Remove vertex
                elif t["dstrid"] is None:
                    minspantree.removevert(t["srcrid"])

                # Regular transfer, remove then add back
                else:
                    # Remove from tree
                    minspantree.removevert(t["srcrid"])
                    minspantree.addvert(t["dstrid"])

                curmstweight = minspantree.getweight()
                singledaymstweights.append((curmstweight, t["tdate"]))
           
            mstweightsbyteam.append(mstweightsbyday)
        
        return mstweightsbyteam

    def team_mstedgeweights(self):
        """Generate minimum spanning trees every day for each team and records
        the weights of each edge."""
        teams = "ABCD"
        basequery = ' '.join(["select t.tdate, t.srcuid, t.srcrid, t.dstuid, t.dstrid, v.vid, v.adate, v.ddate",
                    "from transfers t, visits v where t.vid=v.vid and v.svc like '%MED TEAM {}%' order by t.tdate;"])
        
        mstedgeweightsbyteam = []
        for team in teams:
            print(team)
            transfers = self.createdictrecords(self.db.query(basequery.format(team)),
                    "tdate", "srcuid", "srcrid", "dstuid", "dstrid", "vid", "adate", "ddate")
            transfers = self.healrecordsbyroom(transfers)

            firstdatetime = transfers[0]["tdate"]
            #print(firstdatetime)
            #continue
            #print(firstdatetime)
            # begin main loop
            cutoff = firstdatetime + datetime.timedelta(1)
            mstedgeweights = []
            minspantree = mst.mst(self.singleverttomany, self.alledges)
            day = 0
            for x, t in enumerate(transfers):
                
                
                #print(t["srcrid"], t["dstrid"])
                # Iteratively generate mst's
                # New vertex
                if t["srcrid"] is None:
                    minspantree.addvert(t["dstrid"])

                # Remove vertex
                elif t["dstrid"] is None:
                    minspantree.removevert(t["srcrid"])

                # Regular transfer, remove then add back
                else:
                    # Remove from tree
                    minspantree.removevert(t["srcrid"])
                    minspantree.addvert(t["dstrid"])

                mstedgeweights.append(minspantree.getall_edgeweights())
           
            mstedgeweightsbyteam.append(mstedgeweights)
        
        return mstedgeweightsbyteam

    def team_patientdistality(self):
        """Generate minimum spanning trees every day for each team and records
        the weights of each edge."""
        teams = "ABCD"
        basequery = ' '.join(["select t.tdate, t.srcuid, t.srcrid, t.dstuid, t.dstrid, v.vid, v.adate, v.ddate, v.xlos",
                    "from transfers t, visits v where t.vid=v.vid and v.svc like '%MED TEAM {}%' order by t.tdate;"])
        
        patientdistalitybyteam = []
        for team in teams:
            print(team)
            transfers = self.createdictrecords(self.db.query(basequery.format(team)),
                    "tdate", "srcuid", "srcrid", "dstuid", "dstrid", "vid", "adate", "ddate", "xlos")
            transfers = self.healrecordsbyroom(transfers)

            firstdatetime = transfers[0]["tdate"]
            #print(firstdatetime)
            #continue
            #print(firstdatetime)
            # begin main loop
            cutoff = firstdatetime + datetime.timedelta(1)
            patientdistality = dict() # { vid : distality,... }
            roomtovid = dict() # { room : {vid,... },... }
            minspantree = mst.mst(self.singleverttomany, self.alledges)
            day = 0
            for x, t in enumerate(transfers):
                #print(t["srcrid"], t["dstrid"])
                # Iteratively generate mst's
                # New vertex
                if t["srcrid"] is None:
                    minspantree.addvert(t["dstrid"])
                    if t["dstrid"] not in roomtovid:
                        roomtovid[t["dstrid"]] = set()
                    roomtovid[t["dstrid"]].add(t["vid"])

                # Remove vertex
                elif t["dstrid"] is None:
                    minspantree.removevert(t["srcrid"])
                    roomtovid[t["srcrid"]].remove(t["vid"])

                # Regular transfer, remove then add back
                else:
                    # Remove from tree
                    minspantree.removevert(t["srcrid"])
                    minspantree.addvert(t["dstrid"])
                    roomtovid[t["srcrid"]].remove(t["vid"])
                    if t["dstrid"] not in roomtovid:
                        roomtovid[t["dstrid"]] = set()
                    roomtovid[t["dstrid"]].add(t["vid"])
                
                if x < len(transfers) - 1:
                    distalitybyroom = minspantree.compute_distality() # { room : distality,... }
                    for room in distalitybyroom:
                        for vid in roomtovid[room]:
                            if vid in patientdistality:
                                patientdistality[vid] += distalitybyroom[room] * (transfers[x+1]["tdate"] - t["tdate"]).total_seconds()
                            else:
                                patientdistality[vid] = distalitybyroom[room] * (transfers[x+1]["tdate"] - t["tdate"]).total_seconds()
           
            for vid in patientdistality:
                try:
                    patientdistality[vid] /= self.visitlengths[vid]
                except:
                    print(vid)

            patientdistalitybyteam.append(patientdistality)
        
        return patientdistalitybyteam, self.deltavisitlengths

    def singleverttomany(self, single, many):
        query = "SELECT dst, cost FROM paths WHERE src={newvert} and dst IN ({connectedverts});".format(
            newvert=single, connectedverts=','.join([str(a) for a in many])
        )
        return self.createdictrecords(self.db.query(query), "dst", "cost")

    def singleverttosingle(self, vert1, vert2):
        query = "SELECT dst, cost FROM paths WHERE src={v1} and dst={v2};".format(
            v1=vert1, v2=vert2
        )
        return self.createdictrecords(self.db.query(query), "dst", "cost")[0]

    def alledges(self, verts):
        query = "SELECT src, dst, cost FROM paths WHERE src IN ({vertlist}) AND dst in ({vertlist}) and src<dst ORDER BY cost ASC;".format(
            vertlist=','.join([str(a) for a in verts])
        )
        return self.createdictrecords(self.db.query(query), "src", "dst", "cost")

    def visitaddate(self):
        basequery = ' '.join(["select vid, adate, ddate",
                    "from visits where svc like '%MED TEAM {}%'"])
        teams = "ABCD"
        visits = []
        for team in teams:
            query = basequery.format(team)
            visits.append(self.createdictrecords(self.db.query(query), "vid", "adate", "ddate"))
        return visits

    def healedmedteamrecords(self):
        """Generates minimum spanning trees every day for each team and records
        their weights."""
        teams = "ABCD"
        basequery = ' '.join(["select t.tdate, t.srcuid, t.srcrid, t.dstuid, t.dstrid, v.vid, v.adate, v.ddate, v.xlos, v.svc",
                    "from transfers t, visits v where t.vid=v.vid and v.svc like '%MED TEAM {}%' order by t.tdate;"])
        
        alltransfers = []
        for team in teams:
            print(team)
            transfers = self.createdictrecords(self.db.query(basequery.format(team)),
                    "tdate", "srcuid", "srcrid", "dstuid", "dstrid", "vid", "adate", "ddate", "xlos", "svc")
            transfers = self.healrecordsbyroom(transfers)
            alltransfers.extend(transfers)
        alltransfers.sort(key=lambda x: x["tdate"])
        return alltransfers

    def teampaitentdistance(self):
        teams = "ABCD"
        basequery = ' '.join(["select t.tdate, t.srcuid, t.srcrid, t.dstuid, t.dstrid, v.vid, v.adate, v.ddate, v.xlos",
                            "from transfers t, visits v where t.vid=v.vid and v.svc like '%MED TEAM {}%' order by t.tdate;"])
        
        patientdistancebyteam = []
        for team in teams:
            print(team)
            transfers = self.createdictrecords(self.db.query(basequery.format(team)),
                                               "tdate", "srcuid", "srcrid", "dstuid", "dstrid", "vid", "adate",
                                               "ddate", "xlos")
            transfers = self.healrecordsbyroom(transfers)

            firstdatetime = transfers[0]["tdate"]
            #print(firstdatetime)
            #continue
            #print(firstdatetime)
            patientdistance = dict()  # { vid : distance,... }
            patientlocs = dict()  # { vid : rid,... }
            roomtovid = {}
            MICUHOME = 17454
            for x, t in enumerate(transfers):
                # New vertex
                if t["srcrid"] is None:
                    patientlocs[t["vid"]] = t["dstrid"]
                    if t["dstrid"] not in roomtovid:
                        roomtovid[t["dstrid"]] = set()
                    roomtovid[t["dstrid"]].add(t["vid"])

                # Remove vertex
                elif t["dstrid"] is None:
                    del patientlocs[t["vid"]]
                    roomtovid[t["srcrid"]].remove(t["vid"])
                    if len(roomtovid[t["srcrid"]]) == 0:
                        del roomtovid[t["srcrid"]]

                # Regular transfer
                else:
                    patientlocs[t["vid"]] = t["dstrid"]
                    roomtovid[t["srcrid"]].remove(t["vid"])
                    if len(roomtovid[t["srcrid"]]) == 0:
                        del roomtovid[t["srcrid"]]
                    if t["dstrid"] not in roomtovid:
                        roomtovid[t["dstrid"]] = set()
                    roomtovid[t["dstrid"]].add(t["vid"])

                if x < len(transfers) - 1:
                    if len(roomtovid) > 0:
                        distancebyroom = {d["dst"]: d["cost"] for d in self.singleverttomany(MICUHOME, roomtovid.keys())}
                        for room in distancebyroom:
                            for vid in roomtovid[room]:
                                if vid in patientdistance:
                                    patientdistance[vid] += distancebyroom[room] * (transfers[x+1]["tdate"] - t["tdate"]).total_seconds()
                                else:
                                    patientdistance[vid] = distancebyroom[room] * (transfers[x+1]["tdate"] - t["tdate"]).total_seconds()

            for vid in patientdistance:
                try:
                    patientdistance[vid] /= self.visitlengths[vid]
                except:
                    print(vid)

            patientdistancebyteam.append(patientdistance)
        
        return patientdistancebyteam

    """Calculate the portion of a patient's stay spent in the room they frequent the most"""
    def sedentism(self):
        teams = "ABCD"
        basequery = ' '.join(["select t.tdate, t.srcuid, t.srcrid, t.dstuid, t.dstrid, v.vid, v.adate, v.ddate, v.xlos",
                              "from transfers t, visits v where t.vid=v.vid and v.svc like '%MED TEAM {}%' order by t.tdate;"])

        patientsedentismbyteam = []
        for team in teams:
            print(team)
            transfers = self.createdictrecords(self.db.query(basequery.format(team)),
                                               "tdate", "srcuid", "srcrid", "dstuid", "dstrid", "vid", "adate",
                                               "ddate", "xlos")
            transfers = self.healrecordsbyroom(transfers)

            # print(firstdatetime)
            # continue
            # print(firstdatetime)
            roomsvisited = {}  # { vid : [ timespent,..., time entered  }
            for x, t in enumerate(transfers):
                if t["vid"] not in roomsvisited:
                    roomsvisited[t["vid"]] = []
                if len(roomsvisited[t["vid"]]) > 0:
                    roomsvisited[t["vid"]][-1] = (t["tdate"] - roomsvisited[t["vid"]][-1]).total_seconds()
                if t["dstrid"] is not None:
                    roomsvisited[t["vid"]].append(t["tdate"])

            for vid in roomsvisited:
                try:
                    roomsvisited[vid] = max(roomsvisited[vid]) / self.visitlengths[vid]
                except:
                    print(vid)

            patientsedentismbyteam.append(roomsvisited)

        return patientsedentismbyteam
