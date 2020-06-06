import argparse
import json
from math import ceil
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def main():
    parser = configure_argparser()
    args = parser.parse_args()
    render_library_pages()

    if args.run_debug:
        server = Server()
        server.watch('template.html', render_library_pages)
        server.serve(port=5501, root='.')


def configure_argparser():
    parser = argparse.ArgumentParser(
        description='Программа отрендерит страницы библиотеки'
    )
    parser.add_argument('-d', '--run_debug', action='store_true', help='Запустить в режиме разработки (livereload)')
    return parser


def render_library_pages(books_on_page=10, columns_amount=2, dest_folder='pages'):
    rows_amount = ceil(books_on_page / columns_amount)
    os.makedirs(dest_folder, exist_ok=True)

    with open('book_descriptions.json', 'r') as json_file:
        books = json.loads(json_file.read())
    books = list(chunked(chunked(books, columns_amount), rows_amount))
    page_amount = len(books)

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')

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
