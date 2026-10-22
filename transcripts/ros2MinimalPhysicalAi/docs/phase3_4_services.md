<!--
聞くための原稿（読み上げでは読まれない記録）
原文: SanghunIm1991/ros2MinimalPhysicalAi の main ブランチの docs/phase3_4_services.md（図は docs/img/phase3_4_add_seq.svg と docs/img/phase3_4_reset_flow.svg）
原文のコミット: 132df7b64d48d560def7ec7149f7003938d3d8e5（2026-10-14）
作成: 2026-10-20、Claude Code が手作業で作成（原稿化スキルはまだない）
原文のライセンス: 文章と図は CC BY 4.0、コードとコマンドは Apache-2.0（それぞれ LICENSE の2と1）。ros2 interface show で表示する型の定義（example_interfaces と common_interfaces の std_srvs、Apache License 2.0）は、LICENSE の「第三者の著作物」にある。原文の末尾に、API の使い方は公式チュートリアル（ROS 2 Documentation、CC BY 4.0）を参考にした、とある。この原稿は、原文を聞くために要約・意訳したもの（改変あり）
方針: 英語の略語や製品名、関数やクラスの名前、短いコマンドは原文の表記のまま書く。サンプルコード6本と、package.xml・CMakeLists.txt・setup.py に足す行は、写さずに、ブロックの役割と要の行を言葉で説明した。型の定義は写さず、項目の名前と型だけを言葉で書き、コメントは「ある」とだけ伝えた。期待する結果（ログ、ros2 service call の表示）も、何が表示されるかを言葉で説明した。図と表（2組のサンプル、仕様、主な API、各コードの部分の説明、言語の組み合わせ、トピックとサービスの使い分け、Python版と C++版の違い、つまずきやすい点）は言葉で説明する。文字数の上限は設けない
省いたもの: URL、型の定義へのリンク、ログの時刻の数字
-->

# フェーズ3-4: サービス、つまり要求と応答（聞くための原稿）

これは、ros2MinimalPhysicalAi という教材の、フェーズ3-4 の手順書の話です。1回の要求に1回の応答を返す通信、サービスを扱います。概要をつかむ程度でよく、サンプルは Python の版と C++ の版の両方が載っています。

想定する環境は、WSL2 と Ubuntu 24.04 と ROS2 Jazzy です。前提は、フェーズ3-1 から3-3 を終えていることです。所要時間の目安は1コマです。言語は Python で、C++ の版は任意です。使う標準のインターフェースは、example_interfaces の srv の AddTwoInts と、std_srvs の srv の Trigger の2つです。

原文には、位置づけの囲みがあります。サービスは、フェーズ5 の車両のシミュレーションでは使いません。ノード同士はトピックでつなぎ、ゲインはパラメータで変えます。ここでは、サービスは1回の要求に1回の応答を返す通信で、トピックとはこう使い分ける、という考え方と、コマンドラインからサービスを呼ぶ方法をつかめば十分です。なお、フェーズ3-3 の ros2 param set も、裏では、ノードが自動で持つパラメータ用のサービスを呼んでいます。

必須の範囲は、Python の版の add_server を書いて、ros2 service call で呼ぶところまでです。つまり、4-2節の add_server.py から、6-1節の、コマンドラインからも呼べる、の所までです。クライアントの非同期の呼び出しの add_client、Trigger を使う counter_node、C++ の版の5節は、任意の発展です。作らないノードがある場合は、setup.py の entry_points にも、その行を書きません。

サンプルまで書いて動かす場合の進め方は、これまでと同じです。サンプルは、手順書を作るときにビルドを確かめ、手順は2026年9月27日に実機で確かめています。期待する結果は、コードと ROS2 の仕様から筆者が想定したもので、実機で手順を実行して問題が無いことを確かめてありますが、表示を1つずつ見比べてはいない、とあります。

この原稿では、サンプルコードと型の定義を書き写さず、役割と要の行を言葉で説明します。

## 0. 学習目標と完了の条件

必須、つまり概要をつかむための条件は3つです。

1つ目。標準の .srv の定義、つまり要求と応答の項目を、ros2 interface show で読める。

2つ目。サービスのサーバ、つまり create_service を Python で書き、ros2 service call で呼べる。

3つ目。トピックとの使い分け、つまり継続的な流れか、要求から応答か、を自分の言葉で説明できる。

任意の発展の条件も3つです。4つ目は、クライアント、つまり create_client の非同期の呼び出し、Python の call_async や C++ の async_send_request と、結果の待ち方を説明できること。5つ目は、1つのノードにトピックとサービスを同居させること、つまり counter_node。6つ目は、C++ の版を書くことです。

## 1. 全体像

この手順書のサンプルは、目的の違う2組に分かれています。原文は、組、ノード、使うサービスの型、見どころ、範囲、の5列の表で、2行にまとめています。

1組目は足し算です。ノードは add_server と add_client で、型は AddTwoInts。見どころは、サービスの基本、つまりサーバが要求を受けて応答を返し、クライアントが呼んで結果を待つことです。add_server は必須、add_client は任意です。

2組目は、カウンタのリセットです。ノードは counter_node で、型は Trigger。見どころは、1つのノードに、トピックの配信とサービスのサーバを同居させることです。範囲は任意です。

2つの組は、互いに呼び合いません。以降の節も、この順に分けて書かれています。

原文の図は2つで、どちらも SVG と mermaid の版があります。

1つ目の図は、add_client が呼ぶ場合の、足し算の流れを表すシーケンス図です。左に add_client、右に add_server の箱があり、それぞれから下へ点線が伸びています。まず、add_client から自分自身へ戻る矢印で、wait_for_service、つまりサーバがいるかを待ちます。次に、add_client から add_server へ、要求の Request で、a が3、b が4 を送ります。add_server は、自分自身へ戻る矢印で、sum イコール a 足す b を計算します。そして、add_server から add_client へ、点線の矢印で、応答の Response で、sum が7 を返します。最後に、add_client が自分自身へ戻る矢印で、結果をログに出して終了します。

2つ目の図は、Trigger を使うカウンタのリセットの流れです。左から、灰色の箱の「ros2 service call、/reset_counter」、青い箱の counter_node、灰色の箱の「ros2 topic echo」が並びます。左の箱から counter_node へ、「Trigger の要求、中身なし」の矢印があり、counter_node から左の箱へ、「success と message」の矢印が戻ります。そして、counter_node から右の箱へ、「/counter、Int32 を1秒ごと」の矢印があります。

次に、インターフェースの定義を確かめておきます。ros2 interface show で、example_interfaces/srv/AddTwoInts と、std_srvs/srv/Trigger を表示します。

期待する結果は、こうです。どちらの型の定義も、ハイフン3つの行で、上と下に分かれています。上が要求、つまり Request で、下が応答、つまり Response です。AddTwoInts は、要求が int64 の a と b の2つ、応答が int64 の sum の1つです。Trigger は、ハイフン3つの行の上に何も無い、つまり要求が空の型で、応答は、bool の success と、string の message の2つです。Trigger の2つの項目には、それぞれ説明のコメントが付いています。

各行は、型、名前、の形です。int64 は64ビットの整数、bool は真偽の値、string は文字列で、ROS2 のメッセージで使える基本の型です。基本の型の一覧は、公式のドキュメントの、インターフェースのページの、フィールドの型の節にあります。

## 2. 仕様

### 2-1. 1組目の足し算、add_server と add_client

仕様は、ノード、役割、サービスと型、動作、の4列の表で、2行あります。

1行目、add_server。役割はサーバ。サービスは add_two_ints で、型は example_interfaces/srv/AddTwoInts。要求の a と b を足した sum を返し、ログに出す。

2行目、add_client。役割はクライアント。サービスは add_two_ints。ROS のパラメータの a と b、どちらも整数で、既定は1 と2 を要求に入れて1回呼び、結果をログに出して終わる。サーバがいなければ、5秒待ってあきらめる。

### 2-2. 2組目のカウンタのリセット、counter_node

仕様は、項目と内容の2列の表で、3行あります。

ノードの名前と実行ファイルの名前は、counter_node で、Python の版と C++ の版で同じ。

トピックは counter で、型は std_msgs/msg/Int32。1秒ごとに、0 から数を増やした値を送る。

サービスは reset_counter で、型は std_srvs/srv/Trigger。呼ばれたら、カウントを0 に戻し、success を true、message にリセットする前の値を入れて返す。

## 3. 準備: 依存の追加

package.xml に、example_interfaces と std_srvs の depend の行を、2行足します。C++ の版を作る場合は、learn_cpp の側にも足します。必須の範囲だけなら、learn_py の側の example_interfaces だけでかまいません。

C++ の版を作る場合は、learn_cpp の CMakeLists.txt の、すでにある find_package の並びに、example_interfaces と std_srvs の find_package を、REQUIRED を付けて足します。

導入の確認として、ros2 interface show で AddTwoInts を表示します。example_interfaces は Desktop Install に含まれていて、無い場合は、sudo apt install で ros-jazzy-example-interfaces を入れます。期待する結果は、1節と同じく、int64 の a から始まる定義が表示されれば、導入済みです。導入されていない場合は、example_interfaces というパッケージを知らない、というようなエラーになります。

## 4. Python の版、learn_py

learn_py の内側の learn_py のフォルダに、1組目の足し算の add_server.py と add_client.py、2組目のカウンタのリセットの counter_node.py を作ります。作るのは、進める範囲の分だけでかまいません。

### 4-1. 主な API、rclpy

やりたいことと API の2列の表で、5行あります。

サーバを作るには、self.create_service に、型、サービスの名前、コールバックを渡す。コールバックは、request と response を受け取り、response を返します。

クライアントを作るには、self.create_client に、型とサービスの名前を渡す。

サーバとの待ち合わせは、client の wait_for_service に、timeout_sec を5.0 にして渡す。戻り値は真偽の値です。

非同期の呼び出しは、client の call_async に request を渡し、future を受け取る。

結果の待ち方は、rclpy.spin_until_future_complete にノードと future を渡した後に、future の result() を読む。

非同期の呼び出しと、結果の待ち方、つまり future の意味と待ち方の注意は、クライアントを書く4-3節で説明されます。

### 4-2. 1組目の足し算: サーバ、add_server.py。必須

add_server.py は、30行あまりのコードで、クラスと main の2つのブロックからなります。要の行は、__init__ で create_service に、AddTwoInts 型、add_two_ints、self.on_request を渡す行と、on_request の中で、response.sum に a と b の和を入れて、response を返す行です。

原文の解説です。役割は、add_two_ints という名前のサービスを公開し、要求が来るたびに a 足す b を計算して返すことです。全体の流れは、ノードを作る、サービスを登録する、spin で要求を待ち続ける、の3段階です。トピックの listener とほぼ同じ骨組みで、違いは、受け取ったら結果を返す点だけです。

原文は、部分と、何をしているか、の2列の表で、5行を説明しています。

super().__init__ は、ノードの名前を add_server にして、親のクラスを初期化します。

create_service の引数は、サービスの型、サービスの名前、要求が来たときに呼ぶ関数、の3つです。型は .srv のファイルに対応し、要求の a と b、応答の sum の形を決めます。戻り値の self.srv は、変数に持っておきます。

on_request は、サービスのコールバックです。request には相手が送った値が、response には中身が空の応答が入って渡されます。

response.sum に a と b の和を入れる行は、応答の欄を埋めます。AddTwoInts の a、b、sum は int64 です。

response を return する行。Python では、応答を戻り値として返します。return を忘れると、サーバの側のコールバックでエラーになり、クライアントは応答を受け取れません。つまずきやすい点です。

main は、フェーズ3-1 のノードと同じ決まった形です。rclpy.spin の中で、要求が来るとコールバックが呼ばれます。

観察のポイント。サーバだけを起動しても何も起きず、ログも出ません。要求が来て初めて動きます。ros2 service list -t で、/add_two_ints と AddTwoInts の型が見えること、ros2 service call で呼んだときに、サーバの側のログが出ることを確かめます。

### 4-3. 1組目の足し算: クライアント、add_client.py。任意

4-2節のサーバを呼ぶ側です。add_client.py は、40行ほどのコードです。クラスの __init__ は、パラメータの a と b を宣言して、クライアントを作るだけで、仕事の本体は main 関数にあります。main は、サーバを待つ、要求を作る、非同期に送る、結果を待ってログに出す、の4段で進みます。要の行は、wait_for_service、call_async、spin_until_future_complete の3つを呼ぶ行です。

原文の解説です。役割は、サーバを見つけ、a と b を送って1回だけ呼び、答えをログに出して終わることです。サーバや Publisher と違い、spin し続けるノードではなく、1回の仕事が終わったら main を抜けて終わる形になっています。

__init__ では、パラメータの a と b を既定の値付きで宣言し、これはフェーズ3-3 の復習です。そしてクライアントを作ります。クライアントを作っただけでは、まだ通信は始まりません。

wait_for_service は、サーバが見つかるまで最大5秒待ち、見つかれば True、見つからなければ False を返します。これを挟まずにいきなり呼ぶと、サーバが起動する前だった場合に、要求が届きません。

要求の組み立てで、get_parameter の value の、value を付け忘れると、Parameter のオブジェクトそのものを詰めようとして、型のエラーになります。

call_async は、要求を送って、すぐに future、つまり後で結果が入る箱を返します。ここでは結果はまだありません。

spin_until_future_complete は、future に結果が入るまでノードを回します。この間に、応答を受け取る処理が動きます。これが終わってから、future の result() で Response を取り出します。result() が None のときは呼び出しが失敗していて、future の exception() で原因が見られます。

なぜ非同期か、という囲みもあります。call_async は応答を待たずにすぐ戻るので、結果をいつ取りに行くかは、自分で決める必要があります。このコードは、main の中で spin_until_future_complete を使って待ちます。ノードのコールバックの中から別のサービスを呼びたい場合は、この待ち方は使えないので、future が終わったときに呼ばれるコールバックで結果を受ける、などの別の方法になります。このフェーズでは扱いません。

そして、重要という囲みがあります。spin_until_future_complete は、コールバックの中では呼ばず、main の中で使います。コールバックは spin に呼ばれて動いているので、そのノードはすでに回っています。その中でさらにノードを回そうとすると、Python では、executor がすでに spin している、という RuntimeError、C++ では、ノードがすでに executor に登録されている、という例外で止まります。

落とし穴は2つです。1つ目。wait_for_service が False のとき、このコードは return するだけで、終了のコードは0 のままになります。C++ の版は1 を返します。スクリプトから結果を判定したい場合は、ここが差になります。2つ目。-p で a を3.0 のように実数で渡すと、宣言した整数の型と合わず、パラメータの設定でエラーになります。整数で渡します。

動作の確認。サーバを起動した状態で、ros2 run learn_py add_client を実行すると、既定なら1 足す2 は3 と出ます。-p で a を10、b を20 にしても試します。サーバを止めた状態で実行すると、約5秒後にエラーのログが出て終わることも確かめます。

### 4-4. 2組目のカウンタのリセット、counter_node.py。任意

ここからは、1組目の足し算とは別の組で、このノード1つで動きます。counter_node.py は、40行あまりのコードです。

クラスの __init__ で、Publisher、タイマー、サービスの3つを作り、コールバックは、送る on_timer と、リセットする on_reset の2つです。要の行は、create_service に、Trigger 型、reset_counter、self.on_reset を渡す行です。

原文の解説です。役割は、1秒ごとにカウントを配信しつつ、reset_counter のサービスで0 に戻せることです。1つのノードに、トピックの発行、つまりタイマーと、サービスのサーバが同居する例で、トピックは継続的な流れ、サービスは必要なときの操作、という使い分けを、1本のノードで体感できます。

原文は、部分と、何をしているか、の2列の表で、5行を説明しています。

self.count を0 にする行。ノードが持つ状態で、タイマーのコールバックと、サービスのコールバックの両方が、同じ変数を読み書きします。

create_publisher と create_timer は、フェーズ3-1 と同じで、1秒ごとに on_timer が呼ばれます。

create_service で作る Trigger は、要求が空で、応答が真偽の success と、文字列の message だけの、標準のサービスの型です。引数の要らない合図を送る用途に向きます。

on_timer は、今の count を配信してから1増やします。最初に配信される値は0 です。

on_reset は、success を真にし、message にリセットする前の値を入れてから、count を0 に戻します。順が大事で、先に0 にすると、リセットする前の値が取れません。

on_reset の引数の request は、Trigger の要求が空なので使っていません。それでも、引数としては必要です。省くと、コールバックの呼び出しでエラーになります。

同じ変数を2つのコールバックが触っても安全なのは、rclpy.spin の既定の実行の方式、つまりシングルスレッドでは、コールバックが同時には動かず、1つずつ順に処理されるからです。複数のスレッドの実行の方式に変えると、この前提が崩れて、排他の制御が必要になります。このフェーズでは扱いません。

観察のポイント。ros2 topic echo /counter を見ながら、ros2 service call で /reset_counter を Trigger 型で呼び、値が0 に戻ること、応答の message に、直前の値が入っていることを確かめます。

### 4-5. 登録とビルド、2組に共通

setup.py の entry_points に、作ったノードの行を足し、ビルドし直します。3行のうち、1行目が add_server、2行目が add_client、3行目が counter_node で、作らなかったノードの行は書きません。形は、これまでと同じ、実行ファイルの名前、イコール、パッケージとモジュール、コロン、main です。

cd で ~/ros2_ws に移り、colcon build --symlink-install に --packages-select learn_py を付けてビルドし、source install/setup.bash を実行します。期待する結果は、learn_py の Finished と、1つのパッケージが終わったという Summary が出ることです。

## 5. C++ の版、learn_cpp

このフェーズの C++ の版は、任意の発展です。フェーズ5 の車両のシミュレーションは Python で作ると決めているので、ここで作らなくても先へ進めます。Python の版との違いは、8節のまとめを読めば概要がつかめます。C++ の版を作らない場合は、C++ に向けた依存の追加も要りません。

learn_cpp の src に、add_server.cpp、add_client.cpp、counter_node.cpp を作ります。

### 5-1. 主な API、rclcpp

やりたいことと API の2列の表で、5行あります。

サーバを作るには、create_service に山括弧で型を付け、サービスの名前とコールバックを渡す。コールバックは、Request の SharedPtr と Response の SharedPtr を受け取り、response に書き込みます。Python と違い、戻り値はありません。

クライアントを作るには、create_client に山括弧で型を付け、サービスの名前を渡す。

サーバとの待ち合わせは、client の矢印の wait_for_service に、5s を渡す。戻り値は真偽の値です。

非同期の呼び出しは、client の矢印の async_send_request に request を渡し、future を受け取る。

結果の待ち方は、rclcpp::spin_until_future_complete にノードと future を渡し、戻り値が SUCCESS なら、future の get() を呼ぶ。

Python との違いの見どころは、応答を返すのか、書き込むのか、そして、型の名前が Request と Response という、入れ子の型になることです。

### 5-2. 1組目の足し算: サーバ、add_server.cpp

add_server.cpp は、40行ほどのコードです。要の行は、コンストラクタで create_service に、山括弧で AddTwoInts を付けて、add_two_ints と、ラムダ式を渡し、service_ に入れる行です。ラムダ式の中で、response の矢印の sum に、a と b の和を書き込みます。

解説の要点です。Python の版と同じサーバで、差分を中心に読みます。

using の別名について。example_interfaces の srv の AddTwoInts は、.srv から自動で作られた型で、その中に Request と Response が入れ子になっています。ヘッダの名前は、型の名前をスネークケースにした add_two_ints.hpp で、CMakeLists.txt の依存に example_interfaces が必要です。

create_service は、型をテンプレートの引数で渡し、サービスの名前とコールバックを渡します。戻り値は Service の SharedPtr で、メンバ変数の service_ に持ちます。持たないと、この行の終わりで片付けられて、サービスが消えます。

コールバックの引数。request と response の両方が shared_ptr で渡されるので、矢印で欄にアクセスします。応答は、戻り値ではなく、response に書き込みます。これが Python との最大の違いです。ラムダは this で自分自身、つまりノードを取り込んでいて、get_logger() を呼ぶために必要です。

static_cast の long long と %lld について。a、b、sum は int64_t です。printf の仲間の書式の指定では、int64_t の実体が、環境によって long か long long かが違うため、long long にそろえて %lld で出す、という安全策です。

main は、rclcpp::spin に make_shared で作った AddServer を渡して、ノードを作ることと待ち受けを1行で行います。

観察のポイント。Python の版のサーバと入れ替えても、同じクライアントから同じ結果が返ることです。サービスの名前と型が同じなら、作った言語は関係ありません。

### 5-3. 1組目の足し算: クライアント、add_client.cpp

add_client.cpp は、40行ほどのコードで、クラスを作らず、main の中にすべてを順に書いています。流れは Python の版と同じ4段で、要の行は、wait_for_service、async_send_request、spin_until_future_complete の3つを呼ぶ行です。

解説の要点です。Python の版と同じ、待つ、要求を作る、非同期に送る、結果を待つ、の流れを、main の中に順に書いています。クラスを作らず、rclcpp::Node の make_shared でノードを直接作るのが、Python の版との構造の違いです。

declare_parameter は、型をテンプレートの引数で指定して宣言し、宣言のときに値を受け取ります。Python の版の、declare_parameter と get_parameter の value の2段階が、1行にまとまっています。

5s は5秒を表すリテラルで、chrono_literals の using が無いとコンパイルできません。wait_for_service の戻り値が false なら、エラーのログを出し、shutdown して、終了のコードの1 で終わります。Python の版は0 のままです。

要求は make_shared で shared_ptr として作り、矢印で a と b を詰めます。async_send_request は、Python の call_async に相当し、shared_future という future を返します。

spin_until_future_complete の戻り値は FutureReturnCode です。SUCCESS のときだけ、future の get() で、shared_ptr の応答を取り出し、sum を読みます。それ以外の、TIMEOUT や INTERRUPTED は、失敗として扱います。Python の、result() が None でないか、の判定にあたります。

落とし穴。future の get() は、結果が入っていない状態で呼ぶと、待たされるか、例外になります。先に、戻り値が SUCCESS であることを確かめてから呼ぶ、という順を守ります。また、spin_until_future_complete をサービスのコールバックの中で呼ぶと、例外で止まります。4-3節の、重要の囲みと同じ理由です。

動作の確認。Python の版と同じように、ros2 run learn_cpp add_client を、パラメータ無しと、a を10、b を20 にした場合で、サーバありとなしの両方で試します。サーバなしのときは、約5秒後にエラーのログが出て、echo の、ドル記号と疑問符で、終了のコードの1 が見えます。

### 5-4. 2組目のカウンタのリセット、counter_node.cpp

ここからは、1組目とは別の組で、4-4節の Python の版と同じ仕様です。counter_node.cpp は、50行ほどのコードです。コンストラクタで、Publisher、タイマー、サービスの3つを作り、リセットの処理は、create_service に渡すラムダ式に直接書いています。要の行は、その create_service に、山括弧で Trigger を付けて、reset_counter とラムダ式を渡す行です。

解説の要点です。

create_wall_timer は、1秒の周期のタイマーで、ラムダを通してメンバ関数を呼んでいます。

create_service の Trigger は、型もヘッダも std_srvs のパッケージのもので、CMakeLists.txt の依存に std_srvs が要ります。

コールバックの1つ目の引数、つまり要求に名前が無いのは、Trigger の要求は空で使わないので、あえて変数の名前を書かないからです。名前を付けて使わないと、使っていない引数だという警告が出るので、この書き方が定番です。

message に、文字列とカウンタをつないで、リセットする前の値を入れ、その後で count_ を0 にします。順は Python の版と同じで、先に0 にすると、リセットする前の値が取れません。ログの %s には c_str() が要ります。

data に count_ を後置で増やしながら入れるのは、今の値を data に入れてから、count_ を1増やす、という意味です。配信される最初の値は0 で、Python の版の、配信してから足す、と同じ結果になります。

メンバ変数の pub_、timer_、service_ は、どれも持っておく必要があり、消えると機能が止まります。count_ は、spin の既定では、コールバックが1つずつ順に呼ばれるので、排他の制御なしで、2つのコールバックから触れます。

観察のポイント。Python の版と同じ6-2節の実験で、値が0 に戻ること、message にリセットする前の値が入ることを確かめます。Python の版と C++ の版で、結果が同じになるかも見比べます。

### 5-5. 登録とビルド、2組に共通

CMakeLists.txt に追記し、install(TARGETS ...) に名前を足します。これまでの分は残しますが、前のフェーズで C++ の版を作らなかったノードの名前は書きません。書くと、存在しないターゲットとして、ビルドがエラーになります。

足すのは、3組の add_executable と ament_target_dependencies です。1組目は add_server で、依存は rclcpp と example_interfaces。2組目は add_client で、依存は同じく rclcpp と example_interfaces。3組目は counter_node で、依存は rclcpp、std_msgs、std_srvs です。最初の2組が足し算、3組目がカウンタのリセットです。そして install(TARGETS ...) を、hello から counter_node までの12の名前に並べ直します。

cd で ~/ros2_ws に移り、colcon build --symlink-install に --packages-select learn_cpp を付けてビルドし、source install/setup.bash を実行します。期待する結果は、learn_cpp の Finished と、1つのパッケージが終わったという Summary が出ることです。

## 6. 実験

### 6-1. 1組目の足し算、add_server と add_client

必須の範囲だけを進めている場合は、T1 でサーバを起動したら、T2 のクライアントの代わりに、この後の、コマンドラインから呼ぶ ros2 service call を使います。

T1 で ros2 run learn_py add_server を実行し、add_client を作った場合は、T2 で ros2 run learn_py add_client に、--ros-args と、-p で a を3、b を4 にして実行します。

期待する結果は、こうです。T2 のクライアントは1行出して、すぐに終わり、プロンプトに戻ります。T1 のサーバは、呼ばれるたびに1行ずつログを出し、動き続けます。どちらのログにも、3 足す4 は7、という同じ計算の結果が出ます。サーバの側は、要求を受けて計算した記録、クライアントの側は、応答を受け取った記録です。

サーバを起動せずにクライアントだけを動かすと、約5秒待った後に、ERROR の印で、サービスの add_two_ints が使えない、というログを出して終わります。この節の末尾の課題1 で試します。

コマンドラインからも呼べます。ros2 service call で、/add_two_ints を、example_interfaces/srv/AddTwoInts の型で、引用符と波括弧で囲んだ、a が10、b が20 の要求を付けて呼びます。

期待する結果は、こうです。まず、サービスが使えるようになるのを待っている、という行が出ます。続いて、要求を作って送った、という行に、a が10、b が20 の要求の中身が表示されます。そして、response の見出しの下に、sum が30 の応答の中身が表示されます。T1 のサーバには、10 足す20 は30 のログが出ます。サーバから見ると、自作のクライアントからの要求も、コマンドラインからの要求も、区別がありません。

言語の組み合わせを試すこともできます。add_client と C++ の版を作った場合の任意の実験で、原文は、組み合わせ、T1、T2 の3列の表で、4行を挙げています。Python のサーバと Python のクライアント。Python のサーバと C++ のクライアント。C++ のサーバと Python のクライアント。C++ のサーバと C++ のクライアント。4つの組み合わせのどれでも、表示は同じになります。

課題は4つです。

課題1 は、add_client を作った場合で、サーバを起動しないでクライアントを起動し、5秒待ってあきらめるメッセージが出ることを確かめることです。

課題2 も、add_client を作った場合で、クライアントを先に起動し、5秒以内にサーバを起動して、呼び出しが成功することを確かめることです。wait_for_service の効果です。

課題3 は、ros2 service list -t、ros2 service type /add_two_ints、ros2 node info /add_server で、サービスがどう見えるかを確かめることです。

課題4 は、サーバの add_server の on_request の中に、Python なら time.sleep で3秒、C++ なら std::this_thread::sleep_for を入れて、クライアントの呼び出しが3秒止められることを確かめることです。その3秒の間に、別のターミナルから ros2 service call でもう1回呼ぶとどうなるかも考えます。既定の spin は、1つのスレッドでコールバックを1つずつ順に処理するので、1つ目の処理が終わるまで、2つ目は待たされます。

### 6-2. 2組目のカウンタのリセット、counter_node。任意

T1 で ros2 run learn_py counter_node、T2 で ros2 topic echo /counter、T3 で ros2 service call で /reset_counter を std_srvs/srv/Trigger の型で呼びます。

期待する結果を、T2 で数字が7 まで進んだ所で T3 を実行した例で説明します。T2 では、data が6、7 と進んだ後、0、1 と、0 から数え直します。T3 では、要求を作って送った、という行に、空の Trigger の要求が表示され、続いて response の見出しの下に、success が True で、message が、counter reset、was 8、の応答が表示されます。T1 の counter_node には、同じ、counter reset、was 8、のログが出ます。

説明は2つです。1つ目。counter_node は、配信のたびにはログを出さず、リセットされたときだけ1行出します。2つ目。応答の was 8 が、最後に見えた7 より1大きいのは、on_timer が、配信してから1足す作りだからです。count には、次に配信する予定の値が入っています。どちらの値を返すのが仕様として自然か、考えてみるとよい、とあります。

echo の値が0 に戻り、サービスの応答に、success の True と、リセットする前の値の message が入っていることを確かめます。C++ の版を作った場合は、C++ の版でも同じように確かめます。

課題5 は発展で、Trigger のクライアントを自分で書き、counter_node をリセットするだけのノードを作ることです。AddTwoInts のクライアントとの違いは、要求に中身が無い点だけです。

## 7. トピックとサービスの使い分け

原文は、観点、トピック、サービスの3列の表で、4行にまとめています。

1行目、通信の形。トピックは、一方向で継続的。サービスは、要求から応答で、1回。

2行目、相手を待つか。トピックは待たない。サービスは応答を待つ。非同期でも、結果は待ちます。

3行目、向く用途。トピックは、センサの値や、指令を続けて送ること。サービスは、状態のリセット、設定の取得、一度だけの計算。

4行目、フェーズ5 での使いどころ。トピックは、速度や制御の指令。サービスは、シミュレーションのリセットや、制御の有効と無効の切り替え。

長くかかる処理で、途中経過を知りたい場合は、サービスではなく、フェーズ3-5 のアクションを使います。

## 8. Python の版と C++ の版の違いのまとめ

原文は、観点、Python、C++ の3列の表で、6行にまとめています。

1行目、サーバのコールバックの、応答の返し方。Python は、request と response を受け取り、response を埋めて return する。忘れるとエラー。C++ は、Request と Response の SharedPtr を受け取り、戻り値は無く、response の矢印の sum のように、直接書き込む。

2行目、クライアントの構造。Python は、Node を継承したクラスを作り、main から呼ぶ。C++ は、クラスを作らず、rclcpp::Node の make_shared で直接ノードを作り、main の中に、手続きとして書く。

3行目、wait_for_service。Python は、timeout_sec を5.0 にして呼ぶ。C++ は、chrono_literals の 5s を渡す。

4行目、結果の待ち方。Python は、spin_until_future_complete の後、future の result() を読み、None なら失敗。C++ は、spin_until_future_complete の戻り値が SUCCESS かを判定し、成功なら future の get()。

5行目、Request と Response の型の名前。Python は、AddTwoInts の点の Request。C++ は、コロン2つで入れ子の型として、AddTwoInts の Request にアクセスし、using で別名を付けるのが定石。

6行目、サーバが起動していないときの終了のコード。Python は、return するだけで0 のまま。C++ は、1 を返して、明示的に異常な終わりを示す。

サーバの側の、応答を返す Python と、応答に書き込む C++ の違いが、最も間違えやすい点です。C++ で return を書いてもコンパイルのエラーにならず、単に無視されるので、気づきにくい落とし穴になる、とあります。

## 9. つまずきやすい点

原文では、症状と、確かめることの2列の表で、6行あります。

1行目。クライアントが固まる場合は、サーバが動いているか。ros2 service list に出るか。サービスの名前の綴り。

2行目。Python のクライアントが反応しない場合は、spin_until_future_complete を呼んでいるか。コールバックの中で呼んでいないか。

3行目。C++ で %ld の警告が出る場合は、int64_t は環境で long か long long かが違うので、static_cast の long long と %lld にそろえる。

4行目。Python で、サーバが応答しない場合は、コールバックの最後で response を return しているか。

5行目。ビルドで example_interfaces が見つからない場合は、package.xml の depend と、CMakeLists.txt の example_interfaces の find_package。

6行目。ros2 service call の引数が通らない場合は、YAML の書式。引用符と波括弧で囲み、コロンの後ろに空白を入れる。

## 10. 次へ

フェーズ3-5 で、途中経過を返せる、アクションを扱います。

## 11. 公式ドキュメントと参考資料

確認の状況が書かれています。2026年9月20日の時点で、下の資料は企画の文書に載せた URL で、今回は確かめ直していません。docs.ros.org は、ボット対策で本文の取得が拒否されます。

公式の資料は3つです。ROS 2 Jazzy の、Python で簡単なサービスとクライアントを書くチュートリアル、C++ で書くチュートリアル、そして std_srvs の定義がある、GitHub の ros2/common_interfaces です。公式のドキュメントと食い違う場合は、公式を優先する、とあります。

原文の最後には、出典の注記があります。各サンプルの API の使い方は、公式のチュートリアルを参考にしました。ROS 2 のドキュメントは CC BY 4.0 です。ノードの名前、仕様、コード、文章は独自に書いたもので、一語ずつの転載ではありません。期待する結果に載せた ros2 interface show の表示は、example_interfaces と common_interfaces の型の定義で、Apache License 2.0 です。

以上で、フェーズ3-4 の手順書の話を終わります。

## 出典について

この原稿は、SanghunIm1991 さんの [ros2MinimalPhysicalAi の「フェーズ3-4 手順書: サービス（要求と応答）」](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/docs/phase3_4_services.md)を、聞くために要約・意訳したものです。図の [phase3_4_add_seq.svg](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/docs/img/phase3_4_add_seq.svg) と [phase3_4_reset_flow.svg](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/docs/img/phase3_4_reset_flow.svg) は、言葉で説明しました。元にしたのは、[2026年10月14日の版](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/132df7b64d48d560def7ec7149f7003938d3d8e5/docs/phase3_4_services.md)です。原文の文章と図と同じく、[クリエイティブ・コモンズ 表示 4.0 国際ライセンス](https://creativecommons.org/licenses/by/4.0/deed.ja)で提供します。

原稿の中に原文の表記のまま書いたコマンドと、コードの関数やクラスの名前は、原文では [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0) の対象です。ライセンスの全文は、原文のリポジトリの [LICENSE-APACHE-2.0](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/LICENSE-APACHE-2.0) にあります。サンプルコードは写さず、役割と要の行を言葉で説明しました。

原文のうち、ros2 interface show の表示として載せた型の定義は、[example_interfaces](https://github.com/ros2/example_interfaces) と [common_interfaces](https://github.com/ros2/common_interfaces) の std_srvs（どちらも Apache License 2.0）のものです。この原稿では、それを写さず、項目の名前と型を言葉で説明しました。原文では、API の使い方を [ROS 2 Documentation](https://docs.ros.org/en/jazzy/)（Open Robotics、[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)）の公式チュートリアルを参考にしたとしています。表示の例は、各ツールの表示を言葉で説明したものです。
