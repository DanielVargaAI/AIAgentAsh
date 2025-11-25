import requests
import json
from websocket import create_connection


def get_save_string():
    # Liste aller offenen Chrome-Debug-Sessions holen
    sessions = requests.get("http://localhost:9222/json").json()

    if not sessions:
        raise Exception("Keine Chrome Sessions gefunden. Läuft Chrome mit --remote-debugging-port=9222 ?")

    # Nimm die erste gefundene Seite
    ws_url = sessions[0]["webSocketDebuggerUrl"]

    # WebSocket-Verbindung zum Debugger
    ws = create_connection(ws_url)

    # JavaScript im Browser ausführen
    command = {
        "id": 1,
        "method": "Runtime.evaluate",
        "params": {
            "expression": "localStorage.sessionData_Ripstop"
        }
    }

    ws.send(json.dumps(command))

    result = json.loads(ws.recv())
    ws.close()

    # Der eigentliche Wert
    value = result["result"]["result"].get("value", None)
    return value


if __name__ == "__main__":
    save = get_save_string()
    print("Save data:", save)

    # open cmd, cd into app directory and run:
    # PokeRogue.exe --remote-debugging-port=9222 --remote-allow-origins=http://localhost:9222
