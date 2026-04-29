# RPG Python — Gioco di ruolo a turni

Videogioco RPG testuale sviluppato in Python per il corso ITS Olivetti,
Modulo Python — A.A. 2025/2026.

## Come giocare

```bash
python project_work_finale.py
```

Nessuna libreria esterna richiesta. Basta Python 3.

## Meccaniche di gioco

Il giocatore controlla un **Mago** e affronta in sequenza tre nemici:
Goblin → Orco → Troll.

### Comandi disponibili

| Comando | Costo | Effetto |
|---|---|---|
| `attacco` | 2 energia | Attacco normale (10% di fallimento) |
| `forte` | 4 energia | Attacco forte (25% di fallimento) |
| `difesa` | — | Aggiunge 6 scudo per il turno |
| `riposo` | — | Recupera 5 energia e 3 mana |
| `cura` | 1 pozione | Recupera 8 salute |
| `palla di fuoco` | 5 mana | 6 danni magici |
| `fulmine` | 8 mana | 10 danni magici |
| `veleno` | 4 mana | 5 danni da veleno al turno successivo |