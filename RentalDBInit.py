#!/usr/bin/python
# -*- coding: utf8 -*-

import sqlite3
import os

DB_FILE = 'rental.db'

def RentDbInit(con):
    c = con.cursor()

    c.execute("""
    CREATE TABLE `Room` (
    `roomID` INTEGER PRIMARY KEY AUTOINCREMENT,
    `roomName` VARCHAR(10) UNIQUE NOT NULL,
    `roomPrice` INTEGER
    )
    """)

    c.execute("""
    CREATE TABLE `Guest` (
    `guestID` INTEGER PRIMARY KEY AUTOINCREMENT,
    `guestName` VARCHAR(10) ,
    `IDNum` VARCHAR(18) ,
    `guestInfo` VARCHAR(40)
    )
    """)

    c.execute("""
    CREATE TABLE `Rent` (
    `rentID` INTEGER PRIMARY KEY AUTOINCREMENT,
    `room` INTEGER UNIQUE NOT NULL,
    `guest` INTEGER NOT NULL,
    `rentDate` TEXT,
    `rentMonth` INTEGER,
    FOREIGN KEY(room) REFERENCES Room(roomID),
    FOREIGN KEY(guest) REFERENCES Guest(guestID)
    )
    """)

    c.execute("""CREATE VIEW rentRecord AS
                    SELECT rentID, roomName, guestName, rentDate, rentMonth
                    FROM Room, Rent, Guest
                    WHERE roomID=room AND guestID=guest
        """)

    rooms = (   ('310', 1200),
                ('312', 1300),
                ('318', 1300),
                ('320', 1300),
                ('321', 1300),
                ('322', 1300),
                ('323', 1300),
                ('324', 1300),
                ('325', 1300),
                ('326', 1300),
                ('327', 1300),
                ('328', 1300),
                ('329', 1300),
                ('330', 1300))

    for r in rooms:
        c.execute("INSERT INTO Room(roomName, roomPrice) VALUES (?,?)", r)

    guests = ((u"子夜", u"1234567890", u""),
    (u"杨杰", u"09876543", u""),
    (u"刘三", u"7781341", u""),
    (u"陈一明", u"234523245", u""),
    (u"张三", u"23452", u""),
    (u"何明", u"142432", u""),
    (u"陈中", u"112351234", u""))

    for r in guests:
        c.execute("INSERT INTO Guest(guestName, IDNum, guestInfo) VALUES (?,?,?)", r)

    rents = ((1, 1, u"2009-06-20", 48),
    (2, 2, u"2010-05-22", 36),
    (3, 3, u"2011-09-10", 48),
    (4, 5, u"2012-09-10", 24),
    (5, 4, u"2012-08-30", 36),
    (6, 6, u"2012-04-20", 24),
    (7, 7, u"2013-04-20", 12))

    for r in rents:
        c.execute("INSERT INTO Rent(room, guest, rentDate, rentMonth) VALUES (?,?,?,?)", r)

    # Save (commit) the changes
    con.commit()

if __name__ == "__main__":
    os.system('rm -f %s' % DB_FILE)
    RentDbInit(sqlite3.connect(DB_FILE))

