<!--
聞くための原稿（読み上げでは読まれない記録）
原文: SanghunIm1991/ros2MinimalPhysicalAi の main ブランチの docs/phase1_cli_turtlesim.md（図は docs/img/phase1_topic_flow.svg と docs/img/phase1_four_concepts.svg）
原文のコミット: 02948595c660129f78d3381c9e5c374f64bcdad0（2026-10-15）
作成: 2026-10-19、Claude Code が手作業で作成（原稿化スキルはまだない）
原文のライセンス: 文章と図は CC BY 4.0、コマンドは Apache-2.0（それぞれ LICENSE の2と1）。公式チュートリアルの例と同じ値のコマンド（ROS 2 Documentation、CC BY 4.0）と、ros2 interface show で表示する型の定義（turtlesim は BSD License、geometry_msgs は common_interfaces の Apache License 2.0）は、LICENSE の「第三者の著作物」にある。この原稿は、原文を聞くために要約・意訳したもの（改変あり）
方針: 英語の略語や製品名、短いコマンドは原文の表記のまま書く。公式チュートリアルと同じ値のコマンドの行と、型の定義、期待する結果（各ツールの表示）は写さず、何をするか、何が表示されるかを言葉で説明した。図と表（切り分け、ターミナルの構成、QoS の項目、4つの通信のまとめ、つまずきやすい点、turtlesim のソースの対応）は言葉で説明する。文字数の上限は設けない
省いたもの: URL、日本語の記事の題名（記事が2本あることだけ触れた）、ソースのファイルへのリンク
-->

# フェーズ1: turtlesim と CLI で ROS2 の通信を観察する（聞くための原稿）

これは、ros2MinimalPhysicalAi という教材の、フェーズ1 の手順書の話です。コードは書かず、既製のノードである turtlesim を動かしながら、ros2 のコマンドと rqt で、ROS2 の仕組みを観察します。

想定する環境は、WSL2 と Ubuntu 24.04 と ROS2 Jazzy で、環境構築の手順書を終えていることが前提です。所要時間の目安は1コマから2コマです。このフェーズは言語に依存せず、Python と C++ の区別はありません。

原文には、位置づけと注意の囲みがあります。この手順書のコマンドは、2026年9月21日に、すべて実機で実行して動きを確かめています。ただし、コマンドと出力の例は、筆者である Claude の知識に基づくもので、表示が細部で違う場合は実機を優先します。公式のページ docs.ros.org はボット対策で本文を取得できず、一語ずつの照合はできていません。文章と構成は筆者の言葉で書いたものですが、コマンドの例の値、例えば亀に送る速度や、亀を出す座標、回す角度などは、公式のチュートリアルの例と同じものを含みます。公式のドキュメントは CC BY 4.0 です。また、期待する結果に載せた型の定義のうち、turtlesim の型は turtlesim パッケージのもので BSD License、geometry_msgs の型は common_interfaces のもので Apache License 2.0 です。

この原稿では、公式のチュートリアルと同じ値のコマンドの行や、型の定義、ツールの表示は書き写さず、何をするか、何が表示されるかを言葉で説明します。

## 0. 学習目標と完了の条件

学ぶことは、ROS2 の4つの通信、つまりトピック、サービス、パラメータ、アクションと、それを調べる ros2 のコマンドです。

完了の条件は5つで、すべて満たします。

1つ目。/turtle1/cmd_vel のトピックの型が geometry_msgs/msg/Twist であることを ros2 interface show で確かめ、フィールドの意味、つまり直進の速度と回転の速度を説明できる。

2つ目。ros2 topic pub で亀を動かせる。

3つ目。トピック、サービス、パラメータ、アクションを、それぞれ1回以上コマンドで操作できる。

4つ目。4つの通信の違い、つまり誰が誰に送るか、一方向か往復か、途中経過があるか、を自分の言葉で説明できる。

5つ目。rqt_graph の図と、ノードやトピックの一覧が対応していると確かめられる。

## 1. 準備

### 1-1. パッケージの導入

turtlesim と rqt は、ROS2 の公式の apt のパッケージです。環境構築の手順書のとおり Desktop Install で導入していれば、すでに入っています。下のコマンドを実行しても、最新版だと表示されるだけで、害はありません。

原文は、目的とセキュリティへの影響を書いています。目的は、観察用のシミュレータの turtlesim と、GUI のツールの rqt を入れることです。セキュリティへの影響は、環境構築の手順書で登録した公式の apt のリポジトリからの導入で、外部との通信は apt の取得だけです。追加のリポジトリの登録はありません。

コマンドは、sudo apt update の後、sudo apt install -y で、ros-jazzy-turtlesim、ros-jazzy-rqt、ros-jazzy-rqt-graph、ros-jazzy-rqt-console の4つのパッケージを入れるものです。期待する結果は、導入するパッケージの一覧が表示され、最後に E とコロンで始まるエラーの行が出ずに、プロンプトへ戻ることです。

導入を確かめるには、ros2 pkg executables turtlesim を実行します。ros2 pkg executables にパッケージの名前を付けると、そのパッケージに入っている実行ファイル、つまり ros2 run で起動できるプログラムの名前を並べます。期待する結果は、turtlesim パッケージの4つの実行ファイル、draw_square、mimic、turtle_teleop_key、turtlesim_node が、パッケージ名と並んで表示されることです。

### 1-2. GUI が出ることの確認

turtlesim や rqt は、WSLg を通して、Windows の側にウィンドウが出ます。手順は4つです。

手順A は、表示の前提を、WSL の側で確かめることです。echo で DISPLAY の環境変数を表示して、空でなければよい。WAYLAND_DISPLAY の環境変数も表示しますが、これは空でも、X11 を通して表示できることが多いそうです。そして、ls /mnt/wslg で、WSLg の領域が見えることを確かめます。WSLg が有効な場合の期待する結果は、DISPLAY がコロン0、WAYLAND_DISPLAY が wayland-0 で、/mnt/wslg には、PulseServer、runtime-dir、いくつかのログのファイルなどが並ぶことです。/mnt/wslg の中身は版によって多少違い、ディレクトリがあって何かが並べばよい、とあります。

手順B は、1つ目のターミナル、T1 で、turtlesim を起動することです。コマンドは ros2 run turtlesim turtlesim_node です。書式は、ros2 run の後にパッケージの名前と実行ファイルの名前を続ける形で、ここでは turtlesim パッケージの turtlesim_node、つまり亀を表示するシミュレータのノードを起動します。期待する結果は、水色、つまり青系の背景に、亀が1匹いるウィンドウが、Windows の側に出ることです。ターミナルには、INFO のログが2行出ます。1行目は、turtlesim を /turtlesim というノード名で起動した、という内容。2行目は、turtle1 という亀を、x と y がどちらも約5.54、theta が0 の位置に出した、という内容です。亀の初めの位置は画面の中央で、向きの theta が0 というのは右向きです。確かめたら、T1 で Ctrl+C を押して止めます。ウィンドウも閉じます。

手順C は、T1 で rqt を起動することです。期待する結果は、空の rqt のウィンドウが出ることで、上のメニューの Plugins が開ければよい、とあります。ここではプラグインは使いません。確かめたら、ウィンドウを閉じるか、Ctrl+C で止めます。

手順D は任意で、起動できるものを個別に確かめることです。T1 で rqt_graph を起動します。これはノードとトピックの図を出すウィンドウで、フェーズ1 の後半で使います。T2 では、ros2 run rqt_console rqt_console を実行します。これはログを表示するウィンドウです。rqt_console は、単独のコマンドとしては PATH に無いので、ros2 run を通して起動します。期待する結果は、T1 と T2 のそれぞれで、ウィンドウが Windows の側に開くことです。中身は3-8節で使います。どちらのコマンドも、ウィンドウを閉じるまでターミナルを占めるので、ターミナルを分けて実行します。確かめたら、ウィンドウを閉じます。

うまくいかない場合の切り分けは、症状と、確かめることと対処の2列の表で、4行あります。

1行目。echo で DISPLAY が空の場合は、WSLg が無効です。Windows の側の PowerShell で wsl --version を実行して WSLg の記載を確かめ、wsl --update を実行します。

2行目。wsl --update の後も出ない場合は、Windows の側の PowerShell で wsl --shutdown を実行し、WSL を開き直して、手順A からやり直します。

3行目。Qt の could not connect to display のようなエラーの場合は、手順A の DISPLAY をもう一度確かめます。一時的な確認として、別のターミナルで、DISPLAY をコロン0 に設定する export を試します。

4行目。Package 'turtlesim' not found の場合は、1-1節の導入が終わっていません。ros2 pkg executables turtlesim で確かめます。

これらは、どれも読み取りか、自分の PC の中でのプロセスの起動で、外部との通信や設定の変更はありません。ただし、wsl --update は Microsoft の公式の更新で、Windows の側の変更を伴うので、実行するかは自分で判断します。出力の例とエラーの文言は筆者の知識に基づくもので、実機の表示が違う場合は、実機を優先します。

### 1-3. 環境変数を書き足す

ほかの PC やネットワークの上の ROS2 のノードと混線しないよう、通信の範囲を、自分の PC の中に限ります。コマンドは、ROS_AUTOMATIC_DISCOVERY_RANGE という環境変数を LOCALHOST にする export です。期待する結果は、何も表示されないことです。export は、成功しても何も表示しません。echo でこの環境変数を表示して、LOCALHOST と出れば、設定されています。

環境変数は、ターミナルごとの設定です。毎回手で入力すると、T1 から T3 の一部だけ設定が漏れて、通信の範囲が食い違い、ros2 node list が空になる、という、再現しない不具合につながります。そこで、~/.bashrc に書き足します。書き足した後は、新しく開くターミナルから有効になります。

~/.bashrc に書き足す行の、この時点の累積の一覧は2行です。1行目は、環境構築の手順で足した、ROS2 本体の setup.bash を読み込む行で、いつも必要で、消さない行。2行目は、このフェーズで足した、通信の範囲を自分の PC の中に限る export の行で、これもいつも必要で、消さない行です。

以後のフェーズで ~/.bashrc に書き足す必要が出たら、その手順書の中で、この一覧に足した累積の一覧を示します。学習が一区切りついたときに、どれがいつも要る設定で、どれが確認のための一時的な行かを見分けられるようにするためです。

### 1-4. ターミナルの構成

ターミナルを複数使います。どのターミナルでも、ROS2 は ~/.bashrc で読み込み済みなので、追加の source は要りません。原文の表では、T1 は turtlesim の本体を動かし続ける、T2 は操作用のキーボード、つまり teleop か、観察のコマンドを実行する、T3 は観察のコマンドを追加で実行する、という役割です。

## 2. 全体像

まず、これから観察する対象を、図で押さえます。原文の図は2つで、どちらも SVG と mermaid の版があります。

1つ目の図は、トピックの流れです。左から右へ、3つの箱が並びます。左の箱は turtle_teleop_key というノード、真ん中の箱は turtlesim_node というノード、右の箱は「ros2 topic echo など」です。左の箱から真ん中の箱へ、トピック /turtle1/cmd_vel の矢印があり、その型は Twist で、指令です。真ん中の箱から右の箱へ、トピック /turtle1/pose の矢印があり、その型は Pose で、状態です。つまり、キーボードのノードが亀に指令を送り、亀のシミュレータが状態を返して、それを ros2 topic echo などで見る、という形です。

2つ目の図は、4つの通信の違いです。4つの点線の枠が、2行2列に並んでいます。

左上の枠は、トピックで、一方向で継続的。Publisher の箱から Subscriber の箱へ、矢印が1本あります。

右上の枠は、サービスで、要求から応答への1回。Client の箱から Server の箱へ「要求」の矢印があり、Server から Client へ「応答」の矢印が戻ります。

左下の枠は、パラメータで、ノードの設定の値。「ros2 param や、ほかのノード」の箱から、「ノード」の箱へ、「get / set」の矢印があります。

右下の枠は、アクションで、長い処理で途中経過つき。Client の箱から Server の箱へ「goal」の矢印があり、Server から Client へ、「feedback、途中経過」と「result、最終結果」の2本の矢印が戻ります。

原文は、ここで、車両のシミュレーションとの対応を、フェーズ5 への伏線として書いています。フェーズ5 では、車両を、制御ノードと、プラントのノードに分けて作ります。制御ノードは目標に近づくように指令を出す側、プラントは制御される対象で、指令を受けて動き、今の状態を返す側です。Twist は制御ノードからプラントへの指令に、Pose はプラントから制御ノードへの状態に相当します。turtlesim は、後で作るプラントのノードの見本になる、とあります。

## 3. 手順

### 3-1. turtlesim を起動する（T1）

T1 で、ros2 run turtlesim turtlesim_node を実行します。期待する結果は、青い背景に亀のウィンドウが出ることです。ターミナルのログは、1-2節の手順B と同じです。

### 3-2. キーボードで動かす（T2）

T2 で、ros2 run turtlesim turtle_teleop_key を実行します。期待する結果は、T2 に、操作の方法の英語の案内が出ることです。内容は、キーボードから読み取っていること、矢印のキーで亀を動かすこと、G、B、V、C、D、E、R、T のキーで決まった向きに回り、F で回転を取り消すこと、Q で終わること、です。

このターミナルを選んだ状態で矢印のキーを押すと、亀が動きます。上で前進、下で後退、左右でその場で旋回します。亀が通った跡には、白い線が残ります。動いたら、その裏で何がやり取りされているかが、次の観察の対象になります。

### 3-3. ノードを調べる（T3）

T3 で、ros2 node list と、ros2 node info /turtlesim を実行します。node list には、T1 と T2 で動かしている2つのノードが並びます。node info の出力には、そのノードが購読するもの、つまり Subscribers、配信するもの、つまり Publishers、提供するサービス、つまり Service Servers、そしてアクション、つまり Action Servers が並びます。

期待する結果は、こうです。node list には、/teleop_turtle と /turtlesim の2つが並びます。node info /turtlesim では、トピック名とその型の組が、種類ごとに並びます。

Subscribers には、/parameter_events と、/turtle1/cmd_vel の Twist 型があります。

Publishers には、/parameter_events、ログの /rosout、/turtle1/color_sensor の Color 型、そして /turtle1/pose の Pose 型があります。

Service Servers には、/clear と /reset、これらは中身の無い Empty 型です。ほかに、/kill、/spawn、/turtle1/set_pen、/turtle1/teleport_absolute、/turtle1/teleport_relative があり、さらに /turtlesim/describe_parameters のような、パラメータのためのサービスが6つほど続きます。原文の例では、これは省略されています。

Service Clients は空です。

Action Servers には、/turtle1/rotate_absolute の RotateAbsolute 型があります。Action Clients は空です。

名前の付き方にも意味があります。/turtle1/ で始まる名前のものは、亀1匹ごとに用意され、/clear や /spawn のように亀の名前が付かないものは、シミュレータ全体に1つだけあります。

課題1 は、/turtlesim の Subscribers に /turtle1/cmd_vel が、Publishers に /turtle1/pose があることを確かめることです。

次に、ノードの名前の付け替え、remap も試します。T1 の turtlesim を止めて、名前を変えて起動し直します。T1 では、turtlesim_node を、--ros-args の後に、ノードの名前を my_turtle に付け替える remap の指定を付けて起動し、T3 で ros2 node list を実行します。--ros-args より後ろは、プログラムではなく ROS2 に向けた指定です。remap の指定は、ノードの名前を表す __node を、my_turtle に付け替える、という意味です。

期待する結果は、ノードの一覧の /turtlesim が /my_turtle に置き換わることです。一覧は /my_turtle と /teleop_turtle になります。起動のログも、/my_turtle というノード名で起動した、という内容になります。亀のウィンドウの動きは、何も変わりません。

試し終わったら、T1 を Ctrl+C で止め、元の名前で起動し直してから次へ進みます。この後のコマンドは、/turtlesim という名前を前提にしているからです。

### 3-4. トピック（一方向・継続的）

まず、トピックを調べる5つのコマンドを実行します。

1つ目は、ros2 topic list -t です。-t で、型も表示します。

2つ目は、ros2 topic info /turtle1/cmd_vel で、型と、Publisher の数と、Subscription の数を表示します。

3つ目は、ros2 interface show geometry_msgs/msg/Twist で、Twist 型の中身を表示します。

4つ目は、ros2 topic echo /turtle1/pose で、亀の状態を流して見ます。Ctrl+C で止めます。

5つ目は、ros2 topic hz /turtle1/pose で、配信の周期を測ります。

期待する結果を、1つずつ説明します。echo と hz は、Ctrl+C で止めるまで表示が続きます。

topic list -t では、トピックの名前と、角括弧に入った型が、5行並びます。/parameter_events、/rosout、/turtle1/cmd_vel の Twist、/turtle1/color_sensor の Color、そして /turtle1/pose の Pose です。

topic info /turtle1/cmd_vel では、型が geometry_msgs/msg/Twist、Publisher の数が1、Subscription の数が1 と表示されます。Publisher の1 は teleop、つまり /teleop_turtle で、Subscription の1 は turtlesim です。teleop を止めると、Publisher の数は0 になります。

interface show で表示される Twist 型の定義は、1行の説明のコメントで始まります。中身は2つのフィールドで、linear と angular です。どちらも Vector3 という型で、それぞれ float64 の x、y、z を持ちます。

topic echo /turtle1/pose では、x、y、theta、linear_velocity、angular_velocity の5つの値が、ハイフン3つの区切りの行を挟みながら、繰り返し表示されます。初めは、x と y が約5.54、ほかは0 です。亀が止まっていても、同じ値を流し続けます。状態を定期的に配信しているからです。矢印のキーで亀を動かすと、x、y、theta の値が変わります。

topic hz /turtle1/pose では、平均の周期が約62 Hz と表示され、最小と最大の間隔、標準偏差、測った件数が続きます。約62 Hz というのは、turtlesim の内部の更新の周期、約16ミリ秒ごとです。

Twist は、linear の x、y、z と、angular の x、y、z を持ちます。2次元の亀では、linear の x、つまり前進の速度と、angular の z、つまり旋回の速度だけが意味を持ちます。

次に、コマンドから直接、指令を送ります。ros2 topic pub で、/turtle1/cmd_vel に Twist の型のメッセージを送ります。中身は、linear の x を 2.0、angular の z を 1.8 にしたもので、前に進みながら旋回する指令です。送り方は2通りあります。--once を付けると、1回だけ送ります。-r 1 を付けると、1 Hz で送り続け、亀は円を描きます。Ctrl+C で止めます。

期待する結果は、どちらのコマンドも、送った内容をターミナルに表示することです。最初に、送るループを始めたという行が出て、続いて、何番目に送ったかの番号と、送った Twist の中身、つまり linear の x が2.0、angular の z が1.8 で、ほかが0 の値が表示されます。

--once では、亀は弧を描いて少し進み、約1秒で止まります。turtlesim は、指令が1秒届かないと止まる作りだからです。コマンドは1回送ると終わります。-r 1 では、送った番号が2、3と1秒ごとに増え、亀は円を描き続けます。指令が1秒おきに届くので、止まる前に次の指令が来て、動き続けます。

課題2 は、--once と -r 1 で、亀の動き方がどう違うかを観察することです。ros2 topic echo /turtle1/pose を並行して実行し、位置の x と y、角度の theta が変わる様子を確かめます。

課題3 は、ros2 topic hz /turtle1/cmd_vel を実行しながら、pub を -r 1 と -r 10 で試し、周期が一致することを確かめることです。

### 3-5. サービス（要求から応答）

サービスを調べて呼ぶ、5つのコマンドを実行します。

1つ目は、ros2 service list -t で、サービスの一覧を型と一緒に表示します。

2つ目は、ros2 service type /clear で、/clear の型を表示します。

3つ目は、ros2 interface show turtlesim/srv/Spawn で、Spawn 型の中身を表示します。

4つ目は、ros2 service call で、/clear を、Empty 型で呼びます。画面の軌跡が消えます。

5つ目は、ros2 service call で /spawn を呼び、亀を足します。要求の中身は、x と y が2.0、theta が0.2、名前が空、です。

期待する結果を説明します。

service list -t では、/clear、/kill、/reset、/spawn、そして /turtle1/set_pen、/turtle1/teleport_absolute、/turtle1/teleport_relative などが、型と一緒に並びます。そのほかに、/teleop_turtle/describe_parameters や /turtlesim/describe_parameters のような、ノードごとに自動で作られるパラメータのためのサービスが、たくさん並びます。自分で使うのは、/clear や /spawn などです。

service type /clear では、std_srvs/srv/Empty と表示されます。

interface show turtlesim/srv/Spawn で表示される Spawn 型の定義は、ハイフン3つの行で、上と下の2つに分かれています。上は要求、つまり Request で、float32 の x、y、theta と、string の name です。name の行には、注記のコメントが付いています。下は応答、つまり Response で、string の name だけです。サービスの型は、この要求と応答の組です。

service call で /clear を呼ぶと、要求を送ったという行と、空の要求の表示が出て、続いて応答として、空の応答の表示が出ます。画面の軌跡、つまり白い線が消えます。/clear の型の Empty は、要求にも応答にも中身がありません。応答は空で、終わったことだけが返ります。

service call で /spawn を呼ぶと、要求として x が2.0、y が2.0、theta が0.2、name が空の内容を送ったという表示が出て、応答として、name が turtle2 の内容が返ります。画面の左下寄り、つまり x が2、y が2 の所に、2匹目の亀が現れます。name を空にしたので、名前が自動で付いて、turtle2 が返ってきたわけです。

/spawn の後で ros2 topic list を実行すると、2匹目の亀の、/turtle2/ で始まるトピックが増えています。ノードの名前や名前空間で、対象が区別されることを確かめます。

課題4 は、/spawn で2匹目を出し、ros2 topic pub で /turtle2/cmd_vel に指令を送って、2匹目だけを動かすことです。

### 3-6. パラメータ（ノードの設定の値）

パラメータを扱う、4つのコマンドを実行します。

1つ目は、ros2 param list で、パラメータの一覧を表示します。

2つ目は、ros2 param get で、/turtlesim の background_r、つまり背景の色の赤の成分を読みます。

3つ目は、ros2 param set で、/turtlesim の background_r を150 にします。背景の色が変わります。

4つ目は、ros2 param dump /turtlesim で、今の設定を YAML で出力します。

期待する結果です。param list では、動いているノードごとに、パラメータの名前が並びます。/teleop_turtle の下には、QoS の上書きの設定の項目や、scale_angular、scale_linear、use_sim_time などが並びます。/turtlesim の下には、background_b、background_g、background_r、holonomic、QoS の上書きの設定の項目、use_sim_time などが並びます。

param get では、整数の値が69 だと表示されます。param set では、パラメータの設定に成功した、と表示されます。背景の色の初めの値は、赤が69、緑が86、青が255 で、青い色です。background_r を150 に上げると、背景が紫がかった色に変わります。

param dump の出力は YAML の形式で、フェーズ3-3 の5-4節で、起動するときに YAML でパラメータを与えるときの書式の見本になります。background_r を150 に変えた後の、param dump /turtlesim の期待する結果は、こうです。一番上に /turtlesim の行があり、その下に ros__parameters の行、さらにその下に、パラメータの名前と値の組が並びます。background_b が255、background_g が86、background_r が150、holonomic が false。続いて qos_overrides の項があり、/parameter_events の publisher について、depth が1000、durability が volatile、history が keep_last、reliability が reliable と、入れ子で並びます。最後に、use_sim_time が false です。

読み方は4つです。1つ目。先頭の /turtlesim が対象のノードの名前で、その下の ros__parameters に、パラメータの名前と値が並びます。ノードの名前から始まるこの階層が、フェーズ3 で使うパラメータの YAML の書式そのものです。2つ目。background の r、g、b、つまり背景の色は、set で変えた値が反映されています。use_sim_time は、シミュレーションの時刻を使うかどうかの共通のパラメータで、ここでは false です。3つ目。qos_overrides の項は、そのノードが使うトピックの通信の品質、QoS の設定の値で、次の補足で説明します。4つ目。出力の例は筆者の知識に基づくもので、パラメータの種類、順序、値は、実機で違うことがあります。例えば holonomic があるかどうかです。実機の出力を優先します。

ここで、QoS についての軽い補足があります。QoS、Quality of Service は、トピックの通信の信頼性、過去のデータを覚えておくか、キューの深さなどを決める設定で、Publisher と Subscriber がそれぞれ持ちます。上の qos_overrides に出ている項目の意味は、項目と意味の2列の表で、3行あります。

reliability。reliable は、届くまで再送する。best_effort は、再送せず、取りこぼしを許して、速さを優先する。上の例の値は reliable です。

durability。volatile は、過去の分は保存しない。transient_local は、後から参加した相手にも、直近の分を渡す。上の例の値は volatile です。

history と depth。keep_last と depth の組で、最新の N 件だけをキューに持つ。上の例では1000件です。

Publisher の側と Subscriber の側の QoS がかみ合わないと、エラーにならずに、黙ってつながらないことがあります。実際の相性の体験は、フェーズ3-2b で行います。キューの深さの10 の意味は、フェーズ3-1 でも触れます。今の段階では、トピックには QoS という設定があり、ros2 topic info /turtle1/cmd_vel に -v を付けても見られる、と知っておけば十分です。

課題5 は、ros2 param dump /turtlesim の出力を、/tmp の turtlesim_params.yaml というファイルにリダイレクトして保存し、中身を読むことです。保存先は、/tmp のような作業の外でよく、リポジトリには入れません。

### 3-7. アクション（途中経過つきの長い処理）

アクションを扱う、4つのコマンドを実行します。

1つ目は、ros2 action list -t で、アクションの一覧を型と一緒に表示します。

2つ目は、ros2 action info /turtle1/rotate_absolute で、このアクションのクライアントとサーバを表示します。

3つ目は、ros2 interface show turtlesim/action/RotateAbsolute で、型の中身を表示します。

4つ目は、ros2 action send_goal で、/turtle1/rotate_absolute にゴールを送ります。ゴールの中身は theta が1.57 で、--feedback を付けて、途中経過も表示します。

期待する結果です。action list -t では、/turtle1/rotate_absolute と、その RotateAbsolute 型の1行が表示されます。

action info では、アクションの名前の後に、アクションのクライアントが1つで /teleop_turtle、アクションのサーバが1つで /turtlesim、と表示されます。

interface show で表示される RotateAbsolute 型の定義は、ハイフン3つの行で、3つに区切られています。上から、ゴール、つまり目標の float32 の theta、結果の float32 の delta、そしてフィードバック、つまり途中経過の float32 の remaining で、それぞれに説明のコメントが付いています。theta は向きの目標で、remaining は残りの回転の角度です。

send_goal では、まず、アクションのサーバが使えるようになるのを待っている、という行が出ます。続いて、theta が1.57 のゴールを送ったこと、ゴールが受け付けられて ID が付いたことが表示されます。その後、Feedback の見出しと remaining の値の組が、何度も流れます。remaining は、約1.55、約1.54と、少しずつ減っていきます。実際には、もっと多くの行が流れます。最後に、Result の見出しと delta の値、つまり約マイナス1.55 が表示され、ゴールが SUCCEEDED の状態で終わった、と表示されます。

読み方は4つです。1つ目。アクションの型は、ハイフン3つの行で3つに区切られ、上から、ゴール、結果、フィードバックです。2つ目。亀は、その場で左に回って、上向き、つまり1.57ラジアン、約90度の向きになります。remaining、つまり残りの回転の角度が0 に向かって減り、最後に Result と SUCCEEDED が出ます。3つ目。teleop も、アクションのクライアントになっています。action info の /teleop_turtle がそれで、teleop の G や B などのキーは、このアクションを使って向きを変えています。4つ目。remaining や delta の数値は、亀が初めにどちらを向いていたかで変わります。

--feedback を付けると、回転の途中経過、つまり残りの角度が流れ、最後に結果が返ります。サービスとの違い、つまり途中経過があり、実行中に中断できることを、体で感じてください、とあります。

課題6 は、回転の途中で Ctrl+C を押してみることです。ゴールがキャンセルされます。次に、もう一度 theta を変えて実行し、フィードバックの値が減っていく様子を観察します。

### 3-8. rqt で可視化する

T1 と T2 で turtlesim と teleop が動いたまま、rqt_graph を起動します。Windows の側にウィンドウが開きます。

/teleop_turtle から /turtle1/cmd_vel、そして /turtlesim へ、という図が出ます。楕円がノードで、矢印に添えられた名前がトピックです。表示のフィルタによっては、トピックが四角で描かれます。/spawn でノードを足した後は、左上の更新のボタンで反映します。

課題7 は、2節の図と実際の rqt_graph を見比べることです。表示のフィルタを、ノードだけの Nodes only と、ノードとすべてのトピックの Nodes/Topics (all) で切り替え、隠れていたトピック、例えば /rosout などを確かめます。

続いて、ログを見る rqt_console を、ros2 run rqt_console rqt_console で起動します。期待する結果は、rqt_console のウィンドウが開くことです。亀を壁にぶつけると、警告のログ、Warn が出ます。rqt_console のウィンドウには、WARN の印と時刻と turtlesim の名前の後に、壁に当たった、という英語の文と、押し戻す前の位置、例えば x が約11.1、y が約5.54 の値が表示されます。T1 の turtlesim のターミナルにも、同じ文が出ます。これは、壁に当たったので、位置を画面の中に押し戻した、という意味です。ログのレベル、つまり Debug、Info、Warn、Error、Fatal で絞り込むことも試します。

### 3-9. 片付け

各ターミナルで Ctrl+C を押します。ウィンドウは閉じてかまいません。

## 4. 4つの通信のまとめ

このフェーズで観察した4つの通信を、実際に使ったコマンドとあわせて振り返ります。2節の図の、一方向か往復か、途中経過があるか、に、3節で実行したコマンドを対応させた表で、列は、通信、操作したコマンド、一方向か往復か、途中経過、の4つです。4行あります。

トピック。操作したコマンドは、ros2 topic pub と ros2 topic echo。一方向で継続的。途中経過は無く、値が流れ続けるだけ。

サービス。ros2 service call。往復で、要求から応答。途中経過は無く、1回で終わる。

パラメータ。ros2 param get と set。往復で、get と set。途中経過は無し。

アクション。ros2 action send_goal。往復で、goal から result。途中経過は有り、feedback で進み具合が届く。

整理の仕方として、原文は2つの軸を勧めています。途中経過、つまり feedback があるかどうかが、アクションとサービスを分ける決定的な違い。そして、継続的に流れ続けるか、1回で終わるかが、トピックと、サービスやパラメータを分ける違いです。

## 5. つまずきやすい点

原文では、症状と、確かめることの2列の表で、5行あります。

ros2: command not found の場合は、新しいターミナルを開き、echo で ROS_DISTRO が jazzy かを確かめる。

ウィンドウが出ない場合は、echo で DISPLAY を確かめ、Windows の側で wsl --update を実行する。

ros2 node list が空の場合は、別のターミナルで turtlesim が動いているかを確かめ、ROS_AUTOMATIC_DISCOVERY_RANGE を、すべてのターミナルでそろえる。

teleop で亀が動かない場合は、teleop のターミナルが選ばれているか、つまり矢印のキーの入力先を確かめる。

出力が手順書と違う場合は、版や環境による違いのことが多い。実機の表示を優先し、ERROR や error: などのエラーでなければ、先へ進んでよい。

## 6. 次のフェーズへ

フェーズ2 で、パッケージの作成とビルドを学びます。ament_python と ament_cmake の空のパッケージを作ります。このフェーズで確かめた、ros2 run の後にパッケージと実行ファイルを続ける書式が、自分で作ったパッケージでも同じように使えます。

3D の物理シミュレータの Gazebo で、車両が動く様子を先に見てみたい場合は、フェーズ2 の前に、フェーズ5-0 の1節から3節へ寄り道してもかまいません。このフェーズで使った ros2 topic pub で Gazebo の車両を走らせ、ros2 topic echo でその様子を見られます。動くものを楽しむのが目的で、仕組みの理解は、後で戻ったときでよい、とあります。範囲と注意は、フェーズ5-0 の冒頭にあります。

## 7. 公式ドキュメントと参考資料

確認の状況が書かれています。2026年9月20日に、公式のチュートリアルの3つのページと、Qiita の記事2本は、Web の検索結果で実在を確かめています。ほかの3つの公式のページは、企画の文書に載せた URL で、今回は確かめ直していません。docs.ros.org は、ボット対策で本文の取得が拒否されたので、内容の照合はできていません。

公式の資料は、ROS 2 Jazzy の6つのページです。CLI のツールの初心者向けのチュートリアルの目次、turtlesim と ros2 と rqt の使い方、rqt_console でログを見る方法、ノードの起動、つまりフェーズ4 の予習、コマンドラインのツールでの調べ方、そして基本の概念です。

### turtlesim のソースコード（任意）

このフェーズは、コードを読まなくても終えられます。3節で観察したトピック、サービス、パラメータ、アクションが、ノードの中でどう作られているかを見てみたい場合の手がかりとして、原文は turtlesim のソースを紹介しています。中身は C++ と、GUI の部品の集まりである Qt で書かれています。C++ のノードの書き方はフェーズ3-1 の4節で学ぶので、今は、どのファイルに何があるかの見当をつける程度でよい、とあります。

apt で入れた turtlesim には、ビルド済みのプログラム、つまり opt の ros の jazzy の lib の turtlesim にある4つと、型の定義、つまり share の turtlesim の下の msg、srv、action のフォルダだけが入っていて、C++ のソースは入っていません。ソースは、GitHub の公式のリポジトリ ros/ros_tutorials の、jazzy ブランチの turtlesim のフォルダにあり、BSD License です。

主なファイルと、3節で観察したものとの対応は、ファイル、中身、3節で観察したもの、の3列の表で、5行あります。2026年10月15日に、jazzy ブランチで確かめたものです。

src の turtlesim.cpp。turtlesim_node の main 関数で、ROS2 と Qt のアプリを起動する。3-1節の起動に対応。

src の turtle_frame.cpp。青い背景のウィンドウと、亀の全体の管理。背景の色と holonomic のパラメータの宣言と、/clear、/reset、/spawn、/kill のサービス。3-5節のサービスと、3-6節のパラメータに対応。

src の turtle.cpp。1匹の亀の動き。cmd_vel の購読、pose と color_sensor の配信、set_pen と teleport のサービス、そして rotate_absolute のアクション。どれも、例えば /turtle1/ のように、亀の名前が付く。3-4節のトピック、3-5節の /turtle1/set_pen などのサービス、3-7節のアクションに対応。

tutorials の teleop_turtle_key.cpp。turtle_teleop_key で、キーの入力を cmd_vel として配信し、rotate_absolute のゴールを送る。3-2節のキーボードの操作に対応。G や B などのキーで向きを変えるのは、3-7節のアクションです。

tutorials の draw_square.cpp と mimic.cpp。1-1節で一覧に出た残りの2つで、この手順書では使わない。

どの実行ファイルがどのソースから作られるかは、同じフォルダの CMakeLists.txt の add_executable の行に書かれています。CMakeLists.txt の読み方は、フェーズ2 の1-3節と1-4節で学びます。ブランチは、使っている ROS2 の版、この教材では jazzy に合わせます。既定のブランチは開発中の版のもので、Jazzy のものと細部が違う場合があります。

### 日本語の記事

ほかに、日本語の記事として、Qiita の記事が2本挙げられています。1本は、ROS 2 のツールの実習、もう1本は、Ubuntu 24.04 向けの turtlesim の環境構築の記事です。記事は個人による非公式の解説で、版によってコマンドや出力が違う場合があり、公式のドキュメントと食い違う場合は公式を優先する、とあります。

以上で、フェーズ1 の手順書の話を終わります。

## 出典について

この原稿は、SanghunIm1991 さんの [ros2MinimalPhysicalAi の「フェーズ1 手順書: turtlesimとCLIでROS2の通信を観察する」](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/docs/phase1_cli_turtlesim.md)を、聞くために要約・意訳したものです。図の [phase1_topic_flow.svg](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/docs/img/phase1_topic_flow.svg) と [phase1_four_concepts.svg](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/docs/img/phase1_four_concepts.svg) は、言葉で説明しました。元にしたのは、[2026年10月15日の版](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/02948595c660129f78d3381c9e5c374f64bcdad0/docs/phase1_cli_turtlesim.md)です。原文の文章と図と同じく、[クリエイティブ・コモンズ 表示 4.0 国際ライセンス](https://creativecommons.org/licenses/by/4.0/deed.ja)で提供します。

原稿の中に原文の表記のまま書いたコマンドは、原文では [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0) の対象です。ライセンスの全文は、原文のリポジトリの [LICENSE-APACHE-2.0](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/LICENSE-APACHE-2.0) にあります。

原文のうち、公式チュートリアルの例と同じ値を使ったコマンドの例は [ROS 2 Documentation](https://docs.ros.org/en/jazzy/)（Open Robotics、[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)）、ros2 interface show の表示として載せた型の定義は、turtlesim の型が [turtlesim](https://github.com/ros/ros_tutorials/tree/jazzy/turtlesim)（BSD License）、geometry_msgs の型が [common_interfaces](https://github.com/ros2/common_interfaces)（Apache License 2.0）のものです。この原稿では、それらを写さず、何をするか、何が表示されるかを言葉で説明しました。表示の例は、各ツールの表示を言葉で説明したものです。
