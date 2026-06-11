from flask import Flask, render_template, request, jsonify
from config import Config
from models import db, Partie
from game.songo import Songo
import json

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()

# ==================================================
# PAGES HTML
# ==================================================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/nouvelle-partie")
def nouvelle_partie():
    return render_template("nouvelle_partie.html")


@app.route("/game/humain")
def game_humain():
    return render_template(
        "game.html",
        mode="humain"
    )


@app.route("/game/ia")
def game_ia():
    return render_template(
        "game.html",
        mode="ia"
    )


@app.route("/game")
def game_page():
    return render_template("game.html")


@app.route("/historique")
def historique():

    parties = Partie.query.order_by(
        Partie.id.desc()
    ).all()

    return render_template(
        "historique.html",
        parties=parties
    )


# ==================================================
# CREATION PARTIE
# ==================================================

@app.route("/api/partie", methods=["POST"])
def creer_partie():

    data = request.json

    joueur_sud = data.get(
        "joueur_sud",
        "Joueur Sud"
    )

    joueur_nord = data.get(
        "joueur_nord",
        "Joueur Nord"
    )

    partie = Partie(
        joueur_sud=joueur_sud,
        joueur_nord=joueur_nord,
        plateau=json.dumps([5] * 14),
        joueur_actuel="SUD",
        score_sud=0,
        score_nord=0,
        terminee=False,
        gagnant=None
    )

    db.session.add(partie)
    db.session.commit()

    return jsonify({
        "message": "Partie créée",
        "partie_id": partie.id
    })


# ==================================================
# JOUER UN COUP
# ==================================================

@app.route("/api/jouer", methods=["POST"])
def jouer():

    data = request.json

    partie_id = data["partie_id"]
    case = data["case"]

    jeu = Songo(partie_id)

    resultat = jeu.jouer(case)

    return jsonify(resultat)


# ==================================================
# ETAT PARTIE
# ==================================================

@app.route("/api/etat/<int:partie_id>")
def etat(partie_id):

    jeu = Songo(partie_id)

    return jsonify(
        jeu.etat()
    )


# ==================================================
# IA
# ==================================================

@app.route("/ia/<int:partie_id>")
def jouer_ia(partie_id):

    jeu = Songo(partie_id)

    resultat = jeu.ia_jouer()

    if resultat is None:
        return jsonify(
            jeu.etat()
        )

    return jsonify(resultat)


# ==================================================
# HISTORIQUE JSON
# ==================================================

@app.route("/api/parties")
def toutes_parties():

    parties = Partie.query.order_by(
        Partie.id.desc()
    ).all()

    return jsonify([
        {
            "id": p.id,
            "joueur_sud": p.joueur_sud,
            "joueur_nord": p.joueur_nord,
            "score_sud": p.score_sud,
            "score_nord": p.score_nord,
            "gagnant": p.gagnant,
            "terminee": p.terminee,
            "date_partie": (
                p.date_partie.strftime(
                    "%d/%m/%Y %H:%M"
                )
                if p.date_partie
                else ""
            )
        }
        for p in parties
    ])


# ==================================================
# LANCEMENT
# ==================================================

if __name__ == "__main__":
    app.run(
        debug=True
    )