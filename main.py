import time
import machine
import neopixel
import sys
import select
import math

# 1 LED su GP16
pixels = neopixel.NeoPixel(machine.Pin(16), 1)

# Modalità
MODE_DEV = "DEV"
MODE_GAME = "GAME"
MODE_STUDY = "STUDY"
MODES = [MODE_DEV, MODE_GAME, MODE_STUDY]
# Stati
STATE_IDLE = "IDLE"
STATE_ACTIVE = "ACTIVE"
STATE_NOTIFY = "NOTIFY"
STATE_PAUSE = "PAUSE"

# Configurazione (salvabile in flash)
config = {
    "modes": {
        MODE_DEV: {
            "timer_minutes": 25,  # Pomodoro-style
            "colors": {
                STATE_IDLE: (0, 0, 0),        # spento
                STATE_ACTIVE: (100, 0, 0),    # verde (GRB)
                STATE_NOTIFY: (100, 255, 0),  # arancione (GRB)
                STATE_PAUSE: (0, 0, 50)       # blu scuro (GRB)
            }
        },
        MODE_GAME: {
            "timer_minutes": 45,
            "colors": {
                STATE_IDLE: (0, 0, 0),        # spento
                STATE_ACTIVE: (0, 100, 100),  # viola (GRB)
                STATE_NOTIFY: (0, 255, 0),    # rosso (GRB)
                STATE_PAUSE: (0, 0, 50)       # blu scuro (GRB)
            }
        },
        MODE_STUDY: {
            "timer_minutes": 45,
            "colors": {
                STATE_IDLE: (0, 100, 0),        # spento
                STATE_ACTIVE: (0, 100, 100),  # viola (GRB)
                STATE_NOTIFY: (0, 255, 0),    # rosso (GRB)
                STATE_PAUSE: (0, 0, 50)       # blu scuro (GRB)
            }
        }
    }
}

# Variabili globali
current_mode = MODE_DEV
current_state = STATE_IDLE
timer_start = 0
timer_duration = 0
fade_start = 0

def set_mode(mode):
    """Imposta la modalità (DEV/GAME) - solo da IDLE"""
    global current_mode
    
    # Può cambiare modalità solo da IDLE
    if current_state != STATE_IDLE:
        print(f"ERRORE: Cambiare modalità solo da stato IDLE (stato attuale: {current_state})")
        return False
    
    if mode in MODES:
        current_mode = mode
        print(f"Modalità: {current_mode}")
        update_led()
        return True
    else:
        print(f"Modalità non valida: {mode}")
        return False

def set_state(state):
    """Imposta lo stato del dispositivo con validazione FSM"""
    global current_state, timer_start, timer_duration
    
    if state not in [STATE_IDLE, STATE_ACTIVE, STATE_NOTIFY, STATE_PAUSE]:
        print(f"Stato non valido: {state}")
        return False
    
    # Validazione transizioni FSM
    valid_transitions = {
        STATE_IDLE: [STATE_ACTIVE],
        STATE_ACTIVE: [STATE_PAUSE, STATE_NOTIFY, STATE_IDLE],
        STATE_PAUSE: [STATE_ACTIVE, STATE_IDLE],
        STATE_NOTIFY: [STATE_PAUSE, STATE_IDLE]
    }
    
    if state not in valid_transitions[current_state]:
        print(f"ERRORE: Transizione non valida da {current_state} a {state}")
        print(f"Transizioni valide da {current_state}: {', '.join(valid_transitions[current_state])}")
        return False
    
    current_state = state
    print(f"Stato: {current_state}")
    
    # Avvia timer quando si passa ad ACTIVE
    if state == STATE_ACTIVE:
        timer_start = time.time()
        timer_duration = config["modes"][current_mode]["timer_minutes"] * 60
        print(f"Timer avviato: {config['modes'][current_mode]['timer_minutes']} minuti")
    
    # Reset timer quando si va in IDLE
    elif state == STATE_IDLE:
        timer_start = 0
        timer_duration = 0
    
    update_led()
    return True

def update_led():
    """Aggiorna il colore del LED in base a modalità e stato"""
    color = config["modes"][current_mode]["colors"][current_state]
    pixels[0] = color
    pixels.write()

def check_timer():
    """Controlla se il timer è scaduto"""
    global current_state
    if current_state == STATE_ACTIVE and timer_duration > 0:
        elapsed = time.time() - timer_start
        if elapsed >= timer_duration:
            print("Timer scaduto!")
            set_state(STATE_NOTIFY)
            return True
    return False

def blink_notify():
    """Lampeggio delicato con fade morbido in modalità NOTIFY"""
    global fade_start
    
    if current_state == STATE_NOTIFY:
        # Inizializza fade_start se necessario
        if fade_start == 0:
            fade_start = time.ticks_ms()
        
        # Ciclo di 2000ms per un fade completo (dentro-fuori)
        elapsed = time.ticks_diff(time.ticks_ms(), fade_start)
        cycle_position = (elapsed % 2000) / 2000.0  # 0.0 a 1.0
        
        # Usa una funzione sinusoidale per un fade naturale
        # sin va da -1 a 1, lo normalizziamo tra 0.3 e 1.0
        brightness = 0.3 + 0.7 * (math.sin(cycle_position * 2 * math.pi) * 0.5 + 0.5)
        
        base_color = config["modes"][current_mode]["colors"][STATE_NOTIFY]
        color = tuple(int(c * brightness) for c in base_color)
        
        pixels[0] = color
        pixels.write()
    else:
        # Reset fade_start quando non in NOTIFY
        fade_start = 0

def get_status():
    """Ritorna lo stato corrente del dispositivo"""
    status = {
        "mode": current_mode,
        "state": current_state,
        "timer_remaining": 0
    }
    
    if current_state == STATE_ACTIVE and timer_duration > 0:
        elapsed = time.time() - timer_start
        status["timer_remaining"] = int(timer_duration - elapsed)
    
    return status

def handle_serial_command():
    """Legge e gestisce comandi dalla seriale"""
    poll = select.poll()
    poll.register(sys.stdin, select.POLLIN)
    
    if poll.poll(0):  # Non bloccante
        try:
            line = sys.stdin.readline().strip()
            if not line:
                return
            
            parts = line.split()
            if len(parts) < 2:
                print(f"ERROR: Formato comando non valido")
                return
            
            command = parts[0].upper()
            arg = parts[1].upper()
            
            if command == "SET_MODE":
                if arg in MODES:
                    set_mode(arg)
                    print(f"OK: MODE={arg}")
                else:
                    print(f"ERROR: Modalità non valida '{arg}'")
            
            elif command == "SET_STATE":
                if arg in [STATE_IDLE, STATE_ACTIVE, STATE_NOTIFY, STATE_PAUSE]:
                    set_state(arg)
                    print(f"OK: STATE={arg}")
                else:
                    print(f"ERROR: Stato non valido '{arg}'")
            
            elif command == "GET_STATUS":
                status = get_status()
                # Formato: STATUS: mode,state,timer_remaining
                print(f"STATUS: {status['mode']},{status['state']},{status['timer_remaining']}")
            
            else:
                print(f"ERROR: Comando sconosciuto '{command}'")
        
        except Exception as e:
            print(f"ERROR: {e}")

# Inizializzazione
set_state(STATE_IDLE)

print("\n=== Timer Notifier Ready ===")
print("FSM: IDLE->ACTIVE, ACTIVE->PAUSE/NOTIFY/IDLE, PAUSE->ACTIVE/IDLE, NOTIFY->PAUSE/IDLE")
print(f"Modalità disponibili: {', '.join(MODES)}")
print("Comandi seriali: SET_MODE <mode>, SET_STATE <state>, GET_STATUS")
print(f"Modalità corrente: {current_mode}")
print(f"Stato corrente: {current_state}")

# Main loop
while True:
    handle_serial_command()
    check_timer()
    blink_notify()
    time.sleep(0.1)  # polling ogni 100ms