from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'

# CREATE DATABASE


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)
login_manager=LoginManager()
login_manager.init_app(app)
# CREATE TABLE IN DB
class User(db.Model,UserMixin):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))


with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    if current_user.is_authenticated:
        return render_template('index.html',logged_in=True)
    else:
        return render_template("index.html",logged_in=False)

@app.route('/register',methods=["GET","POST"])
def register():
    if request.method=="POST":
        new_user=User(name=request.form['name'],email=request.form['email'],password=generate_password_hash(request.form['password'],salt_length=8))
        db.session.add(new_user)
        db.session.commit()
        email=request.form['email']
        password=request.form['password']
        print(email,password)
        user=User.query.filter_by(email=email).first()
        login_user(user)
        return redirect(url_for('secrets'))
    return render_template("register.html")



@app.route('/login',methods=["POST","GET"])
def login():
    if request.method=="POST":
        email=request.form['email']
        password=request.form['password']
        print(email,password)
        user=User.query.filter_by(email=email).first()
        print(user)
        if user:
            if check_password_hash(user.password,password):
                login_user(user)

                return redirect(url_for('secrets'))
            else:
                return render_template('login.html',msg='Password was incorrect')
        else:
            return render_template('login.html',msg='Email does not exist')
    return render_template("login.html")


@app.route('/secrets')
@login_required
def secrets():
    return render_template("secrets.html",user_name=current_user.name,logged_in=True)


@app.route('/logout')
def logout():
    logout_user()
    return render_template('login.html')


@app.route('/download')
@login_required
def download():
    return send_from_directory('static/files','cheat_sheet.pdf')


if __name__ == "__main__":
    app.run(debug=True)
