import numpy as np
from flask import Blueprint, jsonify, request
import os
from csv_file_reading import import_year_file, import_month_file, import_daily_file, prediction_data
import pandas as pd
forecast_blueprint = Blueprint('forecast', __name__)

@forecast_blueprint.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file'}), 400
    file = request.files['file']
    csv_url = request.form.get('csv_url', '')
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    uploads_dir = os.path.join(os.getcwd(), 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)

    if 'year' in csv_url.lower():
        file.filename = 'data_year.csv'
    elif 'month' in csv_url.lower():
        file.filename = 'data_month.csv'
    elif 'daily' in csv_url.lower():
        file.filename = 'data_daily.csv'
    else:
        return jsonify({'error': 'Invalid URL'}), 400

    file_path = os.path.join(uploads_dir, file.filename)
    file.save(file_path)
    file_name = ''
    if 'year' in file.filename.lower():
        file_name = import_year_file(file_path)
    elif 'month' in file.filename.lower():
        file_name = import_month_file(file_path)
    elif 'daily' in file.filename.lower():
        file_name = import_daily_file(file_path)
    else:
        return jsonify({'error': 'Invalid file type or URL'}), 400

    return jsonify({'message': 'File processed and saved', 'filename': file_name}), 200

@forecast_blueprint.route('/predict', methods=['POST'])
def predict():
    date_to_predict = request.json.get('date')
    print("THE DATE TO PREDICT:", date_to_predict)
    try:
        forecast_date = pd.to_datetime(date_to_predict, format='%Y-%m-%d')
        print("FORECAST DATE TO PREDICT:", forecast_date)
        predicted_temp = prediction_data(forecast_date)

        if isinstance(predicted_temp, np.ndarray):
            predicted_temp = round(float(predicted_temp.flatten()[0]),1)
        return jsonify({'predicted_temp': predicted_temp}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400

