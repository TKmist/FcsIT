from pathlib import Path
import json
import shutil
import re


ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()

SRC = ROOT / "docs" / "_build" / "html"
DST = ROOT / "src" / "doc" / "assets" / "help_html"

README = ROOT / "README.md"
NOTEBOOK = ROOT / "docs" / "Main_title.ipynb"

VERSION_BADGE_PATTERN = r"version-[^-]+(?:-[^-]+)*-green"


def update_version_badge_in_text(text: str, version: str | None = None) -> str:
    version = version or VERSION
    return re.sub(
        VERSION_BADGE_PATTERN,
        f"version-{version}-green",
        text,
    )


def update_readme(readme_path: Path = README, version: str | None = None) -> bool:
    version = version or VERSION
    text = readme_path.read_text(encoding="utf-8")
    new_text = update_version_badge_in_text(text, version)

    if new_text != text:
        readme_path.write_text(new_text, encoding="utf-8")
        print(f"Updated: {readme_path}")
        return True

    print(f"No changes: {readme_path}")
    return False


def update_notebook(nb_path: Path = NOTEBOOK, version: str | None = None) -> bool:
    version = version or VERSION
    data = json.loads(nb_path.read_text(encoding="utf-8"))
    changed = False

    for cell in data.get("cells", []):
        source = cell.get("source")

        if isinstance(source, list):
            new_source = []
            for line in source:
                new_line = update_version_badge_in_text(line, version)
                if new_line != line:
                    changed = True
                new_source.append(new_line)
            cell["source"] = new_source

        elif isinstance(source, str):
            new_source = update_version_badge_in_text(source, version)
            if new_source != source:
                changed = True
            cell["source"] = new_source

    if changed:
        nb_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8",
        )
        print(f"Updated: {nb_path}")
        return True

    print(f"No changes: {nb_path}")
    return False


def copy_help(src: Path = SRC, dst: Path = DST) -> None:
    if not src.exists():
        raise FileNotFoundError(f"HTML build directory does not exist: {src}")

    if dst.exists():
        shutil.rmtree(dst)

    shutil.copytree(src, dst)
    print(f"Copied: {src} -> {dst}")


# if __name__ == "__main__":
#     nbp = ROOT / "docs" / "Main_title.ipynb"
    
#     update_readme()
#     update_notebook(nbp)
#     copy_help()
