
from flask import Flask, render_template, request, jsonify, redirect, url_for
import random, json, os

app = Flask(__name__)

DATA_2 = "data_app2.json"
MAX_MENSAJES = 8

EMOCIONES = {
    "ternura": [
        "Me caes bien. Eso ya es raro.",
        "No doy atención fácil… pero aquí andas.",
        "Tienes algo tranquilo… y eso engancha.",
        "Me gusta tu vibra. Sin prisa.",
        "Esto se siente bien… lo dejo ahí."
    ],
    "risa": [
        "No prometo ser serio, pero sí interesante.",
        "Ok… eso estuvo bien. Punto para ti 😏",
        "Yo vengo a sumar, no a rogar 😂",
        "Si te ríes, ya gané un poquito.",
        "No soy tu entretenimiento… pero sí puedo ser tu mejor distracción."
    ],
    "picante": [
        "Yo no provoco… solo dejo la puerta entreabierta 😌",
        "Si te da curiosidad, vas bien.",
        "No me apuro. Cuando algo vale, se construye.",
        "Me gusta el juego… pero con clase.",
        "Tú di el ritmo. Yo me adapto."
    ],
    "sorpresa": [
        "No siempre respondo rápido… pero cuando lo hago, se nota.",
        "Te estoy leyendo más de lo que crees 👀",
        "Curioso que sigas aquí… interesante.",
        "Esto puede ponerse bueno, si tú quieres.",
        "No te voy a decir todo. Me gusta dejar algo pendiente."
    ]
}

def load_state():
    if not os.path.exists(DATA_2):
        return {"historial": []}
    try:
        with open(DATA_2, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"historial": []}

def save_state(historial):
    with open(DATA_2, "w", encoding="utf-8") as f:
        json.dump({"historial": historial[-MAX_MENSAJES:]}, f, ensure_ascii=False)

@app.route("/app", methods=["GET", "POST"])
def app_view():
    state = load_state()
    historial = state["historial"]
    frase = None

    if request.method == "POST":
        if "emocion" in request.form:
            emo = request.form["emocion"]
            if emo in EMOCIONES:
                frase = random.choice(EMOCIONES[emo])
                return redirect(url_for("app_view", f=frase))

        if "pregunta" in request.form:
            texto = request.form["pregunta"].strip()
            if texto:
                historial.append({"de": "ella", "texto": texto})
                save_state(historial)
            return redirect(url_for("app_view"))

    frase = request.args.get("f")
    return render_template("index.html", frase_generada=frase, estado_url=url_for("estado"))

@app.route("/panel_miguel", methods=["GET"])
def panel():
    return render_template("miguel.html", estado_url=url_for("estado"), post_url=url_for("post_miguel"))

@app.route("/post_miguel", methods=["POST"])
def post_miguel():
    state = load_state()
    historial = state["historial"]
    texto = request.form.get("respuesta", "").strip()
    if texto:
        historial.append({"de": "miguel", "texto": texto})
        save_state(historial)
    return redirect(url_for("panel"))

@app.route("/estado")
def estado():
    return jsonify(load_state())

if __name__ == "__main__":
    app.run(debug=True)
