import json

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server


def main():
    render_index_page()
    server = Server()
    server.watch('template.html', render_index_page)
    server.serve(port=5501, root='.')


def render_index_page():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    with open('book_descriptions.json', 'r') as json_file:
        books = json.loads(json_file.read())

    template = env.get_template('template.html')
    rendered_page = template.render(books=books)

    with open('index.html', 'w', encoding='utf8') as file:
        file.write(rendered_page)


if __name__ == "__main__":
    main()
