from flask import Blueprint,render_template



route = Blueprint("route",__name__)
###############################################################################
####################___PARTIE DEDIEE AUX CHEMIN DES PAGES___###################
###############################################################################


@route.route("/")
def index():
    return render_template("index.html")

@route.route("/about")
def about():
    return render_template("about.html")

@route.route("/history")
def history():
    return render_template("history.html")



@route.route("/statistical")
def statistical():
    
    return render_template('statistical.html')
