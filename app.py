import logging
import os
import requests
from flask import Flask, request, jsonify
from flask_ngrok import run_with_ngrok
from pyngrok import ngrok
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Logging Setup
logging.basicConfig(level=logging.INFO)

# Flask App Setup
app = Flask(__name__)
run_with_ngrok(app)

# Load API Keys Securely
NGROK_AUTH_TOKEN = os.getenv("NGROK_AUTH_TOKEN")
IBM_CLOUD_API_KEY = os.getenv("IBM_CLOUD_API_KEY")
DEPLOYMENT_ID = os.getenv("DEPLOYMENT_ID")

# IBM Watson API URL
DEPLOYMENT_ENDPOINT = f"https://jp-tok.ml.cloud.ibm.com/ml/v4/deployments/realtime_churn_model/predictions?version=2021-05-01"

# Set Ngrok Authentication
ngrok.set_auth_token(NGROK_AUTH_TOKEN)

# Start Ngrok
ngrok_tunnel = ngrok.connect(5000)
public_url = ngrok_tunnel.public_url
print(f"Flask is running at: {public_url}")


def get_iam_token():
    """Get IBM Watson ML IAM Token"""
    auth_url = "https://iam.cloud.ibm.com/identity/token"
    auth_response = requests.post(
        auth_url,
        data={"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": IBM_CLOUD_API_KEY},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return auth_response.json().get("access_token")


@app.route('/')
def home():
    return "Welcome to the Customer Insights API!"


@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get JSON Data
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request. No data received."}), 400

        # Get IBM Watson ML IAM Token
        iam_token = get_iam_token()
        headers = {"Authorization": f"Bearer {iam_token}", "Content-Type": "application/json"}

        # Send request to IBM Watson ML
        response = requests.post(DEPLOYMENT_ENDPOINT, json=data, headers=headers)

        # Return IBM Watson Response
        return jsonify(response.json())

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
   run_with_ngrok(app)  # ✅ Correct way to run Flask with Ngrok

