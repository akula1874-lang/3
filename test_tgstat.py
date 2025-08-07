#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки TGStat.ru Parser
Быстрая проверка основных функций без полного запуска
"""

import os
import sys
import requests
import subprocess
from pathlib import Path
import json


def test_python_version():
    """Проверка версии Python"""
    print("🐍 Проверка версии Python...")
    version = sys.version_info
    
    if version >= (3, 7):
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Требуется 3.7+")
        return False


def test_dependencies():
    """Проверка установленных зависимостей"""
    print("\n📦 Проверка зависимостей...")
    
    required_packages = ['selenium', 'requests']
    all_installed = True
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - установлен")
        except ImportError:
            print(f"❌ {package} - НЕ УСТАНОВЛЕН")
            all_installed = False
    
    return all_installed


def test_internet_connection():
    """Проверка интернет соединения"""
    print("\n🌐 Проверка интернет соединения...")
    
    test_urls = [
        "https://google.com",
        "https://tgstat.ru"
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {url} - доступен")
            else:
                print(f"⚠️ {url} - код ответа: {response.status_code}")
        except requests.RequestException as e:
            print(f"❌ {url} - недоступен: {e}")
            return False
    
    return True


def test_chrome_installation():
    """Проверка установки Chrome"""
    print("\n🔍 Проверка установки Chrome...")
    
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Users\{username}\AppData\Local\Google\Chrome\Application\chrome.exe".format(
            username=os.getenv('USERNAME', 'User')
        )
    ]
    
    for chrome_path in chrome_paths:
        if os.path.exists(chrome_path):
            print(f"✅ Chrome найден: {chrome_path}")
            
            # Попытка получить версию
            try:
                result = subprocess.run([
                    'wmic', 'datafile', 'where', f'name="{chrome_path.replace(chr(92), chr(92)+chr(92))}"',
                    'get', 'Version', '/value'
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if line.startswith('Version='):
                            version = line.split('=')[1].strip()
                            print(f"🔢 Версия Chrome: {version}")
                            return True
            except Exception:
                pass
            
            return True
    
    print("❌ Chrome не найден в стандартных местах")
    print("💡 Установите Chrome: https://www.google.com/chrome/")
    return False


def test_file_structure():
    """Проверка файловой структуры проекта"""
    print("\n📁 Проверка файловой структуры...")
    
    required_files = [
        "main.py",
        "requirements.txt",
        "README_WINDOWS.md"
    ]
    
    all_exist = True
    
    for file in required_files:
        filepath = Path(file)
        if filepath.exists():
            print(f"✅ {file} - найден")
        else:
            print(f"❌ {file} - НЕ НАЙДЕН")
            all_exist = False
    
    # Проверим создание директорий
    test_dirs = ["results", "logs", "drivers"]
    for dir_name in test_dirs:
        test_dir = Path(dir_name)
        try:
            test_dir.mkdir(exist_ok=True)
            if test_dir.exists():
                print(f"✅ Директория {dir_name}/ - создана/существует")
            else:
                print(f"❌ Директория {dir_name}/ - не удалось создать")
                all_exist = False
        except Exception as e:
            print(f"❌ Ошибка создания {dir_name}/: {e}")
            all_exist = False
    
    return all_exist


def test_encoding():
    """Проверка поддержки UTF-8"""
    print("\n🔤 Проверка поддержки UTF-8...")
    
    test_string = "Тестовая строка с кириллицей: каналы, чаты, подписчики 📱"
    
    try:
        # Тест записи в файл
        test_file = Path("test_encoding.txt")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_string)
        
        # Тест чтения из файла
        with open(test_file, 'r', encoding='utf-8') as f:
            read_string = f.read()
        
        if read_string == test_string:
            print("✅ UTF-8 кодировка - работает корректно")
            test_file.unlink()  # Удаляем тестовый файл
            return True
        else:
            print("❌ UTF-8 кодировка - проблема с чтением")
            return False
            
    except Exception as e:
        print(f"❌ UTF-8 кодировка - ошибка: {e}")
        return False


def test_selenium_basic():
    """Базовая проверка Selenium"""
    print("\n🤖 Базовая проверка Selenium...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        print("✅ Selenium импортирован успешно")
        
        # Проверим настройки Chrome
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        print("✅ Chrome options настроены")
        
        # Не будем создавать драйвер в тесте, только проверим настройки
        return True
        
    except Exception as e:
        print(f"❌ Ошибка Selenium: {e}")
        return False


def generate_test_report():
    """Генерация отчета о тестировании"""
    print("\n" + "="*60)
    print("📊 ОТЧЕТ О ТЕСТИРОВАНИИ")
    print("="*60)
    
    tests = [
        ("Python версия", test_python_version),
        ("Зависимости", test_dependencies),
        ("Интернет соединение", test_internet_connection),
        ("Chrome установка", test_chrome_installation),
        ("Файловая структура", test_file_structure),
        ("UTF-8 кодировка", test_encoding),
        ("Selenium базовый", test_selenium_basic)
    ]
    
    results = {}
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ Критическая ошибка в тесте '{test_name}': {e}")
            results[test_name] = False
    
    print(f"\n📈 РЕЗУЛЬТАТЫ: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Парсер готов к использованию!")
        print("\n🚀 Для запуска введите: python main.py")
    else:
        print("\n⚠️ Обнаружены проблемы, требующие решения:")
        for test_name, result in results.items():
            if not result:
                print(f"   • {test_name}")
        
        print("\n💡 Рекомендации:")
        if not results.get("Зависимости", True):
            print("   • Выполните: pip install -r requirements.txt")
        if not results.get("Chrome установка", True):
            print("   • Установите Chrome: https://www.google.com/chrome/")
        if not results.get("Интернет соединение", True):
            print("   • Проверьте интернет соединение")
    
    # Сохраняем отчет
    report_file = Path("test_report.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': str(Path().resolve()),
            'results': results,
            'passed': passed,
            'total': total,
            'status': 'PASS' if passed == total else 'FAIL'
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 Детальный отчет сохранен: {report_file}")


def main():
    """Главная функция тестирования"""
    try:
        print("🧪 TGStat.ru Parser - Тестирование системы")
        print("Проверка готовности к работе на Windows")
        
        generate_test_report()
        
    except KeyboardInterrupt:
        print("\n⚠️ Тестирование прервано пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка тестирования: {e}")


if __name__ == "__main__":
    main()