let partieId = null;

// MODE reçu depuis Flask
// "ia" ou "humain"
const modeJeu = MODE || "ia";

// ---------------------------
// CREER PARTIE
// ---------------------------
async function creerPartie() {

    const res = await fetch("/api/partie", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            joueur_sud: "Joueur Sud",

            joueur_nord:
                modeJeu === "ia"
                    ? "IA"
                    : "Joueur Nord"
        })
    });

    const data = await res.json();

    partieId = data.partie_id;

    chargerEtat();
}

// ---------------------------
// NOUVELLE PARTIE
// ---------------------------
async function nouvellePartie() {

    document.getElementById("victoryModal").style.display =
        "none";

    await creerPartie();
}

// ---------------------------
// CHARGER ETAT
// ---------------------------
async function chargerEtat() {

    const res = await fetch(`/api/etat/${partieId}`);

    const data = await res.json();

    afficher(data);

    if (data.terminee) {
        afficherVictoire(data.gagnant);
        return;
    }

    // IA uniquement en mode IA
    if (
        modeJeu === "ia" &&
        data.joueur_actuel === "NORD"
    ) {
        setTimeout(jouerIA, 800);
    }
}

// ---------------------------
// JOUER CASE
// ---------------------------
async function jouerCase(index) {

    if (!partieId) return;

    const res = await fetch("/api/jouer", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            partie_id: partieId,
            case: index
        })
    });

    const data = await res.json();

    if (data.error) {
        alert(data.error);
        return;
    }

    afficher(data);

    if (data.terminee) {
        afficherVictoire(data.gagnant);
        return;
    }

    // IA uniquement en mode IA
    if (
        modeJeu === "ia" &&
        data.joueur_actuel === "NORD"
    ) {
        setTimeout(jouerIA, 800);
    }
}

// ---------------------------
// IA
// ---------------------------
async function jouerIA() {

    const res = await fetch(`/ia/${partieId}`);

    const data = await res.json();

    afficher(data);

    if (data.terminee) {
        afficherVictoire(data.gagnant);
        return;
    }

    if (
        modeJeu === "ia" &&
        data.joueur_actuel === "NORD"
    ) {
        setTimeout(jouerIA, 800);
    }
}

// ---------------------------
// AFFICHAGE GENERAL
// ---------------------------
function afficher(data) {

    document.getElementById("score-nord").innerText =
        data.score_nord;

    document.getElementById("score-sud").innerText =
        data.score_sud;

    document.getElementById("info").innerText =
        data.terminee
            ? "Partie terminée"
            : "Tour : " + data.joueur_actuel;

    renderPlateau(
        data.plateau,
        data.joueur_actuel
    );
}

// ---------------------------
// AFFICHAGE PLATEAU
// ---------------------------
function renderPlateau(
    plateau,
    joueurActuel
) {

    const nord =
        document.getElementById("nord");

    const sud =
        document.getElementById("sud");

    nord.innerHTML = "";
    sud.innerHTML = "";

    // ------------------
    // NORD
    // ------------------

    for (let i = 13; i >= 7; i--) {

        if (
            modeJeu === "humain" &&
            joueurActuel === "NORD"
        ) {

            nord.innerHTML += `
                <div class="case"
                     onclick="jouerCase(${i})">
                     ${plateau[i]}
                </div>
            `;

        } else {

            nord.innerHTML += `
                <div class="case">
                    ${plateau[i]}
                </div>
            `;
        }
    }

    // ------------------
    // SUD
    // ------------------

    for (let i = 0; i <= 6; i++) {

        if (joueurActuel === "SUD") {

            sud.innerHTML += `
                <div class="case"
                     onclick="jouerCase(${i})">
                     ${plateau[i]}
                </div>
            `;

        } else {

            sud.innerHTML += `
                <div class="case">
                    ${plateau[i]}
                </div>
            `;
        }
    }
}

// ---------------------------
// MODAL VICTOIRE
// ---------------------------
function afficherVictoire(gagnant) {

    document.getElementById("winnerText").innerText =
        "🏆 Le gagnant est : " + gagnant;

    document.getElementById("victoryModal").style.display =
        "flex";
}

// ---------------------------
// DEMARRAGE
// ---------------------------
window.onload = () => {

    creerPartie();
};