"""聞くための原稿（transcripts/ の .md）から、コピペ用の素のテキスト（plain/ の .txt）を作る。

- 先頭のHTMLコメント（記録）を除き、見出しの「#」、強調の「**」、箇条書きの記号、リンクの URL を外す。
- 原稿ごとに、全文の1ファイルを作る。見出しには、読み上げで区切れるように「。」を足す。
- --max-chars を付けたときだけ、その文字数以下に分けたファイル（-01, -02, ...）も作る。
  全文が上限に収まるときは、分けたファイルは作らない。
- 出典は、全文と各パートの末尾に入れる（CC BY 4.0 の表示のため）。URL は全文の末尾の記録の欄にだけ書く。

使い方: py -3.13 tools/make_plain.py [--max-chars 3000]
標準ライブラリだけを使い、外部との通信はしない。plain/ の中の .txt は毎回作り直す。
"""

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "transcripts"
OUT = ROOT / "plain"

LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
SOURCE_HEADING = "出典について"
URL_NOTE = "（ここから下は、出典の記録です。読み上げは要りません）"
HEADINGS = set()


def to_blocks(md):
    """Markdown を、空行で区切った段落の並びにする。見出しは「#」を外し、HEADINGS に覚えておく。"""
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    blocks = []
    for raw in re.split(r"\n\s*\n", md.strip()):
        if raw.lstrip().startswith("#"):
            HEADINGS.add(re.sub(r"^#+\s*", "", raw.strip()))
        lines = []
        for line in raw.splitlines():
            if line.lstrip().startswith("#"):
                # 見出しの番号（「1. 」等）は箇条書きの記号として外さない
                line = re.sub(r"^\s*#+\s*", "", line)
            else:
                line = re.sub(r"^\s*(?:[-*]|\d+\.)\s+", "", line)
            line = line.replace("**", "")
            lines.append(line.strip())
        text = "\n".join(l for l in lines if l)
        if text:
            blocks.append(text)
    return blocks


def split_source(blocks):
    """本文・題名・出典の段落（リンクの文字だけ）・出典の URL に分ける。"""
    title = blocks[0].replace("（聞くための原稿）", "")
    idx = blocks.index(SOURCE_HEADING)
    body = blocks[1:idx]
    source_md = "\n\n".join(blocks[idx + 1:])
    source = LINK.sub(r"\1", source_md)
    urls = [m.group(2) for m in LINK.finditer(source_md)]
    return title, body, source, urls


def split_long(block, limit):
    """1段落が limit を超えるときは、文（「。」）の切れ目で分ける。"""
    if len(block) <= limit:
        return [block]
    pieces, cur = [], ""
    for sentence in re.findall(r"[^。]*。|[^。]+$", block):
        if cur and len(cur) + len(sentence) > limit:
            pieces.append(cur)
            cur = ""
        cur += sentence
    if cur:
        pieces.append(cur)
    return pieces


def pack(body, limit):
    """段落を、limit 以下のかたまりに詰める。見出しは、次の段落と同じかたまりに入れる。"""
    units, pending = [], None
    for block in body:
        if block in HEADINGS:
            pending = block
            continue
        for piece in split_long(block, limit):
            units.append(f"{pending}。\n\n{piece}" if pending else piece)
            pending = None
    if pending:
        units.append(pending)

    chunks, cur = [], ""
    for unit in units:
        if cur and len(cur) + 2 + len(unit) > limit:
            chunks.append(cur)
            cur = ""
        cur = f"{cur}\n\n{unit}" if cur else unit
    if cur:
        chunks.append(cur)
    return chunks


def build(md_path, max_chars):
    title, body, source, urls = split_source(to_blocks(md_path.read_text(encoding="utf-8")))
    rel = md_path.relative_to(SRC).with_suffix("")
    out_dir = OUT / rel.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    footer = f"出典について。{source}"
    written = []

    body_text = [f"{b}。" if b in HEADINGS else b for b in body]
    full = "\n\n".join([f"{title}。", *body_text, footer, URL_NOTE, "\n".join(urls)]) + "\n"
    full_path = out_dir / f"{rel.name}.txt"
    full_path.write_text(full, encoding="utf-8", newline="\n")
    written.append((full_path, len(full)))
    if max_chars is None:
        return written  # 文字数の上限を決めないときは、全文だけを作る

    # 各パートの見出し・続きの案内・出典のぶんを差し引いた文字数で、本文を分ける
    overhead = len(f"{title}（その00／全00）") + len("（その00に続きます）") + len(footer) + 8
    if max_chars <= overhead + 200:
        raise SystemExit(f"--max-chars が小さすぎます（{rel}: {overhead + 200} より大きくしてください）")
    chunks = pack(body, max_chars - overhead)
    total = len(chunks)
    if total == 1:
        return written  # 全文が上限に収まるときは、パートを作らない
    for i, chunk in enumerate(chunks, 1):
        parts = [f"{title}（その{i}／全{total}）", chunk]
        if i < total:
            parts.append(f"（その{i + 1}に続きます）")
        parts.append(footer)
        text = "\n\n".join(parts) + "\n"
        part_path = out_dir / f"{rel.name}-{i:02d}.txt"
        part_path.write_text(text, encoding="utf-8", newline="\n")
        written.append((part_path, len(text)))
    return written


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--max-chars", type=int, help="1パートの文字数の上限（付けないときは、パートを作らない）")
    args = parser.parse_args()

    for old in OUT.rglob("*.txt"):
        old.unlink()
    for md_path in sorted(SRC.rglob("*.md")):
        for path, n in build(md_path, args.max_chars):
            print(f"{path.relative_to(ROOT).as_posix()}\t{n}")


if __name__ == "__main__":
    main()
