from application import app, db,login_manager
from flask import render_template, request, json, Response, redirect, flash, url_for,session
from application.models import User, Course, Enrollment
from application.forms import LoginForm, RegisterForm
from flask_login import login_user,logout_user

@app.route("/")
@app.route("/index")
@app.route("/home")
def index():
    return render_template("index.html", index=True )

@app.route("/login", methods=['GET','POST'])
def login():
    if session.get('username'):
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        email       = form.email.data
        password    = form.password.data
        remember =True if request.form.get('remember_me') else False
        user = User.objects(email=email).first()
        if user and user.password==password:
            session['user_id']=user.user_id
            session['username']=user.first_name
            flash(f"{user.first_name}, you are successfully logged in!", "success")
            login_user(user,remember=remember)
            return redirect("/index")
        else:
            flash("Sorry, check your login credentials.","danger")
    return render_template("login.html", title="Login", form=form, login=True )

@app.route("/courses/")
@app.route("/courses/<term>")
def courses(term="2019"):
    if not session.get('username'):
        return redirect(url_for('login'))
    classes=Course.objects.order_by("+courseID")
    return render_template("courses.html", courseData=classes, courses = True, term=term )


@app.route("/logout")
def logout():
    logout_user()
    session['user_id']=False
    session.pop('username',None)
    return redirect(url_for('index'))


@app.route("/register", methods=['POST','GET'])
def register():
    if  session.get('username'):
        return redirect(url_for('register'))
    form = RegisterForm()
    if form.validate_on_submit():
        user_id     = User.objects.count()
        user_id     =user_id + 1

        email       = form.email.data
        password    = form.password.data
        first_name  = form.first_name.data
        last_name   = form.last_name.data

        user = User(user_id=user_id, first_name=first_name, last_name=last_name,email=email)
        user.set_password(password)
        user.save()
        flash("You are successfully registered!","success")
        return redirect(url_for('index'))
    return render_template("register.html", title="Register", form=form, register=True)


@app.route("/enrollment", methods=["GET","POST"])
def enrollment():
    if not session.get('username'):
        return redirect(url_for('login'))
    courseID= request.form.get('courseID')
    courseTitle= request.form.get('title')
    user_id = session.get('user_id')

    if courseID:
        if Enrollment.objects(user_id=user_id,courseID=courseID):
            flash(f"Oops!You are already registered in this course {courseTitle}!","danger")
            return redirect("/courses")
        else:
            p=Enrollment(user_id=user_id,courseID=courseID)
            p.save()
            flash(f"You are enrolled in {courseTitle}","success")

    classes=list(User.objects.aggregate(*
                [
                {
                    '$lookup': {
                        'from': 'enrollment', 
                        'localField': 'user_id', 
                        'foreignField': 'user_id', 
                        'as': 'p'
                    }
                }, {
                    '$unwind': {
                        'path': '$p', 
                        'includeArrayIndex': 'p_id', 
                        'preserveNullAndEmptyArrays': False
                    }
                }, {
                    '$lookup': {
                        'from': 'course', 
                        'localField': 'p.courseID', 
                        'foreignField': 'courseID', 
                        'as': 'q'
                    }
                }, {
                    '$unwind': {
                        'path': '$q', 
                        'preserveNullAndEmptyArrays': False
                    }
                }, {
                    '$match': {
                        'user_id': 1
                    }
                }, {
                    '$sort': {
                        'courseID': 1
                    }
                }
            ]))
    return render_template("enrollment.html",title="Enrollment",enrollment=True,classes=classes)    

@app.route("/user")
def user():
     #User(user_id=1, first_name="Christian", last_name="Hur", email="christian@uta.com", password="abc1234").save()
     #User(user_id=2, first_name="Mary", last_name="Jane", email="mary.jane@uta.com", password="password123").save()
     users = User.objects.all()
     return render_template("user.html", users=users)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
