<!--
聞くための原稿（読み上げでは読まれない記録）
原文: SanghunIm1991/ros2MinimalPhysicalAi の main ブランチの docs/phase3_2a_turtlesim.md（図は docs/img/phase3_2_flow.svg）
原文のコミット: 132df7b64d48d560def7ec7149f7003938d3d8e5（2026-10-14）
作成: 2026-10-20、Claude Code が手作業で作成（原稿化スキルはまだない）
原文のライセンス: 文章と図は CC BY 4.0、コードとコマンドは Apache-2.0（LICENSE の1と2）。原文の末尾に、API の使い方は公式チュートリアル（ROS 2 Documentation、CC BY 4.0）を参考にし、コードと文章は独自に書いた、とある。この原稿は、原文を聞くために要約・意訳したもの（改変あり）
方針: 英語の略語や製品名、関数やクラスの名前、短いコマンドは原文の表記のまま書く。サンプルコード2本と、package.xml・CMakeLists.txt・setup.py に足す行は、写さずに、ブロックの役割と要の行を言葉で説明した。期待する結果も、何が起きるかを言葉で説明した。図と表（仕様、主な API、Python版と C++版の違い、つまずきやすい点）は言葉で説明する。文字数の上限は設けない
省いたもの: URL、型の定義へのリンク
-->

# フェーズ3-2a: Twist で turtlesim を動かす（聞くための原稿）

これは、ros2MinimalPhysicalAi という教材の、フェーズ3-2a の手順書の話です。速度の指令の Twist を送って、turtlesim の亀を、自作のノードから動かします。

想定する環境は、WSL2 と Ubuntu 24.04 と ROS2 Jazzy で、turtlesim はフェーズ1 で入れてあります。前提は、フェーズ3-1 を終えて、talker などが動くことです。所要時間の目安は半コマです。言語は Python で、C++ の版は任意です。使う OSS は turtlesim で、GUI のウィンドウが開きます。

原文には、位置づけの囲みがあります。フェーズ3-2 は、互いに独立した2つのテーマに分けてあります。このフェーズ3-2a では、速度の指令の Twist を送って相手の turtlesim を動かす、turtle_circle というノードを作ります。フェーズ5 の車両のシミュレーションで直接使う内容なので、Python の版は必須です。もう1つのテーマの QoS の相性は、フェーズ3-2b で扱います。C++ の版の5節は任意です。

進め方は、フェーズ3-1 と同じです。2節の仕様は、何を作るかの定義で、API の使い方までは書いていません。4節と5節の冒頭の、主な API の表と、サンプルコードと解説を読んで理解し、送る値を変えて動かしながら、体で覚えます。サンプルは、手順書を作るときにビルドを確かめ、手順は2026年9月26日に実機で実行して確かめています。出力が細部で違う場合は、実機の表示を優先します。期待する結果は、コードと ROS2 の仕様から筆者が想定したもので、実機で確かめてあります。

この原稿では、サンプルコードを書き写さず、役割と要の行を言葉で説明します。

## 0. 学習目標と完了の条件

必須の条件は2つです。

1つ目。geometry_msgs/msg/Twist を publish して、turtlesim を自作のノードから動かせる。フェーズ1 で ros2 topic pub を使ってやったことを、コードで行います。Python の版です。

2つ目。新しい依存のパッケージ、geometry_msgs を、package.xml に足す手順を理解する。

任意の発展の条件は1つで、3つ目。C++ の版を書き、CMakeLists.txt にも依存を足す手順を理解する。

## 1. 全体像

原文の図は、SVG と mermaid の版があります。左から右へ、3つの箱が並びます。左の箱は turtle_circle で、自作のノード。真ん中の箱は turtlesim_node で、OSS。右の箱は「今回は使わない」です。左の箱から真ん中の箱へ、トピック /turtle1/cmd_vel の矢印があり、型は geometry_msgs/Twist です。真ん中の箱から右の箱へ、トピック /turtle1/pose の矢印があります。左と真ん中の箱は青で、使わない右の箱だけが灰色です。

## 2. 仕様: turtle_circle、Twist から turtlesim へ

仕様は、項目と内容の2列の表で、4行あります。

役割は Publisher。

トピックは /turtle1/cmd_vel で、型は geometry_msgs/msg/Twist。

動作は、10 Hz、つまり0.1秒の周期で、linear.x を2.0、angular.z を1.0 にした指令を送り続ける。亀が円を描きます。

備考は、パラメータにするのはフェーズ3-3 なので、今は決まった値でよい、です。

原文は、ここで、Twist は turtlesim 専用の型ではない、と説明しています。型の名前の先頭の geometry_msgs は、ROS2 が標準で用意している、位置、姿勢、速度などを表す型を集めたパッケージで、std_msgs の仲間です。Twist は、その中の、並進と回転の速度を表す汎用の型で、turtlesim は、速度の指令を受け取るのに、この標準の型を使っているだけです。turtlesim のために作られた型は、亀の位置を表す turtlesim/msg/Pose のように、先頭が turtlesim になります。

標準の型なので、相手が turtlesim でなくても、移動するロボットへの速度の指令には、ふつう Twist を使います。時刻と座標系の名前を添えた版の、TwistStamped も含みます。フェーズ5-0 では、ROS2 の側から同じ Twist を送って、Gazebo の車両を動かします。Gazebo に向けた形への変換は、橋渡しの役のノードが行います。自律移動の Nav2 のような大きなパッケージも、最後にはこの型で速度の指令を出します。この手順書で書く turtle_circle も、送り先のトピックの名前を差し替えるだけで、別のロボットへの速度の指令になります。フェーズ4 の4-6節で扱う remap、つまりトピックの名前の付け替えを使えば、コードを書き換えずに差し替えられます。

## 3. 準備: 依存の追加、geometry_msgs

turtle_circle は geometry_msgs を使うので、まず依存を足します。

Python の版で足すのは、learn_py の package.xml の1か所だけです。すでにある depend のタグの並びに、geometry_msgs の depend の行を1行足します。

C++ の版を作る場合は、package.xml と CMakeLists.txt の2つのファイルに足します。1つ目に、learn_cpp の package.xml の depend の並びに、Python の版と同じ行を1行足します。2つ目に、learn_cpp の CMakeLists.txt の、すでにある std_msgs の find_package の隣に、geometry_msgs の find_package を、REQUIRED を付けて1行足します。

CMakeLists.txt には、この後もう1行、turtle_circle 専用の ament_target_dependencies を書きます。これは5節の終わりで、add_executable と一緒に新しく足す行で、ここではまだ書きません。雛形が hello のために作った ament_target_dependencies のブロックは、複数の行に分けて書かれていますが、ターゲットごとの指定なので、hello 以外には効きません。そこに geometry_msgs を足す必要はありません。

package.xml の depend は、このパッケージは geometry_msgs に依存する、という宣言で、colcon が依存の関係からビルドの順を決めたり、rosdep が足りないものを見つけたりするのに使います。depend は、ビルドのときと実行のときの、両方の依存をまとめて宣言する書き方です。一方、CMakeLists.txt の find_package は、C++ のビルドのときに、ヘッダやライブラリの場所を探す指示です。C++ では両方が必要で、片方だけだとビルドのエラーになります。Python は package.xml だけでかまいません。

## 4. Python の版、learn_py

learn_py の内側の learn_py のフォルダに、turtle_circle.py を作ります。

主な API の表は1行だけです。Twist 型のメッセージは、geometry_msgs.msg から Twist を import し、msg.linear.x に2.0、msg.angular.z に1.0 を入れて使います。

### サンプルコードと解説

turtle_circle.py は、30行あまりのコードです。

先頭で、rclpy、geometry_msgs.msg の Twist、ExternalShutdownException、Node を import します。

TurtleCircle というクラスは、Node を継承します。__init__ では、ノードの名前を turtle_circle にし、create_publisher で、Twist 型、/turtle1/cmd_vel、10 の Publisher を作って self.pub に入れ、create_timer で、0.1秒ごとに on_timer を呼ぶタイマーを作って self.timer に入れます。

on_timer は、Twist のメッセージを作り、linear.x に2.0、angular.z に1.0 を入れて、publish します。

main 関数は、フェーズ3-1 のノードと同じ形です。rclpy.init、ノードを作る、try の中で rclpy.spin、except で KeyboardInterrupt と ExternalShutdownException を受け止める、finally で destroy_node と rclpy.try_shutdown、です。

原文の解説です。役割は、一定の速度の指令を10 Hz で送り続ける Publisher です。フェーズ1 で、ros2 topic pub に -r 10 を付けて手で打っていたことを、ノードにしたものにあたります。流れは、ノードを作る、Publisher とタイマーを用意する、タイマーが鳴るたびに Twist を作って送る、です。

import について。Twist は geometry_msgs のパッケージのメッセージの型です。だから、package.xml に geometry_msgs の依存が要ります。ExternalShutdownException は、終わりの処理で使います。

super().__init__ は、親のクラスの Node を、turtle_circle という名前で初期化します。これを呼ばないと、それより後の create で始まる関数が使えません。

create_publisher の引数は、メッセージの型、トピックの名前、QoS です。QoS に整数を渡すと、深さ、つまりキューに溜める件数が10 で、ほかは既定の値、つまり reliable と volatile、という意味になります。QoS の中身は、フェーズ3-2b で扱います。トピックの名前の先頭にスラッシュを付けると、絶対の名前になり、ノードに名前空間を付けて起動しても、組み立てられるトピックの名前が変わりません。名前空間が効く範囲と、意識しなければならない場面は、Tips 集の8節にあります。turtlesim が購読するトピックは /turtle1/cmd_vel なので、綴りが違うと亀は動かず、エラーも出ません。

create_timer は、0.1秒、つまり10 Hz ごとに on_timer を呼びます。1つ目の引数の単位は秒です。self.timer に持っているのは、後から止めたり周期を変えたりできるようにするためで、Python ではノードも内部で持っているので、必須ではありません。

on_timer について。Twist() は、すべてのフィールドが0 で作られます。Twist は、linear、つまり並進の速度の x、y、z で、単位はメートル毎秒と、angular、つまり回転の速度の x、y、z で、単位はラジアン毎秒、の2つのベクトルを持ちます。turtlesim は2次元なので、使うのは前進の linear.x と、旋回の angular.z だけです。前進の2.0 と旋回の1.0 を同時に出し続けるので、亀は、2.0 を1.0 で割った、半径2.0 の円を描きます。6節の課題2 で、値を変えて、半径が変わることを確かめます。

main の中の流れについて。Ctrl+C は KeyboardInterrupt に、外からのシャットダウンは ExternalShutdownException になるので、どちらも受け止めて、正常に終わらせます。finally の destroy_node と try_shutdown は、途中で例外が出ても必ず実行したい後始末です。try_shutdown は、すでにシャットダウンしていてもエラーにならない版です。

main の引数の args の既定を None にした形は、setup.py の登録の行が、この関数を呼ぶためです。ファイルの末尾に、if __name__ イコール __main__ の行は要りません。ros2 run は、entry_points から作られたスクリプトを通して main を呼ぶからです。

観察のポイント。turtlesim を先に起動しておき、ros2 topic echo /turtle1/cmd_vel で、linear.x の2.0 と angular.z の1.0 が流れていることを見ます。亀が動かないときは、まず echo の側に値が出ているかで、送れていないのか、届いていないのかを切り分けます。

次に、setup.py の entry_points に、turtle_circle の登録の行を1行足します。フェーズ3-1 までに足した行は残します。形は、実行ファイルの名前、イコール、パッケージとモジュール、コロン、関数、で、ros2 run learn_py turtle_circle の turtle_circle が左辺、呼ばれる関数が右辺の main です。entry_points を変えたときは、--symlink-install でもビルドし直しが必要です。コンマの付け忘れや、リストの外へ書いてしまう誤りに注意します。

cd で ~/ros2_ws に移り、colcon build --symlink-install に --packages-select learn_py を付けてビルドし、source install/setup.bash を実行します。期待する結果は、フェーズ3-1 と同じく、learn_py の Finished と、1つのパッケージが終わったという Summary が出ることです。ros2 pkg executables learn_py を実行すると、今回足した turtle_circle の行が、すでにある実行ファイルと一緒に並びます。

## 5. C++ の版、learn_cpp

このフェーズの C++ の版は、任意の発展です。フェーズ5 の車両のシミュレーションは Python で作ると決めているので、ここで C++ の版を作らなくても先へ進めます。Python の版との違いは、turtle_circle.cpp の解説に書いてあるので、読むだけでも概要がつかめます。C++ の版を作らない場合は、C++ に向けた依存の追加も要りません。

learn_cpp の src に turtle_circle.cpp を作ります。主な API の表は1行で、Twist 型のメッセージは、geometry_msgs/msg/twist.hpp を include し、msg.linear.x に2.0、msg.angular.z に1.0 を入れて使います。

### サンプルコードと解説

turtle_circle.cpp は、40行ほどのコードです。chrono と memory、geometry_msgs/msg/twist.hpp、rclcpp/rclcpp.hpp を include し、using namespace std::chrono_literals を書きます。

TurtleCircle というクラスは、rclcpp::Node を public で継承します。コンストラクタは、初期化のリストで Node に "turtle_circle" を渡し、本体で、create_publisher で Twist 型を山括弧で付けて、/turtle1/cmd_vel、10 の Publisher を作って pub_ に入れ、create_wall_timer で、100ms ごとに、this を取り込んだラムダから on_timer を呼ぶタイマーを作って timer_ に入れます。private の on_timer は、Twist のメッセージを作り、linear.x に2.0、angular.z に1.0 を入れて、pub_ の矢印の publish で送ります。メンバ変数は、Publisher の SharedPtr の pub_ と、TimerBase の SharedPtr の timer_ です。main は、rclcpp::init、make_shared でノードを作って rclcpp::spin に渡す、rclcpp::shutdown、の形です。

原文の解説は、Python の版と同じ Publisher を C++ で書いたもので、ここでは言語に固有の点を中心に書く、としています。

include について。メッセージの型は、パッケージの名前、msg、型の名前を小文字のスネークケースにしたもの、に .hpp を付けたヘッダで取り込みます。型の名前の側は、geometry_msgs、msg、Twist を、コロン2つの名前空間で区切って書きます。

using namespace std::chrono_literals は、100ms や 1s のような時間のリテラルを使えるようにします。Python の0.1秒にあたる部分で、こちらは単位が型に入るので、取り違えにくい。

クラスの継承は、Python の、Node を継承したクラスにあたります。ノードの名前は、初期化のリストで Node に渡します。

create_publisher は、型をテンプレートの引数で指定し、引数はトピックの名前と QoS です。10 は rclcpp::QoS に自動で変換され、深さが10 で、ほかは既定の値になります。

create_wall_timer には、周期とコールバックを渡します。wall は、実際の時間、つまり壁掛け時計で動くタイマーという意味です。コールバックはラムダ式で、this は、メンバ関数を呼ぶためにオブジェクト自身を取り込む指定です。同じことは std::bind でも書けますが、ラムダの方が読みやすいので、この手順書はラムダにそろえています。

Twist のメッセージは、各フィールドが0 で初期化されているので、使う2つだけを代入すればよい。publish の前の矢印は、Publisher が shared_ptr で返ってくるからです。

メンバ変数の pub_ と timer_ は SharedPtr、つまり std::shared_ptr の別名です。ノードが持ち続けている間だけ、Publisher とタイマーが生きます。ローカル変数で受けて関数を抜けると、片付けられて、タイマーが鳴らなくなります。

main では、Python の版のような try と finally は要りません。Ctrl+C は rclcpp が受けて、spin から抜けさせます。ノードは shared_ptr なので、main を抜けるときに自動で片付けられます。

つまずきやすい点。CMakeLists.txt の ament_target_dependencies に geometry_msgs を書き忘れると、twist.hpp が見つからない、というビルドのエラーになります。

次に、CMakeLists.txt に追記し、install(TARGETS ...) に turtle_circle を足します。フェーズ3-1 までの分は残します。足すのは、turtle_circle の add_executable で、ソースは src の turtle_circle.cpp。それと、turtle_circle の ament_target_dependencies で、rclcpp と geometry_msgs。そして install(TARGETS ...) を、hello、talker、listener、sine_pub、sine_sub、turtle_circle の6つの名前に並べ直します。

説明は3つです。add_executable は、ソースから実行ファイルをビルドする指定で、Python の entry_points にあたります。ament_target_dependencies は、そのターゲットが使うパッケージ、つまりヘッダとライブラリを、ターゲットごとに並べます。turtle_circle は Twist を使うので geometry_msgs、それと rclcpp が必要です。ここに書き漏らすと、find_package があっても、そのターゲットのビルドが通りません。install(TARGETS ...) は、ビルドした実行ファイルを、install の learn_cpp の lib の learn_cpp に置きます。ros2 run learn_cpp はこの場所を探すので、ここに名前が無いと、実行ファイルが見つからない、と言われます。すでにある hello から sine_sub までの名前は消さずに残し、turtle_circle を足します。

cd で ~/ros2_ws に移り、colcon build --symlink-install に --packages-select learn_cpp を付けてビルドし、source install/setup.bash を実行します。期待する結果は、learn_cpp の Finished と、1つのパッケージが終わったという Summary が出ることです。geometry_msgs の find_package を書き忘れていると、ここで learn_cpp が Failed になり、その上に、geometry_msgs が見つからない、という趣旨の CMake のエラーが出ます。

## 6. 実験: Twist で turtlesim を動かす

ターミナルを2つ使います。T1 で ros2 run turtlesim turtlesim_node を実行し、T2 で ros2 run learn_py turtle_circle を実行します。C++ の版を作った場合は、T2 は ros2 run learn_cpp turtle_circle でもかまいません。

期待する結果は4つです。

1つ目。turtle_circle はログを出さないので、T2 には何も表示されません。変化は、turtlesim のウィンドウに現れます。

2つ目。亀は、画面の中央から右向きに動き出し、左回り、つまり反時計回りに、円を描き続けます。半径は、linear.x を angular.z で割った、2.0 割る1.0 で2 です。画面の1辺は約11 です。1周にかかる時間は、2π を angular.z で割った、約6.3秒です。通った跡に、白い円が残ります。

3つ目。T2 を Ctrl+C で止めると、指令が途切れて、約1秒後に亀が止まります。

4つ目。Python の版と C++ の版で、亀の動きに違いはありません。

課題は3つです。

課題1 は、C++ の版を作った場合に、Python の版と C++ の版の turtle_circle をそれぞれ動かして、亀の動きが同じになることを確かめることです。

課題2 は、円の半径が linear.x 割る angular.z になることを、値を変えて確かめることです。例えば linear.x を1.0 にします。

課題3 は発展で、/turtle1/pose、つまり turtlesim/msg/Pose を購読するノードを作り、位置をログに出すことです。turtlesim への依存を package.xml に足す必要があります。

## 7. Python の版と C++ の版の違いのまとめ

4節と5節のサンプルを比べると、ノードの形、つまり Publisher とタイマーを作り、タイマーで送る、という形は、フェーズ3-1 の talker と同じです。違いは、別のパッケージのメッセージの型を使うための手続きに集まります。

原文は、観点、Python、C++ の3列の表で、4行にまとめています。

1行目、型の取り込み。Python は、geometry_msgs.msg から Twist を import する。C++ は、twist.hpp を include し、ファイルの名前は小文字のスネークケース。型は、名前空間で区切った geometry_msgs、msg、Twist。

2行目、依存の宣言。Python は、package.xml の depend だけ。C++ は、package.xml の depend に加えて、CMakeLists.txt の find_package と、ターゲットごとの ament_target_dependencies。

3行目、周期の書き方。Python は0.1 で、単位は秒。数値だけなので、取り違えに注意。C++ は 100ms で、単位が型に入る。

4行目、実行ファイルの登録。Python は、setup.py の entry_points に1行。C++ は、add_executable と install(TARGETS ...) の2か所。

C++ では、依存を書く場所が、depend、find_package、ament_target_dependencies の3つに分かれていて、どれか1つを忘れるとビルドが通りません。Python は、depend を書き忘れても、この環境では動いてしまうことが多い。システムに geometry_msgs が入っているからです。依存の宣言としては必要なので、動いても書いておきます。

## 8. つまずきやすい点

原文では、症状と、確かめることの2列の表で、2行あります。

1行目。亀が動かない場合は、turtlesim が起動しているか。ros2 topic info /turtle1/cmd_vel で、Subscriber が1つあるか。トピックの名前の先頭のスラッシュ。

2行目。C++ で、geometry_msgs が見つからない、というビルドのエラーになる場合は、package.xml の depend、CMakeLists.txt の geometry_msgs の find_package と、ament_target_dependencies。

## 9. 次へ

フェーズ3-2b で、QoS の相性を体験します。フェーズ3-2a とは独立したテーマで、ここで作った turtle_circle は使いません。

## 10. 公式ドキュメントと参考資料

確認の状況が書かれています。2026年9月20日の時点で、下の資料は企画の文書に載せた URL で、今回は確かめ直していません。docs.ros.org は、ボット対策で本文の取得が拒否されます。

公式の資料は、ROS 2 Jazzy の2つです。geometry_msgs のページと、turtlesim と ros2 と rqt の使い方のチュートリアルです。公式のドキュメントと食い違う場合は、公式を優先する、とあります。

原文の最後には、出典の注記があります。各サンプルの API の使い方は、公式のチュートリアルを参考にしました。ROS 2 のドキュメントは CC BY 4.0 です。ノードの名前、仕様、コード、文章は独自に書いたもので、一語ずつの転載ではありません。

以上で、フェーズ3-2a の手順書の話を終わります。

## 出典について

この原稿は、SanghunIm1991 さんの [ros2MinimalPhysicalAi の「フェーズ3-2a 手順書: Twistでturtlesimを動かす」](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/docs/phase3_2a_turtlesim.md)を、聞くために要約・意訳したものです。図の [phase3_2_flow.svg](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/docs/img/phase3_2_flow.svg) は、言葉で説明しました。元にしたのは、[2026年10月14日の版](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/132df7b64d48d560def7ec7149f7003938d3d8e5/docs/phase3_2a_turtlesim.md)です。原文の文章と図と同じく、[クリエイティブ・コモンズ 表示 4.0 国際ライセンス](https://creativecommons.org/licenses/by/4.0/deed.ja)で提供します。

原稿の中に原文の表記のまま書いたコマンドと、コードの関数やクラスの名前は、原文では [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0) の対象です。ライセンスの全文は、原文のリポジトリの [LICENSE-APACHE-2.0](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/LICENSE-APACHE-2.0) にあります。サンプルコードは写さず、役割と要の行を言葉で説明しました。

原文では、API の使い方を [ROS 2 Documentation](https://docs.ros.org/en/jazzy/)（Open Robotics、[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)）の公式チュートリアルを参考にしたとしています。
