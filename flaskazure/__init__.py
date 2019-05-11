from flask import Flask

app = Flask(__name__)
wsgi_app = app.wsgi_app
app.config['SECRET_KEY'] = 'ee7ef4b4a154afc46fe57298d41e9c65'

from flaskazure import routes
