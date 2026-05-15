import httpx
import os
import random
from datetime import datetime, timezone, timedelta

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = "@veronastore_ru"
MOSCOW_TZ = timezone(timedelta(hours=3))

# Красивые фото ванных комнат с Unsplash (бесплатная лицензия)
PHOTOS = [
    "https://images.unsplash.com/photo-1753605788101-04d1e653e74a?fm=jpg&q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1552321554-5fefe8c9ef14?fm=jpg&q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1507652313519-d4e9174996dd?fm=jpg&q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1620626011761-996317702782?fm=jpg&q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1600566753086-00f18fb6b3ea?fm=jpg&q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?fm=jpg&q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1571902943202-507ec2618e8f?fm=jpg&q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1629079447777-1e605162dc8d?fm=jpg&q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1560185007-cde436f6a4d0?fm=jpg&q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1595514535215-9a5b0a165e9c?fm=jpg&q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1552321554-5fefe8c9ef14?fm=jpg&q=80&w=1200&auto=format&fit=crop",
    "https://images.unsplash.com/photo-1600585154526-990dced4db0d?fm=jpg&q=80&w=1200&auto=format&fit=crop",
]

# Бренды и темы для постов — чередуются каждый день
BRANDS = [
    {"brand": "Catalano", "topic": "итальянская керамика с 1967 года, минималистичный дизайн, инновационная глазурь CATAglaze которая не царапается"},
    {"brand": "Bette", "topic": "немецкие ванны из глазурованной титановой стали, 30 лет гарантии, более 600 цветов, Made in Germany"},
    {"brand": "Salini", "topic": "сантехника из литьевого мрамора, ванны и раковины которые выглядят как природные объекты, российское производство"},
    {"brand": "Gessi", "topic": "итальянские смесители ручной сборки, бронза и матовое золото, каждый смеситель уникален"},
    {"brand": "Dornbracht", "topic": "немецкие смесители класса люкс с 1950 года, инновационные технологии, минималистичный дизайн"},
    {"brand": "Decor Walther", "topic": "немецкие аксессуары для ванной ручной работы, хром, матовое золото, нержавеющая сталь"},
    {"brand": "Duravit", "topic": "немецкий производитель с 200-летней историей, сотрудничество с Philippe Starck и другими дизайнерами"},
    {"brand": "Antonio Lupi", "topic": "итальянский авангардный дизайн, ванная как место для медитации, дерево, камень и металл"},
    {"brand": "Fantini", "topic": "итальянские смесители с 1947 года, ручная полировка каждого изделия, классика и современность"},
    {"brand": "Falper", "topic": "итальянские ванны и душевые из дерева, камня и металла, натуральные материалы в каждом изделии"},
    {"brand": "Alice Ceramica", "topic": "итальянская керамика — смелые формы, яркие цвета, нестандартные решения для ванной"},
    {"brand": "GSI Ceramica", "topic": "итальянская дизайнерская сантехника Made in Italy, коллекции Nubes, Kube X, Color Elements"},
    {"brand": "Ceramica Cielo", "topic": "поэзия в керамике, нежные формы, пастельные цвета, уникальные фактуры от итальянского бренда"},
    {"brand": "Kerasan", "topic": "итальянская керамика — сочетание традиций и инноваций, ретро-стиль и современные решения в одном бренде"},
    {"brand": "Scarabeo", "topic": "нестандартные раковины и унитазы, более 400 моделей, широкая палитра цветов от итальянского бренда"},
    {"brand": "Ceramica Flaminia", "topic": "итальянское производство с 1956 года, экологичное производство, инновационная глазурь"},
    {"brand": "Radaway", "topic": "душевые ограждения — широкий ассортимент, надёжное качество, разные стили и размеры"},
    {"brand": "Verona Design", "topic": "коллекции Frame, My Time, Optima+ — мебель для ванной с выразительным дизайном и богатым выбором отделок"},
    {"brand": "Brenta", "topic": "коллекции Verso, Scala, Manhattan — итальянская мебель с авторским характером и архитектурной эстетикой"},
    {"brand": "Valdama", "topic": "итальянская керамика ручной работы, уникальные формы и авторский дизайн, смелые цвета"},
    {"brand": "CEA Design", "topic": "итальянские смесители — баланс между технологией и красотой, коллаборации с ведущими дизайнерами"},
    {"brand": "Artceram", "topic": "итальянская керамика премиум-класса, смелый дизайн, инновационные технологии производства"},
    {"brand": "Broner Radiator", "topic": "дизайнерские радиаторы — тепло и стиль в вашей ванной, широкий выбор форм и цветов"},
]

SYSTEM = """Ты автор Telegram-канала магазина Verona Store — премиальная мебель и сантехника для ванных комнат. Verona Store является официальным дилером этих брендов в России.

Пиши как живой человек: с характером, иногда с юмором, всегда с искренним восхищением. Не как робот и не как рекламный буклет.

Правила:
- Начни неожиданно — с вопроса, наблюдения или короткой истории
- Разговорный стиль, как рассказываешь другу
- 4-6 предложений
- 1-2 эмодзи
- В конце ВСЕГДА добавляй точно эти строки:

📞 8 495 998-60-60
🌐 verona-store.ru
🤖 @VeronaStoreBot

Каждый раз новый угол зрения. Никаких шаблонов."""


def generate_caption(brand, topic):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    r = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        },
        json={
            "model": "claude-sonnet-4-5",
            "max_tokens": 300,
            "system": SYSTEM,
            "messages": [{"role": "user", "content": f"Напиши пост про бренд {brand}: {topic}"}]
        },
        timeout=45
    )

    data = r.json()
    if "content" in data:
        return data["content"][0]["text"]

    print(f"Ошибка API: {data}")
    return None


def main():
    now = datetime.now(MOSCOW_TZ)
    day = now.timetuple().tm_yday

    # Выбираем бренд по дню года — каждый день новый бренд
    brand_data = BRANDS[day % len(BRANDS)]
    # Фото выбираем случайно
    photo = PHOTOS[day % len(PHOTOS)]

    print(f"Бренд: {brand_data['brand']}")
    print("Генерирую текст...")

    caption = generate_caption(brand_data["brand"], brand_data["topic"])
    if not caption:
        print("Не удалось сгенерировать текст")
        exit(1)

    r = httpx.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
        json={"chat_id": CHANNEL_ID, "photo": photo, "caption": caption},
        timeout=30
    )

    if r.status_code == 200:
        print(f"✅ Пост про {brand_data['brand']} опубликован!")
    else:
        print(f"Ошибка Telegram: {r.text}")
        exit(1)


if __name__ == "__main__":
    main()
