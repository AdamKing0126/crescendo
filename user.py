"""
User object, dehydrated/rehydrated in json file
"""
class User:

    def __init__(self, username, token, email):
        self.username = username
        self.token = token
        self.email = email
