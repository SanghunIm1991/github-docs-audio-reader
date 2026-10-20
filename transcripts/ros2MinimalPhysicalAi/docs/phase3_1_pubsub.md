<!--
聞くための原稿（読み上げでは読まれない記録）
原文: SanghunIm1991/ros2MinimalPhysicalAi の main ブランチの docs/phase3_1_pubsub.md（図は docs/img/phase3_1_topics.svg と docs/img/phase3_1_spin.svg）
原文のコミット: fe96bffa42d20ef559b3d6995e44b90379b249f5（2026-10-15）
作成: 2026-10-20、Claude Code が手作業で作成（原稿化スキルはまだない）
原文のライセンス: 文章と図は CC BY 4.0、コードとコマンドは Apache-2.0（LICENSE の1と2）。原文の末尾に、API の使い方は公式チュートリアル（ROS 2 Documentation、CC BY 4.0）を参考にし、コードと文章は独自に書いた、とある。この原稿は、原文を聞くために要約・意訳したもの（改変あり）
方針: 英語の略語や製品名、関数やクラスの名前、短いコマンドは原文の表記のまま書く。8本のサンプルコードと、setup.py・CMakeLists.txt・package.xml に足す行は、写さずに、ブロックの役割と要の行を言葉で説明した。期待する結果（各ツールの表示とログ）も写さず、何が表示されるかを言葉で説明した。図と表（仕様、主な API、スマートポインタの書き方、言語をまたいだ接続、Python版と C++版の違い、つまずきやすい点）は言葉で説明する。文字数の上限は設けない
省いたもの: URL、日本語の記事の題名（記事が1本あることだけ触れた）、ログの時刻の数字、型の定義へのリンク
-->

# フェーズ3-1: Publisher と Subscriber、つまりトピックを Python と C++ で書く（聞くための原稿）

これは、ros2MinimalPhysicalAi という教材の、フェーズ3-1 の手順書の話です。同じ仕様のノードを Python と C++ の両方で書き、動きと書き方の違いを比べます。

想定する環境は、WSL2 と Ubuntu 24.04 と ROS2 Jazzy です。前提は、フェーズ2 を終えていること、つまり ros2_ws の src に learn_py と learn_cpp があり、colcon build --symlink-install が通ることです。所要時間の目安は1コマから2コマです。言語は Python と C++ の両方で、Python、C++ の順に進めることを勧めています。

原文には、進め方の囲みがあります。2節の仕様は、何を作るかの定義で、rclpy や rclcpp の API の使い方までは書いていません。この時点では API を知らないので、仕様だけを見て同じコードを書くのは無理があって当然で、それでよい、とあります。まず、3節と4節の冒頭の、主な API の表で、必要な API をつかみ、続くサンプルコードと解説を読んで、1行ずつ何をしているかを理解します。分かったら、変数の名前やログの文言を変える、送る値や周期を変える、フィールドを増やす、といった改造を、実際に手を動かしてやってみると身に付きます。サンプルは学習の手がかりとして最小限に書いたもので、公式のチュートリアルの転載ではありません。コードは、手順書を作るときにビルドを確かめ、手順は2026年9月26日に実機で実行して確かめています。出力が細部で違う場合は、実機の表示を優先します。期待する結果は、コードと ROS2 の仕様から筆者が想定したもので、実機で実行して確かめてあります。時刻、秒数、細かな行は、実行ごとに違います。

この原稿では、サンプルコードを書き写さず、それぞれのコードの役割と、要になる行を言葉で説明します。ツールの表示も、何が表示されるかを言葉で説明します。

## 0. 学習目標と完了の条件

完了の条件は4つです。

1つ目。Publisher、つまり create_publisher と、Subscriber、つまり create_subscription の基本の形を、Python と C++ の両方で書ける。

2つ目。タイマーのコールバックと、購読のコールバックが動く仕組み、つまり spin が呼び出すことを説明できる。

3つ目。Python の Publisher と C++ の Subscriber、その逆の組み合わせでも、通信できることを確かめる。

4つ目。ros2 topic の list、echo、hz、info と、rqt_graph で、自作のノードの通信を観察できる。

## 1. 全体像

原文の図は2つで、どちらも SVG と mermaid の版があります。

1つ目の図は、これから作る4つのノードのつながりです。2つの流れが、上下に並んでいます。上の流れは、左の talker の箱から右の listener の箱への矢印です。talker の箱には「1秒ごとに送信」、listener の箱には「受信してログ出力」と添えられ、矢印には /chatter というトピックの名前と、std_msgs/String という型が書かれています。下の流れは、左の sine_pub の箱から右の sine_sub の箱への矢印です。sine_pub には「10 Hz で送信」、sine_sub には「受信してログ出力」と添えられ、矢印には /sine と std_msgs/Float64 が書かれています。上と下の流れは、つながっていません。

2つ目の図は、コールバックの動き、つまり spin の役割を表すシーケンス図です。上に、左から main、spin、つまり executor、そしてノードのコールバック、の3つの箱が並び、それぞれから下へ点線が伸びています。まず、main から spin へ、rclpy.spin(node) または rclcpp::spin(node) という矢印があります。その下に、「シャットダウンまで」と書かれた loop の枠があり、その中に2つの矢印があります。1つは、spin から自分自身へ戻る矢印で、「タイマー満了」と「メッセージ到着」を待つ、という意味です。もう1つは、spin からノードのコールバックへの矢印で、該当するコールバックを呼ぶ、という意味です。枠の下には、黄色の注記があり、Ctrl+C で spin が戻り、後片付けをして終了する、と書かれています。

## 2. 仕様。Python の版と C++ の版で同じ

仕様は、ノード、役割、トピックとその型、動作、の4列の表で、4行あります。

1行目、talker。役割は Publisher。トピックは chatter で、型は std_msgs/msg/String。1秒ごとに、hello 0、hello 1、と番号を増やしながら送り、送った内容をログに出す。

2行目、listener。役割は Subscriber。トピックは chatter で、型は String。受け取った文字列をログに出す。

3行目、sine_pub。役割は Publisher。トピックは sine で、型は std_msgs/msg/Float64。10 Hz、つまり0.1秒の周期で、時刻 t に対して、sin の2π掛ける0.5掛ける t の値を送る。周期が2秒の正弦波です。

4行目、sine_sub。役割は Subscriber。トピックは sine で、型は Float64。受け取った値をログに出す。

補足が3つあります。1つ目。4つのノードは、2組に分かれます。1組目は talker と listener で、文字列を1秒ごとにやり取りする、トピックの通信の基本です。2組目は sine_pub と sine_sub で、数値の型の Float64 を10 Hz で送る、1組目の応用です。2つの組はトピックの名前が違うので、互いにつながりません。3節と4節のサンプルも、この順に分けて載せています。2つ目。キューの深さ、つまり QoS の depth は10 にします。QoS は、フェーズ3-2b で扱います。3つ目。実行ファイルの名前は、表のノードの名前と同じにします。例えば、ros2 run learn_py talker のように起動できます。

## 3. Python の版、learn_py

### 3-1. 書くもの

learn_py のパッケージの、内側の learn_py のフォルダの下に、4つのファイルを作ります。1組目の文字列の talker.py と listener.py、2組目の正弦波の sine_pub.py と sine_sub.py です。

主な API は、やりたいことと API の2列の表で、7行あります。

ノードを作るには、Node を継承したクラスを書き、super().__init__ にノードの名前を渡す。

Publisher を作るには、self.create_publisher に、メッセージの型、トピックの名前、10 を渡す。

Subscriber を作るには、self.create_subscription に、メッセージの型、トピックの名前、コールバック、10 を渡す。

タイマーは、self.create_timer に、秒の単位の周期と、コールバックを渡す。

ログを出すには、self.get_logger().info を使う。

送るには、publisher の publish に、メッセージを渡す。

起動と終わりは、rclpy.init、rclpy.spin、rclpy.try_shutdown の順に呼ぶ。

サンプルコードをファイルに置く方法、つまり touch と nano で貼り付ける方法と、VS Code で貼り付ける方法は、コードの置き方の手順書にまとめてあります。

#### 1組目のサンプル、talker.py

talker.py は、1秒ごとに hello と番号の文を chatter のトピックへ送るノードで、30行あまりのコードです。

先頭で、rclpy、外部からのシャットダウンを表す例外の ExternalShutdownException、ノードの基のクラスの Node、メッセージの型の String を import します。String は、data というフィールドを1つ持つだけのメッセージです。

次に、Node を継承した Talker というクラスがあります。__init__ の中身は4行です。super().__init__ に 'talker' を渡してノードの名前を決め、create_publisher で String 型、chatter、10 の Publisher を作って self.pub に入れ、番号の self.count を0 にし、create_timer で、1.0秒ごとに on_timer を呼ぶタイマーを作って self.timer に入れます。

on_timer は、String のインスタンスを作り、data に、f文字列で hello と self.count を埋め込んだ文を入れ、self.pub の publish で送り、get_logger().info で、publish という言葉と送った文をログに出し、番号を1増やします。

最後に main 関数があります。rclpy.init で初期化し、Talker を作り、try の中で rclpy.spin に渡します。except で KeyboardInterrupt と ExternalShutdownException を受け止めて何もせず、finally で destroy_node と rclpy.try_shutdown を呼びます。

原文の解説の要点です。

役割と流れ。全体は、ノードを作る、spin でコールバックを待ち続ける、Ctrl+C で後片付けをして終わる、という3段の構えです。この骨組みは、Python の版の4つのファイルのすべてで同じなので、ここで覚えておきます。

__init__ について。super().__init__ を呼ばないと、それより後の create で始まる関数が使えません。create_publisher の引数は、型、トピックの名前、QoS の depth の順です。10 は、送る側のキュー、つまりバッファの深さで、相手の受信が追いつかないときに、最大10件まで溜めておく、という意味です。create_timer の1つ目の引数は周期で、単位は秒の実数です。2つ目の引数は、呼んでほしい関数で、self.on_timer のように、括弧を付けずに関数そのものを渡します。括弧を付けると、その場で実行した結果を渡してしまいます。self.pub や self.timer に入れて持っているのは、後で使うため、また、何を持つノードかがコードから読み取れるようにするためです。Python では、ノードが内部でも持っているので、入れなくても動きます。詳しくは、4-1節の末尾の、スマートポインタの補足にあります。

on_timer について。ログの get_logger().info は、標準出力ではなく、ROS2 のロギングを通すので、時刻やノードの名前が付きます。

main について。rclpy.init は、ROS2 の通信の基盤の初期化で、ノードを作る前に必ず呼びます。rclpy.spin は、シャットダウンされるまで戻りません。中で、タイマーの満了とメッセージの到着を待ち、該当するコールバックを呼び出しています。spin を呼ばないと、コールバックが一度も呼ばれずにプログラムが終わります。try と except と finally は、Ctrl+C で出る KeyboardInterrupt、環境によっては ExternalShutdownException を受け止めて黙って抜け、finally で後片付けをするためです。try_shutdown は、すでにシャットダウンしていれば何もしない版なので、二重に呼んでもエラーになりません。

つまずきやすい点。main の関数の名前は、3-2節で setup.py に足す登録の行の末尾の名前と、一致させます。create_timer の周期に、整数の1 を渡しても動きますが、ミリ秒と勘違いして1000 を渡すと、約17分の周期になります。

観察のポイント。ros2 run learn_py talker で、1秒ごとに publish と hello と番号のログが出て、番号が1ずつ増えること。別のターミナルで ros2 topic echo /chatter をすると、同じ文が同じ順で見えることです。

#### 1組目のサンプル、listener.py

listener.py は、chatter のトピックを購読し、届いた文字列をログに出すノードです。import と main は talker とほぼ同じで、違うのはノードのクラスだけです。

Listener というクラスの __init__ では、super().__init__ に 'listener' を渡し、create_subscription に、String 型、chatter、self.on_message、10 を渡して、self.sub に入れます。on_message は、引数の msg を受け取り、received という言葉と msg.data をログに出すだけです。

解説の要点です。create_subscription の引数は、型、トピックの名前、コールバック、QoS の depth の順です。Publisher と違い、コールバックを3つ目の引数に渡します。Python の版では、コールバックの後ろに QoS が来ます。10 は受ける側のキューの深さで、コールバックの処理が遅れて、まだ処理していないメッセージが溜まったとき、最大10件まで持ちます。on_message の msg は、受け取った String のインスタンスで、msg.data で中身を取り出します。コールバックは spin の中から呼ばれるので、自分で呼び出すコードは書きません。

つまずきやすい点。トピックの名前や型が、送る側と1文字でも違うと、エラーも出ずに、何も受け取りません。ros2 topic list -t で、名前と型を確かめます。また、コールバックの中で、time.sleep などの長い処理を書くと、その間はほかのコールバックも呼ばれません。

観察のポイント。listener を talker より先に起動してもかまいません。後から起動した場合は、それまでに送られた分は受け取れず、起動した後に送られたものから表示されます。既定の QoS では、過去の分は保存されないからです。

#### 2組目のサンプル、sine_pub.py

ここからは、1組目とは別の組です。トピック sine で、数値の Float64 を10 Hz で送ります。ノードの骨組みは1組目と同じなので、違いを中心に読みます。

sine_pub.py は、先頭で math を import し、型は Float64 を import します。SinePub というクラスの __init__ では、ノードの名前を sine_pub にし、Float64 型、sine、10 の Publisher を作り、周波数の self.freq_hz を0.5 にし、0.1秒ごとに on_timer を呼ぶタイマーを作ります。on_timer は、self.get_clock().now() の nanoseconds に 1e-9 を掛けて、今の時刻 t を秒にし、Float64 のメッセージの data に、math.sin の、2.0 掛ける math.pi 掛ける self.freq_hz 掛ける t の値を入れて、publish します。ログは出しません。main は、ほかと同じ形です。

解説の要点です。

値の計算。sin の2π f t は、周波数 f ヘルツ、時刻 t 秒の正弦波です。freq_hz が0.5 なので、周期は、1 を0.5 で割って2秒です。この周期と、create_timer の周期の0.1秒は、別物です。前者は波の形で、後者は、何秒おきに標本を取って送るか、です。2秒の周期の波が、0.1秒おき、つまり1周期あたり20点で標本にされます。

時刻の取り方。get_clock().now() は、ノードが使う時計の今の時刻で、nanoseconds は整数のナノ秒です。1e-9 を掛けて秒にしています。ナノ秒から秒への換算は間違えやすいので、桁を意識します。

なぜ時計の時刻を使うか。カウンタを増やして0.1 を掛けてもよいのですが、時刻から計算する方が、タイマーの呼び出しが遅れても波の形が崩れず、値が実際の時刻に対応します。ROS2 の時計は、シミュレーションの時間を使う設定にも切り替えられますが、今回は触れません。

freq_hz を属性にしている理由は、6節の課題4 と、フェーズ3-3 のパラメータ化の準備です。定数を、コードのあちこちに直接書かないためです。

つまずきやすい点。math.sin はラジアンを取ります。度のつもりで360 を使うと、波になりません。2.0 掛ける math.pi の部分の括弧を落とす計算の誤りも多い、とあります。

観察のポイント。ros2 topic hz /sine が約10 Hz で、ros2 topic echo /sine の値が、マイナス1 から1 の間を、約2秒の周期で往復することです。

#### 2組目のサンプル、sine_sub.py

sine_sub.py は、sine のトピックを購読し、値を小数点以下3桁でログに出すノードです。構造は listener と同じで、ノードの名前が sine_sub、型が Float64、トピックが sine です。on_message は、sine という言葉の後に、msg.data を、f文字列の書式指定の :.3f で、小数点以下3桁にしてログに出します。この書式を外すと、桁がとても長い表示になり、ログが読みにくくなります。C++ の版の %.3f と同じ意味です。

観察のポイント。sine_pub と一緒に動かすと、ログの値が0 の近くから増えて1 に近づき、減ってマイナス1 に近づく、という往復が、約2秒の周期で見えます。10 Hz で流れるので、ログは1秒に10行出ます。

Python の版の4つのファイルに共通する要点は、ノードのクラスの __init__ で、Publisher、Subscription、Timer という通信の口を作り、コールバックに処理を書き、main の spin で回す、という形です。以降のフェーズでも、同じ形を使い回します。

### 3-2. 実行ファイルとして登録する

learn_py の setup.py の entry_points の、console_scripts のリストに、4行を足します。すでにある hello の行は残します。足す行は、talker、listener、sine_pub、sine_sub のそれぞれについて、実行ファイルの名前、イコール、learn_py のモジュールの名前、コロン、main、という形です。登録を足したので、この後はビルドし直しが必要です。--symlink-install でも同じです。

注意が2つあります。1つ目。最後の行の末尾のコンマは、誤りではありません。Python のリストや辞書では、最後の要素の後ろにもコンマを置いてよく、これをトレーリングコンマと呼びます。ros2 pkg create の雛形も、この書き方をしています。付けておくと、次に行を足すときに、前の行へコンマを足し忘れる事故が起きず、差分も1行で済みます。2つ目。字下げは、スペースでそろえます。括弧の内側なので、タブが混ざっても動きはしますが、colcon test で走るスタイルの検査の flake8 で、警告になります。

package.xml には、フェーズ2 で ros2 pkg create に --dependencies rclpy std_msgs を指定していれば、依存はすでに入っています。rclpy と std_msgs の depend の行です。package.xml を cat で見て、test_depend の行しか無い場合は、指定が抜けていました。その場合は、license の行の後ろに、その2行を手で足して、ビルドし直します。

この2行が無くても、この環境ではノードは動きます。rclpy も std_msgs も /opt/ros/jazzy に入っていて、そこから import できるからです。けれども、rosdep による依存の自動の導入や、別の環境でのビルドでは、依存が漏れるので、宣言しておくのが正しい形です。

### 3-3. ビルドして動かす

cd で ~/ros2_ws に移り、colcon build --symlink-install に --packages-select learn_py を付けてビルドし、source install/setup.bash を実行します。

ビルドの期待する結果は、learn_py の Finished の行と、1つのパッケージが終わったという Summary の行が出ることです。秒数は環境によって変わります。Failed や Aborted が出たら、その上に出ているエラーの文を読みます。

ターミナルを2つ使います。T1 で ros2 run learn_py talker、T2 で ros2 run learn_py listener を実行します。

期待する結果は、T1 には1秒ごとに1行ずつ、送ったログが出て、T2 には同じ文字列を受け取ったログが出ることです。Ctrl+C で止めるまで続きます。読み方は3つです。1つ目。ログの1行は、重要度の INFO、時刻、つまり1970年からの秒数、ノードの名前、本文、の並びです。時刻の数字は、実行するたびに変わります。2つ目。番号は0 から1ずつ増えます。listener を後から起動した場合は、起動する前に送られた分は表示されず、途中の番号から始まります。3つ目。Ctrl+C で止めると、プロンプトに戻ります。止めたときに、例外のトレースバックが出なければ、try と except と finally が効いています。

2組目の sine_pub と sine_sub も、同じようにターミナルを2つ使って動かします。1組目を止めてからでも、並べて動かしてもかまいません。トピックが違うので混ざりません。T1 で ros2 run learn_py sine_pub、T2 で ros2 run learn_py sine_sub を実行します。

期待する結果は、こうです。sine_pub はログを出さないので、T1 には何も表示されません。動いていないわけではありません。sine_sub の側には、1秒に10行、小数点以下3桁の値が出ます。値は0.1秒ごとに少しずつ変わり、約2秒で、マイナス1 から1 を1往復します。原文の例では、0.588 から増えて1.000 に達し、また減っていく様子が載っています。最初の値は起動した時刻で決まるので、例とは一致しません。見るべき点は、値が滑らかに増えたり減ったりし、プラスマイナス1 を超えないことです。

## 4. C++ の版、learn_cpp

### 4-1. 書くもの

learn_cpp の src のフォルダの下に、4つのファイルを作ります。1組目の talker.cpp と listener.cpp、2組目の sine_pub.cpp と sine_sub.cpp です。

主な API は、Python と同じ2列の表で、7行あります。

ノードを作るには、rclcpp::Node を public で継承したクラスを書き、コンストラクタで Node にノードの名前を渡す。

Publisher を作るには、create_publisher に、山括弧でメッセージの型を付け、トピックの名前と10 を渡す。

Subscriber を作るには、create_subscription に、山括弧でメッセージの型を付け、トピックの名前、10、コールバックを渡す。

タイマーは、create_wall_timer に、周期とコールバックを渡す。std::chrono_literals の 1s や 100ms が使えます。

ログを出すには、RCLCPP_INFO に、get_logger() と、書式の文字列と、値を渡す。

送るには、publisher の矢印の publish に、メッセージを渡す。

起動と終わりは、rclcpp::init、ノードを std::make_shared で作って rclcpp::spin に渡す、rclcpp::shutdown、の順。

Python との違いの見どころは3つです。型が、テンプレートの引数、つまり山括弧の中で明示されること。SharedPtr というポインタで持ち、Publisher は矢印で publish を呼ぶこと。そして、pub_ や timer_ のようなメンバ変数で持っておかないと、コンストラクタを抜けた時点で片付けられて、動かなくなることです。

#### 1組目のサンプル、talker.cpp

talker.cpp は、Python の talker.py と同じ仕様のノードで、40行ほどのコードです。

先頭で、標準の chrono、memory、string と、rclcpp/rclcpp.hpp、std_msgs/msg/string.hpp を include し、using namespace std::chrono_literals を書きます。

Talker というクラスは、rclcpp::Node を public で継承します。public の部分のコンストラクタは、初期化のリストで Node に "talker" を渡し、本体で、create_publisher で String 型、chatter、10 の Publisher を作って pub_ に入れ、create_wall_timer で、1s ごとに、this を取り込んだラムダ式から on_timer を呼ぶタイマーを作って timer_ に入れます。private の部分には、on_timer と、3つのメンバ変数があります。on_timer は、String のメッセージを作り、data に hello と、count_ を後置で増やしながら std::to_string で文字列にしたものをつないで入れ、pub_ の矢印の publish で送り、RCLCPP_INFO で、publish と %s の書式に、data の c_str() を渡してログに出します。メンバ変数は、Publisher の SharedPtr の pub_、TimerBase の SharedPtr の timer_、0 で初期化した int の count_ です。

main 関数は、rclcpp::init に argc と argv を渡し、std::make_shared で Talker を作って rclcpp::spin に渡し、rclcpp::shutdown を呼んで、0 を返します。

原文の解説の要点です。骨組み、つまりノードを作る、spin、終わる、は Python と同じで、ここでは言語に固有の点を説明しています。

include と using。rclcpp/rclcpp.hpp が rclcpp の本体で、std_msgs/msg/string.hpp がメッセージの型のヘッダです。ファイルの名前は、メッセージの名前の String を、小文字とアンダースコアの形、つまりスネークケースにしたものです。using namespace std::chrono_literals は、1s や 100ms のような時間のリテラルを使えるようにします。

クラスの定義。初期化のリストで Node に名前を渡すのは、Python の super().__init__ に相当します。

create_publisher。型は山括弧のテンプレートの引数で、引数はトピックの名前と QoS です。数値の10 は、QoS の depth を簡単に指定したもので、Python と同じ意味です。戻り値は SharedPtr、つまり std::shared_ptr の別名なので、pub_ のメンバに入れ、送るときは pub_ の矢印で publish を呼びます。

create_wall_timer。wall は壁掛け時計の意味で、シミュレーションの時間ではなく、実際の時間で数えます。周期は std::chrono の型で渡します。コールバックには、ラムダ式を使っています。角括弧の this は、このオブジェクトをラムダの中で使えるように取り込む指定で、これが無いと on_timer を呼べません。同じことは std::bind でも書けますが、ラムダの方が読みやすいので、今回はこちらを使います。

on_timer。count_ の後ろに ++ を付けるのは、今の値を使ってから1増やす、後置のインクリメントです。std::to_string で、数値を文字列に変えます。RCLCPP_INFO は printf の形式で、%s に渡すのは std::string ではなく、c_str() で得る C の文字列です。std::string をそのまま渡すと、コンパイルは通っても、実行のときに文字化けや異常な終了になりえます。

メンバ変数。ローカル変数にすると、コンストラクタを抜けた時点で片付けられて、タイマーが止まります。create_publisher や create_wall_timer が返す SharedPtr は、持ち主の数を数えて、0 になったら自動で片付けるポインタです。rclcpp::Node の側は作ったものを持ち続けないので、メンバ変数に入れてノードを持ち主にしておかないと、持ち主が0 になって片付けられます。詳しくは、この節の末尾の補足にあります。

main。rclcpp::init は、Python の rclpy.init に相当する初期化で、ROS の引数もここで解釈されます。std::make_shared でノードを shared_ptr として作り、rclcpp::spin に渡します。spin は、Ctrl+C まで止まったまま戻りません。ノードは、spin を抜けるまで、shared_ptr によって生きています。rclcpp::shutdown で後片付けをします。Python の版のような try と except は要りません。Ctrl+C で spin が普通に戻るからです。

つまずきやすい点。count_ のようにメンバを初期化し忘れると、値が定まりません。private での宣言の順は、初期化の順と関係します。4-2節で CMakeLists.txt に足す ament_target_dependencies、つまり実行ファイルが使うパッケージを結び付ける行に、std_msgs を書き忘れると、include で失敗します。

観察のポイント。Python の版と同じ形の、publish と hello と番号の出力になること。ビルドに時間がかかるだけで、動きは同じです。

#### 1組目のサンプル、listener.cpp

listener.cpp は、listener.py と同じ仕様のノードです。コンストラクタで、ノードの名前を listener にし、create_subscription に、String 型を山括弧で付け、chatter、10、そしてラムダ式を渡して、sub_ に入れます。ラムダ式は、this を取り込み、String のメッセージへの const の参照を受け取り、RCLCPP_INFO で received と data の c_str() をログに出します。private には、Subscription の SharedPtr の sub_ があります。main は talker と同じ形です。

解説の要点です。create_subscription の引数の順は、トピックの名前、QoS、コールバックです。Python の版の、型、トピックの名前、コールバック、QoS とは、QoS とコールバックの順が逆なので、注意します。コールバックのラムダの引数は、メッセージへの const の参照で、コピーせずに、読み取りだけで受け取ります。this の取り込みは、get_logger() を呼ぶために必要です。

クラスに on_message のメソッドを作らない書き方もあります。短い処理なら、ラムダにその場で書くと、行き来が減って読みやすい。処理が増えたら、メソッドに分けて、ラムダからそのメソッドを呼びます。sub_ のメンバは、持っておかないと購読が終わってしまう点で、Publisher と同じです。

つまずきやすい点。コールバックの引数の型を、メッセージの型と食い違わせると、テンプレートのエラーがとても長く出ます。最初の error: の行を読むと、原因の型の不一致が書かれています。

観察のポイント。Python の talker と C++ の listener を組み合わせても、同じ表示になることです。

#### 2組目のサンプル、sine_pub.cpp

sine_pub.cpp は、sine_pub.py と同じ仕様です。include に cmath と std_msgs/msg/float64.hpp が加わります。コンストラクタで、ノードの名前を sine_pub にし、Float64 型、sine、10 の Publisher と、100ms ごとに on_timer を呼ぶタイマーを作ります。on_timer は、now().seconds() で今の時刻を const の double の t に入れ、Float64 のメッセージの data に、std::sin の、2.0 掛ける M_PI 掛ける freq_hz_ 掛ける t の値を入れて、publish します。ログは出しません。メンバ変数は、pub_、timer_、そして0.5 で初期化した double の freq_hz_ です。

解説の要点です。100ms は chrono_literals のリテラルで、Python の0.1秒に相当します。単位が型に含まれるので、秒とミリ秒の取り違えが起きにくい。now() は Node のメソッドで、ノードの時計の今の時刻を返し、seconds() で、秒の単位の double が直接得られます。Python の版のような、ナノ秒からの手での換算は要りません。M_PI は cmath から来る円周率の定数で、環境によっては定義されないこともありますが、Linux と gcc では普通は使えます。std::sin もラジアンを取ります。変えない値に const を付ける習慣にすると、意図しない書き換えをコンパイラが見つけてくれます。

つまずきやすい点。整数の割り算に注意します。1 を2 で割ると0 になります。周波数を0.5 ではなく、1 割る2 と書くと0 になり、波が消えます。

観察のポイント。Python の版と同じく約10 Hz で、値がマイナス1 から1 を約2秒の周期で往復することです。

#### 2組目のサンプル、sine_sub.cpp

sine_sub.cpp は、sine_sub.py と同じ仕様です。構造は C++ の版の listener と同じで、型が Float64、トピックが sine になっただけです。ラムダの中で、RCLCPP_INFO に、sine と %.3f の書式で、msg.data を渡します。

%.3f は printf の形式で、小数点以下3桁です。msg.data は double なので、%f の仲間がそのまま使えます。%s と違って、c_str() のような変換は要りません。つまずきやすい点は、整数用の %d に double を渡すと、コンパイラが警告を出すか、出力が不正な値になることです。書式の指定子と引数の型を合わせます。観察のポイントは、Python の sine のノードと C++ の sine のノードを混ぜても、値と周期が変わらないことです。

C++ の版の4つのファイルに共通する要点は、Node を継承したクラスのコンストラクタで通信の口を作り、shared_ptr のメンバに持ち、main で make_shared してから spin に渡す、という形です。Python の版とは、create で始まる関数の名前と引数、コールバックを渡すこと、spin の役割が同じです。言語の違いは、主に3つの点に出ます。型の明示、shared_ptr による持ち主の扱い、そして書式の指定です。

#### 補足: スマートポインタ、shared_ptr と、誰が持ち続けるか

C++ の版のコードには、SharedPtr、std::make_shared、矢印が何度も出てきます。これらは、スマートポインタという、C++ の標準の仕組みに関わっています。

まず、ポインタと後片付けの問題です。C++ では、オブジェクトを new で作ると、使い終わったときに、自分で delete して片付ける必要があります。片付け忘れるとメモリが漏れ、まだ誰かが使っているのに片付けると、その人が壊れたメモリを触って異常に終わります。いつ片付けてよいかを、人が正しく判断し続けるのは難しい。

std::shared_ptr の考え方は、こうです。shared_ptr は、オブジェクトを指すと同時に、今いくつの場所から持たれているか、つまり参照の数を数えるポインタです。コピーすると数が1増え、変数が消える、つまりスコープを抜けるか上書きされると、数が1減ります。数が0 になった瞬間に、自動でオブジェクトを片付けます。後片付けを、人の判断ではなく、持っている人がいるかどうかに任せる仕組みです。

原文は、書き方と意味の2列の表で、3行を説明しています。std::make_shared に山括弧で Talker を付けたものは、Talker を作り、それを指す shared_ptr を返します。new を自分で書きません。rclcpp::Publisher の SharedPtr は、rclcpp が用意した別名で、中身は、Publisher を指す std::shared_ptr です。pub_ の矢印の publish は、ポインタが指す先のオブジェクトのメソッドを呼ぶ書き方で、点ではなく矢印を使います。

同じ仲間に、持ち主が1人だけの std::unique_ptr と、数に数えられない、つまり持ち主にならない std::weak_ptr があります。この教材のサンプルで直接書くのは shared_ptr だけですが、weak_ptr は次の話に関わります。

このコードで、誰が何を持っているかは、3つの点に分けて説明されています。

1つ目。main で std::make_shared が作ったノードは、rclcpp::spin に渡され、spin が終わるまで持たれます。main を抜けるとノードが片付けられ、それと一緒にメンバ変数も片付けられます。

2つ目。create_publisher と create_wall_timer は、作った Publisher とタイマーを shared_ptr で返します。これを pub_ と timer_ に入れることで、ノード、つまり Talker が持ち主になります。

3つ目。rclcpp::Node の側は、作ったものを自分では持ち続けません。タイマーや Subscription は、executor が呼び出すために、コールバックグループに登録されますが、そこでは weak_ptr、つまり数に数えられない参照で覚えられるだけです。そのため、pub_ や timer_ に入れずに、ローカル変数で受けると、コンストラクタを抜けた時点で数が0 になり、タイマーは片付けられます。エラーは出ず、ただタイマーが一度も動きません。

Python との考え方の違いも、軽く書かれています。Python では、すべてのオブジェクトが、初めから参照の数を数えて自動で片付ける仕組みで管理されています。CPython の参照カウントです。つまり、Python の変数は、C++ でいえば、いつも shared_ptr のようなものです。そのうえで、rclpy の Node は、create_publisher や create_timer で作ったものを、ノード自身の内部のリストにも入れて、持ち続けます。そのため、Python の版で self.timer に代入しなかったとしても、タイマーは片付けられずに動き続けます。Python で self.pub に入れるのは、後で publish に使うため、そしてコードを読む人に、何を持つノードかを示すためで、生かしておくためではありません。

まとめると、Python では、ライブラリの Node が持っていてくれるのに対し、C++ では、持ち主を自分で決めて、コードに書く必要があります。rclcpp がこうなっているのは、ノードを部品として軽く保ち、要らなくなったものを確実に片付けられるようにするためです。持ち主を明示するのは手間ですが、このタイマーはこのノードが生きている間だけ動く、という寿命の関係が、メンバ変数の宣言を見ればはっきり分かる、という利点もあります。rclcpp::Node が作ったものを持たない理由と、rclpy の Node の内部のリストは、参考資料のノードのクラスの文書の2-4節と3-3節で、クラス図を使って詳しく説明しています。

### 4-2. CMakeLists.txt に登録する

learn_cpp の CMakeLists.txt に、実行ファイルごとの定義を足し、install(TARGETS ...) に名前を並べます。雛形の hello の定義は残します。

足す行は、4つの実行ファイルのそれぞれについて2行ずつです。1行目は add_executable で、実行ファイルの名前と、src の下のソースのファイルを書きます。2行目は ament_target_dependencies で、実行ファイルの名前と、rclcpp と std_msgs を書きます。そして最後に、install(TARGETS ...) で、hello、talker、listener、sine_pub、sine_sub の5つを並べ、DESTINATION に、lib と、プロジェクトの名前の変数を書きます。

説明は3つです。1つ目。1つの実行ファイルにつき、3種類の行を書きます。add_executable は、ソースから実行ファイルを作る指定。ament_target_dependencies は、その実行ファイルが使うパッケージ、ここでは rclcpp と std_msgs の、ヘッダとライブラリを結び付ける指定。install(TARGETS ...) は、ros2 run が探す場所へ置く指定です。ament_target_dependencies に書くパッケージは、雛形の find_package で探してあるものです。フェーズ2 で --dependencies rclcpp std_msgs を指定したので、すでに入っています。各行の詳しい意味は、Tips 集の2節、CMakeLists.txt の読み方にあります。2つ目。雛形にある、hello だけの install(TARGETS ...) の行は、この新しい install(TARGETS ...) に置き換えます。重ねて書きません。3つ目。ament_package() は、必ずファイルの最後に置きます。

### 4-3. ビルドして動かす

cd で ~/ros2_ws に移り、colcon build --symlink-install に --packages-select learn_cpp を付けてビルドし、source install/setup.bash を実行します。そして、T1 で ros2 run learn_cpp talker、T2 で ros2 run learn_cpp listener を実行します。

期待する結果は、こうです。ビルドの表示は、3-3節と同じ形で、learn_cpp の Finished の行と、1つのパッケージが終わったという Summary の行です。Python より時間がかかり、コンパイルの途中では、learn_cpp を処理中だという表示が出ることがあります。実行のときのログは、Python の版と同じ形式で、本文も同じ文言にしてあります。

ログの見た目だけでは、Python のノードか C++ のノードかは区別できません。これは、同じトピックの名前と型なら、言語を気にせずつながる、という6節の話の裏返しでもあります。2組目の sine_pub と sine_sub も、ros2 run learn_cpp sine_pub と ros2 run learn_cpp sine_sub で同じように動かすと、3-3節と同じ表示になります。

C++ のビルドは時間がかかります。エラーが出たら、最初の error: の行から読みます。後に続くエラーは、連鎖であることが多いからです。

## 5. 観察する

2つの言語のノードを動かした状態で、フェーズ1 のコマンドを使います。6つあります。ros2 node list。ros2 topic list -t。ros2 topic info /chatter に -v を付けたもの、これで Publisher と Subscriber の詳しい情報、QoS も出ます。ros2 topic echo /sine。配信の周期を測る ros2 topic hz /sine。そして、ノードとトピックのつながりを図で見る rqt_graph です。

期待する結果を、talker、listener、sine_pub、sine_sub の4つを動かしている場合で説明します。

ros2 node list は、ノードの名前をスラッシュ付きで、アルファベットの順に並べます。/listener、/sine_pub、/sine_sub、/talker の4つです。起動していないノードは出てきません。

ros2 topic list -t には、/chatter の String と /sine の Float64 のほかに、自分で作っていない /parameter_events と /rosout も出ます。どちらもノードが自動で作るトピックで、/rosout はログの集まる先です。/parameter_events はパラメータの変更の通知、/rosout はログの1行を運ぶ型です。

ros2 topic info /chatter -v では、型と、Publisher の数の1 が出て、その Publisher のノードの名前が talker であること、名前空間、型、端点の種類が PUBLISHER であること、そして QoS の設定が表示されます。QoS は、Reliability が RELIABLE、History と Depth が KEEP_LAST の10、Durability が VOLATILE です。続いて、Subscription の数の1 と、そのノードの名前の listener、端点の種類の SUBSCRIPTION が表示されます。KEEP_LAST の10 は、コードで渡した depth の値です。実際には、GID や型のハッシュなど、原文の抜粋より多くの行が出ます。

ros2 topic echo /sine は、メッセージを、ハイフン3つの行で区切って表示します。sine_sub のログと違って書式を指定していないので、桁の多い表示になります。

ros2 topic hz /sine は、平均の周期が10.000 で、最小と最大の間隔がどちらも0.100秒、という集計を、数秒ごとに出し直します。平均が10 の前後なら、仕様どおりです。

rqt_graph では、ノードが楕円、トピックが矢印か四角で描かれ、/talker から /chatter を通って /listener へ、/sine_pub から /sine を通って /sine_sub へ、という2本の流れが見えます。

## 6. 言語をまたいだ接続

トピックの名前と型が同じなら、言語に関係なくつながります。原文は、組み合わせ、T1、T2 の3列の表で、4つの組み合わせをすべて試すように書いています。

1つ目は Python から Python。T1 で learn_py の talker、T2 で learn_py の listener。

2つ目は Python から C++。T1 で learn_py の talker、T2 で learn_cpp の listener。

3つ目は C++ から Python。T1 で learn_cpp の talker、T2 で learn_py の listener。

4つ目は C++ から C++。T1 で learn_cpp の talker、T2 で learn_cpp の listener。

期待する結果は、4つの組み合わせのすべてで、3-3節と同じ表示になることです。T1 に publish と hello と番号、T2 に received と hello と番号です。組み合わせによって、ログの見た目が変わることはありません。どれか1つでも T2 に何も出ない場合は、その組み合わせで使っているパッケージのビルドと source を確かめます。

課題は4つです。

課題1 は、ros2 topic info /chatter -v で、Publisher と Subscriber のノードの名前、型、QoS を確かめ、言語が違っても、表示が同じ形式になることを確かめることです。

課題2 は、talker を2つ、別のターミナルで同時に起動するとどうなるかを観察することです。ros2 node list で、ノードの名前が重なっていることを示す警告が出ることを確かめます。起動した直後のログには出ないこともあります。

課題3 は、listener を起動してから、ros2 topic pub で、/chatter に、String 型で、data が from cli のメッセージを送り、コマンドラインから送ったものも listener が受け取ることを確かめることです。

課題4 は発展で、sine_pub の周波数の freq_hz を変えて、ros2 topic echo /sine の値の変わり方を見ることです。フェーズ3-3 でパラメータにする予習になります。

## 7. Python の版と C++ の版の違いのまとめ

talker を例に、3節と4節のコードを比べた表です。観点、Python、C++ の3列で、6行あります。

1行目、コードの行数。概要のコメントの行を除いて、Python は31行、C++ は39行です。C++ は、include と波括弧の分だけ少し長い。

2行目、Publisher の作り方。Python は、create_publisher に、型、トピックの名前、QoS を、普通の関数の引数として渡す。C++ は、型を山括弧のテンプレートの引数で渡し、戻り値は SharedPtr。

3行目、コールバックの渡し方。Python は、self.on_timer のように、メソッドを括弧を付けずにそのまま渡す。C++ は、this を取り込んだラムダ式で、this が無いとメンバ関数を呼べない。

4行目、購読のコールバックの引数の順。Python は、型、トピックの名前、コールバック、QoS。C++ は、トピックの名前、QoS、コールバックで、Python と順が逆。

5行目、直してから動きを確かめるまでの手数。Python は、--symlink-install なら保存するだけ。C++ は、保存した後に colcon build でコンパイルし直す必要がある。

6行目、エラーの出方。Python は、型の不一致があっても、実行するまで気づかないことがある。C++ は、テンプレートの型の不一致がコンパイルのときにエラーになるが、エラーの文は長くなりがち。

C++ の方が、書く量と手数は増えますが、コールバックのつなぎの間違い、例えば型の取り違えを、コンパイルのときに見つけられる点は利点です。Python は手数が少なく、繰り返しやすい分、実行してみるまで誤りに気づきにくい。この違いが Node クラスのどんな作りから来ているか、例えば、Python では作った Publisher などをノードが自分で持つが、C++ では呼び出した側が SharedPtr で持ち続ける必要がある、という点は、参考資料のノードのクラスの文書で、クラス図を使って説明しています。

## 8. つまずきやすい点

原文では、症状と、確かめることの2列の表で、11行あります。

1行目。ros2 run で、実行ファイルが見つからない、と言われる場合。setup.py の entry_points か、CMakeLists.txt の install(TARGETS ...) を足したか。ビルドし直した後に source したか。C++ なら、add_executable の1つ目の名前を、ament_target_dependencies と install(TARGETS ...) の行まで、そろって間違えていないか。綴りがそろっていれば、エラーにならずに、間違えた名前の実行ファイルができます。登録された名前は、ros2 pkg executables learn_cpp で確かめます。

2行目。C++ のビルドで、ament_target_dependencies の1つ目の引数は正しいターゲットの名前でなければならない、というエラーが出る場合。add_executable の1つ目の名前と、すぐ後の ament_target_dependencies の1つ目の名前が同じか。CMake は名前の正しさを判断できず、ファイルの中で同じ名前がそろっているかだけを見ます。

3行目。C++ のビルドで、install(TARGETS ...) に書いたターゲットが存在しない、というエラーが出る場合。install(TARGETS ...) に並べた名前が、add_executable の名前と同じか。

4行目。C++ のビルドで、ソースのファイルが見つからない、というエラーが出る場合。add_executable の2つ目、つまり src の talker.cpp などのパスとファイルの名前が、実際のファイルと合っているか。

5行目。C++ で、名前を直してビルドし直したのに、ros2 run で前の名前の実行ファイルも動く場合。colcon は、前のビルドで install に入れた実行ファイルを消さないので、古い名前の実行ファイルが残っています。ros2 pkg executables learn_cpp で、同じノードの名前が2つ並んでいないかを見ます。古い方を確実に消すには、ros2_ws で rm -rf を使って build と install の learn_cpp のフォルダを消してから、ビルドし直します。

6行目。C++ で、std_msgs の string.hpp が見つからない、という致命的なエラーが出る場合。find_package の std_msgs と、ament_target_dependencies があるか。雛形で --dependencies を指定しなかった場合は、手で足します。

7行目。Python の package.xml に test_depend しか無い場合。ros2 pkg create で --dependencies を指定し忘れています。3-2節のとおり、rclpy と std_msgs の depend の行を手で足します。無くてもこの環境では動きますが、依存の宣言として必要です。

8行目。listener に何も出ない場合。トピックの名前の chatter と、型の綴り。ros2 topic list -t で確かめます。

9行目。起動してすぐ終わる場合。spin を呼んでいるか。

10行目。Ctrl+C で Python が例外を出す場合。try と finally、それに rclpy.try_shutdown の書き方を確かめます。

11行目。ros2 topic hz が10 から大きく違う場合。WSL の負荷が高い可能性があります。ほかのプロセスを止めて、測り直します。

## 9. 次へ

フェーズ3-2a で、Twist で turtlesim を動かします。続くフェーズ3-2b では、QoS の相性を体験します。これは、フェーズ3-2a とは独立したテーマです。

## 10. 公式ドキュメントと参考資料

確認の状況が書かれています。2026年9月20日の時点で、下の資料は企画の文書に載せた URL で、今回は確かめ直していません。docs.ros.org は、ボット対策で本文の取得が拒否されます。

公式の資料は、ROS 2 Jazzy の4つです。クライアントライブラリの初心者向けのチュートリアルの目次で、Publisher と Subscriber のチュートリアルはここからたどります。rclpy の API と、その Node のページ。rclcpp の C++ の API。そして、std_msgs などのメッセージの定義がある、GitHub の ros2/common_interfaces です。

日本語の資料として、Qiita の、Publisher と Subscriber の通信の実習の記事が1本挙げられています。記事は個人による非公式の解説で、版によって違う場合があり、公式のドキュメントと食い違う場合は公式を優先する、とあります。

原文の最後には、出典の注記があります。各サンプルの API の使い方は、公式のチュートリアルを参考にしました。ROS 2 のドキュメントは CC BY 4.0 です。ノードの名前、仕様、コード、文章は独自に書いたもので、一語ずつの転載ではありません。

以上で、フェーズ3-1 の手順書の話を終わります。

## 出典について

この原稿は、SanghunIm1991 さんの [ros2MinimalPhysicalAi の「フェーズ3-1 手順書: Publisher / Subscriber（トピック）をPython・C++で書く」](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/docs/phase3_1_pubsub.md)を、聞くために要約・意訳したものです。図の [phase3_1_topics.svg](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/docs/img/phase3_1_topics.svg) と [phase3_1_spin.svg](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/docs/img/phase3_1_spin.svg) は、言葉で説明しました。元にしたのは、[2026年10月15日の版](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/fe96bffa42d20ef559b3d6995e44b90379b249f5/docs/phase3_1_pubsub.md)です。原文の文章と図と同じく、[クリエイティブ・コモンズ 表示 4.0 国際ライセンス](https://creativecommons.org/licenses/by/4.0/deed.ja)で提供します。

原稿の中に原文の表記のまま書いたコマンドと、コードの関数やクラスの名前は、原文では [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0) の対象です。ライセンスの全文は、原文のリポジトリの [LICENSE-APACHE-2.0](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/LICENSE-APACHE-2.0) にあります。サンプルコードは写さず、役割と要の行を言葉で説明しました。

原文では、API の使い方を [ROS 2 Documentation](https://docs.ros.org/en/jazzy/)（Open Robotics、[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)）の公式チュートリアルを参考にしたとしています。表示の例は、各ツールの表示を言葉で説明したものです。
