from flask import Flask, render_template, request, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
from google_auth_oauthlib.flow import Flow
from flask import session, url_for, redirect

# Configure the OAuth flow
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # ONLY for development!
CLIENT_SECRETS_FILE = "client_secret_247911754370-mavihk86ul34h1nch20dumjrn1r7s43a.apps.googleusercontent.com.json"
SCOPES = ['https://www.googleapis.com/auth/calendar']

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a real secret key for production
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_calendar():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'excel_file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['excel_file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            # Add logic to process the file and interact with Google Calendar here
            flash('File successfully uploaded and processed')
            # Redirect or process the file as needed
            return redirect(url_for('upload_calendar'))
    return render_template('upload.html')


@app.route('/authorize')
def authorize():
    # Create a flow instance to manage the OAuth 2.0 Authorization Grant Flow steps
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=['https://www.googleapis.com/auth/calendar'],
        redirect_uri=url_for('oauth2callback', _external=True))

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')

    # Store the state in the session so that the callback can verify the
    # auth server response.
    session['state'] = state

    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    state = session['state']

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=['https://www.googleapis.com/auth/calendar'],
        state=state,
        redirect_uri=url_for('oauth2callback', _external=True))

    flow.fetch_token(authorization_response=request.url)

    if not flow.credentials.is_valid():
        return 'Failed to fetch credentials', 401

    # Store the credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    # credentials in a persistent database instead.
    session['credentials'] = flow.credentials

    return redirect(url_for('upload_calendar'))

# You will need to define the route that triggers the 'authorize' method.


# Include other routes and functions as necessary

if __name__ == '__main__':
    app.run(debug=True)
