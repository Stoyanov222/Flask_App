from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Where to redirect if not logged in

# Dummy User Data (You should use a database in production)
users = {
    'user1': {'password': 'sfitapp'},
    'user2': {'password': 'sfitapp'}
}

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Load user function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Login Form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6, max=20)])

# Home page (redirect to login if not logged in)
@app.route('/')
def home():
    return redirect(url_for('login'))

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        if username in users and users[username]['password'] == password:
            user = User(username)
            login_user(user)
            return redirect(url_for('main_page'))  # Redirect to the BMR calculator after login
        else:
            flash('Invalid username or password')

    return render_template('login.html', form=form)

def calculate_bmr(age, height, weight, gender):
    if gender == 'male':
        return 66 + (13.7 * weight) + (5 * height) - (6.8 * age)
    else:
        return 655 + (9.6 * weight) + (1.8 * height) - (4.7 * age)
    
@app.route('/home')
@login_required
def main_page():
    return render_template('index.html')

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

# New route for the logged out page
@app.route('/logged_out')
def logged_out():
    return render_template('logged_out.html')

if __name__ == '__main__':
    app.run(debug=True)
