#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TGStat.ru Parser - Адаптированный для Windows/PyCharm
Автор: AI Assistant
Версия: 2.0 (Windows Edition)

Парсер для извлечения данных о Telegram каналах и чатах с сайта tgstat.ru
Полностью адаптирован для работы на Windows через PyCharm
"""

import os
import sys
import time
import random
import logging
import requests
import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import zipfile
import subprocess

# Selenium imports
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
    from selenium.webdriver.common.action_chains import ActionChains
except ImportError:
    print("❌ Ошибка: Selenium не установлен!")
    print("Выполните: pip install selenium requests")
    sys.exit(1)


class TGStatParser:
    """Основной класс парсера TGStat.ru для Windows"""
    
    def __init__(self):
        """Инициализация парсера"""
        self.base_url = "https://tgstat.ru"
        self.driver = None
        self.results_dir = Path("results")
        self.logs_dir = Path("logs")
        self.driver_dir = Path("drivers")
        
        # Создание необходимых директорий
        for directory in [self.results_dir, self.logs_dir, self.driver_dir]:
            directory.mkdir(exist_ok=True)
        
        # Настройка логирования
        self.setup_logging()
        
        # User agents для ротации
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        ]
        
        self.logger.info("🚀 TGStat Parser инициализирован для Windows")
    
    def setup_logging(self):
        """Настройка системы логирования"""
        log_file = self.logs_dir / f"tgstat_parser_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        # Настройка форматтера
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Консольный хендлер
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        
        # Файловый хендлер
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        
        # Настройка логгера
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        
        # Отключаем лишние логи Selenium
        selenium_logger = logging.getLogger('selenium')
        selenium_logger.setLevel(logging.WARNING)
    
    def check_internet_connection(self) -> bool:
        """Проверка интернет соединения"""
        try:
            self.logger.info("🌐 Проверка интернет соединения...")
            response = requests.get("https://google.com", timeout=5)
            if response.status_code == 200:
                self.logger.info("✅ Интернет соединение установлено")
                return True
        except requests.RequestException as e:
            self.logger.error(f"❌ Нет интернет соединения: {e}")
            return False
        return False
    
    def get_chrome_version(self) -> Optional[str]:
        """Получение версии Chrome в Windows"""
        try:
            # Различные пути установки Chrome в Windows
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                r"C:\Users\{username}\AppData\Local\Google\Chrome\Application\chrome.exe".format(
                    username=os.getenv('USERNAME', '')
                )
            ]
            
            for chrome_path in chrome_paths:
                if os.path.exists(chrome_path):
                    try:
                        # Получаем версию через wmic
                        result = subprocess.run([
                            'wmic', 'datafile', 'where', f'name="{chrome_path.replace(chr(92), chr(92)+chr(92))}"',
                            'get', 'Version', '/value'
                        ], capture_output=True, text=True, timeout=10)
                        
                        if result.returncode == 0:
                            for line in result.stdout.strip().split('\n'):
                                if line.startswith('Version='):
                                    version = line.split('=')[1].strip()
                                    major_version = version.split('.')[0]
                                    self.logger.info(f"🔍 Найдена версия Chrome: {version} (мажорная: {major_version})")
                                    return major_version
                    except Exception as e:
                        self.logger.debug(f"Не удалось получить версию через wmic: {e}")
                        continue
            
            self.logger.warning("⚠️ Не удалось определить версию Chrome автоматически")
            return "120"  # Версия по умолчанию
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка при определении версии Chrome: {e}")
            return "120"
    
    def download_chromedriver(self, version: str) -> Optional[str]:
        """Скачивание ChromeDriver для Windows"""
        try:
            self.logger.info(f"📥 Скачивание ChromeDriver версии {version}...")
            
            # URL для скачивания ChromeDriver
            base_url = "https://chromedriver.storage.googleapis.com"
            
            # Получаем доступные версии
            try:
                versions_url = f"{base_url}/{version}/chromedriver_win32.zip"
                response = requests.head(versions_url, timeout=10)
                
                if response.status_code != 200:
                    # Пробуем новый формат URL для более новых версий
                    versions_url = f"https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/{version}.0.6167.85/win64/chromedriver-win64.zip"
                    response = requests.head(versions_url, timeout=10)
                    
                    if response.status_code != 200:
                        # Fallback на стабильную версию
                        versions_url = "https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_win32.zip"
            except:
                versions_url = "https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_win32.zip"
            
            # Скачиваем ChromeDriver
            driver_zip = self.driver_dir / "chromedriver.zip"
            
            self.logger.info(f"🔗 URL для скачивания: {versions_url}")
            
            response = requests.get(versions_url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(driver_zip, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Извлекаем архив
            with zipfile.ZipFile(driver_zip, 'r') as zip_ref:
                zip_ref.extractall(self.driver_dir)
            
            # Удаляем архив
            driver_zip.unlink()
            
            # Ищем исполняемый файл
            driver_paths = list(self.driver_dir.rglob("chromedriver.exe"))
            if driver_paths:
                driver_path = str(driver_paths[0])
                self.logger.info(f"✅ ChromeDriver загружен: {driver_path}")
                return driver_path
            
            self.logger.error("❌ ChromeDriver не найден после извлечения")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка при загрузке ChromeDriver: {e}")
            return None
    
    def setup_webdriver(self) -> bool:
        """Настройка WebDriver для Windows"""
        try:
            self.logger.info("🔧 Настройка WebDriver...")
            
            # Проверяем существующий драйвер
            existing_drivers = list(self.driver_dir.rglob("chromedriver.exe"))
            driver_path = None
            
            if existing_drivers:
                driver_path = str(existing_drivers[0])
                self.logger.info(f"📁 Найден существующий ChromeDriver: {driver_path}")
            else:
                # Загружаем новый драйвер
                chrome_version = self.get_chrome_version()
                driver_path = self.download_chromedriver(chrome_version)
                
                if not driver_path:
                    self.logger.error("❌ Не удалось загрузить ChromeDriver")
                    return False
            
            # Настройка опций Chrome
            chrome_options = Options()
            
            # Базовые опции для стабильной работы
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")
            chrome_options.add_argument("--disable-javascript")
            
            # User agent
            user_agent = random.choice(self.user_agents)
            chrome_options.add_argument(f"--user-agent={user_agent}")
            
            # Размер окна
            chrome_options.add_argument("--window-size=1920,1080")
            
            # Отключаем уведомления об автоматизации
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Создаем сервис
            service = Service(driver_path)
            
            # Инициализируем драйвер
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Убираем следы автоматизации
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.logger.info("✅ WebDriver успешно настроен")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка при настройке WebDriver: {e}")
            return False
    
    def wait_for_cloudflare(self, timeout: int = 30) -> bool:
        """Ожидание прохождения Cloudflare защиты"""
        try:
            self.logger.info("🛡️ Ожидание прохождения Cloudflare защиты...")
            
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                try:
                    # Проверяем наличие элементов Cloudflare
                    cf_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                        ".cf-browser-verification, .cf-checking-browser, .cf-spinner-allow-5-secs")
                    
                    if not cf_elements:
                        # Проверяем, что страница загрузилась
                        if "tgstat.ru" in self.driver.current_url.lower():
                            self.logger.info("✅ Cloudflare защита пройдена")
                            return True
                    
                    time.sleep(2)
                    
                except Exception:
                    pass
            
            self.logger.warning("⚠️ Превышено время ожидания Cloudflare")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка при ожидании Cloudflare: {e}")
            return False
    
    def get_categories(self, content_type: str = "channels") -> List[Dict[str, str]]:
        """Получение списка категорий"""
        try:
            self.logger.info(f"📝 Получение категорий для {content_type}...")
            
            url = f"{self.base_url}/{content_type}"
            self.driver.get(url)
            
            if not self.wait_for_cloudflare():
                self.logger.warning("⚠️ Проблемы с Cloudflare, используем fallback категории")
                return self.get_fallback_categories(content_type)
            
            time.sleep(3)
            
            categories = []
            
            # Пробуем различные селекторы для категорий
            category_selectors = [
                "a[href*='/channels/']",
                "a[href*='/chats/']",
                ".category-link",
                ".nav-link",
                "[data-category]"
            ]
            
            for selector in category_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        try:
                            link = element.get_attribute("href")
                            text = element.text.strip()
                            
                            if link and text and ("channels" in link or "chats" in link):
                                categories.append({
                                    "name": text,
                                    "url": link,
                                    "type": content_type
                                })
                        except Exception:
                            continue
                    
                    if categories:
                        break
                        
                except Exception:
                    continue
            
            # Убираем дубликаты
            unique_categories = []
            seen_urls = set()
            
            for cat in categories:
                if cat["url"] not in seen_urls:
                    unique_categories.append(cat)
                    seen_urls.add(cat["url"])
            
            if unique_categories:
                self.logger.info(f"✅ Найдено {len(unique_categories)} категорий")
                return unique_categories[:20]  # Ограничиваем количество
            else:
                self.logger.warning("⚠️ Категории не найдены, используем fallback")
                return self.get_fallback_categories(content_type)
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка при получении категорий: {e}")
            return self.get_fallback_categories(content_type)
    
    def get_fallback_categories(self, content_type: str) -> List[Dict[str, str]]:
        """Fallback категории если не удалось получить с сайта"""
        if content_type == "channels":
            return [
                {"name": "Новости", "url": f"{self.base_url}/channels/news", "type": "channels"},
                {"name": "Развлечения", "url": f"{self.base_url}/channels/entertainment", "type": "channels"},
                {"name": "Технологии", "url": f"{self.base_url}/channels/tech", "type": "channels"},
                {"name": "Спорт", "url": f"{self.base_url}/channels/sport", "type": "channels"},
                {"name": "Музыка", "url": f"{self.base_url}/channels/music", "type": "channels"},
            ]
        else:
            return [
                {"name": "Общение", "url": f"{self.base_url}/chats/communication", "type": "chats"},
                {"name": "Игры", "url": f"{self.base_url}/chats/games", "type": "chats"},
                {"name": "Работа", "url": f"{self.base_url}/chats/work", "type": "chats"},
                {"name": "Криптовалюты", "url": f"{self.base_url}/chats/crypto", "type": "chats"},
            ]
    
    def parse_channel_data(self, url: str, max_pages: int = 1) -> List[Dict[str, str]]:
        """Парсинг данных каналов с указанной страницы"""
        results = []
        
        try:
            self.logger.info(f"🔍 Парсинг: {url} (страниц: {max_pages})")
            
            for page in range(1, max_pages + 1):
                try:
                    page_url = f"{url}?page={page}" if page > 1 else url
                    self.logger.info(f"📄 Обработка страницы {page}")
                    
                    self.driver.get(page_url)
                    
                    if not self.wait_for_cloudflare():
                        self.logger.warning(f"⚠️ Проблемы с Cloudflare на странице {page}")
                        continue
                    
                    time.sleep(random.uniform(2, 4))
                    
                    # Прокручиваем страницу для загрузки контента
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                    
                    page_results = self.extract_channels_from_page()
                    results.extend(page_results)
                    
                    self.logger.info(f"✅ Страница {page}: найдено {len(page_results)} каналов")
                    
                    # Задержка между страницами
                    if page < max_pages:
                        delay = random.uniform(3, 6)
                        self.logger.info(f"⏱️ Задержка {delay:.1f}с перед следующей страницей")
                        time.sleep(delay)
                        
                except Exception as e:
                    self.logger.error(f"❌ Ошибка на странице {page}: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка при парсинге {url}: {e}")
        
        return results
    
    def extract_channels_from_page(self) -> List[Dict[str, str]]:
        """Извлечение каналов с текущей страницы"""
        channels = []
        
        try:
            # Множественные стратегии поиска
            selectors = [
                "a[href*='t.me/']",
                "[data-channel]",
                ".channel-item",
                ".channel-link",
                "a[href*='telegram']",
            ]
            
            found_links = []
            
            # Пробуем каждый селектор
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        try:
                            link = element.get_attribute("href")
                            if link and "t.me/" in link:
                                found_links.append((element, link))
                        except Exception:
                            continue
                            
                except Exception:
                    continue
            
            # Дополнительный поиск прямыми ссылками
            if not found_links:
                page_source = self.driver.page_source
                telegram_links = re.findall(r'https?://t\.me/([a-zA-Z0-9_]+)', page_source)
                
                for username in telegram_links:
                    found_links.append((None, f"https://t.me/{username}"))
            
            # Обрабатываем найденные ссылки
            for element, link in found_links:
                try:
                    # Извлекаем username
                    username_match = re.search(r't\.me/([a-zA-Z0-9_]+)', link)
                    if not username_match:
                        continue
                    
                    username = username_match.group(1)
                    
                    # Получаем название и подписчиков
                    name = "Неизвестный канал"
                    subscribers = "Неизвестно"
                    
                    if element:
                        try:
                            # Ищем название рядом с элементом
                            parent = element.find_element(By.XPATH, "./..")
                            name_candidates = parent.find_elements(By.CSS_SELECTOR, 
                                ".title, .name, .channel-name, h3, h4, .text-lg, .font-bold")
                            
                            if name_candidates:
                                name = name_candidates[0].text.strip() or username
                            
                            # Ищем количество подписчиков
                            sub_elements = parent.find_elements(By.CSS_SELECTOR, 
                                ".subscribers, .members, .count, .number")
                            
                            for sub_elem in sub_elements:
                                sub_text = sub_elem.text.strip()
                                if any(keyword in sub_text.lower() for keyword in ['подписчик', 'member', 'участник', 'k', 'm']):
                                    subscribers = sub_text
                                    break
                        
                        except Exception:
                            name = username
                    else:
                        name = username
                    
                    channels.append({
                        "name": name,
                        "url": link,
                        "subscribers": subscribers,
                        "username": username
                    })
                    
                except Exception as e:
                    self.logger.debug(f"Ошибка при обработке ссылки {link}: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка при извлечении каналов: {e}")
        
        return channels
    
    def save_results(self, results: List[Dict[str, str]], filename: str):
        """Сохранение результатов в файл"""
        try:
            if not results:
                self.logger.warning("⚠️ Нет данных для сохранения")
                return
            
            filepath = self.results_dir / f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("# TGStat.ru Parser Results\n")
                f.write(f"# Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# Всего найдено: {len(results)}\n\n")
                
                for i, channel in enumerate(results, 1):
                    line = f"{i}. {channel['name']} | {channel['url']} | {channel['subscribers']}\n"
                    f.write(line)
            
            self.logger.info(f"✅ Результаты сохранены: {filepath}")
            self.logger.info(f"📊 Всего каналов: {len(results)}")
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка при сохранении: {e}")
    
    def interactive_menu(self):
        """Интерактивное меню для пользователя"""
        print("\n" + "="*60)
        print("🎉 TGStat.ru Parser - Windows Edition")
        print("="*60)
        
        while True:
            try:
                print("\n📋 ГЛАВНОЕ МЕНЮ:")
                print("1. Парсить каналы")
                print("2. Парсить чаты")  
                print("3. Тестовое подключение")
                print("4. Выход")
                
                choice = input("\n👉 Выберите действие (1-4): ").strip()
                
                if choice == "1":
                    self.parse_content("channels")
                elif choice == "2":
                    self.parse_content("chats")
                elif choice == "3":
                    self.test_connection()
                elif choice == "4":
                    print("\n👋 До свидания!")
                    break
                else:
                    print("❌ Неверный выбор. Попробуйте снова.")
                    
            except KeyboardInterrupt:
                print("\n\n⚠️ Прерывание пользователем")
                break
            except Exception as e:
                self.logger.error(f"❌ Ошибка в меню: {e}")
    
    def parse_content(self, content_type: str):
        """Парсинг контента выбранного типа"""
        try:
            print(f"\n🔍 Парсинг {content_type}...")
            
            # Настраиваем WebDriver
            if not self.setup_webdriver():
                print("❌ Не удалось настроить WebDriver")
                return
            
            # Получаем категории
            categories = self.get_categories(content_type)
            
            if not categories:
                print("❌ Не удалось получить категории")
                return
            
            print(f"\n📂 Доступные категории ({len(categories)}):")
            for i, cat in enumerate(categories, 1):
                print(f"{i}. {cat['name']}")
            
            # Выбор категории
            while True:
                try:
                    cat_choice = input(f"\n👉 Выберите категорию (1-{len(categories)}): ").strip()
                    cat_index = int(cat_choice) - 1
                    
                    if 0 <= cat_index < len(categories):
                        selected_category = categories[cat_index]
                        break
                    else:
                        print("❌ Неверный номер категории")
                except ValueError:
                    print("❌ Введите число")
            
            # Выбор количества страниц
            print("\n📄 Количество страниц для парсинга:")
            print("1. 1 страница (быстро)")
            print("2. 10 страниц (средне)")
            print("3. 50+ страниц (долго)")
            print("4. Свое количество")
            
            while True:
                try:
                    page_choice = input("\n👉 Выберите (1-4): ").strip()
                    
                    if page_choice == "1":
                        max_pages = 1
                        break
                    elif page_choice == "2":
                        max_pages = 10
                        break
                    elif page_choice == "3":
                        max_pages = 50
                        break
                    elif page_choice == "4":
                        custom_pages = input("👉 Введите количество страниц: ").strip()
                        max_pages = int(custom_pages)
                        break
                    else:
                        print("❌ Неверный выбор")
                except ValueError:
                    print("❌ Введите число")
            
            # Запускаем парсинг
            print(f"\n🚀 Начинаем парсинг: {selected_category['name']}")
            print(f"📄 Страниц: {max_pages}")
            
            results = self.parse_channel_data(selected_category['url'], max_pages)
            
            if results:
                filename = f"{content_type}_{selected_category['name'].replace(' ', '_')}"
                self.save_results(results, filename)
                print(f"\n✅ Парсинг завершен! Найдено: {len(results)} каналов")
            else:
                print("\n❌ Данные не найдены")
                
        except Exception as e:
            self.logger.error(f"❌ Ошибка при парсинге: {e}")
            print(f"❌ Произошла ошибка: {e}")
        
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None
    
    def test_connection(self):
        """Тестирование соединения"""
        print("\n🧪 ТЕСТИРОВАНИЕ СОЕДИНЕНИЯ")
        print("-" * 40)
        
        # Проверка интернета
        if not self.check_internet_connection():
            print("❌ Нет интернет соединения")
            return
        
        # Проверка Chrome
        chrome_version = self.get_chrome_version()
        print(f"🔍 Версия Chrome: {chrome_version}")
        
        # Проверка WebDriver
        if self.setup_webdriver():
            print("✅ WebDriver настроен успешно")
            
            try:
                self.driver.get("https://tgstat.ru")
                print("✅ Подключение к tgstat.ru успешно")
                
                if self.wait_for_cloudflare():
                    print("✅ Cloudflare защита пройдена")
                else:
                    print("⚠️ Проблемы с Cloudflare защитой")
                    
            except Exception as e:
                print(f"❌ Ошибка подключения: {e}")
            
            finally:
                self.driver.quit()
                self.driver = None
        else:
            print("❌ Ошибка настройки WebDriver")
    
    def cleanup(self):
        """Очистка ресурсов"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None


def main():
    """Главная функция"""
    parser = None
    
    try:
        # Проверка Python версии
        if sys.version_info < (3, 7):
            print("❌ Требуется Python 3.7 или выше")
            return
        
        print("🐍 Python версия:", sys.version.split()[0])
        
        # Создаем парсер
        parser = TGStatParser()
        
        # Проверяем интернет
        if not parser.check_internet_connection():
            print("❌ Отсутствует интернет соединение")
            return
        
        # Запускаем интерактивное меню
        parser.interactive_menu()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Программа прервана пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
    finally:
        if parser:
            parser.cleanup()


if __name__ == "__main__":
    main()