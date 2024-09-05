"""Convert a pile of Markdown files to HTML."""

import argparse
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
from markdown import markdown
from pathlib import Path


MARKDOWN_EXTENSIONS = ["attr_list", "def_list", "fenced_code", "md_in_html", "tables"]
SUFFIXES_BIN = {".ico", ".jpg", ".png"}
SUFFIXES_SRC = {".css", ".html", ".js", ".md", ".py", ".sh", ".txt"}
SUFFIXES_TXT = SUFFIXES_SRC | {".csv", ".json", ".svg"}
SUFFIXES = SUFFIXES_BIN | SUFFIXES_TXT

RENAMES = {
    "CODE_OF_CONDUCT.md": "code_of_conduct.md",
    "CONTRIBUTING.md": "contributing.md",
    "LICENSE.md": "license.md",
    "README.md": "index.md",
}


def main():
    """Main driver."""
    opt = parse_args()

    env = Environment(loader=FileSystemLoader(opt.templates))
    skips = {opt.out, opt.templates}

    files = find_files(opt, skips)
    for filepath, content in files.items():
        if filepath.suffix == ".md":
            render_markdown(env, opt.out, filepath, content)
        else:
            copy_file(opt.out, filepath, content)


def copy_file(output_dir, source_path, content):
    """Copy a file verbatim."""
    output_path = make_output_path(output_dir, source_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_file(output_path, content)


def do_markdown_links(doc, source_path):
    """Fix .md links in HTML."""
    for node in doc.select("a[href]"):
        if node["href"].endswith(".md"):
            node["href"] = node["href"].replace(".md", ".html").lower()


def do_root_path_prefix(doc, source_path):
    """Fix @root links in HTML."""
    depth = len(source_path.parents) - 1
    prefix = "./" if (depth == 0) else "../" * depth
    targets = (
        ("a[href]", "href"),
        ("link[href]", "href"),
        ("script[src]", "src"),
    )
    for selector, attr in targets:
        for node in doc.select(selector):
            if "@root/" in node[attr]:
                node[attr] = node[attr].replace("@root/", prefix)


def do_title(doc, source_path):
    """Make sure title element is filled in."""
    doc.title.string = doc.h1.get_text()


def find_files(opt, skips=None):
    """Collect all interesting files."""
    return {
        filepath: read_file(filepath)
        for filepath in Path(opt.root).glob("**/*.*")
        if is_interesting_file(filepath, skips)
    }


def is_interesting_file(filepath, skips):
    """Is this file worth checking?"""
    if not filepath.is_file():
        return False
    if str(filepath).startswith("."):
        return False
    if filepath.suffix not in SUFFIXES:
        return False
    if str(filepath.parent.name).startswith("."):
        return False
    if (skips is not None) and any(str(filepath).startswith(s) for s in skips):
        return False
    return True


def make_output_path(output_dir, source_path):
    """Build output path."""
    if source_path.name in RENAMES:
        source_path = Path(source_path.parent, RENAMES[source_path.name])
    source_path = Path(str(source_path).replace(".md", ".html"))
    return Path(output_dir, source_path)


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=str, default="docs", help="output directory")
    parser.add_argument("--root", type=str, default=".", help="root directory")
    parser.add_argument("--templates", type=str, default="templates", help="templates directory")
    return parser.parse_args()


def read_file(filepath):
    """Read file as bytes or text."""
    if filepath.suffix in SUFFIXES_TXT:
        return filepath.read_text()
    else:
        return filepath.read_bytes()


def render_markdown(env, output_dir, source_path, content):
    """Convert Markdown to HTML."""
    html = markdown(content, extensions=MARKDOWN_EXTENSIONS)
    template = env.get_template("page.html")
    html = template.render(content=html)

    transformers = (
        do_markdown_links,
        do_title,
        do_root_path_prefix, # must be last
    )
    doc = BeautifulSoup(html, "html.parser")
    for func in transformers:
        func(doc, source_path)

    output_path = make_output_path(output_dir, source_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(str(doc))


def write_file(filepath, content):
    """Write file as bytes or text."""
    if filepath.suffix in SUFFIXES_TXT:
        return filepath.write_text(content)
    else:
        return filepath.write_bytes(content)


if __name__ == "__main__":
    main()
