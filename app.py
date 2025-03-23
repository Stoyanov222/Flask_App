from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length, EqualTo
from dotenv import load_dotenv
import os
import sqlitecloud
from werkzeug.security import generate_password_hash, check_password_hash


load_dotenv()

# Establish SQLite connection using sqlitecloud (connect here once globally)


def get_db_connection():
    return sqlitecloud.connect(os.getenv("CONNECTION_STRING"))


app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Where to redirect if not logged in

# User class for Flask-Login


class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

# Load user function for Flask-Login


@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()  # Get new connection each time
    try:
        cursor = conn.execute(
            'SELECT id, username FROM users WHERE id = ?', (user_id,))
        user_data = cursor.fetchone()
        if user_data:
            # Assuming columns are id, username
            return User(user_data[0], user_data[1])
    finally:
        conn.close()  # Ensure the connection is closed after use
    return None

# Sign-Up Form


class SignUpForm(FlaskForm):
    username = StringField('Username', validators=[
                           InputRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[
                             InputRequired(), Length(min=6, max=20)])
    confirm_password = PasswordField('Confirm Password', validators=[
                                     InputRequired(), EqualTo('password', message='Passwords must match.')])

# Login Form


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
                           InputRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[
                             InputRequired(), Length(min=6, max=20)])

# Root route for the application (Redirects to login page or home page)


@app.route('/')
def index():
    if current_user.is_authenticated:
        # Redirect to the index page after login if the user is authenticated
        # Or any other content you want to show
        return render_template('index.html')
    return redirect(url_for('login'))  # Redirect to login if not logged in

# Sign-Up route


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Hash the password before storing it in the database
        hashed_password = generate_password_hash(password)

        # Check if username already exists
        conn = get_db_connection()
        try:
            cursor = conn.execute(
                'SELECT * FROM users WHERE username = ?', (username,))
            user_data = cursor.fetchone()
            if user_data:
                flash('Username already exists!')
                return redirect(url_for('signup'))

            # Insert new user into database with hashed password
            conn.execute(
                'INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()

            flash('Account created successfully! Please log in.')
            return redirect(url_for('login'))
        finally:
            conn.close()

    return render_template('signup.html', form=form)

# Login route


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Query the SQLite database for the user
        conn = get_db_connection()
        try:
            cursor = conn.execute(
                'SELECT * FROM users WHERE username = ?', (username,))
            user_data = cursor.fetchone()

            # Check if user exists and if password matches the hashed password
            # user_data[2] is the hashed password
            if user_data and check_password_hash(user_data[2], password):
                # Assuming columns are id, username, password_hash
                user = User(user_data[0], user_data[1])
                login_user(user)
                # Redirect to the BMR calculator after login
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password')
        finally:
            conn.close()  # Ensure the connection is closed after use

    return render_template('login.html', form=form)


def calculate_bmr(age, height, weight, gender):
    if gender == 'male':
        return 66 + (13.7 * weight) + (5 * height) - (6.8 * age)
    else:
        return 655 + (9.6 * weight) + (1.8 * height) - (4.7 * age)


@app.route('/bmr', methods=['GET', 'POST'])
def calculate_result():
    result = None
    error_message = None

    if request.method == 'POST':
        try:

            age = int(request.form['age'])
            height = int(request.form['height'])
            weight = int(request.form['weight'])
            gender = request.form.get('gender')
            protein = float(request.form.get('protein'))
            calories = int(request.form.get('calories'))
            weight_lb = weight * 2.2

            bmr = calculate_bmr(age, height, weight, gender)

            sedentery_cals = bmr * 1.2 + calories
            light_cals = bmr * 1.35 + calories
            moderate_cals = bmr * 1.5 + calories
            high_cals = bmr * 1.68 + calories
            protein_per_day = weight_lb * protein
            protein_per_day_cals = protein * 4

            result = f"""
                    Your BMR is: {round(bmr)} calories/day
                    Caloric needs based on activity level: 
                    Sedentary: {round(sedentery_cals)} cal/day 
                    Lightly active: {round(light_cals)} cal/day 
                    Moderately active: {round(moderate_cals)} cal/day
                    Very active: {round(high_cals)} cal/day
                    Protein per day: {round(protein_per_day)}g / {round(protein_per_day_cals)} cal
                    Caloric adjustment: {int(calories)} cal
    """
        except ValueError:
            error_message = "Please ensure all fields are filled out correctly."

    return render_template('bmr_page.html', result=result, error_message=error_message)

# Logout route


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('logged_out'))


@app.route('/logged_out')
def logged_out():
    return render_template('logged_out.html')


if __name__ == '__main__':
    app.run(debug=True)
