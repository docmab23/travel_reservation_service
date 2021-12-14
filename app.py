from flask import Flask, render_template, request, redirect, url_for, session, render_template_string
import hashlib
# from flask_mysqldb import MySQLpip
import mysql.connector
import re
import sys
import json
from datetime import date
from datetime import datetime

from flask_bootstrap import Bootstrap


def intersection(lst1, lst2):
    return list(set(lst1) & set(lst2))

today = date.today()

app = Flask(__name__, static_url_path="")
Bootstrap(app)
app.secret_key = 'cs4400fall2021'

users=["admin","cowner" ,"customer","owner"]
db_connection = mysql.connector.connect(host="localhost",
                                        user="root",
                                        passwd="armaloc23",
                                        db="travel_reservation_service",
                        )

@app.route('/', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('index.html', msg='')

    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        cursor = db_connection.cursor(buffered=True)
        email = request.form['email']
        password = request.form['password']
        select_statement = "SELECT * FROM Accounts WHERE Email = %s AND Pass = %s "
        cursor.execute(select_statement, (email, password))
        result = cursor.fetchall()
        print(result)

        #If it finds the user credentials in the DB, it then seeks to update the session accordingly
        if result:
            #checkForPermissions()
            session['loggedin'] = True
            session['username'] = email
            
            query2="SELECT EXISTS(SELECT * FROM admins WHERE Email= %s)"
            cursor.execute(query2,(email,))
            data=cursor.fetchall()
            if data[0][0]==1:
                session['userType'] = users[0]
                return redirect("/admin")
            else:
                 query3="SELECT EXISTS(SELECT * FROM Customer WHERE Email= %s)"
                 query4="SELECT EXISTS(SELECT * FROM owners WHERE Email= %s)"
                 cursor.execute(query3,(email,))
                 data1=cursor.fetchall()
                 cursor.execute(query4,(email,))
                 data2=cursor.fetchall()
                 if data1[0][0]==1 and data2[0][0]==1:
                     session['userType'] = users[1]
                     return redirect("/choice")
                 elif data1[0][0]:
                     session['userType'] = users[2]
                     print(session["userType"])
                     return redirect("/customer")
                 elif data2[0][0]==1:
                     session['userType'] = users[3]
                     return redirect("/owner")
                 
        else:
            msg="Login Failed , You need to register"

        cursor.close()  
    #print(session["userType"])
    return render_template("index.html", msg=msg)      




# @app.route('/logout', methods=['GET'])
# def logout():
#     session.pop('loggedin', None)
#     session.pop('username', None)
#     return redirect(url_for('login'))
#
#

@app.route('/register_customer', methods=['GET', 'POST'])
def register_customer():
    # Output message if something goes wrong...
    msg = ''
    # Check if POST requests exist (user submitted form)
    if request.method == 'POST':
        # Create variables for easy access
        email = request.form['email'],
        phonenumber = request.form['phonenumber'],
        password = request.form['password'],
        confirm_password = request.form['confirm_password'],
        firstname = request.form['firstName'],
        lastname = request.form['lastName'],

        cardno = request.form['cardno']
        cvvno = request.form['cvvno']
        expire = request.form['expire']
        expire = expire+"-01"
        location = 'no location'

    # Check if account exists using MySQL
        # cursor = db_connection.cursor(mysql.connector.cursors.DictCursor)
        cursor = db_connection.cursor()
        cursor.execute(
            'SELECT * FROM Accounts WHERE Email = %s',(email) )
        account = cursor.fetchone()
        print(account)
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
            return render_template('register_customer.html', msg=msg)
        elif not re.match(r'[A-Za-z]+', firstname[0]):
            msg = 'Firstname must contain only characters!'
            return render_template('register_customer.html', msg=msg)
        elif not re.match(r'[A-Za-z]+', lastname[0]):
            msg = 'Lastname must contain only characters!'
            return render_template('register_customer.html', msg=msg)
        elif len(password[0]) < 8:
            msg = 'Please choose a password length of at least 8!'
            return render_template('register_customer.html', msg=msg)
        elif password != confirm_password:
            msg = 'Passwords do not match!'
            return render_template('register_customer.html', msg=msg)
        else:
            cursor.callproc('register_customer', (email[0], firstname[0],
                                                  lastname[0], password[0], phonenumber[0], cardno, cvvno, expire, location[0]))
            db_connection.commit()
            cursor.close()
            msg = 'Successfully registered!'
            return render_template('index.html', msg=msg)
    return render_template('register_customer.html', msg=msg)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if session["userType"]==users[0]:
     return render_template("admin.html")
    else:
        return render_template("index.html")

@app.route('/choice', methods=['GET', 'POST'])
def choice():
    return render_template("choice.html")

@app.route('/admin/sc_flight', methods=['GET', 'POST'])
def sc_flight():
         cur_date=today
         query="SELECT Airline_Name from airline"
         cursor = db_connection.cursor()
         cursor.execute(query)
         airlines= cursor.fetchall()
         airlines=[a[0] for a in airlines]
         print(session['username'])
         if request.method=="POST":
           fno=str(request.form['Fno'])
           f_airport=request.form['From Airport']
           t_airport=request.form['To Airport']
           d_time=request.form['d_time']
           a_time=request.form['a_time']
           f_date=str(request.form['Flight Date'])
           c_date=str(request.form['Current Date'])
           cost=float(request.form['Cost per person'])
           cpc=int(request.form['Capacity'])
           airline_=request.form['airlines']
           d_time = datetime.strptime(d_time, "%H:%M")
           d_time=str(d_time.strftime("%H:%M:%S"))
           a_time= datetime.strptime(a_time, "%H:%M")
           a_time= str(a_time.strftime("%H:%M:%S"))
           print(session['username'])
           print(fno,airline_,f_airport,t_airport,d_time,a_time,f_date,cost,cpc,c_date)
           if request.form.get('sc')=='Schedule Flight':

                #q=("call schedule_flight(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
                if t_airport !=f_airport:
                 cursor.callproc("schedule_flight",(fno,airline_,f_airport,t_airport,d_time,a_time,f_date,cost,cpc,c_date))
                 db_connection.commit()
                 print(type(a_time))
                 res=cursor.fetchall()
                 print(res)
           if request.form.get('cancel')=='Cancel':
               return render_template("sc_flight.html",airlines=airlines,cur_date=cur_date)

            
          





           print(t_airport,f_airport)


    


         return render_template("sc_flight.html",airlines=airlines,cur_date=cur_date)

@app.route('/admin/remove_flight',methods=["GET","POST"])
def remove_flight():
    i=0
    cur_date='2021-09-18'
    q3="SELECT Flight_Num,Airline_Name,Flight_Date from flight"
    cursor = db_connection.cursor()
    cursor.execute(q3)
    fl=cursor.fetchall()
    fl1= ["".join(f[0:2]) for f in fl ]
    print(session["username"])

    query="SELECT Airline_Name from airline"
    cursor.execute(query)
    airlines= cursor.fetchall()
    airlines=[a[0] for a in airlines]
    if request.method=="POST":
     fno=request.form['Fno']
     date1=request.form['Date1']
     date2=request.form['Date2']
     air=request.form['airlines']

     '''if fno != None and date1!=None and date2!=None and air!=None:
      query2="SELECT Flight_Num,Airline_Name,Flight_Date from flight WHERE Flight_Num = %s and Flight_Date between %s and %s and air = %s"
      print(fno)
      cursor.execute(query2,(fno,date2,date1,air))
      fl=cursor.fetchall()
      print(fl)'''
     print(fno)
     if fno:
            query3="SELECT Flight_Num,Airline_Name,Flight_Date from flight WHERE Flight_Num = %s"
            cursor.execute(query3,(fno,))
            fj=cursor.fetchall()
            fl=intersection(fl,fj)
     
     if date1 and date2:
           if date2 > date1:
             query="SELECT Flight_Num,Airline_Name,Flight_Date from flight WHERE Flight_Date between %s and %s"
             cursor.execute(query,(date1,date2))
             fk=cursor.fetchall()
             fl=intersection(fl,fk)
           else:
               print("Date input wrong")  
     print(fl)
     if air:
            queryx="SELECT Flight_Num,Airline_Name,Flight_Date from flight WHERE Airline_Name =%s"
            cursor.execute(queryx,(air,))
            fm=cursor.fetchall()
            fl=intersection(fl,fm)
            #print(fl)

     fl=list(fl)
     fl=[list(f) for f in fl]
     #print(fl)
     if request.form.get("options"):
      option = request.form.getlist('options')
    # print(option)
     #option = request.form.getlist('options')
     #flight_num,airline_name=option[0],option[1]
     #print((option))
    # print(flight_num,airline_name)
      f_no= (option[0].split(",")[0].replace("[","").replace("(","").replace("'",""))
      a_no= option[0].split(",")[1].replace("'","")
      #a_no= set(a_no)
      #g=set('Un Airlines')
      #(g.difference(a_no))
      a_no = a_no[:0] + "" + a_no[1:]
      print(f_no,a_no,cur_date)
     
      cursor.execute("call remove_flight(%s , %s , %s)",(f_no,a_no,cur_date))
      print(type(fno), type)
      print(cursor.fetchall())
      results = [r.fetchall() for r in cursor.stored_results()]
      print(results)
      db_connection.commit()

      cursor.close()
     



    
    return render_template('remove_flight.html',cur_date=cur_date,airlines=airlines,fl=fl)


@app.route('/admin/view_airport',methods=["GET","POST"])
def view_airport():
    cursor = db_connection.cursor()
    q=("""SELECT Airport_Id , Airport_Name , Time_Zone , concat_ws("," ,Street , City , State , Zip) as Address from airport""")
    cursor.execute(q)
    a_data=cursor.fetchall()
    a_data=list(a_data)
    #a_data=[list(a) for a in a_data]
    max_len=len(a_data[0])-1
    
    if request.method=="POST":

        id=request.form["ID"]
        tz=request.form['tz']

        if id:
           q=("SELECT Airport_Id , Airport_Name , Time_Zone , concat_ws("," ,Street , City , State , Zip) as Address from airportWHERE Airport_Id=%s")
           cursor.execute(q,(id,))
           df=cursor.fetchall()
           df=list(df)
           a_data=intersection(a_data,df)
        
        if tz:
           q=("SELECT Airport_Id , Airport_Name , Time_Zone , concat_ws("," ,Street , City , State , Zip) as Address from airport WHERE Time_Zone=%s")
           cursor.execute(q,(tz,))
           dh=cursor.fetchall()
           dh=list(dh)
           a_data=intersection(a_data,dh)
    

        if request.form.get('reset_')=='Reset':
               return redirect("/admin/view_airport")
        if request.f.get("_back")=="Back":
              return redirect("/admin")



    
 
        a_data=[list(a) for a in a_data]
        
    return render_template("view_airports.html",airports=a_data)



@app.route('/admin/view_airlines',methods=["GET","POST"])
def view_airlines():
    cursor = db_connection.cursor()
    q=("SELECT * From view_airlines")
    cursor.execute(q)
    airlines=cursor.fetchall()
    if request.method=="POST":
        name=request.form["name"]
        if name:
            q1=("SELECT * From view_airlines WHERE airline_name=%s")
            cursor.execute(q1,(name,))
            airlines=cursor.fetchall()




    return render_template("view_airlines.html",airlines=airlines)

@app.route('/admin/view_customers',methods=["GET","POST"])
def view_customers():
    cursor = db_connection.cursor()
    q=("SELECT * From view_customers")
    cursor.execute(q)
    customers=cursor.fetchall()
    if request.method=="POST":
        name=request.form["name"]
        if name:
            q1=("SELECT * From view_customers WHERE customer_name like %%s% ")
            cursor.execute(q1,(name,))
            customers=cursor.fetchall()
        
        if request.form.get('reset')=='Reset':
               return render_template("viewc.html")

         



    return render_template("viewc.html",customers=customers)


@app.route('/customer/view_properties', methods=['POST', 'GET'])
def view_properties():
        cursor = db_connection.cursor()
        q = ("SELECT * From view_properties")
        cursor.execute(q)
        capacity = cursor.fetchall()
        if request.method == "POST":
            capacity1 = request.form["capacity1"]
            capacity2 = request.form["capacity2"]

            if capacity1 and capacity2:
                if capacity2>capacity1:
                 q1 = ("SELECT * From view_properties WHERE capacity between %s and %s ")
                 cursor.execute(q1, (capacity1,capacity2))
                 capacity = cursor.fetchall()
            if request.form.get("Back")=="Back":
                return render_template("view_properties.html",capacity=capacity)

        return render_template("view_properties.html", capacity=capacity)



@app.route('/customer/view_property_reservations', methods=["GET", "POST"])
def view_property_reservations():
    cursor = db_connection.cursor()
    # cursor.execute('SELECT * FROM Reserve')
    a_data = None
    # a_data = list(a_data)

    # result_a = None
    if request.method == "POST":

        property_name = request.form['property_name'],
        owner_email = request.form['owner_email'],


        # cursor = db_connection.cursor()
        # cursor.execute('SELECT * FROM Property WHERE Property_Name = %s and Owner_Email = %s', (property_name,owner_email))
        # a_data = cursor.fetchall()
        #
        #
        # if a_data:
        cursor.callproc('view_individual_property_reservations', (property_name[0], owner_email[0]))
        db_connection.commit()
        cursor.execute('SELECT * FROM view_individual_property_reservations')
        a_data = cursor.fetchall()

        print(a_data)
        # cursor.close()

        #
        #     q = ("SELECT * From view_individual_property_reservations WHERE i_property_name= %s ")
        #     cursor.execute(q, (i_property_name,))
        #     df = cursor.fetchall()
        #     df = list(df)
        #     a_data = intersection(a_data, df)
        #
        # if i_owner_email:
        #     q = ("SELECT * From view_individual_property_reservations WHERE i_owner_email= %s ")
        #     cursor.execute(q, (i_owner_email,))
        #     dh = cursor.fetchall()
        #     dh = list(dh)
        #     a_data = intersection(a_data, dh)
        #
        # a_data = [list(a) for a in a_data]
        # for x in a_data:
        #     x[3:6] = [','.join(x[3:6])]

    return render_template("view_property_reservations.html", abc=a_data)

@app.route('/owner/add_property', methods=['POST', 'GET'])
def add_property():
    # Output message if something goes wrong...
    msg = ''
    # Check if POST requests exist (user submitted form)
    if request.method == 'POST':
        cursor = db_connection.cursor()

        propertyname = request.form['propertyname']
        propertydescription = request.form['propertydescription']
        street = request.form['street']
        city = request.form['city']
        state = request.form['state']
        zip = request.form['zip']

        nearestairport = request.form['nearestairport']
        disttoairport = request.form['disttoairport']
        capacity = request.form['capacity']
        owner_email = session["username"]
        cost = '50.00'


        cursor.callproc('add_property', (propertyname, owner_email, propertydescription, capacity, cost,
                                         street, city, state, zip, nearestairport, disttoairport
                                         ))
        db_connection.commit()
        cursor.close()
        msg = 'Property Added!'

    return render_template('add_property.html', msg=msg)


@app.route('/owner', methods=['GET', 'POST'])
def owner_home():
    if session["userType"]==users[1] or session["userType"]==users[3]:
     return render_template("owner_home.html")
    else:
        return render_template("index.html")


@app.route('/owner/remove_property', methods=['POST', 'GET'])
def remove_property():
    cursor = db_connection.cursor()
    # query1 = "select start_date, p.property_name, p.owner_email, concat(street,' ',city,' ',state, ' ',zip) " \
    #          "as address from reserve r join property p on (p.property_name, p.owner_email)=(r.property_name, r.owner_email) where was_cancelled =0;"

    query1 = "select Property_Name, Descr, Capacity, Cost, concat(Street,' ',City,' ',State, ' ',Zip) as address from Property where Owner_Email= %s;"

    cursor.execute(query1,(session["username"],))
    tb = cursor.fetchall()
    tb = [list(t) for t in tb]
    msg = ''

    if request.method == 'POST':

        if 'submit_button' in request.form:
            usr_response = request.form.getlist('options')

            if not usr_response:
                msg = 'Please select a property you want to remove!'
                return render_template('remove_property.html', tb=tb, msg=msg)

            else:
                property_name = usr_response[0].split(",")[0].replace("'", "").replace("[", "")
                owner_email = 'lebron6@gmail.com'
                curdate = '2021-10-22'
                cursor.callproc('remove_property', (property_name, owner_email, curdate,))
                db_connection.commit()
                #cursor.close()
                #db_connection.close()
                msg = 'Successfully removed!'
                return render_template('remove_property.html', msg=msg)
    return render_template('remove_property.html', tb=tb, msg=msg)


@app.route('/customer/cancel_property', methods=['POST', 'GET'])
def cancel_property():
    cursor = db_connection.cursor()
    # query1 needs fix: 'where customer='' ; start_date > curdate()
    query1 = "select start_date, p.property_name, p.owner_email, concat(street,' ',city,' ',state, ' ',zip) as address from reserve r join property p on (p.property_name, p.owner_email)=(r.property_name, r.owner_email) where was_cancelled =0;"
    cursor.execute(query1)
    tb = cursor.fetchall()
    tb = [list(t) for t in tb]
    msg = ''

    if request.method == 'POST':

        if 'submit_button' in request.form:
            usr_response = request.form.getlist('options')

            if not usr_response:
                msg = 'Please select a property you want to cancel!'
                return render_template('cancel_property.html', tb=tb, msg=msg)

            else:
                property_name = usr_response[0].split(",")[3].replace(" '", "").replace("'", "")
                onr_email = usr_response[0].split(",")[4].replace(" ", "").replace("'", "")
                customer = session["username"]
                curdate = today
                cursor.callproc('cancel_property_reservation', (property_name, onr_email, customer, curdate,))
                db_connection.commit()
                cursor.close()
                # db_connection.close()
                msg = 'Successfully Cancelled!'
                return render_template('cancel_property.html', msg=msg)
    return render_template('cancel_property.html', tb=tb, msg=msg)

@app.route('/owner/owner_deletes_account', methods=['GET', 'POST'])
def owner_deletes_account():
    msg=''
    if request.method == 'POST':


        cursor = db_connection.cursor()
        owner_email =  session["username"]
        if request.form.get('da')=="delete account":
            cursor.callproc('remove_owner', (owner_email,))
            db_connection.commit()
            #cursor.close()
            # db_connection.close()
            msg = 'Successfully Deleted Account!'
        if request.form.get("lg")=="Logout":
            session["loggedin"]==False
            return redirect("/")


    return render_template("owner_deletes_account.html", msg=msg)

@app.route('/customer/view_flights', methods=['POST', 'GET'])
def view_flights():
        cursor = db_connection.cursor()
        #customer = 'bshelton@gmail.com'
        customer = session['username']
        q = ("select flight_id, airline, destination, flight_date, Num_Seats, seat_cost, total_spent from view_flight, Book where (flight_id, airline) = (Flight_Num, airline_name) and Customer = %s;")
        cursor.execute(q,(customer,))
        flight = cursor.fetchall()
        if request.method == "POST":
            fid = request.form["flightid"]

            if 'submit' in request.form:
                query = ("select flight_id, airline, destination, flight_date, Num_Seats, seat_cost, total_spent from view_flight, Book where (flight_id, airline) = (Flight_Num, airline_name) and flight_id = %s and customer = %s;")
                cursor.execute(query, (fid,customer))
                flight = cursor.fetchall()

        return render_template("view_flights.html", total=flight)
@app.route('/register_owner', methods=["GET", "POST"])
def register_owner():
    msg = ''
    if request.method == 'POST':
        # Create variables for easy access
        email = request.form['email'],
        phonenumber = request.form['phonenumber'],
        password = request.form['password'],
        confirm_password = request.form['confirm_password'],
        firstname = request.form['firstName'],
        lastname = request.form['lastName'],

        # Check if account exists using MySQL
        # cursor = db_connection.cursor(mysql.connector.cursors.DictCursor)
        cursor = db_connection.cursor()
        cursor.execute(
            'SELECT * FROM owners WHERE Email = %s', (email))
        account = cursor.fetchone()
        print(account)
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
            return render_template('register_customer.html', msg=msg)
        elif not re.match(r'[A-Za-z]+', firstname[0]):
            msg = 'Firstname must contain only characters!'
            return render_template('register_customer.html', msg=msg)
        elif not re.match(r'[A-Za-z]+', lastname[0]):
            msg = 'Lastname must contain only characters!'
            return render_template('register_customer.html', msg=msg)
        elif len(password[0]) < 8:
            msg = 'Please choose a password length of at least 8!'
            return render_template('register_customer.html', msg=msg)
        elif password != confirm_password:
            msg = 'Passwords do not match!'
            return render_template('register_customer.html', msg=msg)
        else:
            cursor.callproc('register_owner', (email[0], firstname[0],
                                                  lastname[0], password[0], phonenumber[0]))
            db_connection.commit()
            cursor.close()
            msg = 'Successfully registered!'
            return render_template('index.html', msg=msg)
    return render_template('register_owner.html', msg=msg)




# Screen 9
@app.route('/admin/view_owners', methods=['GET', 'POST'])
def view_owners():
    cursor = db_connection.cursor()
    q = "SELECT * From view_owners"
    cursor.execute(q)
    owners = cursor.fetchall()
    if request.method == "POST":
        name = request.form["name"]
        if name:
            q1 = "SELECT * From view_owners WHERE owner_name like concat('%', %s, '%')"
            cursor.execute(q1, (name,))
            owners = cursor.fetchall()

    return render_template("view_owners.html", owners=owners)


# Screen 10
@app.route('/admin/process_date', methods=['POST', 'GET'])
def process_date():
    if request.method == 'POST':
        cursor = db_connection.cursor()
        args = request.form["date"]
        cursor.callproc('process_date', (args,))
        db_connection.commit()
        cursor.close()

    return render_template('process_date.html')


# Screen 11
@app.route('/customer', methods=['GET', 'POST'])
def customer():
        if request.form.get("b1"):
            session["username"]=""
            session["loggedin"]=False
        return render_template("customer.html")


# Screen 12
@app.route('/customer/book_flight', methods=['GET', 'POST'])
def book_flight():
    msg =''
    cursor = db_connection.cursor()
    #cur_date = '2021-10-10'
    cur_date = datetime.date(datetime.now())

    q1 = 'SELECT flight_date as "Flight Date", airline as "Airline", flight_id as "Flight Num", num_empty_seats as "Available Seats" FROM ' \
        'view_flight where flight_date > %s '
    cursor.execute(q1,(cur_date,))
    flights = cursor.fetchall()
    #cursor.close()
    customer = session['username']
    #customer = "aray@tiktok.com"
    q2 = "select book.flight_num as 'Booked Flight Num', case when was_cancelled = 1 then num_seats * seat_cost * 0.2 " \
        "else num_seats * seat_cost end as 'amount_spent' from book, view_flight where (flight_num, airline_name) = (" \
        "flight_id, airline) and customer = %s "
    cursor = db_connection.cursor()
    cursor.execute(q2, (customer,))
    old_flight = cursor.fetchall()
    if request.method == 'POST':
        if 'submit_button' in request.form:
            option = request.form.getlist('options')
            num_seats = int(request.form['seats'])
            flight_num = option[0].split(",")[4].replace(" \'", "").replace("\'", "")
            airline_name = option[0].split(",")[3].replace(" \'", "").replace("\'", "")
            capacity = int(option[0].split(",")[5].replace(" Decimal('", "").replace("\'))", ""))
            flight_date = option[0].split(")")[0].replace("(datetime.date(", "").replace(", ", "-")
            if num_seats <= capacity:
                q3 = 'select * FROM view_flight, book where (flight_num, airline_name) = (flight_id, airline) and ' \
                     'flight_date = %s and customer = %s and was_cancelled = 0 '
                cursor.execute(q3,(flight_date, customer))
                exist_flight = cursor.fetchall()
                if exist_flight:
                    msg = "Existing flight on this date."
                    render_template("book_flight.html", flights=flights, booked=old_flight, msg=msg)
                else:
                    cursor.callproc('book_flight', (customer, flight_num, airline_name, num_seats, cur_date))
                    db_connection.commit()
                    msg = 'Flight booked successfully!'
            else:
                msg = 'Number of seats exceeds capacity'
                render_template("book_flight.html", flights=flights, booked=old_flight, msg=msg)
    return render_template("book_flight.html", flights=flights, booked=old_flight, msg=msg)


@app.route('/customer/cancel_flight', methods=['POST', 'GET'])
def cancel_flight():
    #cur_date = '2020-10-10'
    cur_date = datetime.date(datetime.now())

    i = 0
    customer = session['username']
    q = "SELECT flight.airline_name as Airline, flight.flight_num as 'Flight', flight_date as 'Date' from " \
        "flight, book where flight.flight_num=book.flight_num and flight.airline_name=book.airline_name and customer " \
        "= %s and flight_date > %s"
    cursor = db_connection.cursor()
    cursor.execute(q, (customer, cur_date,))
    fl = cursor.fetchall()

    query = "SELECT Airline_Name from airline"
    cursor.execute(query)
    airlines = cursor.fetchall()
    airlines = [a[0] for a in airlines]
    if request.method == "POST":
        fno = request.form['Fno']
        air = request.form['airlines']

        print(fno)
        if fno:
            query3 = "SELECT flight.airline_name as Airline, flight.flight_num as 'Flight', flight.flight_date as 'Date' from " \
        "flight, book where flight.flight_num= %s and flight.airline_name=book.airline_name and customer = %s"
            cursor.execute(query3, (fno, customer,))
            fj = cursor.fetchall()
            fl = intersection(fl, fj)

        if air:
            queryx = "SELECT flight.airline_name as Airline, flight.flight_num as 'Flight', flight.flight_date as 'Date' from " \
        "flight, book where flight.flight_num= book.flight_num and flight.airline_name= %s and customer = %s"
            cursor.execute(queryx, (air, customer,))
            fm = cursor.fetchall()
            fl = intersection(fl, fm)

        fl = list(fl)
        fl = [list(f) for f in fl]

        option = request.form.getlist('options')

        a_no = option[0].split(",")[0].replace("(\'", "").replace("\'", "")
        f_no = option[0].split(",")[1].replace("'", "").replace(" ", "")

        cursor.callproc('cancel_flight_booking', (customer, f_no, a_no, cur_date))
        db_connection.commit()

    return render_template('cancel_flight.html', cur_date=cur_date, airlines=airlines, fl=fl)


'''@app.route('/customer/review_property', methods=['POST', 'GET'])
def review_property():
    cursor = db_connection.cursor()
    # query1 needs fix: 'where customer='' and was_canceled ==0
    query1 = "select start_date, p.property_name, p.owner_email, concat(street,' ',city,' ',state, ' '," \
             "zip) as address from reserve r join property p on (p.property_name, p.owner_email)=(r.property_name, " \
             "r.owner_email) where was_cancelled =0 and (p.property_name, p.owner_email, customer) not in (select " \
             "property_name, owner_email, customer from review); "
    cursor.execute(query1)
    tb = cursor.fetchall()
    tb = [list(t) for t in tb]
    msg = ''

    if request.method == 'POST':
        if 'submit_button' in request.form:
            review = request.form["review"]
            rating = request.form["rating"]
            curdate = '2021-10-12'

            usr_response = request.form.getlist('options')
            property_name = usr_response[0].split(",")[3].replace(" '", "").replace("'", "")
            onr_email = usr_response[0].split(",")[4].replace(" ", "").replace("'", "")
            customer = session['username']
            cursor.callproc('customer_review_property', (property_name, onr_email, customer, review, rating, curdate))
            db_connection.commit()
            cursor.close()
            msg = 'Successfully Submitted!'
            return render_template('review_property.html', msg=msg)

    return render_template('review_property.html', tb=tb, msg=msg)'''

@app.route('/customer/review_property', methods=['POST', 'GET'])
def review_property():
    cursor = db_connection.cursor()
    customer = session['username']
    cur_date = datetime.date(datetime.now())
    # query1 needs fix: 'where customer=''
    query1 = "select start_date, p.property_name, p.owner_email, concat(street,' ',city,' ',state, ' ',zip) as address "\
        "from reserve r join property p on (p.property_name, p.owner_email)=(r.property_name, r.owner_email) where was_cancelled =0 "\
            "and customer=%s and (p.property_name, p.owner_email, customer) not in (select property_name, owner_email, customer from review) and start_date < curdate();"
    cursor.execute(query1,(customer,))
    tb = cursor.fetchall()
    print(tb)
    tb =[list(t) for t in tb]
    msg=''

    if not tb:
        msg = 'No property to rate'
        return render_template('review_property.html', msg=msg)

    elif request.method == 'POST':
        if 'submit_button' in request.form:
            review=request.form["review"]
            rating=request.form["rating"]
            # curdate = '2021-12-12'
            usr_response=request.form.getlist('options')
            # print(usr_response)
            
            if not usr_response:
                msg = 'Please select a property!'
                return render_template('review_property.html', tb=tb, msg=msg)
            
            if len(review) > 500:
                msg = 'Please enter less then 500 characters!'
                return render_template('review_property.html', tb=tb, msg=msg)
            
            if len(review) == 0:
                msg = 'Please type in something!'
                return render_template('review_property.html', tb=tb, msg=msg)
            
            else:
                property_name=usr_response[0].split(",")[3].replace(" '","").replace("'","")
                onr_email=usr_response[0].split(",")[4].replace(" ","").replace("'","")
                customer='cbing10@gmail.com'
                cursor.callproc('customer_review_property', (property_name,onr_email,customer,review,rating,cur_date,))
                db_connection.commit()
                cursor.close()
                msg = 'Successfully Submitted!'
                return render_template('review_property.html', msg=msg)

    return render_template('review_property.html', tb=tb, msg=msg)


# screen 16


# screen 18
@app.route('/customer/customer_rate_owner', methods=['POST', 'GET'])
def customer_rate_owner():
    cursor = db_connection.cursor()
    customer = session['username']
    cur_date = datetime.date(datetime.now())
    # query1 needs fix: 'where customer='' ; start_date < curdate()
    query1="select start_date, p.property_name, p.owner_email, concat(street,' ',city,' ',state, ' ',zip) as "\
            "address from reserve r join property p on (r.property_name, r.owner_email)=(p.property_name, p.owner_email) "\
            "where was_cancelled =0 and customer=%s and start_date<curdate();"
    cursor.execute(query1,(customer,))
    tb = cursor.fetchall()
    tb =[list(t) for t in tb]
    
    query2='select distinct owner_email from reserve where was_cancelled=0 and (owner_email, customer) not in '\
            '(select owner_email, customer from customers_rate_owners) and customer=%s;'
    cursor.execute(query2,(customer,))
    tb2 = cursor.fetchall()
    tb2 = [list(t) for t in tb2]
    msg=''

    if not tb:
        msg = 'No owner to rate'
        return render_template('customer_rate_owner.html', msg=msg)
    
    elif not tb2:
        msg = 'No owner to rate'
        return render_template('customer_rate_owner.html', tb=tb, msg=msg)
    
    elif request.method == 'POST':
        if 'submit_button' in request.form:
            onr_email=request.form["owner"]
            rating=request.form["rating"]
            # curdate='2021-12-06'
            # customer='cdemilio@tiktok.com'
            cursor.callproc('customer_rates_owner', (customer, onr_email, rating, cur_date,))
            db_connection.commit()
            cursor.close()
            # db_connection.close()
            msg = 'Successfully Submitted!'
            return render_template('customer_rate_owner.html',tb=tb, msg=msg)
    return render_template('customer_rate_owner.html', tb=tb, tb2=tb2, msg=msg)


# screen 24
@app.route('/owner/owner_rate_customer', methods=['POST', 'GET'])
def owner_rate_customer():
    cursor = db_connection.cursor()
    owner_ = session['username']
    cur_date = datetime.date(datetime.now())
    query1="""select  start_date, customer, p.property_name, concat(street,' ',city,' ',state, ' ',zip) 
            as address from reserve r join property p on (r.property_name, r.owner_email)=(p.property_name, p.owner_email) 
            where was_cancelled=0 and p.owner_email=%s and start_date<curdate()"""
    cursor.execute(query1,(owner_,))
    tb = cursor.fetchall()
    tb =[list(t) for t in tb]
    
    query2="select distinct customer from reserve where was_cancelled=0 and (owner_email, customer) not in (select owner_email, customer from owners_rate_customers) and Owner_Email=%s;"
    cursor.execute(query2,(owner_,))
    tb2 = cursor.fetchall()
    tb2 = [list(t) for t in tb2]
    msg=''

    if not tb:
        msg = 'No customer to rate'
        return render_template('owner_rate_customer.html', msg=msg)
    
    elif not tb2:
        msg = 'No customer to rate'
        return render_template('owner_rate_customer.html', tb=tb, msg=msg)
    
    elif request.method == 'POST':
        if 'submit_button' in request.form:
            cus_email=request.form["customer"]
            rating=request.form["rating"]
            # curdate='2021-12-06'
            # owner='msmith5@gmail.com'
            cursor.callproc('owner_rates_customer', (owner_, cus_email, rating, cur_date,))
            db_connection.commit()
            cursor.close()
            # db_connection.close()
            msg = 'Successfully Submitted!'
            return render_template('owner_rate_customer.html',tb=tb, msg=msg)
    return render_template('owner_rate_customer.html', tb=tb, tb2=tb2, msg=msg)

# screen15
@app.route('/customer/reserve_property', methods=['POST', 'GET'])
def reserve_property():
    cursor = db_connection.cursor()
    cur_date='2021-09-20'
    customer='cbing10@gmail.com'
    # query1 needs fix:
    query1="select property_name, owner_email, capacity from property"
    cursor.execute(query1)
    tb = cursor.fetchall()
    print(tb)
    tb = [list(t) for t in tb]
    msg=''

    if request.method == 'POST':
        if 'submit_button' in request.form:
            date1=request.form['Date1']
            date2=request.form['Date2']
            seats=request.form['seats']
            usr_response=request.form.getlist('options')
            print(usr_response)
            property_name=usr_response[0].split(",")[0].replace("['","").replace("'","")
            onr_email=usr_response[0].split(",")[1].replace(" '","").replace("'","")
            print(customer)
            if not date1 or not date2:
                msg='Please select the time range'
                return render_template('reserve_property.html',msg=msg)
            
            elif date1 <cur_date:
                msg='Start date should be in the future'
                return render_template('reserve_property.html',msg=msg)

            elif date1>date2:
                msg='Strat date should be earlier than end date'
                return render_template('reserve_property.html',msg=msg)

            elif not usr_response:
                msg='Please select a property to book'
                return render_template('reserve_property.html',msg=msg)
            
            elif not seats:
                msg='Please specify the number of guests to book'
                return render_template('reserve_property.html',msg=msg)

            query3='select property_name from reserve where %s between start_date and end_date and was_cancelled=0 and customer=%s;'
            cursor.execute(query3,(date1,customer,))
            tb3 = cursor.fetchall()
            tb3 = [list(t) for t in tb3]

            if tb3:
                msg='Already exist another reservation in this time period'
                return render_template('reserve_property.html',msg=msg)

            query4="select (capacity -num_guests) from property p join reserve r "\
                    "on (p.property_name, p.owner_email)=(r.property_name, r.owner_email) "\
                    "where (p.property_name, p.owner_email)=(%s,%s) and %s between start_date and end_date and was_cancelled=0;"
            cursor.execute(query4,(property_name,onr_email,date1,))
            tb4 = cursor.fetchall()
            tb4 = [list(t) for t in tb4]
            if not tb4:
                query5="select capacity from property where (property_name, owner_email)=(%s,%s);"
                cursor.execute(query5,(property_name,onr_email,))
                tb5=cursor.fetchall()
                tb5=[list(t) for t in tb5]
                avai=tb5[0][0]
            else:
                avai=tb4[0][0]
            print(date1)
            print(avai)
            
            if int(seats) > avai:
                msg='The available capacity is smaller than required number'
                return render_template('reserve_property.html',msg=msg)

            else:
                cursor.callproc('reserve_property', (property_name,onr_email,customer,date1,date2,int(seats),cur_date,))
                db_connection.commit()
                cursor.close()
                # db_connection.close()
                msg='Reservation Complete'
                return render_template('reserve_property.html',msg=msg)

    return render_template('reserve_property.html', tb=tb, msg=msg)

if __name__ == '__main__':
    app.run(debug=True)
    


