# Ce script sert à envoyer la bonne page quand l'utilisateur va sur un lien
# Exemple : /about => about.html

from flask import Blueprint,render_template



route = Blueprint("route",__name__)

###############################################################################
####################___PARTIE DEDIEE AUX CHEMIN DES PAGES___###################
###############################################################################


@route.route("/")
def index():
    return render_template("index.html")

@route.route("/about") # ici, quand l'utilisateur va aller sur /about
def about(): # la fonction about va être appelée
    return render_template("about.html") # et la page about.html va être affichée.

@route.route("/history")
def history():
    return render_template("history.html")


@route.route("/statistical")
def statistical():
    
    return render_template('statistical.html')

@route.route("/login")
def login():
    
    return render_template('account/login.html')

@route.route("/signup")
def signup():
    
    return render_template('account/signup.html')
