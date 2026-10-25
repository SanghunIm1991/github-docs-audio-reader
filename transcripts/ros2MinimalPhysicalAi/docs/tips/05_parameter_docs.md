<!--
聞くための原稿（読み上げでは読まれない記録）
原文: SanghunIm1991/ros2MinimalPhysicalAi の main ブランチの docs/tips.md のうち、5節（パラメータを利用者に知らせる方法）。あわせて、冒頭の説明、項目の一覧の5節の行、期待する結果の出どころと出どころのうち5節に関わる部分、15節の出典の注記のうち全体に関わる部分（15節の参考資料には、5節を名指ししたものはない）
原文のコミット: 56e5e3044ad955d0b57c9300d1f03f2306cc64ae（2026-10-17）
作成: 2026-10-25、Claude Code が手作業で作成（原稿化スキルはまだない）
原文のライセンス: 文章は CC BY 4.0、コードとコマンドは Apache-2.0（それぞれ LICENSE の2と1）。5-3節の期待する結果の、turtlesim のパラメータの説明文は turtlesim（ros_tutorials、BSD License）のもの。LICENSE の「第三者の著作物」にある tips.md の引用は、5節には含まれない。この原稿は、原文を聞くために要約・意訳したもの（改変あり）
方針: Tips集は、テーマごとに docs/tips/ に番号を付けて分ける（2026-10-19 にユーザーが決定）。1つのテーマだけを聞いても分かるよう、頭に Tips集の冒頭の説明と、このテーマの関係する手順書・出どころを置く（01_use_sim_time.md と同じ形）。15節の参考資料の1つ目〈ros2 param のコマンドのページ〉は、原文の括弧の説明が use_sim_time の扱いなので 01 の原稿に置き、この原稿には参考資料の節を置かなかった。15節の出典の注記のうち全体に関わる部分は、冒頭の出どころの同じ趣旨の文と重なるので、出どころの段落で1回だけ読んだ。英語の略語や製品名、パラメータ・クラス・項目・パッケージの名前、短いコマンドは原文の表記のまま書く。オプションの - は「マイナス」と読む。5-3節の期待する結果（ros2 param の表示）は写さず、表示ごとに骨組みと値を1回だけ読み、原文の箇条書きの説明では、値を読み直さずに「どの行か」で指した。turtlesim の英語の説明文と、範囲の外の値のエラーの英文は、写さずに意味を言った。表（ParameterDescriptor の項目、使い分けの目安）は、行と列の数を言い、行ごとに全部読んだ。文字数の上限は設けない
省いたもの: URL、リンク先のファイル名、冒頭の対象のうち14節の SB3 の版、期待する結果の出どころと出どころのうち、ほかの節に関わる部分、項目の一覧のほかの節の行、15節の参考資料と、その確認状況、15節の出典の注記のうち、ほかの節に関わる部分、5-3節の表示の先頭のドル記号と、表示の細部の英文（説明文とエラーの英文。意味は読んだ）、5-2節のコマンドの後の空白（ノード名まで打つ、と言った）、5-2節の ros2 run の書き方の、マイナス p の後の省略の記号、5-3節の list の表示の qos_overrides の名前の書き方（QoS の上書きの設定と、トピック名と項目の名前で言い換えた）
-->

# Tips集 5: パラメータを利用者に知らせる方法（聞くための原稿）

これは、ros2MinimalPhysicalAi という教材の、Tips集の5つ目の項目です。

Tips集は、手順書、つまりフェーズの本文に入れると流れが途切れる、分量の少ない補足をまとめた資料です。どの項目も独立しているので、関係する手順書を読んでいるときや、疑問を持ったときに、その項目だけを読めばよい、とあります。

対象は、ROS2 Jazzy と Ubuntu 24.04 です。版に依存する記述は、この資料を作ったときに、/opt/ros/jazzy と Ubuntu のパッケージに入っていたもので確かめた、とあります。所要の目安は、1項目あたり5 から15分の読み物です。

この項目に関係する手順書は、フェーズ3-3 のパラメータと、フェーズ4 の launch です。

出どころについて、断りがあります。この資料の内容は、/opt/ros/jazzy のソースなどを読んで確かめ、自分の言葉で書いたもので、ソースやドキュメントの転載ではない、とあります。5節は、/opt/ros/jazzy の ros2param、ros2run、ros2cli のソース、つまり補完の仕組みと、turtlesim のプログラムを読み、手順書を作ったときに turtlesim を起動して、5-3節の ros2 param の表示を確かめた、とあります。ただし、Tab キーでの補完の表示は確かめていない、とあります。5-4節の generate_parameter_library は、Jazzy 向けの apt のパッケージがあることだけを確かめ、機能の説明は、このライブラリについての一般的な情報から書いた、とあります。この環境には導入しておらず、動かしていません。

この原稿では、コマンドの表示を書き写さずに、何が表示されるかを言葉で説明します。

## 5. パラメータを利用者に知らせる方法

### 5-1. 困りごと: 起動するまで一覧が分からない

作ったノードを人に渡すとき、どんなパラメータがあり、どんな値を入れてよいかを、どう伝えるか。ソースコードを読んでもらうか、実際に動かして試してもらうのでは、不便です。ros2 run に、パッケージと実行ファイル、マイナス2つの ros-args、マイナス p、名前、コロンとイコール、値、と打つときに、Tab キーでパラメータの名前の候補が出ることもありません。

これは、ROS2 のパラメータが、ノードが起動して declare_parameter を呼んだ時点で、初めて決まる仕組みだからです。実行ファイルを起動しないまま、そのパラメータの一覧を取り出す標準の方法はありません。そこで実務では、起動中のノードに問い合わせる方法と、起動しなくても分かるように、別の形で知らせる方法を、組み合わせます。

### 5-2. 起動中のノードに問い合わせる

ノードが動いていれば、ros2 param list に、スラッシュとノード名を付けると、一覧が分かります。ros2 param describe に、スラッシュとノード名と、パラメータの名前を付けると、型、説明、値の制約が分かります。これは、フェーズ3-3 の5-3節で扱いました。

describe に説明や値の範囲を出すには、ノードの側で、declare_parameter の引数に、ParameterDescriptor、つまりパラメータの説明書きを渡しておきます。主に設定できるのは、次の項目です。範囲を付けておくと、範囲の外の値を設定しようとしたときに、自動で拒否されます。

表は2列で4行です。列は、項目と、その中身です。

1行目は description で、説明文です。

2行目は read_only で、起動した後は変えられないようにするかです。

3行目は integer_range と floating_point_range で、整数と小数の値の範囲です。最小、最大、刻みを決めます。

4行目は additional_constraints で、範囲では表せない制約を、文章で書きます。

自分のノードに付ける練習は、フェーズ3-3 の5-4節の末尾にある、発展の課題6 で行えます。ParameterDescriptor に、説明文と FloatingPointRange を付ける課題です。

起動中のノードに対しては、Tab キーでの補完も効きます。ros2 param get や ros2 param describe に、/turtlesim のようなノード名まで打って Tab キーを押すと、そのノードに問い合わせて、パラメータの名前の候補を出します。ros2 の補完は、source /opt/ros/jazzy/setup.bash で、自動的に有効になります。ros2cli のパッケージが、Python の補完のライブラリの argcomplete を登録するからです。一方、ros2 run は、実行ファイルの名前より後ろの引数、つまりマイナス2つの ros-args やマイナス p などを、補完しません。補完しようにも、起動する前のノードからは、パラメータの一覧を取れないからです。これは5-1節で説明したとおりです。

### 5-3. turtlesim で確かめる

turtlesim は、背景色のパラメータに、説明文と、0 から255 の値の範囲を付けています。フェーズ1 で使った ros2 param get と set に加えて、describe で説明と範囲を読み、範囲の外の値を入れてみます。

コマンドは、T1 が1つ、T2 が5つです。T1 で、ros2 run turtlesim turtlesim_node を起動します。T2 では、順に、ros2 param list /turtlesim、ros2 param describe /turtlesim background_r、ros2 param describe /turtlesim holonomic、ros2 param set /turtlesim background_r 300、ros2 param set /turtlesim background_r 150 を実行します。

期待する結果を、T2 の分について、コマンドごとに説明します。

list では、パラメータの名前が10個、1行に1つずつ、字下げして並びます。background_b、background_g、background_r、holonomic、QoS の上書きの設定の項目が4つ、start_type_description_service、use_sim_time です。QoS の上書きの設定の4つは、/parameter_events の publisher の、depth、durability、history、reliability です。

background_r の describe では、Parameter name の行の下に、Type、Description、Constraints の行が字下げして並び、Constraints の下に、さらに3行が続きます。Type は integer です。Description は、背景色の赤のチャンネル、という意味の英語の説明文です。Constraints の下の3行は、Min value が0、Max value が255、Step が1 です。

holonomic の describe でも、Parameter name、Type、Description、Constraints の行が並びます。Type は boolean です。Description は、true なら亀が holonomic になる、という意味の英語の説明文です。

300 の set では、失敗の1行が出ます。Setting parameter failed に続いて、background_r が整数の範囲に合わない、という意味の英語の文です。

150 の set では、成功の1行、Set parameter successful が出ます。

期待する結果についての説明は、4つです。

1つ目。background_r の Description の行が説明文で、Constraints の下の3行が値の範囲です。どちらも、ParameterDescriptor に書かれた内容です。

2つ目。holonomic は説明文だけを付けていて、範囲は付けていないので、Constraints の下が空になります。

3つ目。範囲の外の300 は拒否され、背景色は変わりません。範囲の中の150 は成功し、turtlesim のウィンドウの背景が、紫がかった色に変わります。

4つ目。ros2 param describe /turtlesim まで打って、Tab キーを2回押すと、background_b や background_g などの候補が並びます。T1 の turtlesim を止めると、候補は出なくなります。

### 5-4. 起動しなくても分かるようにする

利用者が起動する前に知りたい情報は、次のような形で知らせます。3つあります。最初の項目は、launch ファイル、つまり複数のノードをまとめて起動する設定のファイルを使うので、フェーズ4 の後に読むと分かりやすい、とあります。

1つ目は、launch の引数として見せることです。利用者に変えてほしい値を、launch ファイルの DeclareLaunchArgument に、説明と既定値を付けて宣言します。ros2 launch に、パッケージとファイル、マイナス2つの show-args を付けると、起動せずに、名前、説明、既定値の一覧を表示できます。これは、フェーズ4 の4-1節で扱いました。配布するときは、ノードを直接 ros2 run してもらうのではなく、launch ファイルを入口にするのが一般的な形だ、とあります。

2つ目は、既定値の YAML のファイルを同梱することです。すべてのパラメータと既定値を並べた YAML を、パッケージの config のフォルダに置き、コメントで、説明や範囲を書いておきます。利用者は、これを写して書き換えます。YAML での指定のしかたは、フェーズ3-3 の5-4節で扱いました。インストールしておけば、ros2 pkg prefix にパッケージを付けて示される場所の、share の、パッケージの名前の、config のフォルダで見つけられます。

3つ目は、定義ファイルから、コードと説明書を作ることです。外部のライブラリの generate_parameter_library を使います。PickNik 社の OSS で、Jazzy 向けの apt のパッケージは、ros-jazzy-generate-parameter-library です。これを使うと、パラメータの名前、型、既定値、説明、制約を、YAML に1回書くだけで、宣言と値の検査をする C++ と Python のコードと、Markdown などの説明書を、生成できます。コードと説明書の内容がずれないのが利点で、ros2_control などが採用している、とあります。

### 5-5. 使い分けの目安

使い分けの表は、3列で4行です。列は、方法と、起動しなくても分かるか、向いている場面、です。

1行目は、ParameterDescriptor と ros2 param describe です。起動しなくても分かるかは、分からない、で、起動中のノードに問い合わせます。向いている場面は、どのノードでも、まず付けておくことです。範囲の検査も兼ねます。

2行目は、launch の引数と、マイナス2つの show-args です。起動しなくても分かります。向いているのは、利用者に変えてほしい値が、少数に絞れるときです。

3行目は、既定値の YAML の同梱です。ファイルを読めば、起動しなくても分かります。向いているのは、パラメータが多く、まとめて書き換えてもらうときです。

4行目は、generate_parameter_library です。生成した説明書を読めば、起動しなくても分かります。向いているのは、パラメータが多く、説明書との食い違いを防ぎたいときです。

小さなパッケージなら、上の3つ、つまり ParameterDescriptor、launch の引数、YAML で足りる、とあります。

## 出典について

この原稿は、SanghunIm1991 さんの [ros2MinimalPhysicalAi の「Tips集: 手順書の本文に入れなかった小さな補足」](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/docs/tips.md)のうち、5節を、聞くために要約・意訳したものです。元にしたのは、[2026年10月17日の版](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/56e5e3044ad955d0b57c9300d1f03f2306cc64ae/docs/tips.md)です。原文の文章と同じく、[クリエイティブ・コモンズ 表示 4.0 国際ライセンス](https://creativecommons.org/licenses/by/4.0/deed.ja)で提供します。

原稿の中に原文の表記のまま書いたコマンドと、コードの関数やクラスの名前は、原文では [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0) の対象です。ライセンスの全文は、原文のリポジトリの [LICENSE-APACHE-2.0](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/LICENSE-APACHE-2.0) にあります。

原文の5-3節の期待する結果にある、パラメータの説明文は、[turtlesim](https://github.com/ros/ros_tutorials/tree/jazzy/turtlesim)（BSD License）のプログラムが付けているものです。この原稿では、その英文を写さず、意味を言葉で説明しました。表示の例は、各ツールの表示を言葉で説明したものです。
