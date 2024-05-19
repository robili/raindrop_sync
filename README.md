# Raindrop to ePub

This is a simple script that takes a few raindrops (url:s) from your Raindrop.io account, pulls the text (somewhat crudely) from those sources and creates an ePub file out of them, one chapter per article.

I built this to get daily reading material for my Kindle.

## Setup

You need an acc.py file containing just your Raindrop token. Like:

ACCESS_TOKEN = 'abc123'

In Raindrop you need three collections. One collection contains the list of urls you want to process (SOURCE_COLLECTION_ID), one is for storing the processed ones (PROCESSED_COLLECTION_ID) and the one for the ones that couldn't be processed (UNPROCESSED_COLLECTION_ID). You need to specify the IDs in main.py.

You can also define the number of articles per run in main.py (ARTICLES_PER_RUN).

## Output

The script will create a file with today's date in the current folder. This can then just be sent to your Kindle, uploaded to you Kobo Reader or whatever you use to consume text.
