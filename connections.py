from flask import Flask, render_template, request, redirect, url_for, session
import hashlib
# from flask_mysqldb import MySQLpip
import mysql.connector
import re
import sys
import json
from datetime import date
def intersection(lst1, lst2):
    return list(set(lst1) & set(lst2))

today = date.today()

app = Flask(__name__, static_url_path="")
app.secret_key = 'cs4400fall2021'


db_connection = mysql.connector.connect(host="localhost",
                                        user="root",
                                        passwd="armaloc23",
                                        db="travel_reservation_service",
                        )

@app.route('/', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('index.html', msg='')

    if request.method == 'POST':
        cursor = db_connection.cursor(buffered=True)
        email = request.form['email']
        password = request.form['password']
        select_statement = "SELECT * FROM Accounts WHERE Email = %s AND Pass = %s "
        cursor.execute(select_statement, (email, password))
        result = cursor.fetchall()
        print(result)

        #If it finds the user credentials in the DB, it then seeks to update the session accordingly
        if result:
            return 'Hello ' + str(email)
            #checkForPermissions()

        cursor.close()
        return "Login Failed"




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
    return render_template("admin.html")


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

                q=("call schedule_flight(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
                cursor.execute(q,(fno,airline_,f_airport,t_airport,d_time,a_time,f_date,cost,cpc,c_date))
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
    cur_date=today
    q3="SELECT Flight_Num,Airline_Name,Flight_Date from flight"
    cursor = db_connection.cursor()
    cursor.execute(q3)
    fl=cursor.fetchall()
    fl1= ["".join(f[0:2]) for f in fl ]

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
            query="SELECT Flight_Num,Airline_Name,Flight_Date from flight WHERE Flight_Date between %s and %s"
            cursor.execute(query,(date2,date1))
            fk=cursor.fetchall()
            fl=intersection(fl,fk)
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
     option = request.form.getlist('options')
    # print(option)
     #option = request.form.getlist('options')
     #flight_num,airline_name=option[0],option[1]
     #print((option))
    # print(flight_num,airline_name)
     f_no= option[0].split(",")[0].replace("[","").replace("(","").replace("'","")
     a_no= option[0].split(",")[1].replace("'","")
     print(f_no , a_no)
     
     cursor.callproc('remove_flight',(f_no,a_no,cur_date))
     print(cursor.fetchall())
     
     



    
    return render_template('remove_flight.html',cur_date=cur_date,airlines=airlines,fl=fl)

@app.route('/admin/view_airport',methods=["GET","POST"])
def view_airport():
    cursor = db_connection.cursor()
    q=("SELECT * From airport")
    cursor.execute(q)
    a_data=cursor.fetchall()
    a_data=list(a_data)
    #a_data=[list(a) for a in a_data]
    max_len=len(a_data[0])-1
    
    if request.method=="POST":
        id=request.form["ID"]
        tz=request.form['tz']

        if id:
           q=("SELECT * From airport WHERE Airport_Id=%s")
           cursor.execute(q,(id,))
           df=cursor.fetchall()
           df=list(df)
           a_data=intersection(a_data,df)
        
        if tz:
           q=("SELECT * From airport WHERE Time_Zone=%s")
           cursor.execute(q,(tz,))
           dh=cursor.fetchall()
           dh=list(dh)
           a_data=intersection(a_data,dh)




    
 
        a_data=[list(a) for a in a_data]
        for x in a_data:
         x[3:6] = [','.join(x[3:6])]
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


    return render_template("view_customers.html",customers=customers)


    

if __name__ == '__main__':
    app.run(debug=True)
