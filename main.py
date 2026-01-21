
from flask import Flask, render_template

app = Flask(__name__)


from api import api
from route import route
from esp import esp

app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(route, url_prefix='/')
app.register_blueprint(esp, url_prefix='/request')


###############################################################################
###########################___LANCE L'APPLICATION___###########################
###############################################################################


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)