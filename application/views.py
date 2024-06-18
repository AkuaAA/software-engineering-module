from flask import Blueprint


views = Blueprint('views', __name__)

@views.route('/')
def home():
    return "<h1> Welcome To The App-Innovation Opportunity Tracker!</h1>"