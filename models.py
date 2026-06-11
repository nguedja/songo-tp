from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Partie(db.Model):
    __tablename__ = "parties"

    id = db.Column(db.Integer, primary_key=True)

    joueur_sud = db.Column(db.String(50), nullable=False)
    joueur_nord = db.Column(db.String(50), nullable=False)

    score_sud = db.Column(db.Integer, default=0)
    score_nord = db.Column(db.Integer, default=0)

    plateau = db.Column(db.Text, nullable=False)  # JSON stocké en texte

    joueur_actuel = db.Column(db.String(10), default="SUD")

    gagnant = db.Column(db.String(20), nullable=True)

    terminee = db.Column(db.Boolean, default=False)

    date_partie = db.Column(db.DateTime, default=datetime.utcnow)


class Coup(db.Model):
    __tablename__ = "coups"

    id = db.Column(db.Integer, primary_key=True)

    partie_id = db.Column(db.Integer, db.ForeignKey("parties.id"))

    joueur = db.Column(db.String(10), nullable=False)

    case_jouee = db.Column(db.Integer, nullable=False)

    plateau_apres = db.Column(db.Text)

    date_coup = db.Column(db.DateTime, default=datetime.utcnow)