from flask import Blueprint, render_template, abort, flash
from flask import request
from asst.auth import require_role
from itertools import *
from asst.models import hotel, room, breakfast, service,  res, review, includes, roomreview_evaluates, breakfastreview_asseses, servicereview_rates
from flask_table import Table, Col, ButtonCol
import flask_login
import datetime
from dateutil.parser import parse
import traceback, sys
import math
import random
import json
import time

page = Blueprint('feedback', __name__, template_folder='templates')
inv_no = '1'
rrate = '-1'
bfrate = '-1'
srate = '-1'
ReviewType = '-1'
choice = 'no'
servtype = "sno"
breakftype = "bno"
rootype = 'rno'
rno = '1'
hid = '0'
ReviewIDtest = '0'
class ItemTable(Table):
    '''
    This is a itemTable class that generates text/html automatically to create a table for created reservations
    '''
    html_attrs = {'class': 'table table-striped'}
    inv = Col('Invoice No')
    out_date = Col('Check Out')
    in_date = Col('Check In')
    room_no = Col('Room Number')
    hotel_id = Col('Hotel ID')

class ItemTable2(Table):
    '''
    This is a itemTable class that generates text/html automatically to create a table for created reservations
    '''
    html_attrs = {'class': 'table table-striped'}
    serv = Col('Service Ordered')
    inv = Col('Invoice No')
    hotel_id = Col('Hotel ID')

class ItemTable3(Table):
    '''
    This is a itemTable class that generates text/html automatically to create a table for created reservations
    '''
    html_attrs = {'class': 'table table-striped'}
    inv = Col('Invoice No')
    brktype = Col('Breakfast Type')
    hotel_id = Col('Hotel ID')

@page.route('/', methods=['GET'])
@require_role(['admin','manager', 'customer'],getrole=True) # Example of requireing a role(and authentication)
def feedback(role):
    return render_template('feedback/index.html', logged_in=True,role=role)

@page.route("/pick_res",methods=['GET'])
@require_role(['admin','manager', 'customer'],getrole=True) # Example of requireing a role(and authentication)
def pick_res(role):
    reserv = []
    reserv2 = []
    reserv3 = []
    hotel_id = -1
    global inv_no
    global rno
    global hid
    try:
        user = flask_login.current_user
        cid = user.CID
        INV_NO = request.args.get('id')
        inv_no = INV_NO
    except:
        traceback.print_exc(file=sys.stdout)
        flash("Could not find any rooms for the specified dates", 'danger')
        return render_template('feedback/index.html', logged_in=True,role=role)
    for r in res.Reservation.select().where(res.Reservation.CID == cid, res.Reservation.InvoiceNo == inv_no):
        try:
            reserv.append(dict(inv = r.InvoiceNo, ordered = r.ResDate, out_date = r.OutDate, in_date = r.InDate, room_no = r.Room_no, hotel_id = r.HotelID, \
                               cnumber = r.CNumber, totalamt = r.TotalAmt, cid = r.CID))
            rno = r.Room_no
            hid = r.HotelID
        except:
            traceback.print_exc(file=sys.stdout)
            continue
    for s in includes.Cont_Service.select().where(includes.Cont_Service.InvoiceNo == inv_no):
        try:
            reserv2.append(dict(serv = s.sType, inv = s.InvoiceNo, hotel_id = s.HotelID ))
        except:
            traceback.print_exc(file=sys.stdout)
            continue
    for bf in includes.Inc_Breakfast.select().where(includes.Inc_Breakfast.InvoiceNo == inv_no):
        try:
            reserv3.append(dict(inv = bf.InvoiceNo, brktype = bf.BType, hotel_id = bf.HotelID))
        except:
            traceback.print_exc(file=sys.stdout)
            continue
    table = ItemTable(reserv)
    table2 = ItemTable2(reserv2)
    table3 = ItemTable3(reserv3)
    return render_template('feedback/make_rev.html', logged_in=True,role=role, table = table, table2 = table2, table3 = table3)

@page.route("/rating", methods=['POST'])
@require_role(['admin','manager', 'customer'],getrole=True) # Example of requireing a role(and authentication)
def get_rating_and_global(role):
    global rrate
    global bfrate
    global srate
    global ReviewType
    global rtype
    global bftype
    global stype
    global rate
    hold = []
    try:
        data = request.get_json()

        rate = data['radioValue']
        RevType = data['ReviewType']
        if(RevType == 1):
            rrate = rate
        elif(RevType == 2):
            bfrate = rate
        elif(RevType == 3):
            srate = rate
        roomtype = data['rootype']
        breaktype = data['breakftype']
        servtype = data['servtype']
        ReviewType = RevType
        rtype = roomtype
        bftype = breaktype
        stype = servtype
        hold.append([RevType])
        return json.dumps(hold)
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return "Error", 500


@page.route("/load_Res", methods=['POST'])
@require_role(['admin','manager', 'customer'],getrole=True) # Example of requireing a role(and authentication)
def get_reserv(role):
    try:
        data = request.get_json()
        RevType = data['RevType']
        reserv = []
    #    bf = 'none'
    #    serv = 'none'
        rmtype = 'none'
        user = flask_login.current_user
        cid = user.CID
        for r in res.Reservation.select().where(res.Reservation.CID == cid):
            invoic_no = r.InvoiceNo
           # for b in includes.Inc_Breakfast.select().where(includes.Inc_Breakfast.InvoiceNo == invoic_no):
            #    bf.append(b)
           # for se in includes.Cont_Service.select().where(includes.Cont_Service.InvoiceNo == invoic_no):
           #     serv.append(se)
            for rt in room.Room.select().where(room.Room.Room_no == r.Room_no):
                rmtype = rt.Type
            reserv.append([r.HotelID, rmtype, r.Room_no, r.InvoiceNo])
        return json.dumps(reserv)
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return "Error", 500

    return render_template('feedback/index.html', logged_in=True,role=role)
@page.route('/success',methods=['GET', 'POST'])
@require_role(['admin','manager', 'customer'],getrole=True) # Example of requireing a role(and authentication)
def rreview(role):
    SCounter = 0
    global inv_no
    print(str(inv_no))
    global ReviewType
    global rtype
    global bftype
    global stype
    global rrate
    global bfrate
    global srate
    global rno
    global hid
    global ReviewIDtest
    print(str(ReviewType))
    print(str(rrate))
    print(str(rtype))
    Text = 'hi'
    if SCounter == 0:
        try:
            user = flask_login.current_user
            cid = user.CID
            if ReviewType == 1:
                for q in res.Reservation.select().where(res.Reservation.CID == cid, res.Reservation.InvoiceNo == inv_no):
                    print("Reservation: " + str(q))
                    try:
                        for rm in room.Room.select().where(room.Room.HotelID == q.HotelID, room.Room.Room_no == q.Room_no):
                            print("Room Info: " + str(rm))
                            print("Room Type: " + str(rm.Type))
                            try:
                                if rm.Type == rtype:
                                    Text = request.form['description']
                                    print("Room Description: " + str(Text))
                                    SCounter += 1
                                    #rvw = review.writes_Review.create_review(rrate, Text, cid, inv_no)
                            except:
                                continue
                    except:
                        traceback.print_exc(file=sys.stdout)
                        flash("There was an error processing your request. Please try again", 'danger')
                        return render_template('feedback/index.html', logged_in=True, role=role)
            elif ReviewType == 2:
                for q in res.Reservation.select().where(res.Reservation.CID == cid, res.Reservation.InvoiceNo == inv_no):
                    print("Reservation: " + str(q))
                    try:
                        for food in includes.Inc_Breakfast.select().where(includes.Inc_Breakfast.InvoiceNo == inv_no):
                            print("Breakfast Info: " + str(food))
                            print("Breakfast Type: " + str(food.BType))
                            try:
                                if food.BType == bftype:
                                    Text = request.form['description2']
                                    print("Food Description: " + str(Text))
                                    SCounter += 1
                                    #rvw = review.writes_Review.create_review(bfrate, Text, cid, inv_no)
                            except:
                                continue
                    except:
                        traceback.print_exc(file=sys.stdout)
                        flash("There was an error processing your request. Please try again", 'danger')
                        return render_template('feedback/index.html', logged_in=True, role=role)
            elif ReviewType == 3:
                for q in res.Reservation.select().where(res.Reservation.CID == cid, res.Reservation.InvoiceNo == inv_no):
                    print("Reservation: " + str(q))
                    try:
                        for ser in includes.Cont_Service.select().where(includes.Cont_Service.InvoiceNo == inv_no):
                            print("Service Info: " + str(ser))
                            print("Service Type: " + str(ser.sType))
                            try:
                                if ser.sType == stype:
                                    Text = request.form['description3']
                                    print("Service Description: " + str(Text))
                                    SCounter += 1
                                    #rvw = review.writes_Review.create_review(srate, Text, cid, inv_no)
                            except:
                                continue
                    except:
                        traceback.print_exc(file=sys.stdout)
                        flash("There was an error processing your request. Please try again", 'danger')
                        return render_template('feedback/index.html', logged_in=True, role=role)
        except:
            traceback.print_exc(file=sys.stdout)
            flash("There was an error processing your request. Please try again", 'danger')
            return render_template('feedback/index.html', logged_in=True,role=role)
        if SCounter > 0:
            if ReviewType == 1:
                rvw = review.writes_Review.create_review(rrate, Text, cid, inv_no)
                for test in review.writes_Review.select().where(review.writes_Review.Rating == rrate, review.writes_Review.TextComment == Text, review.writes_Review.InvoiceNo == inv_no):
                    try:
                        ReviewIDtest = test.ReviewID
                    except:
                        continue
                rmrvw = roomreview_evaluates.RoomReview_evaluates.create_rmreview(ReviewIDtest, rno, hid)
            elif ReviewType == 2:
                rvw = review.writes_Review.create_review(bfrate, Text, cid, inv_no)
                for test in review.writes_Review.select().where(review.writes_Review.Rating == bfrate, review.writes_Review.TextComment == Text, review.writes_Review.InvoiceNo == inv_no):
                    try:
                        ReviewIDtest = test.ReviewID
                    except:
                        continue
                bfrvw = breakfastreview_asseses.BreakfastReview_asseses.create_brkreview(ReviewIDtest, bftype, hid)
            elif ReviewType == 3:
                rvw = review.writes_Review.create_review(srate, Text, cid, inv_no)
                for test in review.writes_Review.select().where(review.writes_Review.Rating == srate, review.writes_Review.TextComment == Text, review.writes_Review.InvoiceNo == inv_no):
                    try:
                        ReviewIDtest = test.ReviewID
                    except:
                        continue
                srvw = servicereview_rates.ServiceReview_rates.create_servreview(ReviewIDtest, stype, hid)
            return render_template('feedback/success.html', logged_in=True, role=role)
        else:
            flash("error, please review only for things that were actually ordered.", 'danger')
            return render_template('feedback/index.html', logged_in=True, role=role)

