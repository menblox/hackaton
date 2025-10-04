import asyncio
from bleak import BleakClient, BleakScanner

# Имя устройства
DEVICE_NAME = "Оно живое!"

# Предполагаемые UUID (замените, если знаете точные)
SERVICE_UUID = "19b10000-e8f2-537e-4f6c-d104768a1214"
CHAR_UUID = "19b10001-e8f2-537e-4f6c-d104768a1214"

async def connect_to_esp32():
    # Поиск устройства
    print(f"Поиск {DEVICE_NAME}...")
    devices = await BleakScanner.discover(timeout=15.0)  # Сканируем 15 секунд
    target_device = None
    for device in devices:
        if device.name == DEVICE_NAME:
            target_device = device
            break

    if not target_device:
        print(f"Устройство {DEVICE_NAME} не найдено!")
        return

    print(f"Найдено: {target_device.name} ({target_device.address})")

    # Подключение
    async with BleakClient(target_device.address) as client:
        if await client.is_connected():
            print(f"Подключено к {target_device.name}")

            # Функция обработки уведомлений
            def handle_notification(sender, data):
                try:
                    emg_value = data.decode('utf-8')
                    print(f"Получено: {emg_value}")
                except UnicodeDecodeError:
                    print(f"Неверные данные: {data}")

            # Включение уведомлений
            try:
                await client.start_notify(CHAR_UUID, handle_notification)
                print("Ожидание данных... (Ctrl+C для выхода)")
                await asyncio.sleep(3600)  # Ждём 1 час
            except Exception as e:
                print(f"Ошибка при подписке на уведомления: {e}")
            finally:
                await client.stop_notify(CHAR_UUID)

# Запуск
try:
    asyncio.run(connect_to_esp32())
except KeyboardInterrupt:
    print("Остановлено пользователем")