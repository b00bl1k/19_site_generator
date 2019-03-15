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


def fill_urls_in_config(config):
    for article_idx in range(len(config["articles"])):
        path_md = config["articles"][article_idx]["source"]
        (base_path, _) = os.path.splitext(path_md)
        path_html = "{}{}{}".format(base_path, os.path.extsep, "html")
        url = "{}/{}/{}".format(OUTPUT_DIR, ARTICLES_DIR, path_html)
        config["articles"][article_idx]["output"] = url
        config["articles"][article_idx]["url"] = urllib.parse.quote(url)

    return config


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
    config = fill_urls_in_config(config)
    env = Environment(loader=FileSystemLoader("templates"), autoescape=True)

    index_template = env.get_template("index.html")
    index_content = generate_index(index_template, config)
    save_to_file("index.html", index_content)

    article_template = env.get_template("article.html")
    for article in config["articles"]:
        article_content = generate_article(article_template, article)
        save_to_file(article["output"], article_content)


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
