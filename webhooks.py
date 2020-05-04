from flask import Flask, redirect, render_template, session, request, url_for
from googleapiclient.discovery import build
import google.oauth2.credentials
import google_auth_oauthlib.flow
import os
import uuid
import requests

app = Flask(__name__)
app_path = os.path.realpath(os.path.dirname(__file__))

calendar_api = None
credentials = None
state = None

@app.route("/")
def hello():
	global state
	if state is None:
		state = request.args.get("state")	
	if state is None:
		return sign_in_and_authorize()

	global credentials
	if credentials is None:
		credentials = get_credentials()

	global calendar_api
	calendar_api = build("calendar", "v3", credentials=credentials)

	return redirect(url_for("notification"))

@app.route("/notification", methods=["GET"])
def notification():
	submit_calendar_event_webhook()

	return render_template("notification.html")

@app.route("/webhook", methods=["POST"])
def calendar_event_webhook():
	res = "Webhook is called"
	print(res)
	return res

def submit_calendar_event_webhook():
	payload = {
		"id": str(uuid.uuid1()),
		"type": "web_hook",
		"address": "https://personal.yesasurya.com/webhook"
	}

	global calendar_api
	return calendar_api.events().watch(calendarId="primary", body=payload).execute()

def get_credentials():
	flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
		os.path.join(app_path, "static/client_secret_1083467553321-rah1no5l2obuqf5d4sfbjap8969c7p7l.apps.googleusercontent.com"),
		scopes=None,
		state=state
	)
	flow.redirect_uri = "https://personal.yesasurya.com"

	authorization_response = request.url
	flow.fetch_token(authorization_response=authorization_response)

	return flow.credentials

def sign_in_and_authorize():
	flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
		os.path.join(app_path, "static/client_secret_1083467553321-rah1no5l2obuqf5d4sfbjap8969c7p7l.apps.googleusercontent.com"),
		["https://www.googleapis.com/auth/calendar"]
	)
	flow.redirect_uri = "https://personal.yesasurya.com"
	authorization_url, state = flow.authorization_url(
		access_type='offline',
		include_granted_scopes='true'
	)
	return redirect(authorization_url)

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=443, ssl_context=("https/fullchain.pem", "https/privkey.pem"))