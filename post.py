import httpx
import os
from datetime import datetime, timezone, timedelta

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = "@veronastore_ru"
MOSCOW_TZ = timezone(timedelta(hours=3))

# Фото с verona-store.ru + salini (все проверенные)
POSTS = [
    {"photo": "https://verona-store.ru/img/52327573.jpg", "brand": "Verona Design Frame", "topic": "коллекция Frame — архитектурная рамка вокруг фасада, керамогранит под камень, шпон американского ореха, стиль конструктивизма"},
    {"photo": "https://verona-store.ru/img/52327701.jpg", "brand": "Verona Design My Time", "topic": "коллекция My Time — фасады под углом 45°, чёткая геометрия, широкий выбор отделок для тех кто ценит индивидуальность"},
    {"photo": "https://verona-store.ru/img/52327581.jpg", "brand": "Verona Design Optima+", "topic": "коллекция Optima+ — максимум хранения при минимуме пространства, модульные тумбы, идеальное решение для компактных ванных"},
    {"photo": "https://verona-store.ru/img/52327703.jpg", "brand": "Verona Design Classic", "topic": "коллекция Classic — вневременная элегантность, фрезерованные фасады, фурнитура хром и золото, для ценителей традиционного стиля"},
    {"photo": "https://verona-store.ru/img/52345249.jpg", "brand": "Verona Design Ampio", "topic": "коллекция Ampio — создана для больших ванных с характером, широкие модули, два выдвижных ящика на полную ширину Soft-Close"},
    {"photo": "https://verona-store.ru/img/52345457.jpg", "brand": "Brenta Verso", "topic": "коллекция Verso — плавные линии, зеркальные или матовые поверхности, элегантность итальянского дизайна, spa-атмосфера"},
    {"photo": "https://verona-store.ru/img/52327459.jpg", "brand": "Brenta Lester", "topic": "коллекция Lester — матовый лак и фурнитура золото матовое, атмосфера премиального отеля, тумбы 100-200 см"},
    {"photo": "https://verona-store.ru/img/52327463.jpg", "brand": "Brenta Scala", "topic": "коллекция Scala — фасады из керамогранита который не боится влаги, царапин и перепадов температур, натуральная текстура камня"},
    {"photo": "https://verona-store.ru/img/52319105.jpg", "brand": "Brenta Manhattan", "topic": "коллекция Manhattan — матовый парящий фасад, скрытые ручки, графичные прямые формы, вдохновлён городским характером"},
    {"photo": "https://verona-store.ru/img/52327455.jpg", "brand": "Brenta Fusion", "topic": "коллекция Fusion — тепло натурального шпона и сдержанность матового лака, итальянская школа дизайна"},
    {"photo": "https://verona-store.ru/img/52315053.jpg", "brand": "Brenta Fly", "topic": "коллекция Fly — подвесные тумбы с тонкими фасадами, push-to-open, воздух и лёгкость, минимализм без лишних деталей"},
    {"photo": "https://verona-store.ru/img/52327611.jpg", "brand": "Brenta Simple", "topic": "коллекция Simple — никаких лишних деталей, скрытое крепление, простота как осознанный выбор, подходит к любому интерьеру"},
    {"photo": "https://cdn-salini.storage.yandexcloud.net/iblock/2da/2da22e46b6959d9b10c20b159d4bc327/00.jpg", "brand": "Salini", "topic": "ванна PERLA и раковины ARMONIA из литьевого мрамора — природный материал, ручная отделка, когда сантехника становится скульптурой"},
    {"photo": "https://cdn-salini.storage.yandexcloud.net/iblock/4d3/4d32cf86850dc131d284f24a6a488ade/R_1.jpg", "brand": "Salini", "topic": "ванна LUCE в мансардной ванной — литьевой мрамор Salini органично вписывается даже в нестандартные пространства"},
    {"photo": "https://cdn-salini.storage.yandexcloud.net/iblock/9b5/9b5a3c65786a4d225ab6682a43f07809/R_2.jpg", "brand": "Salini", "topic": "минималистичная ванная с сантехникой Salini — светлые тона, чистые линии, литьевой мрамор который не стареет"},
    {"photo": "https://cdn-salini.storage.yandexcloud.net/iblock/b0e/b0ee08dc1424defc20c54a118fd21434/SpalnaNovyy%20blok_View110000.jpg", "brand": "Salini", "topic": "ванная в эко-стиле с ванной Ornella Salini — три стихии: дерево, камень, мрамор в одном пространстве"},
    {"photo": "https://cdn-salini.storage.yandexcloud.net/iblock/220/220b573f70d0bade97dd6bf15eb1558c/05.jpg", "brand": "Salini", "topic": "отдельностоящая ванна Salini из литьевого камня — когда ванна становится главным арт-объектом комнаты"},
    {"photo": "https://cdn-salini.storage.yandexcloud.net/iblock/f97/f9767080f0a51c9ba8ef815f53ac8851/07.jpg", "brand": "Salini", "topic": "ванная как личный sanctuary — продукция Salini создаёт пространство где хочется остаться подольше"},
    {"photo": "https://cdn-salini.storage.yandexcloud.net/iblock/b55/b5521eb42e6dff26e1344850faf7db95/09.jpg", "brand": "Salini", "topic": "ванная в тёмных тонах с угловой ванной Salini — графит, антрацит, ощущение глубины и камерности"},
    {"photo": "https://cdn-salini.storage.yandexcloud.net/iblock/d3c/d3cdf37b46e3d5e72fd60b198dd1f442/06.jpg", "brand": "Bette", "topic": "немецкие ванны Bette из глазурованной титановой стали с 1952 года — 30 лет гарантии, более 600 цветов, Made in Germany"},
    {"photo": "https://cdn-salini.storage.yandexcloud.net/iblock/f5e/f5e01a1dfd6418a0ee8e15b180fce7be/01.jpg", "brand": "Gessi", "topic": "итальянские смесители Gessi ручной сборки — бронза, матовое золото, каждое изделие уникально как произведение искусства"},
    {"photo": "https://cdn-salini.storage.yandexcloud.net/iblock/54c/54c053241a36ba1a06f064b460b490a8/04.jpg", "brand": "Catalano", "topic": "итальянская керамика Catalano с 1967 года — инновационная глазурь CATAglaze не царапается и не впитывает загрязнения"},
    {"photo": "https://cdn-salini.storage.yandexcloud.net/iblock/226/2260a325989a35ff96882a803d46e1a2/08.jpg", "brand": "Dornbracht", "topic": "немецкие смесители Dornbracht класса люкс с 1950 года — инновационные технологии и философия чистоты линий"},
]

SYSTEM = """Ты автор Telegram-канала магазина Verona Store — официального дилера премиальной мебели и сантехники для ванных комнат в России.

Пиши как живой человек: с характером, иногда с юмором, всегда с искренним восхищением. Не как робот.

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
            "messages": [{"role": "user", "content": f"Напиши пост про {brand}: {topic}"}]
        },
        timeout=45
    )

    data = r.json()
    if "content" in data:
        return data["content"][0]["text"]

    print(f"Ошибка API: {data}")
    return None


def main():
    day = datetime.now(MOSCOW_TZ).timetuple().tm_yday
    post = POSTS[day % len(POSTS)]

    print(f"Бренд: {post['brand']}")
    print("Генерирую текст...")

    caption = generate_caption(post["brand"], post["topic"])
    if not caption:
        print("Не удалось сгенерировать текст")
        exit(1)

    r = httpx.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
        json={"chat_id": CHANNEL_ID, "photo": post["photo"], "caption": caption},
        timeout=30
    )

    if r.status_code == 200:
        print(f"Пост про {post['brand']} опубликован!")
    else:
        print(f"Ошибка Telegram: {r.text}")
        exit(1)


if __name__ == "__main__":
    main()
