import os
import json
import urllib
import markdown
import argparse
from livereload import Server
from jinja2 import Environment, FileSystemLoader

ARTICLES_DIR = "articles"
OUTPUT_DIR = "static/site"
SITE_URL = "https://b00bl1k.ru/19_site_generator/"


def load_config(filepath="config.json"):
    with open(filepath, "r", encoding="utf-8") as fh:
        return json.loads(fh.read())


def load_article(filepath):
    full_filepath = os.path.join(ARTICLES_DIR, filepath)
    with open(full_filepath, "r", encoding="utf-8") as fh:
        return fh.read()


def save_to_file(filepath, content):
    base_path = os.path.dirname(filepath)
    if base_path:
        os.makedirs(base_path, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as fh:
        fh.write(content)


def get_article_output_path(source_path):
    (base_path, _) = os.path.splitext(source_path)
    path_html = "{}{}{}".format(base_path, os.path.extsep, "html")
    return "{}/{}/{}".format(OUTPUT_DIR, ARTICLES_DIR, path_html)


def get_article_url(source_path):
    output_path = get_article_output_path(source_path)
    return urllib.parse.quote(output_path)


def generate_index(template, config):
    index = []
    for topic in config["topics"]:
        articles_by_topic = list(filter(
            lambda x: x["topic"] == topic["slug"],
            config["articles"]
        ))
        index.append({
            "title": topic["title"],
            "articles": articles_by_topic
        })

    return template.render({"index": index, "site_url": SITE_URL})


def generate_article(template, article):
    content_md = load_article(article["source"])
    content_html = markdown.markdown(content_md)
    return template.render({
        "title": article["title"],
        "content": content_html,
        "site_url": SITE_URL
    })


def make_site():
    config = load_config()

    for article in config["articles"]:
        article["url"] = get_article_url(article["source"])

    env = Environment(loader=FileSystemLoader("templates"), autoescape=True)

    index_template = env.get_template("index.html")
    index_content = generate_index(index_template, config)
    save_to_file("index.html", index_content)

    article_template = env.get_template("article.html")
    for article in config["articles"]:
        article_content = generate_article(article_template, article)
        output_path = get_article_output_path(article["source"])
        save_to_file(output_path, article_content)


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="subparser")
    serve_parser = subparsers.add_parser("serve")
    serve_parser.add_argument("-p", "--port", type=int, default=8000)
    args = parser.parse_args()

    make_site()

    if args.subparser == "serve":
        server = Server()
        server.watch("{}/*/*.md".format(ARTICLES_DIR), make_site)
        server.watch("config.json", make_site)
        server.watch("templates", make_site)
        server.serve(port=args.port, root=".")


if __name__ == "__main__":
    main()
