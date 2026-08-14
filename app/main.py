import asyncio
import html
import os
import random
import secrets
import time
import uuid
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response, StreamingResponse
from starlette.middleware.sessions import SessionMiddleware

# FAVICON SVG: Lightbulb + Gear + Gold Coin Theme
FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">
  <rect width="64" height="64" rx="16" fill="#0f172a"/>
  <!-- Gear background -->
  <path d="M 32 10 L 35 14 L 40 13 L 42 18 L 47 19 L 47 24 L 51 27 L 49 32 L 51 37 L 47 40 L 47 45 L 42 46 L 40 51 L 35 50 L 32 54 L 29 50 L 24 51 L 22 46 L 17 45 L 17 40 L 13 37 L 15 32 L 13 27 L 17 24 L 17 19 L 22 18 L 24 13 L 29 14 Z" fill="#b45309" opacity="0.3"/>
  <!-- Lightbulb Glow -->
  <circle cx="32" cy="28" r="16" fill="#f59e0b" opacity="0.25"/>
  <!-- Lightbulb Body -->
  <path d="M 22 28 C 22 20, 42 20, 42 28 C 42 33, 37 36, 37 41 L 27 41 C 27 36, 22 33, 22 28 Z" fill="#fbbf24"/>
  <!-- Lightbulb Base -->
  <rect x="27" y="42" width="10" height="3" rx="1" fill="#94a3b8"/>
  <rect x="28" y="46" width="8" height="2" rx="1" fill="#64748b"/>
  <!-- Filament Spark -->
  <path d="M 32 24 L 30 29 L 34 29 L 32 34" stroke="#d97706" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
  <!-- Gold Coin overlay -->
  <circle cx="46" cy="46" r="10" fill="#f59e0b" stroke="#78350f" stroke-width="2"/>
  <circle cx="46" cy="46" r="7" fill="#fbbf24"/>
  <text x="46" y="50" font-size="10" font-weight="bold" fill="#78350f" text-anchor="middle">$</text>
</svg>"""

SESSION_SECRET = os.getenv("SESSION_SECRET") or secrets.token_urlsafe(32)

fastapi_app = FastAPI(title="Inventori Pazzi")
fastapi_app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    same_site="lax",
    https_only=os.getenv("SESSION_HTTPS_ONLY", "false").lower() == "true",
)
app = fastapi_app

# --- DATASETS (>100 Problemi, >250 Parole/Oggetti) ---
PROBLEMI = [
    "Come evitare di fare i compiti durante le vacanze estive?",
    "Come svegliarsi la mattina presto senza usare la sveglia?",
    "Come mangiare la pizza senza sporcarsi mai le mani?",
    "Come raffreddare una minestra bollente in meno di 3 secondi?",
    "Come convincere il proprio cane a portarti le ciabatte al letto?",
    "Come piegare i lenzuoli con gli angoli senza impazzire?",
    "Come non piangere assolutamente mentre si tagliano le cipolle?",
    "Come ritrovare sempre il secondo calzino scomparso dopo il lavaggio?",
    "Come far finta di ascoltare con attenzione durante una riunione noiosa?",
    "Come fare la spesa al supermercato senza comprare cibo spazzatura?",
    "Come pettinarsi le sopracciglia dopo essere scesi da una montagna russa?",
    "Come recuperare le chiavi cadute in un tombino stretto?",
    "Come scaldare i piedi freddi sotto le coperte d'inverno?",
    "Come smettere di starnutire nei momenti meno opportuni?",
    "Come aprire un barattolo di marmellata con il coperchio bloccato?",
    "Come fare foto perfette ai gatti senza che si girino dall'altra parte?",
    "Come non far sciogliere il gelato al pistacchio al sole d'agosto?",
    "Come rimuovere i pelucchi dal maglione di lana preferito?",
    "Come camminare sui sassi in spiaggia senza fare facce strane?",
    "Come zittire il vicino che suona la batteria alle tre di notte?",
    "Come fare la valigia facendoci entrare il triplo dei vestiti?",
    "Come togliere l'etichetta del prezzo senza lasciare la colla appiccicosa?",
    "Come rinfrescare la macchina parcheggiata al sole in estate?",
    "Come evitare che il gatto graffi il divano nuovo in pelle?",
    "Come fare entrare un divano angolare in un ascensore piccolissimo?",
    "Come superare l'ansia quando il cameriere porta il conto al ristorante?",
    "Come prendere la ciambella dal fondo dell'armadio senza far cadere tutto?",
    "Come ricaricare lo smartphone senza usare cavi nè prese elettriche?",
    "Come evitare che il gelato sgoccioli sulla maglietta bianca?",
    "Come dire a qualcuno che ha un pezzo di insalata tra i denti senza metterlo a disagio?",
    "Come fare il bagno al mare mantenendo l'asciugamano asciutto?",
    "Come asciugarsi le mani in bagno quando finiscono i tovagliolini?",
    "Come nascondere i dolci ai fratelli o alle sorelle golose?",
    "Come ritrovare il telecomando nascosto tra i cuscini del divano?",
    "Come raffreddare l'interno della macchina senza aria condizionata?",
    "Come bere la cioccolata calda senza bruciarsi la lingua?",
    "Come sbucciare le uova sode senza rompere l'albume?",
    "Come evitare che i cavi degli auricolari si aggroviglino in tasca?",
    "Come lavare i piatti sporchi senza bagnarsi la manica della felpa?",
    "Come impedire che gli occhiali si appannino quando si entra in casa d'inverno?",
    "Come togliere le briciole di patatine dalla tastiera del PC?",
    "Come addormentarsi in 2 minuti quando c'è un caldo soffocante?",
    "Come tagliare l'anguria gigante senza allagare il tavolo della cucina?",
    "Come fare i popcorn a casa senza bruciarne nemmeno uno?",
    "Come ritrovare l'automobile nel parcheggio di un centro commerciale enorme?",
    "Come togliere il chewing-gum rimasto attaccato sotto la scarpa?",
    "Come far durare il sapone per le mani il doppio del tempo?",
    "Come pettinarsi la mattina senza specchio ed essere impeccabili?",
    "Come trasportare 10 buste della spesa dal bagagliaio al terzo piano in un solo viaggio?",
    "Come evitare che il caffè della moka fuoriesca sporcando il fornello?",
    "Come stirare una camicia stropicciata senza usare il ferro da stiro?",
    "Come far smettere subito il singhiozzo improvviso durante un esame?",
    "Come staccare due bicchieri di vetro incastrati l'uno nell'altro?",
    "Come togliere l'odore di aglio dalle mani dopo aver cucinato?",
    "Come convincere un bimbo piccolo a mangiare i broccoli e le verdure?",
    "Come raccogliere le briciole dal divano senza aspirapolvere?",
    "Come far stare dritti i calzini corti che scivolano dentro la scarpa?",
    "Come evitare di perdere il filo quando si racconta una barzelletta?",
    "Come spalmarsi la crema solare sulla schiena da soli senza aiuto?",
    "Come suonare il campanello di casa quando si hanno le mani occupate?",
    "Come rimuovere i peli del cane dai vestiti prima di uscire di casa?",
    "Come fare in modo che l'acqua della pasta non schiumi e fuoriesca dalla pentola?",
    "Come trasportare una torta di panna in bicicletta senza distruggerla?",
    "Come evitare che il gatto salti sulla tastiera mentre si lavora?",
    "Come asciugare le scarpe da ginnastica bagnate dalla pioggia entro un'ora?",
    "Come tagliare una torta in parti uguali senza usare il coltello?",
    "Come fermare una fontana di bibita gassata appena stappata?",
    "Come riuscire a infilare il filo nella cruna dell'ago al primo tentativo?",
    "Come pulire gli occhiali senza lasciare neanche un alone?",
    "Come evitare che le caramelle gommose si appiccichino tra loro d'estate?",
    "Come trasportare un cono gelato con tre palline mentre si guida il monopattino?",
    "Come raffreddare una lattina di bibita in 60 secondi netti?",
    "Come evitare che il sapone scivoli via dalle mani nella doccia?",
    "Come togliere una macchia di pomodoro fresco da una camicia bianca?",
    "Come fare foto a un gruppo di 20 persone senza che qualcuno chiuda gli occhi?",
    "Come accendere un fuoco da campeggio senza fiammiferi nè accendino?",
    "Come far profumare le scarpe da ginnastica dopo una corsa di 10 km?",
    "Come evitare di addormentarsi sulle sedie scomode della sala d'attesa?",
    "Come versare il succo dal cartone senza farlo schizzare ovunque?",
    "Come recuperare un anello caduto nel tubo dello scarico del lavandino?",
    "Come pulire le griglie del barbecue crostose senza faticare?",
    "Come impedire al cane di abbaiare ogni volta che suona il citofono?",
    "Come svitare una vite con la testa sgranata e consumata?",
    "Come non fare rumore quando si apre il pacchetto di patatine di notte?",
    "Come non far scivolare il tappetino del bagno sul pavimento bagnato?",
    "Come tenere fresche le bibite in spiaggia senza la borsa frigo?",
    "Come togliere la sabbia appiccicata ai piedi prima di salire in macchina?",
    "Come togliere il guscio da un uovo sodo in meno di due secondi?",
    "Come cucinare il pesce in casa senza lasciare odore per tre giorni?",
    "Come sbloccare una zip della giacca incastrata nel tessuto?",
    "Come non far cadere le gocce di candela sulla tovaglia buona?",
    "Come evitare di battere il mignolino del piede contro lo spigolo del letto?",
    "Come conservare l'avocado aperto senza farlo diventare nero?",
    "Come dosare la quantità esatta di spaghetti da buttare in pentola?",
    "Come piegare una mappa stradale gigante esattamente lungo le pieghe originali?",
    "Come togliere la pittura dalle mani dopo aver ridipinto la camera?",
    "Come recuperare l'ultimo centimetro di dentifricio dal tubetto schiacciato?",
    "Come evitare di scottarsi la lingua assaggiando il sugo di pomodoro?",
    "Come togliere la polvere dietro i termosifoni stretti?",
    "Come evitare che il pane diventi duro dopo solo un giorno?",
    "Come fare un nodo alla cravatta perfetto in meno di 10 secondi?",
    "Come non far volare via il cappello quando c'è un vento fortissimo?",
    "Come evitare di dimenticare dove si sono lasciati gli occhiali da vista?",
    "Come servire il miele dal vasetto senza creare fili appiccicosi sul tavolo?",
    "Come cantare sotto la doccia senza far abbaiare i cani del quartiere?",
]

PAROLE_OGGETTI = [
    "Tostapane", "Razzo", "Nonna", "Ventaglio", "Papera di gomma", "Microonde", "Supercolla", "Cactus",
    "Spaghetti", "Casco da astronauta", "Banana", "Poltrona", "Catena di bicicletta", "Dentiera", "Trombetta",
    "Sgabello", "Ananas", "Pattini a rotelle", "Frullatore", "Sturalavandini", "Scopa volante", "Ombrello",
    "Cucchiaio di legno", "Mattoncino LEGO", "Ciambella gonfiabile", "Occhiali da sole", "Ventilatore",
    "Macchina fotografica", "Calzino spaiato", "Palla da biliardo", "Sgombro in scatola", "Pennello", "Radiolina",
    "Carota", "Scatola di cartone", "Guanto da forno", "Elastico", "Ruota di scorta", "Tromba d'aria", "Sveglia a molla",
    "Saponetta", "Pellicola trasparente", "Cucitrice", "Mappamondo", "Sedia a dondolo", "Ventosa", "Pettine",
    "Bottiglia di ketchup", "Martello gommato", "Sveglia sparacaffè", "Cestino di vimini", "Sacchetto di trucioli",
    "Biliardino", "Lampadario di cristallo", "Prosciutto cotto", "Mandolino", "Scolapasta", "Forchetta gigante",
    "Fischietto", "Zaino da trekking", "Furfante di peluche", "Galleggiante da pesca", "Tappo di sughero", "Vaso da fiori",
    "Palla di cannone", "Mulinello", "Scatola di fiammiferi", "Grattugia", "Borraccia di metallo", "Guantoni da boxe",
    "Gomme da masticare", "Pinzetta per sopracciglia", "Cappello da mago", "Disco volante", "Molla colorata", "Lente d'ingrandimento",
    "Cricchetto", "Sassofono", "Waffel", "Cannuccia pieghevole", "Pistola ad acqua", "Carillon", "Pallone da sub",
    "Manubrio da palestra", "Molletta da bucato", "Monopattino elettrico", "Bandiera pirata", "Boccale di birra",
    "Slitta", "Cuscino per la cervicale", "Ventresca di tonno", "Tazza da tè", "Scatola di pennarelli", "Palla da bowling",
    "Grillo parlante", "Sciarpa di lana", "Bomba d'acqua", "Telescopio", "Portachiavi con torcia", "Zerbino",
    "Pannello solare tascabile", "Borraccia termica", "Rullo per pittura", "Serratura a combinazione", "Palla medica",
    "Caffettiera moka", "Ferro da stiro", "Campanaccio", "Ventosa per vetri", "Setacciatore", "Carrello della spesa",
    "Piumino per la polvere", "Pennello da barba", "Stivale in gomma", "Termometro digitale", "Spugna da bagno",
    "Frusta da cucina", "Imbuto di plastica", "Coltello da burro", "Barattolo di maionese", "Formaggio grattugiato",
    "Salsiccia piccante", "Bastone da passeggio", "Moschettone da arrampicata", "Faro da bicicletta", "Fermacarte d'ottone",
    "Cuscino antidecubito", "Mocio lavapavimenti", "Pinza da barbecue", "Sottobicchiere", "Pettine per gatti",
    "Coperta termica", "Vaporizzatore", "Tavola da surf", "Pinne da sub", "Maschera da cantiere", "Trapano avvitatore",
    "Livella a bolla", "Metro a nastro", "Spatola da muratore", "Galleggiante a fenicottero", "Palla da tennis",
    "Racchetta da badminton", "Volano", "Tappeto elastico tascabile", "Sacco a pelo", "Tenda da campeggio", "Bussola",
    "Lampada tascabile", "Barattolo di Nutella", "Biscotto al cioccolato", "Pacco di cracker", "Spremiagrumi",
    "Fornetto elettrico", "Bilancia da cucina", "Minipimer", "Bollitore", "Piastra per panini", "Tritacarne",
    "Tagliere in legno", "Cavatappi", "Apriscatole", "Pelapatate", "Schiaccianoci", "Stampo per cubetti di ghiaccio",
    "Guanto di feltro", "Scaldamanica", "Sciarpa a quadri", "Berretto con pompon", "Paraorecchie", "Impermeabile giallo",
    "Ombrellino da cocktail", "Cannuccia di vetro", "Stuzzicadenti", "Tovagliolo di stoffa", "Portafrutta",
    "Vassoio d'argento", "Zuccheriera", "Saliera", "Pepiera", "Ampolla d'olio", "Cestino del pane", "Biscottiera",
    "Teiera in ceramica", "Lattina di soda", "Bottiglietta di chinotto", "Ghiacciolo all'amarena", "Cono gelato",
    "Fetta di torta", "Croissant al pistacchio", "Brioche col tuppo", "Muffin al mirtillo", "Pancake", "Sciroppo d'acero",
    "Barattolo di miele", "Confettura di fragole", "Tavoletta di cioccolato", "Sacchetto di caramelle", "Marshmallow",
    "Pacco di patatine", "Busta di pop-corn", "Pistacchi tostati", "Mandorle salate", "Arancino al ragù",
    "Fetta di pizza", "Piadina romagnola", "Panino con porchetta", "Tramezzino", "Focaccia genovese", "Schiacciata toscana",
    "Tarallo pugliese", "Grissino torinese", "Biscotto della fortuna", "Torrone d'mandorle", "Cannolo siciliano",
    "Cassata", "Tiramisù", "Panna cotta", "Babà al rum", "Sfogliatella napoletana", "Gelato su stecco",
    "Chitarra acustica", "Ukulele", "Tamburello", "Maracas", "Xilofono", "Fisarmonica", "Trombone", "Violino",
    "Pianoforte a coda", "Batteria musicale", "Gong tibetano", "Campana di bronzo", "Diapason", "Metronomo",
    "Microfono vintage", "Cassa acustica bluetooth", "Cuffie da DJ", "Disco in vinile", "Cassetta VHS",
    "Walkman", "Game Boy", "Joystick", "Visore VR", "Puntatore laser", "Proiettore cinematografico", "Telescopio da balcone",
]

rooms = {}
room_subscribers = {}


def notify_room(room_code):
    if not room_code or room_code not in room_subscribers:
        return
    subscribers = room_subscribers[room_code]
    for queue in list(subscribers):
        try:
            queue.put_nowait("update")
        except Exception:
            pass


def generate_room_code():
    chars = "ABCDEFGHILMNOPQRSTUVZ"
    while True:
        code = "".join(random.choice(chars) for _ in range(4))
        if code not in rooms:
            return code


def join_player_logic(room_code, player_name, player_id=None):
    player_name = (player_name or "").strip()
    room_code = (room_code or "").strip().upper()
    if not player_name:
        raise ValueError("Nome giocatore mancante")
    if room_code and (len(room_code) > 6 or not room_code.isalpha()):
        raise ValueError("Codice stanza non valido")
    if not room_code:
        room_code = generate_room_code()
    if room_code not in rooms:
        rooms[room_code] = {
            "code": room_code,
            "players": [],
            "hostId": player_id,
            "status": "waiting",  # 'waiting', 'pitching', 'voting', 'round_result', 'ended'
            "roundNumber": 1,
            "totalRounds": 3,
            "firstSpeakerIndex": 0,
            "speakerOrder": [],
            "currentSpeakerIndex": 0,
            "pitchState": "preparing",  # 'preparing', 'pitching'
            "pitchStartTime": None,
            "pitchDuration": 45,
            "currentProblem": "",
            "currentWords": [],
            "votes": {},
            "lastRoundResult": None,
            "lastGameResult": None,
        }

    room = rooms[room_code]
    player_id = player_id or str(uuid.uuid4())[:8]

    for p in room["players"]:
        if p["id"] != player_id and p["name"].lower() == player_name.lower():
            raise ValueError("Nome già in uso in questa stanza")

    existing_player = next((p for p in room["players"] if p["id"] == player_id), None)
    if existing_player is None:
        existing_player = {
            "id": player_id,
            "name": player_name,
            "isHost": not room["players"],
            "score": 0,
            "confirmedNext": False,
        }
        room["players"].append(existing_player)
        if room["hostId"] is None:
            room["hostId"] = player_id
    else:
        existing_player["name"] = player_name

    return room, player_id, None


def start_game_logic(room_code, player_id):
    room = rooms.get(room_code)
    if not room:
        raise ValueError("Stanza non trovata")
    if room["hostId"] != player_id:
        raise ValueError("Solo l'host può avviare la partita")
    if len(room["players"]) < 3:
        raise ValueError("Servono almeno 3 giocatori per giocare")

    num_players = len(room["players"])
    room["status"] = "pitching"
    room["roundNumber"] = 1
    room["totalRounds"] = num_players
    room["firstSpeakerIndex"] = 0

    # Reset scores and confirmation flags
    for p in room["players"]:
        p["score"] = 0
        p["confirmedNext"] = False

    # Calculate initial speaker order
    room["speakerOrder"] = [p["id"] for p in room["players"]]
    room["currentSpeakerIndex"] = 0
    room["pitchState"] = "preparing"
    room["pitchStartTime"] = None
    room["votes"] = {}
    room["lastRoundResult"] = None
    room["lastGameResult"] = None

    # Pick random problem and 3 distinct random words
    room["currentProblem"] = random.choice(PROBLEMI)
    room["currentWords"] = random.sample(PAROLE_OGGETTI, 3)

    return room, None


def start_pitch_logic(room_code, player_id):
    room = rooms.get(room_code)
    if not room or room["status"] != "pitching":
        raise ValueError("Stanza non valida o non in fase di pitch")

    if not room["speakerOrder"] or room["currentSpeakerIndex"] >= len(room["speakerOrder"]):
        raise ValueError("Indice speaker non valido")

    current_speaker_id = room["speakerOrder"][room["currentSpeakerIndex"]]
    if player_id != current_speaker_id:
        raise ValueError("Non è il tuo turno di parlare!")

    room["pitchState"] = "pitching"
    room["pitchStartTime"] = time.time()
    return room


def next_speaker_logic(room_code, player_id):
    room = rooms.get(room_code)
    if not room or room["status"] != "pitching":
        raise ValueError("Stanza non valida o non in fase di pitch")

    if not room["speakerOrder"] or room["currentSpeakerIndex"] >= len(room["speakerOrder"]):
        raise ValueError("Indice speaker non valido")

    current_speaker_id = room["speakerOrder"][room["currentSpeakerIndex"]]
    if player_id != current_speaker_id:
        raise ValueError("Solo lo speaker corrente può passare il turno!")

    # Check if there are more speakers in this round
    if room["currentSpeakerIndex"] + 1 < len(room["speakerOrder"]):
        room["currentSpeakerIndex"] += 1
        room["pitchState"] = "preparing"
        room["pitchStartTime"] = None
    else:
        # All speakers finished pitching -> Move to secret voting / market phase
        room["status"] = "voting"
        room["votes"] = {}

    return room


def vote_logic(room_code, voter_id, target_id):
    room = rooms.get(room_code)
    if not room or room["status"] != "voting":
        return room

    all_player_ids = {p["id"] for p in room["players"]}
    if voter_id not in all_player_ids or target_id not in all_player_ids:
        return room

    if voter_id == target_id:
        raise ValueError("Non puoi votare per te stesso!")

    # Toggle vote or register vote
    if room["votes"].get(voter_id) == target_id:
        del room["votes"][voter_id]
    else:
        room["votes"][voter_id] = target_id

    # If all players have voted, resolve round votes!
    if len(room["votes"]) >= len(room["players"]):
        resolve_round_votes(room)

    return room


def resolve_round_votes(room):
    # Count votes received per player in this round
    vote_counts = {p["id"]: 0 for p in room["players"]}
    for voter_id, target_id in room["votes"].items():
        if target_id in vote_counts:
            vote_counts[target_id] += 1

    # Find highest votes in this round
    max_votes = max(vote_counts.values()) if vote_counts else 0
    winner_ids = [pid for pid, count in vote_counts.items() if count == max_votes and max_votes > 0]

    players_map = {p["id"]: p for p in room["players"]}
    winner_names = [players_map[pid]["name"] for pid in winner_ids if pid in players_map]

    player_details = {}
    for p in room["players"]:
        pid = p["id"]
        received = vote_counts.get(pid, 0)
        voted_for = room["votes"].get(pid)

        # Talent Scout bonus: +1 coin if voted for a round winner
        talent_bonus = 1 if (voted_for and voted_for in winner_ids) else 0
        total_round_coins = received + talent_bonus
        p["score"] += total_round_coins
        p["confirmedNext"] = False

        player_details[pid] = {
            "name": p["name"],
            "votesReceived": received,
            "talentBonus": talent_bonus,
            "votedForName": players_map[voted_for]["name"] if voted_for in players_map else "Nessuno",
            "totalRoundCoins": total_round_coins,
            "newTotalScore": p["score"],
        }

    room["lastRoundResult"] = {
        "roundNumber": room["roundNumber"],
        "roundWinnerIds": winner_ids,
        "roundWinnerNames": winner_names,
        "maxVotes": max_votes,
        "playerDetails": player_details,
    }
    room["status"] = "round_result"


def confirm_next_round_logic(room_code, player_id):
    room = rooms.get(room_code)
    if not room or room["status"] != "round_result":
        return room

    player = next((p for p in room["players"] if p["id"] == player_id), None)
    if player:
        player["confirmedNext"] = True

    # Check if ALL players have confirmed
    all_confirmed = all(p.get("confirmedNext", False) for p in room["players"])
    if all_confirmed:
        if room["roundNumber"] < room["totalRounds"]:
            # Advance to next round!
            room["roundNumber"] += 1
            num_players = len(room["players"])
            room["firstSpeakerIndex"] = (room["firstSpeakerIndex"] + 1) % num_players

            # Shift speaker order so next player starts
            idx = room["firstSpeakerIndex"]
            room["speakerOrder"] = [room["players"][(idx + i) % num_players]["id"] for i in range(num_players)]
            room["currentSpeakerIndex"] = 0
            room["pitchState"] = "preparing"
            room["pitchStartTime"] = None

            # Pick new problem & 3 words
            room["currentProblem"] = random.choice(PROBLEMI)
            room["currentWords"] = random.sample(PAROLE_OGGETTI, 3)
            room["votes"] = {}
            room["status"] = "pitching"
        else:
            # Game Over! Determine final standings
            sorted_players = sorted(room["players"], key=lambda p: p["score"], reverse=True)
            max_score = sorted_players[0]["score"] if sorted_players else 0
            top_winners = [p for p in sorted_players if p["score"] == max_score]

            room["lastGameResult"] = {
                "topWinners": top_winners,
                "winnerNames": ", ".join(w["name"] for w in top_winners),
                "isTie": len(top_winners) > 1,
                "standings": sorted_players,
            }
            room["status"] = "ended"

    return room


def reset_game_logic(room_code, player_id):
    room = rooms.get(room_code)
    if not room or room["hostId"] != player_id:
        raise ValueError("Stanza non trovata o solo l'host può riavviare")

    room["status"] = "waiting"
    room["roundNumber"] = 1
    room["firstSpeakerIndex"] = 0
    room["speakerOrder"] = []
    room["currentSpeakerIndex"] = 0
    room["pitchState"] = "preparing"
    room["pitchStartTime"] = None
    room["currentProblem"] = ""
    room["currentWords"] = []
    room["votes"] = {}
    room["lastRoundResult"] = None
    room["lastGameResult"] = None

    for p in room["players"]:
        p["score"] = 0
        p["confirmedNext"] = False

    return room


def leave_room_logic(room_code, player_id):
    room = rooms.get(room_code)
    if not room:
        raise ValueError("Stanza non trovata")

    player_tbd = next((p for p in room["players"] if p["id"] == player_id), None)
    if not player_tbd:
        raise ValueError("Giocatore non trovato")

    room["players"].remove(player_tbd)
    room["votes"].pop(player_id, None)

    room_closed = False
    if player_tbd["isHost"]:
        if len(room["players"]) >= 1:
            new_host = room["players"][0]
            new_host["isHost"] = True
            room["hostId"] = new_host["id"]
        else:
            room_closed = True
            rooms.pop(room_code, None)

    return {"room": room, "room_closed": room_closed}


CSS = """
* { box-sizing: border-box; }
body { margin: 0; min-height: 100vh; color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: linear-gradient(135deg, #0f172a, #1e1b4b, #172554); background-attachment: fixed; }
main { max-width: 680px; min-height: 100vh; margin: 0 auto; padding: 20px; display: grid; place-items: center; }
.card { width: 100%; padding: 28px; border: 1px solid rgba(245, 158, 11, 0.25); border-radius: 24px; background: rgba(15, 23, 42, 0.75); backdrop-filter: blur(16px); box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5); }
h1 { margin: 0 0 8px; text-align: center; font-size: 2.2rem; color: #f59e0b; text-shadow: 0 0 15px rgba(245,158,11,0.3); }
h2, h3, h4 { margin-top: 0; color: #fbbf24; }
.subtitle, .hint { color: rgba(241, 245, 249, 0.8); text-align: center; line-height: 1.5; font-size: 0.95rem; }
.icon { margin-bottom: 12px; font-size: 3.6rem; text-align: center; filter: drop-shadow(0 0 10px rgba(245,158,11,0.4)); }
label { display: block; margin: 18px 0 8px; color: #f1f5f9; font-weight: 600; font-size: 0.95rem; }
input { width: 100%; padding: 14px 16px; border: 2px solid rgba(245, 158, 11, 0.3); border-radius: 14px; color: #fff; background: rgba(30, 41, 59, 0.6); font-size: 1.05rem; outline: none; transition: border-color 0.2s; }
input:focus { border-color: #f59e0b; box-shadow: 0 0 12px rgba(245,158,11,0.3); }
button, .button { display: block; width: 100%; margin-top: 14px; padding: 16px; border: 0; border-radius: 14px; color: #fff; background: linear-gradient(135deg, #f59e0b, #d97706); cursor: pointer; font: inherit; font-weight: 700; font-size: 1.05rem; text-align: center; text-decoration: none; transition: transform 0.1s, filter 0.2s; box-shadow: 0 4px 15px rgba(217, 119, 6, 0.35); }
button:hover, .button:hover { filter: brightness(1.1); }
button:active, .button:active { transform: scale(0.98); }
.button.secondary, button.secondary { border: 2px solid rgba(255,255,255,.2); background: rgba(255,255,255,.08); box-shadow: none; }
.danger { background: linear-gradient(135deg, #ef4444, #dc2626); box-shadow: 0 4px 15px rgba(220, 38, 38, 0.3); }
.success { background: linear-gradient(135deg, #10b981, #059669); box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3); }
.room-code { margin: 16px 0; padding: 16px; border-radius: 18px; background: rgba(245, 158, 11, 0.15); border: 2px stroke #f59e0b; color: #fbbf24; font-size: 2.8rem; font-weight: 900; letter-spacing: 0.4rem; text-align: center; text-shadow: 0 0 12px rgba(251, 191, 36, 0.4); }
.player-list { display: grid; gap: 10px; margin: 16px 0; }
.player { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 12px 16px; border-radius: 14px; background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(255,255,255,0.08); }
.player-info { display: flex; align-items: center; gap: 12px; }
.avatar { display: grid; width: 42px; height: 42px; place-items: center; border-radius: 50%; background: linear-gradient(135deg, #f59e0b, #b45309); font-size: 1.2rem; color: #fff; font-weight: 800; }
.player-name { font-weight: 600; font-size: 1.05rem; }
.badge { color: #fbbf24; font-size: 0.85rem; font-weight: 700; padding: 4px 10px; border-radius: 8px; background: rgba(245, 158, 11, 0.2); border: 1px solid rgba(245, 158, 11, 0.3); }
.coin-badge { background: rgba(251, 191, 36, 0.2); border: 1px solid rgba(251, 191, 36, 0.4); color: #fbbf24; font-weight: 800; padding: 6px 12px; border-radius: 12px; font-size: 0.95rem; display: inline-flex; align-items: center; gap: 4px; }
.notice { margin: 0 0 18px; padding: 14px; border-radius: 12px; background: rgba(16, 185, 129, 0.2); border: 1px solid rgba(16, 185, 129, 0.4); color: #6ee7b7; text-align: center; }
.error { background: rgba(239, 68, 68, 0.2); border: 1px solid rgba(239, 68, 68, 0.4); color: #fca5a5; }

/* Problem & Words Cards */
.schema-card { margin: 18px 0; padding: 20px; border-radius: 18px; background: linear-gradient(135deg, rgba(245,158,11,0.15), rgba(217,119,6,0.08)); border: 2px solid rgba(245, 158, 11, 0.35); text-align: center; }
.problem-title { font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1.5px; color: #fbbf24; font-weight: 800; margin-bottom: 8px; }
.problem-box { font-size: 1.25rem; font-weight: 700; color: #ffffff; line-height: 1.4; margin-bottom: 16px; }
.words-container { display: flex; flex-wrap: wrap; justify-content: center; gap: 10px; margin-top: 12px; }
.word-badge { padding: 8px 16px; border-radius: 12px; background: linear-gradient(135deg, #3b82f6, #1d4ed8); color: #fff; font-weight: 800; font-size: 1rem; border: 1px solid rgba(255,255,255,0.2); box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3); }

/* Pitching View */
.speaker-turn-banner { padding: 16px; border-radius: 16px; text-align: center; background: rgba(245, 158, 11, 0.2); border: 2px solid #f59e0b; margin: 18px 0; font-size: 1.3rem; font-weight: 800; color: #fbbf24; }
.timer-display { font-size: clamp(3.5rem, 10vw, 5rem); font-weight: 900; color: #fbbf24; text-shadow: 0 0 20px rgba(251, 191, 36, 0.5); text-align: center; margin: 16px 0; letter-spacing: 2px; }

/* Voting Market */
.vote-form button { text-align: left; background: rgba(30, 41, 59, 0.7); font-weight: 600; border: 1px solid rgba(255,255,255,0.1); margin-top: 10px; }
.vote-form button.selected { border: 2px solid #f59e0b; background: rgba(245, 158, 11, 0.25); box-shadow: 0 0 15px rgba(245,158,11,0.4); }
.progress { height: 12px; overflow: hidden; border-radius: 10px; background: rgba(255,255,255,0.1); margin: 10px 0 16px; border: 1px solid rgba(255,255,255,0.1); }
.progress > span { display: block; height: 100%; background: linear-gradient(90deg, #f59e0b, #10b981); transition: width 0.4s ease-in-out; }

/* Winner Announcement */
.winner-banner { padding: 20px; border-radius: 20px; text-align: center; background: linear-gradient(135deg, rgba(245,158,11,0.3), rgba(16,185,129,0.2)); border: 3px solid #fbbf24; margin-bottom: 20px; box-shadow: 0 0 30px rgba(251,191,36,0.3); }
.winner-title { font-size: clamp(1.8rem, 6vw, 2.6rem); font-weight: 900; color: #fbbf24; text-shadow: 0 0 15px rgba(251,191,36,0.6); margin: 0; letter-spacing: 1px; }

/* Results Detail Table */
.result-card { margin: 12px 0; padding: 14px 18px; border-radius: 14px; background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255,255,255,0.1); display: flex; flex-direction: column; gap: 6px; }
"""


def e(value):
    return html.escape(str(value or ""), quote=True)


def redirect(path="/"):
    return RedirectResponse(path, status_code=303)


def set_flash(request, message, kind="notice"):
    request.session["flash"] = {"message": message, "kind": kind}


def pop_flash(request):
    return request.session.pop("flash", None)


def csrf_token(request):
    token = request.session.get("csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        request.session["csrf_token"] = token
    return token


def csrf_input(token):
    return f'<input type="hidden" name="csrf_token" value="{e(token)}">'


def check_csrf(request, submitted_token):
    expected_token = request.session.get("csrf_token", "")
    if not expected_token or not submitted_token or not secrets.compare_digest(expected_token, submitted_token):
        raise HTTPException(status_code=403, detail="Richiesta non valida")


def layout(title, content, in_room=False):
    sse_script = """
    <script>
    if (typeof EventSource !== 'undefined') {
      const es = new EventSource('/events');
      es.onmessage = function(e) {
        if (e.data === 'update') {
          window.location.reload();
        }
      };
    }
    </script>
    """ if in_room else ""

    return f"""<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{e(title)} · Inventori Pazzi</title><link rel="icon" type="image/svg+xml" href="/favicon.svg"><style>{CSS}</style></head><body><main>{content}</main>{sse_script}</body></html>"""


def flash_markup(flash):
    if not flash:
        return ""
    kind = "error" if flash.get("kind") == "error" else "notice"
    return f'<p class="notice {kind}">{e(flash.get("message"))}</p>'


def avatar_markup(name):
    initial = (name or "I")[0].upper()
    return f'<span class="avatar">{e(initial)}</span>'


def render_schema(problem, words):
    words_markup = "".join(f'<span class="word-badge">[ {e(w)} ]</span>' for w in words)
    return f"""
    <div class="schema-card">
      <div class="problem-title">💡 Problema del Round</div>
      <div class="problem-box">"{e(problem)}"</div>
      <div class="problem-title" style="margin-top:14px;">🧩 3 Parole Obbligatorie nell'Invenzione</div>
      <div class="words-container">{words_markup}</div>
    </div>"""


def render_home(request, flash):
    token = csrf_token(request)
    content = f"""
    <section class="card">
      <div class="icon">💡</div>
      <h1>Inventori Pazzi</h1>
      <p class="subtitle">Il party game multiplayer di invenzioni assurde e mercato spietato!</p>
      {flash_markup(flash)}
      <form action="/join" method="post">{csrf_input(token)}
        <label for="player_name">Il tuo Nome da Inventore</label>
        <input id="player_name" name="player_name" maxlength="20" required autofocus placeholder="es. Leonardo Da Vinci">
        
        <label for="room_code">Codice Stanza (lascia vuoto per creare una nuova)</label>
        <input id="room_code" name="room_code" maxlength="6" pattern="[A-Za-z]+" autocomplete="off" placeholder="es. ABCD">
        
        <button type="submit"> Entra nell'Officina</button>
      </form>
    </section>
    <script>
    (function() {{
      const nameInput = document.getElementById('player_name');
      const form = nameInput ? nameInput.closest('form') : null;
      if (!nameInput) return;

      const savedName = localStorage.getItem('inventore_pazzo_name');
      if (savedName) {{
        nameInput.value = savedName;
      }}

      if (form) {{
        form.addEventListener('submit', function() {{
          if (nameInput.value.trim()) {{
            localStorage.setItem('inventore_pazzo_name', nameInput.value.trim());
          }}
        }});
      }}
    }})();
    </script>"""
    return HTMLResponse(layout("Home", content, in_room=False))


def render_lobby(request, room, player, flash):
    token = csrf_token(request)
    player_count = len(room["players"])

    players_markup = []
    for p in room["players"]:
        host_badge = '<span class="badge">HOST</span>' if p["isHost"] else ""
        players_markup.append(
            f'<div class="player">'
            f'<div class="player-info">{avatar_markup(p["name"])}<span class="player-name">{e(p["name"])}</span></div>'
            f'{host_badge}</div>'
        )

    if player["id"] == room["hostId"]:
        if player_count >= 3:
            start_btn = f'<form action="/start" method="post">{csrf_input(token)}<button class="success" type="submit">🚀 Avvia Partita ({player_count} Inventori)</button></form>'
        else:
            start_btn = f'<button disabled style="opacity:0.5; cursor:not-allowed;">⏳ In attesa di almeno 3 giocatori ({player_count}/3)</button>'
    else:
        start_btn = '<p class="hint">In attesa che l\'host avvii la partita...</p>'

    content = f"""
    <section class="card">
      {flash_markup(flash)}
      <p class="subtitle">Codice Stanza dell'Officina</p>
      <div class="room-code">{e(room["code"])}</div>
      <p class="hint">Condividi questo codice con i tuoi amici. (Minimo 3 giocatori)</p>
      
      <h3>👥 Inventori in Stanza ({player_count})</h3>
      <div class="player-list">{"".join(players_markup)}</div>
      
      {start_btn}
      
      <form action="/leave" method="post">{csrf_input(token)}
        <button class="danger" type="submit">Lascia Stanza</button>
      </form>
    </section>"""
    return HTMLResponse(layout("Lobby Stanza", content, in_room=True))


def render_pitching(request, room, player, flash):
    token = csrf_token(request)

    current_speaker_id = room["speakerOrder"][room["currentSpeakerIndex"]]
    players_map = {p["id"]: p for p in room["players"]}
    current_speaker = players_map.get(current_speaker_id, {"name": "Sconosciuto"})

    is_my_turn = player["id"] == current_speaker_id
    pitch_state = room.get("pitchState", "preparing")
    pitch_start_time = room.get("pitchStartTime")
    duration = room.get("pitchDuration", 45)

    schema_html = render_schema(room["currentProblem"], room["currentWords"])

    # Action / Timer Block
    if is_my_turn:
        if pitch_state == "preparing":
            action_block = f"""
            <div class="speaker-turn-banner">🎤 È IL TUO TURNO DI PARLARE!</div>
            <p class="hint">Quando sei pronto a presentare la tua invenzione assurda, premi il pulsante per avviare i 45 secondi di timer!</p>
            <form action="/start-pitch" method="post">
              {csrf_input(token)}
              <button class="success" type="submit" style="font-size:1.25rem;">🚀 Inizia Turno (45s)</button>
            </form>"""
        else:
            action_block = f"""
            <div class="speaker-turn-banner">🎤 STAI PRESENTANDO LA TUA INVENZIONE!</div>
            <div id="timer-box" class="timer-display">45</div>
            <form action="/next-speaker" method="post">
              {csrf_input(token)}
              <button class="success" id="next-btn" type="submit" style="font-size:1.2rem;">▶️ Passa Turno al Prossimo Inventore</button>
            </form>"""
    else:
        if pitch_state == "preparing":
            action_block = f"""
            <div class="speaker-turn-banner" style="background:rgba(255,255,255,0.08); border-color:rgba(255,255,255,0.2); color:#e2e8f0;">
              ⏳ <strong>{e(current_speaker["name"].upper())}</strong> SI STA PREPARANDO...
            </div>
            <p class="hint">Attendi che l'inventore inizi la sua presentazione.</p>"""
        else:
            action_block = f"""
            <div class="speaker-turn-banner">🎤 <strong>{e(current_speaker["name"].upper())}</strong> STA PRESENTANDO!</div>
            <div id="timer-box" class="timer-display">45</div>
            <p class="hint">Ascolta la sua invenzione e preparati a giudicare nel mercato!</p>"""

    # Timer JavaScript snippet
    timer_script = ""
    if pitch_state == "pitching" and pitch_start_time:
        timer_script = f"""
        <script>
        (function() {{
          const startTime = {pitch_start_time};
          const duration = {duration};
          const timerBox = document.getElementById('timer-box');
          if (!timerBox) return;

          function updateTimer() {{
            const elapsed = Math.floor(Date.now() / 1000 - startTime);
            const remaining = Math.max(0, duration - elapsed);
            timerBox.textContent = remaining;
            if (remaining === 0) {{
              timerBox.style.color = '#ef4444';
              timerBox.style.textShadow = '0 0 20px rgba(239,68,68,0.7)';
            }}
          }}

          updateTimer();
          setInterval(updateTimer, 500);
        }})();
        </script>"""

    round_info_header = f"""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
      <span class="badge" style="font-size:0.95rem;">ROUND {room["roundNumber"]} / {room["totalRounds"]}</span>
      <span class="coin-badge">🪙 Salvadanaio: {player.get("score", 0)} Monete</span>
    </div>"""

    content = f"""
    <section class="card">
      {round_info_header}
      <h1>Lo Show degli Inventori</h1>
      {flash_markup(flash)}
      {schema_html}
      {action_block}
      <form action="/leave" method="post" style="margin-top:20px;">{csrf_input(token)}
        <button class="danger secondary" type="submit">Lascia Stanza</button>
      </form>
    </section>
    {timer_script}"""
    return HTMLResponse(layout("Pitch Invenzioni", content, in_room=True))


def render_voting(request, room, player, flash):
    token = csrf_token(request)
    voted_count = len(room["votes"])
    total_players = len(room["players"])
    pct = int((voted_count / total_players) * 100) if total_players > 0 else 0

    schema_html = render_schema(room["currentProblem"], room["currentWords"])

    # Voting Forms (Exclude self-vote)
    my_vote = room["votes"].get(player["id"])
    vote_forms = []
    for candidate in room["players"]:
        if candidate["id"] == player["id"]:
            continue
        is_selected = my_vote == candidate["id"]
        selected_class = " selected" if is_selected else ""
        selected_badge = '<span class="badge" style="background:#10b981; color:#fff;">Tuo Voto 🪙</span>' if is_selected else ""
        vote_forms.append(
            f'<form class="vote-form" action="/vote" method="post">{csrf_input(token)}'
            f'<input type="hidden" name="target_id" value="{e(candidate["id"])}">'
            f'<button class="{selected_class}" type="submit">'
            f'<div style="display:flex; justify-content:space-between; align-items:center;">'
            f'<span style="display:flex; align-items:center; gap:10px;">{avatar_markup(candidate["name"])} <strong>{e(candidate["name"])}</strong></span>'
            f'{selected_badge}'
            f'</div></button></form>'
        )

    content = f"""
    <section class="card">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
        <span class="badge" style="font-size:0.95rem;">FASE MERCATO - ROUND {room["roundNumber"]}</span>
        <span class="coin-badge">🪙 Salvadanaio: {player.get("score", 0)} Monete</span>
      </div>
      <h1>Votazione Mercato 🪙</h1>
      <p class="subtitle">Consegna la tua moneta all'invenzione migliore del round!</p>
      {flash_markup(flash)}
      {schema_html}
      
      <div style="margin: 18px 0;">
        <div style="display:flex; justify-content:space-between; font-size:0.9rem; font-weight:600; color:#fbbf24; margin-bottom:4px;">
          <span>Voti registrati nel mercato</span>
          <span>{voted_count} / {total_players} ({pct}%)</span>
        </div>
        <div class="progress"><span style="width:{pct}%"></span></div>
      </div>

      <div style="background:rgba(245,158,11,0.1); border:1px solid rgba(245,158,11,0.25); padding:14px; border-radius:14px; margin-bottom:16px;">
        ⭐ <strong>Bonus Talent Scout:</strong> Se voti l'inventore che vince il round, guadagni +1 moneta bonus nel tuo salvadanaio!
      </div>

      <h3>🗳️ Seleziona l'Invenzione Migliore</h3>
      <div>{"".join(vote_forms)}</div>

      <form action="/leave" method="post" style="margin-top:20px;">{csrf_input(token)}
        <button class="danger secondary" type="submit">Lascia Stanza</button>
      </form>
    </section>"""
    return HTMLResponse(layout("Mercato Votazione", content, in_room=True))


def render_round_result(request, room, player, flash):
    token = csrf_token(request)
    result = room.get("lastRoundResult", {})
    winner_names = result.get("roundWinnerNames", [])
    winner_str = ", ".join(winner_names) if winner_names else "Nessuno"

    player_details = result.get("playerDetails", {})
    my_details = player_details.get(player["id"], {})

    # Confirmation Status List
    players_status_markup = []
    ready_count = 0
    total_players = len(room["players"])

    for p in room["players"]:
        is_ready = p.get("confirmedNext", False)
        if is_ready:
            ready_count += 1
            badge = '<span class="badge" style="background:#10b981; color:#fff;">✅ PRONTO</span>'
        else:
            badge = '<span class="badge" style="background:rgba(255,255,255,0.15); color:#cbd5e1;">⏳ In Attesa</span>'

        details = player_details.get(p["id"], {})
        votes_rec = details.get("votesReceived", 0)
        t_bonus = details.get("talentBonus", 0)

        bonus_tag = ' <span style="color:#10b981; font-weight:bold;">(+1 ⭐ Talent Scout)</span>' if t_bonus > 0 else ""

        players_status_markup.append(
            f'<div class="result-card">'
            f'<div style="display:flex; justify-content:space-between; align-items:center;">'
            f'<span style="display:flex; align-items:center; gap:10px;">{avatar_markup(p["name"])} <strong>{e(p["name"])}</strong></span>'
            f'{badge}</div>'
            f'<div style="font-size:0.9rem; color:rgba(241,245,249,0.8); margin-top:4px;">'
            f'🪙 Incasso Mercato: <strong>+{votes_rec} Monete</strong>{bonus_tag} &bull; Totale: <strong>{p["score"]} Monete</strong>'
            f'</div>'
            f'</div>'
        )

    i_am_ready = player.get("confirmedNext", False)
    if i_am_ready:
        action_btn = """
        <div style="margin-top:20px; padding:16px; border-radius:14px; background:rgba(16,185,129,0.2); border:1px solid #10b981; color:#6ee7b7; text-align:center; font-weight:700;">
          ✅ Hai confermato! In attesa che tutti gli altri inventori proseguano...
        </div>"""
    else:
        next_label = "▶️ Prosegui al Prossimo Round" if room["roundNumber"] < room["totalRounds"] else "🏆 Vai alla Classifica Finale"
        action_btn = f"""
        <form action="/confirm-next" method="post" style="margin-top:20px;">
          {csrf_input(token)}
          <button class="success" type="submit" style="font-size:1.2rem;">{next_label}</button>
        </form>"""

    my_bonus_msg = ""
    if my_details.get("talentBonus", 0) > 0:
        my_bonus_msg = '<div class="notice" style="margin:14px 0;">⭐ <strong>Complimenti!</strong> Hai votato il vincitore e ottenuto +1 Moneta col Bonus Talent Scout!</div>'

    content = f"""
    <section class="card">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
        <span class="badge" style="font-size:0.95rem;">RISULTATI ROUND {room["roundNumber"]} / {room["totalRounds"]}</span>
        <span class="coin-badge">🪙 Tuo Salvadanaio: {player.get("score", 0)} Monete</span>
      </div>
      
      <h1>Esito del Mercato 🪙</h1>
      {flash_markup(flash)}
      
      <div style="background:rgba(245,158,11,0.15); border:2px stroke #f59e0b; padding:16px; border-radius:16px; text-align:center; margin:16px 0;">
        <div style="font-size:0.85rem; text-transform:uppercase; color:#fbbf24; font-weight:800;">👑 Vincitore Invenzione del Round</div>
        <div style="font-size:1.6rem; font-weight:900; color:#ffffff; margin-top:4px;">{e(winner_str)}</div>
      </div>

      {my_bonus_msg}

      <h3>📊 Resoconto Incassi ed Avanzamento ({ready_count}/{total_players} Pronti)</h3>
      <div>{"".join(players_status_markup)}</div>

      {action_btn}

      <form action="/leave" method="post" style="margin-top:16px;">{csrf_input(token)}
        <button class="danger secondary" type="submit">Lascia Stanza</button>
      </form>
    </section>"""
    return HTMLResponse(layout(f"Risultati Round {room['roundNumber']}", content, in_room=True))


def render_game_over(request, room, player, flash):
    token = csrf_token(request)
    game_res = room.get("lastGameResult", {})
    winner_names = game_res.get("winnerNames", "Nessuno")
    standings = game_res.get("standings", [])
    is_tie = game_res.get("isTie", False)

    banner_title = f"{e(winner_names.upper())} HA VINTO!" if not is_tie else f"VITTORIA A PARITÀ TRA {e(winner_names.upper())}!"

    standings_markup = []
    for rank, p in enumerate(standings, 1):
        medal = "🥇" if rank == 1 else ("🥈" if rank == 2 else ("🥉" if rank == 3 else f"#{rank}"))
        standings_markup.append(
            f'<div class="player" style="padding:14px 18px; margin-bottom:8px;">'
            f'<div class="player-info">'
            f'<span style="font-size:1.3rem; font-weight:800; min-width:32px;">{medal}</span>'
            f'{avatar_markup(p["name"])}'
            f'<span class="player-name">{e(p["name"])}</span>'
            f'</div>'
            f'<span class="coin-badge" style="font-size:1.05rem;">🪙 {p["score"]} Monete</span>'
            f'</div>'
        )

    host_actions = ""
    if player["id"] == room["hostId"]:
        host_actions = f"""
        <form action="/start" method="post">{csrf_input(token)}
          <button class="success" type="submit">🔄 Gioca un'Altra Partita</button>
        </form>
        <form action="/end-game" method="post">{csrf_input(token)}
          <button class="button secondary" type="submit">Torna alla Lobby</button>
        </form>"""

    content = f"""
    <section class="card">
      <div class="winner-banner">
        <div style="font-size:3rem; margin-bottom:8px;">🏆</div>
        <h1 class="winner-title">{banner_title}</h1>
      </div>
      
      {flash_markup(flash)}
      
      <h3>🏆 Classifica Finale Salvadanai</h3>
      <div class="player-list">{"".join(standings_markup)}</div>

      {host_actions}

      <form action="/leave" method="post" style="margin-top:16px;">{csrf_input(token)}
        <button class="danger secondary" type="submit">Lascia Stanza</button>
      </form>
    </section>"""
    return HTMLResponse(layout("Classifica Finale", content, in_room=True))


def session_room_and_player(request):
    room_code = request.session.get("room_code")
    player_id = request.session.get("player_id")
    room = rooms.get(room_code)
    if not room or not player_id:
        return None, None
    player = next((item for item in room["players"] if item["id"] == player_id), None)
    return room, player


def require_session_player(request):
    room, player = session_room_and_player(request)
    if not room or not player:
        raise ValueError("La tua sessione non è più associata a una stanza")
    return room, player


@fastapi_app.get("/favicon.svg", include_in_schema=False)
@fastapi_app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(content=FAVICON_SVG, media_type="image/svg+xml")


@fastapi_app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    flash = pop_flash(request)
    room, player = session_room_and_player(request)
    if not room or not player:
        request.session.pop("room_code", None)
        return render_home(request, flash)

    if room["status"] == "pitching":
        return render_pitching(request, room, player, flash)
    if room["status"] == "voting":
        return render_voting(request, room, player, flash)
    if room["status"] == "round_result":
        return render_round_result(request, room, player, flash)
    if room["status"] == "ended":
        return render_game_over(request, room, player, flash)

    return render_lobby(request, room, player, flash)


@fastapi_app.get("/events")
async def events_endpoint(request: Request):
    room_code = request.session.get("room_code")
    if not room_code or room_code not in rooms:
        return StreamingResponse(iter([]), media_type="text/event-stream")

    queue = asyncio.Queue()
    if room_code not in room_subscribers:
        room_subscribers[room_code] = set()
    room_subscribers[room_code].add(queue)

    async def event_generator():
        try:
            while True:
                try:
                    msg = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield f"data: {msg}\n\n"
                except asyncio.TimeoutError:
                    yield ": ping\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            if room_code in room_subscribers:
                room_subscribers[room_code].discard(queue)
                if not room_subscribers[room_code]:
                    del room_subscribers[room_code]

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@fastapi_app.post("/join")
async def join_room(
    request: Request,
    player_name: str = Form(""),
    room_code: str = Form(""),
    csrf_token_value: str = Form("", alias="csrf_token"),
):
    check_csrf(request, csrf_token_value)
    player_id = request.session.get("player_id") or str(uuid.uuid4())[:8]
    previous_room_code = request.session.get("room_code")
    desired_room_code = room_code.strip().upper()

    if previous_room_code and previous_room_code != desired_room_code and previous_room_code in rooms:
        try:
            leave_room_logic(previous_room_code, player_id)
            notify_room(previous_room_code)
        except ValueError:
            pass

    try:
        room, player_id, _ = join_player_logic(
            desired_room_code,
            player_name,
            player_id,
        )
        notify_room(room["code"])
    except ValueError as exc:
        set_flash(request, str(exc), "error")
        return redirect()

    request.session["player_id"] = player_id
    request.session["room_code"] = room["code"]
    return redirect()


@fastapi_app.post("/start")
async def start_game(request: Request, csrf_token_value: str = Form("", alias="csrf_token")):
    check_csrf(request, csrf_token_value)
    try:
        room, player = require_session_player(request)
        start_game_logic(room["code"], player["id"])
        notify_room(room["code"])
    except ValueError as exc:
        set_flash(request, str(exc), "error")
    return redirect()


@fastapi_app.post("/start-pitch")
async def start_pitch(request: Request, csrf_token_value: str = Form("", alias="csrf_token")):
    check_csrf(request, csrf_token_value)
    try:
        room, player = require_session_player(request)
        start_pitch_logic(room["code"], player["id"])
        notify_room(room["code"])
    except ValueError as exc:
        set_flash(request, str(exc), "error")
    return redirect()


@fastapi_app.post("/next-speaker")
async def next_speaker(request: Request, csrf_token_value: str = Form("", alias="csrf_token")):
    check_csrf(request, csrf_token_value)
    try:
        room, player = require_session_player(request)
        next_speaker_logic(room["code"], player["id"])
        notify_room(room["code"])
    except ValueError as exc:
        set_flash(request, str(exc), "error")
    return redirect()


@fastapi_app.post("/vote")
async def vote(
    request: Request,
    target_id: str = Form(""),
    csrf_token_value: str = Form("", alias="csrf_token"),
):
    check_csrf(request, csrf_token_value)
    try:
        room, player = require_session_player(request)
        vote_logic(room["code"], player["id"], target_id)
        notify_room(room["code"])
    except ValueError as exc:
        set_flash(request, str(exc), "error")
    return redirect()


@fastapi_app.post("/confirm-next")
async def confirm_next(request: Request, csrf_token_value: str = Form("", alias="csrf_token")):
    check_csrf(request, csrf_token_value)
    try:
        room, player = require_session_player(request)
        confirm_next_round_logic(room["code"], player["id"])
        notify_room(room["code"])
    except ValueError as exc:
        set_flash(request, str(exc), "error")
    return redirect()


@fastapi_app.post("/end-game")
async def end_game(request: Request, csrf_token_value: str = Form("", alias="csrf_token")):
    check_csrf(request, csrf_token_value)
    try:
        room, player = require_session_player(request)
        reset_game_logic(room["code"], player["id"])
        notify_room(room["code"])
    except ValueError as exc:
        set_flash(request, str(exc), "error")
    return redirect()


@fastapi_app.post("/leave")
async def leave_room(request: Request, csrf_token_value: str = Form("", alias="csrf_token")):
    check_csrf(request, csrf_token_value)
    current_room_code = request.session.get("room_code")
    try:
        room, player = require_session_player(request)
        leave_room_logic(room["code"], player["id"])
        notify_room(room["code"])
    except ValueError as exc:
        set_flash(request, str(exc), "error")
        if current_room_code:
            notify_room(current_room_code)
    request.session.pop("room_code", None)
    return redirect()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
