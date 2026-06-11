import json
from models import db, Partie, Coup


class Songo:
    """
    Moteur complet du jeu Songo connecté à SQLite.
    Version avancée avec règles principales.
    """

    def __init__(self, partie_id):
        self.partie_id = partie_id
        self.partie = Partie.query.get(partie_id)

        self.plateau = json.loads(self.partie.plateau)
        self.joueur_actuel = self.partie.joueur_actuel

        self.score_sud = self.partie.score_sud
        self.score_nord = self.partie.score_nord

        self.terminee = self.partie.terminee
        self.gagnant = self.partie.gagnant

    # ---------------------------
    # SAUVEGARDE
    # ---------------------------
    def sauvegarder(self):
        self.partie.plateau = json.dumps(self.plateau)
        self.partie.joueur_actuel = self.joueur_actuel
        self.partie.score_sud = self.score_sud
        self.partie.score_nord = self.score_nord
        self.partie.terminee = self.terminee
        self.partie.gagnant = self.gagnant

        db.session.commit()

    def enregistrer_coup(self, joueur, case, plateau_apres):
        coup = Coup(
            partie_id=self.partie_id,
            joueur=joueur,
            case_jouee=case,
            plateau_apres=json.dumps(plateau_apres)
        )
        db.session.add(coup)
        db.session.commit()

    # ---------------------------
    # COUPS POSSIBLES
    # ---------------------------
    def coups_possibles(self, joueur):
        if joueur == "SUD":
            return [i for i in range(0, 7) if self.plateau[i] > 0]
        else:
            return [i for i in range(7, 14) if self.plateau[i] > 0]

    # ---------------------------
    # VALIDATION COUP
    # ---------------------------
    def coup_valide(self, case):

        if self.terminee:
            return False

        if case < 0 or case > 13:
            return False

        if self.joueur_actuel == "SUD" and not (0 <= case <= 6):
            return False

        if self.joueur_actuel == "NORD" and not (7 <= case <= 13):
            return False

        if self.plateau[case] == 0:
            return False

        # interdiction case 7 SUD (case 6 index)
        if self.joueur_actuel == "SUD" and case == 6:
            if self.plateau[case] in [1, 2]:
                return False

        return True

    # ---------------------------
    # SEMIS
    # ---------------------------
    def semer(self, case):
        graines = self.plateau[case]
        self.plateau[case] = 0

        pos = case

        while graines > 0:
            pos = (pos + 1) % 14
            self.plateau[pos] += 1
            graines -= 1

        return pos

    # ---------------------------
    # CAPTURE (VERSION AVANCEE)
    # ---------------------------
    def capturer(self, case):

        # règle spéciale case 1 adverse
        if self.joueur_actuel == "SUD" and case == 7:
            self.score_sud += 1
            self.plateau[case] -= 1
            return

        if self.joueur_actuel == "NORD" and case == 6:
            self.score_nord += 1
            self.plateau[case] -= 1
            return

        captures = 0
        courant = case

        while True:

            if self.joueur_actuel == "SUD" and not (7 <= courant <= 13):
                break

            if self.joueur_actuel == "NORD" and not (0 <= courant <= 6):
                break

            if not (2 <= self.plateau[courant] <= 4):
                break

            captures += self.plateau[courant]
            self.plateau[courant] = 0

            courant -= 1

        if self.joueur_actuel == "SUD":
            self.score_sud += captures
        else:
            self.score_nord += captures

    # ---------------------------
    # SOLIDARITE
    # ---------------------------
    def verifier_solidarite(self):

        camp_adverse_vide = (
            sum(self.plateau[7:14]) == 0 if self.joueur_actuel == "SUD"
            else sum(self.plateau[0:7]) == 0
        )

        if not camp_adverse_vide:
            return True

        for case in self.coups_possibles(self.joueur_actuel):

            temp = self.plateau[case]
            pos = case
            graines = temp

            while graines > 0:
                pos = (pos + 1) % 14
                graines -= 1

                if self.joueur_actuel == "SUD" and 7 <= pos <= 13:
                    return True

                if self.joueur_actuel == "NORD" and 0 <= pos <= 6:
                    return True

        return False

    # ---------------------------
    # JEU
    # ---------------------------
    def jouer(self, case):

        if not self.coup_valide(case):
            return {"error": "Coup invalide"}

        if not self.verifier_solidarite():
            self.terminee = True
            self.determiner_gagnant()
            return {"error": "Solidarité impossible - fin de partie"}

        joueur = self.joueur_actuel

        derniere_case = self.semer(case)
        self.capturer(derniere_case)

        self.enregistrer_coup(joueur, case, self.plateau)

        self.verifier_fin()

        if not self.terminee:
            self.changer_joueur()

        self.sauvegarder()

        return self.etat()

    # ---------------------------
    # CHANGEMENT JOUEUR
    # ---------------------------
    def changer_joueur(self):
        self.joueur_actuel = "NORD" if self.joueur_actuel == "SUD" else "SUD"

    # ---------------------------
    # FIN DE PARTIE
    # ---------------------------
    def verifier_fin(self):

        if self.score_sud >= 40:
            self.terminee = True
            self.gagnant = "SUD"
            return

        if self.score_nord >= 40:
            self.terminee = True
            self.gagnant = "NORD"
            return

        if len(self.coups_possibles(self.joueur_actuel)) == 0:
            self.terminee = True
            self.determiner_gagnant()
            return

        if sum(self.plateau) < 10:
            self.terminee = True
            self.determiner_gagnant()
            return

    # ---------------------------
    # GAGNANT
    # ---------------------------
    def determiner_gagnant(self):

        total_sud = self.score_sud + sum(self.plateau[0:7])
        total_nord = self.score_nord + sum(self.plateau[7:14])

        if total_sud > total_nord:
            self.gagnant = "SUD"
        elif total_nord > total_sud:
            self.gagnant = "NORD"
        else:
            self.gagnant = "MATCH NUL"

    # ---------------------------
    # ETAT
    # ---------------------------
    def etat(self):

        return {
            "plateau": self.plateau,
            "joueur_actuel": self.joueur_actuel,
            "score_sud": self.score_sud,
            "score_nord": self.score_nord,
            "terminee": self.terminee,
            "gagnant": self.gagnant
        }

    def ia_jouer(self):
        """
        IA simple pour le joueur NORD
        """

        if self.terminee:
          return None

        coups = self.coups_possibles("NORD")

        if not coups:
          self.terminee = True
          self.determiner_gagnant()
          return None

        # stratégie simple :
        # choisir la case avec le plus de graines
        meilleur_coup = max(coups, key=lambda c: self.plateau[c])

        return self.jouer(meilleur_coup)    