from flask import Flask, render_template, request

app = Flask(__name__)

# Helper function for BMR calculation


def calculate_bmr(age, height, weight, gender):
    if gender == 'male':
        return 66 + (13.7 * weight) + (5 * height) - (6.8 * age)
    else:
        return 655 + (9.6 * weight) + (1.8 * height) - (4.7 * age)


@app.route('/', methods=['GET', 'POST'])
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


if __name__ == '__main__':
    app.run(debug=True)
