import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')

import os

###############################################################################
#######################___PARTIE DEDIEE AU GRAPHIQUE___########################
###############################################################################

def create_graph_line(var, echelle, label_x="Date", label_y="Value", line_title=["Line 1"], title="Title", x=10, y=5, color=["tab:blue"],date="today",limit=24):
    """
    Cette fonction sert a créer un graphique de type linéaire
    """
    from app.api import api_datas_list # on utilise la fonction api_datas_list pour récupérer 24 données selon la date

    hour = api_datas_list(echelle,limit=limit,date_filter=date)

    if not hour:
        print(f"[ERREUR] Aucune date trouvee pour {echelle}")
        return

    x = limit/5
    plt.figure(figsize=(x, y))
    plt.margins(x=0.01, y=0.01)

    for i in range(len(var)):
        values = api_datas_list(var[i],limit=limit,date_filter=date)
        if not values:
            print(f"[ERREUR] Aucune valeur trouvee pour {var[i]}")
            continue
        # Ajuster la longueur des valeurs pour correspondre aux hour
        values = values[-len(hour):]  # Prendre les dernières valeurs
        plt.plot(hour, values, marker='o', color=color[i], label=line_title[i])

    plt.title(f"{title} | {date}")
    plt.xlabel(label_x)
    plt.ylabel(label_y)
    plt.xticks(rotation=90)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(BASE_DIR, 'static')
    os.makedirs(static_dir, exist_ok=True)
    # On sauvegarde le graphique avec le titre du graphique. l'ancien se fait écraser.
    file_path = os.path.join(static_dir, f"graph_{title}.png") 

    try:
        plt.savefig(file_path)
        plt.close()
        print(f"Graphique sauvegardé à : {file_path}")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde : {e}")
        plt.close()
        return "Erreur interne — impossible de générer le graphique", 500
# exemple d'utilisation
# create_graph_line(["pressure1","pressure2"],"hour",label_x="",label_y="hPa",line_title=["Sensor 1","Sensor 2"],title="Pressures", color =["tab:blue","tab:red"])



def create_graph_bar(var,echelle,label_x="abscissa",label_y="height",bar_title=["title of bar"],title="Title",x=10,y=5,color=["tab:blue"],limit=24,date="today"):
    """
    Cette fonction sert a créer un graphique de type barres
    """
    from app.api import api_datas_list

    hour = api_datas_list(echelle,limit=limit,date_filter=date)

    if not hour:
        print(f"[ERREUR] Aucune date trouvee pour {echelle}")
        return

    x = limit/5
    plt.figure(figsize=(x, y))
    plt.margins(x=0.01, y=0.01)

    n = len(var)
    bar_width = 0.8 / n
    x_positions = np.arange(len(hour))
    for i in range(n):
        offset = (i - n/2 + 0.5) * bar_width
        values = api_datas_list(var[i],limit=limit,date_filter=date)
        if not values:
            print(f"[ERREUR] Aucune valeur trouvee pour {var[i]}")
            continue
        values = values[-len(hour):]  # Ajuster la longueur
        plt.bar(x_positions + offset,
                values,
                width=bar_width,
                color=color[i],
                label=bar_title[i],
                alpha=0.7)
    plt.xticks(x_positions, hour, rotation=90, ha='right')
    plt.title(f"{title} | {date}")
    plt.xlabel(label_x)
    plt.ylabel(label_y)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(BASE_DIR, 'static')
    os.makedirs(static_dir, exist_ok=True)

    file_path = os.path.join(static_dir, f"graph_{title}.png")

    try:
        plt.savefig(file_path)
        plt.close()
        print(f"Graphique sauvegardé à : {file_path}")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde : {e}")
        plt.close()
        return "Erreur interne — impossible de générer le graphique", 500

# exemple d'utilisation
# create_graph_bar(["humidity1","humidity2"],"hour",label_x="",label_y="%",bar_title=["Sensor 1","Sensor 2"],title="Humidity levels", color =["tab:blue","tab:red"])
