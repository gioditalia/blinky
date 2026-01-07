# Blinky App - Node.js Controller (TypeScript)

Controller app per gestire il dispositivo Blinky via seriale.

## 🎯 Funzionalità (Planned)

- ⏱️ Gestione automatica timer basata su modalità
- 🖥️ Idle detection per auto-reset
- 🔔 Notifiche desktop quando il timer scade
- 📊 Statistiche sessioni di lavoro/gioco
- 🎮 Integrazione con rilevamento processi (IDE, giochi)
- ⚙️ Configurazione tramite file JSON

## 🚀 Installazione

```bash
npm install
npm run build
```

## 📝 Utilizzo

```bash
npm start
```

## 🔧 Configurazione

```json
{
  "serialPort": "COM7",
  "idleTimeout": 300,
  "modes": {
    "dev": {
      "processNames": ["Code.exe"]
    },
    "game": {
      "processNames": ["steam.exe"]
    }
  }
}
```

## 📖 API

### BlinkyDevice Class

```typescript
import { BlinkyDevice } from './src/blinky';

const device = new BlinkyDevice('COM7');

device.on('ready', (data) => {
  console.log('Device ready:', data);
});

device.on('timer_expired', (data) => {
  console.log('Timer expired!', data);
  // Invia notifica
});

await device.setMode('DEV');
await device.setState('ACTIVE');

const status = await device.getStatus();
```

## 🛠️ Sviluppo

```bash
npm run dev     # Dev mode con auto-reload
npm test        # Run tests
npm run build   # Compile TypeScript
npm run lint    # Check code style
```

## 📦 Stack

- **TypeScript** - Type safety e developer experience
- **SerialPort** - Comunicazione seriale
- **Node.js** - Runtime

---

*Work in progress - Coming soon!*
