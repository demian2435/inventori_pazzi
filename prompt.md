Sei un software engineer esperto di Python, FastAPI e web application multiplayer real-time leggere e responsive.

Genera una web app completa in un singolo file Python (`app.py`) per un party game online intitolato:
**Inventori Pazzi**

Il codice deve ricalcare fedelmente l'architettura tecnica e i pattern di un template FastAPI/SSE esistente, basato su:
- Framework: `FastAPI` + `SessionMiddleware` (Starlette) + `asyncio.Queue` per Server-Sent Events (SSE).
- Interfaccia: Single-file render HTML con template string (nessuna cartella templates esterna), CSS moderno incorporato, mobile-first, zero framework JS esterni tranne la connessione SSE nativa (`EventSource('/events')`).
- Sicurezza & Sessioni: Protezione CSRF su tutti i form POST tramite token di sessione, persistenza del nome giocatore in `localStorage`.
- Stato del server in-memory: Dizionario globale `rooms` e `room_subscribers` con broadcast real-time via `notify_room(room_code)`.

---

### REGOLE E MECCANICA DI GIOCO

1. **Obiettivo:** Una volta che il giro sarà termianto e che tutti sono stati i "primi" venditori, si vede chi ha incassato piu soldi e sarà il vincitore.
2. **Setup Stanza:** Minimo 3 giocatori. L'host avvia la partita e tramite sistema di permutazione permette a tutti di essere primi, secondi, terzi etc così da eliminare il problema della posizione, ovviamente i round devono essere il numero di persone, 3 persone == 3 round.
3. **Flusso del Round:**
   - **Fase 1 - Generazione Scheda Comune:** A inizio round l'app seleziona casualmente da un ampio database statico:
     - 1 Problema buffo (es. *"Come evitare di fare i compiti durante le vacanze?"*, *"Come svegliarsi senza sveglia?"*, *"Come mangiare la pizza senza mani?"* - inserisci almeno 100 problemi divertenti e adatti a tutte le età).
     - 3 Parole/Oggetti bizzarri comuni per tutti (es. `[ Tostapane ]`, `[ Razzo ]`, `[ Nonna ]` - inserisci almeno 250 oggetti/parole casuali).
   - **Fase 2 - Pitch a Turno (Lo Show):** 
     - L'app mostra chiaramente il problema comune, le 3 parole obbligatorie e di chi è il turno di parola (es. *"🎤 È IL TURNO DI MARCO"*).
     - La persona selezionata quando è pronta preme "inizia turno" ed un timer di 45 secondi appare, appena termina gli compare il tasto passa turno, e passa al successivo, mentre gli altri vedono, "MARCO SI STA PREPARANDO" e quando inizia vedono il timer, ed una volta finito il turno passa al successivo seguendo la logica esposta prima.
     - **Rotazione automatica:** L'ordine di turno scala di 1 posizione ogni round per garantire equità su chi parla per primo e per ultimo.
   - **Fase 3 - Votazione Segreta e Meccanica Anti-Strategica (Fase Mercato):**
     - Quando tutti i giocatori hanno completato il loro pitch, si passa alla schermata di voto.
     - Ciascun giocatore ha a disposizione **1 moneta** da dare al concorrente che ha realizzato l'invenzione migliore/più divertente (non è ammesso l'autovoto).
     - La barra di progresso mostra quanti voti sono stati espressi in tempo reale.
     - **Bonus Talent Scout:** Chi vota l'inventore che vince il round ottiene +1 moneta bonus nel proprio salvadanaio segreto (incentivando tutti a votare la performance oggettivamente migliore e non un ripiego).
   - **Fase 4 - Schermata Suspense / Risultato Round:**
     - Viene svelato l'esito: quanti voti/monete ha preso ciascun giocatore nel round. separati tra monete ricevute e se hanno ricevuto il +1 del Bonus talent scout.
     - I punteggi cumulativi dei salvadanai vengono aggiornati (+1 moneta per ogni voto ricevuto).
     - Ogni giocatore deve premere il pulsante "▶️ Prosegui al prossimo round" (con status di conferma visibile in tempo reale per tutti).
   - **Fase 5 - Condizione di Fine Partita:**
     - Al termine dei turni mostra la classifica finale completa scrivendo in alto "MARCO HA VINTO!"

---

### STRUTTURA DEL CODICE RICHIESTA

1. **Favicon SVG dedicata:** Icona SVG a tema lampadina/ingranaggio/moneta d'oro integrata inline.
2. **Dataset:** Liste ricche e divertenti di `PROBLEMI` e `PAROLE_OGGETTI` in italiano.
3. **Logica di Stato:**
   - Gestione stanze (`rooms[code]`): `code`, `players`, `hostId`, `status` ('waiting', 'pitching', 'voting', 'ended'), `roundNumber`, `firstSpeakerIndex`, `currentSpeakerIndex`, `currentProblem`, `currentWords`, `votes`, `scores` (salvadanaio).
   - Funzioni logiche pure: `join_player_logic`, `start_game_logic`, `next_speaker_logic`, `vote_logic`, `resolve_round_votes`, `reset_game_logic`, `leave_room_logic`.
4. **Design UI (CSS Moderno):**
   - Palette brillante a tema "Officina degli Inventori / Gold" (toni ambra/giallo oro `#f59e0b`, viola/blu scuro `#0f172a`, card in glassmorphism, badge monete in evidenza `🪙`).
   - Visualizzazione chiara e leggibile su smartphone per il problema e le 3 parole (badge grandi e colorati).
   - Visualizzazione chiara del salvadanaio (es. `🪙 4 Monete`).
5. **Endpoint FastAPI:**
   - `GET /`
   - `GET /events` (SSE con gestione disconnessioni sicure)
   - `POST /join`
   - `POST /start`
   - `POST /next-speaker`
   - `POST /vote`
   - `POST /end-game`
   - `POST /leave`

Fornisci il codice Python completo pronto all'uso con comando di avvio `python app.py` tramite Uvicorn.

Trovi il Temaplate in allegato