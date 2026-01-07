# Hardware - Blinky

Hardware plug-and-play per Blinky - zero saldature necessarie!

## 🛒 Bill of Materials (BOM)

| Componente | Quantità | Note | Link |
|------------|----------|------|------|
| Waveshare RP2040 One | 1 | Board USB dongle con LED integrato | [Link](https://www.waveshare.com/rp2040-one.htm) |

**Totale costo:** ~€8-10

## 📐 Specifiche Board

**Waveshare RP2040 One:**
- MCU: RP2040 dual-core Cortex M0+ @ 133MHz
- Flash: 2MB
- LED NeoPixel RGB: Integrato su GPIO 16
- Form factor: USB-A dongle (23mm x 18mm)
- Connettore: USB-A maschio integrato
- Alimentazione: 5V via USB

## 🔌 Setup

**Semplicissimo - plug and play!**

```
RP2040 One (USB Dongle)
    ┌────────┐
    │  LED   │ ← LED RGB integrato
    │ [RP2040]│
    └────┬───┘
         │
    [USB-A] ← Inserisci direttamente nel PC
```

**Zero collegamenti necessari:**
- ✅ LED già saldato sulla board
- ✅ USB integrato
- ✅ Nessun cavo esterno

## 🚀 Quick Start

1. **Flash firmware MicroPython** (vedi [firmware/README.md](../firmware/README.md))
2. **Inserisci nel PC** - la board è riconosciuta come porta seriale
3. **Avvia l'app** controller
4. **Done!** ✨

## 💡 Caratteristiche Hardware

- **Compatto**: Form factor USB dongle, non occupa spazio
- **Portatile**: Nessun cavo, inserisci e usa
- **LED visibile**: Posizionato in modo ottimale sulla board
- **Robusto**: PCB di qualità, componenti SMD

## ⚠️ Note d'Uso

- Il LED può essere luminoso in ambienti bui - la luminosità è configurabile nel firmware
- La board può scaldarsi leggermente durante l'uso (normale per RP2040)
- Evita di inserire/rimuovere ripetutamente - usa una prolunga USB se necessario
- Non servono driver su Windows 10/11, macOS, Linux

## 📷 Foto & Riferimenti

- [Waveshare Wiki](https://www.waveshare.com/wiki/RP2040-One)
- LED NeoPixel WS2812B integrato (formato GRB)
- Dimensioni perfette per stare inserito nel PC senza intralciare

---

**Status:** ✅ Hardware completo - plug and play!
