import json
from math import ceil
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def main():
    render_index_pages()
    server = Server()
    server.watch('template.html', render_index_pages)
    server.serve(port=5501, root='.')


def render_index_pages():
    books_on_page = 10
    columns_amount = 2
    rows_amount = ceil(books_on_page / columns_amount)
    dest_folder = 'pages'
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    with open('book_descriptions.json', 'r') as json_file:
        books = json.loads(json_file.read())

    books = list(chunked(chunked(books, columns_amount), rows_amount))
    template = env.get_template('template.html')
    os.makedirs(dest_folder, exist_ok=True)

    page_amount = len(books)
    for page_number, page_books in enumerate(books):
        page_number += 1
        rendered_page = template.render(books=page_books,
                                        page_number=page_number,
                                        page_amount=page_amount)
        filepath = os.path.join(dest_folder, f'index{page_number}.html')
        with open(filepath, 'w', encoding='utf8') as file:
            file.write(rendered_page)


if __name__ == "__main__":
    main()
