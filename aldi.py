from datetime import datetime
from sqlalchemy.exc import IntegrityError
from bs4 import BeautifulSoup
import requests
import models
from sqlalchemy.orm import Session
# list-of-products
# https://www.aldi-sued.de/de/produkte/produktsortiment/brot-aufstrich-und-cerealien.html


def get_soup(url: str):
    text = requests.get(url).text
    return BeautifulSoup(text, 'html.parser')


def get_products(url: str):
    soup = get_soup(url)
    product_list = soup.find("div", {"class": "list-of-products"})
    for product in product_list.find_all("article", {"class": "wrapper"}):
        item = product.find("div", {"class": "item"})
        product_id = item.get("data-productid")
        item_class = product.get("data-acgshierarchy")
        title = product.find("h2", {"class": "product-title"}).string
        try:
            price = product.find("span", {"class": "price"}).string[:-1].strip()
            price = float(price[2:].replace(",", "."))
        except ValueError as ve:
            price = -1

        try:
            img = product.find("img").get("data-src")
        except AttributeError:
            img = "invalid"

        yield dict(title=title, price=price, img=img, id=product_id, item_class=item_class)


def get_categories():
    # https://www.aldi-sued.de/de/produkte/produktsortiment.html
    soup = get_soup("https://www.aldi-sued.de/de/produkte/produktsortiment.html")

    titles = []
    for title in soup.find_all("h2", {"class": "trenner"}):
        titles.append(title.string)

    print(titles)

    for i, c in enumerate(soup.find_all("p", {"class": "produkte-teaser"})):
        print(c)
        href = c.find("a").get("href")
        yield dict(name=titles[i], href=href)


def populate_categories(session: Session):

    for category in get_categories():
        session.add(models.Category(**category))

    session.commit()


def insert_product(session: Session, product: dict):
    session.add(models.Product(**product))
    session.commit()


def insert_price(session: Session, product: dict):
    product_id = product['id']
    price = product['price']
    ts = datetime.utcnow().timestamp()
    price_data = dict(product_id=product_id, ts=ts, price=price)
    session.add(models.Price(**price_data))
    session.commit()


def get_db_categories(session: Session):
    return [models.row2dict(c) for c in session.query(models.Category).all()]


def insert_products(session: Session, href: str):
    # https://www.aldi-sued.de/de/produkte/produktsortiment/brot-aufstrich-und-cerealien.onlyProduct.html?pageNumber=0
    url = f"https://www.aldi-sued.de{href}"
    page = 0

    def page_maker(p): return f"https://www.aldi-sued.de{href[:-5]}.onlyProduct.html?pageNumber={p}"

    print(f"inserting produts for {href}")

    while True:
        url = page_maker(page)
        print(f"query {url}")
        products = list(get_products(url))
        print(f"found {len(products)} products on page {page}")
        if len(products) == 0:
            print(f"finsihed at page {page} for href {href}")
            break

        for product in products:
            try:
                insert_product(session, product)
                print(f"inserted {product['title']}")
            except IntegrityError as ie:
                print(f"already inserted {product['title']}")
                session.rollback()

            try:
                insert_price(session, product)
                print(f"inserted price data for product {product['id']}")
            except IntegrityError as ie:
                print(f"error: could not insert price for product {product}")
                session.rollback()

        page += 1


def task():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    import tqdm

    # https://www.aldi-sued.de/de/produkte/produktsortiment/brot-aufstrich-und-cerealien.onlyProduct.html?pageNumber=3&_1649191510292
    # https://www.aldi-sued.de/de/produkte/produktsortiment/brot-aufstrich-und-cerealien.html
    # print(list(get_products(
    #     "https://www.aldi-sued.de/de/produkte/produktsortiment/brot-aufstrich-und-cerealien.onlyProduct.html?pageNumber=4")))

    engine = create_engine(f"sqlite:///database.sqlite")
    session_maker = sessionmaker(bind=engine, autocommit=False, autoflush=True)
    session = session_maker()

    # models.Base.metadata.create_all(bind=engine)
    # populate_categories(session)

    categories = get_db_categories(session)

    for category in tqdm.tqdm(categories):
        href = category['href']
        insert_products(session, href)


if __name__ == '__main__':
    import time
    import schedule

    print("run initial job for testing")
    task()

    print("starting aldi schedule")
    schedule.every().day.at("10:30").do(task)

    while True:
        schedule.run_pending()
        time.sleep(1)
