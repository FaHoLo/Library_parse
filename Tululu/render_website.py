import json
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
    rows_in_column = int(books_on_page / 2)
    dest_folder = 'pages'
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    with open('book_descriptions.json', 'r') as json_file:
        books = json.loads(json_file.read())

    books = list(chunked(chunked(books, 2), rows_in_column))
    template = env.get_template('template.html')
    os.makedirs(dest_folder, exist_ok=True)

    for page_number, page_books in enumerate(books):
        rendered_page = template.render(books=page_books)
        filepath = os.path.join(dest_folder, f'index{page_number+1}.html')
        with open(filepath, 'w', encoding='utf8') as file:
            file.write(rendered_page)


if __name__ == "__main__":
    main()
