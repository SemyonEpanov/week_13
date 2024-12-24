import asyncio
import websockets
from websockets.exceptions import ConnectionClosed

async def send_messages(websocket):
    """
    Читает сообщения из stdin и отправляет их на сервер.
    """
    while True:
        message = input("Введите сообщение (или /exit для выхода): ")
        if message.strip().lower() == '/exit':
            print("Выходим из чата...")
            # Закроем соединение, чтобы вызвать корректное завершение на сервере
            await websocket.close(reason="Пользователь завершил сессию")
            break
        else:
            await websocket.send(message)

async def receive_messages(websocket):
    """
    Асинхронно получает сообщения с сервера и выводит их на экран.
    """
    try:
        async for message in websocket:
            print(f"-> {message}")
    except ConnectionClosed as e:
        print(f"[CLIENT] Соединение закрыто: {e.reason}")

async def main():
    # Подключаемся к серверу
    uri = "ws://localhost:8765"
    print(f"[CLIENT] Подключаемся к {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            print("[CLIENT] Подключение установлено. Можете отправлять сообщения.")
            # Запускаем чтение с клавиатуры и приём сообщений параллельно
            sender_task = asyncio.create_task(send_messages(websocket))
            receiver_task = asyncio.create_task(receive_messages(websocket))
            
            # Ожидаем завершения любой из задач (или прерывания /exit)
            done, pending = await asyncio.wait(
                [sender_task, receiver_task],
                return_when=asyncio.FIRST_COMPLETED
            )

            # Завершаем оставшуюся задачу, если одна уже завершена
            for task in pending:
                task.cancel()
    except ConnectionRefusedError:
        print("[CLIENT] Не удалось подключиться к серверу. Убедитесь, что сервер запущен.")

if __name__ == "__main__":
    asyncio.run(main())
