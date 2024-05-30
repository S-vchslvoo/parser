import requests
from bs4 import BeautifulSoup
import json
import csv

url = 'https://health-diet.ru/table_calorie/?utm_source=leftMenu&utm_medium=table_calorie'
headers = {  # показываем сайту, что мы не бот, а пользователь
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}
req = requests.get(url, headers=headers)
src = req.text

with open('index.html', 'w', encoding="utf-8") as file:
    file.write(src)

with open('index.html', 'r', encoding="utf-8") as file:
    src = file.read()

soup = BeautifulSoup(src, 'lxml')

all_products_hrefs = soup.find_all(class_='mzr-tc-group-item-href')
all_categories_dict = {}
for item in all_products_hrefs:
    item_text = item.text
    item_href = 'https://health-diet.ru' + item.get('href')
    all_categories_dict[item_text] = item_href

with open('all_categories_dict.json', 'w', encoding="utf-8") as file:
    json.dump(all_categories_dict, file, indent=4, ensure_ascii=False)

with open('all_categories_dict.json', 'r', encoding="utf-8") as file:
    all_categories = json.load(file)

iteration_count = int(len(all_categories)) - 1
count = 0
print(f'Всего итераций: {iteration_count}')
for categories_name, categories_href in all_categories.items():
    rep = [',', ' ', '-', '\'']
    for item in rep:
        if item in categories_name:
            categories_name = categories_name.replace(item, '_')

    req = requests.get(url=categories_href, headers=headers)
    src = req.text

    with open(f'data/{count}_{categories_name}.html', 'w', encoding="utf-8") as file:
        file.write(src)
    with open(f'data/{count}_{categories_name}.html', 'r', encoding="utf-8") as file:
        src = file.read()

    soup = BeautifulSoup(src, 'lxml')

    # проверяем на наличие таблицы
    alert_block = soup.find(class_='uk-alert-danger')
    if alert_block is not None:
        continue

    # собираем заголовки таблицы

    table_href = soup.find(class_='mzr-tc-group-table').find('tr').find_all('th')
    product = table_href[0].text
    calories = table_href[1].text
    proteins = table_href[2].text
    fats = table_href[3].text
    carbohydrates = table_href[4].text

    with open(f'data/{count}_{categories_name}.csv', 'w', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            (
                product,
                calories,
                proteins,
                fats,
                carbohydrates
            )
        )

    # собираем данные

    product_data = soup.find(class_='mzr-tc-group-table').find('tbody').find_all('tr')

    product_info = []
    for item in product_data:
        product_tds = item.find_all('td')
        title = product_tds[0].find('a').text
        calories = product_tds[1].text
        proteins = product_tds[2].text
        fats = product_tds[3].text
        carbohydrates = product_tds[4].text

        product_info.append(
            {
                'Title': title,
                'Calories': calories,
                'Proteins': proteins,
                'Fats': fats,
                'Carbohydrates': carbohydrates
            }
        )

        with open(f'data/{count}_{categories_name}.csv', 'a', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(
                (
                    title,
                    calories,
                    proteins,
                    fats,
                    carbohydrates
                )
            )

    with open(f'data/{count}_{categories_name}.json', 'a', encoding="utf-8") as file:
        json.dump(product_info, file, indent=4, ensure_ascii=False)

    count += 1
    print(f'# Итерация {count}. {categories_name} записан...')
    iteration_count = iteration_count - 1
    if iteration_count == 0:
        print('Работа завершена !')
        break
    print(f"осталось итераций {iteration_count}")
