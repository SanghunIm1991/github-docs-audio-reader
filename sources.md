# 原稿にするリポジトリ

聞くための原稿にしてよいリポジトリの一覧です。ユーザーが選んで登録し、Claude Code はこの一覧から、原稿を作る候補を提案します（手順は `CLAUDE.md`）。候補の洗い出しには `tools/list_candidates.py` を使い、このファイルの表を読み込みます。

- 登録してよいのは、公開リポジトリだけです。
- 「対象」と「除外」には、リポジトリの中のパスのパターンを、`` ` `` で囲んで書きます（`**` は0個以上のフォルダ）。除外は、共通の除外とあわせて効きます。
- ライセンスは、登録したときに各リポジトリの LICENSE を読んで書いたものです。原稿を作るときは、そのときの LICENSE を改めて確かめます。
- MIT の部分を原稿にするときは、出典の節に、LICENSE の著作権表示と許諾の文の全文を入れます（MIT が、複製物にこの2つを含めるよう求めているため）。著作権者は、LICENSE の表記（例: 「〜 contributors」）のとおりに書きます。Apache-2.0 のコードを原稿に写すときも、ライセンスの全文の所在と、写したことを書きます。

## 共通の除外

作業の記録や、リポジトリの運用のための文書は、原稿にしません。

`**/CLAUDE.md` `LICENSE*` `CHANGELOG.md` `docs/qa_log.md` `docs/idea_origin.md` `docs/handoff.md` `docs/review_log.md` `docs/public_release_review.md` `**/archive/**`

## リポジトリ

| リポジトリ | 対象 | 除外 | ライセンス（登録時に確認） | メモ |
|---|---|---|---|---|
| physical-ai-info-repo | `**/*.md` | `templates/**` `docs/research_procedure.md` | CC BY 4.0 | 2026-10-18 登録 |
| gymnasium-rl-textbook | `**/*.md` | | 文章と図は CC BY 4.0、コード（コードブロックを含む）は MIT | 2026-10-18 登録 |
| statistics-certification-study | `**/*.md` | | 文章と図は CC BY 4.0、コード（文書中のコードの例を含む）は MIT | 2026-10-18 登録。Notebook（`.ipynb`）は今は対象にしていない。著作権者の表記は「statistics-certification-study contributors」 |
| ros2MinimalPhysicalAi | `**/*.md` | | 文章と図は CC BY 4.0、保存するためのコードとコマンドは Apache-2.0 | 2026-10-18 登録。ROS 2 の公式ドキュメント等から引用した部分があり、LICENSE の「第三者の著作物」に一覧がある |
| mathworks-resource-guide | `**/*.md` | | このリポジトリのために書いた文章は CC BY 4.0 | 2026-10-18 登録。リンク先の資料（主に The MathWorks, Inc.）はライセンスの対象外なので、原稿にはその中身を入れない |
| learn-playwright-dotnet | `**/*.md` | `docs/traceability_matrix.md` | MIT（文章を含むリポジトリ全体） | 2026-10-18 登録。文章も MIT なので、どの原稿にも、出典の節に MIT の著作権表示と許諾の文の全文を入れる。著作権者の表記は「learn-playwright-dotnet contributors」 |
