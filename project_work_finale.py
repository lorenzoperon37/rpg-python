import random

# ----------------------------
# FUNZIONI UTILI
# ----------------------------

def limita_valore(val, minimo, massimo):
    return max(minimo, min(val, massimo))

def applica_danno(salute, scudo, danno):
    if scudo > 0:
        if danno <= scudo:
            scudo -= danno
            danno = 0
        else:
            danno -= scudo
            scudo = 0

    salute -= danno
    if salute < 0:
        salute = 0
    return salute, scudo

def stampa_stato(player, enemy):
    print("\n--- NUOVO TURNO ---")
    print("Giocatore -> Salute:", player["salute"], "/", player["saluteMax"],
          "| Scudo:", player["scudo"],
          "| Energia:", player["energia"], "/", player["energiaMax"],
          "| Mana:", player["mana"], "/", player["manaMax"])
    print(enemy["nome"], "-> Salute:", enemy["salute"], "/", enemy["saluteMax"],
          "| Scudo:", enemy["scudo"],
          "| Veleno:", enemy["veleno"])
    print("Inventario -> Pozioni:", player["inventario"]["pozioni"],
          "| Oro:", player["inventario"]["oro"])

def logga(storico, turno, testo):
    storico.append("Turno " + str(turno) + ". " + testo)

# ----------------------------
# AZIONI GIOCATORE
# ----------------------------

def riposo_giocatore(player):
    prima_energia = player["energia"]
    prima_mana = player["mana"]

    player["energia"] = limita_valore(
        player["energia"] + player["recuperoRiposo"],
        0,
        player["energiaMax"]
    )

    player["mana"] = limita_valore(
        player["mana"] + 3,
        0,
        player["manaMax"]
    )

    return "Il giocatore usa RIPOSO (energia " + str(prima_energia) + \
           " -> " + str(player["energia"]) + \
           ", mana " + str(prima_mana) + \
           " -> " + str(player["mana"]) + ")"

def difesa_giocatore(player):
    prima = player["scudo"]
    player["scudo"] += player["difesa"]["valoreScudo"]
    return "Il giocatore usa DIFESA (scudo " + str(prima) + " -> " + str(player["scudo"]) + ")"

def cura_giocatore(player):
    inv = player["inventario"]
    if inv["pozioni"] <= 0:
        return None, "Il giocatore prova CURA ma non ha pozioni"

    inv["pozioni"] -= 1
    prima = player["salute"]
    player["salute"] = limita_valore(player["salute"] + inv["recuperoSalutePozione"], 0, player["saluteMax"])
    return "ok", "Il giocatore usa CURA (salute " + str(prima) + " -> " + str(player["salute"]) + ")"

def magia_giocatore(player, enemy, nome_magia):
    magia = player["magie"][nome_magia]
    costo = magia["costo"]

    if player["mana"] < costo:
        return None, "Mana insufficiente per " + nome_magia.upper()

    player["mana"] -= costo

    if nome_magia == "veleno":
        enemy["veleno"] = magia["danno"]
        return "ok", "Il giocatore lancia VELENO (il nemico subira' " + str(magia["danno"]) + " danni per turno)"

    danno = magia["danno"]
    enemy["salute"], enemy["scudo"] = applica_danno(enemy["salute"], enemy["scudo"], danno)
    return "ok", "Il giocatore lancia " + nome_magia.upper() + " e infligge " + str(danno) + " danni"

def attacco_giocatore(player, enemy, tipo):
    if tipo == "attacco":
        costo = player["costoAttacco"]
        danno_base = player["dannoAttaccoNormale"]
        soglia_fallimento = player["fallimentoNormale"]
    else:
        costo = player["costoAttaccoForte"]
        danno_base = player["dannoAttaccoForte"]
        soglia_fallimento = player["fallimentoForte"]

    if player["energia"] < costo:
        return None, "Energia insufficiente (hai " + str(player["energia"]) + ", serve " + str(costo) + ")"

    player["energia"] -= costo
    tiro = random.randint(1, 100)

    if tiro <= soglia_fallimento:
        return "ok", "Il giocatore manca il bersaglio"

    danno = danno_base

    if tiro >= player["sogliaCritico"]:
        danno *= 2
        enemy["salute"], enemy["scudo"] = applica_danno(enemy["salute"], enemy["scudo"], danno)
        return "ok", "COLPO CRITICO! Danni: " + str(danno)

    enemy["salute"], enemy["scudo"] = applica_danno(enemy["salute"], enemy["scudo"], danno)
    return "ok", "Attacco riuscito. Danni: " + str(danno)

# ----------------------------
# TURNO GIOCATORE
# ----------------------------

def turno_giocatore(player, enemy, comandi_validi):
    azione = input("Comando -> ").lower().strip()

    if azione not in comandi_validi:
        return None, "Comando non valido. Comandi disponibili: " + ", ".join(comandi_validi)

    if azione == "riposo":
        return "ok", riposo_giocatore(player)

    if azione == "difesa":
        return "ok", difesa_giocatore(player)

    if azione == "cura":
        return cura_giocatore(player)

    if azione in player["magie"]:
        return magia_giocatore(player, enemy, azione)

    if azione == "attacco" or azione == "forte":
        return attacco_giocatore(player, enemy, azione)

    return None, "Azione non gestita"

# ----------------------------
# TURNO NEMICO
# ----------------------------

def turno_nemico(player, enemy):
    scelta = random.randint(1, 100)

    if scelta <= 70:
        danno = enemy["forzaAttacco"]
        player["salute"], player["scudo"] = applica_danno(player["salute"], player["scudo"], danno)
        testo = enemy["nome"] + " attacca e infligge " + str(danno) + " danni"
    else:
        prima = enemy["salute"]
        enemy["salute"] = limita_valore(enemy["salute"] + enemy["cura"], 0, enemy["saluteMax"])
        testo = enemy["nome"] + " si cura (salute " + str(prima) + " -> " + str(enemy["salute"]) + ")"

    # FIX: il veleno viene applicato e poi azzerato ogni turno
    if enemy["veleno"] > 0 and enemy["salute"] > 0:
        danno_veleno = enemy["veleno"]
        enemy["salute"], enemy["scudo"] = applica_danno(enemy["salute"], enemy["scudo"], danno_veleno)
        enemy["veleno"] = 0  # FIX: il veleno dura solo un turno

        if enemy["salute"] == 0:
            testo += " | Poi subisce " + str(danno_veleno) + " da veleno e muore"
        else:
            testo += " | Poi subisce " + str(danno_veleno) + " da veleno"

    return testo

# ----------------------------
# TURNO SINGOLO
# ----------------------------

def turno_singolo(player, enemy, comandi_validi, storico, turno_globale):
    stampa_stato(player, enemy)

    # FIX: usiamo None come segnale di azione non valida, non una stringa
    esito, testo_g = turno_giocatore(player, enemy, comandi_validi)
    print(testo_g)

    if esito is None:
        return False  # turno non consumato

    logga(storico, turno_globale, testo_g)

    if enemy["salute"] == 0:
        return True

    testo_n = turno_nemico(player, enemy)
    print(testo_n)
    logga(storico, turno_globale, testo_n)

    return True

# ----------------------------
# DATI GIOCATORE
# ----------------------------

giocatore = {
    "nome": "Mago",
    "saluteMax": 30,
    "salute": 30,
    "scudo": 0,
    "energiaMax": 10,
    "energia": 10,
    "recuperoRiposo": 5,
    "costoAttacco": 2,
    "costoAttaccoForte": 4,
    "manaMax": 15,
    "mana": 15,
    "dannoAttaccoNormale": 4,
    "dannoAttaccoForte": 7,
    "fallimentoNormale": 10,
    "fallimentoForte": 25,
    "sogliaCritico": 90,
    "magie": {
        "palla di fuoco": {"costo": 5, "danno": 6},
        "fulmine": {"costo": 8, "danno": 10},
        "veleno": {"costo": 4, "danno": 5}
    },
    "difesa": {"valoreScudo": 6},
    "inventario": {
        "pozioni": 3,
        "recuperoSalutePozione": 8,
        "oro": 0
    }
}

# ----------------------------
# NEMICI
# ----------------------------

nemici = [
    {"nome": "Goblin", "saluteMax": 20, "salute": 20, "scudo": 0, "forzaAttacco": 5, "cura": 3, "veleno": 0},
    {"nome": "Orco",   "saluteMax": 28, "salute": 28, "scudo": 0, "forzaAttacco": 7, "cura": 2, "veleno": 0},
    {"nome": "Troll",  "saluteMax": 35, "salute": 35, "scudo": 0, "forzaAttacco": 8, "cura": 4, "veleno": 0}
]

# FIX: "attacco forte" con spazio diventa "forte" (piu' semplice da digitare)
COMANDI = {
    "attacco":        {},
    "forte":          {},  # era "attacco forte"
    "difesa":         {},
    "riposo":         {},
    "cura":           {},
    "palla di fuoco": {},
    "fulmine":        {},
    "veleno":         {}
}

# ----------------------------
# PARTITA
# ----------------------------

storico_mosse = []
turnoGlobale = 0

print("Inizia l'avventura!")
print("Comandi disponibili:", ", ".join(COMANDI.keys()))

for nemico in nemici:
    # Reset nemico
    nemico["salute"] = nemico["saluteMax"]
    nemico["scudo"] = 0
    nemico["veleno"] = 0

    # FIX: reset scudo giocatore tra uno scontro e l'altro
    giocatore["scudo"] = 0

    print("\nHai davanti a te un", nemico["nome"])

    while giocatore["salute"] > 0 and nemico["salute"] > 0:
        turnoGlobale += 1

        turno_consumato = turno_singolo(
            giocatore, nemico, COMANDI, storico_mosse, turnoGlobale
        )

        if not turno_consumato:
            turnoGlobale -= 1

    if giocatore["salute"] == 0:
        print("\nHai perso!")
        break
    else:
        giocatore["inventario"]["oro"] += 1
        print("Hai sconfitto", nemico["nome"], "! Oro totale:",
              giocatore["inventario"]["oro"])
else:
    print("\nHai sconfitto tutti i nemici!")

print("\n--- STORICO MOSSE ---")
for riga in storico_mosse:
    print(riga)