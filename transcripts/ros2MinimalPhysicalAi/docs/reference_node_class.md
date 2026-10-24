<!--
聞くための原稿（読み上げでは読まれない記録）
原文: SanghunIm1991/ros2MinimalPhysicalAi の main ブランチの docs/reference_node_class.md（図は docs/img/reference_node_rclpy.svg と docs/img/reference_node_rclcpp.svg）
原文のコミット: 86dc0ed3d606c4a05d1e087421bb10318a37e521（2026-10-14）
作成: 2026-10-24、Claude Code が手作業で作成（原稿化スキルはまだない）
原文のライセンス: 文章と図は CC BY 4.0、コードとコマンドは Apache-2.0（それぞれ LICENSE の2と1）。原文にはサンプルコードも実行の手順も無く、本文に出てくるクラス・変数・メソッドの名前と短い呼び出しの例だけが Apache-2.0 の対象になりうる。原文の冒頭に、クラスの構造・変数名・メソッド名は ROS2 Jazzy のソースを読んで確かめたもので、文章は自分の言葉で書いており、ソースの転載ではない、とある。この原稿は、原文を聞くために要約・意訳したもの（改変あり）
方針: 英語の略語や製品名、クラス・変数・メソッドの名前は原文の表記のまま書く。名前の先頭のアンダースコアの数が意味を持つ __node だけ、「アンダースコアが2つの」と言い添えた。C++ のテンプレートの < > は「山括弧」と言った。2つの図（SVG）は、箱の並びと線の種類を言葉で説明した。表（変数の読み方、メソッドの分類、11個の部品、比較、教材のどこで何を使ったか）は言葉で説明し、値は全部読んだ。原文の手順書への参照（フェーズ3-1 の1節の図など）は、原文どおり言った。公式ドキュメントの節は、リンクの題名と括弧の説明を読んだ。文字数の上限は設けない
省いたもの: URL、リンク先のファイル名、String の型の定義へのリンク、mermaid 版の図（SVG と同じ内容で、折りたたみになっている）、図の中の箱の座標と色の細部、図の中のメソッドの引数と、変数の行の細部（Python の図の _subscriptions・_timers・_services・_clients など）
-->

# 参考資料: Node クラスの構造、Python 版と C++ 版のクラス図（聞くための原稿）

フェーズ3 から後、ノードを書くたびに、Node クラスを継承し、create_publisher や declare_parameter を呼んできました。この資料では、その Node クラスの中身をクラス図にして、Python 版の rclpy.node.Node と、C++ 版の rclcpp::Node の、作りの違いを読み解きます。

対象は、ROS2 Jazzy の rclpy の 7.1.12 と、rclcpp の 28.1.22 です。版は、この資料を作ったときに /opt/ros/jazzy に入っていたものです。前提は、フェーズ3-1、つまりトピックの手順書を読み終えていることです。フェーズ3-3 から3-5 と、間章の内容にも触れますが、読んでいなくても、図と表は読めます。所要の目安は、0.5 から1コマで、読み物です。

原文には、囲みが2つあります。

1つ目は、この資料の位置づけです。手順書、つまりフェーズの流れからは独立した参考資料で、必要になったときに読めばよい、とあります。手を動かす作業はありません。Node を継承すると何が手に入るのか、なぜ C++ では pub_ などをメンバに保持しないといけないのか、といった疑問に、ソースコードの構造から答えることが目的です。

2つ目は、出どころです。クラスの構造、変数名、メソッド名は、/opt/ros/jazzy にあるソース、つまり rclpy の node.py や、rclcpp の node.hpp ほかを読んで確かめた、とあります。文章は自分の言葉で書いていて、ソースの転載ではありません。図は、主要な部分だけを抜き出して描いたもので、すべてのメソッドを載せてはいません。図の SVG は生成のスクリプトで作り、文字と線の重なりは計算で点検しましたが、画像にして目で確かめてはいない、とあります。表示が崩れている場合は、図の下にある、同じ内容の mermaid の版を参照します。

## 0. この資料で分かること

分かることは3つです。

1つ目。Python 版と C++ 版の Node が、それぞれどんな変数を持ち、どんな周辺のクラスとつながっているか。

2つ目。教材で使ったメソッドが、Node の機能全体の中で、どこに当たるか。

3つ目。Python 版は、1つのクラスに機能を集める作りで、C++ 版は、機能ごとの部品を組み合わせる作りであること。そして、その違いが、書き方の違いとして表に出ていること。例えば、C++ では、作ったものを保持し続ける必要があります。

## 1. 全体像、どちらにも共通する形

Python 版と C++ 版のどちらでも、ノードの形は、次の4つの関係でできています。

1つ目。自作のノードは、Node を継承します。Talker や Listener は Node の子クラスで、Node が持つメソッドを、そのまま使えます。

2つ目。Node は、通信の口を作ります。create_publisher、create_subscription、create_timer、create_service、create_client を呼ぶと、それぞれ Publisher、Subscription、Timer、Service、Client のオブジェクトが作られて、返ってきます。

3つ目。Node は、Context に属します。rclpy の init や、rclcpp の init で作られる Context は、そのプロセスでの ROS2 の通信の土台で、ノードは必ず、どれか1つの Context に属します。

4つ目。Executor が、ノードを回します。spin の中身は Executor で、登録されたノードの、タイマーの満了やメッセージの到着を待ち、対応するコールバックを呼びます。フェーズ3-1 の1節の図の内容です。

違いは、Node の中身の作り方にあります。ここから、Python 版を2節で、C++ 版を3節で見て、4節で比べます。

## 2. Python 版、rclpy.node.Node

最初の図は、Python 版の Node クラスと、周辺のクラスのクラス図です。箱が全部で15個あり、どの箱も、上の段にクラスの名前、下の段に中身が書かれています。

真ん中の大きな箱が、rclpy.node.Node です。中は3段に分かれていて、名前の下の段に変数が6行、その下の段に、メソッドが11行並びます。変数とメソッドは、2-1節と2-2節で読みます。

Node の箱の上には、自作のノード、Talker や Listener などの箱があります。中身は、__init__ で通信の口を作ることと、on_timer などのコールバックの2行です。この箱から、Node に向かって、白い三角の矢印、つまり継承の線が下りています。

左の列には、上から順に4つの箱があります。1つ目は Context で、rclpy の init で作られる、とあります。Node から Context へは、点線の矢印で、所属、と書かれています。2つ目は、C 拡張の _rclpy.Node で、rcl、つまり C 言語の層のノード、とあります。Node の側に黒いひし形の付いた実線で、中身、と書かれています。3つ目は Executor で、add_node と、spin と spin_once のメソッドがあります。Executor から Node へは点線の矢印で、登録して回す、とあります。4つ目は、SingleThreadedExecutor と、MultiThreadedExecutor、こちらにはフェーズ3-5 と添えてあります。この箱から Executor へ、継承の線が上がっています。

右の列には、上から順に5つの箱があります。Publisher には publish、Subscription にはコールバックを持つ、Timer には cancel、Service にはコールバックを持つ、Client には call_async と書かれています。5つとも、Node の側にひし形の付いた実線でつながり、作って list で保持、と書かれています。

下の列には、左から4つの箱があります。CallbackGroup には、既定は MutuallyExclusive、とあります。ActionServer と ActionClient の箱には、rclpy.action で、Waitable の一種、とあります。ParameterService には、ros2 param の要求に答える、ROSClock には、get_clock が返す時計、とあります。このうち、CallbackGroup、ParameterService、ROSClock の3つは、Node の側にひし形の付いた実線でつながっています。ActionServer と ActionClient の箱だけは、箱の側から Node へ点線の矢印が上がり、add_waitable で登録、と書かれています。

図のいちばん下には、線の凡例があります。白い三角の矢印は継承で、矢印の先が親クラスです。黒いひし形の付いた実線は保持で、ひし形の側が持ち主です。点線の矢印は、使う、登録する、作って返す、です。

### 2-1. 変数の読み方

__init__ の中で作られる、主な変数を、図の上の段に載せた、とあります。名前の先頭のアンダースコア1つは、クラスの内部用、2つは、さらに外から触りにくくした内部用、という Python の慣習です。

表は3列で、変数、中身、意味です。5行あります。

1行目は _context です。中身は Context です。このノードが属する、通信の土台です。引数で渡さなければ、rclpy の init が作った、既定の Context が入ります。

2行目は、アンダースコアが2つの __node です。中身は _rclpy.Node です。これが、ノードの本体です。C 言語で書かれた拡張モジュール、_rclpy のオブジェクトで、その先は、ROS2 の共通の C 言語の層、rcl につながります。Python の Node は、この本体を包む、使いやすい外側です。

3行目は、_publishers などのリストです。中身は、Publisher などのリストです。create_ で始まるメソッドで作ったものを、ノード自身が覚えておくリストです。

4行目は _parameters です。中身は辞書です。宣言したパラメータの、名前と値です。

5行目は _default_callback_group です。中身は MutuallyExclusiveCallbackGroup です。コールバックグループを指定しなかったときに使われるグループで、同じグループのコールバックは同時に動かさない、という種類です。既定のままなら、1つのノードの、タイマーや受信のコールバックは、1つずつ順に処理されます。これが、複数のコールバックが同じ変数を触っても食い違わない理由の一部です。例は、フェーズ3-4 の counter_node です。

このほか、__init__ では、ParameterService、つまり ros2 param の要求に答えるサービスの群れと、ROSClock、つまり get_clock が返す時計と、TimeSource、つまり use_sim_time を扱うものなども、作られます。自作のノードに ros2 param list を実行すると、フェーズ3-3 の5-3節のとおり、自分で宣言していない use_sim_time や start_type_description_service も並びます。これは、Node の __init__ が、これらを自動で用意しているからです。

### 2-2. メソッドの分類

公開されているメソッドは、プロパティを含めて、70余りあります。分類すると、次の表のようになります。表は3列で、分類、代表的なメソッド、教材で使ったもの、です。6行あります。

1行目は、通信の口を作る、です。代表的なメソッドは、create_publisher、create_subscription、create_timer、create_service、create_client、create_rate、create_guard_condition です。教材で使ったのは、最初の5つで、フェーズ3-1 から3-4 です。

2行目は、通信の口を壊す、です。代表的なメソッドは、destroy_publisher、destroy_subscription、destroy_timer などと、destroy_node です。教材で使ったのは destroy_node で、全部のフェーズの main の finally です。

3行目は、パラメータです。代表的なメソッドは、declare_parameter と declare_parameters、get_parameter と get_parameters、set_parameters、has_parameter、describe_parameter、add_on_set_parameters_callback、add_pre_set_parameters_callback、add_post_set_parameters_callback などです。教材で使ったのは、declare_parameter、get_parameter、add_on_set_parameters_callback で、フェーズ3-2b と3-3 です。

4行目は、ノードの情報と道具です。代表的なメソッドは、get_name、get_namespace、get_logger、get_clock、get_fully_qualified_name です。教材で使ったのは、get_logger で、フェーズ3-1 から後、と、get_clock で、フェーズ3-1 の sine_pub です。

5行目は、グラフ、つまりネットワーク全体の問い合わせです。代表的なメソッドは、get_node_names、get_topic_names_and_types、count_publishers、count_subscribers、wait_for_node などです。教材では使っていません。ros2 node list や ros2 topic list の CLI が、同じ情報を、別の経路で調べています。

6行目は、実行の仕組みとの接続です。代表的なものは、executor というプロパティと、add_waitable と、default_callback_group です。教材では、間接的に使いました。rclpy の spin に node を渡すと、その中で、executor がノードを登録します。アクションは add_waitable を使います。

### 2-3. 周辺のクラスとの関係

まず、図の右の、Publisher、Subscription、Timer、Service、Client です。create_ で始まるメソッドが作って返すと同時に、ノード自身のリスト、_publishers などにも入れます。図のひし形は、ノードが持ち主として保持していることを表します。

次に、図の左の Executor です。rclpy の spin に node を渡すと、内部で、Executor に、指定しなければ既定の Executor に、add_node でノードを登録し、spin を回します。フェーズ3-5 で使った MultiThreadedExecutor は、Executor の子クラスの1つです。

次に、図の下の ActionServer と ActionClient です。Node には、create_action_server のようなメソッドはありません。アクションは、rclpy.action という別のモジュールのクラスで、作られるときに、node の add_waitable に self を渡して、ノードに自分を登録します。Waitable は、executor が待つことのできるもの、を表す基底クラスです。フェーズ3-5 で、ActionServer に、self、Fibonacci、fibonacci という名前の順に渡し、最初の引数にノード自身を渡していたのは、このためです。

最後に、図の左下の CallbackGroup です。既定のグループを1つ持ちます。フェーズ3-5 の ReentrantCallbackGroup は、既定の代わりに指定した、別のグループです。

### 2-4. 作りの特徴

Python 版の Node は、機能を1つのクラスに集めた作りです。rclpy の node.py というファイルは2,300行ほどあり、パラメータの検証から、グラフの問い合わせまでが、1つのクラスに並んでいます。重い処理、例えば実際の通信や名前の解決は、C 拡張の __node に任せています。

学習する側にとって大事な帰結は、create_ で始まるメソッドで作ったものを、ノードが、自分のリストで持ち続けることです。フェーズ3-1 の talker.py の解説で、self.pub や self.timer に代入して保持しているのは、後から使うため、と書き、括弧で、Python ではノードが内部でも保持するので、保持しなくても動くことが多い、と書いたのは、この _publishers や _timers などのリストがあるからです。C++ 版では、ここが違います。3-3節で見ます。

## 3. C++ 版、rclcpp::Node

2つ目の図は、C++ 版の Node クラスと、周辺のクラスのクラス図です。箱が全部で14個あり、どの箱も、上の段にクラスの名前、下の段に中身が書かれています。

真ん中の大きな箱が、rclcpp::Node です。中は3段で、名前の下の段に、変数が3行あります。1行目は、node_base_、node_topics_、node_timers_ など、2行目は、それが11個で、node_interfaces の何々 Interface の SharedPtr であること、3行目は、node_options_ で、型は NodeOptions です。その下の段に、メソッドが11行並びます。コンストラクタの、名前と NodeOptions を取る Node から始まり、山括弧で型を付けた create_publisher、create_subscription、それから create_wall_timer、山括弧で型を付けた create_service と create_client と declare_parameter、get_parameter、add_on_set_parameters_callback、get_logger と get_clock と now、そして最後が、get_node_base_interface などで、部品を返すもの、とあります。

Node の箱の上には、自作のノード、Talker や Listener などの箱があります。中身は2行で、コンストラクタの Talker と、NodeOptions を取る Talker、こちらには間章と添えてあります。もう1行は、pub_、timer_、sub_ で、型は SharedPtr です。この箱から Node へ、継承の線が下りています。Node の箱の右上、自作のノードの箱の右には、std::enable_shared_from_this の箱があり、山括弧の中は Node です。中身は、自分を指す SharedPtr を作れる、とあります。Node の箱の上の辺から、この箱へも、継承の線が上がっています。

Node の右には、node_interfaces、つまり部品の箱があり、11個の部品の名前が縦に並びます。名前は3-1節の表で読みます。Node の側にひし形の付いた実線でつながり、11個を保持、処理を任せる、と書かれています。

左の列には、上から順に4つの箱があります。1つ目は NodeOptions で、remap、パラメータ、プロセス内通信などの設定、とあります。NodeOptions から Node へ点線の矢印で、渡す、と書かれています。2つ目は Context で、rclcpp の init で作られる、とあります。Node から Context へ点線の矢印で、所属、とあります。3つ目は Executor で、ノードの部品を受け取る add_node と、spin と spin_once があります。Executor から Node へ点線の矢印で、登録して回す、とあります。4つ目は、SingleThreadedExecutor と MultiThreadedExecutor の箱で、Executor へ継承の線が上がっています。

Node の下には、5つの箱が横に並びます。左から、山括弧で型を付けた Subscription、WallTimer、山括弧で型を付けた Service と Client で、この4つの中身はコールバックです。いちばん右は、山括弧で型を付けた Publisher で、publish があります。Node の箱の下から点線が下り、横に分かれて、5つの箱へ矢印が下ります。線には、作って SharedPtr で返す、括弧で、持ち続けるのは呼び出し側、と書かれています。

左下には CallbackGroup の箱があり、WeakPtr のリストで覚える、とあります。この箱から、点線の矢印が右へ伸び、上に折れて、Subscription の箱に届きます。線には、弱い参照、つまり WeakPtr で覚える、括弧で、Subscription、Timer、Service、Client、と書かれています。

図のいちばん下の凡例は、最初の図と同じ3種類の線です。

### 3-1. 11個の部品、node_interfaces

C++ 版の Node が持つ変数、つまり private の部分は、ほとんどが、部品へのポインタです。rclcpp::Node は、ノードの機能を、11個の部品、つまり node_interfaces という名前空間のクラスに分けて持ち、create_publisher などを呼ばれると、担当の部品に処理を任せます。

表は3列で、部品、担当すること、対応する Node のメソッドの例、です。11行あります。

1行目は NodeBaseInterface です。担当は、ノードの名前、名前空間、所属する Context、コールバックグループです。メソッドの例は get_name です。Executor の add_node は、この部品を受け取ります。

2行目は NodeTopicsInterface です。担当は、Publisher と Subscription の登録です。例は、create_publisher と create_subscription です。

3行目は NodeTimersInterface です。担当は、タイマーの登録です。例は、create_wall_timer と create_timer です。

4行目は NodeServicesInterface です。担当は、サービスとクライアントの登録です。例は、create_service と create_client です。

5行目は NodeParametersInterface です。担当は、パラメータの宣言、取得、変更の検証です。例は、declare_parameter、get_parameter、add_on_set_parameters_callback です。

6行目は NodeClockInterface です。担当は時計で、例は get_clock と now です。

7行目は NodeLoggingInterface です。担当はロガーで、例は get_logger です。

8行目は NodeGraphInterface です。担当は、他のノードやトピックの一覧、つまりグラフの問い合わせです。例は、get_topic_names_and_types と count_publishers です。

9行目は NodeTimeSourceInterface です。担当は、use_sim_time のときの時刻の元です。メソッドは、直接は呼びません。

10行目は NodeWaitablesInterface です。担当は、Waitable、つまりアクションなどの登録です。rclcpp_action の create_server が使います。

11行目は NodeTypeDescriptionsInterface です。担当は、メッセージの型の説明を返すサービスで、Jazzy で入った機能です。直接は呼びません。ros2 param list に出る start_type_description_service が、この機能を有効にするか無効にするかを決めます。

get_node_base_interface のように、部品そのものを取り出すメソッドも、公開されています。自作のコードで使うことはまれですが、ROS2 の側では多用されます。例えば、フェーズ3-5 の、rclcpp_action の create_server に this を渡す呼び出しは、中で、ノードから、get_node_base_interface、get_node_clock_interface、get_node_logging_interface、get_node_waitables_interface の4つを取り出して、アクションのサーバを組み立てています。Python 版で add_waitable を呼んでいたことに当たる処理が、C++ では、必要な部品だけを取り出して渡す形になっています。

### 3-2. テンプレートのメソッド

山括弧で std_msgs の msg の String を付けて、chatter と 10 を渡す create_publisher のように、メッセージの型を山括弧で渡すメソッドは、C++ のテンプレートです。Python 版では、create_publisher に、String、chatter、10 と渡し、型を普通の引数にしていました。テンプレートにすることで、コンパイルの時点で型が決まり、publish に違う型のメッセージを渡すと、コンパイルのエラーになります。フェーズ3-1 の7節の、実行時エラーの出方、の内容です。山括弧で std::string を付けた declare_parameter も同じで、宣言と同時に、型の決まった値を返します。

### 3-3. SharedPtr で返し、呼び出し側が持ち続ける

C++ 版の、create_ で始まるメソッドは、作ったものを SharedPtr で返します。SharedPtr は、参照の数を数えるポインタで、最後の1つが消えると、中身も消えます。ここが、Python 版と大きく違います。

Node は、作った Subscription や Timer などを、自分では持ち続けません。登録先のコールバックグループ、つまり CallbackGroup は、それらを WeakPtr のリストで覚えるだけです。WeakPtr は弱い参照で、数に数えないので、中身を生かしておく力がありません。

そのため、呼び出し側が、戻り値の SharedPtr を捨てると、参照の数が0になって、Subscription やタイマーは消え、コールバックは二度と呼ばれません。エラーも出ません。

フェーズ3-1 の C++ の版で、pub_、timer_、sub_ を必ずメンバ変数に保持していたのは、このためです。フェーズ3-3 の add_on_set_parameters_callback の戻り値、つまり OnSetParametersCallbackHandle の SharedPtr を保持しないと、コールバックの登録が外れます。これも同じ仕組みによるもので、フェーズ3-3 の7節の比較表と、8節のつまずきの表の内容です。

### 3-4. NodeOptions と enable_shared_from_this

NodeOptions は、コンストラクタの2つ目の引数で、remap、パラメータの上書き、プロセス内通信を使うか、など、ノードを作るときの設定をまとめたものです。フェーズ3 では省略していて、既定値が使われます。間章のコンポーネントでは、コンテナが NodeOptions に設定を詰めて渡してくるので、それを Node へ渡すコンストラクタにしました。

std::enable_shared_from_this は、山括弧の中が Node で、Node の親クラスの1つです。ノードが、自分自身を指す SharedPtr を作れるようにする、C++ の標準の仕組みです。C++ のノードを、std::make_shared で Talker を作ってから、rclcpp の spin に渡していたのは、ノードが SharedPtr で管理されることを前提にした作りだからです。

## 4. 比較

比べた表は3列で、観点、Python の rclpy.node.Node、C++ の rclcpp::Node、です。7行あります。

1行目は、クラスの作りです。Python は、1つのクラスに機能を集め、重い処理は C 拡張の __node に任せます。C++ は、11個の部品、node_interfaces を組み合わせ、処理を任せます。

2行目は、親クラスです。Python は、親クラスは無く、Python の object だけです。C++ は、std::enable_shared_from_this で、山括弧の中は Node です。

3行目は、作った通信の口の保持です。Python は、ノードが自分のリストで持ち続け、保持しなくても動きます。C++ は、呼び出し側が SharedPtr で持ち続ける必要があり、持たないと消えます。

4行目は、メッセージの型の渡し方です。Python は、普通の引数で、create_publisher の最初に String を渡します。C++ は、テンプレートの引数で、create_publisher に山括弧で String を付けます。

5行目は、アクションとのつながりです。Python は、ActionServer が、node の add_waitable で自分を登録します。C++ は、create_server が、ノードから部品を取り出して組み立てます。

6行目は、作るときの設定です。Python は、キーワード引数で、namespace や parameter_overrides などです。C++ は、NodeOptions にまとめて渡します。

7行目は、公開メソッドの数、つまり名前の数です。Python は70余りです。C++ は60余りで、ほかに部品のメソッドがあります。

どちらも、ROS2 の共通の C 言語の層、rcl の上に作られた外側である点は、同じです。だからこそ、Python のノードと C++ のノードが、同じトピックで話せます。フェーズ3-1 の6節の内容です。違うのは、その外側を、それぞれの言語で扱いやすい形に整える方法です。Python は、1つのクラスで何でもできる手軽さを選んでいます。C++ は、部品に分けて、必要な部品だけを、他の仕組み、つまり executor、アクション、コンポーネントのコンテナに渡せる柔軟さと、型の安全さを選んでいます。

## 5. 教材のどこで何を使ったか

表は4列で、使ったもの、Python、C++、手順書、です。12行あります。

1行目は、Node の継承です。Python は、class Talker の括弧に Node。C++ は、class Talker に、コロンの public で rclcpp::Node。手順書は3-1 から後です。

2行目は、Publisher と Subscription です。Python は、create_publisher と create_subscription。C++ は同じ名前で、テンプレートです。手順書は、3-1、3-2a、3-2b です。

3行目は、タイマーです。Python は create_timer、C++ は create_wall_timer です。手順書は3-1 から後です。

4行目は、時計です。Python は、get_clock の now。C++ は now です。手順書は3-1 の sine_pub です。

5行目は、ログです。Python は、get_logger の info。C++ は、RCLCPP_INFO に get_logger を渡します。手順書は3-1 から後です。

6行目は、パラメータです。Python は、declare_parameter と get_parameter。C++ は、山括弧で型を付けた declare_parameter です。手順書は3-2b と3-3 です。

7行目は、パラメータの変更の検証です。Python は add_on_set_parameters_callback。C++ は同じ名前で、戻り値を保持します。手順書は3-3 です。

8行目は、サービスです。Python は、create_service と create_client。C++ は同じ名前で、テンプレートです。手順書は3-4 です。

9行目は、アクションです。Python は、self を渡す ActionServer と ActionClient。C++ は、this を渡す rclcpp_action の create_server などです。手順書は3-5 です。

10行目は、実行の仕組みです。Python は、rclpy の spin、MultiThreadedExecutor、ReentrantCallbackGroup。C++ は、rclcpp の spin です。手順書は3-1 と3-5 です。

11行目は、作るときの設定です。Python では使っていません。C++ は NodeOptions です。手順書は間章です。

12行目は、後片付けです。Python は destroy_node。C++ は、SharedPtr が消えるときに自動です。手順書は3-1 から後です。

教材で使ったのは、Node の機能のうち、通信の口を作る、パラメータ、ログと時計、の3つの分類がほとんどです。グラフの問い合わせ、つまり2-2節の表にある分類や、個別の destroy_ で始まるメソッド、create_rate などは使っていません。必要になったら、6節の公式の API リファレンスで、2-2節の表の分類を手がかりに探すとよい、とあります。

## 6. 公式ドキュメントと参考資料

確認の状況が書かれています。2026年9月24日の時点で、下の資料は、Web 検索の結果で実在を確かめました。docs.ros.org は、本文の取得がボット対策で拒否されるため、内容の照合はできていません。ページに表示される版の番号、例えば rclpy の 3.2.1 などは、この資料で読んだ手元のパッケージの版、つまり冒頭の対象に書いた版とは一致しません。構造は、手元のソースを正とした、とあります。

資料は4つです。

1つ目は、Node、rclpy の Jazzy で、Python 版の Node の API リファレンスです。

2つ目は、Execution and Callbacks、rclpy の Jazzy で、Executor とコールバックグループです。

3つ目は、Class Node、rclcpp の Jazzy で、C++ 版の Node の API リファレンスです。

4つ目は、File node.hpp、rclcpp の Jazzy で、C++ 版の Node の宣言があるヘッダです。

## 出典について

この原稿は、SanghunIm1991 さんの [ros2MinimalPhysicalAi の「参考資料: Nodeクラスの構造（Python版とC++版のクラス図）」](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/docs/reference_node_class.md)を、聞くために要約・意訳したものです。図の [reference_node_rclpy.svg](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/docs/img/reference_node_rclpy.svg) と [reference_node_rclcpp.svg](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/docs/img/reference_node_rclcpp.svg) は、言葉で説明しました。元にしたのは、[2026年10月14日の版](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/86dc0ed3d606c4a05d1e087421bb10318a37e521/docs/reference_node_class.md)です。原文の文章と図と同じく、[クリエイティブ・コモンズ 表示 4.0 国際ライセンス](https://creativecommons.org/licenses/by/4.0/deed.ja)で提供します。

原稿の中に原文の表記のまま書いた、クラス・変数・メソッドの名前と、短い呼び出しの例は、原文では [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0) の対象です。ライセンスの全文は、原文のリポジトリの [LICENSE-APACHE-2.0](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/LICENSE-APACHE-2.0) にあります。原文には、サンプルコードも実行の手順もありません。

原文のクラスの構造と名前は、筆者が ROS2 Jazzy の rclpy と rclcpp のソースを読んで確かめたもので、原文では、文章は自分の言葉で書いており、ソースの転載ではない、としています。この原稿も、ソースのコードは写していません。
