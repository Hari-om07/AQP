from flask import Flask, request, jsonify, render_template, url_for
import pickle as pk
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from datetime import datetime
import numpy as np

app = Flask(__name__, template_folder='templates', static_folder='static')

# Load dataset
df = pd.read_csv('data/air_pollution_data.csv')

# Load the pickled model
rf_model = pk.load(open('data/rf.pkl', 'rb'))

# Initialize LabelEncoders
le_city = LabelEncoder()
le_date = LabelEncoder()

# Ensure date column is in datetime format
df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')  # Adjust the format for DD-MM-YYYY
df['date'] = df['date'].astype(str)  # Convert to string for LabelEncoder

# Fit LabelEncoders with data
le_city.fit(df['city'])
le_date.fit(df['date'])

# Use a flag to mimic 'before_first_request'
first_request = True

@app.before_request
def setup_once():
    global first_request
    if first_request:
        # Code to run only before the first request
        print("This runs only once before the first request")
        first_request = False

@app.route('/')
def index():
    return render_template('index.html')

# Route for the prediction form
@app.route('/form')
def form():
    return render_template('form.html')

# Route to handle form submission and predict
@app.route('/predict', methods=['POST', 'GET'])
def predict():
    if request.method == 'POST':
        try:
            # Extract form data
            city = request.form['city']
            date_str = request.form['date']
            co = float(request.form['co'])
            no = float(request.form['no'])
            no2 = float(request.form['no2'])
            o3 = float(request.form['o3'])
            so2 = float(request.form['so2'])
            pm2_5 = float(request.form['pm2_5'])
            pm10 = float(request.form['pm10'])
            nh3 = float(request.form['nh3'])

            # Parse and validate date
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            if date_obj.year < 2020 or date_obj.year > 2030:
                error = 'Date must be between the years 2020 and 2030'
                return render_template('form.html', error=error)
            
            # Encode city
            city_encoded = le_city.transform([city])[0]

            # Handle unseen dates
            if date_str not in le_date.classes_:
                le_date.classes_ = np.append(le_date.classes_, date_str)  # Add unseen date to encoder
            date_encoded = le_date.transform([date_str])[0]

            # Prepare input data
            input_data = pd.DataFrame([{
                'city': city_encoded,
                'date': date_encoded,
                'co': co,
                'no': no,
                'no2': no2,
                'o3': o3,
                'so2': so2,
                'pm2_5': pm2_5,
                'pm10': pm10,
                'nh3': nh3
            }])

            # Predict AQI
            rf_pred = rf_model.predict(input_data)
            aqi_pred = min(max(round(rf_pred[0]), 0), 5)

            # Return JSON with result
            prediction_text = f'Air Quality Index: {aqi_pred}'
            return render_template('form.html', prediction_text=prediction_text)
        except Exception as e:
            error = f"Error during prediction: {str(e)}"
            return render_template('form.html', error=error)

    return render_template('form.html')

@app.route('/about')
def about_page():
    return render_template('about.html')

@app.route('/contact')
def contact_page():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)
