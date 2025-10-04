import asyncio
from bleak import BleakScanner, BleakClient

SERVICE_UUID = "19b10000-e8f2-537e-4f6c-d104768a1214"
CHARACTERISTIC_UUID = "19b10001-e8f2-537e-4f6c-d104768a1214"

class EMGReceiver:
    def __init__(self):
        self.client = None
        self.connected = False

    def notification_handler(self, sender, data):
        print(f"📨 Получены данные: {data}")
        try:
            text = data.decode('utf-8', errors='ignore')
            print(f"   Текст: {text}")
        except:
            print(f"   HEX: {data.hex()}")

    def handle_disconnect(self, client):
        print("🔌 Соединение разорвано")
        self.connected = False

    async def connect_with_retry(self, device_address, max_attempts=5):
        for attempt in range(max_attempts):
            print(f"🔗 Попытка подключения {attempt + 1}/{max_attempts}...")
            
            try:
                self.client = BleakClient(
                    device_address, 
                    disconnected_callback=self.handle_disconnect,
                    timeout=20.0  # Увеличиваем таймаут
                )
                
                await self.client.connect()
                self.connected = True
                print("✅ Успешно подключено!")
                
                # Подписываемся на уведомления
                await self.client.start_notify(CHARACTERISTIC_UUID, self.notification_handler)
                print("📡 Слушаем данные...")
                
                # Ждем пока соединение активно
                while self.connected:
                    await asyncio.sleep(1)
                    
                print("🔄 Соединение потеряно, переподключаемся...")
                await asyncio.sleep(2)  # Ждем перед переподключением
                
            except Exception as e:
                print(f"❌ Ошибка подключения (попытка {attempt + 1}): {e}")
                if attempt < max_attempts - 1:
                    print("🔄 Повтор через 3 секунды...")
                    await asyncio.sleep(3)
                else:
                    print("🚫 Все попытки подключения исчерпаны")
                    break

async def main():
    receiver = EMGReceiver()
    device_address = "B0:B2:1C:A7:E2:9A"
    
    print(f"🎯 Целевое устройство: {device_address}")
    await receiver.connect_with_retry(device_address)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Остановлено пользователем")