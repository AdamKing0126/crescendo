import json
from flask import Flask, url_for, redirect, session, render_template, request, g
from authlib.integrations.flask_client import OAuth
import requests
from utils import build_repo_data, read_user, write_user, logout_user
from user import User

app = Flask(__name__)
app.config.from_file("config.json", load=json.load)

CLIENT_ID = app.config.get("GITHUB_CLIENT_ID")
CLIENT_SECRET = app.config.get("GITHUB_CLIENT_SECRET")
SCOPE = 'user:email'

oauth = OAuth(app)
github = oauth.register(
    name='github',
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': SCOPE},
)


@app.route('/')
def index():
    current_user = session.get('user')
    return render_template('index.html')


@app.route("/login")
def login():
    redirect_url = url_for("authorize", _external=True)
    return github.authorize_redirect(redirect_url)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index", _external=True))


@app.route("/authorize")
def authorize():
    """
    Get the github user, write their username into
    the session, store the user in the json file database
    """
    token = github.authorize_access_token()
    resp = github.get('user', token=token)
    profile_data = resp.json()
    user = User(username=profile_data['login'],
                token=token['access_token'],
                email=profile_data['email'])
    write_user(user)
    session['user'] = user.username
    return redirect('/')


@app.route("/activation_code", methods=['POST'])
def activation_code():
    """
    Super simple form handling.  Does the activation code match?
    """
    if request.form.get('activation_code') == 'OCTOCAT':
        repos_url = url_for('repos', _external=True)
        return redirect(repos_url)
    logout_user()
    return render_template('error.html')


@app.route("/repos")
def repos():
    """
    Retrieve the user's Github repos and display them 
    in a template
    """
    user = read_user()
    api_url = f"https://api.github.com/users/{user.username}/repos"
    response = requests.get(api_url)
    repos = build_repo_data(response.json())
    return render_template("repos.html", repos=repos)


if __name__ == '__main__':
    app.config['SESSION_TYPE'] = 'filesystem'
    app.secret_key = app.config.get("SECRET_KEY")
    app.run(debug=True, host="0.0.0.0", port=5000)
