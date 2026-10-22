<!--
聞くための原稿（読み上げでは読まれない記録）
原文: SanghunIm1991/ros2MinimalPhysicalAi の main ブランチの docs/phase4_launch.md（図は docs/img/phase4_overview.svg と docs/img/phase4_bringup_role.svg と docs/img/phase4_compose.svg）
原文のコミット: 6d6f7ab7206ed5a18d6de96d4ff31d8d53a510e7（2026-10-17）
作成: 2026-10-21、Claude Code が手作業で作成（原稿化スキルはまだない）
原文のライセンス: 文章と図は CC BY 4.0、コードとコマンドは Apache-2.0（それぞれ LICENSE の2と1）。原文の末尾に、API の使い方は公式チュートリアル（ROS 2 Documentation、CC BY 4.0）を参考にした、とある。この原稿は、原文を聞くために要約・意訳したもの（改変あり）
方針: 英語の略語や製品名、関数やクラスの名前、短いコマンドは原文の表記のまま書く。launch ファイル6本と、package.xml・CMakeLists.txt に足す行は、写さずに、ブロックの役割と要の行を言葉で説明した。期待する結果（ros2 pkg create、--show-args、--print、launch のログ、ros2 param get、ros2 node list、ros2 topic list、ros2 topic info の表示）も、何が表示されるかを言葉で説明した。図と表（パッケージとlaunchファイルの仕様、主な API、各部分の役割、Python と XML の対応、3形式の比較、まとめ、つまずきやすい点）は言葉で説明する。文字数の上限は設けない
省いたもの: URL、ログの時刻とプロセス番号とアドレスの数字、ログの置き場所のパス、ros2 pkg create のメンテナの名前とメールアドレス
-->

# フェーズ4: launch ファイルで複数のノードを束ねる（聞くための原稿）

これは、ros2MinimalPhysicalAi という教材の、フェーズ4 の手順書の話です。学習計画のフェーズ4、元のアイデアのステップ1 の1-6 にあたります。これまで別々のターミナルで起動していたノードを、1つの launch ファイルで起動します。要点は、Python の版と C++ の版のノードを、引数で切り替えることです。

想定する環境は、WSL2 と Ubuntu 24.04 と ROS2 Jazzy です。前提は、フェーズ3-1 から3-3 を終えていることです。learn_py と learn_cpp に、このフェーズで起動する talker、listener、param_talker、turtle_circle があるはずです。フェーズ3-4 と3-5 のノードは使わないので、その2つは概要をつかんだだけでも先へ進めます。C++ の版の param_talker と turtle_circle は、フェーズ3-2a と3-3 では任意だったので、作っていない場合は、lang:=cpp の代わりに lang:=py で起動します。一方、learn_cpp の talker と listener、つまりフェーズ3-1 のものは、4-1節の言語の切り替えで使うので必要です。所要時間の目安は1から2コマです。launch ファイルは、Python、XML、YAML の3つの形式を扱い、起動するノードは Python と C++ です。OSS は turtlesim を使い、GUI のウィンドウが開きます。

原文の進め方の囲みです。2節の仕様は、何を作るかの定義で、launch の API の使い方までは書いていません。まず各節の冒頭の、主な API の表で、そのファイルに要る API をつかみ、続くサンプルと解説を読んで理解します。分かったら、引数の既定値や起動するノードを変えるなど、手を動かして改造すると身に付きます。サンプルは、手順書を作るときに、ros2 launch の --print、つまり起動せずに中身を表示するオプションで、読み込めることまで確かめてあります。手順は2026年9月27日に実機で確かめています。ただし、4-6節の remap の部分、つまり2026年10月17日に足した param_listener は、--print で読み込めることまでを確かめ、実機では実行していません。出力が細部で違うときは、実機の表示を優先します。

期待する結果の出どころの囲みもあります。--show-args と --print の表示は、手順書を作るときに使い捨ての環境で実行して確かめたものです。ノードを起動した後の表示は、コードと ROS2 の仕様から筆者が想定したもので、実機で手順を実行して問題が無いことを確かめてありますが、表示を1つずつ見比べてはいません。ただし、4-6節の param_listener のログの行と、ros2 topic info の /param_chatter の表示は、想定したもので、実機では確かめていません。時刻やプロセス番号、つまり pid などの細部は、実行ごとに違います。4-1節の Ctrl+C の後の表示は、同じ main の書き方をした公式のサンプル、demo_nodes_py と demo_nodes_cpp の talker と、フェーズ5-3 のノードを、使い捨ての環境で launch から起動して確かめたものです。端末の Ctrl+C をまねて、プロセスのグループ全体に割り込みを送る方法で確かめた、とあります。

この原稿では、launch ファイルのコードを書き写さず、ブロックの役割と要の行を言葉で説明します。

## 0. 学習目標と完了の条件

完了の条件は5つです。

1つ目。launch のパッケージ、learn_bringup を作り、launch ファイルをインストールして、ros2 launch で起動できる。

2つ目。launch の引数、つまり DeclareLaunchArgument と LaunchConfiguration で、ノードの言語、Python の版と C++ の版を切り替えられる。

3つ目。4通りの組み合わせ、つまり Python と Python、Python と C++、C++ と Python、C++ と C++ を、引数だけで起動できる。

4つ目。パラメータ、つまり YAML のファイルと引数からの上書き、それから remap と namespace を、launch から指定できる。

5つ目。Python、XML、YAML の3つの形式の、書き方の違いを説明できる。

## 1. 全体像

図が3枚あります。

1枚目は、ros2 launch が2つのノードを同時に起動する図です。上に、薄い黄色の箱が1つあり、2行で、ros2 launch learn_bringup pubsub.launch.py と、talker_lang:=cpp listener_lang:=py と書いてあります。この箱から、下の2つの薄い青の箱へ、それぞれ実線の矢印が出ています。左の箱は、talker の C++ の版、右の箱は、listener の Python の版です。そして、talker から listener へ、/chatter というラベルの付いた実線の矢印があります。1つのコマンドで、言語の違う2つのノードを起動し、/chatter でつなぐ、という絵です。

2枚目は、launch のパッケージの役割の図です。launch のパッケージは、ノードを作らず、起動の設定だけを持ちます。左に、薄い黄色の箱で、learn_bringup、その下に小さく、launch フォルダと config フォルダだけ、と書いてあります。この箱から右へ、4本の矢印が出ています。3本は破線で、どれも、起動する、というラベルが付き、行き先は、薄い青の箱の learn_py のノード、同じく薄い青の箱の learn_cpp のノード、そして灰色の箱の turtlesim、OSS です。残りの1本は実線で、パラメータを渡す、というラベルが付き、行き先は灰色の箱の config/param_talker.yaml です。

3枚目は、launch ファイルの合成、つまり IncludeLaunchDescription の図です。4-6節で作る、書いた launch ファイルを部品として組み合わせる例です。図に出てくる IncludeLaunchDescription は、別の launch ファイルを呼び出すもの、GroupAction は、中の指定をまとめて効かせるもの、namespace は、ノード名やトピック名の前に demo を付けて住み分けるもの、remap は、起動するときにトピック名を付け替えるものです。使い方は4-6節で扱うので、ここでは、launch ファイルは組み合わせられる、ということだけつかめばよい、とあります。

図の左に、薄い黄色の箱で compose.launch.py があります。そこから実線の矢印が3本出ます。1本目は、薄い緑の箱の GroupAction へ向かい、その箱には、namespace イコール demo とも書いてあります。GroupAction の箱から、さらに実線の矢印が、薄い黄色の箱の pubsub.launch.py、include へ向かいます。2本目は、薄い黄色の箱の param.launch.py、include へ向かいます。3本目は、薄い青の箱へ向かい、その箱には、listener、ノード名は param_listener、そして remap で chatter を param_chatter に、と書いてあります。

## 2. 仕様

### 2-1. パッケージ

2列の表で、3行あります。

パッケージ名は learn_bringup です。ament_cmake で作る、ノードを持たない、launch と設定の専用のパッケージです。

置くものは、launch フォルダ、つまり launch ファイルと、config フォルダ、つまりパラメータの YAML です。

依存は、起動する相手の learn_py、learn_cpp、turtlesim と、launch、launch_ros、launch_xml、launch_yaml です。どれも実行時の依存、exec_depend として書きます。

### 2-2. launch ファイル

2列の表で、6行あります。

pubsub.launch.py は、talker と listener を起動します。引数 talker_lang と listener_lang で、それぞれの言語を選びます。値は py か cpp で、既定は py です。

pubsub.launch.xml は、同じ内容を XML の形式で書きます。

pubsub.launch.yaml は、同じ内容を YAML の形式で書きます。

param.launch.py は、param_talker を起動します。引数は lang、既定は py と、period、既定は1.0 です。パラメータは config の param_talker.yaml を読み、さらに引数 period で上書きします。

turtle.launch.py は、OSS の turtlesim_node と、turtle_circle を起動します。引数は lang、既定は py です。

compose.launch.py は、pubsub.launch.py を、talker_lang を cpp、listener_lang を py に固定して、名前空間 demo の下で include し、param.launch.py は、そのまま include します。さらに、Python の版の listener を、ノード名 param_listener で起動し、remap で chatter を param_chatter に付け替えて、param_talker の文字列を受け取ります。

## 3. 準備

### 3-1. パッケージを作る

ros2_ws の src に移り、ros2 pkg create で、ビルドの種類を ament_cmake、ライセンスを Apache-2.0 にして、learn_bringup を作ります。メンテナの名前とメールアドレスも、オプションで指定します。そのあと、mkdir で、learn_bringup の中に launch と config のフォルダを作ります。

期待する結果です。ros2 pkg create の表示は、フェーズ2 の2-3節、C++ のパッケージのときと同じ形です。--node-name を付けていないので、src の中に実行ファイルのひな形、つまりフェーズ2 の hello.cpp にあたるものは作られません。src と、include の learn_bringup は、空のフォルダとして作られます。--dependencies を付けていないので、依存は空と表示されます。mkdir は、成功しても何も表示しません。ls で learn_bringup の中を見ると、CMakeLists.txt、LICENSE、config、include、launch、package.xml、src が並びます。include と src は、ひな形が作る空のフォルダで、このパッケージでは使いません。

次に、フェーズ3-3 で ros2_ws の config に作ったパラメータの YAML、param_talker.yaml を、mv で、このパッケージの config へ移します。mv は成功しても何も表示しないので、ls で learn_bringup の config を見て、param_talker.yaml が見えれば移っています。ros2_ws の config が空になったら、rmdir で消してよい、とあります。

### 3-2. package.xml に依存を足す

learn_bringup の package.xml の、buildtool_depend の次あたりに、実行時の依存を7行足します。exec_depend のタグで、learn_py、learn_cpp、turtlesim、launch、launch_ros、launch_xml、launch_yaml を1行ずつ書きます。

なぜ depend でなく exec_depend にするのか、の説明があります。フェーズ3-2a の3節のとおり、depend は、ビルド時と実行時の両方の依存をまとめて宣言する書き方です。package.xml の書き方の規則、REP 149 では、ビルド時の依存の build_depend、このパッケージを使う側のビルドに要る依存の build_export_depend、実行時の依存の exec_depend の3つを、同時に書いたのと同じ、と決めています。learn_bringup は、C++ や Python のコードを持たず、launch ファイルと YAML をインストールするだけなので、ビルドのときには上のパッケージを使いません。使うのは、ros2 launch で起動するときだけです。そこで、実行時の依存だけを表す exec_depend で書きます。depend で書いてもビルドと起動はできますが、実際には要らないビルド時の依存まで宣言することになります。

一方、learn_py と learn_cpp の depend は、ros2 pkg create の --dependencies が書いたもの、つまり rclpy、rclcpp、std_msgs と、フェーズ3-2a の geometry_msgs などで、その書き方にならって足したものです。C++ の learn_cpp は、メッセージの型やライブラリのヘッダをビルドで使うので、ビルド時の依存も要ります。Python の learn_py は、ビルドでコンパイルしないので、厳密には実行時の依存だけで足りますが、メッセージの型のパッケージは、ひな形と C++ の版にそろえて depend で書いています。どちらで書いても、ビルドと実行の結果は変わりません。メッセージの型ではないライブラリ、たとえばフェーズ7-5 の numpy は、実行時にだけ使うことがはっきりしているので、exec_depend で書きます。

### 3-3. CMakeLists.txt でインストールする

learn_bringup の CMakeLists.txt の、ament_package の前に、2行の install の指定を足します。中身は、install の DIRECTORY に launch と config を並べ、DESTINATION を share の下の、パッケージ名のフォルダにする、というものです。

ここでインストールしたものが、ros2 launch から探されます。場所は、install の learn_bringup の share の learn_bringup の launch です。--symlink-install でビルドすると、既にあるファイルの編集は、ビルドし直さなくても反映されます。新しいファイルを足したときは、ビルドし直しが要ります。

Python でノードを書いていても CMakeLists.txt を編集する理由、の説明があります。CMakeLists.txt は C++ のためのファイルに見えますが、ここで書いた2行はコンパイルの指定ではなく、launch と config のフォルダを、インストール先の share の learn_bringup へ置く、という指定です。C++ の知識は要りません。learn_bringup を ament_cmake で作ったのは、このパッケージがノードを持たず、Python の版と C++ の版のどちらのノードも起動する、言語に属さないパッケージだからです。2行はフォルダを丸ごと指定しているので、launch に新しいファイルを足しても、この行は変えず、ビルドし直すだけでよい、とあります。

一般には、launch ファイルは Python のパッケージ、ament_python にも置けます。その場合は、CMakeLists.txt の代わりに、setup.py の data_files に、インストールするファイルと、その置き場所、たとえば share のパッケージ名の launch を書きます。data_files は、Python のコード以外のファイルをインストールするための一覧で、ros2 pkg create のひな形の setup.py にも、package.xml を入れる行が既にあります。書かないと、launch ファイルは install に入らず、ros2 launch から見つかりません。ファイル名を1つずつ並べる代わりに、Python 標準の glob、つまりパターンに合うファイルの一覧を返す関数で書けば、ament_cmake と同じく、ファイルを足しても setup.py を変えずに、ビルドし直すだけで済みます。2026年10月15日に使い捨ての環境で、data_files に書かないと入らないこと、glob で書けば後から足したファイルもビルドし直しで入ることを確かめた、とあります。どちらの形でも、フォルダのファイルを share へ入れる指定がどこかに要り、この教材では、それを learn_bringup の CMakeLists.txt にまとめています。フェーズ5-4 の2-3節で worlds フォルダを足すときも、同じ行を変えます。

なお、Python だけで書くノードのために、自作のメッセージなどの型、つまりインターフェースを作る場合も、CMakeLists.txt を編集します。こちらは、型から Python と C++ のコードを作る仕組みが CMake で動くためで、詳しくは参考資料のインターフェースの6-1節にあります。

## 4. launch ファイルを書く

### 4-1. Python の形式、pubsub.launch.py

主な API の表は、2列で、5行あります。

引数の宣言は、DeclareLaunchArgument に、名前、default_value に既定の値、description に説明を渡します。

引数の値を使うには、LaunchConfiguration に名前を渡します。これは、実行時に評価される、置換と呼ばれるものです。

ノードの起動は、launch_ros の actions の Node に、package、executable、name、output イコール screen などを渡します。

文字列と置換をつなぐには、リストで書きます。たとえば package に、文字列の learn_ と、LaunchConfiguration の talker_lang を並べたリストを渡します。

全体を返すのは、generate_launch_description という関数で、LaunchDescription にアクションのリストを入れて返します。

サンプルは、learn_bringup の launch フォルダの pubsub.launch.py です。

pubsub.launch.py は、30行ほどのコードで、ブロックは、先頭の import と、generate_launch_description の関数の2つです。import では、LaunchDescription、DeclareLaunchArgument、LaunchConfiguration、そして launch_ros の Node を読み込みます。関数は、LaunchDescription を1つ返すだけで、そのリストに4つの要素を並べます。1つ目と2つ目は、DeclareLaunchArgument で、talker_lang と listener_lang を、既定値 py と、talker の言語、py または cpp、のような説明付きで宣言します。3つ目と4つ目は Node です。要の行は、Node の package を、文字列の learn_ と LaunchConfiguration の talker_lang のリストにする行で、listener の側も同じく listener_lang を使います。executable と name はどちらも talker、または listener で、output は screen です。

原文の解説の要点です。役割は、talker と listener の2つのノードを、言語を引数で選んで起動することです。launch ファイルは、ノードを起動する手順書のようなプログラムで、ros2 launch は、このファイルの generate_launch_description を呼び、返ってきた LaunchDescription、つまりやることの一覧を、上から順に実行します。

解説の表は、2列で、6行あります。

generate_launch_description は、関数の名前が決まっています。ros2 launch がこの名前で探して呼ぶので、つづりを変えると、見つからないというエラーになります。

LaunchDescription は、起動のアクション、たとえば引数の宣言やノードの起動を、リストで並べたものです。

DeclareLaunchArgument は、起動のときに talker_lang:=cpp の形で渡せる引数を宣言します。default_value は指定しなかったときの値、description は --show-args で表示される説明です。

LaunchConfiguration の talker_lang は、引数 talker_lang の値を表す置換、substitution です。その場で文字列になるのではなく、起動の実行時に評価される、予約票のようなものです。

Node は、ROS2 のノードを1つ起動します。package と executable は、ros2 run のパッケージと実行ファイルの2つの引数にあたります。name でノード名を上書きし、output イコール screen でログを端末に出します。

package に文字列と置換をリストで並べると、つながって1つの文字列になります。py なら learn_py、cpp なら learn_cpp になり、パッケージ名を切り替えることで言語を切り替えています。

ポイントは、LaunchConfiguration が、あとで評価される置換であることです。generate_launch_description が動く時点では、まだ引数の値は決まっていません。そのため、この関数の中で、Python の if で、LaunchConfiguration が cpp と等しいか、のように判定することはできません。いつも置換のオブジェクトが比べられてしまいます。値で分岐したいときは、OpaqueFunction を使います。これは、この節の最後の課題3で扱います。

つまずきやすい点は3つです。1つ目。DeclareLaunchArgument を書き忘れて、LaunchConfiguration だけ使うと、その launch configuration が存在しない、という趣旨のエラーになります。宣言は LaunchDescription のリストに入れ、慣例としてノードより上に書きます。2つ目。引数の値は、いつも文字列として扱われます。数値など型が要る場面は、4-4節の ParameterValue のように明示します。3つ目。package と executable の組み合わせが実在しないと、起動のときにエラーになります。たとえば talker_lang:=rust は、learn_rust が無いというエラーで、この節の最後の課題2で試します。

観察のポイントです。--show-args で2つの引数と、説明と既定値が見えること。--print では、置換が評価される前の形、つまり learn_ に LaunchConfig の talker_lang を足す式の形で見えること。起動した後に、ros2 node list に /talker と /listener が出ること。LaunchConfiguration は起動のときに評価される予約票だ、という説明を、--print の表示で目で確かめられます。この後の XML の版と YAML の版は、同じ内容を別の書き方で表したもので、Python の版との対応を見比べます。

実行の前に、引数の一覧と、展開の結果を確かめます。この段階では、ノードは起動しません。ros2_ws に移り、colcon build に --symlink-install と、--packages-select learn_bringup を付けてビルドし、source install/setup.bash をしてから、ros2 launch learn_bringup pubsub.launch.py に --show-args を付けたものと、--print を付けたものを実行します。

期待する結果です。--show-args は、DeclareLaunchArgument に書いた名前、説明、既定値を、そのまま並べます。talker_lang と listener_lang の2つが、それぞれの説明と、既定値 py の表示付きで出ます。--print は、LaunchDescription の中身を木の形で表示します。DeclareLaunchArgument が2つと、ノードの起動、つまり ExecuteProcess が2つ、コードに書いた順に並びます。表示の中のアドレスの数字は、毎回変わります。パッケージ名は、learn_ と LaunchConfig の talker_lang を足す式のままで、learn_py には置き換わっていません。talker_lang:=cpp を付けて --print しても、表示は同じです。置換の評価は実際の起動のときに行われるので、--print で分かるのは、ファイルが読み込めて、構造が正しいか、までです。

次に、起動します。1つ目は、引数を付けずに ros2 launch learn_bringup pubsub.launch.py、2つ目は、talker_lang:=cpp と listener_lang:=py を付けたものです。

期待する結果、1つ目のコマンドの例です。2つのノードのログが、1つのターミナルに混ざって出ます。最初に launch 自身の行が2つ、つまりログの置き場所と、既定のログの詳しさが INFO であることが出ます。続いて、talker-1 と listener-2 のプロセスが、プロセス番号付きで起動したと出ます。そのあとは、talker の publish の hello 0 と、listener の received の hello 0 が交互に、1秒ごとに番号を増やして出ます。各行の先頭の、角かっこの talker-1 などは、launch が付ける、どのプロセスの出力か、の印で、ハイフンの後の数字は、起動した順の番号です。

Ctrl+C を押すと、2つのノードがまとめて終わります。

期待する結果、どちらも Python の版の1つ目のコマンドを止めた場合の抜粋です。まず launch が、ユーザーが ctrl-c、つまり SIGINT で中断した、という警告を出します。続いて、listener-2 と talker-1 に、それぞれ SIGINT の信号を送っている、という行が出ます。そのあと、talker-1 から Traceback が出て、途中に node.destroy_node の行があり、KeyboardInterrupt で終わります。最後に、talker-1 のプロセスが終了コード マイナス2 で死んだ、という ERROR の行が出ます。listener にも、talker と同じ数行が出ます。

Traceback や、プロセスが死んだという ERROR の行が出ますが、ノードは止まっていて、異常ではありません。理由はこうです。Ctrl+C を押すと、端末が launch と各ノードにまとめて割り込み、SIGINT を送り、さらに launch も、各ノードへ割り込みを送り直します。SIGINT を送っている、という行がそれです。Python のノードは、1回目の割り込みで spin を抜けて、後片付けの destroy_node に入りますが、その最中に2回目の割り込みが届き、後片付けが中断されて、KeyboardInterrupt の表示になります。終了コードのマイナス2 は、割り込みの信号、SIGINT、番号2 で終わった、という意味です。ROS2 の公式のサンプル、demo_nodes_py の talker も、フェーズ3-1 と同じ main の書き方で、launch から起動して Ctrl+C で止めると同じ表示になります。C++ の版のノード、たとえば talker_lang:=cpp では、rclcpp の signal_handler の行が出たあと、process has finished cleanly、きれいに終わった、と表示されます。rclcpp は、2回目の割り込みも後片付けの妨げにしないからです。続けて、もう一度 ctrl-c で中断されたが無視する、という行が出ることもあり、これも問題ありません。

2つ目のコマンド、talker_lang:=cpp でも、動いている間のログ、つまり publish と received の行の見た目は同じです。Ctrl+C の後の表示は、上の説明のとおり言語によって違い、この場合は、C++ の版の talker と、Python の版の listener の表示が混ざります。どちらの言語が動いているかは、ログではなく、ros2 node info の /talker などで調べます。これが課題1です。課題2の talker_lang:=rust では、ノードは1つも起動せず、launch の ERROR で、launch の中で例外を捕まえた、という行に続いて、learn_rust というパッケージが見つからない、という趣旨のメッセージが出て終わります。

課題が3つあります。

課題1。4通りの組み合わせをすべて起動し、ros2 node list と、ros2 topic info /chatter に -v を付けたもので、どの言語のノードがつながっているかを確かめます。

課題2。存在しない値、talker_lang:=rust を渡すとどうなるかを確かめます。learn_rust のパッケージが見つからないエラーになります。

課題3、発展です。値を検証して、py と cpp 以外は分かりやすいエラーにしたい、という課題です。OpaqueFunction を使うと、引数の値を文字列として取り出して、Python の側で if で判定できます。調べて書いてみます。

### 4-2. XML の形式、pubsub.launch.xml

XML では、ドル記号とかっこの var、つまり、ドル、かっこ、var、引数名、かっこ閉じ、の形で引数を参照し、文字列に埋め込めます。リストでつなぐ必要が無いぶん、この用途では Python より短く書けます。

サンプルは、launch フォルダの pubsub.launch.xml です。

pubsub.launch.xml は、8行ほどのコードで、先頭に概要のコメントが1行あり、そのあと全体を launch のタグで囲みます。中には、arg のタグが2つと、node のタグが2つあります。arg のタグは、name、default、description の属性で、talker_lang と listener_lang を宣言します。要の行は node のタグで、pkg の属性を、learn_ のあとに var の talker_lang を埋め込んだ文字列にし、exec と name を talker、output を screen にします。listener の側も、同じ形です。

原文の解説の要点です。Python の版の各要素が、XML のタグに、ほぼ1対1で対応しています。

対応の表は、3列で、3行あります。列は、Python、XML、補足です。

1行目。Python の DeclareLaunchArgument は、XML では arg のタグになります。属性の名前が、default_value ではなく default になります。

2行目。Python の Node は、XML では node のタグになります。package は pkg、executable は exec と短くなります。

3行目。Python の、learn_ と LaunchConfiguration のリストは、XML では、learn_ に var の引数名を埋め込んだ1つの文字列になります。文字列の中に、そのまま埋め込めます。

全体は launch のタグで囲みます。Python ではリストでつながなければならなかった部分が、XML では1つの文字列で書けるので、この用途では短く読みやすくなります。

つまずきやすい点は3つです。1つ目。var の書き方は、宣言してある引数、つまり arg のタグを参照する書式です。古い資料にある、ドル、かっこ、arg の書き方は、別の古い書き方なので、混ぜません。2つ目。タグは必ず閉じます。自分で閉じる形の、スラッシュと山かっこを忘れないようにします。閉じ忘れは、XML として読めないエラーになります。3つ目。XML では、if や計算のような複雑な処理は書けません。条件付きの起動は、if や unless の属性で最低限できますが、凝った処理は Python の形式に任せます。

観察のポイントです。--print の出力が、Python の版と同じ内容になることです。手順書を作るときに確かめた範囲では、アドレスの数字以外は1文字も違わなかった、とあります。書き方が違っても、読み込まれた後は同じ LaunchDescription になります。

### 4-3. YAML の形式、pubsub.launch.yaml

サンプルは、launch フォルダの pubsub.launch.yaml です。

pubsub.launch.yaml は、20行ほどのコードで、先頭に概要のコメントが1行あり、最上位のキーは launch です。その下に、ハイフンで始まるリストの要素が4つ並びます。1つ目と2つ目は arg で、その下にインデントして、name、default、description を書き、talker_lang と listener_lang を宣言します。3つ目と4つ目は node で、要の行は、pkg を、learn_ に var の talker_lang を埋め込んだ値にする行です。その下に、exec、name、output を書きます。

原文の解説の要点です。構造は3つの点にまとめられます。最上位のキーの launch の下に、ハイフンで始まる行のリストで、アクションを並べます。リストの各要素は、arg や node のような1つのキーを持ち、その下に属性をインデントして書きます。属性の名前は、XML の形式とほぼ同じで、pkg、exec、name、output、引数の default です。引数の埋め込みは、XML と同じ var の書き方で、値の中に置けます。

YAML でも XML でも、引数を宣言してからノードを起動する、という順序は変わりません。YAML の利点は、XML のタグの閉じ忘れが無く、見た目がすっきりすることです。反面、インデントがずれると意味が変わるか、エラーになるので、スペースの数をそろえます。タブは使えません。

つまずきやすい点は3つです。1つ目。arg の直後の属性を、1段深くインデントし忘れると、読み込みに失敗します。2つ目。コロンや特別な記号を含む値は、YAML では引用符が要る場合があります。この例の description は、コロンを含まないので、そのまま書けています。3つ目。3つの形式とも、--print で、読み込めるか、つまり書式の誤りが無いかと、読み込まれた構造を確かめられます。書いたら、まず --print で読み込めるかを見ます。var などの置換の値は、--print では評価されません。

3つの形式を書き比べると、Python は自由度が高く、分岐、計算、関数にまとめることができ、XML と YAML は、単純な起動の一覧を短く書ける、という違いが見えます。

比較の表は、4列で、3行あります。列は、観点、Python、XML、YAML です。

行数の行です。pubsub.launch のファイルで、概要のコメントの行を除くと、Python は25行、XML は7行、YAML は19行です。

引数の埋め込みの行です。Python は LaunchConfiguration に引数名を渡し、Python のオブジェクトとして扱います。XML は var の書き方です。YAML も var の書き方で、XML と共通の記法です。

条件分岐と計算の行です。Python はできます。条件で起動するかを切り替える IfCondition や、Python の式を評価する PythonExpression、それに素の Python の関数や分岐が、そのまま使えます。XML はできず、宣言的な起動の一覧だけです。YAML も同じくできません。

行数だけなら XML が圧倒的に短いのですが、これは talker と listener を1つずつ書くだけ、という単純な内容だからです。4-4節や4-6節のように、パスの組み立てや条件分岐が絡むと、Python の形式でないと書けない処理が増えます。

実行の前に、の囲みです。4-2節の pubsub.launch.xml と、この節の pubsub.launch.yaml を足したので、4-1節と同じく、ros2_ws で colcon build をし直し、source install/setup.bash をしてから実行します。ビルドしないと、ros2 launch が新しいファイルを見つけられません。理由は5節にあります。

3つの形式を確かめるには、pubsub.launch.xml と pubsub.launch.yaml を、それぞれ talker_lang:=cpp と --print を付けて ros2 launch します。

期待する結果です。どちらも、4-1節の pubsub.launch.py の --print と同じ木、つまり DeclareLaunchArgument が2つと、ExecuteProcess が2つ、が表示されます。talker_lang:=cpp を付けていても、パッケージ名は、learn_ と LaunchConfig の talker_lang の式のままです。XML や YAML の書式を間違えているときは、木の代わりに、読み込みのエラーが出ます。

課題4。3つの形式で、同じ pubsub.launch を実際に動かし、上の表の内容、つまり行数、引数の埋め込み、分岐ができるかを、自分の目で確かめます。目安として、複雑な条件や計算が要る場合は Python、単純な起動の一覧は XML や YAML が読みやすい、とあります。

### 4-4. パラメータを launch から渡す、param.launch.py

主な API の表は、2列で、4行あります。

インストール先のパスを得るには、FindPackageShare に learn_bringup を渡します。PathJoinSubstitution と組み合わせて使います。

YAML を読ませるには、Node の parameters に、YAML のファイルのパスを入れたリストを渡します。

個別の値で上書きするには、parameters のリストの後ろに、period と値の辞書を足します。後ろのものが勝ちます。

引数の値の型を決めるには、ParameterValue に、LaunchConfiguration の period と、value_type イコール float を渡します。

ParameterValue を使う理由です。引数はもともと文字列で、そのままだと1 のような値が整数として渡されて、フェーズ3-3 で見た、型の不一致になり得ます。value_type に float を指定すれば、実数として渡せます。

サンプルは、launch フォルダの param.launch.py です。

param.launch.py は、30行ほどのコードで、ブロックは、先頭の import と、generate_launch_description の関数の2つです。import では、4-1節のものに加えて、PathJoinSubstitution、ParameterValue、FindPackageShare を読み込みます。関数の先頭で、config という変数に、PathJoinSubstitution で、FindPackageShare の learn_bringup と、config と、param_talker.yaml をつないだパスを入れます。続いて LaunchDescription を返し、そのリストには、DeclareLaunchArgument の lang、既定は py と、period、既定は文字列の1.0、説明は送信の周期、秒、実数と、Node が1つ並びます。Node の package は、learn_ と LaunchConfiguration の lang のリストで、executable と name は param_talker、output は screen です。要の行は、Node の parameters で、リストの1つ目に config のパス、2つ目に、period を ParameterValue で包んだ LaunchConfiguration の period、value_type は float、とする辞書を置きます。

原文の解説の要点です。役割は、param_talker を、YAML のファイルのパラメータで起動し、一部だけ引数で上書きすることです。パラメータの渡し方を、ファイル、個別の値、型の指定、の3段で読みます。

解説の表は、2列で、6行あります。

FindPackageShare の learn_bringup は、パッケージのインストール先、つまり install の learn_bringup の share の learn_bringup を、実行時に見つける置換です。--symlink-install を付けたかどうかや、インストールの場所によらない書き方になります。

PathJoinSubstitution は、いくつかの要素を、OS に合ったパスの区切りでつないで、1つのパスにします。文字列をプラスでつなぐより安全です。

関数の先頭の、config への代入は、パスをいったん変数に入れておき、後で parameters に渡すためのものです。これも置換なので、評価は起動のときです。

DeclareLaunchArgument の lang と period は、言語と送信の周期の引数です。既定値は、文字列の1.0 になっています。

parameters に config と辞書を並べたものは、パラメータのリストです。要素には、YAML のファイルのパスか、名前と値の辞書を置けます。前から順に当てはめられ、後ろが勝つので、YAML で読んだ period を、辞書の period が上書きします。

ParameterValue に LaunchConfiguration の period と value_type の float を渡したものは、文字列の引数を、実数として渡すための包みです。

YAML のパラメータのファイル、config の param_talker.yaml の構造は、3つの階層になっています。最上位はノード名の param_talker で、Node の name の param_talker と一致しないと、パラメータが黙って無視されます。その下は ros__parameters で、アンダースコアが2つです。つづりを間違えると、やはり無視されます。その下が、パラメータの名前と値、つまり message や period などです。

ParameterValue が要る理由の補足もあります。launch の引数はすべて文字列で、そのまま辞書に入れると、1 のような値が整数として解釈され得ます。フェーズ3-3 で見たとおり、ノードは period を実数として宣言しているので、整数が来ると、型の不一致で起動に失敗します。value_type に float を付けると、1 でも1.0 として渡されます。

つまずきやすい点は3つです。1つ目。Node の name を変えたのに、YAML の最上位のノード名を直し忘れる。2つ目。YAML を parameters の後ろに置くと、引数で渡したはずの値が、YAML に上書きされる。並びの順序に意味があります。3つ目。引数に既定値があるので、period を指定しなくても、引数の側の1.0 が使われ、YAML の値の0.5 は結果として使われない。これは、この節の最後の課題5と、その補足で扱います。

観察のポイントです。ros2 param get で、message は YAML の値、period は引数の値、たとえば period:=0.2 なら0.2 になっていること。YAML が install の share の下から読まれていることも、この節の最後の課題6で確かめます。

実行の前に、の囲みです。param.launch.py を足したので、同じく ros2_ws で colcon build をし直し、source install/setup.bash をしてから実行します。

起動のコマンドは2つです。1つ目は、引数なしの ros2 launch learn_bringup param.launch.py、2つ目は、lang:=cpp と period:=0.2 を付けたものです。2つ目は、C++ の版の param_talker を作った場合で、作っていなければ lang:=py にします。

期待する結果、2つ目のコマンドの例です。launch 自身の行は4-1節と同じなので省いてあります。param_talker-1 のプロセスが起動したと出たあと、param_talker の publish の from yaml、つまり YAML の message の値が、引数で上書きした周期の0.2秒ごと、1秒に5行の速さで出ます。1つ目のコマンド、つまり引数なしでは、周期は引数の既定値の1.0秒になります。

別のターミナルで、実際に値が入っているかを確かめます。ros2 param get の /param_talker message で、YAML で渡した値を、ros2 param get の /param_talker period で、launch の引数で上書きした値を確かめます。

期待する結果、period:=0.2 で起動した場合です。message は、文字列の値が from yaml、period は、Double の値が0.2、と表示されます。

課題が2つあります。

課題5。period を渡さない場合に、YAML の0.5 になるか、引数の既定の1.0 になるかを確かめます。parameters の並び順の決まりから、予想してから試します。補足として、引数 period に既定値の1.0 があるので、指定しなくても、いつも引数の側が勝ち、YAML の0.5 は使われない、とあります。発展として、引数の既定を空にして、指定が無ければ YAML の値を使う書き方を、調べて試します。

課題6。FindPackageShare の learn_bringup がどこを指すかを、ros2 pkg prefix に --share と learn_bringup を付けて確かめます。ros2_ws の install の learn_bringup の share の learn_bringup と表示されます。その下の config に param_talker.yaml があることを ls で確かめ、PathJoinSubstitution が組み立てるパスと一致することを確かめます。--print では、パラメータのパスは表示されません。置換は起動のときに評価されるからです。

### 4-5. OSS と自作のノードを一緒に起動する、turtle.launch.py

サンプルは、launch フォルダの turtle.launch.py です。

turtle.launch.py は、25行ほどのコードで、ブロックの形は pubsub.launch.py と同じです。import のあと、generate_launch_description が LaunchDescription を返し、そのリストに3つの要素を並べます。1つ目は DeclareLaunchArgument の lang で、既定は py、説明は turtle_circle の言語です。要の行は残りの2つの Node で、1つ目の Node は、package を固定の文字列の turtlesim、executable を turtlesim_node、name を turtlesim にします。2つ目の Node は、package を learn_ と LaunchConfiguration の lang のリストにし、executable と name を turtle_circle にします。どちらも output は screen です。

原文の解説の要点です。役割は、OSS の turtlesim のノードと、自作の turtle_circle を、1つのコマンドで一緒に起動することです。pubsub.launch.py との違いは3つあります。

1つ目。OSS のノードも、同じ Node で起動できます。package を turtlesim、executable を turtlesim_node にするのは、ros2 run turtlesim turtlesim_node と同じ指定です。自作でも他人のパッケージでも、launch の書き方は変わりません。

2つ目。turtlesim の側の package は固定の文字列で、自作の側だけを、learn_ と LaunchConfiguration の lang で切り替えています。切り替えたい部分にだけ置換を使う、という使い分けの例です。

3つ目。name の turtlesim は、ノード名を、既定と同じ turtlesim に明示しています。

つまずきやすい点は2つです。1つ目。launch は、リストのノードを、ほぼ同時に起動します。順番は保証されません。turtlesim のウィンドウが立ち上がる前に、turtle_circle が最初の指令を送ると、その指令は届かないことがあります。慌てず、少し待って、動きが始まるかを見ます。2つ目。turtlesim が入っておらず、パッケージ turtlesim が見つからない、と出る場合は、フェーズ1 で導入を済ませたかを確かめます。

観察のポイントです。1つのターミナルの Ctrl+C で、2つのノードがまとめて止まること。これは、別々のターミナルで起動していたときとの違いです。また、ros2 node list に、/turtlesim と /turtle_circle が並ぶことです。

実行の前に、同じく turtle.launch.py を足したので、colcon build をし直し、source してから実行します。

起動のコマンドは、ros2 launch learn_bringup turtle.launch.py に、lang:=cpp を付けたものです。C++ の版の turtle_circle を作っていなければ、lang:=py にします。

期待する結果です。turtlesim のウィンドウが開き、少し待つと、亀が円を描き始めます。フェーズ3-2a の6節と同じ動きです。ターミナルには、turtlesim_node-1 と turtle_circle-2 の、2つのプロセスの起動が出ます。turtle_circle はログを出さないので、そのあとは turtlesim の側のログだけが出ます。turtlesim のノード名で起動したこと、そして、turtle1 という亀を、座標と向き付きで生み出したことの2行です。

### 4-6. launch を合成する、名前空間、remap、compose.launch.py

主な API の表は、2列で、3行あります。

別の launch ファイルを呼ぶには、IncludeLaunchDescription に、PythonLaunchDescriptionSource で包んだパスと、launch_arguments に辞書の items を渡します。

名前空間をまとめて付けるには、GroupAction のリストに、PushRosNamespace の demo と、まとめたいアクションを並べます。

トピック名を付け替える、つまり remap するには、Node の remappings に、元の名前と新しい名前の組のリストを渡します。

名前空間 demo の下では、ノード名は /demo/talker、トピックは /demo/chatter になります。remap を付けたノードは、コードに書いたトピック名の chatter の代わりに、新しい名前、たとえば param_chatter を使います。

サンプルは、launch フォルダの compose.launch.py です。

compose.launch.py は、30行ほどのコードで、ブロックは3つです。1つ目は import で、GroupAction、IncludeLaunchDescription、PythonLaunchDescriptionSource、PathJoinSubstitution、Node、PushRosNamespace、FindPackageShare を読み込みます。2つ目は、_launch_file という補助の関数で、名前を受け取り、FindPackageShare の learn_bringup と、launch と、その名前をつないだパスを、PythonLaunchDescriptionSource で包んで返します。3つ目が generate_launch_description で、変数を3つ作ってから、LaunchDescription に pubsub、param、param_listener の3つを並べて返します。

要の行は、その3つの変数です。pubsub は GroupAction で、リストの1つ目が PushRosNamespace の demo、2つ目が IncludeLaunchDescription で、_launch_file の pubsub.launch.py を呼び、launch_arguments に、talker_lang を cpp、listener_lang を py とする辞書の items を渡します。param は、IncludeLaunchDescription で _launch_file の param.launch.py を呼ぶだけで、引数は渡しません。param_listener は Node で、package は learn_py、executable は listener、name は param_listener、remappings に、chatter から param_chatter への組を1つ入れ、output は screen です。

原文の解説の要点です。役割は2つあります。既にある launch ファイルを部品として呼び出し、名前空間をまとめて付けること。そして、remap で、コードを書き換えずに、トピック名の違うノード同士をつなぐことです。pubsub.launch.py と param.launch.py を組み合わせ、さらに listener をもう1つ起動して、param_talker の送る param_chatter を聞かせます。

解説の表は、2列で、6行あります。

_launch_file は、learn_bringup の launch の下の、指定したファイルを指す PythonLaunchDescriptionSource、つまり起動元を作る補助の関数です。同じ書き方を2回書かないためのまとめで、先頭のアンダースコアは、このファイルの内部用、という慣習です。

IncludeLaunchDescription は、別の launch ファイルを、この場所で実行します。launch_arguments は、呼び出す側の引数を、まとめて固定する指定で、辞書の items、つまりキーと値の組の並びで渡します。値は文字列です。

PushRosNamespace の demo は、以降のノードに、名前空間 demo を付けます。

GroupAction は、アクションをグループにまとめます。名前空間の指定は、グループの中だけに効くので、グループの外の param には影響しません。

param_listener の Node は、フェーズ3-1 の Python の版の listener を、ノード名 param_listener で起動します。remappings は、元の名前から新しい名前への組のリストで、コードの中の chatter を param_chatter に付け替えます。

最後の LaunchDescription は、グループと include とノードを並べて返します。

実行の結果として、pubsub.launch.py のノードは /demo/talker と /demo/listener、トピックは /demo/chatter になります。param.launch.py は名前空間の外なので、/param_talker のままです。ros2 node list で、この違いが見えます。

remap の考え方です。listener のコードは、chatter を購読すると決め打ちしていて、param_talker は param_chatter に送ります。名前が違うので、そのままではつながりません。コードを書き換える代わりに、起動するときに、このノードの中の chatter を param_chatter と読み替える、と指定するのが remap です。同じ listener の実行ファイルが、/demo/listener では /demo/chatter、つまり talker の hello N を、/param_listener では /param_chatter、つまり param_talker の from yaml を受け取ります。他人が書いたノードや、フェーズ1 の turtlesim のような OSS のノードを、名前の決まった相手につなぐときに使います。フェーズ3-2a の turtle_circle も、/turtle1/cmd_vel を付け替えれば、別のロボットへの速度の指令になります。

補足が5つあります。

1つ目。include された側の引数は、launch_arguments で渡さなければ、その既定値が使われます。param の呼び出しは引数を渡していないので、lang は py、period は1.0 になります。pubsub は、talker_lang を cpp、listener_lang を py で固定しています。

2つ目。名前空間が効くのは、相対名、つまり先頭にスラッシュが無い名前の、ノード名とトピック名です。コードの中でスラッシュ chatter のように絶対名で書くと、名前空間を付けても変わりません。talker は chatter と相対名で書いているので、/demo/chatter になります。

3つ目。Node の remappings に書いた remap は、そのノードの中だけに効きます。param_listener は、相手の param_talker が元から param_chatter に送っているので、受信側の1つに付けるだけでつながります。逆に、つながっている2つのノードのトピック名を、そろって変えたい場合は、送信側と受信側の両方に、同じ remap が要ります。片方だけに付けると、名前が食い違って、つながらなくなります。これは、この節の最後の課題7で試します。

4つ目。新しい名前に param_chatter のような相対名を書くと、そのノードの名前空間の下の名前になります。このノードは名前空間の外なので、/param_chatter です。名前空間の中のノードから外のトピックを指すときは、スラッシュ param_chatter のように絶対名で書きます。

5つ目。--print の表示には、remap の中身は出ません。効いているかは、起動した後に ros2 topic info やログで確かめます。

つまずきやすい点は3つです。1つ目。launch_arguments に辞書をそのまま渡し、items を付けないと、型のエラーになります。2つ目。名前空間を付けたのに、コードが絶対名を使っていて変わらない、という食い違いに注意します。3つ目。同じノード名が2つ起動すると、ログに警告が出ます。これが、名前空間を付ける理由の1つです。

観察のポイントです。ros2 node list と ros2 topic list の結果が、このあとの期待する結果のとおり、/demo/talker、/demo/listener、/param_listener、/param_talker、そして /demo/chatter、/param_chatter になること。param_listener のログに、received の from yaml が出て、/param_chatter の購読の数が1 になること、つまり remap が効いていること。Ctrl+C で、全部のノードが止まること。これは課題8です。

実行の前に、同じく compose.launch.py を足したので、colcon build をし直し、source してから実行します。

ターミナル1 で、ros2 launch learn_bringup compose.launch.py を起動し、動かしたまま、ターミナル2 で、ros2 node list、ros2 topic list、ros2 topic info の /param_chatter を実行します。

期待する結果です。ターミナル1 の launch には、4つのプロセス、talker、listener、param_talker、listener のログが混ざって出ます。ノード名は名前空間付きで、demo ドット talker のように、ドットで区切って表示されます。例として、talker-1 の demo.talker が hello 0 を publish し、listener-2 の demo.listener が hello 0 を受け取り、param_talker-3 の param_talker が from yaml を publish し、listener-4 の param_listener が from yaml を受け取る、という4行が載っています。listener-4 は、remap を付けて起動した2つ目の listener です。プロセスの印は実行ファイルの名前の listener から付くので、ノード名の param_listener は、その後ろの角かっこで見分けます。received の from yaml は、param_talker の送った文字列が届いたことを示します。

ターミナル2 での確かめです。ros2 node list には、/demo/listener、/demo/talker、/param_listener、/param_talker の4つが並びます。ros2 topic list の抜粋には、/demo/chatter、/param_chatter、/parameter_events、/rosout の4つが並びます。ros2 topic info の /param_chatter は、型が std_msgs の msg の String、publisher の数が1、subscription の数が1 と表示されます。

demo の下に入るのは、GroupAction の中で include した pubsub.launch.py の2つのノードと、そのトピックだけで、param.launch.py の側は名前空間なしのままです。/parameter_events と /rosout は、どのノードも共有する全体のトピックなので、名前空間が付きません。ros2 topic list に /chatter が無いのは、どのノードも、名前空間の外で chatter を使っていないからです。param_listener の chatter は、remap で param_chatter になっています。/param_chatter の購読の数が1 なのは、param_listener が購読していることを示します。remap を外すと0 になり、代わりに /chatter が現れます。

課題が2つあります。

課題7。pubsub.launch.py の Node に、chatter を renamed に付け替える remappings を足して、トピック名が変わることと、talker と listener の両方に同じ remap を付けないと、つながらないことを確かめます。確かめたら、元に戻します。

課題8。launch を Ctrl+C で止めたときに、起動した全部のノードが終わることを確かめます。ログに、各ノードの終了が出ます。

## 5. ビルドと反映

4節では、launch ファイルを足すたびにビルドし直しました。ここで、その理由をまとめます。ros2 launch は、ソースの launch フォルダではなく、ビルドで install の learn_bringup の share の learn_bringup の launch に入れたファイルを探します。3-3節の install の指定です。そのため、launch ファイルを追加したときは、ビルドし直しが要ります。ros2_ws に移り、colcon build に --symlink-install と --packages-select learn_bringup を付けて実行し、source install/setup.bash をします。

期待する結果です。learn_bringup が終わった、という行と、1つのパッケージが終わった、という要約が出れば成功です。表示の形は、フェーズ3-1 の3-3節と同じです。source は、成功しても何も表示しません。

既にある launch ファイルの編集だけなら、--symlink-install のおかげで、ビルドし直さなくても反映されます。新しいターミナルで確かめます。

## 6. このフェーズのまとめ

2列の表で、4行あります。

1行目は、4通りの組み合わせ、つまり Python と Python、Python と C++、C++ と Python、C++ と C++ の起動の結果です。全部の組み合わせで、つながります。4-1節で確かめ、フェーズ3-1 で確かめた、言語に関係なくつながる、ということが、launch でも成り立ちます。

2行目は、パラメータの優先順位、YAML と引数です。parameters の、YAML と辞書のリストは、後ろが勝ちます。これは4-4節です。さらに、引数の側に既定値があると、指定しなくても引数が優先され、YAML の値は使われません。これは4-4節の課題5の補足です。

3行目は、namespace と remap の効き方です。名前空間は、相対名、つまり先頭がスラッシュでない名前にだけ効きます。スラッシュ chatter のような絶対名で書かれたノードには効きません。これは4-6節です。remap は、付けたノードの中だけに効き、コードを変えずに、名前の違う相手とつなげます。4-6節の param_listener がその例です。つながっている2つのトピック名をそろって変えるなら、送信側と受信側の両方に、同じ指定が要ります。片方だけだと、つながらなくなります。これは4-6節の課題7です。

4行目は、Python、XML、YAML の使い分けです。単純な起動の並びは、XML と YAML が短く書けます。pubsub.launch で、XML は7行、YAML は19行、Python は25行でした。条件分岐、計算、パスの組み立てが要る場合、つまり4-4節や4-6節は、Python の形式でないと書けません。これは4-3節です。

フェーズ3-1 から3-5 とフェーズ2 の、各節の、Python の版と C++ の版の違いのまとめと合わせて読み返すと、学習計画の1-7 の振り返りの材料になります。1-7 は、学習計画でフェーズ3 と4 の後に置いた、Python と C++ を比べる振り返りで、コードの量、型の扱い、ビルドの手順、つまずきの傾向を比べます。フェーズ5 の言語の方針、つまり Python が中心であることは、既に決まっていますが、この振り返りは、今後 C++ で書く場合の勘所の確かめ直しとして使えます。

## 7. つまずきやすい点

2列の表で、8行あります。列は、症状と、確かめることです。

1行目。learn_bringup の share のフォルダに、あるファイルが見つからない、と出る場合。launch ファイルを追加した後にビルドし直したか、CMakeLists.txt に、launch と config の install の指定があるかを確かめます。

2行目。パッケージ learn_cpp が見つからない、と出る場合。source install/setup.bash をしたか、learn_cpp をビルドしてあるかを確かめます。

3行目。ビルドで、ament_cmake_symlink_install_directory が config を見つけられない、と出る場合。learn_bringup の config フォルダが無いか、空のため Git の上に存在しない状態です。3-1節の手順のとおり config を作り、param_talker.yaml を入れます。

4行目。ros2 launch で、パラメータが効かない場合。YAML の1行目のノード名と、Node の name が一致しているか、ros__parameters のつづりを確かめます。

5行目。period で型の不一致が起きる場合。ParameterValue に value_type の float を付けているか、YAML の period が、1 のような整数になっていないかを確かめます。

6行目。ノードが起動しない、すぐ終わる場合。output を screen にして、エラーのログを見ます。ros2 launch に --print を付けて、ファイルが読み込めるかを、--show-args で、引数の名前と既定値を確かめます。置換の値は、--print では評価されません。

7行目。Ctrl+C で、Traceback と、終了コード マイナス2 でプロセスが死んだ、という表示が出る場合。Python のノードでは異常ではありません。4-1節の、Ctrl+C の期待する結果の後の説明のとおりです。

8行目。XML や YAML で引数が展開されない場合。var の書式になっているかを確かめます。arg の書き方は古い書き方です。また、引数を、XML の arg のタグか、YAML の arg のキーで宣言しているかを確かめます。

## 8. 次へ

次は間章のコンポーネントで、フェーズ3-1 の C++ の版の talker と listener を、コンポーネントに作り直します。コンポーネントは、main を持たず、どのプロセスで動かすかを起動のときに決められるノードです。この節で書いた launch も、コンテナを起動する形に発展させます。その後、フェーズ5 の、車両のシミュレーションの本体に進みます。最初はフェーズ5-0 で、Gazebo を導入して動かします。フェーズ5-3 と5-4 では、learn_bringup に、車両のシミュレーション用の launch ファイル、つまりフェーズ5-3 の vehicle_sim.launch.py と、フェーズ5-4 の gazebo_plant.launch.py を追加します。

## 9. 公式のドキュメントと参考資料

確かめた状況は、2026年9月20日の時点です。下の資料は、元のアイデアの文書に載せてある URL で、今回は確かめ直していない、とあります。docs.ros.org は、ボット対策で本文の取得を断られるためです。

公式の資料は、ROS 2 Jazzy の4つと、REP 149 です。launch ファイルを作るチュートリアル、launch ファイルを ROS 2 のパッケージに組み込むチュートリアル、launch のチュートリアルの目次、そして、コマンドラインのツールで複数のノードを起動するチュートリアルです。REP 149 は、package.xml の書き方の規則、Package Manifest Format Three の仕様で、3-2節の depend と exec_depend の違いのところで使っています。2026年10月12日に原稿で確かめた、とあります。

公式のドキュメントと食い違う場合は、公式を優先する、とあります。

原文の最後には、出典の注記があります。各サンプルの API の使い方は、公式のチュートリアルを参考にしました。ROS 2 のドキュメントは CC BY 4.0 です。ノードの名前、仕様、コード、文章は独自に書いたもので、一語ずつの転載ではありません。

以上で、フェーズ4 の手順書の話を終わります。

## 出典について

この原稿は、SanghunIm1991 さんの [ros2MinimalPhysicalAi の「フェーズ4 手順書: launchファイルで複数ノードを束ねる」](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/docs/phase4_launch.md)を、聞くために要約・意訳したものです。図の [phase4_overview.svg](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/docs/img/phase4_overview.svg) と [phase4_bringup_role.svg](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/docs/img/phase4_bringup_role.svg) と [phase4_compose.svg](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/docs/img/phase4_compose.svg) は、言葉で説明しました。元にしたのは、[2026年10月17日の版](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/6d6f7ab7206ed5a18d6de96d4ff31d8d53a510e7/docs/phase4_launch.md)です。原文の文章と図と同じく、[クリエイティブ・コモンズ 表示 4.0 国際ライセンス](https://creativecommons.org/licenses/by/4.0/deed.ja)で提供します。

原稿の中に原文の表記のまま書いたコマンドと、コードの関数やクラスの名前は、原文では [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0) の対象です。ライセンスの全文は、原文のリポジトリの [LICENSE-APACHE-2.0](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/LICENSE-APACHE-2.0) にあります。launch ファイルなどのサンプルコードは写さず、役割と要の行を言葉で説明しました。

原文では、API の使い方を [ROS 2 Documentation](https://docs.ros.org/en/jazzy/)（Open Robotics、[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)）の公式チュートリアルを参考にしたとしています。表示の例は、ros2 や colcon などの各ツールの表示を言葉で説明したものです。
