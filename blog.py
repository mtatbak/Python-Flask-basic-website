from flask import Flask,render_template,flash,redirect,url_for,request,session,logging
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt

app = Flask(__name__)

app.secret_key = "blog"

class registerForm(Form):
    name = StringField("Name Surname",validators=[validators.length(min=5,max=30)])
    username = StringField("Username",validators=[validators.length(min=5,max=30),validators.DataRequired("Please buddy")])
    email = StringField("E-Mail",validators=[validators.Email("Please buddy")])
    password = PasswordField("Password",validators=[validators.EqualTo(fieldname="confirm",message="Cmonnn"),validators.DataRequired("Please buddy")])
    confirm = PasswordField("Password")

class loginForm(Form):
    username = StringField("Username",validators=[validators.DataRequired(message=("Lets go buddy"))])
    password = PasswordField("Password",validators=[validators.DataRequired(message=("Lets go buddy"))])

#mysql config

app.config["MYSQL_HOST"]= "localhost"
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'github'
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)



#main page
@app.route("/")
def index():
    return render_template("index.html")

#about page
@app.route("/about")
def about():
    return render_template("about.html")

#register page
@app.route("/register",methods = ["GET","POST"])
def register():
    
    form =registerForm(request.form)

    if request.method == "POST" and form.validate():
        #save data
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(form.password.data)

        cursor = mysql.connection.cursor()
        sorgu = "Insert into users (name,email,username,password) Values(%s,%s,%s,%s)"
        cursor.execute(sorgu,(name,email,username,password))
        mysql.connection.commit()

        cursor.close()

        flash(message="Success",category="success")
        #secret_key!!!

        return redirect(url_for("login"))
    else:
        return render_template("register.html",form = form)

#login page
@app.route("/login",methods = ["GET","POST"])
def login():
    form = loginForm(request.form)

    if request.method == "POST":
        username = form.username.data
        password_entered = form.password.data

        cursor = mysql.connection.cursor()
        sorgu = "Select *From users where username = %s"

        result = cursor.execute(sorgu,(username,))
        if result>0:
            data = cursor.fetchone()
            real_password = data["password"]
            if sha256_crypt.verify(password_entered,real_password):
                flash("success",category="success")

                session["logged_in"] = True
                
                return redirect(url_for("index"))
            else:
                flash("ı am sorry",category="danger")
                return redirect(url_for("login"))
        else:
            flash("I am Sorry", category="danger")
            return redirect(url_for("login"))
    else:
        return render_template("login.html",form = form)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)

