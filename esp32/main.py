from micropython import const
import asyncio
import aioble
import bluetooth
from machine import UART, Pin

# UART для связи с Arduino
uart = UART(1, baudrate=9600, tx=19, rx=21)  # Пины и скорость можно изменить

# BLE UUID
_BLE_SERVICE_UUID = bluetooth.UUID('19b10000-e8f2-537e-4f6c-d104768a1214')
_BLE_SENSOR_CHAR_UUID = bluetooth.UUID('19b10001-e8f2-537e-4f6c-d104768a1214')
_ADV_INTERVAL_MS = 250_000

# Регистрация сервиса
ble_service = aioble.Service(_BLE_SERVICE_UUID)
sensor_characteristic = aioble.Characteristic(ble_service, _BLE_SENSOR_CHAR_UUID, read=True, notify=True)
aioble.register_services(ble_service)

def _encode_data(data):
    return str(data).encode('utf-8')

async def sensor_task():
    while True:
        if uart.any():
            data = uart.readline().strip()
            try:
                emg_value = int(data)
                sensor_characteristic.write(_encode_data(emg_value), send_update=True)
                print('Отправлено по BLE: ', emg_value)
            except ValueError:
                print('Неверные данные от UART')
        await asyncio.sleep_ms(100)

async def peripheral_task():
    while True:
        async with await aioble.advertise(
            _ADV_INTERVAL_MS,
            name="Оно живое!",
            services=[_BLE_SERVICE_UUID],
        ) as connection:
            print("Соединение от", connection.device)
            await connection.disconnected()

async def main():
    t1 = asyncio.create_task(sensor_task())
    t2 = asyncio.create_task(peripheral_task())
    await asyncio.gather(t1, t2)

asyncio.run(main())