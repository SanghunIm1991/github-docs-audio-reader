"""sources.md に登録したリポジトリから、聞くための原稿を作る候補を洗い出す。

- 手元に複製した各リポジトリの、対象のファイル（sources.md の「対象」から「除外」を除いたもの）を、
  原稿の有無と原文の更新で「未作成」「原文が更新」「最新」に分ける。
- 言葉にする手間と価値の目安として、図（mermaid・画像）・コードブロック・表・文字数を数える。
- 原文が消えた原稿があれば、それも示す。
- 標準ライブラリと git だけを使う。通信はしない（複製と更新は、実行する前に済ませておく）。

使い方: py -3.13 tools/list_candidates.py --clones <複製を置いたフォルダ>
  複製は <複製を置いたフォルダ>/<リポジトリ名> に置く。
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "sources.md"
TRANSCRIPTS = ROOT / "transcripts"

PATTERN = re.compile(r"`([^`]+)`")
COMMIT = re.compile(r"原文のコミット:\s*([0-9a-f]{7,40})")
STATUS_ORDER = ["判定できない", "原文が更新", "未作成", "最新"]


def read_sources():
    """sources.md から、共通の除外と、リポジトリごとの対象・除外を読む。"""
    common, repos, section = [], [], None
    for line in SOURCES.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
        elif section == "共通の除外" and line.startswith("`"):
            common += PATTERN.findall(line)
        elif section == "リポジトリ" and line.startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            # 見出しの行・区切りの行・列が足りない行は飛ばす（セルの中に「|」は書かない決まり）
            if len(cells) < 3 or cells[0] in ("リポジトリ", "") or set(cells[0]) <= set("-"):
                continue
            repos.append((cells[0], PATTERN.findall(cells[1]), PATTERN.findall(cells[2])))
    return common, repos


def git(repo_dir, *args):
    return subprocess.run(["git", "-C", str(repo_dir), *args],
                          capture_output=True, text=True, encoding="utf-8", check=True).stdout


def matches(path, patterns):
    p = PurePosixPath(path)
    return any(p.full_match(pat) for pat in patterns)


def measure(text):
    """図・コードブロック・表・文字数を数える。"""
    fences = re.findall(r"^\s*```\s*(\S*)", text, flags=re.M)[::2]  # 開きの行だけ
    mermaid = sum(1 for lang in fences if lang == "mermaid")
    return {
        "図": mermaid + len(re.findall(r"!\[[^\]]*\]\(", text)) + len(re.findall(r"<img\s", text)),
        "コード": len(fences) - mermaid,
        "表": len(re.findall(r"^\s*\|[\s:|-]*-[\s:|-]*\|\s*$", text, flags=re.M)),
        "文字": len(text),
    }


def classify(repo, repo_dir, path):
    transcript = TRANSCRIPTS / repo / path
    if not transcript.exists():
        return "未作成", ""
    m = COMMIT.search(transcript.read_text(encoding="utf-8"))
    if not m:
        return "原文が更新", "原稿に原文のコミットの記録がない"
    recorded = m.group(1)
    # 記録したコミットからの差分が無ければ、原稿は原文に追いついている
    changed = subprocess.run(["git", "-C", str(repo_dir), "diff", "--quiet", recorded, "HEAD", "--", path],
                             capture_output=True)
    if changed.returncode == 0:
        return "最新", ""
    if changed.returncode != 1:  # 1 は差分あり。それ以外は、記録したコミットが複製に無い等のエラー
        return "判定できない", f"記録したコミット {recorded[:7]} が複製に見つからない（浅い複製なら、深く複製し直す）"
    latest = git(repo_dir, "log", "-1", "--format=%h %cs", "--", path).strip()
    return "原文が更新", f"原稿は {recorded[:7]}、原文の最新は {latest}"


def main():
    # Windows の既定（cp932）だと文字化けするため。--help やエラーの表示にも効くよう、最初に切り替える
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    if sys.version_info < (3, 13):
        raise SystemExit("Python 3.13 以上で実行してください（PurePosixPath.full_match を使うため）: py -3.13 tools/list_candidates.py")
    parser = argparse.ArgumentParser(description="原稿を作る候補を洗い出す")
    parser.add_argument("--clones", required=True, type=Path, help="各リポジトリを複製したフォルダ")
    args = parser.parse_args()

    common, repos = read_sources()
    for repo, include, exclude in repos:
        repo_dir = args.clones / repo
        print(f"## {repo}")
        if not (repo_dir / ".git").exists():
            print(f"（複製が見つかりません: {repo_dir}）\n")
            continue
        head = git(repo_dir, "log", "-1", "--format=%h %cs").strip()
        print(f"原文の HEAD: {head}")
        # 日本語のファイル名が引用符と8進数の形にならないよう、quotePath を切り、区切りを NUL にする
        listed = git(repo_dir, "-c", "core.quotePath=false", "ls-files", "-z").split("\0")
        files = [f for f in listed if f and matches(f, include) and not matches(f, common + exclude)]
        rows = []
        for f in files:
            status, note = classify(repo, repo_dir, f)
            text = (repo_dir / f).read_text(encoding="utf-8", errors="replace")
            rows.append((STATUS_ORDER.index(status), f, status, measure(text), note))
        print("| 状態 | ファイル | 図 | コード | 表 | 文字 | 備考 |")
        print("|---|---|---|---|---|---|---|")
        for _, f, status, n, note in sorted(rows):
            print(f"| {status} | {f} | {n['図']} | {n['コード']} | {n['表']} | {n['文字']} | {note} |")
        # 原文が消えた（または対象から外れた）原稿
        targets = set(files)
        for t in sorted((TRANSCRIPTS / repo).rglob("*.md")) if (TRANSCRIPTS / repo).exists() else []:
            rel = t.relative_to(TRANSCRIPTS / repo).as_posix()
            if rel not in targets:
                print(f"| 原文なし | {rel} | | | | | 原文が消えたか、対象から外れた |")
        print()


if __name__ == "__main__":
    main()
