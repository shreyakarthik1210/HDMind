from flask import Flask, render_template, request, redirect, url_for
import pymysql

app = Flask(__name__)


@app.route('/')
def root():
   return render_template('login.html')

@app.route('/login', methods=['GET','POST'])
def login():
     msg=''
     username = request.form.get('username')
     password = request.form.get('password')
     if username == "admin@gmail.com":
        msg='Logged in successfully'
        return render_template('register.html',msg= msg)
     else:
         msg="Invalid login"
     return render_template('login.html',msg=msg)


@app.route('/register', methods=['GET','POST'])
def register():
 msg=''
 if(request.method=='POST' and 'username' in request.form):
    firstName = request.form.get("firstName")
    lastName = request.form.get("lastName")
    gender = request.form.get("gender")
    email = request.form.get("username")
    password = request.form.get("password")
    

    # Basic validation
   

    # Store user data 
   # sql="INSERT INTO users (id,firstName,lastName,Gender,DOB,email,password) values (%s,%s,%s,%s,%s,%s,%s)"
    #val=("10",firstName, lastName, gender, email, password)
    msg='Registration successful'
 elif request.method=='POST':
     msg='Fill form'
    # return f'Registration successful, {email}! You can now <a href="/login">Login</a>.'
 return render_template('register.html',msg=msg)

if __name__ == '__main__':
    app.run(debug=True)