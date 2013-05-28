#!/usr/bin/python
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk
import sys
import gobject
import sqlite3
import time
import datetime

class RentManager:
    roomColumName = (u"姓名", u"房间名", u"价格")
    guestColumName = (u"客人姓名", u"身份证号")

    def __init__(self):
        self.dbconn = sqlite3.connect('rental.db')
        self.dbconn.text_factory = str
        self.cursor = self.dbconn.cursor()
        
        self.nowDate = time.strftime("%Y-%m-%d").decode("utf-8")
        inputRoomInitData = (u"房间名", u"价格")

        try:
            builder = gtk.Builder()
            builder.add_from_file("ui.glade")
        except BaseException, e:
            self.errorMessage("Fail to load UI file.")
            print e
            sys.exit(1)

        builder.connect_signals(self)
        self.window = builder.get_object("mainWindow")

        self.rentView = builder.get_object("rentView")
        self.rentViewModel = builder.get_object("rentViewModel")
        self.rentViewInit()


        self.returnView = builder.get_object("returnView")
        self.returnViewModel = builder.get_object("returnViewModel")
        self.returnEntryGuestID = builder.get_object("returnGuestID")
        self.returnEntryRoomID = builder.get_object("returnRoomID")
        self.returnViewInit()

        self.queryView = builder.get_object("queryView")
        self.queryViewReaderModel = builder.get_object("queryViewGuestModel")
        self.queryViewRoomModel = builder.get_object("queryViewRoomModel")


        self.inputView = builder.get_object("inputView")
        self.inputViewRoomModel = builder.get_object("inputViewRoomModel")
        self.inputViewGuestModel = builder.get_object("inputViewGuestModel")
        self.inputViewModel = None
        self.inputRoom()


    def rentViewInit(self):
        columName = (u"客人姓名", u"房间名", "身份证号", u"租出日期", u"租赁时长")
        columEditAttr = (True, True, True, False, True)
        for columnNum in range(len(columName)):
            renderer = gtk.CellRendererText()
            renderer.set_data("column", columnNum)
            renderer.set_property("editable", columEditAttr[columnNum])
            if columEditAttr[columnNum]:
                renderer.connect("edited", self.on_rent_cell_edited)
            column = gtk.TreeViewColumn(columName[columnNum], renderer, 
                                        text=columnNum)
            column.set_resizable(True)
            self.rentView.append_column(column)

    def returnViewInit(self):
        columName = (u"租赁记录", u"房间名", u"客人姓名",  u"租出日期", u"租赁时长")
        for columnNum in range(len(columName)):
            renderer = gtk.CellRendererText()
            column = gtk.TreeViewColumn(columName[columnNum], renderer, 
                                        text=columnNum)
            column.set_resizable(True)
            self.returnView.append_column(column)

    # QueryView
    def queryViewSetColumn(self, columName):
        self.queryRecord = 0
        columns = self.queryView.get_columns()
        for c in columns:
            self.queryView.remove_column(c)
        
        self.queryViewModel.clear()
        self.queryView.set_model(self.queryViewModel)
        for columnNum in range(len(columName)):
            renderer = gtk.CellRendererText()
            renderer.set_property("editable", True)
            column = gtk.TreeViewColumn(columName[columnNum], renderer, 
                                        text=columnNum)
            column.set_resizable(True)
            self.queryView.append_column(column)


    def queryGuest(self):
        self.queryViewModel = self.queryViewReaderModel
        self.queryViewSetColumn(self.guestColumName)
        self.cursor.execute("SELECT COUNT(*) FROM Guest")
        self.maxRecords = self.cursor.fetchone()[0]
        print self.maxRecords

    def queryRoom(self):
        self.queryViewModel = self.queryViewRoomModel
        self.queryViewSetColumn(self.roomColumName)
        self.cursor.execute("SELECT COUNT(*) FROM Room")
        self.maxRecords = self.cursor.fetchone()[0]
        print self.maxRecords

    #inputView
    def inputViewSetColumn(self, columName):
        columns = self.inputView.get_columns()
        for c in columns:
            self.inputView.remove_column(c)
        
        self.inputViewModel.clear()
        self.inputView.set_model(self.inputViewModel)
        for columnNum in range(len(columName)):
            renderer = gtk.CellRendererText()
            renderer.set_property("editable", True)
            renderer.set_data("column", columnNum)
            renderer.connect("edited", self.on_input_cell_edited)

            column = gtk.TreeViewColumn(columName[columnNum], renderer, text=columnNum)
            column.set_resizable(True)
            self.inputView.append_column(column)

    def inputGuest(self):
        self.inputViewModel = self.inputViewGuestModel
        self.inputViewSetColumn(self.guestColumName)

    def inputRoom(self):
        self.inputViewModel = self.inputViewRoomModel
        self.inputViewSetColumn(self.roomColumName[1:])

    #Callback Functions
    def on_mainWindow_delete_event(self, widget, data=None):
        print "destroy signal occurred"
        gtk.main_quit()

    #BorrowView
    def on_rentAdd_clicked(self, button, data = None):
        self.rentViewModel.append(('请输入姓名', '房间', '请输入身份证号', self.nowDate, 12))

    def on_rentDel_clicked(self, button, data = None):
        selection = self.rentView.get_selection()
        model, iter = selection.get_selected()
        if iter:
            model.remove(iter)

    def on_rentClear_clicked(self, button, data = None):
        self.rentViewModel.clear()

    def on_rentSubmit_clicked(self, button, data = None):
        # TODO
        for row in self.rentViewModel:
            guestName = row[0]
            roomName = row[1]
            IDNum = row[2]
            rentDate = row[3]
            rentMonth = row[4]
            print guestName, roomName, IDNum, rentDate, rentMonth
            print "Insert value"
            self.cursor.execute("""INSERT INTO Guest(guestName, IDNum)
                                    VALUES (?, ?)""", (guestName, IDNum))

            self.cursor.execute("SELECT guestID FROM Guest WHERE guestName=?",
                                    [guestName])
            guestID = self.cursor.fetchone()[0]
            
            self.cursor.execute("SELECT roomID FROM Room WHERE roomName = ?", 
                                    [roomName])
            roomID = self.cursor.fetchone()[0]

            print guestID, roomID

            #self.cursor.execute("SELECT * FROM Guest \
            #                        WHERE guestName = ? AND IDNum = ?", (guestName, IDNum))


            sql = """INSERT INTO Rent(guest, room, rentDate, rentMonth)
                    VALUES (?, ?, ?, ?)"""
            self.cursor.execute(sql, (guestID, roomID, rentDate, rentMonth))

        self.dbconn.commit()
        self.infoMessage(u"租赁记录已经成功提交。")
        self.rentViewModel.clear()

    def on_rent_cell_edited(self, cell, path_string, new_text):
        model = self.rentViewModel
        iter = model.get_iter_from_string(path_string)
        column = cell.get_data("column")
        if column == 4:
            try:
                id = int(new_text)
            except ValueError, e:
                print e
                self.errorMessage(u"请输入纯数字记录。")
                return

        if column == 0:
            model.set(iter, column, new_text)

        if column == 1:
            self.cursor.execute("SELECT * FROM Room where roomName = ?", [new_text])
            if self.cursor.fetchone():
                model.set(iter, column, new_text)
                self.cursor.execute("SELECT * FROM rentRecord WHERE roomName = ?", [new_text])
                if self.cursor.fetchone():
                    self.errorMessage(u"房间: %s 已出租" % new_text)
            else:
                self.errorMessage(u"不存在该房间: %s。" % new_text)

        if column == 2:
            model.set(iter, column, new_text)

        if column == 4:
            model.set(iter, column, id)

    #QueryView
    def on_queryEmptyRoom_clicked(self, button, data = None):
        self.queryRoom()
        self.cursor.execute("""SELECT roomID, roomName, roomPrice FROM Room
                WHERE NOT EXISTS (SELECT * FROM Rent WHERE roomID=room)
                LIMIT ? OFFSET ?""", [15, 0])
        for row in self.cursor:
            print row
            self.queryViewModel.append(row)

    def on_queryRoom_clicked(self, button, data = None):
        self.queryRoom()
        self.cursor.execute("SELECT roomID, roomName, roomPrice FROM Room LIMIT ? OFFSET ?", [15, 0])
        for row in self.cursor:
            print row
            self.queryViewModel.append(row)

    def on_queryGuest_clicked(self, button, data = None):
        self.queryGuest()
        self.cursor.execute("SELECT guestID, guestName, IDnum FROM Guest LIMIT ? OFFSET ?", [15, 0])
        for row in self.cursor:
            self.queryViewModel.append(row)

    def on_queryPrev_clicked(self, button, data = None):
        if self.queryRecord == 0:
            self.errorMessage(u"已到最前页。")
            return
        self.queryRecord -= 15
        self.queryViewModel.clear()

        if self.queryViewModel.get_n_columns() == 9:
            self.cursor.execute("SELECT * FROM Room LIMIT ? OFFSET ?",[15, self.queryRecord])

        elif self.queryViewModel.get_n_columns() == 4:
            self.cursor.execute("SELECT * FROM Guest LIMIT ? OFFSET ?",[15, self.queryRecord])

        for row in self.cursor:
            self.queryViewModel.append(row)


    def on_queryNext_clicked(self, button, data = None):
        if self.queryRecord + 15 > self.maxRecords:
            self.errorMessage(u"已到最后页。")
            return

        self.queryRecord += 15
        self.queryViewModel.clear()

        if self.queryViewModel.get_n_columns() == 9:
            self.cursor.execute("SELECT * FROM Room LIMIT ? OFFSET ?",[15, self.queryRecord])

        elif self.queryViewModel.get_n_columns() == 4:
            self.cursor.execute("SELECT * FROM Guest LIMIT ? OFFSET ?",[15, self.queryRecord])

        for row in self.cursor:
            self.queryViewModel.append(row)


    def on_returnQuery_clicked(self, button, data = None):
        print 'on_returnQuery_clicked'
        guestid = self.returnEntryGuestID.get_text()
        roomid = self.returnEntryRoomID.get_text()

        print guestid, roomid

        if len(guestid) and len(roomid):
            self.cursor.execute("SELECT rentID, roomName, guestName,\
                                rentDate, rentMonth FROM rentRecord \
                                WHERE guestID = ? AND roomName = ?", [guestid, roomid])
        elif len(guestid):
            self.cursor.execute("SELECT rentID, roomName, guestName,\
                                rentDate, rentMonth FROM rentRecord \
                                WHERE guestName LIKE"+" '%"+guestid+"%'")
        elif len(roomid):
            self.cursor.execute("SELECT rentID, roomName, guestName,\
                                rentDate, rentMonth FROM rentRecord \
                                WHERE roomName = ?", [roomid])
        else:
            print "in else"
            self.cursor.execute("SELECT rentID, roomName, guestName,\
                                rentDate, rentMonth FROM rentRecord")

        self.returnViewModel.clear()

        for row in self.cursor:
            print row
            self.returnViewModel.append(row)
                

    def on_returnCommit_clicked(self, button, data = None):
        selection = self.returnView.get_selection()
        model, iter = selection.get_selected()
        if iter:
            print "iter"
            rentDate = time.strptime(model.get_value(iter, 3), "%Y-%m-%d")
            timeDelta = datetime.date.today() - datetime.date(*rentDate[0:3])
            rentDays = timeDelta.days

            roomName = model.get_value(iter, 1)
            self.cursor.execute("DELETE FROM Rent WHERE room = ?", [roomName])
            self.dbconn.commit()
            guestName = model.get_value(iter, 2)
            self.infoMessage(u"客人  %s  所租赁%s 退房。 租出%d天" % (guestName, roomName, rentDays))
            model.remove(iter)

    #inputView
    def on_inputGuest_clicked(self, button, data = None):
        self.inputGuest()

    def on_inputRoom_clicked(self, button, data = None):
        self.inputRoom()

    def on_inputAdd_clicked(self, button, data = None):
        if not self.inputViewModel:
            self.errorMessage(u"请先选择录入类型。")
            return
        count = self.inputViewModel.get_n_columns()
        if count == 3:
            inputGuestInitData = (u"姓名", u"性别", u"身份证")
            self.inputViewModel.append(inputGuestInitData)
        elif count == 2:
            inputRoomInitData = (u"房间名", u"价格")
            self.inputViewModel.append(inputRoomInitData)

    def on_inputDel_clicked(self, button, data = None):
        selection = self.inputView.get_selection()
        model, iter = selection.get_selected()
        if iter:
            model.remove(iter)

    def on_inputSubmit_clicked(self, button, data = None):
        count = self.inputViewModel.get_n_columns()
        for row in self.inputViewModel:
            #录入房间
            if count == 2:
                dataRow = []
                for obj in row:
                    if isinstance(obj, str):
                        dataRow.append(obj.decode("utf-8"))
                    else:
                        dataRow.append(obj)
                print dataRow
                self.cursor.execute(u"INSERT INTO Room(roomName, roomPrice) VALUES (?, ?)",\
                                    dataRow)
        self.dbconn.commit()
        self.infoMessage(u"记录已经成功提交。")
        self.inputViewModel.clear()

    def on_input_cell_edited(self, cell, path_string, new_text):
        iter = self.inputViewModel.get_iter_from_string(path_string)
        column = cell.get_data("column")
        columnCount = self.inputViewModel.get_n_columns()
        if columnCount == 3:
            self.inputViewModel.set(iter, column, new_text)
        elif columnCount == 2:
            if self.inputViewModel.get_column_type(column) == gobject.TYPE_FLOAT:
                try:
                    self.inputViewModel.set(iter, column, float(new_text))
                except ValueError, e:
                    self.errorMessage(u"请输入价格。")
                    return
            elif self.inputViewModel.get_column_type(column) == gobject.TYPE_UINT:
                try:
                    self.inputViewModel.set(iter, column, int(new_text))
                except ValueError, e:
                    self.errorMessage(u"请输入整数。")
                    return
            else:
                self.inputViewModel.set(iter, column, new_text)

    def errorMessage(self, message):
        print message
        dialog = gtk.MessageDialog(None,
                                   gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                   gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, message)
        dialog.run()
        dialog.destroy()

    def infoMessage(self, message):
        print message
        dialog = gtk.MessageDialog(None,
                                   gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                   gtk.MESSAGE_INFO, gtk.BUTTONS_OK, message)
        dialog.run()
        dialog.destroy()

    def main(self):
        self.window.show()
        gtk.main()

if __name__ == "__main__":
    app = RentManager()
    app.main()
