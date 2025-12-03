import json
import requests
import websocket


def get_devtools_ws_url():
    # Hole Liste der offenen Tabs
    tabs = requests.get("http://localhost:9222/json").json()

    # Nimm die erste normale Seite
    for t in tabs:
        if t.get("type") == "page":
            return t["webSocketDebuggerUrl"]

    raise RuntimeError("Kein Page-Target gefunden")


def fetch_global_scene():
    ws_url = get_devtools_ws_url()

    ws = websocket.create_connection(ws_url)

    # globalScene serialisieren
    request = {
        "id": 1,
        "method": "Runtime.evaluate",
        "params": {
            "expression": "JSON.stringify(globalScene)"
        }
    }

    ws.send(json.dumps(request))
    response = json.loads(ws.recv())
    ws.close()

    # Ergebnis extrahieren
    result_str = response["result"]["result"].get("value", "{}")
    result_obj = json.loads(result_str)

    # In Datei speichern
    with open("global_scene.json", "w", encoding="utf-8") as f:
        json.dump(result_obj, f, indent=4, ensure_ascii=False)

    return result_obj


if __name__ == "__main__":
    scene = fetch_global_scene()
    print("globalScene gespeichert.")
