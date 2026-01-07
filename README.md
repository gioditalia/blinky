# Blinky - LED Timer Notifier

Sistema di notifica silenziosa per la gestione del tempo durante attività prolungate (sviluppo, gaming, studio). Utilizza un LED RGB per fornire feedback visivo discreto e notifiche delicate quando è il momento di fare una pausa.

## 🎯 Caratteristiche

- ⏱️ **Timer configurabili** per diverse modalità (DEV, GAME)
- 🚦 **Macchina a stati robusta** (FSM) per transizioni valide
- 💡 **Fade morbido** per notifiche non invasive
- 📡 **Protocollo JSON** per comunicazione semplice ed efficiente
- 🔔 **Eventi proattivi** - nessun polling necessario
- 🎨 **Modalità estendibili** - facile aggiungere nuove configurazioni

## 📁 Struttura del Progetto

```
blinky/
├── firmware/          # MicroPython per RP2040
│   ├── main.py       # Codice principale del dispositivo
│   └── README.md     # Documentazione firmware e protocollo
│
├── app/              # Node.js controller (work in progress)
│   └── ...           # App per gestire il device
│
├── hardware/         # Meccanica e case
│   ├── case/         # File STL per stampa 3D
│   └── README.md     # BOM e istruzioni hardware
│
└── docs/             # Documentazione aggiuntiva
    └── ...
```

## 🚀 Quick Start

### 1. Setup Hardware
- Board: Waveshare RP2040 One
- LED: NeoPixel RGB (WS2812) su GPIO 16
- Vedi [hardware/README.md](hardware/README.md) per dettagli completi

### 2. Flash Firmware
```bash
cd firmware
mpremote connect COM7 fs cp main.py :
mpremote connect COM7 reset
```

Vedi [firmware/README.md](firmware/README.md) per istruzioni dettagliate.

### 3. Installa App Controller (Coming Soon)
```bash
cd app
npm install
npm start
```

## 🔌 Protocollo

Comunicazione seriale JSON a 115200 baud.

**Comandi:**
```json
{"action":"SET_MODE","mode":"DEV"}
{"action":"SET_STATE","state":"ACTIVE"}
{"action":"GET_STATUS"}
```

**Eventi:**
```json
{"event":"ready","mode":"DEV","state":"IDLE","modes":["DEV","GAME","STUDY"]}
{"event":"timer_expired","mode":"DEV"}
{"event":"state_changed","state":"NOTIFY","mode":"DEV"}
```

Documentazione completa: [firmware/README.md](firmware/README.md)

## 🛠️ Sviluppo

### Aggiungere una Nuova Modalità

Modifica `firmware/main.py`:

```python
MODE_CUSTOM = "CUSTOM"
MODES = [MODE_DEV, MODE_GAME, MODE_STUDY, MODE_CUSTOM]

config = {
    "modes": {
        # ... altre modalità ...
        MODE_CUSTOM: {
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

## 📊 Roadmap

- [x] Firmware base con FSM
- [x] Protocollo JSON
- [x] Eventi proattivi
- [ ] App Node.js controller
- [ ] Idle detection automatica
- [ ] Case stampabile 3D
- [ ] Configurazione dinamica via seriale
- [ ] Statistiche e logging

## 📖 Licenza

MIT License - Sentiti libero di usare e modificare!

## 🤝 Contributi

Pull request e suggerimenti sono benvenuti!

---

**Componenti del Progetto:**
- 🔧 [Firmware](firmware/) - MicroPython per RP2040
- 📱 [App](app/) - Controller Node.js
- 🏗️ [Hardware](hardware/) - Schemi e case 3D
- 📚 [Docs](docs/) - Documentazione extra
