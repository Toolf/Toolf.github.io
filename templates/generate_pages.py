import os
import re
import json
import argparse
from jinja2 import Environment, FileSystemLoader


def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9']+", "-", text)
    text = text.strip("-")
    text = text.replace("-", "_")
    return text or "unknown"


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def generate_pages(json_path, detail_tpl_path, list_tpl_path, output_dir):
    raw_data = load_json(json_path)

    # Підтримка формату: list з dict, де є 'data' або без
    entries = []
    for entry in raw_data:
        if isinstance(entry, dict) and "data" in entry:
            entries.append(entry["data"])
        elif isinstance(entry, dict):
            entries.append(entry)
        else:
            # ігноруємо не dict елементи
            continue

    # Jinja2 env
    detail_dir, detail_file = os.path.split(detail_tpl_path)
    list_dir, list_file = os.path.split(list_tpl_path)
    # Якщо шаблони у різних папках — можна передавати кілька шляхів
    env = Environment(loader=FileSystemLoader([detail_dir or ".", list_dir or "."]))

    detail_tpl = env.get_template(detail_file)
    list_tpl = env.get_template(list_file)

    os.makedirs(output_dir, exist_ok=True)

    listing = []
    for item in entries:
        # Використовуємо eng назву або rus як fallback
        name_eng = (
            item.get("name", {}).get("eng")
            or item.get("name", {}).get("rus")
            or "unknown"
        )
        filename = slugify(name_eng) + ".html"
        item["filename"] = filename
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(detail_tpl.render(item=item))
        listing.append(item)

    index_path = os.path.join(output_dir, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(list_tpl.render(items=listing))


def main():
    parser = argparse.ArgumentParser(
        description="Generate static pages from JSON + Jinja2 templates"
    )
    parser.add_argument("json_path", help="Path to input JSON file")
    parser.add_argument("detail_tpl", help="Path to Jinja2 detail template")
    parser.add_argument("list_tpl", help="Path to Jinja2 listing template")
    parser.add_argument("output_dir", help="Output directory for generated pages")
    args = parser.parse_args()

    generate_pages(args.json_path, args.detail_tpl, args.list_tpl, args.output_dir)


if __name__ == "__main__":
    main()
