from selenium import webdriver
from bs4 import BeautifulSoup
from smtplib import SMTP_SSL
import time
import json
import os

SERVER_DETAILS = ('smtp.gmail.com', 465)
SPRITE_URL = (
    'http://www.mysupermarket.co.uk/tesco-price-comparison/'
    'Soft_Drinks/Sprite_Zero_2L.html'
)
SLEEP_PAGE_LOAD_SECONDS = 5
SLEEP_POST_CLICK_SECONDS = 0.2
PRICE_CUTOFF = 1.


def load_details(keys=('username', 'password', 'recipient')):
    credentials_file_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'credentials.json'
    )
    with open(credentials_file_path) as fd:
        data = json.load(fd)

    return (data[key] for key in keys)


def main():
    driver = webdriver.Firefox()
    driver.get(SPRITE_URL)

    time.sleep(SLEEP_PAGE_LOAD_SECONDS)

    see_all_button = driver.find_element_by_id('SeeAllPrices')
    see_all_button.click()

    time.sleep(SLEEP_POST_CLICK_SECONDS)

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    driver.quit()

    first_store = soup.find('div', {'id': 'NgMspProductPrice'})
    first_storename = first_store.find('img').get('alt')
    first_price_description = first_store.find(
        'span', {'id': 'PriceDescription'}
    )
    first_price_text = first_price_description.text.split()[-1]

    # Format is £1.85., trim first and last characters.
    price = float(first_price_text[1:-1])

    prices = {first_storename: price}

    discount_stores = soup.find_all('li', {'class': 'PriceDiscount'})
    for discount_store in discount_stores:
        storename = discount_store.find('img').get('alt')
        price = discount_store = float(
            discount_store.find('div', {'class': 'HasOffer'}).text.strip()[1:]
        )
        prices[storename] = price

    prices = {
        storename: price
        for storename, price in prices.items()
        if price <= PRICE_CUTOFF
    }

    if len(prices) >= 1:
        message = (
            'Good news!\n\n2L bottles of Sprite Zero are available from the '
            'following stores at these excellent prices!\n\n'
        )
        message += ', '.join(
            ['{} for only £{}'.format(key, val) for key, val in prices.items()]
        ) + '.'

        message = 'Subject: Great deals on Sprite Zero!\n\n{}'.format(message)
        message = message.encode('utf8')

        username, password, recipient = load_details()

        server = SMTP_SSL(*SERVER_DETAILS)
        server.ehlo()
        server.login(username, password)

        server.sendmail(username, recipient, message)

        server.close()


if __name__ == '__main__':
    main()
