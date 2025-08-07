#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт установки и настройки TGStat.ru Parser для Windows
Автоматическая установка всех зависимостей и проверка системы
"""

import os
import sys
import subprocess
import requests
import zipfile
from pathlib import Path


def check_python_version():
    """Проверка версии Python"""
    print("🐍 Проверка версии Python...")
    version = sys.version_info
    
    if version >= (3, 7):
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Требуется 3.7+")
        print("💡 Скачайте новую версию: https://www.python.org/downloads/")
        return False


def install_dependencies():
    """Установка Python зависимостей"""
    print("\n📦 Установка зависимостей...")
    
    requirements = ["selenium>=4.15.0", "requests>=2.31.0"]
    
    for package in requirements:
        try:
            print(f"📥 Установка {package}...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {package} установлен")
            else:
                print(f"❌ Ошибка установки {package}: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Критическая ошибка установки {package}: {e}")
            return False
    
    return True


def create_directories():
    """Создание необходимых директорий"""
    print("\n📁 Создание директорий...")
    
    directories = ["results", "logs", "drivers"]
    
    for dir_name in directories:
        try:
            Path(dir_name).mkdir(exist_ok=True)
            print(f"✅ Директория {dir_name}/ создана")
        except Exception as e:
            print(f"❌ Ошибка создания {dir_name}/: {e}")
            return False
    
    return True


def download_chromedriver():
    """Загрузка ChromeDriver"""
    print("\n🔧 Загрузка ChromeDriver...")
    
    # Проверяем, есть ли уже драйвер
    driver_dir = Path("drivers")
    existing_drivers = list(driver_dir.rglob("chromedriver.exe"))
    
    if existing_drivers:
        print(f"✅ ChromeDriver уже существует: {existing_drivers[0]}")
        return True
    
    # Список URL для загрузки
    download_urls = [
        "https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_win32.zip",
        "https://chromedriver.storage.googleapis.com/113.0.5672.63/chromedriver_win32.zip",
        "https://chromedriver.storage.googleapis.com/112.0.5615.49/chromedriver_win32.zip"
    ]
    
    for url in download_urls:
        try:
            print(f"🔗 Попытка загрузки: {url}")
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Сохраняем архив
            driver_zip = driver_dir / "chromedriver.zip"
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(driver_zip, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\r📥 Загружено: {progress:.1f}%", end='')
            
            print("\n📦 Извлечение архива...")
            
            # Извлекаем архив
            with zipfile.ZipFile(driver_zip, 'r') as zip_ref:
                zip_ref.extractall(driver_dir)
            
            # Удаляем архив
            driver_zip.unlink()
            
            # Проверяем результат
            driver_paths = list(driver_dir.rglob("chromedriver.exe"))
            if driver_paths:
                print(f"✅ ChromeDriver загружен: {driver_paths[0]}")
                return True
            
        except Exception as e:
            print(f"\n⚠️ Ошибка загрузки с {url}: {e}")
            continue
    
    print("❌ Не удалось загрузить ChromeDriver")
    return False


def test_installation():
    """Тестирование установки"""
    print("\n🧪 Тестирование установки...")
    
    try:
        # Тест импорта
        import selenium
        import requests
        print("✅ Модули импортированы успешно")
        
        # Тест ChromeDriver
        driver_dir = Path("drivers")
        driver_paths = list(driver_dir.rglob("chromedriver.exe"))
        
        if driver_paths:
            print(f"✅ ChromeDriver найден: {driver_paths[0]}")
        else:
            print("❌ ChromeDriver не найден")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False


def main():
    """Главная функция установки"""
    print("🚀 УСТАНОВКА TGSTAT.RU PARSER")
    print("=" * 50)
    print("Автоматическая установка для Windows")
    print("=" * 50)
    
    steps = [
        ("Проверка Python", check_python_version),
        ("Установка зависимостей", install_dependencies),
        ("Создание директорий", create_directories),
        ("Загрузка ChromeDriver", download_chromedriver),
        ("Тестирование", test_installation)
    ]
    
    for step_name, step_func in steps:
        print(f"\n⏳ {step_name}...")
        
        try:
            if not step_func():
                print(f"\n❌ Ошибка на этапе: {step_name}")
                print("💡 Проверьте сообщения об ошибках выше")
                return False
        except KeyboardInterrupt:
            print("\n⚠️ Установка прервана пользователем")
            return False
        except Exception as e:
            print(f"\n❌ Критическая ошибка на этапе '{step_name}': {e}")
            return False
    
    # Финальный отчет
    print("\n" + "=" * 50)
    print("🎉 УСТАНОВКА ЗАВЕРШЕНА!")
    print("=" * 50)
    print("✅ Все компоненты установлены и настроены")
    print("\n🚀 Для запуска парсера введите:")
    print("   python main.py")
    print("\n🧪 Для диагностики введите:")
    print("   python debug_chrome.py")
    print("\n📚 Документация:")
    print("   README_WINDOWS.md - полная документация")
    print("   ИНСТРУКЦИЯ_WINDOWS.md - пошаговое руководство")
    print("   ЗАПУСК_В_PYCHARM.md - инструкция для PyCharm")
    
    return True


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Установка прервана пользователем")
    except Exception as e:
        print(f"\n\n❌ Критическая ошибка установки: {e}")
        print("💡 Попробуйте запустить установку еще раз")