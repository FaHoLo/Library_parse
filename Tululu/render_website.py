import json

from jinja2 import Environment, FileSystemLoader, select_autoescape


def main():
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
