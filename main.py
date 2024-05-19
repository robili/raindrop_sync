import requests
import acc
import get_page
from datetime import datetime

ACCESS_TOKEN = acc.ACCESS_TOKEN
SOURCE_COLLECTION_ID = '36864622'
PROCESSED_COLLECTION_ID = '44271309'
UNPROCESSED_COLLECTION_ID = '44302142'
URL = f'https://api.raindrop.io/rest/v1/raindrops/{SOURCE_COLLECTION_ID}/'
ARTICLES_PER_RUN = 5


def get_all_raindrops():
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }

    raindrops = []
    page = 0

    while True:
        params = {
            "page": page
        }
        response = requests.get(URL, headers=headers, params=params)
        # print(response.text)

        if response.status_code != 200:
            raise Exception(f"Failed to retrieve raindrops: {response.status_code} {response.text}")

        data = response.json()
        raindrops.extend(data["items"])

        if len(data["items"]) < data["count"]:
            break

        page += 1
        break # Temporary solution 

    return raindrops


def update_raindrop(id, no_process):
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }

    data = {
        'collection': {
            '$id': UNPROCESSED_COLLECTION_ID if no_process else PROCESSED_COLLECTION_ID
        }
    }

    url = f'https://api.raindrop.io/rest/v1/raindrop/{id}'
    response = requests.put(url, json=data, headers=headers)
    print(response)


if __name__ == '__main__':
    todays_date = datetime.now().strftime('%d%m%y')
    epub = get_page.epub_book_writer(todays_date)

    counter = 1
    try:
        raindrops = get_all_raindrops()
        for raindrop in raindrops:
            print(f"{raindrop['title']}: {raindrop['link']}")
            result = epub.add_chapter(raindrop['link'])
            update_raindrop(raindrop['_id'], result)
            if counter == ARTICLES_PER_RUN:
                break
            if result == 0:
                counter = counter + 1
    except Exception as e:
        print(f"An error occurred: {e}")

    epub.write_epub_book()
