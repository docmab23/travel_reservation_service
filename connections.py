from flask import Flask
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
    if request.method == "POST":
        # getting input with name = fname in HTML form
        conn=mysql.connect()
        cursor=conn.cursor()
        e= str(request.form.get("Email"))
        p= str(request.form.get("Password"))
        # getting input with name = lname in HTML form
        query=("""IF ((%s,%s) in (SELECT Email,Pass FROM accounts))THEN SELECT("Login"); END IF;""")
        tuple1 = (e,p)
        cursor.execute(query, tuple1)
        #cursor.execute(query)

        data = cursor.fetchall()
        print(data)
    #return data
    return render_template("form.html")


if __name__ == '__main__':
    app.run(debug=True)