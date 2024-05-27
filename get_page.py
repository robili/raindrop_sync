import requests
from bs4 import BeautifulSoup
from ebooklib import epub

class epub_book_writer():
    minimum_text_length = 100
    title = None
    url = None
    book = None
    counter = 1
    chapter_list = ['nav']
    table_of_contents = []


    def __init__(self, title) -> None:
        self.title = title
        self._create_epub_book(title)


    # Get the page and remove all the clutter to make it as nice as possible
    def add_chapter(self, url) -> int:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        for script in soup(['script', 'style', 'header', 'footer', 'nav', 'aside', 'img', 'form', 'noscript']):
            script.decompose()

        # A mini trick that works frequently enough... Pull the paragraphs and clean them up. Ignore the formatting inside of them.
        paragraphs = soup.find_all('p')
        cleaned_paragraphs = []

        for p in paragraphs:
            cleaned_paragraphs.append(str(p))

        cleaned_text = ''.join(cleaned_paragraphs)

        if len(cleaned_text) <= self.minimum_text_length:
            return 1

        # Create a chapter
        page_title = soup.title.string if soup.title else 'Untitled'
        chapter = epub.EpubHtml(title=page_title, file_name=f'chap_{self.counter}.xhtml', lang='en')
        source_host = url.split('.')[1]
        chapter.content = f'<html><head></head><body><h1>From {source_host}</h1>{cleaned_text}</body></html>'
        self.table_of_contents.append(epub.Link(f'chap_{self.counter}.xhtml', page_title, f'chap_{self.counter}'))

        # Add chapter to the book
        self.book.add_item(chapter)
        self.chapter_list.append(chapter)
        self.counter = self.counter + 1

        return 0


    def _create_epub_book(self, title) -> None:
        # Create the epub book and set some basic metadata
        self.book = epub.EpubBook()

        # Set metadata
        self.book.set_title(title)
        self.book.set_language('en')


    def write_epub_book(self) -> str:
        self.book.spine = self.chapter_list
        self.book.toc = self.table_of_contents

        # Add default NCX and Nav file
        self.book.add_item(epub.EpubNcx())
        self.book.add_item(epub.EpubNav())

        # Define CSS style
        style = 'body { font-family: Arial, sans-serif; }'
        nav_css = epub.EpubItem(uid='style_nav', file_name='style/nav.css', media_type='text/css', content=style)
        self.book.add_item(nav_css)

        # Write to the file
        epub.write_epub(f'{self.title}.epub', self.book, {})

        print(f'ePub book created successfully: {self.title}.epub')

        return {self.title}.epub


if __name__ == '__main__':
    e = epub_book_writer('Muppet')
    e.add_chapter('https://www.vice.com/en/article/m7bxdx/scientists-are-researching-a-device-that-can-induce-lucid-dreams-on-demand')
    e.add_chapter('https://www.fastcompany.com/91126591/is-the-self-driving-dream-going-to-crash-into-a-regulatory-wall')
    e.add_chapter('https://www.youtube.com/watch?v=4C7UtIQx3qY')
    e.write_epub_book()