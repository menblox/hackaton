from machine import UART, Pin
import ubluetooth
import time

# UART настройка
uart = UART(1, baudrate=9600, tx=Pin(19), rx=Pin(21))

class BLEManager:
    def __init__(self):
        self.ble = ubluetooth.BLE()
        self.ble.active(True)
        self.ble.irq(self.ble_irq)
        self.connected = False
        self.setup_ble()
        
    def setup_ble(self):
        # BLE служба и характеристика
        service_uuid = '19b10000-e8f2-537e-4f6c-d104768a1214'
        char_uuid = '19b10001-e8f2-537e-4f6c-d104768a1214'
        
        service = (ubluetooth.UUID(service_uuid),)
        characteristic = (
            ubluetooth.UUID(char_uuid),
            ubluetooth.FLAG_READ | ubluetooth.FLAG_NOTIFY,
        )
        
        service_ble = (service, (characteristic,))
        services = (service_ble,)
        
        ((self.char_handle,),) = self.ble.gatts_register_services(services)
        
        # Настройка рекламы
        name = b'EMG-Sensor'
        adv_data = bytearray()
        adv_data.extend(bytes([0x02, 0x01, 0x06]))  # Flags
        adv_data.extend(bytes([len(name) + 1, 0x09]))  # Complete local name
        adv_data.extend(name)
        
        # Добавляем UUID службы в рекламу
        service_uuid_bytes = bytes.fromhex(service_uuid.replace('-', ''))
        adv_data.extend(bytes([1 + len(service_uuid_bytes), 0x06]))
        adv_data.extend(service_uuid_bytes)
        
        self.ble.gap_advertise(100000, adv_data)  # Рекламируем каждые 100ms
        print("🚀 BLE Server запущен")

    def ble_irq(self, event, data):
        if event == 1:  # _IRQ_CENTRAL_CONNECTED
            self.connected = True
            print("✅ Устройство подключено")
        elif event == 2:  # _IRQ_CENTRAL_DISCONNECTED
            self.connected = False
            print("🔌 Устройство отключено")
            # Перезапускаем рекламу
            self.ble.gap_advertise(100000, self.adv_data)
        elif event == 3:  # _IRQ_GATTS_WRITE
            print("📨 Получены данные от клиента")

    def send_data(self, data):
        if self.connected:
            try:
                self.ble.gatts_write(self.char_handle, data)
                self.ble.gatts_notify(0, self.char_handle, data)
                return True
            except Exception as e:
                print(f"❌ Ошибка отправки: {e}")
                self.connected = False
        return False

# Основной цикл
ble = BLEManager()
counter = 0

print("🔄 Запуск основного цикла...")

while True:
    # Проверяем UART данные
    if uart.any():
        data = uart.readline()
        if data:
            data = data.strip()
            print(f"📨 UART данные: {data}")
            ble.send_data(data)
    else:
        # Отправляем тестовые данные
        test_data = f"Test:{counter}".encode()
        if ble.send_data(test_data):
            print(f"📤 Отправлено: {test_data}")
            counter += 1
    
    time.sleep(1)