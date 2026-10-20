<!--
聞くための原稿（読み上げでは読まれない記録）
原文: SanghunIm1991/ros2MinimalPhysicalAi の main ブランチの docs/phase3_3_parameters.md（図は docs/img/phase3_3_sources.svg と docs/img/phase3_3_validate.svg）
原文のコミット: 86dc0ed3d606c4a05d1e087421bb10318a37e521（2026-10-14）
作成: 2026-10-20、Claude Code が手作業で作成（原稿化スキルはまだない）
原文のライセンス: 文章と図は CC BY 4.0、コードとコマンドは Apache-2.0（LICENSE の1と2）。原文の末尾に、API の使い方は公式チュートリアル（ROS 2 Documentation、CC BY 4.0）を参考にし、コードと文章は独自に書いた、とある。この原稿は、原文を聞くために要約・意訳したもの（改変あり）
方針: 英語の略語や製品名、関数やクラスの名前、短いコマンドは原文の表記のまま書く。サンプルコード2本と、YAML のファイル、setup.py・CMakeLists.txt に足す行は、写さずに、ブロックの役割と要の行を言葉で説明した。期待する結果（ログ、ros2 param の表示、rclpy と rclcpp のエラーの文面）も写さず、何が表示されるかを言葉で説明した。図と表（仕様、主な API、値の流れ、フェーズ5 のパラメータ、Python版と C++版の違い、つまずきやすい点）は言葉で説明する。文字数の上限は設けない
省いたもの: URL、日本語の記事の題名（記事が1本あることだけ触れた）、型の定義へのリンク、ログの時刻の数字
-->

# フェーズ3-3: パラメータの宣言、実行中の変更、YAML での指定（聞くための原稿）

これは、ros2MinimalPhysicalAi という教材の、フェーズ3-3 の手順書の話です。ノードの設定の値を、コードに埋め込まず、外から与える方法を学びます。Python の版は必須、C++ の版は任意です。

このフェーズは、フェーズ5 の PI 制御のノードで、ゲイン、つまり Kp と Ki を外から調整する土台になります。PI 制御は、目標と今の値の差から、指令を自動で決める方法で、ゲインは、その差や、差を積み上げた値に掛ける係数です。詳しくはフェーズ5-2 で扱います。

想定する環境は、WSL2 と Ubuntu 24.04 と ROS2 Jazzy です。前提は、フェーズ3-1、3-2a、3-2b を終えていることです。所要時間の目安は1コマです。

原文には、位置づけの囲みがあります。パラメータは、フェーズ5 の PI 制御のノードで、ゲインを外から与え、実行中に調整するのに、そのまま使います。だから、Python の版は必須として、手を動かして身に付けます。C++ の版の4節は任意です。

進め方は、これまでと同じです。2節の仕様は何を作るかの定義で、主な API の表、サンプルコードと解説を読んで理解し、既定の値や型を変えたり、パラメータを増やしたりして改造すると身に付きます。サンプルは、手順書を作るときにビルドを確かめ、手順は2026年9月26日に実機で確かめています。

期待する結果は、コードと ROS2 の仕様から筆者が想定したもので、エラーの文言は、手元の rclpy と rclcpp のソースから取っています。実機で実行して確かめてあります。5-3節の ros2 param の表示と、5-4節の dump と load の表示は、どちらも Python の版で、実機の表示に合わせて直したものです。dump の値は、実行した時点の設定によって変わります。

この原稿では、サンプルコードを書き写さず、役割と要の行を言葉で説明します。ツールの表示やエラーの文面も、何が表示されるかを言葉で説明します。

## 0. 学習目標と完了の条件

完了の条件は4つです。

1つ目。declare_parameter でパラメータを宣言し、値を取得できる。Python で、C++ の版は任意です。

2つ目。3通りの与え方を使い分けられる。コードの既定の値、起動のときの -p か YAML、そして実行中の ros2 param set、の3つです。

3つ目。実行中の変更に反応する、つまり変更を検証して受け入れたり拒否したりする、コールバックを書ける。

4つ目。YAML のファイルの書式の ros__parameters と、型の厳しさ、つまり1 と1.0 は別のものだ、ということを説明できる。

## 1. 全体像

原文の図は2つで、どちらも SVG と mermaid の版があります。

1つ目の図は、パラメータの値がノードに入る3つの道です。左に3つの箱が縦に並びます。上から、「コードの既定値、declare_parameter」、「起動時、-p と --params-file」、「実行中、ros2 param set」です。3つの箱から、それぞれ矢印が、真ん中の大きめの箱「ノード、param_talker」に集まります。そして、ノードの箱から右へ矢印が出て、灰色の箱「トピック、/param_chatter」に向かいます。図の --params-file は、パラメータの値を YAML のファイルにまとめて渡す、起動のときの指定で、5-4節で使います。

値が決まる優先の順は、後のものが勝ちます。コードの既定の値より、起動のときの -p や YAML の指定が勝ち、それより、実行中の ros2 param set が勝ちます。

2つ目の図は、実行中の変更の流れを表すシーケンス図です。上に、左から、ros2 param set、ノード、on_set_parameters のコールバック、の3つの箱が並びます。まず、ros2 param set からノードへ、「period を0.5 に」という矢印があります。次に、ノードからコールバックへ、「変更案を渡す」という矢印があります。その下に、alt の枠があり、点線で上下2つに分かれています。

上の段は、「妥当、つまり period が0 より大きい」場合です。コールバックからノードへ、点線で「successful イコール True」が返り、ノードが自分自身へ戻る矢印で「値を反映、タイマーを作り直す」をし、ノードから ros2 param set へ、点線で「Set parameter successful」が返ります。

下の段は、「不正、つまり period が0 以下」の場合です。コールバックからノードへ、点線で「successful イコール False と reason」が返り、ノードから ros2 param set へ、点線で「Setting parameter failed と reason」が返ります。

原文の注記によると、この図は流れの説明のためのもので、サンプルコードでの検証と反映の書き方と、その注意点は、3節の解説で扱います。

## 2. 仕様

仕様は、項目と内容の2列の表で、6行あります。

ノードの名前と実行ファイルの名前は、param_talker で、Python の版と C++ の版で同じ。

役割は Publisher。

トピックは param_chatter で、型は std_msgs/msg/String。

パラメータは2つ。message は文字列で、既定は hello。period は実数で、既定は1.0秒。

動作は、period 秒ごとに、message の内容を送り、ログにも出す。

実行中の変更は、message は次に送るときから反映する。period は、タイマーを作り直して反映する。period が0 以下の値は拒否し、変更する前の値のままにする。

## 3. Python の版、learn_py

learn_py の内側の learn_py のフォルダに、param_talker.py を作ります。

主な API は、やりたいことと API の2列の表で、4行あります。

宣言は、self.declare_parameter に名前と既定の値を渡す。既定の値の型が、そのパラメータの型になります。

取得は、self.get_parameter に名前を渡して、value を読む。

変更の検証と反映は、self.add_on_set_parameters_callback にコールバックを渡す。コールバックの戻り値は、rcl_interfaces.msg の SetParametersResult。

タイマーの作り直しは、self.timer の cancel() を呼んでから、self.create_timer を呼ぶ。

SetParametersResult が属する rcl_interfaces は、rclpy が依存しているパッケージなので、package.xml に依存を足さなくても import できます。明示したい場合は、rcl_interfaces の depend の行を足します。

### サンプルコード、param_talker.py

param_talker.py は、60行ほどのコードです。ブロックは、クラスの __init__、送る処理の on_timer、変更を検証して反映する on_params、そして main です。要の行は3つです。__init__ で、declare_parameter に message と既定の 'hello'、period と既定の1.0 を渡す行。__init__ の最後で、add_on_set_parameters_callback に on_params を渡す行。そして on_params が返す、SetParametersResult の行です。on_params は、2回のループで、まず検証し、問題がなければ反映します。

原文の解説の要点です。

役割と流れ。フェーズ3-1 の talker に、message と period の2つのパラメータを足したものです。起動のときに値を決め、実行中に ros2 param set で変わったら、その都度、コールバックが検証して反映します。

宣言と取得。declare_parameter は、この名前のパラメータを持つ、と登録して、既定の値を与えます。宣言しないと、-p や ros2 param set で渡しても受け付けられません。既定の設定では、宣言していないパラメータは設定できないからです。パラメータの型は、既定の値の型で決まります。'hello' なら文字列、1.0 なら実数の double です。そのため、例えば起動のときに、period を、小数点の無い2 で渡すと、2 は整数として扱われ、型が合わずにエラーになります。5-2節の課題1 で確かめます。get_parameter の value で、今の値を取り出します。宣言の時点で、起動のときの指定があれば、既定の値ではなく、そちらの値が入っています。この、上書きされた値を取り出すのが、この2行の目的です。

タイマーとコールバックの登録。取得した self.period を使ってタイマーを作り、最後に add_on_set_parameters_callback で、パラメータを変える要求が来たら on_params を呼んでほしい、と登録します。登録をタイマーなどを作った後にしてあるのは、コールバックの中で self.timer を使うからです。

on_timer は、self.message を送るだけです。パラメータを毎回 get_parameter で読み直す書き方もありますが、ここでは属性に保存しておき、変更のコールバックで更新する方式にしています。

on_params について。引数の params は、今回の要求で変えられようとしている Parameter のリストで、name と value で中身を見ます。複数のパラメータが、1回の要求でまとめて来ることがあるので、リストを2回ループします。1回目のループは検証だけで、period が0 以下なら、successful を False にし、reason を付けて返して、拒否します。拒否すると値は変わらず、ros2 param set の側に、reason の文字列が表示されます。2回目のループで反映します。message は属性を更新するだけです。period は、今のタイマーを cancel してから、新しい周期で create_timer し直します。タイマーは、作るときに周期の値を写し取って持つので、self.period を書き換えるだけでは周期が変わらないからです。最後に successful を True にして返し、受け入れます。

なぜ2回に分けるか。1つのループで検証と反映を同時にやると、先頭の message は反映したが、後ろの period が不正で拒否した、という中途半端な状態になり、拒否したのに一部が変わってしまうからです。

落とし穴は3つです。1つ目。コールバックが返す値は、必ず SetParametersResult です。True などを返すとエラーになります。2つ目。value が0.0 以下かの比較は、period が実数として宣言されているから成り立ちます。整数が渡された場合は、そもそもコールバックより前に、型の不一致で失敗します。3つ目。このサンプルは、簡単にするため、検証するコールバックの中で、反映、つまり属性の書き換えまで行っています。そのため、同じ要求の中の別のパラメータが、後から別の検証で拒否された場合には、属性とノードのパラメータが食い違うおそれがあります。Jazzy には、検証を通った後に反映するための add_post_set_parameters_callback があるので、発展の課題として調べるとよい、とあります。この手順書では扱いません。

観察のポイント。起動して、ros2 topic echo /param_chatter を見ながら、ros2 param set で /param_talker の period を0.2 にすると、間隔が5倍速くなること。0.0 にすると拒否されて、間隔が変わらないこと。message を変えると、次に送るときから内容が変わることです。

#### 補足: 値はコピーされるのか、参照されるのか

同じパラメータの変更でも、message は属性を書き換えるだけで反映されるのに、period はタイマーを作り直さないと反映されません。この違いは、それぞれの値が、どこに保存され、いつ読まれるかで説明できます。

原文は、値の流れ、保存のされ方、読まれるとき、パラメータの変更の反映、の4列の表で、3行に整理しています。

1行目は、パラメータから、self.message と self.period への流れです。ノードが持つパラメータとは別に、属性として保存します。読まれるのは、__init__ と on_params で代入したときです。パラメータを変えても自動では変わらず、on_params で代入し直します。

2行目は、self.message から、送るメッセージへの流れです。属性のままで、on_timer が呼ばれるたびに、その時点の self.message を読みます。属性を書き換えれば、次に送るときから変わります。

3行目は、self.period から、タイマーの周期への流れです。create_timer が呼ばれた時点で、タイマーの内部に写し取られ、読まれるのは、タイマーを作るときの1回だけです。属性を書き換えても変わらず、タイマーを作り直します。

説明は3つです。

1つ目、パラメータと属性。ノードが管理するパラメータと、属性の self.period は、別々の場所に保存されています。ros2 param set は、ノードの側のパラメータを新しい値に差し替えるだけで、self.period には何もしません。そのため、self.period は、on_params で代入し直すまで元の値のままで、結果として、取得した時点の値のコピーを持っているのと同じように振る舞います。なお、Python の変数や属性は、値そのものではなく、オブジェクトへの名札、つまり参照です。ただ、float や str は中身を書き換えられない、immutable な型なので、同じ値を指す名札が複数あっても、どこかで値の中身が書き換わる心配はありません。

2つ目、タイマーの周期。create_timer は、受け取った秒の値を、その場でナノ秒の整数に変換し、タイマーの内部、つまり Python より下の、C 言語で書かれた rcl の層に保存します。これは、rclpy の node.py の create_timer で確かめた、とあります。タイマーは self.period を見に行かないので、後から書き換えても周期は変わりません。

3つ目、message が反映される理由。タイマーが持っているのは、周期の値と、self.on_timer というメソッドへの参照です。メソッドは呼ばれるたびに、self、つまりノードそのものから属性を読み直すので、self.message を書き換えれば、次に呼ばれたときには新しい値が使われます。

作り直さずに周期を変える方法も書かれています。Jazzy の rclpy の Timer には、周期を設定し直すプロパティ、timer_period_ns があります。rclpy の timer.py で確かめたもので、内部で rcl の周期を差し替える関数を呼んでいます。これに、self.period に 1e9 を掛けて整数にした値を入れれば、作り直さずに周期を変えられます。ただし、rcl のヘッダの説明には、差し替えは、すでに待っている wait set、つまり executor がタイマーの発火などを待つ仕組みには影響しない、とあり、新しい周期がいつから効くかは、executor の待ちの状況によります。また、C++ の rclcpp のタイマーには、同じことをする公開のメソッドが見当たりません。このサンプルでは、両方の言語で同じ書き方にするため、作り直す方式にしています。この方法は、手順書を作るときにソースを読んで確かめただけで、動かしては確かめていない、とあります。

### 登録とビルド

setup.py の entry_points に、param_talker の登録の行を1行足し、ビルドし直します。cd で ~/ros2_ws に移り、colcon build --symlink-install に --packages-select learn_py を付けてビルドし、source install/setup.bash を実行します。期待する結果は、learn_py の Finished と、1つのパッケージが終わったという Summary が出ることで、表示の形はフェーズ3-1 と同じです。source は、成功しても何も表示しません。

## 4. C++ の版、learn_cpp

このフェーズの C++ の版は、任意の発展です。フェーズ5 の車両のシミュレーションは Python で作ると決めているので、ここで作らなくても先へ進めます。Python の版との違いは、7節のまとめを読めば概要がつかめます。C++ の版を作らない場合は、CMakeLists.txt への登録も要りません。

learn_cpp の src に、param_talker.cpp を作ります。

主な API は、やりたいことと API の2列の表で、5行あります。

宣言は、declare_parameter に山括弧で double などの型を付け、名前と既定の値を渡す。値も返ります。

取得は、get_parameter に名前を渡して、as_double() や as_string() を呼ぶ。

変更の検証と反映は、add_on_set_parameters_callback。コールバックの引数は rclcpp::Parameter の std::vector で、戻り値は rcl_interfaces::msg の SetParametersResult。

ハンドルの保持。add_on_set_parameters_callback の戻り値の、OnSetParametersCallbackHandle の SharedPtr を、メンバに保存します。捨てると、コールバックが無効になります。

周期が秒の実数のタイマーは、create_wall_timer に、std::chrono::duration の double で包んだ period を渡す。

### サンプルコード、param_talker.cpp

param_talker.cpp は、80行ほどのコードです。クラスには、コンストラクタと、private の3つのメソッド、つまりタイマーを作る start_timer、送る on_timer、変更を検証して反映する on_params、そして5つのメンバ変数があります。要の行は3つです。コンストラクタで、declare_parameter に山括弧で型を付けて宣言し、返った値を message_ と period_ に入れる行。add_on_set_parameters_callback の戻り値を、param_cb_ に入れる行。そして start_timer の中で、period_ を std::chrono::duration の double で包んで create_wall_timer に渡す行です。

原文の解説の要点です。Python の版と同じ動作、同じ流れで、言語に固有の点を中心に書かれています。

宣言と取得を1行で。山括弧で型を付けた declare_parameter は、宣言と同時に、今の値を返します。起動のときに -p などで指定があれば、その値が返ります。このサンプルの Python の版では、宣言と get_parameter の value の2行に分けましたが、ここでは1行にまとまります。なお、rclpy の declare_parameter も、値の入った Parameter を返すので、declare_parameter の value と1行で書くこともできます。型は、テンプレートの引数で明示します。declare_parameter に double のように型を書くので、型の食い違いは、コンパイルのときに気づきやすい。

コンストラクタの順は、パラメータの宣言、Publisher、タイマー、コールバックの登録、です。コールバックの中で timer_ を使うので、登録は最後にしています。

start_timer について。std::chrono::duration の double は、秒の単位の実数を表す時間の型です。この時点の period_ の値から時間の値を作り、create_wall_timer は、それをナノ秒に変換して、タイマーの内部に写し取ります。rclcpp の create_timer.hpp で確かめた、とあります。そのため、C++ の版でも、period_ を書き換えるだけでは周期は変わらず、start_timer() を呼び直して作り直しています。一方、ラムダが取り込んでいるのは、ノード自身へのポインタの this なので、on_timer は呼ばれるたびに、その時点の message_ を読みます。Python の版の補足と同じ構図です。仮に、ラムダに message_ の値そのものを取り込むと、作ったときの値の写しが固定され、message を変えても反映されなくなります。start_timer は、コンストラクタと on_params の両方から呼べるよう、メソッドに切り出してあります。Python の、cancel して作り直す書き方との違いは、C++ の版では timer_ に新しい shared_ptr を代入するだけで、古いタイマーへの参照が無くなって片付けられ、止まる点です。明示的な cancel は書いていません。

add_on_set_parameters_callback の戻り値を持つこと。戻り値の、OnSetParametersCallbackHandle の SharedPtr、つまり param_cb_ を捨てると、コールバックの登録が解かれます。メンバ変数に保存しておく必要があります。Python では、戻り値を持たなくても動きます。8節の、C++ で実行中の変更に反応しない、という症状の典型の原因です。

コールバックの引数と戻り値。引数は、rclcpp::Parameter の std::vector への const の参照で、変えようとしているパラメータのリストを、コピーせずに受け取ります。戻り値は SetParametersResult で、successful と reason のフィールドを埋めて返します。Python のように、コンストラクタの引数で渡すのではなく、変数を作ってフィールドに代入します。

型ごとの取り出し。get_name() で名前、as_double() や as_string() で値を取り出します。取り出す型は、宣言した型と一致させます。合わないと例外が飛びます。Python は value が型を問わず使える分、C++ の方が型に厳しい。

2回のループにする理由は、Python の版と同じで、検証してから反映するためです。

メンバの初期化。message_ と period_ は、宣言のときに初期の値を持たず、コンストラクタの先頭で declare_parameter の戻り値を代入しています。start_timer() は period_ を使うので、代入より前に呼ばないこと。

include の追加。set_parameters_result.hpp を、rclcpp とは別に include しています。CMake の依存に rcl_interfaces を書いていないのは、rclcpp を通して使えているからで、この構成でビルドを確かめてあります。依存を明示したい場合は、package.xml と ament_target_dependencies に足します。

つまずきやすい点。ラムダで this の取り込みを書き忘れると、on_params を呼べず、ビルドが通りません。

観察のポイント。Python の版と同じ5節の実験を、ros2 run learn_cpp param_talker で繰り返し、間隔の変化や拒否のメッセージが、同じ結果になることです。

### CMakeLists.txt とビルド

CMakeLists.txt に、param_talker の add_executable と、rclcpp と std_msgs の ament_target_dependencies を足し、install(TARGETS ...) に param_talker を足して、hello から param_talker までの9つの名前を並べます。これまでの分は残します。ただし、前のフェーズで C++ の版を作らなかったノードの名前は書きません。書くと、存在しないターゲットとして、ビルドがエラーになります。

cd で ~/ros2_ws に移り、colcon build --symlink-install に --packages-select learn_cpp を付けてビルドし、source install/setup.bash を実行します。期待する結果は、learn_cpp の Finished と、1つのパッケージが終わったという Summary が出ることです。

## 5. 実験

### 5-1. コードの既定の値で動かす

T1 で ros2 run learn_py param_talker、T2 で ros2 topic echo /param_chatter を実行します。

期待する結果は、既定の値、つまり message が hello で period が1.0秒のとおりに、1秒ごとに hello が送られることです。T1 には、publish と hello のログが1秒ごとに出て、T2 には、data が hello のメッセージが、ハイフン3つの区切りを挟んで出ます。C++ の版を作った場合は、ros2 run learn_cpp param_talker でも同じように確かめます。表示は同じになります。

### 5-2. 起動のときに指定する、-p

ros2 run learn_py param_talker に、--ros-args を付け、-p で message を、引用符で囲んだ from cli に、もう1つの -p で period を0.5 にして起動します。

期待する結果は、0.5秒ごと、つまり1秒に2行、指定した from cli の文字列がログに出ることです。コードを1文字も変えていないのに、振る舞いが変わる点が大事です。

この節の末尾の課題1 のように、period を小数点の無い2 で渡すと、ノードは起動した直後に異常に終わります。Python の版では、トレースバック、つまりエラーまでの呼び出しの履歴の最後に、rclpy の InvalidParameterTypeException という例外が出ます。内容は、period に INTEGER、つまり整数の2 を設定しようとしたが、DOUBLE、つまり実数が期待されている、という英語の文です。続いて、ros2 run のプロセスが失敗で終わった、という行が出ます。C++ の版では、period の型が正しくない、double の型のパラメータに integer を設定することはできない、という趣旨の文になります。

課題1 は、period を小数点の無い2 で起動するとエラーになることを確かめることです。1 は整数、1.0 は実数として区別されます。宣言のときの既定の値の1.0 が実数なので、整数を渡すと型が合いません。エラーの文言を控えておきます。

### 5-3. 実行中に読む、変える、ros2 param

T1 で ros2 run learn_py param_talker を実行し、T2 で、上から順に7つのコマンドを実行します。

1つ目、ros2 param list /param_talker。2つ目、ros2 param describe /param_talker period。3つ目、ros2 param get /param_talker message。4つ目、ros2 param set /param_talker message を、引用符で囲んだ changed に。5つ目、ros2 param set /param_talker period 0.2。6つ目、ros2 param set /param_talker period 0.0、つまり範囲の外の値を設定してみる。7つ目、ros2 param get /param_talker period で、設定が拒否された後の値を確かめる。

期待する結果を、順に説明します。

param list では、message、period、start_type_description_service、use_sim_time の4つが並びます。自分で宣言した message と period のほかに、ノードが自動で持つパラメータも並ぶわけです。C++ の版の param_talker では、さらに、qos_overrides で始まる名前が4つ並びます。これは、パラメータの変更を知らせる内部のトピックの /parameter_events の、通信の設定、つまり QoS を、起動のときに変えられるようにするためのもので、rclcpp は自動で宣言し、rclpy は宣言しません。

param describe では、パラメータの名前が period で、型が double、そして制約、Constraints の見出しが表示され、その下は空です。double の型は、宣言のときの既定の値の1.0 から決まったものです。制約が空なのは、範囲などの制約を付けていないからです。5-4節の課題6 で、ParameterDescriptor を使って範囲を付けます。

param get の message では、文字列の値が hello だと表示されます。

param set の message と、period の0.2 では、どちらも、パラメータの設定に成功した、と表示されます。message を変えると、T1 のログが、次に送るときから publish と changed に変わります。period を0.2 にすると、ログが1秒に5行に増えます。

param set の period の0.0 では、パラメータの設定に失敗した、という文の後に、period must be > 0 と表示されます。これは、コードの reason に書いた文字列そのものです。拒否されたので、値は0.2 のままです。

最後の param get の period では、実数の値が0.2 だと表示されます。

ほかに2つの注意があります。5-1節のように、別のターミナルで ros2 topic echo /param_chatter を動かしておけば、period を変えたときに、表示される間隔も変わります。そして、ros2 param set で period を整数の2 にしても、型の不一致で失敗します。2.0 と書きます。Python の版のノードでは、パラメータの設定に失敗した、型が違う、DOUBLE を期待したが INTEGER だった、という趣旨の文が表示されます。起動のときの -p と違って、ノードは終わらずに動き続けます。

課題2 は、period を0.0 に設定して拒否されることと、その後も動作が変わらないことを確かめることです。課題3 は、拒否の理由のメッセージが、コードの reason と一致することを確かめることです。

### 5-4. YAML のファイルで指定する

ros2_ws の config のフォルダに、param_talker.yaml を作ります。ros2_ws の config は、パッケージではない普通のフォルダで、フェーズ4 で learn_bringup の config へ移します。ros2_ws は、フェーズ2 の2-8節の方法で Git の管理の下にしない限り、git status とは関係しません。2-8節の方法で練習のコードを Git で管理している場合は、git status にまだ管理していないものとして出ますが、フェーズ4 で移すまでコミットしません。

YAML のファイルの中身は4行です。1行目がノードの名前の param_talker で、その下の字下げした2行目が ros__parameters、さらにその下の3行目と4行目に、message を、引用符で囲んだ from yaml に、period を0.5 に、と書きます。

説明は2つです。1行目は、ノードの名前です。ノードの名前にかかわらず、すべてのノードに当てたい場合は、スラッシュとアスタリスク2つ、と書きます。ros__parameters は、アンダースコアが2つの、決まったキーです。

ros2 run learn_py param_talker に、--ros-args と、--params-file で、~/ros2_ws の config の param_talker.yaml を渡して起動します。

期待する結果は、YAML に書いた値で動くことです。つまり、0.5秒ごとに、publish と from yaml のログが出ます。5-2節で -p を使ったときと同じ振る舞いです。

YAML の1行目のノードの名前を間違えていると、エラーにはならずに、既定の値、つまり hello を1秒ごとに送る形で動きます。何も言われずに反映されないので、表示の文字列で確かめる習慣を付けるとよい、とあります。

実行中の設定を、YAML で書き出したり読み込んだりもできます。ros2 param dump /param_talker で書き出し、ros2 param load /param_talker に YAML のファイルのパスを付けて読み込みます。

期待する結果は、Python の版の param_talker で、ros2 param set で message を changed、period を0.2 にした後の例です。dump では、一番上に /param_talker の行、その下に ros__parameters の行、さらにその下に、message が changed、period が0.2、start_type_description_service が true、use_sim_time が false、と並びます。load では、message の設定に成功した、period の設定に成功した、の2行が表示されます。

dump の出力は、5-4節の冒頭で書いた YAML と同じ書式、つまりノードの名前、ros__parameters、値、の形になっています。C++ の版の param_talker では、5-3節で見た qos_overrides の4つが、qos_overrides の下に入れ子になって加わります。そのままファイルに保存すれば、今の設定を、次に起動するときに使えます。load の後は、T1 のログが publish と from yaml に、間隔が0.5秒に戻ります。

#### YAML でパラメータを渡す利点

ここまでで、パラメータを与える方法を3つ見ました。コードの既定の値、起動のときの -p、そして YAML のファイルです。パラメータが2つしかない param_talker では、どれを使っても手間はあまり変わりません。けれども、フェーズ5 の車両のシミュレーションのように、ゲインや目標の速度を何度も変えながら試す場面では、YAML にしておく利点がはっきりしてきます。原文は、利点を6つ挙げています。

1つ目。コードを変えずに、設定だけを変えられる。既定の値を変えたいとき、コードを書き換えると、ビルドし直しが必要になることがあり、C++ の版は必ず要ります。また、プログラムの修正と、設定の変更が、同じ差分に混ざってしまいます。YAML なら、ファイルを直してノードを起動し直すだけで済みます。コードは、どう動くか、YAML は、どの値で動かすか、と役割を分けられます。

2つ目。数が増えても、まとめて読み書きできる。-p はパラメータ1つにつき1つ書くので、数が増えるとコマンドが長くなり、打ち間違えやすい。YAML なら1か所に並べて書け、シャープの記号から行の末尾までのコメントで、単位や、なぜこの値にしたか、も残せます。

3つ目。調整した結果を保存して、再現できる。実行中に ros2 param set で値を探り、よい値が見つかったら、ros2 param dump の出力を、大なりの記号で、例えば tuned.yaml というファイルに保存します。dump は画面に YAML の形で表示するだけなので、大なりの記号でファイルへ書き出すわけです。次回は、そのファイルを --params-file で渡せば、同じ設定から始められます。フェーズ5 で PI 制御のゲインの kp と ki を調整するときの、基本の流れになります。ただし、dump の出力には、自分で書いたコメントは残りません。コメントを付けたファイルに大なりの記号で上書きすると、コメントが消えます。別の名前で書き出してから、必要な値を写すとよい、とあります。

4つ目。設定を記録して、ほかの人と共有できる。YAML はテキストのファイルなので、Git で履歴を管理できます。この教材の練習用の ros2_ws は、既定では Git の管理の外で、管理したい場合はフェーズ2 の2-8節の方法を使います。いつ、どの値を、どう変えたかが差分で追えるうえ、同じファイルを渡せば、ほかの人も同じ条件で動かせます。

5つ目。用途ごとに設定を切り替えられる。動作の確認用と、本番の実験用のように、ファイルを複数用意しておけば、起動のときに渡すファイルを変えるだけで、設定を切り替えられます。コードは1つのまま使えます。

6つ目。複数のノードの設定を、1つのファイルにまとめられる。1行目のノードの名前を変えて並べれば、1つのファイルに複数のノードの設定を書けます。すべてのノードに共通の値は、スラッシュとアスタリスク2つの下に書きます。フェーズ4 では、launch ファイルからこの YAML を読み込んで、起動するノードにパラメータを渡します。

一方で、YAML には、ノードの名前を間違えても、エラーにならずに既定の値で動く、という落とし穴があります。また、1 と1.0 の書き分けで型が変わる点にも、注意が要ります。YAML で渡したときは、起動した直後の表示や、ros2 param get で、意図した値になっているかを確かめる習慣を付けるとよい、とあります。

課題は3つです。

課題4 は、YAML の period を0.5 から1 に変えて起動すると、どうなるかを確かめることです。

課題5 は、YAML と一緒に、-p で period を3.0 にする指定も付けると、YAML と -p のどちらが勝つかを確かめることです。引数の並びの順が影響します。

課題6 は発展で、declare_parameter に、ParameterDescriptor、つまり説明の文と FloatingPointRange を付けて、ros2 param describe に範囲が出ることを確かめることです。範囲の外の値が、自動で拒否されることも確かめます。

## 6. 車両のシミュレーションとの対応。フェーズ5 への伏線

フェーズ5 の PI 制御のノードでは、パラメータを次のように使う予定です。原文は、パラメータ、意味、変更の使い方、の3列の表で、3行を挙げています。

kp は、比例のゲイン。実行中に ros2 param set で調整します。

ki は、積分のゲイン。同じく、実行中に調整します。

target_speed は、目標の速度。起動のときの YAML か、実行中に変えます。ただし、フェーズ5-2 では、実行中に次々と変わる入力なので、パラメータではなく、トピックの /target_velocity にした、とあります。

今回の、変更を検証して拒否するコールバックは、kp が0 より小さい、のような不正なゲインを弾くのに使えます。

## 7. Python の版と C++ の版の違いのまとめ

原文は、観点、Python、C++ の3列の表で、5行にまとめています。

1行目、宣言から取得までの書き方。Python は、このサンプルでは、declare_parameter で宣言し、別の行の get_parameter の value で取得する2行。declare_parameter の value と1行で書くこともできる。C++ は、山括弧で型を付けた declare_parameter が、宣言と同時に今の値を返す1行。

2行目、コールバックの引数と戻り値の型。Python は、引数が Parameter のリストで、戻り値は SetParametersResult を、コンストラクタの引数で組み立てる。C++ は、引数が rclcpp::Parameter の std::vector への const の参照で、戻り値は SetParametersResult の変数を作り、フィールドに代入する。

3行目、ハンドルを持つ必要。Python は不要で、戻り値を持たなくても動く。C++ は必須で、add_on_set_parameters_callback の戻り値をメンバに保存しないと、コールバックの登録が解かれる。

4行目、タイマーの作り直し。Python は、self.timer の cancel() を呼んでから create_timer し直す、明示的な取り消し。C++ は、新しい shared_ptr を timer_ に代入するだけで、古いタイマーは参照が無くなって自動で片付けられ、止まる。

5行目、値の取り出し方。Python は、value が型を問わず使える。C++ は、as_double() や as_string() など、宣言した型に合わせて呼び分け、型が合わないと例外になる。

C++ で最も見落としやすいのは、コールバックのハンドルの持ち忘れです。Python には無い落とし穴で、C++ の add_on_set_parameters_callback に特有の注意点です。

## 8. つまずきやすい点

原文では、症状と、確かめることの2列の表で、5行あります。

1行目。YAML を渡しても反映されない場合は、1行目のノードの名前が、実際のノードの名前と一致しているか。字下げのスペース。ros__parameters の綴り。

2行目。-p で period を2 にして失敗する場合は、実数は小数点を付けて2.0 と書く。型は、宣言のときの既定の値で決まる。

3行目。C++ で、実行中の変更に反応しない場合は、add_on_set_parameters_callback の戻り値を持っているか。

4行目。ros2 param set が、ノードが見つからない、と言う場合は、ノードが起動しているか。ノードの名前の /param_talker の、先頭のスラッシュ。

5行目。Python で、value の型が想定と違う場合は、宣言のときの既定の値の型が、1.0 か1 か。

## 9. 次へ

フェーズ3-4 で、サービス、つまり要求と応答を扱います。

## 10. 公式ドキュメントと参考資料

確認の状況が書かれています。2026年9月20日の時点で、下の資料は企画の文書に載せた URL で、今回は確かめ直していません。docs.ros.org は、ボット対策で本文の取得が拒否されます。

公式の資料は、ROS 2 Jazzy の3つです。パラメータを理解するチュートリアル、Python のクラスでパラメータを使うチュートリアル、C++ のクラスでパラメータを使うチュートリアルです。

日本語の資料として、Qiita の、YAML のファイルによる ROS2 のパラメータの設定の記事が1本挙げられています。記事は個人による非公式の解説で、版によって違う場合があり、公式のドキュメントと食い違う場合は公式を優先する、とあります。

原文の最後には、出典の注記があります。各サンプルの API の使い方は、公式のチュートリアルを参考にしました。ROS 2 のドキュメントは CC BY 4.0 です。ノードの名前、仕様、コード、文章は独自に書いたもので、一語ずつの転載ではありません。

以上で、フェーズ3-3 の手順書の話を終わります。

## 出典について

この原稿は、SanghunIm1991 さんの [ros2MinimalPhysicalAi の「フェーズ3-3 手順書: パラメータ（宣言・実行中の変更・YAML指定）」](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/docs/phase3_3_parameters.md)を、聞くために要約・意訳したものです。図の [phase3_3_sources.svg](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/docs/img/phase3_3_sources.svg) と [phase3_3_validate.svg](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/docs/img/phase3_3_validate.svg) は、言葉で説明しました。元にしたのは、[2026年10月14日の版](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/86dc0ed3d606c4a05d1e087421bb10318a37e521/docs/phase3_3_parameters.md)です。原文の文章と図と同じく、[クリエイティブ・コモンズ 表示 4.0 国際ライセンス](https://creativecommons.org/licenses/by/4.0/deed.ja)で提供します。

原稿の中に原文の表記のまま書いたコマンドと、コードの関数やクラスの名前は、原文では [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0) の対象です。ライセンスの全文は、原文のリポジトリの [LICENSE-APACHE-2.0](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/LICENSE-APACHE-2.0) にあります。サンプルコードと YAML のファイルは写さず、役割と要の行を言葉で説明しました。

原文では、API の使い方を [ROS 2 Documentation](https://docs.ros.org/en/jazzy/)（Open Robotics、[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)）の公式チュートリアルを参考にしたとしています。表示の例とエラーの文面は、各ツールの表示を言葉で説明したものです。
