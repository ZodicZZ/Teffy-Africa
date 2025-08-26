from flask import Flask, jsonify, request
import requests
import tensorflow as tf
import numpy as np
app = Flask(__name__)
#Trained model will implemented once a large mass of data is collected using the probe.
#Hardcoded data will be feteched for know
CARDANO_VALIDATION_API = "https://localhost/cardano-validation"
def fetch_cardano_data(location):
    response = requests.get(f"{CARDANO_VALIDATION_API}?location={location}")
    if response.status_code == 200:
        return response.json()
    else:
        return None
def adjust_thresholds_with_tensorflow(location_data):

    model = tf.keras.Sequential([
        tf.keras.layers.Dense(32, activation='relu', input_shape=(len(location_data),)),
        tf.keras.layers.Dense(1)
    ])    
    input_data = np.array(location_data).reshape(1, -1)
    adjusted_thresholds = model.predict(input_data)
    return adjusted_thresholds[0][0]
@app.route('/get-thresholds', methods=['GET'])
def get_thresholds():
    location = request.args.get('location', default='soil', type=str)
    cardano_data = fetch_cardano_data(location)
    if cardano_data is None:
        return jsonify({"error": "Failed to fetch Cardano validation data"}), 500
    location_data = [
        cardano_data['temperature'],
        cardano_data['humidity'],
        cardano_data['light'],
        cardano_data['ph'],
        cardano_data['soil_moisture']
    ]
    adjusted_value = adjust_thresholds_with_tensorflow(location_data)
    thresholds = {
        "minTemp": adjusted_value * 0.8,
        "maxTemp": adjusted_value * 1.2,
        "minHumidity": adjusted_value * 0.7,
        "maxHumidity": adjusted_value * 1.3,
        "minLight": adjusted_value * 0.9,
        "maxLight": adjusted_value * 1.1,
        "minPH": adjusted_value * 0.6,
        "maxPH": adjusted_value * 1.4,
        "minSoil": adjusted_value * 0.5,
        "maxSoil": adjusted_value * 1.5
    }
    return jsonify(thresholds)
if __name__ == "__main__":
    app.run(debug=True)