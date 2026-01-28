import time
import machine
import neopixel
import sys
import select
import math
import json

# 1 LED su GP16
pixels = neopixel.NeoPixel(machine.Pin(16), 1)

# Modalità
MODE_DEV = "DEV"
MODE_GAME = "GAME"
MODES = [MODE_DEV, MODE_GAME]
# Stati
STATE_IDLE = "IDLE"
STATE_ACTIVE = "ACTIVE"
STATE_NOTIFY = "NOTIFY"
STATE_PAUSE = "PAUSE"

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
        }
    }
}

# Variabili globali
current_mode = MODE_DEV
current_state = STATE_IDLE
timer_start = 0
timer_duration = 0
fade_start = 0
elapsed_before_pause = 0

def set_mode(mode):
    """Imposta la modalità (DEV/GAME) - solo da IDLE"""
    global current_mode
    
    # Può cambiare modalità solo da IDLE
    if current_state != STATE_IDLE:
        return False
    
    if mode in MODES:
        current_mode = mode
        update_led()
        return True
    else:
        return False

def set_state(state):
    """Imposta lo stato del dispositivo con validazione FSM"""
    global current_state, timer_start, timer_duration, elapsed_before_pause
    
    if state not in [STATE_IDLE, STATE_ACTIVE, STATE_NOTIFY, STATE_PAUSE]:
        return False
    
    # Validazione transizioni FSM
    valid_transitions = {
        STATE_IDLE: [STATE_ACTIVE],
        STATE_ACTIVE: [STATE_PAUSE, STATE_NOTIFY, STATE_IDLE],
        STATE_PAUSE: [STATE_ACTIVE, STATE_IDLE],
        STATE_NOTIFY: [ STATE_IDLE]
    }
    
    if state not in valid_transitions[current_state]:
        return False
    
    current_state = state
    
    # Avvia timer quando si passa ad ACTIVE
    if state == STATE_ACTIVE:
        if elapsed_before_pause > 0:
            # Riprende da pausa
            timer_start = time.time() - elapsed_before_pause
            elapsed_before_pause = 0
        else:
            timer_start = time.time()
            timer_duration = config["modes"][current_mode]["timer_minutes"] * 60

    elif state == STATE_PAUSE:
        # Salva progresso
        if timer_start > 0 and timer_duration > 0:
            elapsed_before_pause = time.time() - timer_start

    # Reset timer quando si va in IDLE
    elif state == STATE_IDLE:
        timer_start = 0
        timer_duration = 0
        elapsed_before_pause = 0
    
    update_led()
    
    # Notifica evento cambio stato all'app
    event = {"event": "state_changed", "state": current_state, "mode": current_mode}
    print(json.dumps(event))
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
            set_state(STATE_NOTIFY)
            # Notifica evento all'app
            event = {"event": "timer_expired", "mode": current_mode}
            print(json.dumps(event))
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
    elif current_state == STATE_PAUSE and elapsed_before_pause > 0:
        status["timer_remaining"] = int(timer_duration - elapsed_before_pause)
        
    return status

def handle_serial_command():
    """Legge e gestisce comandi dalla seriale in formato JSON"""
    poll = select.poll()
    poll.register(sys.stdin, select.POLLIN)
    
    if poll.poll(0):  # Non bloccante
        try:
            line = sys.stdin.readline().strip()
            if not line:
                return
            
            # Parse JSON command
            cmd = json.loads(line)
            action = cmd.get("action", "").upper()
            
            if action == "SET_MODE":
                mode = cmd.get("mode", "").upper()
                if mode in MODES:
                    success = set_mode(mode)
                    response = {"status": "ok" if success else "error", "action": "set_mode", "mode": mode}
                else:
                    response = {"status": "error", "action": "set_mode", "message": f"Invalid mode: {mode}"}
                print(json.dumps(response))
            
            elif action == "SET_STATE":
                state = cmd.get("state", "").upper()
                if state in [STATE_IDLE, STATE_ACTIVE, STATE_NOTIFY, STATE_PAUSE]:
                    success = set_state(state)
                    if not success:
                        response = {"status": "error", "action": "set_state", "message": "Invalid transition"}
                    else:
                        response = {"status": "ok", "action": "set_state", "state": state}
                else:
                    response = {"status": "error", "action": "set_state", "message": f"Invalid state: {state}"}
                print(json.dumps(response))
            
            elif action == "GET_STATUS":
                status = get_status()
                response = {"status": "ok", "action": "get_status", "data": status}
                print(json.dumps(response))
            
            else:
                response = {"status": "error", "message": f"Unknown action: {action}"}
                print(json.dumps(response))
        
        except json.JSONDecodeError as e:
            response = {"status": "error", "message": f"Invalid JSON: {str(e)}"}
            print(json.dumps(response))
        except Exception as e:
            response = {"status": "error", "message": str(e)}
            print(json.dumps(response))

# Inizializzazione
set_state(STATE_IDLE)

print(json.dumps({"event": "ready", "mode": current_mode, "state": current_state, "modes": MODES}))

# Main loop
while True:
    handle_serial_command()
    check_timer()
    blink_notify()
    time.sleep(0.1)  # polling ogni 100ms