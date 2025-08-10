# app.py
from flask import Flask, redirect, request, session
import requests
import config
import secrets

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a secure, random string

@app.route('/')
def home():
    # Generate a secure random state token
    state = secrets.token_urlsafe(16)
    session['oauth_state'] = state

    # Redirect to Blizzard's OAuth authorization URL with state
    return redirect(
        f"{config.AUTH_URL}?client_id={config.CLIENT_ID}"
        f"&redirect_uri={config.REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=wow.profile"
        f"&state={state}"
    )

@app.route('/callback')
def callback():
    code = request.args.get('code')
    returned_state = request.args.get('state')
    expected_state = session.get('oauth_state')

    # Validate the state parameter
    if returned_state != expected_state:
        return "Error: Invalid state parameter", 400

    # Exchange code for access token
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': config.REDIRECT_URI,
        'client_id': config.CLIENT_ID,
        'client_secret': config.CLIENT_SECRET
    }
    response = requests.post(config.TOKEN_URL, data=data)
    
    if response.status_code != 200:
        return f"Error fetching token: {response.text}", response.status_code

    access_token = response.json().get('access_token')
    return f"Access Token: {access_token}"

if __name__ == '__main__':
    app.run(debug=True)