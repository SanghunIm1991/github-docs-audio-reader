<!--
聞くための原稿（読み上げでは読まれない記録）
原文: SanghunIm1991/ros2MinimalPhysicalAi の main ブランチの docs/interlude_micro_ros.md（図は docs/img/interlude_micro_ros_overview.svg）
原文のコミット: e21773ba3dfe6808e69fde552d6a3304f3b2c958（2026-10-17）
作成: 2026-10-23、Claude Code が手作業で作成（原稿化スキルはまだない）
原文のライセンス: 文章と図は CC BY 4.0、コードとコマンドは Apache-2.0（それぞれ LICENSE の2と1）。原文の冒頭と末尾に、説明と表は micro-ROS の公式サイトの文書（CC BY-ND 4.0）と各リポジトリの説明から、事実を独自にまとめ直したもので、公式サイトの文書は改変を認めないライセンスのため、文章もコードも転載・翻訳せずリンクに留めた、5節のコードは rclc（Apache License 2.0）の関数を使って独自に書いた骨組みで、公式の例の写しではない、とある。この原稿は、原文を聞くために要約・意訳したもの（改変あり）
方針: 英語の略語や製品名、関数・設定・道具の名前、短いコマンドは原文の表記のまま書く。5節の骨組みのコード（C）は写さずに、ブロックの構成と要の行を言葉で説明し、各行の意味は原文の「読むときの要点」に任せた（要の行は、要点に出てこない行だけにした）。図と表（層の比較、通信路、開発の道具、rclc と rclpy の対応、メモリの枠の設定、つまずきやすい点）は言葉で説明する。文字数の上限は設けない
省いたもの: URL、型の定義へのリンク、gcc の点検のコマンドの細かいオプション（言語の規格と警告の指定だけ言葉で残した）、10節の各リンクのアドレス
-->

# 間章: micro-ROS でマイコンを ROS2 につなぐ（聞くための原稿）

これは、ros2MinimalPhysicalAi という教材の、入門の読み物の間章の話です。フェーズ5-4 までを読み終えた人向けの、任意の章です。ここまでの教材では、ノードはすべて PC の上で動き、車両も Gazebo の中のものでした。実際のロボットでは、モーターを回す、センサの値を読む、といった体に近い仕事を、小さなマイコン、つまりマイクロコントローラが受け持つことが多いです。マイコンには、PC のような OS も、何ギガバイトものメモリもありません。それでも、マイコンの上のプログラムを、PC のノードと同じようにトピックでやり取りできる ROS2 のノードにできれば、ros2 topic echo でセンサの値を見たり、PC のノードから指令を送ったりする、これまでと同じ作り方がそのまま使えます。それを実現するのが micro-ROS です。この章では、特定のマイコンに限らず、micro-ROS の仕組みと、プログラムの書き方、開発の道具の選び方、小さなマイコンで気をつけることを、読み物として見ていきます。

想定する環境は、ありません。この章では、コマンドを実行せず、パッケージも導入しません。micro-ROS を実際に使うときは、ROS2 Jazzy の入った PC と、micro-ROS に対応したマイコンのボードが要ります。3節と4節で扱います。前提はフェーズ5-4 ですが、内容としては、トピック、QoS、タイマー、実行器、つまり executor の考え方、つまりフェーズ3-1、3-2b、フェーズ4 までが分かれば読めます。フェーズ6 と7 の本文は、この章に依存しません。所要時間の目安は0.5 から1コマです。言語は C で、5節の骨組みのコードを読みます。書いて動かす実習はありません。

この章の位置づけの囲みです。実習の無い読み物で、マイコンの種類を限定しません。説明は、micro-ROS の公式サイトの文書と、各リポジトリの説明から、要点を自分の言葉でまとめ直したものです。公式サイトの文書は、改変を認めないライセンス、つまり CC BY-ND 4.0 なので、文章もコードも転載・翻訳せず、リンクだけにしています。5節のコードは、公式の例を写したものではなく、rclc、ライセンスは Apache License 2.0 の関数を使って、独自に書いた骨組みです。

確かめた範囲の囲みもあります。この章には、実行する手順と、期待する結果はありません。5節のコードは、作るときに、ros2 の rclc の jazzy のブランチのヘッダーと、ROS2 Jazzy のヘッダーを使って、コンパイラの gcc で、C99 の規格と警告を全部出す指定で、文法だけの点検を、警告なしで通しました。実行もリンクもしていません。マイコンへの書き込みと、エージェントにつないで動かすことは、作るときにはしていません。対応するボード、道具、枝、つまりブランチの名前は、作った時点、2026年10月16日の各リポジトリの説明で確かめたもので、今後変わることがあります。

この原稿では、コードを書き写さず、表と図とあわせて、言葉で説明します。

## 0. この章で得てほしいこと

5つあります。

1つ目。普通の ROS2 をマイコンでそのまま動かせない理由と、micro-ROS が、クライアントとエージェントに分けることで、それをどう解決しているかを説明できる。

2つ目。micro-ROS の層、つまり自分のプログラム、rclc と rcl、rmw_microxrcedds、Micro XRCE-DDS のクライアントと、PC の側のエージェントの役目を説明できる。

3つ目。開発の道具、つまり micro_ros_setup、micro_ros_platformio、micro_ros_arduino、ESP-IDF や Zephyr の部品の違いと、使うボードに合わせた選び方を説明できる。

4つ目。rclc で書いたノードの骨組み、つまり準備、ノード、パブリッシャーとサブスクリプションとタイマー、実行器、回す、の流れを読み、rclpy のノードとの対応を説明できる。

5つ目。小さなマイコンで気をつけること、つまり静的なメモリの枠、メッセージの大きさ、QoS、エージェントとのつながりの確認を説明できる。

完了の条件です。5節の骨組みのコードの各行が、rclpy のどの書き方に当たるかを説明でき、6節の表の項目を見て、自分の使いたいマイコンとメッセージで、どこに気をつければよいかを挙げられることです。

## 1. マイコンで普通の ROS2 が動かない理由

PC の上の ROS2 のノードは、通信の土台に DDS、つまり Data Distribution Service を使っています。フェーズ0 の2節で見た、ROS2 の下の層の通信の仕組みです。DDS は、ネットワークの中の相手を自動で探し、QoS に合わせて届け方を変える、高機能な仕組みです。その分、プログラムもメモリも大きく、ふつうは、Linux のような OS の上で、何十から何百メガバイトのメモリを使って動かす前提になっています。

一方、ロボットで使われるマイコンのメモリは、RAM が数十から数百キロバイト、プログラムを置くフラッシュメモリが数百キロバイトから数メガバイトといった大きさで、PC より何桁も小さいです。OS も、小さなリアルタイム OS、つまり RTOS で、たとえば FreeRTOS、Zephyr、NuttX か、OS なしです。OS なしとは、Arduino のように、setup と loop の2つの関数だけで動かす形で、ベアメタルとも呼びます。DDS をそのまま載せる余裕はありません。

micro-ROS は、この問題を、通信の仕事を2つに分けて解きます。

マイコンの側には、DDS-XRCE、つまり DDS for eXtremely Resource Constrained Environments、資源のとても限られた機器のための DDS の規格の、クライアントだけを置きます。クライアントは、相手を探したり、たくさんの相手と直接やり取りしたりせず、決まった1つの相手と、シリアル、つまり USB や UART、または UDP などの通信路で、小さなメッセージを送り合うだけにします。

PC の側には、エージェント、つまり micro-ROS エージェントを動かします。エージェントは、つながってきたクライアントの代わりに DDS に参加し、クライアントのノード、パブリッシャー、サブスクリプションを、DDS の中に作ります。

PC の ROS2 のノードから見ると、エージェントが作ったものは、普通の ROS2 のノードやトピックと区別がつきません。そのため、ros2 node list や ros2 topic echo などの道具も、そのまま使えます。

micro-ROS が主な対象にしているのは、RAM が数十キロバイト以上ある、32ビットの中くらいのマイコンです。RAM の少ない8ビットのマイコンは、この対象から外れます。たとえば、Arduino UNO R3、チップは ATmega328P で RAM が2キロバイトのものは、作った時点の対応ボードの一覧にありません。そうしたマイコンを ROS2 とつなぐには、マイコンはシリアルで文字や数を送受信するだけにして、PC の側に、シリアルとトピックを中継するノードを自分で書く、という形がよく使われます。この章では扱いません。

## 2. 全体像

ここに図が1枚あります。左に、灰色の破線の縦長の枠があり、見出しは、マイコン、RTOS か、OS なし、です。右下に、同じく灰色の破線の横長の枠があり、見出しは、PC、Linux など、です。

マイコンの枠の中には、4つの箱が、上から下へ縦に並びます。1つ目は薄いオレンジ色の箱で、自分のプログラム、センサを読む、指令を受ける。2つ目からは薄い青の箱で、2つ目は rclc プラス rcl、ノード、トピック、実行器。3つ目は rmw_microxrcedds、静的なメモリの枠で動かす。4つ目は Micro XRCE-DDS、クライアント、と書いてあります。上下に隣り合う箱の間は、両向きの矢印でつながっています。

PC の枠の中には、2つの箱が横に並びます。左は薄いオレンジ色の箱で、micro-ROS エージェント、代わりに DDS に参加する。右は薄い灰色の箱で、ROS2 のノード、ros2 topic などの道具、と書いてあります。

マイコンの枠のいちばん下の、Micro XRCE-DDS のクライアントの箱から、右へ、PC の枠のエージェントの箱まで、両向きの矢印が伸びています。ラベルは、XRCE-DDS、シリアル、UDP など、です。エージェントの箱と、右の ROS2 のノードの箱の間も、両向きの矢印でつながり、ラベルは2行で、上が DDS、下が普通の ROS2 です。

まとめると、自分のプログラムは、マイコンの中の層を下りてクライアントに届き、クライアントは通信路でエージェントとやり取りし、エージェントが普通の ROS2 の通信で、PC のノードや道具とつながる、という流れです。

マイコンの中は、PC の ROS2 と同じ層の分け方になっています。フェーズ0 の2節の、rclpy や rclcpp から、rcl、rmw、DDS と積み重なる形です。違うのは、各層の中身です。

表は3列で、5行あります。列は、層、PC の ROS2、micro-ROS のマイコンです。

1行目は、クライアントライブラリ、つまりノードを書くための API です。PC では、Python の rclpy と、C++ の rclcpp です。micro-ROS では、C の rclc で、ROS2 の共通の土台の rcl に、よく使う手順をまとめた関数と、マイコン向けの実行器を足したものです。

2行目は、共通の土台です。PC は rcl で、micro-ROS も rcl、つまり PC と同じものです。

3行目は、ミドルウェアとのつなぎ、つまり rmw です。PC では rmw_fastrtps_cpp などです。micro-ROS では rmw_microxrcedds で、使うメモリを、起動の前に決めた大きさの枠、つまり静的なメモリの中に収めます。

4行目は、通信です。PC では DDS で、たとえば Fast DDS です。micro-ROS では、Micro XRCE-DDS のクライアントで、C99 のライブラリです。相手はエージェントだけです。

5行目は、OS です。PC では Linux、Windows、macOS です。micro-ROS では、FreeRTOS、Zephyr、NuttX などの RTOS か、OS なし、たとえば Arduino です。

rcl が PC と同じものなので、ノード、トピック、サービス、パラメータ、タイマーといった考え方も、PC の ROS2 と同じです。公式の説明によると、rclc と rcl は、初期化が済んだ後は、動的なメモリの確保をせずに使えるように作られています。動的なメモリの確保とは、malloc のような、実行中にメモリを借りる操作のことです。マイコンでは、実行中にメモリが足りなくなったり、細切れになったりするのを避けるため、これが大事になります。

## 3. エージェントとつながり方

### 3-1. 通信路

クライアントとエージェントの間の通信路、つまりトランスポートは、作った時点の説明では、4つが用意されています。

表は2列で、4行あります。列は、通信路と、よく使う場面です。

1つ目は、シリアル、つまり USB のシリアルや UART です。ボードを USB で PC につなぐ場面で、いちばん手軽です。

2つ目は、UDP で、Wi-Fi や有線の Ethernet を使います。Wi-Fi や Ethernet の付いたボード、たとえば ESP32 を、無線や有線のネットワークでつなぐ場面です。

3つ目は、TCP で、UDP の代わりに TCP を使います。

4つ目は、自作、つまりカスタムです。ボードに独自の通信の方法がある場合に、送る、受け取る、などの関数を自分で書いて足します。

マイコンの側は、プログラムを書き込む前に、どの通信路を使い、エージェントがどこにいるかを決めておきます。シリアルなら機器、UDP なら PC の IP アドレスとポートです。

### 3-2. エージェントを動かす

エージェントは、PC の側で動かす ROS2 のノードの一種で、パッケージの名前は micro_ros_agent です。作った時点の ROS2 Jazzy の apt には、このパッケージはありませんでした。apt-cache policy で確かめた、とあります。そのため、次のどちらかで用意します。

1つ目は、ソースからビルドする方法です。micro-ROS のビルドの道具、micro_ros_setup、これは4節で扱いますが、これを自分のワークスペースに置いてビルドし、その中のスクリプト、つまり create_agent_ws.sh と build_agent.sh で、エージェントのパッケージを取ってきてビルドします。

2つ目は、Docker のイメージを使う方法です。公式のイメージ microros の micro-ros-agent に、ROS2 の版の名前、たとえば jazzy のタグが用意されています。

起動するときは、通信路と、その設定を引数で渡します。シリアルなら、ros2 run micro_ros_agent micro_ros_agent に、serial と、--dev で機器のパスを渡す形です。UDP なら、ros2 run micro_ros_agent micro_ros_agent に、udp4 と、--port でポートの番号を渡す形です。この章では実行しません。

エージェントとマイコンがつながると、PC の側では、マイコンのノードとトピックが、普通の ROS2 のものと同じように見えます。5節の骨組みなら、ros2 node list に /mcu_node が、ros2 topic list に /mcu_counter と /mcu_command が並び、ros2 topic echo の /mcu_counter で、マイコンが送る数を読めるはずです。

### 3-3. WSL2 で使う場合の注意

この教材の環境、つまり WSL2 で、USB でつないだボードを使う場合は、もう1つ準備が要ります。WSL2 の Linux からは、PC の USB の機器がそのままでは見えないので、Windows の側に usbipd-win を導入し、USB の機器を WSL に渡す必要があります。

渡す前に、一度だけ、管理者の権限で、機器を共有の対象にします。usbipd bind です。この設定は、再起動しても残ります。そして、使うたびに、usbipd attach に --wsl を付けて渡します。再起動や、ケーブルの抜き差しの後は、渡し直します。

usbipd-win は、Windows に常駐のサービスと、ローカルのネットワークからの接続、つまり TCP の3240番を許すファイアウォールの規則を加えます。導入する前に、使う PC の方針と照らして、入れてよいかを判断します。使い終わったら機器を外し、つまり usbipd detach、共有が要らなくなったら、共有の対象からも外す、つまり usbipd unbind のがよい、とあります。また、Linux でシリアルの機器を読み書きするには、ふつう、ユーザーが dialout のグループに入っている必要があります。

UDP で、Wi-Fi のボードを使う場合は、ボードが PC のエージェントに届く必要があります。WSL2 の既定のネットワークの形では、WSL の中のプログラムは、Windows とは別のアドレスを持つので、ボードから届くようにするには、ネットワークの設定を考える必要があります。この章では扱いません。

## 4. 開発の道具とボード

### 4-1. 道具の種類

micro-ROS を使うマイコンのプログラムは、マイコン向けに組み立て直した、つまりクロスコンパイルした micro-ROS のライブラリと一緒にビルドして、ボードに書き込みます。そのための道具が、いくつか用意されています。使うボードと、そのボードで普段使っている開発環境に合わせて選びます。

表は3列で、4行あります。列は、道具、向いている場面、作った時点に確かめたこと、です。

1つ目は、micro_ros_setup です。RTOS、つまり FreeRTOS、Zephyr、NuttX で、ボードに合わせた一式を作る場面に向きます。ROS2 のパッケージなので、ros2 run で使います。確かめたことは、jazzy の枝があること、手順は、作る、つまり create、設定する、configure、ビルドする、build、書き込む、flash の4段階であること、エージェントのビルドにも使うことです。

2つ目は、micro_ros_platformio です。PlatformIO、つまり VS Code などで使うマイコンの開発環境で、Arduino の形のプログラムを書く場面に向きます。確かめたことは、platformio.ini の board_microros_distro で jazzy を選べること、通信路は board_microros_transport で選び、既定は serial であることです。

3つ目は、micro_ros_arduino です。Arduino IDE で書く場面に向きます。確かめたことは、対応するボードごとに、組み立て済みのライブラリが配られていること、jazzy の枝があることです。

4つ目は、ESP-IDF の部品と Zephyr の部品です。ESP32 の公式の開発環境の ESP-IDF や、Zephyr で作るプロジェクトに組み込む場面に向きます。確かめたことは、どちらも jazzy の枝があることです。

どの道具でも、プログラムの書き方、つまり5節の rclc は同じです。違うのは、ビルドの仕方、通信路の設定の仕方、メモリの枠の設定、つまり6-1節の置き場所です。

micro-ROS の公式サイトのチュートリアルの多くは、作った時点では、ROS2 Humble の時代に書かれたもので、ページに Written for Humble の印があります。Jazzy で使うときは、各リポジトリの jazzy の枝の説明を合わせて読むのがよい、とあります。5節の rclc_timer_init_default2 のように、関数が替わっていることもあります。

### 4-2. ボードの選び方

対応するボードは、道具ごとに一覧があります。作った時点の micro_ros_platformio の一覧では、Teensy 4.x、ESP32、Raspberry Pi Pico、Arduino Nano RP2040 Connect、Arduino Portenta H7、Arduino Due、Arduino Zero などです。micro_ros_arduino の一覧には、コミュニティによる対応として、Arduino UNO R4 もあります。一覧は更新されるので、使う前に、その道具のリポジトリの説明で確かめます。

ボードを選ぶときは、3つの点を見ます。

1つ目はメモリです。RAM が数十キロバイト以上あるかを見ます。少ないボードは、一覧で、メモリを節約する設定、たとえば colcon_lowmem.meta や colcon_verylowmem.meta が指定されています。6-1節で扱います。

2つ目は通信路です。USB のシリアルだけでよいか、Wi-Fi や Ethernet が要るかを見ます。

3つ目は開発環境です。普段使っている、または学びたい開発環境、たとえば Arduino、PlatformIO、ESP-IDF、Zephyr の道具があるかを見ます。

## 5. プログラムの書き方、rclc

### 5-1. 流れ

rclc で書くノードは、次の順に部品を作り、最後に実行器を回し続けます。5つの段階です。

1つ目は準備で、rclc_support_init です。通信の準備をして、エージェントにつなぎます。

2つ目はノードで、rclc_node_init_default です。ノードを作ります。

3つ目は、パブリッシャー、サブスクリプション、タイマーで、rclc_publisher_init_default などです。送る、受け取る、決まった周期で呼ぶ部品を作ります。

4つ目は実行器で、rclc_executor_init と、rclc_executor_add で始まる関数です。コールバックを呼ぶ係を作り、どの部品のコールバックを呼ぶかを登録します。

5つ目は回すことで、rclc_executor_spin_some を繰り返します。届いたメッセージや、時間になったタイマーのコールバックを呼びます。

rclpy のノード、つまりフェーズ3-1 と比べると、次のように対応します。

表は3列で、7行あります。列は、C の rclc、Python の rclpy、違い、です。

1行目。rclc_support_init は、rclpy.init に当たります。micro-ROS では、ここでエージェントにつなぐので、エージェントが動いていないと失敗します。

2行目。rclc_node_init_default は、Node に名前を渡すことに当たります。ノードは、クラスでなく、構造体の変数として作ります。

3行目。rclc_publisher_init_default と rclc_publisher_init_best_effort は、create_publisher に当たります。QoS は、関数の名前で選びます。default は reliable、best_effort は best_effort です。細かく決めるときは、rclc_publisher_init に QoS の構造体を渡します。

4行目。rclc_subscription_init_default は、create_subscription に当たります。コールバックは、ここではなく、実行器に登録するときに渡します。

5行目。rclc_timer_init_default2 は、create_timer に当たります。周期はナノ秒で渡し、RCL_MS_TO_NS に1000 を渡したものが1秒です。最後の引数は、すぐに動かし始めるかどうかです。

6行目。rclc_executor_init、rclc_executor_add_timer、rclc_executor_add_subscription は、rclpy では、rclpy.spin が自動でしてくれる部分です。実行器に登録する部品の数、つまりハンドルの数を、先に決めて渡します。

7行目。rclc_executor_spin_some を繰り返すことは、rclpy.spin にノードを渡すことに当たります。自分のループの中で、少しずつ回すので、間に、自分の処理、たとえばセンサを読む処理を挟めます。

### 5-2. 骨組みのコード

1秒ごとに数を1つずつ増やしてトピック mcu_counter に送り、トピック mcu_command で受け取った数を覚えておくノードの骨組みです。メッセージの型は、どちらも std_msgs の msg の Int32 を使います。

ファイルは、ありません。読むための例です。実際に使うときは、使う道具の決まった場所に書きます。たとえば micro_ros_platformio なら、PlatformIO のプロジェクトの src の main.cpp に、5-3節の Arduino の形に直して書きます。

コードは60行ほどの C で、先頭に、1秒ごとに数を送り、受け取った指令の数を覚えておく骨組みだ、という1行のコメントがあり、ブロックは5つです。

1つ目は include で、stdbool.h と、rcl の rcl.h、rclc の rclc.h と executor.h、std_msgs の msg の int32.h を読み込みます。

2つ目は、関数の外に static で置く変数で、パブリッシャーの publisher、サブスクリプションの subscription、送るメッセージの send_msg、受け取るメッセージの recv_msg、そして受け取った指令の数を覚える last_command を、0 で用意します。

3つ目は、タイマーのコールバックの timer_callback です。4つ目は、購読のコールバックの subscription_callback です。5つ目は main で、部品を順に作り、実行器を回し続けます。

要の行は3か所です。1つ目は、timer_callback の中で、send_msg の data を1増やし、rcl_publish で publisher から送る行です。2つ目は、subscription_callback の中で、届いたメッセージの data を last_command に書き込む行です。3つ目は、main の最後で、send_msg の data を0 にしてから、終わらない while のループの中で、rclc_executor_spin_some を、待つ時間の上限を100ミリ秒にして呼び続ける行です。

読むときの要点は、6つあります。

1つ目。部品は、関数の外の変数、つまり static か、main の中の変数として、先に用意しておきます。rclpy のように、実行中に部品を次々と作るのではなく、起動するときに必要な数だけ作ります。コールバックから使う部品、つまり publisher と送るメッセージは、関数の外に置いています。

2つ目は、型の情報です。ROSIDL_GET_MSG_TYPE_SUPPORT に、std_msgs、msg、Int32 を渡す書き方です。C には、Python のように型そのものを引数に渡す書き方が無いので、この決まった書き方で、型を表す情報を渡します。メッセージの型は、std_msgs、msg、Int32 を、それぞれ2つの下線でつないだ名前の構造体になります。

3つ目は QoS です。送る側を best_effort、受け取る側を reliable、つまり default にしています。センサの値のように、たくさん送って1つ欠けても困らないものは best_effort にすると、届いたかの確認、つまり6-3節を待たずに済みます。PC の側で受け取る自作のノードの QoS との相性は、フェーズ3-2b、QoS の相性と同じ規則で決まります。送る側が best_effort なら、受け取る側も best_effort にします。ros2 topic echo は、QoS を指定しなければ、送る側の QoS を調べて合わせて購読します。送る側に reliable でないものがあれば best_effort にするので、そのまま読めます。

4つ目は、実行器のハンドルの数です。rclc_executor_init の3つ目の引数の2 で、登録する部品の数、ここではタイマーと購読の2つです。足りないと、登録が失敗します。

5つ目は、受け取ったメッセージの置き場所、つまり recv_msg です。サブスクリプションを実行器に登録するときに、受け取ったメッセージを書き込む変数を渡します。ON_NEW_DATA は、新しいメッセージが届いたときだけコールバックを呼ぶ、という指定です。

6つ目は、失敗の確かめ方です。この骨組みでは、短くするため、最初の rclc_support_init だけで戻り値を確かめていて、エージェントとつながらないと、ここで失敗します。実際には、すべての関数の戻り値が RCL_RET_OK かを確かめ、失敗したら、LED を点滅させて止まる、などの処理をします。公式の例では、確かめる処理をマクロにまとめて書いています。

Jazzy の rclc では、タイマーを作る関数が rclc_timer_init_default2 に替わり、自動で動かし始めるかの引数、つまり最後の true が増えました。Humble の時代の例に出てくる rclc_timer_init_default は、非推奨になっていて、使うと警告が出ます。作るときに、jazzy の枝のヘッダーで確かめた、とあります。

### 5-3. Arduino の形で書く場合

micro_ros_platformio や micro_ros_arduino で、Arduino の形、つまり setup と loop の形で書く場合は、5-2節の main を2つに分けます。

setup の最初で、通信路を決める関数を呼びます。シリアルなら、Serial.begin に115200 を渡した後に、set_microros_serial_transports に Serial を渡して呼びます。これは micro_ros_platformio の場合です。Wi-Fi なら、ネットワークの名前、パスワード、エージェントの IP アドレスとポートを渡す関数を使います。続けて、5-2節の rclc_support_init から、実行器への登録までを書きます。

loop では、rclc_executor_spin_some を呼びます。loop は何度も呼ばれるので、5-2節の while のループは書きません。

Wi-Fi のパスワードのような値を、プログラムに直接書いた場合は、そのファイルを公開のリポジトリに入れないように気をつけます。

## 6. 小さなマイコンで気をつけること

### 6-1. 静的なメモリの枠

rmw_microxrcedds は、ノード、パブリッシャー、サブスクリプションなどを、種類ごとに、ビルドのときに決めた数の枠、つまりメモリのプールの中に作ります。枠の数を超えて作ろうとすると、作る関数が失敗します。枠の数は、ビルドの設定のファイル、たとえば colcon.meta で決めます。道具によって置き場所が違います。

表は2列で、5行あります。列は、設定と、決めることです。

1行目。RMW_UXRCE_MAX_NODES は、ノードの数の上限です。

2行目。RMW_UXRCE_MAX_PUBLISHERS と RMW_UXRCE_MAX_SUBSCRIPTIONS は、パブリッシャーとサブスクリプションの数の上限です。

3行目。RMW_UXRCE_MAX_SERVICES と RMW_UXRCE_MAX_CLIENTS は、サービスの提供側と、呼ぶ側の数の上限です。

4行目。RMW_UXRCE_MAX_HISTORY は、受け取ったメッセージを、読むまで溜めておく数です。

5行目。RMW_UXRCE_STREAM_HISTORY は、届いたかを確かめる通信、つまり6-3節の reliable で使う枠の数で、1つの枠は MTU の大きさの区切りです。送り直しと、分けて送る大きなメッセージ、つまり6-2節に使います。

枠を増やすとメモリを多く使うので、メモリの少ないボードでは、使う数に合わせて小さくします。4-2節の一覧の colcon_lowmem.meta と colcon_verylowmem.meta は、枠を小さくした設定のファイルです。

### 6-2. メッセージの大きさとメモリ

1回に送れるメッセージの大きさには、限りがあります。基準は、通信路ごとの1回の送信の大きさ、つまり MTU で、UCLIENT_SERIAL_TRANSPORT_MTU などの設定で決まります。公式の説明によると、best_effort では、MTU から12バイトを引いた大きさまでになります。reliable では、メッセージを分けて送れるので、MTU と、6-1節の RMW_UXRCE_STREAM_HISTORY から決まる、より大きな値までになります。どちらにしても、画像のような大きなメッセージは、マイコンでは扱いにくいです。

文字列、つまり string や、長さの決まっていない配列、たとえば int32 の配列を含むメッセージは、受け取る側で、中身を書き込むメモリを、あらかじめ用意しておく必要があります。Python や C++ のように、届いた長さに合わせて自動でメモリが確保されるわけではありません。用意の仕方は、手で確保する方法と、補助のパッケージ micro_ros_utilities を使う方法が、公式の文書で説明されています。この章の骨組みのように、数だけの型、たとえば std_msgs の Int32 を使えば、この手間は要りません。

### 6-3. QoS

reliable で送ると、メッセージごとに、届いたかの確認を待つので、通信が遅い、または不安定なときは、rcl_publish や、実行器を回す関数が、その分だけ待つことがあります。best_effort は、確認を待たないので速く、メモリも少なく済みますが、通信の誤りで欠けることがあります。周期的に送るセンサの値は best_effort、取りこぼすと困る指令は reliable、のように使い分けます。

### 6-4. エージェントとのつながりと時刻

2つあります。

1つ目は、つながりの確認です。rmw_uros_ping_agent に、待つ時間と、試す回数を渡すと、エージェントが応答するかを確かめられます。初期化の前でも使えるので、起動したら、エージェントが見つかるまで待ってから rclc_support_init を呼ぶ、という書き方ができます。エージェントを止めたり、ケーブルが抜けたりすると、マイコンの側の部品は使えなくなるので、途切れたら部品を作り直す、という処理も、必要に応じて書きます。

2つ目は、時刻の合わせ方です。マイコンには、正しい時刻を知る仕組みが無いことが多いです。rmw_uros_sync_session で、エージェントの PC の時刻に合わせられます。ネットワークの遅れも考えに入れて合わせます。メッセージの header の stamp に時刻を入れる場合に使います。

## 7. この章のまとめ

5つあります。

1つ目。普通の ROS2 の通信の土台、つまり DDS は、マイコンには大きすぎます。micro-ROS は、マイコンには DDS-XRCE のクライアントだけを置き、PC のエージェントが、その代わりに DDS に参加します。PC のノードと道具からは、マイコンのノードとトピックが、普通のものと同じに見えます。

2つ目。マイコンの中は、自分のプログラム、rclc と rcl、rmw_microxrcedds、Micro XRCE-DDS のクライアント、の層になっていて、rcl は PC の ROS2 と同じものです。通信路には、シリアル、UDP、TCP、自作があります。

3つ目。開発の道具は、RTOS なら micro_ros_setup、PlatformIO なら micro_ros_platformio、Arduino IDE なら micro_ros_arduino、ESP-IDF や Zephyr なら、それぞれの部品を使います。主な対象は、RAM が数十キロバイト以上ある32ビットのマイコンで、対応するボードは道具ごとの一覧で確かめます。

4つ目。rclc のノードは、準備、ノード、パブリッシャーとサブスクリプションとタイマー、実行器への登録、回す、の順に書きます。部品は起動するときに必要な数だけ作り、QoS は関数の名前で選びます。Jazzy では、タイマーを作る関数が rclc_timer_init_default2 に替わりました。

5つ目。小さなマイコンでは、部品の数の枠、つまり RMW_UXRCE_MAX で始まる設定、メッセージの大きさ、つまり MTU と、文字列や配列のメモリの用意、QoS の使い分け、エージェントとのつながりの確認に気をつけます。

## 8. つまずきやすい点

実際に micro-ROS を使い始めたときに、よく出会う症状と、確かめることを挙げます。作るときに、この章の内容を実行して確かめたものではなく、仕組みから考えた確かめどころだ、とあります。

表は2列で、7行あります。列は、症状と、確かめることです。

1行目。マイコンの rclc_support_init が失敗する場合です。PC のエージェントが動いているか。エージェントの通信路と設定、つまりシリアルの機器のパスや UDP のポートが、マイコンに書き込んだ設定と合っているか。シリアルなら、ほかのプログラム、たとえばシリアルモニタが、同じ機器を使っていないか、を確かめます。

2行目。部品を作る関数の一部だけが失敗する場合です。作ろうとした数が、6-1節の枠、たとえば RMW_UXRCE_MAX_PUBLISHERS を超えていないか。実行器に登録する数が、rclc_executor_init に渡したハンドルの数を超えていないか、を確かめます。

3行目。PC の ros2 topic echo に何も出ない場合です。エージェントの表示で、マイコンがつながったか。ros2 topic list に、マイコンのトピックがあるか。トピックの名前が、マイコンのプログラムと合っているか、を確かめます。

4行目。ros2 topic echo では読めるのに、PC の自作のノードで受け取れない場合です。送る側と受け取る側の QoS の相性、つまりフェーズ3-2b を確かめます。送る側が best_effort なら、受け取る側も best_effort にします。ros2 topic echo は、送る側に合わせて購読するので読めます。5-2節の話です。

5行目。文字列や配列のメッセージが、空のまま、または途中で切れて届く場合です。受け取る側で、中身を書き込むメモリを用意したか、つまり6-2節。メッセージが、送れる大きさを超えていないか、を確かめます。best_effort なら、MTU から12バイトを引いた大きさです。

6行目。WSL2 で、USB でつないだボードが見えない場合です。Windows の側で、usbipd-win で機器を WSL に渡したか、つまり3-3節。ユーザーが dialout のグループに入っているか、を確かめます。

7行目。ビルドで、rclc_timer_init_default が非推奨という警告が出る場合です。Jazzy では rclc_timer_init_default2 を使います。5-2節の話です。

## 9. 次へ

この章は任意の読み物なので、本筋はフェーズ6-1、記録して見直す、へ進みます。

## 10. 公式のドキュメントと参考資料

確かめた状況は、2026年10月16日の時点です。micro-ROS の公式サイトの文書のうち、Features and Architecture、Supported Hardware、License Overview、Introduction to Client Library、Micro XRCE-DDS、micro-ROS Build System、External Build Systems、First micro-ROS Application on Linux、rclc のプログラミングの各ページ、つまり Publishers and subscribers、Executor and timers、Quality of service、micro-ROS utilities、そして Middleware Configuration と、Handling messages memory in micro-ROS は、原稿、つまり GitHub の micro-ROS の micro-ROS.github.io で本文を確かめ、公開しているサイト、micro.vulcanexus.org で、同じパスのページが開けることを確かめました。micro_ros_arduino と micro_ros_platformio の対応ボードの一覧と設定は、各リポジトリの説明で、jazzy の枝の有無とライセンスは、GitHub のリポジトリの情報で確かめました。rclc の関数の引数と、rclc_timer_init_default の非推奨は、ros2 の rclc の jazzy の枝のヘッダーで確かめました。メモリを節約する設定のファイルの名前は、micro_ros_platformio と micro_ros_arduino の対応ボードの表で、micro_ros_agent が Jazzy の apt に無いことは apt-cache policy で、ros2 topic echo の QoS の選び方は、導入した ros2cli の ros2topic のソースで、usbipd bind に管理者の権限が要ることは、usbipd-win の説明で確かめました。8節の症状と確かめどころは、実際に起こして確かめたものではない、とあります。

公式の資料は、7つのまとまりです。

1つ目は、micro-ROS の公式サイトです。文書は CC BY-ND 4.0 で、作った時点には、前のアドレスの micro.ros.org から、今のアドレスに移っていました。その中の8つのページを挙げています。Features and Architecture は、特徴と層の構成です。Supported Hardware は、対象のマイコンと、対応するボードです。Micro XRCE-DDS は、クライアントとエージェント、通信路です。micro-ROS Build System と External Build Systems は、micro_ros_setup の4段階と、ほかの開発環境の部品です。First micro-ROS Application on Linux は、マイコンを使わず、PC の上で micro-ROS のノードとエージェントを動かすチュートリアルで、最初に試すのに向く、とあります。Programming with rcl and rclc の Overview は、rclc でのノード、パブリッシャー、実行器、QoS、時刻合わせなどの書き方です。Middleware Configuration は、6-1節の枠の数と MTU の設定です。Handling messages memory in micro-ROS は、6-2節の文字列と配列のメモリの用意です。

2つ目は、GitHub の micro-ROS の micro_ros_setup と micro-ROS-Agent で、ビルドの道具とエージェントです。ライセンスは Apache License 2.0 です。

3つ目は、GitHub の micro-ROS の micro_ros_platformio と micro_ros_arduino で、Arduino の形で書く場合の道具と、対応するボードの一覧です。

4つ目は、GitHub の micro-ROS の micro-ROS-demos の jazzy の枝で、rclc の例の集まりです。

5つ目は、GitHub の ros2 の rclc の jazzy の枝で、rclc のソースと説明です。実行器の詳しい説明もあります。

6つ目は、GitHub の eProsima の Micro-XRCE-DDS で、通信の土台の DDS-XRCE の実装です。

7つ目は、GitHub の dorssel の usbipd-win で、3-3節の、WSL2 で USB の機器を使う道具です。サービスとファイアウォールの規則の説明もあります。

原文の最後には、出典の注記があります。この章の説明と表は、上の公式の文書と各リポジトリの説明から、事実を独自にまとめ直したもので、転載・翻訳ではありません。micro-ROS の公式サイトの文書は CC BY-ND 4.0 のため、文章とコードを改変して載せることはせず、リンクに留めた、とあります。5節のコードは、rclc、ライセンスは Apache License 2.0 の関数を使って独自に書いたもので、公式の例の写しではありません。関数、設定、道具の名前は、各ソフトウェアのものです。

以上で、micro-ROS の間章の話を終わります。

## 出典について

この原稿は、SanghunIm1991 さんの [ros2MinimalPhysicalAi の「間章: micro-ROSでマイコンをROS2につなぐ（入門・読み物）」](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/docs/interlude_micro_ros.md)を、聞くために要約・意訳したものです。図の [interlude_micro_ros_overview.svg](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/docs/img/interlude_micro_ros_overview.svg) は、言葉で説明しました。元にしたのは、[2026年10月17日の版](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/e21773ba3dfe6808e69fde552d6a3304f3b2c958/docs/interlude_micro_ros.md)です。原文の文章と図と同じく、[クリエイティブ・コモンズ 表示 4.0 国際ライセンス](https://creativecommons.org/licenses/by/4.0/deed.ja)で提供します。

原稿の中に原文の表記のまま書いたコマンドと、コードの関数や変数の名前は、原文では [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0) の対象です。ライセンスの全文は、原文のリポジトリの [LICENSE-APACHE-2.0](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/LICENSE-APACHE-2.0) にあります。5節の骨組みのコードは写さず、構成と要の行を言葉で説明しました。

原文の説明は、[micro-ROS](https://micro.vulcanexus.org/) の公式サイトの文書（CC BY-ND 4.0）と各リポジトリの説明から、事実を独自にまとめ直したもので、原文では、公式サイトの文書の文章とコードを転載・翻訳せず、リンクに留めたとしています。この原稿も、公式サイトの文書は直接使わず、原文の説明だけを元にしています。5節のコードは、原文では、[rclc](https://github.com/ros2/rclc)（Apache License 2.0）の関数を使って独自に書いたもので、公式の例の写しではないとしています。関数・設定・道具の名前は、各ソフトウェアのものです。
