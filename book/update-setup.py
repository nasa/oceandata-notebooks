import argparse
import re
import sys
from pathlib import Path

import tomlkit


def main(reqs: Path, script: Path) -> None:
    with reqs.open() as f:
        pkgs = f.read()
    comment = re.compile(r"^\s*#")
    pkgs = [i for i in pkgs.splitlines() if not comment.match(i)]
    with script.open() as f:
        content = f.read()
    toml, body = parse(content)
    toml["dependencies"] = tomlkit.array(pkgs).multiline(True)
    head = "\n# ".join(tomlkit.dumps(toml).splitlines())
    with script.open("w") as f:
        f.write("".join(("# /// script\n# ", head, "\n# ///", body)))


def parse(script: str) -> dict:
    head = r"(?m)^# /// (?P<type>[a-zA-Z0-9-]+)$\s(?P<content>(^#(| .*)$\s)+)^# ///$"
    match = re.match(head, script)
    toml = [i[2:] for i in match.group("content").splitlines()]
    return tomlkit.loads("\n".join(toml)), script[slice(match.end(), None)]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Injects dependencies as inline pyproject metadata.",
    )
    parser.add_argument("reqs", help="file listing requirements (PEP 508)", type=Path)
    parser.add_argument("-o", dest="script", help="target to modify", type=Path)
    args = parser.parse_args()
    sys.exit(main(**vars(args)))
