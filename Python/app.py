import base64
from flask import abort, Flask, redirect, request, session, url_for
import os
import requests
import urllib

app = Flask(__name__)
app.secret_key = 'ChangeThisToSomethingRandom'

APP_KEY = '<YOUR APP KEY>';
APP_SECRET = '<YOUR APP SECRET>';

@app.route('/')
def index():
	csrf_token = base64.urlsafe_b64encode(os.urandom(18))
	session['csrf_token'] = csrf_token
	return redirect('https://www.dropbox.com/1/oauth2/authorize?%s' % urllib.urlencode({
		'client_id': APP_KEY,
		'redirect_uri': url_for('callback', _external=True),
		'response_type': 'code',
		'state': csrf_token
	}))

@app.route('/callback')
def callback():
	if request.args['state'] != session.pop('csrf_token'):
		abort(403)
	data = requests.post('https://api.dropbox.com/1/oauth2/token',
		data={
			'code': request.args['code'],
			'grant_type': 'authorization_code',
			'redirect_uri': url_for('callback', _external=True)
		},
		auth=(APP_KEY, APP_SECRET)).json()
	token = data['access_token']

	info = requests.get('https://api.dropbox.com/1/account/info', headers={'Authorization': 'Bearer %s' % token}).json()
	return 'Successfully authenticated as %s.' % info['display_name']

if __name__=='__main__':
	app.run(debug=True)
