# LED Timer Notifier

Dispositivo di notifica basato su RP2040 (Waveshare RP2040 One) con LED NeoPixel per gestire timer e pause durante attività prolungate.

## 🎯 Scopo del Progetto

Sistema di notifica silenziosa per gestire il tempo dedicato a diverse attività (sviluppo, gaming, studio). Il dispositivo utilizza un LED RGB per indicare lo stato corrente e notificare delicatamente quando è il momento di fare una pausa.

## 🔧 Hardware

- **Board**: Waveshare RP2040 One
- **LED**: 1x NeoPixel RGB (GRB format) su GPIO 16
- **Firmware**: MicroPython

## 📊 Modalità e Stati

### Modalità Disponibili

| Modalità | Timer | Colore Attivo | Colore Notifica |
|----------|-------|---------------|-----------------|
| **DEV** | 60 min | Verde | Arancione |
| **GAME** | 90 min | Viola | Rosso |

### Macchina a Stati (FSM)

```
IDLE ─────> ACTIVE
             │  │  │
             │  │  └──> IDLE
             │  └─────> PAUSE ─────> ACTIVE
             │                   └──> IDLE
             └────────> NOTIFY ──────> PAUSE
                                   └──> IDLE
```

**Transizioni valide:**
- `IDLE` → `ACTIVE` - Avvia il timer
- `ACTIVE` → `PAUSE` - Mette in pausa
- `ACTIVE` → `NOTIFY` - Notifica (automatica o manuale)
- `ACTIVE` → `IDLE` - Reset completo
- `PAUSE` → `ACTIVE` - Riprende l'attività
- `PAUSE` → `IDLE` - Reset da pausa
- `NOTIFY` → `PAUSE` - Pausa dopo notifica
- `NOTIFY` → `IDLE` - Reset da notifica

**Note:** Il cambio di modalità è permesso **solo** dallo stato `IDLE`.

## 🔌 Protocollo Seriale

Comunicazione via USB/UART a 115200 baud.

### Comandi

| Comando | Parametro | Descrizione | Esempio |
|---------|-----------|-------------|---------|
| `SET_MODE` | DEV\|GAME\|STUDY | Imposta modalità (solo da IDLE) | `SET_MODE DEV` |
| `SET_STATE` | IDLE\|ACTIVE\|NOTIFY\|PAUSE | Cambia stato (rispetta FSM) | `SET_STATE ACTIVE` |
| `GET_STATUS` | - | Ottiene stato corrente | `GET_STATUS` |

### Risposte

```
OK: MODE=DEV              # Modalità impostata con successo
OK: STATE=ACTIVE          # Stato cambiato con successo
STATUS: DEV,ACTIVE,1500   # mode,state,timer_remaining (secondi)
ERROR: <messaggio>        # Errore con descrizione
```

## 🚀 Installazione

### 1. Installare MicroPython
Flash MicroPython sulla board RP2040:
```bash
# Scarica il firmware da https://micropython.org/download/RPI_PICO/
# Entra in bootloader mode (tieni premuto BOOT mentre colleghi USB)
# Copia il file .uf2 sulla board
```

### 2. Installare mpremote
```bash
pip install mpremote
```

### 3. Caricare il codice
```bash
cd hello
mpremote connect COM7 fs cp main.py :
mpremote connect COM7 reset
```

## 💡 Funzionamento LED

### Stati Base
- **IDLE**: LED spento
- **ACTIVE**: Colore fisso (dipende dalla modalità)
- **PAUSE**: Blu scuro
- **NOTIFY**: Fade morbido (effetto "respiro")

### Effetto Notifica
Quando il timer scade o si entra in `NOTIFY`:
- Fade sinusoidale con ciclo di 2 secondi
- Luminosità varia dal 30% al 100%
- Transizione molto dolce e non invasiva

## 📝 Utilizzo con App Esterna

Il dispositivo è progettato per essere controllato da un'applicazione esterna (Node.js, Python, ecc.) che:
1. Monitora l'attività dell'utente
2. Imposta la modalità appropriata
3. Avvia/ferma il timer via comandi seriali
4. Gestisce la logica di idle detection per reset automatici

### Esempio Node.js
```javascript
const { SerialPort } = require('serialport');
const { ReadlineParser } = require('@serialport/parser-readline');

const port = new SerialPort({ path: 'COM7', baudRate: 115200 });
const parser = port.pipe(new ReadlineParser({ delimiter: '\n' }));

// Avvia sessione di sviluppo
port.write('SET_MODE DEV\n');
port.write('SET_STATE ACTIVE\n');

// Leggi risposte
parser.on('data', (line) => {
  console.log('Device:', line);
});
```

## 🛠️ Personalizzazione

### Aggiungere una Nuova Modalità

Modifica la sezione configurazione in `main.py`:

```python
# Aggiungi la modalità alla lista
MODE_READING = "READING"
MODES = [MODE_DEV, MODE_GAME, MODE_READING]

# Aggiungi la configurazione
config = {
    "modes": {
        # ... altre modalità ...
        MODE_READING: {
            "timer_minutes": 30,
            "colors": {
                STATE_IDLE: (0, 0, 0),       
                STATE_ACTIVE: (50, 0, 50),   # Rosa (GRB)
                STATE_NOTIFY: (100, 150, 0), # Giallo (GRB)
                STATE_PAUSE: (0, 0, 50)      
            }
        }
    }
}
```

**Nota:** I colori sono in formato GRB (Green, Red, Blue) per compatibilità con NeoPixel WS2812.

## 📖 Licenza

MIT License - Sentiti libero di usare e modificare per i tuoi progetti!

## 🤝 Contribuire

Suggerimenti e pull request sono benvenuti! 

## 📧 Autore

Created for personal productivity management.
