<!--
聞くための原稿（読み上げでは読まれない記録）
原文: SanghunIm1991/ros2MinimalPhysicalAi の main ブランチの docs/phase3_2b_qos.md（図は docs/img/phase3_2_qos.svg）
原文のコミット: 132df7b64d48d560def7ec7149f7003938d3d8e5（2026-10-14）
作成: 2026-10-20、Claude Code が手作業で作成（原稿化スキルはまだない）
原文のライセンス: 文章と図は CC BY 4.0、コードとコマンドは Apache-2.0（それぞれ LICENSE の2と1）。原文の末尾に、API の使い方は公式ドキュメント（ROS 2 Documentation、CC BY 4.0）を参考にし、コードと文章は独自に書いた、とある。この原稿は、原文を聞くために要約・意訳したもの（改変あり）
方針: 英語の略語や製品名、関数やクラスの名前、短いコマンドは原文の表記のまま書く。サンプルコード6本と、setup.py・CMakeLists.txt に足す行は、写さずに、ブロックの役割と要の行を言葉で説明した。期待する結果（ログ、非互換の警告の文面、ros2 topic info の表示）も写さず、何が表示されるかを言葉で説明した。図と表（仕様、7通りの組み合わせ、主な API、名前の使い分け、Python と C++ の QoS の対応、Python版と C++版の違い、つまずきやすい点）は言葉で説明する。文字数の上限は設けない
省いたもの: URL、型の定義へのリンク、ログの時刻の数字
-->

# フェーズ3-2b: QoS の相性を体験する（聞くための原稿）

これは、ros2MinimalPhysicalAi という教材の、フェーズ3-2b の手順書の話です。QoS の設定の組み合わせを変えて、トピックがつながるか、つながらないかを観察します。

想定する環境は、WSL2 と Ubuntu 24.04 と ROS2 Jazzy です。前提は、フェーズ3-1 を終えて、talker などが動くことです。フェーズ3-2a とは独立したテーマで、3-2a で作ったものは使いません。所要時間の目安は半コマです。言語は Python で、C++ の版は任意です。使う OSS はありません。

原文には、位置づけの囲みがあります。このフェーズの目的は、QoS という設定があり、合わないと、エラーも出ずに黙ってつながらないことがある、と知ることで、概要をつかむ程度でかまいません。フェーズ5 では、すべてのノードが既定の QoS のまま通信します。2-2節の7通りの組み合わせのうち、1番、つまり talker と listener のどちらも reliable でつながるものと、4番、つまり talker が best_effort で listener が reliable でつながらないもの、の2つを試せば十分で、残りは任意です。C++ の版の4節も任意です。

進め方は、フェーズ3-1 と同じです。仕様は何を作るかの定義で、API の使い方は、主な API の表とサンプルコードと解説を読んで理解し、QoS のパラメータを変えて動かしながら体で覚えます。サンプルは、手順書を作るときにビルドを確かめ、手順は2026年9月26日に実機で確かめています。出力が細部で違う場合は、実機の表示を優先します。

パラメータについての注意もあります。このフェーズでは、QoS の設定を起動のときに切り替えるために、ROS のパラメータ、つまりノードの外から与えられる設定の値を使います。けれども、パラメータそのものの説明は、次のフェーズ3-3 で行います。ここでは、declare_parameter で名前と既定の値を宣言し、起動のときに -p で、名前、コロン、イコール、値、の形で値を渡すと、ノードの中で読み取れる、という使い方だけを押さえておけば十分で、細かな仕組みが分からなくても先へ進んでよい、とあります。

期待する結果は、コードと ROS2 の仕様から筆者が想定したもので、実機で確かめてあります。

この原稿では、サンプルコードを書き写さず、役割と要の行を言葉で説明します。ログや警告の文面も、何が表示されるかを言葉で説明します。

## 0. 学習目標と完了の条件

必須の条件は1つです。QoS が合わないと、エラーにならずに黙ってつながらないことがある、と説明できること。5-1節で、2-2節の1番と4番を試します。

任意の発展の条件は2つです。2つ目は、2-2節の7通りの組み合わせをすべて試し、ros2 topic info に -v を付けて、QoS を読み取れること。3つ目は、C++ の版を書き、QoS の扱いが言語によらないことを確かめることです。

## 1. 全体像

同じトピック qos_test を、送り手の qos_talker と、受け手の qos_listener でやり取りします。どちらも QoS を起動のときのパラメータで切り替えられるようにしておき、組み合わせを変えて、つながるか、つながらないかを観察します。

QoS の相性は、購読する側の要求を、配信する側の提供が満たせるかで決まります。この教材で扱う QoS の設定は、reliability、つまり信頼性と、durability、つまり持続性の2つです。

原文の図は、その組み合わせを一覧にしたもので、SVG と mermaid の版があります。図の一番上に、左の列の見出しとして「qos_talker、配信側、提供する」、右の列の見出しとして「qos_listener、購読側、要求する」とあります。その下に、点線の枠が上下に2つあります。

上の枠は reliability で、「届かなかったメッセージを再送するか」と添えられています。枠の中には4つの行があり、それぞれ左の箱から右の箱への矢印でつながっています。1番は、左が reliable、右が reliable で、つながる。2番は、左が reliable、右が best_effort で、つながる。3番は、左が best_effort、右が best_effort で、つながる。4番は、左が best_effort、右が reliable で、この行だけは矢じりの無い赤い点線で、バツ印と「つながらない」と書かれています。

下の枠は durability で、「後から来た購読側に、過去のメッセージを渡すか」と添えられています。枠の中には3つの行があります。5番は、左が transient_local、右が transient_local で、つながり、過去の分も届く。6番は、左が transient_local、右が volatile で、つながるが、過去の分は届かない。7番は、左が volatile、右が transient_local で、ここも赤い点線で、つながらない。

図の番号の1番から7番は、2-2節の表の番号と同じです。

読み方の目安は、こうです。配信する側が、購読する側の要求と同じか、それより手厚いものを提供していれば、つながります。reliable は best_effort より手厚く、transient_local は volatile より手厚い。要求の方が手厚いと、4番と7番のように、つながりません。

## 2. 仕様

### 2-1. qos_talker と qos_listener

仕様は、ノード、役割、トピックと型、動作、の4列の表で、2行あります。

1行目、qos_talker。役割は Publisher。トピックは qos_test で、型は std_msgs/msg/String。1秒ごとに、msg 0、msg 1、と番号を増やして送る。QoS は、ROS のパラメータの reliability と durability で決める。reliability は reliable か best_effort、durability は volatile か transient_local で、既定は reliable と volatile。深さは10。

2行目、qos_listener。役割は Subscriber。トピックと型は同じ。受け取った文字列をログに出す。QoS は、talker と同じパラメータで決める。

パラメータの与え方の例として、原文は、ros2 run learn_py qos_talker の後に、--ros-args を付け、-p で reliability を best_effort に、もう1つの -p で durability を volatile にするコマンドを載せています。実際に実行して結果を見るのは、5節の実験です。

パラメータの詳しい扱いは、次のフェーズ3-3 で学びます。宣言、取得、型の決まり方は3-3 の3節、起動のときの -p は5-2節、実行中に値を読み書きする ros2 param は5-3節、YAML のファイルでの指定は5-4節で扱います。ここでは、起動のときに値を渡せることだけを使います。

### 2-2. 試す組み合わせ、1番から7番

5節の実験で試す組み合わせに、番号を振っておきます。表は2つで、どちらも、番号、qos_talker、qos_listener、期待、の4列です。

1つ目の表は reliability の組み合わせで、durability は、どちらも既定の volatile です。4行あります。

1番。talker が reliable、listener が reliable。つながる。

2番。talker が reliable、listener が best_effort。つながる。

3番。talker が best_effort、listener が best_effort。つながる。

4番。talker が best_effort、listener が reliable。つながらない。送る側と受ける側の両方に、相性が合わないという警告が出る。

2つ目の表は durability の組み合わせで、reliability は、どちらも既定の reliable です。3行あります。

5番。talker が transient_local、listener が transient_local。つながり、後から起動した listener にも、過去のメッセージが、深さの10件まで届く。

6番。talker が transient_local、listener が volatile。つながるが、過去の分は届かない。

7番。talker が volatile、listener が transient_local。つながらない。

必須は1番と4番の2つで、残りは任意です。

## 3. Python の版、learn_py

learn_py の内側の learn_py のフォルダに、qos_util.py、qos_talker.py、qos_listener.py の3つを作ります。qos_util.py はノードではなく、talker と listener が共通で使う関数、make_qos を置く部品です。使うメッセージの型は std_msgs のもので、依存はフェーズ3-1 で package.xml に足してあるので、新しく足す依存はありません。

主な API は、やりたいことと API の2列の表で、3行あります。

QoS の設定は、rclpy.qos から QoSProfile、ReliabilityPolicy、DurabilityPolicy を import し、QoSProfile に、depth を10、reliability と durability を指定して作る。

パラメータの宣言と取得は、self.declare_parameter に名前と既定の値を渡し、self.get_parameter に名前を渡して、get_parameter_value() の string_value で文字列を取り出す。

同じパッケージの自作のモジュールを使うには、learn_py.qos_util から make_qos を import する。パッケージの名前、点、モジュールの名前、の形です。

### qos_util.py

qos_util.py は、十数行の短いファイルで、make_qos という関数を1つだけ持ちます。make_qos は、reliability_str と durability_str の2つの文字列を受け取り、前半で想定していない値なら ValueError を投げ、後半で QoSProfile を作って返します。要の行は、QoSProfile に、depth を10、文字列に応じた ReliabilityPolicy と DurabilityPolicy を渡す行です。

原文の解説です。役割は、talker と listener が同じ規則で QoS を組み立てるための、共通の関数です。ノードではないので main は無く、setup.py の entry_points にも足しません。entry_points に書くのは、ros2 run で起動する実行ファイルだけです。

想定していない文字列を ValueError にしているのは、綴りの誤りに気づけるようにするためです。黙って既定の値に落とすと、実験の結果が何の設定だったか分からなくなります。

QoSProfile の3つの項目の意味です。depth は、履歴、つまり history の深さで、直近の何件までを持つかです。ここでは、直近の10件を持つ、keep last の設定になります。reliability の RELIABLE は、届くまで再送を試みる。BEST_EFFORT は、再送せず、取りこぼしを許す代わりに軽い。durability の VOLATILE は、送った時点でつながっている相手にだけ届く。TRANSIENT_LOCAL は、Publisher が直近の depth 件を覚えておき、後から接続した購読する側にも渡す。

1か所にまとめる理由。この実験では、talker と listener が、同じ文字列を同じ QoS に変換することが前提です。同じ関数を2つのファイルに書き写すと、片方だけを直したとき、例えば受け付ける文字列を増やしたり depth を変えたりしたときに、食い違いが起きます。そうなると、QoS が合わないからつながらないのか、変換の規則がずれているのかが、区別できなくなります。1か所に置けば、直す場所も1つで済みます。

置き場所と読み込み方。learn_py の内側の learn_py のフォルダに置いた .py のファイルは、パッケージ learn_py の一部としてインストールされます。そのため、同じパッケージの別のファイルから、learn_py.qos_util から make_qos を import する形で読み込めます。ファイルの名前の .py は付けません。

#### 補足: 変数の名前とパラメータの名前を分けている理由

このサンプルでは、パラメータの名前は reliability ですが、その値を受け取るローカル変数と、make_qos の引数は、reliability_str と名前を変えています。durability も同じです。

一般的な書き方として、パラメータの値を同じ名前の変数に入れる書き方は、ROS2 のコードでよく見かけます。どのパラメータがどの変数に入るかが、一目で分かるからです。C++ では、メンバ変数の末尾にアンダースコアを付けて区別することが多い。例えば、パラメータの period の値を、メンバ変数の period_ に入れます。末尾のアンダースコアは、フェーズ3-1 の C++ の版の pub_ や timer_ と同じ、メンバ変数の印です。受け取った値を、型も意味も変えずにそのまま使うなら、同じ名前でも困ることは少ない、とあります。

このサンプルで分けた理由は、パラメータから読んだ文字列、例えば reliable を、API が求める列挙の値、例えば ReliabilityPolicy の RELIABLE に変換してから渡すからです。仮に全部を reliability と書くと、同じ名前が、中身の違う3つのものを指すことになります。

原文は、それを、書く場所、何の名前か、中身、名前を変えられるか、の4列の表で整理しています。3行あります。

1行目。declare_parameter や、-p で reliability を best_effort にする所に書くのは、ROS のパラメータの名前です。中身は、ノードの外から見える設定の名前で、変えることはできますが、起動のコマンドも変わります。

2行目。reliability_str への代入や、make_qos の引数に書くのは、コードの中の変数や引数の名前です。中身は、reliable か best_effort の文字列で、名前は自由に付けられます。

3行目。QoSProfile の reliability に書くのは、rclpy の API のキーワード引数の名前です。中身は、ReliabilityPolicy の RELIABLE などの列挙の値で、名前は API が決めているので変えられません。

特に、make_qos の中の、reliability に、文字列が reliable なら RELIABLE を渡す、という行は、変数も reliability という名前だと、1行の中に同じ名前の別物が並んでしまいます。そこで、学習のためのサンプルとして、読み間違いを防ぐことを優先し、パラメータから読んだ、変換する前の文字列だと分かるように、末尾に _str を付けました。一方で、ログやエラーの文言は、ノードを使う人が -p で指定する名前と対応させるため、パラメータの名前のままにしています。

実務での目安として、値を別の型や意味に変換する前と後で名前を分ける書き方、例えば _str や _name を付けたり、変換した後を reliability_policy としたりする書き方は、ROS2 に限らずよく使われます。どちらの書き方にするかは、チームのコーディングの規約があれば、それに従う、とあります。

### qos_talker.py

qos_talker.py は、40行ほどのコードで、骨組みはフェーズ3-1 の talker と同じです。違いは __init__ の前半で、パラメータの reliability と durability を、既定の reliable と volatile で宣言して読み、QoS の設定をログに出します。要の行は、create_publisher に、String 型、qos_test、そして make_qos で組み立てた QoS を渡す行です。on_timer は、msg と番号の文を送ってログに出します。

原文の解説の要点です。役割は、QoS を起動のときのパラメータで切り替えられる Publisher で、5節の相性の実験の送り手になります。

import について。QoS の組み立ては make_qos に任せたので、このファイルでは rclpy.qos を import しません。import の並べ方は、ROS2 の標準の Linter の ament_flake8、つまり colcon test で動くものの規則に合わせています。この規則では、自分のパッケージの learn_py も、rclpy や std_msgs と同じ、インストール済みのパッケージとして扱い、モジュールの名前のアルファベットの順に、learn_py、rclpy、std_msgs と並べます。一般的な Python の慣習の PEP 8 では、自作のモジュールを最後に分けて書くことも多いのですが、ROS2 のパッケージでは Linter の規則に従う方が、colcon test で指摘されずに済みます。

次の2つ、declare_parameter と get_parameter は、フェーズ3-3 で詳しく学ぶパラメータの先取りです。ここでは、こう書くと -p で渡した値を読める、と分かれば十分です。

declare_parameter は、パラメータを名前と既定の値付きで宣言します。宣言していないパラメータは、-p で渡しても受け付けられません。既定の値の型、ここでは文字列が、そのパラメータの型になります。

get_parameter が返すのは Parameter、つまり名前と値の組です。そこから get_parameter_value() で、値の入れ物の ParameterValue を取り出し、型に合ったフィールド、文字列なら string_value を読みます。整数なら integer_value、実数なら double_value です。フェーズ3-3 では、型を問わずに値を取り出せる、より短い、get_parameter の value の書き方を使います。

起動のときに QoS の設定をログに出しているのは、今どの設定で動いているかを、ターミナルで確かめるためです。実験で設定を取り違えないための工夫です。

on_timer のログの publish は、送ろうとした印で、受け取る側がいるかどうかに関係なく出ます。つながらない組み合わせでも、talker の側は普通にログを出し続けます。相手が受け取れないだけで、送り手のエラーにはなりません。

観察のポイントは、2-2節の番号で書かれています。実験は5節でまとめて行うので、ここでは何を見るかだけを押さえます。5番では、talker を先に起動して5秒ほど待ってから、listener を起動します。listener が起動した直後に、msg 0 から数件が一気に届けば成功です。depth が10 なので、10件を超えて溜まっても、届くのは直近の10件までです。4番と7番のような、つながらない組み合わせでは、QoS が合わないという警告が、ログに出ることが多い。出方はノードや言語で違いうるので、実験で確かめます。ros2 topic info /qos_test -v で、Publisher と Subscription の QoS を見比べます。

つまずきやすい点。ノードのコンストラクタで例外が出ると、spin に入る前に、プロセスごと落ちます。invalid reliability という ValueError が出たら、パラメータの綴りか、大文字と小文字を疑います。

### qos_listener.py

qos_listener.py も、40行ほどのコードです。パラメータと QoS のログは talker と同じで、要の行は、create_subscription に、String 型、qos_test、self.on_message、make_qos の QoS を渡す行です。on_message は、受け取った文をログに出します。

解説の要点です。create_subscription の引数の順は、型、トピックの名前、コールバック、QoS です。create_publisher の、型、名前、QoS とは違い、コールバックが QoS より前に来ます。順を逆にすると、型のエラーになります。on_message は、メッセージが届くたびに呼ばれ、コールバックは spin の中で呼ばれるので、spin に入っていないと何も起きません。self.sub に持っているのは、後から参照できるようにするためで、Python ではノードも内部で持っているので、必須ではありません。make_qos は talker と同じく qos_util.py から読み込むので、同じパラメータの値を渡せば、必ず同じ QoS が組み立てられます。

観察のポイント。listener を起動したときの QoS のログを、talker の側の値と見比べます。つながるか、つながらないかは、この2つの組、つまり購読する側の要求と、配信する側の提供で決まります。つながらないとき、received のログは1件も出ません。

### 登録とビルド

setup.py の entry_points に、qos_talker と qos_listener の2行を足します。前の節までの行は残します。形は、実行ファイルの名前、イコール、パッケージとモジュール、コロン、main です。entry_points を変えたときは、--symlink-install でもビルドし直しが必要です。コンマの付け忘れや、リストの外へ書く誤りに注意します。

cd で ~/ros2_ws に移り、colcon build --symlink-install に --packages-select learn_py を付けてビルドし、source install/setup.bash を実行します。期待する結果は、learn_py の Finished と、1つのパッケージが終わったという Summary が出ることです。ros2 pkg executables learn_py を実行すると、今回足した qos_listener と qos_talker の2行が、すでにある実行ファイルと一緒に並びます。

## 4. C++ の版、learn_cpp

このフェーズの C++ の版は、任意の発展です。フェーズ5 の車両のシミュレーションは Python で作ると決めているので、ここで作らなくても先へ進めます。Python の版との違いは、各ファイルの解説、特に qos_util.hpp の解説にある対応の表を読めば、概要がつかめます。

learn_cpp の include の下の learn_cpp のフォルダに、共通のヘッダの qos_util.hpp を、learn_cpp の src に、qos_talker.cpp と qos_listener.cpp を作ります。Python の版の qos_util.py と同じく、make_qos をヘッダの1か所に置き、2つのノードから使います。include の下の learn_cpp のフォルダは、フェーズ2 の ros2 pkg create が、空のフォルダとして作ってあります。std_msgs の依存はフェーズ3-1 で足してあるので、package.xml と find_package の追加は要りません。

主な API は、やりたいことと API の2列の表で、3行あります。

QoS の設定は、rclcpp::QoS を深さ10 で作り、reliable、best_effort、transient_local、durability_volatile のメソッドで設定する。

パラメータの宣言と取得は、declare_parameter に、山括弧で std::string を付けて、名前と既定の値を渡す。宣言と同時に値が返ります。

共通のヘッダを使うには、learn_cpp/qos_util.hpp を include し、CMake で target_include_directories に、ターゲット、PRIVATE、include を書く。

### qos_util.hpp

qos_util.hpp は、30行ほどのヘッダで、インクルードガードの中に、inline の関数の make_qos を1つ持ちます。想定していない値なら std::invalid_argument を throw し、深さ10 の rclcpp::QoS を作って、文字列に応じたメソッドで設定してから返します。

原文の解説の要点です。Python の版の qos_util.py にあたる、talker と listener の共通の部品で、1か所にまとめる理由も同じです。

make_qos について。Python では QoSProfile に引数で渡していたものを、C++ では、深さ10 の rclcpp::QoS を作ってから、メソッドで設定を上書きしていきます。原文は、Python と C++ の2列の表で、対応を4行にしています。ReliabilityPolicy の RELIABLE は qos.reliable()。BEST_EFFORT は qos.best_effort()。DurabilityPolicy の TRANSIENT_LOCAL は qos.transient_local()。VOLATILE は qos.durability_volatile()。最後だけ名前が durability_volatile なのは、volatile が C++ の予約語だからです。

インクルードガードは、同じヘッダが1つの .cpp の中で2回以上読み込まれても、中身が1回分だけになるようにする決まり文句です。マクロの名前は、パッケージの名前、アンダースコア2つ、ファイルの名前、アンダースコア、を大文字にする形が、ROS2 の C++ のコードでよく使われます。

inline は、ヘッダに関数の本体まで書くときに付けます。ヘッダは複数の .cpp に読み込まれるので、inline が無いと、同じ関数が複数の場所で定義されたことになり、1つの実行ファイルに複数の .cpp をまとめたときに、リンクのエラーになります。今回は talker と listener が別の実行ファイルなので起きませんが、ヘッダに本体を書くときの決まりとして付けておきます。

引数の const の std::string の参照は、コピーせず参照で受け取り、書き換えない、という意味です。std::invalid_argument の throw は、Python の ValueError に相当します。コンストラクタで例外が出ると、ノードは作られず、プロセスが例外で終わります。stdexcept と string は、このヘッダ自身が使うものなので、ヘッダの中で読み込みます。読み込む側の .cpp に頼らないことで、どの .cpp から読み込んでも、そのままビルドできます。

### qos_talker.cpp

qos_talker.cpp は、50行ほどのコードで、骨組みはフェーズ3-1 の talker.cpp と同じです。違いはコンストラクタの前半で、declare_parameter で2つのパラメータを宣言し、返ってきた値を reliability_str と durability_str に入れます。要の行は、create_publisher に、String 型、qos_test、make_qos の QoS を渡す行です。

解説の要点です。

ヘッダの include のパスは、include のフォルダからの相対のパスで書きます。include のフォルダをどこから探すかは、後で CMakeLists.txt の target_include_directories で指定します。自分のパッケージのヘッダも、rclcpp などと同じ、二重引用符の形で読み込みます。

declare_parameter は、フェーズ3-3 の先取りで、宣言と同時に値が返ります。このサンプルの Python の版では、宣言の後に get_parameter で読み直していました。rclpy の declare_parameter も、値の入った Parameter を返すので、declare_parameter の value と、1行で書くこともできます。const auto で受けると std::string になります。テンプレートの引数の型を付けないと、既定の値の型から推論される場面もありますが、文字列は std::string と明示しておく方が安全です。受け取る変数をパラメータの名前から変えているのは、Python の版と同じ理由です。

RCLCPP_INFO はログのマクロで、書式は printf の形式です。%s には、std::string そのものではなく、c_str() で得る C の形式の文字列を渡します。そのまま渡すと、実行のときに不正な表示になったり、落ちたりします。

create_publisher の QoS の引数には、整数の代わりに rclcpp::QoS を渡せます。

msg と count_ の連結について。msg という文字の並びの方は const char のポインタですが、右の辺が std::string なので連結できます。std::to_string を通さずに、count_ を直接足すと、意図しないポインタの演算になります。count_ を0 で初期化するのは、Python の self.count を0 にするのにあたります。

観察のポイントと落とし穴は、Python の版と同じです。QoS の扱いは言語で変わらないので、5-3節の課題3 で、Python の版と C++ の版を組み合わせて確かめます。

### qos_listener.cpp

qos_listener.cpp は、40行ほどのコードです。パラメータとログは talker と同じで、要の行は、create_subscription に、String 型、qos_test、make_qos の QoS、そして受け取った文をログに出すラムダ式を渡す行です。

解説の要点です。create_subscription の引数の順は、トピックの名前、QoS、コールバックです。Python の版は、コールバックが先で QoS が後なので、言語を行き来するときに取り違えやすい。コールバックのラムダの引数は、メッセージへの const の参照で、コピーが起きません。本文の中で get_logger() を呼ぶために、this の取り込みが要ります。sub_ を SharedPtr のメンバとして持つのは、Publisher と同じ理由で、消えると購読が解かれるからです。memory の include は、SharedPtr のために置いてあります。

観察のポイント。2-2節のつながらない組み合わせ、4番と7番では、received が出ず、警告だけが出ます。警告の末尾には、どの QoS のポリシーが合わないかが示されます。

### CMakeLists.txt とビルド

CMakeLists.txt に追記し、install(TARGETS ...) に名前を足します。前の節までの分は残します。足すのは、qos_talker と qos_listener のそれぞれについて3行ずつです。add_executable で、実行ファイルの名前と src の下のソース。target_include_directories で、その名前と、PRIVATE と、include。ament_target_dependencies で、その名前と、rclcpp と std_msgs。そして install(TARGETS ...) を、hello、talker、listener、sine_pub、sine_sub、turtle_circle、qos_talker、qos_listener の8つの名前に並べ直します。

説明は5つです。

add_executable は、ソースから実行ファイルをビルドする指定で、Python の entry_points にあたります。

target_include_directories は、そのターゲットをビルドするとき、二重引用符の include のヘッダを、パッケージの include のフォルダからも探すように指定します。これで、learn_cpp/qos_util.hpp の include が、include の learn_cpp の qos_util.hpp を指します。PRIVATE は、このターゲットの中だけで使う、という意味です。フェーズ2 の ros2 pkg create が hello のために書いた target_include_directories は、もっと長い形で、ビルドするときとインストールした後で、ヘッダの探し先を切り替える書き方です。この切り替えが要るのは、主にヘッダをライブラリとして、ほかのパッケージへ公開する場合で、実行ファイルがパッケージの中のヘッダを読むだけの今回は、この短い形で足ります。

ament_target_dependencies は、ターゲットが使うパッケージを、ターゲットごとに並べます。2つのノードは String を使うので std_msgs、それと rclcpp が必要です。

install(TARGETS ...) は、ビルドした実行ファイルを、install の learn_cpp の lib の learn_cpp に置きます。ここに名前が無いと、ros2 run で、実行ファイルが見つからない、と言われます。すでにある名前は消さずに残し、新しい2つを足します。

install(TARGETS ...) の turtle_circle は、フェーズ3-2a で C++ の版の turtle_circle を作った場合だけ書きます。作っていないのに名前を書くと、存在しないターゲットを指定したことになり、CMake の段階でビルドがエラーになります。

cd で ~/ros2_ws に移り、colcon build --symlink-install に --packages-select learn_cpp を付けてビルドし、source install/setup.bash を実行します。期待する結果は、learn_cpp の Finished と、1つのパッケージが終わったという Summary が出ることです。install(TARGETS ...) に、作っていないノードの名前、例えば turtle_circle が残っていると、learn_cpp が Failed になり、その上に、install に書いたターゲットの turtle_circle が存在しない、という趣旨の CMake のエラーが出ます。

## 5. 実験: QoS の相性を確かめる

ros2 run learn_py の qos_talker と qos_listener で、2-2節の表のとおりにパラメータを変えて起動します。C++ の版でも同じです。ターミナルを2つ使い、T1 に talker、T2 に listener を置きます。概要をつかむだけなら、5-1節の1番と4番の2つを試せば十分です。

### 5-1. reliability、1番から4番

まず1番、つまり両方とも既定の reliable で、つながる様子を見ます。T1 で ros2 run learn_py qos_talker、T2 で ros2 run learn_py qos_listener を、パラメータを付けずに実行します。

期待する結果は、こうです。どちらのターミナルも、起動した直後の1行目に、reliability が reliable、durability が volatile という QoS の設定のログが出ます。続いて、T1 には publish と msg と番号のログが1秒ごとに、T2 には received と同じ番号のログが1秒ごとに出ます。

1行目は、パラメータから読み取った QoS の設定です。ここで意図した組み合わせになっているかを、まず確かめます。T2 に received が1秒ごとに出れば、つながっています。時刻の数字は、実行ごとに変わります。

次に、両方を Ctrl+C で止めてから、4番を試します。T1 では、qos_talker を、--ros-args と、-p で reliability を best_effort にして起動します。T2 では、qos_listener を、-p で reliability を reliable にして起動します。

期待する結果は、こうです。talker は publish のログを出し続けますが、listener には received が1行も出ません。その代わり、両方のターミナルに、WARN の警告が出ます。listener の側の警告は、qos_test のトピックで新しい Publisher を見つけたが、それが提供する QoS は合わないので、そこからはメッセージを受け取らない、という内容の英語の文です。talker の側の警告は、新しい Subscription を見つけたが、それが要求する QoS は合わないので、そこへはメッセージを送らない、という内容です。どちらも末尾に、最後に合わなかったポリシーとして、RELIABILITY と示されます。これは Python の版の場合で、C++ の版では、末尾のポリシーの名前が RELIABILITY_QOS_POLICY になります。

警告は、相手を見つけたが、QoS が合わないのでメッセージをやり取りしない、という意味で、最後のポリシーの名前が、食い違っている項目を示します。エラーで止まるわけではないので、ログを見落とすと、何も起きないように見えます。配信する側と受ける側がどうやってお互いを見つけ、QoS を突き合わせているのか、reliable では届いたことをどう確かめているのかは、Tips 集の4節、トピックの通信の裏側にまとめてある、とあります。

4番のまま、3つ目のターミナルで、ros2 topic info /qos_test -v を実行して、QoS を確かめます。

期待する結果は、こうです。型は String で、Publisher の数は1。その Publisher のノードの名前は qos_talker で、QoS は、Reliability が BEST_EFFORT、History と Depth が KEEP_LAST の10、Durability が VOLATILE です。続いて、Subscription の数は1。そのノードの名前は qos_listener で、QoS は、Reliability が RELIABLE、History と Depth が KEEP_LAST の10、Durability が VOLATILE です。

Publisher の数と Subscription の数は、どちらも1 で、ROS2 から見ると、両方いる。それでもつながらない理由は、Reliability の行の食い違い、つまり Publisher が BEST_EFFORT、Subscription が RELIABLE であることにあります。つながらない場合は、この2つを見比べて、どちらが食い違っているかを読み取ります。

任意の2番と3番も、同じ要領で、-p の reliability の値を、2-2節の表のとおりに変えて起動します。どちらもつながります。

### 5-2. durability、5番から7番、任意

5番、つまり両方とも transient_local の組み合わせでは、talker を先に起動して、5秒ほど待ってから、listener を起動します。T1 で、qos_talker を、-p で durability を transient_local にして起動し、5秒ほど待ちます。T2 で、qos_listener を、同じく -p で durability を transient_local にして起動します。

期待する結果は、listener が起動した直後に、それまでの分がまとめて届くことです。QoS の設定のログに続いて、received の msg 0、1、2、3、4 が、時刻がほぼ同じで一気に出て、5 からは1秒ごとに出ます。talker を10秒以上待ってから listener を起動した場合は、深さの10 を超えた古い分は捨てられているので、直近の10件だけが届きます。

6番、つまり talker が transient_local で listener が volatile では、同じ手順でも過去の分は届かず、listener が起動した後に送られた番号から始まります。

7番、つまり talker が volatile で listener が transient_local では、つながらず、5-1節の4番と同じ形の警告が出ます。違いは、末尾のポリシーの名前が DURABILITY になることです。ros2 topic info /qos_test -v では、Durability の行が食い違っています。

### 5-3. 課題

課題は3つです。

課題1 は任意で、2-2節の表の1番から7番をすべて試し、期待どおりの結果になるかを確かめることです。つながらない組み合わせ、つまり4番と7番では、受ける側のログに、合わないポリシーの名前を含む警告が出ることを確かめます。

課題2 も任意で、つながらない組み合わせのまま、ros2 topic info /qos_test -v で、Publisher と Subscription のどの行が食い違っているかを読み取ることです。

課題3 は、C++ の版を作った場合で、Python の版の talker と C++ の版の listener、その逆でも、4番と7番が同じ結果になることを確かめることです。QoS の扱いが言語に依存しないことを確かめます。

## 6. QoS の互換性のまとめ

5節で確かめた組み合わせを、判定の規則として、4つにまとめています。

1つ目、reliability。best_effort の Publisher と reliable の Subscriber の組み合わせ、つまり4番だけがつながりません。Subscriber が要求する reliable の品質を、Publisher が best_effort で提供できないからです。それ以外の、1番、2番、3番はつながります。

2つ目、durability。volatile の Publisher と transient_local の Subscriber、つまり7番だけがつながりません。理由は reliability と同じ構造で、Subscriber が要求する transient_local を、Publisher が提供できないからです。

3つ目、共通の考え方。QoS の互換性は、Subscriber が要求する最低の品質が、Publisher が提供する品質以下であるか、で決まります。要求と提供のモデルです。Publisher の側の設定を緩めると、つながらなくなることがある、と覚えておくと判断しやすい、とあります。

4つ目。この判定は、Python の版と C++ の版のどちらの組み合わせでも、同じ結果になります。QoS は ROS2 に共通の仕組みで、言語には依存しません。

## 7. 実務への手がかり

センサのデータは、多少欠けても最新が大事なので、best_effort にすることが多い。ROS2 には、そのための定義済みの設定があります。Python では、rclpy.qos から qos_profile_sensor_data を import します。C++ では、rclcpp::SensorDataQoS() を使います。フェーズ5 の車両のシミュレーションで、センサに相当する速度や、制御の指令のトピックに、どの QoS を使うかを考える材料になります。

## 8. Python の版と C++ の版の違いのまとめ

3節と4節のサンプルを比べると、QoS の中身、つまり depth、reliability、durability と、互換性の判定は、言語によらず同じです。違いは、組み立て方と、パラメータの取り方に集まります。

原文は、観点、Python、C++ の3列の表で、6行にまとめています。

1行目、QoS の組み立て。Python は、QoSProfile に、depth と、ReliabilityPolicy の RELIABLE などの列挙の値を、引数で渡す。C++ は、深さ10 の rclcpp::QoS を作ってから、reliable() や transient_local() などのメソッドで上書きする。volatile は予約語なので、durability_volatile() になる。

2行目、パラメータの宣言と取得。Python は、このサンプルでは、declare_parameter の後に、get_parameter から get_parameter_value() の string_value で取り出す2行。declare_parameter の戻り値から読むこともできる。C++ は、山括弧で std::string を付けた declare_parameter が、宣言と同時に値を返す1行。

3行目、想定外の値の扱い。Python は ValueError を raise する。C++ は std::invalid_argument を throw する。

4行目、共通の関数の切り出し。Python は、同じパッケージのモジュールの qos_util.py に置き、learn_py.qos_util から import する。ビルドの設定は変えなくてよい。C++ は、include の learn_cpp の qos_util.hpp に inline の関数として置き、include する。CMakeLists.txt に target_include_directories を足す。

5行目、create_subscription の引数の順。Python は、型、トピックの名前、コールバック、QoS。C++ は、トピックの名前、QoS、コールバックで、型はテンプレートの引数。

6行目、ログへの文字列の渡し方。Python は、f文字列をそのまま渡す。C++ は printf の形式で、std::string には c_str() を付ける。

言語を行き来するときに、最も取り違えやすいのは、create_subscription のコールバックと QoS の順です。順を間違えると、Python では実行のときの型のエラー、C++ ではビルドのエラーになります。

## 9. つまずきやすい点

原文では、症状と、確かめることの2列の表で、6行あります。

1行目。invalid reliability という ValueError が出る場合。パラメータの綴りを確かめる。reliable か best_effort で、小文字です。

2行目。Python の版を起動したときに、learn_py.qos_util というモジュールが見つからない、という ModuleNotFoundError が出る場合。qos_util.py を、learn_py の内側の learn_py のフォルダ、つまり setup.py のある階層の1つ下の learn_py に置いたか。ファイルの名前の綴り。--symlink-install を付けずにビルドしている場合は、ファイルを足した後に、ビルドし直しが要ります。

3行目。C++ の版のビルドで、learn_cpp/qos_util.hpp が見つからない、という致命的なエラーが出る場合。ヘッダを、learn_cpp の include の learn_cpp のフォルダに置いたか。CMakeLists.txt の、エラーが出たターゲットに、target_include_directories を書いたか。

4行目。5番で、過去の分が届かない場合。talker が transient_local か、listener の側も transient_local か。talker を先に起動して待ったか。

5行目。合わないという警告が出ない場合。警告は、ノードのログ、つまりターミナルに出ます。rqt_console でも確かめられます。

6行目。C++ の版のビルドで、install に書いたターゲットの turtle_circle が存在しない、というようなエラーが出る場合。install(TARGETS ...) に、作っていないノードの名前を書いていないか。

## 10. 次へ

フェーズ3-3 で、パラメータを本格的に扱います。ここで使った -p の指定と、YAML での指定を学びます。

## 11. 公式ドキュメントと参考資料

確認の状況が書かれています。2026年9月20日の時点で、下の資料は企画の文書に載せた URL で、今回は確かめ直していません。docs.ros.org は、ボット対策で本文の取得が拒否されます。

公式の資料は、ROS 2 Jazzy の2つです。QoS の設定のページで、ここには互換性の一覧の表があります。そして、rclcpp の QoS クラスのページです。公式のドキュメントと食い違う場合は、公式を優先する、とあります。

原文の最後には、出典の注記があります。各サンプルの API の使い方は、公式のドキュメントを参考にしました。ROS 2 のドキュメントは CC BY 4.0 です。ノードの名前、仕様、コード、文章は独自に書いたもので、一語ずつの転載ではありません。

以上で、フェーズ3-2b の手順書の話を終わります。

## 出典について

この原稿は、SanghunIm1991 さんの [ros2MinimalPhysicalAi の「フェーズ3-2b 手順書: QoSの相性を体験する」](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/docs/phase3_2b_qos.md)を、聞くために要約・意訳したものです。図の [phase3_2_qos.svg](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/docs/img/phase3_2_qos.svg) は、言葉で説明しました。元にしたのは、[2026年10月14日の版](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/132df7b64d48d560def7ec7149f7003938d3d8e5/docs/phase3_2b_qos.md)です。原文の文章と図と同じく、[クリエイティブ・コモンズ 表示 4.0 国際ライセンス](https://creativecommons.org/licenses/by/4.0/deed.ja)で提供します。

原稿の中に原文の表記のまま書いたコマンドと、コードの関数やクラスの名前は、原文では [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0) の対象です。ライセンスの全文は、原文のリポジトリの [LICENSE-APACHE-2.0](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/LICENSE-APACHE-2.0) にあります。サンプルコードは写さず、役割と要の行を言葉で説明しました。

原文では、API の使い方を [ROS 2 Documentation](https://docs.ros.org/en/jazzy/)（Open Robotics、[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)）の公式ドキュメントを参考にしたとしています。表示の例と警告の文面は、各ツールの表示を言葉で説明したものです。
