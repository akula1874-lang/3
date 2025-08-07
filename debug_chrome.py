#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Отладочный скрипт для диагностики проблем с Chrome и ChromeDriver
Специально для Windows
"""

import os
import sys
import time
import subprocess
import requests
import zipfile
from pathlib import Path

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except ImportError:
    print("❌ Selenium не установлен. Выполните: pip install selenium")
    sys.exit(1)


def test_chrome_installation():
    """Тестирование установки Chrome"""
    print("🔍 Проверка установки Chrome...")
    
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        rf"C:\Users\{os.getenv('USERNAME', 'User')}\AppData\Local\Google\Chrome\Application\chrome.exe"
    ]
    
    for chrome_path in chrome_paths:
        if os.path.exists(chrome_path):
            print(f"✅ Chrome найден: {chrome_path}")
            
            # Получаем версию через командную строку
            try:
                result = subprocess.run([chrome_path, '--version'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    version = result.stdout.strip()
                    print(f"🔢 Версия: {version}")
                    return chrome_path, version
            except Exception as e:
                print(f"⚠️ Не удалось получить версию: {e}")
                
            return chrome_path, "неизвестна"
    
    print("❌ Chrome не найден")
    return None, None


def test_chromedriver_basic():
    """Базовый тест ChromeDriver"""
    print("\n🧪 БАЗОВЫЙ ТЕСТ CHROMEDRIVER")
    print("-" * 40)
    
    # Проверяем существующий драйвер
    driver_dir = Path("drivers")
    driver_paths = list(driver_dir.rglob("chromedriver.exe"))
    
    if not driver_paths:
        print("❌ ChromeDriver не найден в папке drivers/")
        return False
    
    driver_path = str(driver_paths[0])
    print(f"📁 Найден ChromeDriver: {driver_path}")
    
    # Минимальные настройки
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    service = Service(driver_path)
    
    try:
        print("🚀 Запуск Chrome...")
        driver = webdriver.Chrome(service=service, options=options)
        
        print("✅ Chrome запущен успешно")
        
        # Простой тест
        driver.get("https://www.google.com")
        print("✅ Страница Google загружена")
        
        time.sleep(2)
        driver.quit()
        print("✅ Chrome закрыт")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def test_chromedriver_headless():
    """Тест ChromeDriver в headless режиме"""
    print("\n🤖 ТЕСТ HEADLESS РЕЖИМА")
    print("-" * 40)
    
    driver_dir = Path("drivers")
    driver_paths = list(driver_dir.rglob("chromedriver.exe"))
    
    if not driver_paths:
        print("❌ ChromeDriver не найден")
        return False
    
    driver_path = str(driver_paths[0])
    
    # Настройки для headless
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    service = Service(driver_path)
    
    try:
        print("🚀 Запуск Chrome в headless режиме...")
        driver = webdriver.Chrome(service=service, options=options)
        
        print("✅ Chrome запущен в headless режиме")
        
        # Тест загрузки страницы
        driver.get("https://www.google.com")
        title = driver.title
        print(f"✅ Заголовок страницы: {title}")
        
        driver.quit()
        print("✅ Chrome закрыт")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в headless режиме: {e}")
        return False


def test_tgstat_connection():
    """Тест подключения к tgstat.ru"""
    print("\n🌐 ТЕСТ ПОДКЛЮЧЕНИЯ К TGSTAT.RU")
    print("-" * 40)
    
    driver_dir = Path("drivers")
    driver_paths = list(driver_dir.rglob("chromedriver.exe"))
    
    if not driver_paths:
        print("❌ ChromeDriver не найден")
        return False
    
    driver_path = str(driver_paths[0])
    
    # Настройки для обхода защиты
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(driver_path)
    
    try:
        print("🚀 Запуск Chrome для tgstat.ru...")
        driver = webdriver.Chrome(service=service, options=options)
        
        # Убираем следы автоматизации
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("🌐 Подключение к tgstat.ru...")
        driver.get("https://tgstat.ru")
        
        # Ждем загрузки
        time.sleep(5)
        
        current_url = driver.current_url
        title = driver.title
        
        print(f"🔗 Текущий URL: {current_url}")
        print(f"📄 Заголовок: {title}")
        
        if "tgstat" in current_url.lower():
            print("✅ Успешное подключение к tgstat.ru")
            result = True
        else:
            print("⚠️ Возможно, есть редирект или блокировка")
            result = False
        
        # Сохраняем скриншот для диагностики
        try:
            screenshot_path = "debug_screenshot.png"
            driver.save_screenshot(screenshot_path)
            print(f"📸 Скриншот сохранен: {screenshot_path}")
        except Exception:
            pass
        
        driver.quit()
        return result
        
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False


def main():
    """Главная функция диагностики"""
    print("🔧 ДИАГНОСТИКА CHROME + CHROMEDRIVER")
    print("=" * 50)
    
    # Тест 1: Проверка Chrome
    chrome_path, chrome_version = test_chrome_installation()
    if not chrome_path:
        print("💡 Установите Chrome: https://www.google.com/chrome/")
        return
    
    # Тест 2: Базовый тест ChromeDriver
    basic_test = test_chromedriver_basic()
    
    # Тест 3: Headless режим
    headless_test = test_chromedriver_headless()
    
    # Тест 4: Подключение к tgstat.ru
    tgstat_test = test_tgstat_connection()
    
    # Итоговый отчет
    print("\n" + "=" * 50)
    print("📊 ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 50)
    
    tests = [
        ("Chrome установлен", chrome_path is not None),
        ("Базовый ChromeDriver", basic_test),
        ("Headless режим", headless_test),
        ("Подключение к tgstat.ru", tgstat_test)
    ]
    
    passed = 0
    for test_name, result in tests:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 Результат: {passed}/{len(tests)} тестов пройдено")
    
    if passed == len(tests):
        print("🎉 Все тесты пройдены! Парсер должен работать.")
    elif basic_test:
        print("💡 Базовая функциональность работает. Возможно, проблема в специфических настройках.")
    else:
        print("🚨 Есть проблемы с базовой настройкой Chrome/ChromeDriver.")
        print("💡 Рекомендации:")
        print("   • Перезапустите все процессы Chrome")
        print("   • Обновите Chrome до последней версии")
        print("   • Удалите папку drivers/ и запустите парсер заново")


if __name__ == "__main__":
    main()