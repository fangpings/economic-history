#!/usr/bin/env python3
"""Inventory and local-link checks; explicitly not a content or fact audit."""
import argparse
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
HAN = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\U00020000-\U0002fa1f]")
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^\s)]+)(?:\s+\"[^\"]*\")?\)")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, help="Write inventory to this path")
    parser.add_argument("--require-complete", action="store_true",
                        help="Fail for missing or short chapters as well as structural errors")
    args = parser.parse_args()
    plan = json.loads((ROOT / "curriculum.json").read_text())
    rows, errors, pending_links = [], [], []
    planned_paths = {(ROOT / "textbook" / c["file"]).resolve() for c in plan["chapters"]}
    for chapter in plan["chapters"]:
        path = ROOT / "textbook" / chapter["file"]
        exists = path.is_file()
        content = path.read_text() if exists else ""
        # Exclude exercise/reference sections, retaining later prose and capstones.
        # Chapter 06 places its comparative capstone after its exercises.
        excluded_heading = re.compile(
            r"^##\s+(?:[一二三四五六七八九十百零〇0-9]+[.、．：: ]+)?"
            r"(?:本章)?(?:练习|推理练习|思考题|理解与迁移|章末|参考资料|参考文献|资料来源)"
        )
        sections = re.split(r"(?m)(?=^## )", content)
        body = "".join(section for section in sections
                       if not excluded_heading.match(section))
        body = re.sub(r"```.*?```", "", body, flags=re.S)
        row = {"number": chapter["number"], "part": chapter["part"],
               "file": chapter["file"], "exists": exists,
               "body_han_estimate": len(HAN.findall(body)),
               "whole_chapter_han": len(HAN.findall(content)),
               "external_links": len(re.findall(r"\]\(https?://", content)),
               "headings": len(re.findall(r"(?m)^## ", content))}
        rows.append(row)
        if exists:
            if not content.startswith("# "):
                errors.append(f"{path.name}: missing title")
            if content.count("```") % 2:
                errors.append(f"{path.name}: unbalanced fenced code block")
            if content.count("<details>") != content.count("</details>"):
                errors.append(f"{path.name}: unbalanced details elements")
            for target in LINK.findall(content):
                if target.startswith(("http:", "https:", "mailto:", "#", "data:")):
                    continue
                local = unquote(urlsplit(target.strip("<>")).path)
                if local and not (path.parent / local).exists():
                    message = f"{path.name}: missing local target {local}"
                    if (path.parent / local).resolve() in planned_paths:
                        pending_links.append(message)
                    else:
                        errors.append(message)
    missing = [r["file"] for r in rows if not r["exists"]]
    short = [r["file"] for r in rows if r["exists"] and r["body_han_estimate"] < 8000]
    report = {"warning": "Counts and structure do not prove historical accuracy or editorial completion. "
              "Body counts are estimates; headings must be checked before final acceptance.",
              "chapters_planned": len(rows), "chapters_present": len(rows)-len(missing),
              "body_han_estimate": sum(r["body_han_estimate"] for r in rows),
              "whole_chapter_han": sum(r["whole_chapter_han"] for r in rows),
              "missing": missing, "below_planned_depth_length": short,
              "structural_errors": errors, "planned_but_unwritten_links": pending_links,
              "chapters": rows}
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n")
    print(f"Chapters present: {report['chapters_present']}/{len(rows)}")
    print(f"Body Han estimate: {report['body_han_estimate']:,}; whole chapters: {report['whole_chapter_han']:,}")
    print(f"Missing: {len(missing)}; below planned length: {len(short)}; structural errors: {len(errors)}")
    print(f"Links to planned but unwritten chapters: {len(pending_links)}")
    for error in errors:
        print(error)
    print(report["warning"])
    return int(bool(errors or (args.require_complete and (missing or short or pending_links))))


if __name__ == "__main__":
    raise SystemExit(main())
