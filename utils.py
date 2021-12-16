import json
from user import User
from flask import session
import requests


def logout_user():
    session.pop('user')

def write_user(user):
    """
    Store the user in the "database" (json file)
    """
    with open('data.json', 'w') as f:
        json.dump(user.__dict__, f)


def read_user():
    """
    Pull the user data out of the "database"
    """
    with open('data.json', 'r') as f:
        user_data = f.read()
        if user_data:
            return User(**json.loads(user_data))
    return None


def make_fake_repo(idx):
    """
    Build a fake repo data object
    """
    return {
        "name": f"repo_{idx}", 
        "stars": idx, 
        "pulls": idx, 
        "owner": f"owner_{idx}", 
        "url": "https://www.github.com"
    }


def build_repo_data(data):
    """
    Given a data object from Github, construct a list of dicts
    to be rendered in the template
    """
    repos = []
    for elem in data:
        name = elem['name']
        stars = elem['stargazers_count']
        pulls_url = f"https://api.github.com/repos/{elem['full_name']}/pulls?state=all"
        pulls_count = len(requests.get(pulls_url).json())
        owner = elem['owner']['login']
        url = elem['html_url']
        repos.append({'name': name, 'stars': stars, 'pulls': pulls_count, 'owner': owner, 'url': url})

    # If we don't have enough repos to make a full page of them, add some fake
    # ones
    if len(repos) < 10:
        for x in range(10):
            repos.append(make_fake_repo(x))

    return repos
