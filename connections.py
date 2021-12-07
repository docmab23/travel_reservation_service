from flask import Flask
from flask.scaffold import F
from flaskext.mysql import MySQL
#from flaskext_mysql import MySQL
from flask import Flask, render_template,request,send_from_directory,send_file

app = Flask(__name__)
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'armaloc23'
app.config['MYSQL_DATABASE_DB'] = 'travel_reservation_service'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)



'''cursor.execute("SELECT * from review")
data = cursor.fetchall()
print(data)'''
@app.route('/', methods=["GET", "POST"])
def gfg():
    admin=False
    re=False
    if request.method == "POST":
        # getting input with name = fname in HTML form
        

        conn=mysql.connect()
        cursor=conn.cursor()
        e= str(request.form.get("Email"))
        p= str(request.form.get("Pass"))
        # getting input with name = lname in HTML form
        print(e,p)
        query=("SELECT EXISTS(SELECT * FROM accounts WHERE Email= %s and Pass=%s)")
        query2=("SELECT EXISTS(SELECT * FROM admins WHERE Email= %s)")

        tuple1 = (e,p)
        tuple2=(e)
        cursor.execute(query,tuple1)
        #cursor.execute(query2,tuple2)

        data = cursor.fetchall()
        if (data[0][0])==1:
            cursor.execute(query2,tuple2)
            data2=cursor.fetchall()
            if data2[0][0]==1:
                print("Admin screen")
                admin=True
            else:
               query3=("SELECT EXISTS(SELECT * FROM Customer WHERE Email= %s)")
               cursor.execute(query3,tuple2)
               data3=cursor.fetchall()
               if data3[0][0]==1:
                   print("Customer")
               else:
                   print("Owner")
        else:
            print("User not found")
            re=True



             

        



    #return data
    return render_template("form3.html",ad=admin,r=re)
@app.route('/register', methods=["GET", "POST"])
def reg():
    admin=False
    re=False
    if request.method == "POST":
        # getting input with name = fname in HTML form
        

        conn=mysql.connect()
        cursor=conn.cursor()
        e1= str(request.form.get("Email"))
        p1= str(request.form.get("Password"))
        f=str(request.form.get("First_Name"))
        l=str(request.form.get("Last_Name"))
        print(e1,p1,f,l)
        queryx=("INSERT INTO accounts (Email,First_Name,Last_Name,Pass) VALUES (%s, %s, %s, %s)")

        tuple4=(e1,f,l,p1)
        cursor.execute(queryx,tuple4)
        print(cursor.fetchall())

    return render_template("register_form.html")

if __name__ == '__main__':
    app.run(debug=True)