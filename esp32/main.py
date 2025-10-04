from machine import UART, Pin, reset
import time
import sys

print("=" * 50)
print("🔧 ДИАГНОСТИКА ESP32")
print("=" * 50)

# Проверка пинов
try:
    uart = UART(1, baudrate=9600, tx=Pin(19), rx=Pin(21))
    print("✅ UART1 инициализирован")
    print(f"   TX: Pin 19, RX: Pin 21, Baudrate: 9600")
except Exception as e:
    print(f"❌ Ошибка UART: {e}")

# Проверка памяти
import gc
mem_free = gc.mem_free()
mem_alloc = gc.mem_alloc()
print(f"📊 Память: свободно {mem_free} байт, использовано {mem_alloc} байт")

# Тест работы
print("\n🎯 Начинаем основной цикл...")
print("📝 Отправляем 'TEST:X' в UART каждые 3 секунды")
print("📖 Читаем данные из UART если есть")
print("⏹️  Нажмите Ctrl+C в мониторе порта для остановки")

counter = 0
try:
    while True:
        # Чтение из UART
        if uart.any():
            data = uart.readline()
            if data:
                clean_data = data.decode('utf-8', errors='ignore').strip()
                print(f"📨 ВХОД: {clean_data} (сырые байты: {data})")
        
        # Запись в UART
        test_message = f"TEST:{counter}"
        uart.write(test_message + '\n')
        print(f"📤 ВЫХОД: {test_message}")
        
        counter += 1
        time.sleep(3)
        
except KeyboardInterrupt:
    print("\n🛑 Остановлено пользователем")
except Exception as e:
    print(f"💥 Критическая ошибка: {e}")
    print("🔄 Перезагрузка через 5 секунд...")
    time.sleep(5)
    reset()