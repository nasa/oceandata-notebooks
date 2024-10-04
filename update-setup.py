from pathlib import Path
import re
import sys

import tomlkit


def main(req: str) -> None:
    comment = re.compile(r"^\s*#")
    req = Path(req)
    out = req.parent / "setup.py"
    with req.open() as f:
        pkgs = f.read()
    pkgs = [i for i in pkgs.splitlines() if not comment.match(i)]
    with out.open() as f:
        content = f.read()
    toml, body = parse(content)
    toml["dependencies"] = tomlkit.array(pkgs).multiline(True)
    head = "\n# ".join(tomlkit.dumps(toml).splitlines())
    with out.open("w") as f:
        f.write("".join(("# /// script\n# ", head, "\n# ///", body)))


def parse(script: str) -> dict:
    head = r"(?m)^# /// (?P<type>[a-zA-Z0-9-]+)$\s(?P<content>(^#(| .*)$\s)+)^# ///$"
    match = re.match(head, script)
    toml = [i[2:] for i in match.group("content").splitlines()]
    return tomlkit.loads("\n".join(toml)), script[slice(match.end(), None)]


if __name__ == "__main__":
    main(*sys.argv[1:])
