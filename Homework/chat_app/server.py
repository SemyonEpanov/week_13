import asyncio
import json
import datetime
import websockets

connected_clients = set()

async def log_message(data):
    try:
        with open("messages.json", "r", encoding="utf-8") as f:
            messages = json.load(f)
    except FileNotFoundError:
        messages = []

    messages.append(data)
    with open("messages.json", "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

async def handler(websocket):
    print(f"Новое подключение: {websocket.remote_address}")
    client_id = f"Client_{id(websocket)}"
    connected_clients.add(websocket)
    welcome_msg = {
        "time": datetime.datetime.now().isoformat(),
        "client_id": client_id,
        "message": "Добро пожаловать в чат!",
        "sender": "server"
    }
    await websocket.send("Добро пожаловать в чат!")
    await log_message(welcome_msg)
    try:
        async for msg in websocket:
            print(f"Получено сообщение от {client_id}: {msg}")
            data = {
                "time": datetime.datetime.now().isoformat(),
                "client_id": client_id,
                "message": msg,
                "sender": "client"
            }
            await log_message(data)
            sends = []
            for client in connected_clients:
                sends.append(client.send(msg))
            await asyncio.gather(*sends)
    except websockets.ConnectionClosed:
        print(f"Соединение с {client_id} закрыто.")
        disconnect_msg = {
            "time": datetime.datetime.now().isoformat(),
            "client_id": client_id,
            "message": "Сессия завершена. До свидания!",
            "sender": "server"
        }
        await log_message(disconnect_msg)
    finally:
        connected_clients.remove(websocket)
        await websocket.close()

async def main():
    print("Запуск WebSocket-сервера на ws://localhost:8765")
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()  # Работает до принудительной остановки

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[SERVER] Остановка сервера...")