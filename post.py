import httpx
import os
from datetime import datetime, timezone, timedelta

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = "@veronastore_ru"
MOSCOW_TZ = timezone(timedelta(hours=3))

PHOTOS = [
    {
        "photo": "https://cdn-salini.storage.yandexcloud.net/iblock/2da/2da22e46b6959d9b10c20b159d4bc327/00.jpg",
        "context": "ванная с массивной чёрной скалой, ванна PERLA и круглые раковины ARMONIA от Salini из литьевого мрамора, природный стиль"
    },
    {
        "photo": "https://cdn-salini.storage.yandexcloud.net/iblock/b0e/b0ee08dc1424defc20c54a118fd21434/SpalnaNovyy%20blok_View110000.jpg",
        "context": "ванная в эко-стиле, три вида отделки — дерево, камень, мрамор, ванна Ornella от Salini"
    },
    {
        "photo": "https://cdn-salini.storage.yandexcloud.net/iblock/4d3/4d32cf86850dc131d284f24a6a488ade/R_1.jpg",
        "context": "мансардная ванная с косым потолком, ванна LUCE от Salini, нестандартное пространство"
    },
    {
        "photo": "https://cdn-salini.storage.yandexcloud.net/iblock/9b5/9b5a3c65786a4d225ab6682a43f07809/R_2.jpg",
        "context": "светлая минималистичная ванная, сантехника Salini из литьевого мрамора, спокойствие и роскошь"
    },
    {
        "photo": "https://cdn-salini.storage.yandexcloud.net/iblock/cb9/cb955b6bac92a7e8e1788bd9a5a58728/03.jpg",
        "context": "современная ванная с натуральными материалами, ванна Salini как арт-объект"
    },
    {
        "photo": "https://cdn-salini.storage.yandexcloud.net/iblock/220/220b573f70d0bade97dd6bf15eb1558c/05.jpg",
        "context": "отдельностоящая ванна Salini как скульптура, литьевой мрамор, современный дизайн"
    },
    {
        "photo": "https://cdn-salini.storage.yandexcloud.net/iblock/f97/f9767080f0a51c9ba8ef815f53ac8851/07.jpg",
        "context": "ванная как личное пространство для отдыха, атмосфера спа, продукция Salini"
    },
    {
        "photo": "https://cdn-salini.storage.yandexcloud.net/iblock/226/2260a325989a35ff96882a803d46e1a2/08.jpg",
        "context": "большая ванная комната, длинная линия мебели, правильное зонирование пространства"
    },
    {
        "photo": "https://cdn-salini.storage.yandexcloud.net/iblock/b55/b5521eb42e6dff26e1344850faf7db95/09.jpg",
        "context": "ванная в тёмных тонах — графит и антрацит, угловая ванна Salini"
    },
    {
        "photo": "https://cdn-salini.storage.yandexcloud.net/iblock/f5e/f5e01a1dfd6418a0ee8e15b180fce7be/01.jpg",
        "context": "плавные формы ванны Salini, литьевой камень, природные изгибы"
    },
    {
        "photo": "https://cdn-salini.storage.yandexcloud.net/iblock/54c/54c053241a36ba1a06f064b460b490a8/04.jpg",
        "context": "компактная ванная до 5 кв.м, правильное планирование, подвесная сантехника Salini"
    },
    {
        "photo": "https://cdn-salini.storage.yandexcloud.net/iblock/d3c/d3cdf37b46e3d5e72fd60b198dd1f442/06.jpg",
        "context": "световая стена в ванной вместо окна, правильное освещение, современная ванная Salini"
    },
]

SYSTEM = """Ты — автор Telegram-канала магазина Verona Store, который продаёт премиальную мебель и сантехнику для ванных комнат.

Пишешь посты как живой человек — с характером, иногда с юмором, всегда с искренним восхищением красивыми интерьерами. Не как робот и не как рекламный буклет.

Правила:
- Начни с чего-то неожиданного — вопроса, наблюдения, короткой истории
- Пиши разговорно, как будто рассказываешь другу
- 4-6 предложений, не больше
- 1-2 эмодзи — уместно, не перебарщивай
- В конце ВСЕГДА добавляй точно эти строки (без изменений):

📞 8 495 998-60-60
🌐 verona-store.ru
🤖 @VeronaStoreBot

Каждый раз пиши по-разному — меняй угол зрения, начало, стиль. Никаких шаблонов."""

def generate_caption(context):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ANTHROPIC_API_KEY не найден!")
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
            "messages": [{"role": "user", "content": f"Напиши пост для этого фото: {context}"}]
        },
        timeout=45
    )
    
    data = r.json()
    print(f"API status: {r.status_code}")
    print(f"API response: {data}")
    
    if "content" in data:
        return data["content"][0]["text"]
    else:
        print(f"Ошибка API: {data.get('error', data)}")
        return None

def main():
    import random
post = random.choice(PHOTOS)

    print(f"Генерирую текст для поста...")
    caption = generate_caption(post["context"])
    
    if not caption:
        print("Не удалось сгенерировать текст — выхожу")
        exit(1)

    r = httpx.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
        json={"chat_id": CHANNEL_ID, "photo": post["photo"], "caption": caption},
        timeout=30
    )
    
    if r.status_code == 200:
        print("Пост опубликован!")
    else:
        print(f"Ошибка Telegram: {r.text}")
        exit(1)

if __name__ == "__main__":
    main()
