#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Демонстрационный скрипт для создания примеров результатов
Показывает, как выглядят результаты парсинга TGStat.ru
"""

import os
from pathlib import Path
from datetime import datetime


def create_demo_results():
    """Создание демонстрационных результатов парсинга"""
    
    # Создаем папку results если не существует
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)
    
    # Демонстрационные данные каналов
    demo_channels = [
        {"name": "РИА Новости", "url": "https://t.me/rian_ru", "subscribers": "2.1M подписчиков"},
        {"name": "Медуза — LIVE", "url": "https://t.me/meduzalive", "subscribers": "890K подписчиков"},
        {"name": "RT на русском", "url": "https://t.me/rt_russian", "subscribers": "1.5M подписчиков"},
        {"name": "Коммерсантъ", "url": "https://t.me/kommersant", "subscribers": "654K подписчиков"},
        {"name": "Дождь", "url": "https://t.me/tvrain", "subscribers": "432K подписчиков"},
        {"name": "ТАСС", "url": "https://t.me/tass_agency", "subscribers": "1.2M подписчиков"},
        {"name": "Lenta.ru", "url": "https://t.me/lentachold", "subscribers": "567K подписчиков"},
        {"name": "Московский Комсомолец", "url": "https://t.me/mk_ru", "subscribers": "389K подписчиков"},
        {"name": "Известия", "url": "https://t.me/izvestia", "subscribers": "445K подписчиков"},
        {"name": "Ведомости", "url": "https://t.me/vedomosti", "subscribers": "234K подписчиков"},
    ]
    
    demo_chats = [
        {"name": "IT Общение", "url": "https://t.me/it_chat_ru", "subscribers": "45K участников"},
        {"name": "Криптовалюты", "url": "https://t.me/crypto_chat", "subscribers": "78K участников"},
        {"name": "Работа в IT", "url": "https://t.me/work_it", "subscribers": "123K участников"},
        {"name": "Стартапы", "url": "https://t.me/startup_chat", "subscribers": "67K участников"},
        {"name": "Python разработчики", "url": "https://t.me/python_dev", "subscribers": "89K участников"},
    ]
    
    # Создаем файл с демо-каналами
    channels_file = results_dir / f"DEMO_channels_news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(channels_file, 'w', encoding='utf-8') as f:
        f.write("# TGStat.ru Parser Results - ДЕМОНСТРАЦИЯ\n")
        f.write(f"# Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# Категория: Новости\n")
        f.write(f"# Всего найдено: {len(demo_channels)}\n")
        f.write("# ЭТО ДЕМОНСТРАЦИОННЫЕ ДАННЫЕ\n\n")
        
        for i, channel in enumerate(demo_channels, 1):
            line = f"{i}. {channel['name']} | {channel['url']} | {channel['subscribers']}\n"
            f.write(line)
    
    # Создаем файл с демо-чатами
    chats_file = results_dir / f"DEMO_chats_tech_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(chats_file, 'w', encoding='utf-8') as f:
        f.write("# TGStat.ru Parser Results - ДЕМОНСТРАЦИЯ\n")
        f.write(f"# Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# Категория: Технологии\n")
        f.write(f"# Всего найдено: {len(demo_chats)}\n")
        f.write("# ЭТО ДЕМОНСТРАЦИОННЫЕ ДАННЫЕ\n\n")
        
        for i, chat in enumerate(demo_chats, 1):
            line = f"{i}. {chat['name']} | {chat['url']} | {chat['subscribers']}\n"
            f.write(line)
    
    print("✅ Демонстрационные результаты созданы:")
    print(f"   📄 {channels_file}")
    print(f"   📄 {chats_file}")
    
    return channels_file, chats_file


def show_demo_usage():
    """Показать примеры использования"""
    print("\n📋 ПРИМЕРЫ РЕЗУЛЬТАТОВ ПАРСИНГА:")
    print("="*60)
    
    print("\n🔹 Формат результатов:")
    print("   Номер. Название | https://t.me/username | количество подписчиков")
    
    print("\n🔹 Примеры каналов:")
    print("   1. РИА Новости | https://t.me/rian_ru | 2.1M подписчиков")
    print("   2. Медуза — LIVE | https://t.me/meduzalive | 890K подписчиков")
    print("   3. RT на русском | https://t.me/rt_russian | 1.5M подписчиков")
    
    print("\n🔹 Примеры чатов:")
    print("   1. IT Общение | https://t.me/it_chat_ru | 45K участников")
    print("   2. Криптовалюты | https://t.me/crypto_chat | 78K участников")
    
    print("\n🔹 Структура файлов:")
    print("   results/")
    print("   ├── channels_news_20241215_143022.txt")
    print("   ├── chats_tech_20241215_144511.txt")
    print("   └── DEMO_*.txt")


def main():
    """Главная функция демо"""
    print("🎭 ДЕМОНСТРАЦИЯ - TGStat.ru Parser Results")
    print("Создание примеров результатов для ознакомления")
    
    try:
        # Создаем демо файлы
        create_demo_results()
        
        # Показываем примеры
        show_demo_usage()
        
        print("\n💡 Для реального парсинга запустите: python main.py")
        
    except Exception as e:
        print(f"❌ Ошибка при создании демо: {e}")


if __name__ == "__main__":
    main()