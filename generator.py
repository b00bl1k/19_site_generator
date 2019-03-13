import os
import sys
import json
from jinja2 import Environment, FileSystemLoader


def load_config(filepath="config.json"):
    with open(filepath, "r", encoding="utf-8") as fh:
        return json.loads(fh.read())


def load_article(filepath, articles_dir="articles"):
    full_filepath = os.path.join(articles_dir, filepath)
    with open(full_filepath, "r", encoding="utf8") as fh:
        return fh.read()


def save_to_file(filepath, content):
    with open(filepath, "w", encoding="utf-8") as fh:
        fh.write(content)


def generate_index(template, config, filepath="index.html"):
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

    return template.render({"index": index})


def main():
    try:
        config = load_config()
    except FileNotFoundError:
        sys.exit("Configuration file not found")
    except json.JSONDecodeError:
        sys.exit("Invalid configuration")

    env = Environment(loader=FileSystemLoader("templates"))

    index_template = env.get_template("index.html")
    index_content = generate_index(index_template, config)
    save_to_file("index.html", index_content)


if __name__ == "__main__":
    main()
