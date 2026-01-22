
import os
from flask import Flask, render_template

app = Flask(__name__)


from api import api
from route import route
from esp import esp

# Les blueprints serevnt à séparer les différentes parties de l'application
# Quand on va sur /api/quelquechose, ça va aller dans api.py puis sur les
# routes définies dans là bas.
app.register_blueprint(route, url_prefix='/')
app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(esp, url_prefix='/request')


###############################################################################
###########################___LANCE L'APPLICATION___###########################
###############################################################################


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)