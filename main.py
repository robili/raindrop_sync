import requests
import acc
import get_page
from datetime import datetime
import smtplib
from email.message import EmailMessage

ACCESS_TOKEN = acc.ACCESS_TOKEN
SOURCE_COLLECTION_ID = '36864622'
PROCESSED_COLLECTION_ID = '44271309'
UNPROCESSED_COLLECTION_ID = '44302142'
URL = f'https://api.raindrop.io/rest/v1/raindrops/{SOURCE_COLLECTION_ID}/'
ARTICLES_PER_RUN = 5

EMAIL_SEND = acc.EMAIL_SEND
EMAIL_PASS = acc.EMAIL_PASS
KINDLE_EMAIL = acc.KINDLE_EMAIL
SMTP_SERVER=acc.SMTP_SERVER
SMTP_PORT=acc.SMTP_PORT


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


def send_mail(file_path, sender_email, sender_password, kindle_email, smtp_server, smtp_port):
    msg = EmailMessage()
    msg['From'] = sender_email
    msg['To'] = kindle_email
    msg['Subject'] = 'Raindrop'
    
    with open(file_path, 'rb') as f:
        file_data = f.read()
        file_name = f.name
        msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)

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

    file_destination = epub.write_epub_book()

    send_mail(file_destination, EMAIL_SEND, EMAIL_PASS, KINDLE_EMAIL, SMTP_SERVER, SMTP_PORT)
