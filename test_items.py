import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
import json

link_page = ['1', '2', '3', '4']
json_dict = {}

file1 = open("links.txt", "r")
list_link_old = file1.readlines()
list_link = [i.rstrip('\n') for i in list_link_old]
file1.close()


@pytest.fixture(scope="function")
def browser():
    print("\nstart browser for test..")
    browser = webdriver.Chrome()
    yield browser
    print("\nquit browser..")
    browser.quit()


class BasePage:
    """
    Класс для работы со страницами и браузером
    """
    def __init__(self, browser, url, timeout=10):
        self.browser = browser
        self.url = url
        self.browser.implicitly_wait(timeout)

    def open(self):
        """
        Открываем ссылку
        """
        self.browser.get(self.url)

    def getting_product_links(self):
        """
        Здесь ищем ссылки и записываем их в файл
        """
        product_link = self.browser.find_elements(By.CSS_SELECTOR,
                                                  "#products-inner a[data-v-606e0d9f][data-qa='product-card-photo-link']")
        for i in range(len(product_link)):
            list_link.append(product_link[i].get_attribute('href'))

        with open("links.txt", "w") as file:
            for x in list_link:
                file.write(x + '\n')

    def getting_product_date(self):
        """
        Здесь ищем данные и записываем их в словарь
        """
        item_number = self.browser.find_element(By.XPATH, "//p[@itemprop='productID']")
        name_of_product = self.browser.find_element(By.XPATH,
                                                    "//meta[@itemprop='name']")
        link_to_the_product = self.url
        brand = self.browser.find_element(By.XPATH, "//li[@class='product-attributes__list-item'][1]/a")
        try:
            assert self.browser.find_element(By.XPATH, "//div[@class='product-price-discount-above__top']/div")
            promo_price = self.browser.find_element(By.XPATH, "//meta[@itemprop='price']")
            regular_price = self.browser.find_element(By.XPATH,
                                                      "//div[@class='product-price-discount-above__top']//span[@class='product-price__sum']//span[@class='product-price__sum-rubles']")
            regular_price = regular_price.text
            promo_price = promo_price.get_attribute('content')
            d = {'name': name_of_product.get_attribute('content'), 'link': link_to_the_product,
                 'regular_price': regular_price, 'promo_price': promo_price, 'brand': brand.text}
            json_dict[item_number.text] = d


        except:
            regular_price = self.browser.find_element(By.XPATH, "//meta[@itemprop='price']")  # content
            promo_price = 'not promo'
            d = {'name': name_of_product.get_attribute('content'), 'link': link_to_the_product,
                 'regular_price': regular_price.get_attribute('content'), 'promo_price': promo_price, 'brand': brand.text}
            json_dict[item_number.text] = d


# парсим ссылки на товары
@pytest.mark.skip
@pytest.mark.parametrize('number', ['1', '2', '3', '4'])
def test_bypassing_product_pages(browser, number):
    link = f"https://online.metro-cc.ru/category/chaj-kofe-kakao/kofe/kofe-v-zernakh?from=under_search&in_stock=1&page={number}&eshop_order=1"
    page = BasePage(browser, link)
    page.open()
    page.getting_product_links()


# обходим страницы с продуктами
@pytest.mark.parametrize('link', iter(list_link))
def test_bypassing_product(browser, link):
    page = BasePage(browser, link)
    page.open()
    page.getting_product_date()


# записываем данные в json
def test_writing_to_json_file():
    with open('data.json', 'w') as outfile:
        json.dump(json_dict, outfile, indent=2, ensure_ascii=False)
