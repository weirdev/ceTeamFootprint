#!/usr/bin/env python2
import dbcom
import pickle

unittoroom = {}
with dbcom.DBCom() as db:
    unitquery = "SELECT uid FROM units;"
    units = [u[0] for u in db.query(unitquery)]
    baseroomquerydst = "SELECT dstrid FROM transfers WHERE dstuid={} AND dstrid<>0 ORDER BY tdate DESC LIMIT 1;"
    baseroomquerysrc = "SELECT srcrid FROM transfers WHERE srcuid={} AND srcrid<>0 ORDER BY tdate DESC LIMIT 1;"
    for unit in units:
        room = db.query(baseroomquerydst.format(unit))
        if len(room) > 0:
            unittoroom[unit] = room[0][0]
        else:
            room = db.query(baseroomquerysrc.format(unit))
            if len(room) > 0:
                unittoroom[unit] = room[0][0]

with open("unitstoroom.pickle", "wb") as f:
    pickle.dump(unittoroom, f)
