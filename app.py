from flask import Flask, render_template, request, jsonify, redirect, url_for
import random
import os
from supabase import create_client, Client

app = Flask(__name__)

# ==========================
#  SUPABASE CONFIG
# ==========================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL o SUPABASE_KEY no están configuradas")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

CHAT_ID = "madison"   # identificador del chat
MAX_MENSAJES = 20     # últimos 20 visibles

# ==========================
#  FRASES (NO TOCADAS)
# ==========================
EMOCIONES = {
    "ternura": [
        "Cada que veo un mensaje tuyo me acuerdo del primero que te mande, como si no te conociera y todo empezara de cero.",
        "Eres un mundo al que quiero conocer por cielo y tierra.",
        "Me gustaria saber que se siente mirarte a los ojos, no se si me ponga nervioso",
        "En cualquier momento nos podemos dejar de hablar pero yo se que te seguiras acordando de mi.",
        "Yo se que somos mundos diferentes porque sabemos que ambos somos como agua y aceite pero quiero sentir esa adrenalina contigo."
    ],
    "risa": [
        "Quieres jugar otro juego mas comprometido? se tienen que respetar las reglas",
        "Subierias una montaña conmigo?",
        "Seguro pusiste cara rara leyendo mis ocurrencias 😂",
        "Grabate todo de mi porque no soy un video para que le des retroceder",
        "No te coqueteo… solo me sale natural y si lo ves coqueteo avisame.",
        "Saldrias de noche conmigo y no regresar hasta el dia siguiente cansada pero contenta?",
    ],
    "picante": [
        "Que harias si te beso?",
        "No pases una noche conmigo porque vas a querer otra y no siempre voy a estar disponible",
        "Te dejarias hacer lo que yo te diga y obedecer cada palabra como niña buena?",
        "No sigas viendo esto.",
        "Que harias si beso tu cuello y luego tomo tu cintura y te jalo hacia mi ?",
        "Que harias si cierro la puerta y jugamos a los nudos, pero tu vas primero, y ya no te puedes mover y comienzo a besarte lento?",
        "Me dejerias poner mi mano en tu cuello y someterte mientras te digo cosas que nuca te han dicho en tu vida",
        "No tengo prisa contigo pero el deseo se puede acumular y cuando se detone esto sera muy violento",
    ],
    "sorpresa": [
        "Irias por CDMX conmigo a 10 lados diferentes yo los escojo y tu escoges el ultimo",
        "Tu y yo en la oscuridad y que solo nuestras manos sientan y vean lo que esta pasando",
        "Quiero verte en persona pero eso es algo que se dara natural y sin presiones",
        "Me dejarias entrar a tu mente?",
        "Que todo esto sea un secreto, no le dire a nadie, los tesoros se guardan bien"
    ]
}

# ==========================
#  HELPERS SUPABASE (CHAT)
# ==========================
def guardar_mensaje(de, texto):
    supabase.table("mensajes").insert({
        "chat": CHAT_ID,
        "de": de,
        "texto": texto
    }).execute()

def obtener_historial():
    res = (
        supabase.table("mensajes")
        .select("de, texto, created_at")
        .eq("chat", CHAT_ID)
        .order("created_at", desc=False)
        .limit(MAX_MENSAJES)
        .execute()
    )
    return res.data if res.data else []

# ==========================
#  NO REPETIR FRASE (mood_state)
# ==========================
def get_last_mood(emocion: str):
    res = (
        supabase.table("mood_state")
        .select("last_text")
        .eq("chat", CHAT_ID)
        .eq("emocion", emocion)
        .limit(1)
        .execute()
    )
    if res.data and len(res.data) > 0:
        return res.data[0].get("last_text")
    return None

def set_last_mood(emocion: str, last_text: str):
    # upsert por PK (chat, emocion)
    supabase.table("mood_state").upsert({
        "chat": CHAT_ID,
        "emocion": emocion,
        "last_text": last_text
    }).execute()

def pick_non_repeating_phrase(emocion: str) -> str:
    opciones = EMOCIONES.get(emocion, [])
    if not opciones:
        return ""

    # Si solo hay 1 frase, no hay forma de evitar repetir
    if len(opciones) == 1:
        return opciones[0]

    last = get_last_mood(emocion)

    # elige una distinta a la última (hasta 10 intentos)
    frase = random.choice(opciones)
    intentos = 0
    while last is not None and frase == last and intentos < 10:
        frase = random.choice(opciones)
        intentos += 1

    set_last_mood(emocion, frase)
    return frase

# ==========================
#  ROUTES
# ==========================
@app.route("/")
def home():
    return redirect(url_for("app_view"))

@app.route("/app", methods=["GET", "POST"])
def app_view():
    frase = None

    if request.method == "POST":
        if "emocion" in request.form:
            emo = request.form["emocion"]
            if emo in EMOCIONES:
                frase = pick_non_repeating_phrase(emo)
                return redirect(url_for("app_view", f=frase))

        if "pregunta" in request.form:
            texto = request.form["pregunta"].strip()
            if texto:
                guardar_mensaje("ella", texto)
            return redirect(url_for("app_view"))

    frase = request.args.get("f")
    return render_template(
        "index.html",
        frase_generada=frase,
        estado_url=url_for("estado")
    )

@app.route("/panel_miguel", methods=["GET"])
def panel():
    return render_template(
        "miguel.html",
        estado_url=url_for("estado"),
        post_url=url_for("post_miguel")
    )

@app.route("/post_miguel", methods=["POST"])
def post_miguel():
    texto = request.form.get("respuesta", "").strip()
    if texto:
        guardar_mensaje("miguel", texto)
    return redirect(url_for("panel"))

@app.route("/estado")
def estado():
    return jsonify({"historial": obtener_historial()})

@app.route("/favicon.ico")
def favicon():
    return ("", 204)

if __name__ == "__main__":
    app.run(debug=True)
