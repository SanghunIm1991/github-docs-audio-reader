<!--
聞くための原稿（読み上げでは読まれない記録）
原文: SanghunIm1991/ros2MinimalPhysicalAi の main ブランチの docs/reference_interfaces.md（図は docs/img/reference_interfaces_generate.svg）
原文のコミット: 41d2c800082a372a810d286ded1bb56d9c05b67e（2026-10-17）
作成: 2026-10-24、Claude Code が手作業で作成（原稿化スキルはまだない）
原文のライセンス: 文章と図は CC BY 4.0、コードとコマンドは Apache-2.0（それぞれ LICENSE の2と1）。原文の末尾に、文法と型の対応は、公式ドキュメント（CC BY 4.0）と手元の定義ファイル・生成済みのコード・rosidl_adapter から確かめ、自分の言葉でまとめたもので、期待する結果に載せた標準の型の定義は ros2 interface show の表示（定義の元は common_interfaces・rcl_interfaces で、Apache License 2.0）、自作の型の定義ファイル・サンプル・文章は独自に書いたもの、とある。この原稿は、原文を聞くために要約・意訳したもの（改変あり）
方針: 英語の略語や製品名、型・項目・関数の名前、短いコマンドは原文の表記のまま書く。単位は「毎秒のメートル」のように読む。定義ファイル（VehicleState.msg・SetGains.srv・DriveDistance.action）と、CMakeLists.txt・package.xml に足す行は、写さずに、項目の名前と型、ブロックの役割を言葉で説明した。CMakeLists.txt と package.xml に足す行は、原文の表がすべての行を説明しているので、要の行は立てなかった。C++ の使い方の例は、原文の説明に出てこない要の行（pedal に定数を入れる行）を言葉で説明した。期待する結果（ros2 interface・ros2 pkg create・colcon build・python3 の表示）は写さず、期待する結果の側では骨組みを言い、値は原文の説明の側で1回だけ読んだ。6-4節の ros2 interface show の表示は、6-2節で読んだ定義と同じなので、値を読まずに「6-2節で書いた定義」と言った。図と表（3つの種類、名前の書き方、基本の型、配列、名前の決まり、標準のパッケージ、調べるコマンド、自作する3つの型、書き足した行、つまずきやすい点、教材のどこで何を使ったか）は言葉で説明し、表の値は全部読んだ。ホームのフォルダは「ホームの」と言い換えた。公式ドキュメントの節は、リンクの題名と括弧の説明を読んだ。文字数の上限は設けない
省いたもの: URL、リンク先のファイル名、型の定義へのリンク、mermaid 版の図（SVG と同じ内容で、折りたたみになっている）、2-4節の Quaternion の x・y・z の既定値の0、2-5節の Log の定数のうち INFO 以外の値、ros2 pkg create の表示の版数・説明・作ったフォルダとファイルの行の細部と、メンテナのダミーのメールアドレス、ビルドの秒数、6-6節のエラーの英文のうち、名前の正規表現のパターン（意味だけを言った）
-->

# 参考資料: ROS2 の標準のデータ型とインターフェース、自作する方法も（聞くための原稿）

この教材では、トピックに std_msgs の msg の Float64 や、geometry_msgs の msg の Twist を、サービスに std_srvs の srv の Trigger を、アクションに example_interfaces の action の Fibonacci などを使います。これらはどれも、ROS2 が標準で用意している、インターフェース、つまり、ノードどうしがやり取りするデータの型です。この資料では、インターフェースの定義の読み方、よく使う標準の型、型を調べるコマンドをまとめ、最後に、インターフェースを自分で定義する方法を扱います。

対象は ROS2 Jazzy で、この資料を作ったときに /opt/ros/jazzy に入っていたものです。前提は、フェーズ3-1、つまりトピックの手順書を読み終えていることです。サービスのフェーズ3-4 と、アクションのフェーズ3-5 の節は、読んでいなくても、型の説明は読めます。所要の目安は、読むだけなら0.5 から1コマ、6節の自作を手元で試すなら、さらに0.5 から1コマです。

原文には、囲みが3つあります。

1つ目は、この資料の位置づけです。手順書、つまりフェーズの流れからは独立した参考資料で、必要になったときに読めばよい、とあります。1節から5節は読み物で、手を動かす作業はありません。6節は、自分でインターフェースを定義してみたくなったときの手順で、試すかどうかは任意です。手順書のどのフェーズも、6節で作るパッケージを前提にしていません。

2つ目は、出どころです。型の定義、文法、生成される Python と C++ の型は、/opt/ros/jazzy にある定義ファイルと生成済みのコード、定義ファイルを読み込む部品の rosidl_adapter で確かめた、とあります。文法の細部は、8節の公式ドキュメントの Interfaces とも照らし合わせました。文章は自分の言葉で書いていて、公式ドキュメントの転載ではありません。図の SVG は生成のスクリプトで作り、文字と線の重なりは計算で点検しましたが、画像にして目で確かめてはいない、とあります。表示が崩れている場合は、図の下にある、同じ内容の mermaid の版を参照します。

3つ目は、期待する結果の出どころです。表示はすべて、この資料を作ったときに、使い捨ての環境で実際に実行したものです。実行したのは、ros2 interface、ros2 pkg create、colcon build、python3 のマイナス c だけで、ノードは起動していません。ビルドの秒数は、環境によって変わります。ros2 pkg create の表示の作成先のパスは、練習環境の場所、つまりホームの ros2_ws の src に直して載せた、とあります。

この原稿では、定義ファイルとコードは書き写さずに、中身と役割を言葉で説明します。表示も、何が表示されるかを言葉で説明します。

## 0. この資料で分かること

分かることは4つです。

1つ目。インターフェースの3つの種類、つまりメッセージ、サービス、アクションと、std_msgs の msg の Float64 のような名前の読み方。

2つ目。定義ファイル、つまり .msg、.srv、.action の書き方と、それが Python と C++ で、どんな型になるか。

3つ目。よく使う標準のパッケージと型、型を調べるコマンド。

4つ目。標準の型で足りないときに、自分でインターフェースを定義して使う方法。

## 1. 全体像

### 1-1. 3つの種類

インターフェースには、通信の方法に合わせて、3つの種類があります。表は5列で、種類、定義ファイル、使う通信、中身、例、です。3行あります。

1行目は、メッセージ、msg です。定義ファイルは .msg、使う通信はトピック、中身はデータの並び、例は std_msgs の msg の Float64 です。

2行目は、サービス、srv です。定義ファイルは .srv、使う通信はサービス、中身は、要求と応答をマイナス3つで区切ったもの、例は std_srvs の srv の Trigger です。

3行目は、アクション、action です。定義ファイルは .action、使う通信はアクション、中身は、ゴール、結果、途中経過を、マイナス3つで区切ったもの、例は example_interfaces の action の Fibonacci です。

サービスとアクションの定義は、マイナス3つで区切った、メッセージの組です。フェーズ3-4 の1節で扱う AddTwoInts の定義は、マイナス3つの上が要求、下が応答です。アクションは区切りが2つで、上から順に、ゴール、結果、途中経過になります。

### 1-2. 名前の読み方

std_msgs の msg の Float64 は、std_msgs パッケージの、メッセージ、つまり msg の、Float64 という型、と読みます。同じ型を、Python と C++ では、次のように書きます。表は2列で、書く場所と書き方です。4行あります。

1行目は、ros2 topic pub などのコマンドです。std_msgs、スラッシュ、msg、スラッシュ、Float64 と書きます。

2行目は、Python の import です。from std_msgs.msg import Float64 と書きます。

3行目は、C++ の include です。std_msgs の msg の float64.hpp を include します。ファイル名は、型名を小文字とアンダースコアに直したものです。

4行目は、C++ の型名です。std_msgs、コロン2つ、msg、コロン2つ、Float64 と書きます。

サービスとアクションも同じ形で、std_srvs の srv の Trigger は、from std_srvs.srv import Trigger、std_srvs の srv の trigger.hpp の include、そして、コロン2つでつないだ std_srvs の srv の Trigger になります。

### 1-3. 定義ファイルから、各言語のコードが作られる

インターフェースの本体は、.msg、.srv、.action という、文字だけの定義ファイルです。パッケージをビルドすると、ROS2 のコード生成の仕組み、rosidl が、定義ファイルから、Python のクラスと、C++ のクラス、つまり構造体を作ります。ノードは、それを import や include して使います。

図は、左から右へ流れる図で、箱が4つあります。

いちばん左は、点線で囲んだ、インターフェースのパッケージ、という枠です。中の箱に、msg の VehicleState.msg、srv の SetGains.srv、action の DriveDistance.action の3つのファイル名と、ament_cmake で作る、という注記が並びます。

この箱から右へ矢印が出て、真ん中の箱に入ります。真ん中の箱は、colcon build の、rosidl_generate_interfaces で、コードを生成する、とあります。

真ん中の箱からは、矢印が2本に分かれて、右の2つの箱に入ります。右上の箱は、Python のクラスで、learn_interfaces.msg、import して使う、とあります。右下の箱は、C++ のクラス、つまり構造体で、コロン2つでつないだ learn_interfaces の msg、include して使う、とあります。右の2つの箱の間には、同じ定義から作るので、言語が違ってもつながる、と書かれています。

Python のノードと C++ のノードが、同じトピックで話せるのは、フェーズ3-1 の6節の内容ですが、両方が、同じ定義ファイルから作られたコードを使い、同じ形でデータを送るからです。標準の型も、std_msgs などのパッケージの中で同じように作られ、ROS2 と一緒にインストールされています。図の定義ファイルの名前は、6節で自作する例のものです。

## 2. 定義ファイルの書き方

### 2-1. 1行が1つの項目

定義ファイルは、1行に1つの項目、つまりフィールドを、型、名前、の形で書きます。シャープから後ろはコメントです。

原文の例は3行で、どれも型が float64 で、名前が x、y、z です。これは、geometry_msgs の msg の Point、つまり3次元の点の中身と、同じ形です。

### 2-2. 基本の型

項目に使える基本の型と、生成される Python と C++ の型を、表にしています。表は4列で、定義ファイルの型、中身、Python、C++ です。8行あります。

1行目は bool です。中身は真偽値で、Python は bool、C++ も bool です。

2行目は byte です。中身は1バイトのデータで、Python は長さ1の bytes、C++ は unsigned char です。

3行目は char です。中身は1バイトの文字で、Python は int、C++ は uint8_t です。

4行目は、int8、int16、int32、int64 です。中身は符号付きの整数で、数字はビット数です。Python は int、C++ は int8_t から int64_t です。

5行目は、uint8、uint16、uint32、uint64 です。中身は符号なしの整数で、Python は int、C++ は uint8_t から uint64_t です。

6行目は、float32 と float64 です。中身は浮動小数点数で、Python は float、C++ は、それぞれ float と double です。

7行目は string です。中身は文字列で、Python は str、C++ は std::string です。

8行目は wstring です。中身は、UTF-16 で表した文字列で、ASCII 以外の文字を扱う版です。Python は str、C++ は std::u16string です。

表の後に、注意が2つあります。

1つ目。教材で速度やペダルに使う float64 は、C++ の double、Python の float です。

2つ目。Python の int には範囲がありませんが、定義ファイルの int32 は、32ビットに収まる値しか送れません。Jazzy の既定では、Python で、範囲の外の値や、違う型の値を代入しても、その場ではエラーになりません。生成されたクラスは、環境変数の ROS_PYTHON_CHECK_FIELDS が1のときだけ、代入を検査します。値の範囲は、送る側で気をつけます。

### 2-3. 配列

型の後ろに、角括弧の開きと閉じを付けると、配列になります。表は4列で、書き方、意味、Python、C++ です。4行あります。

1行目は、角括弧に3を入れた float64 です。長さがちょうど3の配列で、Python は、数値なら numpy.ndarray、C++ は、山括弧で double と3を付けた std::array です。

2行目は、空の角括弧の float64 です。長さが自由の配列で、Python は、数値なら array.array、文字列やメッセージなら list です。C++ は、山括弧で double を付けた std::vector です。

3行目は、角括弧に、小なりイコール10を入れた float64 です。長さが10以下の配列で、Python は上と同じ、C++ は rosidl_runtime_cpp の BoundedVector、つまり長さの上限付きの vector です。

4行目は、string に小なりイコール16を付けたものです。16文字以下の文字列で、Python は str、C++ は std::string です。

長さが決まっている配列の例は、nav_msgs の msg の Odometry の中の、長さ36の float64 の配列、covariance です。Odometry は、移動ロボットの位置と速度を送る型で、covariance は、6かける6の、誤差の大きさの表です。どちらも2-4節で扱います。長さが自由の配列の例は、std_msgs の msg の Float64MultiArray の、float64 の配列の data です。

Python で試すコマンドは、python3 のマイナス c で、Float64MultiArray を import し、data に 1.0 と 2.0 のリストを渡して作り、その data を表示するものです。

期待する結果は1行で、array の括弧の中に、型の文字の d と、渡した2つの値の並びが表示されます。

Python の list を渡しても、中では、array.array、つまり、同じ型の数値だけを並べる、Python の標準の配列にそろえて持ちます。表示の d は、double、つまり float64 の並び、という意味です。

### 2-4. 別のメッセージを項目にする、入れ子

項目の型には、基本の型のほかに、別のメッセージの型も書けます。フェーズ5-0 と5-4 で使うオドメトリ、つまり nav_msgs の msg の Odometry は、入れ子の深い例です。オドメトリは、車輪の回転などから推定した、移動ロボットの位置と速度です。ros2 interface show は、入れ子の型の中身も、字下げで表示します。ここでは、マイナス2つの no-comments を付けて、コメントを省きます。

コマンドは、ros2 interface show に、nav_msgs の msg の Odometry と、マイナス2つの no-comments を付けたものです。

期待する結果は、項目が4つの段に分かれて表示されます。

1つ目は、std_msgs の Header 型の header です。その中に、builtin_interfaces の Time 型の stamp があり、さらにその中に、int32 の sec と、uint32 の nanosec があります。stamp の次に、string の frame_id があります。

2つ目は、string の child_frame_id です。

3つ目は、geometry_msgs の PoseWithCovariance 型の pose です。その中に、Pose 型の pose と、長さ36の float64 の配列の covariance があります。Pose の中には、Point 型の position と、Quaternion 型の orientation があります。position の中は、float64 の x、y、z です。orientation の中は、float64 の x、y、z、w で、それぞれの後ろに既定値が付いています。

4つ目は、geometry_msgs の TwistWithCovariance 型の twist です。その中に、Twist 型の twist と、長さ36の float64 の配列の covariance があります。Twist の中には、Vector3 型の linear と angular があり、どちらの中も、float64 の x、y、z です。

読み方は4つです。

1つ目。字下げが1段深い行は、その上の行の型の中身です。例えば、pose の中に、Pose 型の pose があり、その中に、position、つまり Point 型の位置と、orientation、つまり Quaternion 型があります。クォータニオンは、4つの数で3次元の向きを表す形式です。Python では、この段を、msg.pose.pose.position.x のように、ドットでたどります。任意のフェーズ6-2 で書く、見張りのノードの goal_monitor も、この書き方で、オドメトリの位置を読みます。

2つ目。別のパッケージの型は、std_msgs スラッシュ Header のように、パッケージ名スラッシュ型名で書き、同じパッケージの型は、Pose のように、型名だけで書けます。PoseWithCovariance は geometry_msgs の型なので、中の Pose は、geometry_msgs の Pose になります。定義ファイルの中では、間の msg を書きません。

3つ目。Quaternion の、float64 の w の行の最後の1は、既定値です。2-5節で扱います。

4つ目。covariance は、値がどれくらい不確かかを表す表、つまり共分散行列で、この資料では立ち入りません。

### 2-5. 既定値と定数

項目の後ろに値を書くと、既定値になります。メッセージを作ったときに、その値が最初から入ります。原文の例は2行で、int32 の count に5、string の name に、ダブルクォートで囲んだ car を付けたものです。

既定値は、基本の型の項目と、その配列にだけ付けられます。入れ子のメッセージの項目には付けられません。何も書かなければ、数値は0、文字列は空、真偽値は false になります。

イコールでつなぐと、定数になります。定数は項目ではなく、型に付いた決まった値で、送るデータには入りません。名前は大文字で書きます。rcl_interfaces の msg の Log、つまりノードのログを運ぶ型は、ログの重要度を、定数で持っています。

コマンドは、ros2 interface show に、rcl_interfaces の msg の Log と、マイナス2つの no-comments を付けたものです。

期待する結果は、先頭の抜粋が載っています。まず、uint8 の定数が5つ、DEBUG、INFO、WARN、ERROR、FATAL の順に、イコールで値を付けて並びます。続いて項目が、builtin_interfaces の Time 型の stamp、その中の int32 の sec と uint32 の nanosec、uint8 の level、string の name、string の msg、と並びます。

level には、Python なら Log.INFO、C++ なら、コロン2つでつないだ rcl_interfaces の msg の Log の INFO のように、定数の名前で値を入れられます。INFO の値の20を、数字のままコードに直接書くより、意味が読み取りやすい、とあります。

### 2-6. 名前の決まり

表は3列で、名前、決まり、例です。3行あります。

1行目は、型名、つまりファイル名です。大文字で始め、英字と数字だけで、単語の区切りは大文字にします。例は VehicleState で、ファイルは VehicleState.msg です。

2行目は、項目の名前です。小文字で始め、小文字、数字、アンダースコアだけにします。アンダースコアの連続や、末尾のアンダースコアは使えません。例は target_velocity です。

3行目は、定数の名前です。大文字で書きます。例は PEDAL_MAX です。

決まりを破ると、定義ファイルを読み込む時点、つまりビルドでエラーになります。6-6節の表に、実際のエラーの文面を載せた、とあります。

## 3. よく使う標準のパッケージと型

### 3-1. 一覧

表は3列で、パッケージ、中身、代表的な型です。8行あります。

1行目は std_msgs です。中身は、基本の型を1つだけ包んだ型と、時刻付きの見出しです。代表的な型は、Float64、String、Int32、Bool、Header、Float64MultiArray です。

2行目は builtin_interfaces です。中身は、時刻と時間の長さで、代表的な型は Time と Duration です。

3行目は geometry_msgs です。中身は、位置、向き、速度、力などの幾何です。代表的な型は、Point、Vector3、Quaternion、Pose、Twist、TwistStamped です。

4行目は nav_msgs です。中身は、移動ロボットの位置と地図です。代表的な型は、Odometry、Path、OccupancyGrid です。

5行目は sensor_msgs です。中身はセンサの値で、代表的な型は、Imu、LaserScan、JointState、Image です。

6行目は std_srvs です。中身は、中身の少ない汎用のサービスで、代表的な型は、Empty、Trigger、SetBool です。

7行目は example_interfaces です。中身はチュートリアル用の例で、代表的な型は AddTwoInts と Fibonacci です。

8行目は、rcl_interfaces と rosgraph_msgs です。中身は、ROS2 自身が使う型で、ログ、パラメータ、時計です。代表的な型は、Log、ParameterEvent、Clock です。

ros2 interface packages で、今の PC に入っている、インターフェースのパッケージを一覧できます。4節で扱います。ROS2 の Desktop Install だけでも数十個あり、フェーズ5-0 で入れた Gazebo の連携のような、追加のパッケージを入れると増えます。

### 3-2. 見出しの Header と、Stamped の付く型

std_msgs の msg の Header は、いつの値か、つまり stamp と、どの座標系で測った値か、つまり frame_id を持つ、小さなメッセージです。TwistStamped のように、名前に Stamped が付く型は、元の型、ここでは Twist に、Header を足したものです。

時刻を持つ型と、持たない型では、受け取る側の扱いが変わります。例えば rqt_plot は、時刻の欄を持たない Float64 の値を、届いた時刻で横軸に並べます。フェーズ6-1 の3-1節の内容です。時刻を持つ型なら、送った側が付けた時刻で扱えます。

ただし、付ける時刻が PC の時計、つまり現在時刻なら、PC の時計が時刻合わせで飛んだとき、付ける時刻も同じだけ飛びます。時計が飛ぶ話は、フェーズ6-1 の2-2節の注記にあります。時刻を付けておけば、時計の飛びを後から直せる、というわけではありません。直せるのは、シミュレーション時刻のように、PC の時計とは別に進む時刻を付けた場合です。シミュレーション時刻は、シミュレータが自分の計算に合わせて進める時刻で、フェーズ5-4 の5節で扱います。

### 3-3. 単位と向きの決まり

ROS2 の標準の型は、単位を国際単位系にそろえる約束になっています。長さはメートル、時間は秒、角度はラジアン、速度は毎秒のメートルです。これは REP 103 という約束で、8節に挙げています。定義ファイルに単位の欄は無いので、自作の型では、コメントに単位を書いておきます。6-2節に例があります。

## 4. 型を調べるコマンド

表は2列で、コマンドと、分かることです。5行あります。

1行目は ros2 interface packages で、インターフェースを持つパッケージの一覧が分かります。

2行目は、ros2 interface package に、パッケージを付けたもので、そのパッケージの型の一覧が分かります。

3行目は ros2 interface list で、すべての型の一覧が、メッセージ、サービス、アクションに分けて表示されます。

4行目は、ros2 interface show に、型を付けたもので、型の定義が分かります。マイナス2つの no-comments でコメントを省き、マイナス2つの all-comments で、入れ子の型のコメントも出します。

5行目は、ros2 interface proto に、型を付けたものです。その型の値を、すべての項目を既定値にした YAML で表示します。ros2 topic pub に渡す値の雛形です。

例のコマンドは2つで、ros2 interface package に std_srvs を付けたものと、ros2 interface proto に、geometry_msgs の msg の Twist を付けたものです。

期待する結果です。型の並ぶ順は、環境によって変わることがある、とあります。1つ目のコマンドでは、std_srvs の srv の、Trigger、Empty、SetBool の3行が並びます。2つ目のコマンドでは、ダブルクォートで囲んだ YAML が出ます。中は、linear と angular の下に、それぞれ x、y、z が並び、値はどれも 0.0 です。

proto の表示は、前後のダブルクォートまで含めて、そのまま、ros2 topic pub の、スラッシュ cmd_vel と geometry_msgs の msg の Twist の後ろに、貼り付けられる形です。値を書き換えてから送ればよい、とあります。

動いているトピックの型を調べるときは、ros2 topic type に、スラッシュとトピック名を付けて型の名前を出し、ros2 interface show に渡します。ros2 interface show に、マイナスを1つだけ付けると、型の名前を、前のコマンドから受け取ります。例は、ros2 topic type のスラッシュ chatter を、縦棒のパイプで、ros2 interface show のマイナスにつなぐものです。

## 5. 標準の型を使うか、自作するか

原文には、型の選び方の補足の囲みがあります。話は3つです。

1つ目は、一般的な考え方です。意味の合う標準の型があれば、それを使います。標準の型なら、rqt_plot、ros2 bag、RViz などのツールや、ほかの人のパッケージが、そのまま扱えます。意味の合う型が無いときに、自作します。std_msgs の Float64 や String のような、値を1つ包んだだけの型は、どの項目も data という名前で、中身の意味、つまり何の値か、単位は何かを伝えません。8節の common_interfaces のリポジトリにある std_msgs の説明でも、試作には便利だが、長く使う型としては勧めない、とされています。

2つ目は、この教材が Float64 を使った理由です。教材では、トピックとノードの仕組みを学ぶことを優先し、型は最も簡単なものにしました。目標速度、速度、ペダルを、別々の Float64 のトピックにしたので、rqt_plot で1本ずつ描けて、ros2 topic pub でも手で送りやすい。その代わり、値に時刻が無く、これは3-2節の話です。単位は、トピック名と手順書の説明に頼っています。

3つ目は、実務の目安です。決まった組でしか意味を持たない値、例えば、ある時刻の目標速度、速度、ペダルなどは、1つの自作の型にまとめ、Header で時刻を付け、コメントに単位を書きます。ほかの人やツールと共有する値は、標準の型を優先します。位置なら geometry_msgs、センサの値なら sensor_msgs です。

## 6. 自作する

ここでは、フェーズ5 の車両の値を題材に、メッセージ、サービス、アクションを、1つずつ定義します。フェーズ5 では、前後にだけ動く車両の速度を、目標速度に合わせて制御します。ペダルは、アクセルとブレーキの踏み込みを、1つの数で表した値で、範囲はマイナス1から1、正がアクセル、負がブレーキです。PI 制御のゲインは、目標との差からペダルを決めるときの強さを表す係数で、K の p と、K の i の2つです。

作るのは、次の3つです。どれも、手順書のノードでは使わない、練習用の型です。表は3列で、種類、型、中身です。3行あります。

1行目は、メッセージの VehicleState です。中身は、時刻、目標速度、速度、ペダルの組です。

2行目は、サービスの SetGains です。中身は、PI 制御のゲインを変える要求と、その結果です。

3行目は、アクションの DriveDistance です。中身は、決めた距離を走るゴール、かかった時間の結果、走った距離の途中経過です。

### 6-1. インターフェース専用のパッケージを作る

インターフェースは、ament_cmake のパッケージで定義します。コードを生成する仕組みが CMake で動くためで、Python だけで書くノードの型でも、ament_python のパッケージ、つまり learn_py には置けません。ノードのパッケージとは分けて、インターフェースだけのパッケージを作るのが一般的です。名前は、何々 _interfaces か、何々 _msgs にすることが多い、とあります。

手順は3つです。まず、ホームの ros2_ws の src に cd します。次に、ros2 pkg create で、ビルドの種類を ament_cmake、ライセンスを Apache-2.0、メンテナの名前を learner、メールをダミーのアドレスにして、learn_interfaces というパッケージを作ります。最後に、mkdir のマイナス p で、learn_interfaces の下に、msg、srv、action の3つのフォルダを作ります。

期待する結果は、ros2 pkg create の分で、パスは環境によって変わる、とあります。まず、新しいパッケージを作る、という1行が出て、続いて設定の内容の確認が並びます。パッケージの名前は learn_interfaces、作成先はホームの ros2_ws の src、パッケージの形式は3、メンテナは learner、ライセンスは Apache-2.0、ビルドの種類は ament_cmake、依存は空です。その後に、learn_interfaces のフォルダ、package.xml、src と include のフォルダ、CMakeLists.txt を作った、という行が並びます。

フェーズ4 の3-1節の learn_bringup と、同じ作り方です。mkdir は、成功しても何も表示しません。src と、include の下の learn_interfaces は、雛形が作る空のフォルダで、このパッケージでは使いません。

### 6-2. 定義ファイルを書く

1つ目のファイルは、ros2_ws の src の learn_interfaces の msg の、VehicleState.msg です。先頭のコメントに、車両の状態で、フェーズ5 の一式の、目標速度、速度、ペダルを、時刻付きの1つのメッセージにまとめたもの、とあります。続いて、ペダルの範囲の定数が2つあります。float64 の PEDAL_MAX が1.0、PEDAL_MIN がマイナス1.0 です。項目は4つです。std_msgs の Header 型の header で、コメントは、時刻と座標系の名前。float64 の target_velocity で、コメントは、目標速度、単位は毎秒のメートル。float64 の velocity で、コメントは、速度、単位は毎秒のメートル。float64 の pedal で、コメントは、ペダルで、PEDAL_MIN から PEDAL_MAX、正がアクセル、負がブレーキ、です。

2つ目のファイルは、srv の SetGains.srv です。先頭のコメントに、PI 制御のゲインを変える、要求にゲインを入れ、応答で受け付けたかを返す、とあります。マイナス3つの区切りの上の要求は、float64 の kp と ki です。下の応答は、bool の success と、string の message です。

3つ目のファイルは、action の DriveDistance.action です。先頭のコメントに、決めた距離を走る、ゴールに距離を、結果にかかった時間を、途中経過に走った距離を入れる、とあります。ゴールは、float64 の distance で、コメントは、走る距離、単位はメートル。結果は、float64 の elapsed_time で、コメントは、かかった時間、単位は秒。途中経過は、float64 の traveled で、コメントは、ここまでに走った距離、単位はメートルです。

説明は4つです。

1つ目。ファイル名は型名と同じにします。2-6節の決まりです。置くフォルダは、種類ごとに、msg、srv、action にします。

2つ目。VehicleState は、std_msgs の Header で時刻を持たせ、これは3-2節の話です。単位はコメントに書きました。これは3-3節の話です。ペダルの範囲は定数にしたので、使う側は、1.0 と書く代わりに、PEDAL_MAX と書けます。

3つ目。SetGains の応答は、std_srvs の srv の Trigger と同じ、success と message の組にしました。受け付けなかった理由、例えば負のゲインなどを、message で返せます。

4つ目。DriveDistance は、フェーズ6-2 で扱う、決めた距離まで走ったら終わる、を、アクションの形にしたものです。途中経過で走った距離を返せば、呼んだ側は、フェーズ6-2 の見張りのノード goal_monitor のログのように、進み具合を見られます。

### 6-3. CMakeLists.txt と package.xml に書き足す

ros2_ws の src の learn_interfaces の CMakeLists.txt の、ament_cmake を探す find_package の後ろ、ament_package より前に、10行ほどを足します。中身は、2つの find_package と、3つの定義ファイルを並べた rosidl_generate_interfaces と、ament_export_dependencies です。

同じフォルダの package.xml の、ament_cmake の buildtool_depend の次に、4つの要素を足します。buildtool_depend、depend、exec_depend、member_of_group です。

書き足した行を説明する表があります。表は2列で、書いたものと、何をしているか、です。7行あります。

1行目は、rosidl_default_generators を探す find_package に、REQUIRED を付けたものです。コードを生成する部品、つまり rosidl を探します。

2行目は、rosidl_generate_interfaces に、PROJECT_NAME の変数と、定義ファイルの並びを渡すものです。並べた定義ファイルから、このパッケージ名、つまり learn_interfaces で、Python と C++ のコードを作ります。定義ファイルを足したら、ここにも足します。

3行目は、DEPENDENCIES に std_msgs を書いたものです。定義ファイルの中で使っている、別のパッケージの型、つまり std_msgs の Header です。find_package と、package.xml の depend にも、同じものを書きます。

4行目は、ament_export_dependencies に rosidl_default_runtime を渡すものです。このパッケージを使う側にも、実行に要る部品を伝えます。

5行目は、buildtool_depend の rosidl_default_generators です。ビルドするときに、コードを生成する部品が要ります。

6行目は、exec_depend の rosidl_default_runtime です。実行するときに、生成したコードを動かす部品が要ります。

7行目は、member_of_group の rosidl_interface_packages です。このパッケージがインターフェースのパッケージであることを、ビルドの仕組みに知らせます。

アクションを定義しても、この資料を作ったときの環境では、アクション用の依存、つまり action_msgs を自分で足さなくても、ビルドできた、とあります。rosidl_default_generators が面倒を見ます。

### 6-4. ビルドして確かめる

コマンドは4つです。ホームの ros2_ws に cd し、colcon build に、マイナス2つの symlink-install と、マイナス2つの packages-select の learn_interfaces を付けてビルドします。source で install の setup.bash を読み込み、ros2 interface package に learn_interfaces を付けて実行し、最後に、ros2 interface show に、learn_interfaces の msg の VehicleState を付けて実行します。

期待する結果は3つです。

colcon build では、learn_interfaces の Starting の行と、秒数付きの Finished の行が出て、1つのパッケージが終わった、という Summary の行が出ます。

ros2 interface package では、learn_interfaces の、msg の VehicleState、action の DriveDistance、srv の SetGains の3行が並びます。

ros2 interface show では、6-2節で書いた VehicleState の定義が、コメントごと表示されます。そのうえで、header の下に、2-4節と同じく、stamp と、その中の sec と nanosec、そして frame_id が、字下げで出ます。

説明は3つです。

1つ目。定義ファイルは短いのですが、Python と C++ の両方のコードを生成するので、ビルドには、C++ のパッケージと同じくらいの時間がかかります。

2つ目。ros2 interface package に3つの型が並べば、生成できています。並ぶ順は、環境によって変わることがあります。

3つ目。ros2 interface show は、書いた定義ファイルをコメントごと表示し、入れ子の Header の中身も、字下げで出します。2-4節の話です。

### 6-5. 別のパッケージから使う

自作の型を使う側のパッケージ、つまり learn_py や learn_cpp などの package.xml に、依存を1行足します。ファイルは、ros2_ws の src の learn_py の package.xml で、learn_cpp から使う場合は、learn_cpp の package.xml です。足すのは、learn_interfaces の depend の1行です。

colcon build は、この依存を見て、learn_interfaces を先にビルドします。

Python では、標準の型と同じく import します。setup.py は変えなくてよい、とあります。まずは、ノードを書く前に、生成されたクラスを python3 から直接試せます。

コマンドは、python3 のマイナス c で、learn_interfaces.msg から VehicleState を import し、velocity を9.5、pedal を0.54 にして作ったメッセージを表示し、続けて VehicleState の PEDAL_MAX を表示するものです。

期待する結果は2行です。1行目は、learn_interfaces.msg の VehicleState の中身で、header、target_velocity、velocity、pedal の順に並びます。header の中には、stamp の sec と nanosec と、frame_id があります。velocity と pedal は、渡した値です。2行目は、PEDAL_MAX の値、つまり6-2節で決めた値です。

指定しなかった項目、つまり header と target_velocity は、既定の0や空の値で作られています。2-5節の話です。定数の PEDAL_MAX は、作ったメッセージではなく、型、つまりクラスから読めます。サービスとアクションは、from learn_interfaces.srv import SetGains と、from learn_interfaces.action import DriveDistance で読み込み、SetGains の Request に、kp が0.5、ki が0.1 を渡したり、DriveDistance の Goal に、distance が450.0 を渡したりして、要求やゴールを作ります。フェーズ3-4 と3-5 の、AddTwoInts の Request や、Fibonacci の Goal と同じ形です。

C++ では、ros2_ws の src の learn_cpp の CMakeLists.txt で、learn_interfaces を探す find_package に REQUIRED を付け、ament_target_dependencies に learn_interfaces を足します。フェーズ3-1 の4-2節で、talker に std_msgs を足したのと同じ形です。コードでは、ヘッダを include して、型名で使います。

原文には、ノードのソースに書く部分だけを抜き出した、使い方の例があります。ファイルの完全な形ではなく、include はファイルの先頭に、残りは、メッセージを作る関数の中に書く、とあります。4行ほどのコードで、include の1行と、VehicleState 型の変数の msg を作り、velocity に9.5 を入れ、pedal に値を入れる3行です。要の行は、pedal に、コロン2つでつないだ VehicleState の PEDAL_MAX、つまり型に付いた定数を入れる行です。

ヘッダのファイル名は、型名を小文字とアンダースコアに直したもので、VehicleState なら vehicle_state.hpp です。1-2節の話です。この書き方は、この資料を作ったときに、使い捨ての環境でビルドして確かめた、とあります。

任意の課題があります。フェーズ5-3 の一式を動かしながら、スラッシュ target_velocity、スラッシュ plant の velocity、スラッシュ plant の pedal の最新の値を覚えておき、1秒に10回、VehicleState にまとめて、スラッシュ vehicle_state へ送るノードを書きます。header の stamp には、self の get_clock の now の to_msg で、今の時刻を入れます。ros2 topic echo の、スラッシュ vehicle_state で、4つの値が1つのメッセージで届くことを確かめます。

### 6-6. つまずきやすい点

表は2列で、症状と、確認することです。7行あります。

1行目。ビルドで、Velocity は無効な項目名で、決まったパターンに合わせるべきだ、というエラーが出る。確認することは、項目の名前が小文字で始まっているかで、2-6節の話です。

2行目。ビルドで、vehicle_state は無効なメッセージ名で、決まったパターンに合わせるべきだ、というエラーが出る。確認することは、定義ファイルの名前が、VehicleState.msg のように、大文字で始まる型名になっているかです。

3行目。ビルドで、定義の中の、別のパッケージの型が見つからない。確認することは、find_package、DEPENDENCIES、package.xml の depend の3か所に、そのパッケージ、例えば std_msgs などを書いたかです。

4行目。定義ファイルを足したのに、ros2 interface package に出ない。確認することは、rosidl_generate_interfaces の並びに足したか、ビルドし直して、source で install の setup.bash を読み込んだかです。

5行目。Python で、learn_interfaces というモジュールが無い、というエラーが出る。確認することは、使う前に learn_interfaces をビルドして、source で install の setup.bash を読み込んだかです。

6行目。定義を変えた後、ノードどうしがつながらない。確認することは、使う側のパッケージもビルドし直したかです。古い定義のままのノードと、新しい定義のノードは、同じ名前の型でも中身が違うので、正しくやり取りできません。

7行目。ament_python のパッケージに msg のフォルダを作ったが、型が生成されない。確認することは、インターフェースは ament_cmake のパッケージでしか定義できない、ということで、6-1節の話です。

## 7. 教材のどこで何を使ったか

表は3列で、型、種類、使った手順書です。11行あります。

1行目は、std_msgs の msg の String で、メッセージです。フェーズ3-1 の talker と listener で使いました。

2行目は、std_msgs の msg の Float64 で、メッセージです。フェーズ3-1 の sine_pub と、5-1 から5-4、6-1 から6-3 の、目標速度、速度、ペダルで使いました。

3行目は、std_msgs の msg の Int32 で、メッセージです。フェーズ3-4 の counter_node で使いました。

4行目は、geometry_msgs の msg の Twist で、メッセージです。フェーズ1 の turtlesim、3-2a、5-0 の、車両への速度の指令で使いました。

5行目は、nav_msgs の msg の Odometry で、メッセージです。フェーズ5-0 と5-4 の、Gazebo の車両の位置と速度、そして6-2 の案 B で使いました。

6行目は、rosgraph_msgs の msg の Clock で、メッセージです。フェーズ5-4 の、シミュレーション時刻で使いました。

7行目は、example_interfaces の srv の AddTwoInts で、サービスです。フェーズ3-4 で使いました。

8行目は、std_srvs の srv の Trigger で、サービスです。フェーズ3-4 の counter_node で使いました。

9行目は、std_srvs の srv の Empty で、サービスです。フェーズ1 の、turtlesim のスラッシュ clear などで使いました。

10行目は、example_interfaces の action の Fibonacci で、アクションです。フェーズ3-5 で使いました。

11行目は、turtlesim の型、つまり Pose、Spawn、RotateAbsolute などで、3種類ともあります。フェーズ1 と3-2a で使いました。

教材で使ったメッセージの多くは、値を1つ包んだだけの std_msgs の型でした。その理由と、実務での選び方は、5節にまとめた、とあります。

## 8. 公式ドキュメントと参考資料

確認の状況が書かれています。2026年9月27日の時点で、公式のページは、GitHub にある原稿、つまり ros2 の ros2_documentation の jazzy のブランチが実在することを確かめた、とあります。docs.ros.org のページは、ボット対策で本文を取得できません。型の定義へのリンクは、raw.githubusercontent.com の同じパスが存在することを確かめました。REP 103 は、原稿の ros-infrastructure の rep が実在することを確かめた、とあります。

公式の資料は6つです。

1つ目は、Interfaces、ROS 2 Documentation の Jazzy で、定義ファイルの文法、基本の型、配列、既定値、定数です。

2つ目は、Creating custom msg and srv files、ROS 2 Documentation の Jazzy で、インターフェース専用のパッケージを作って使う方法です。

3つ目は、Implementing custom interfaces、ROS 2 Documentation の Jazzy で、同じパッケージの中で定義して使う方法です。

4つ目は、Creating an action、ROS 2 Documentation の Jazzy で、アクションの定義ファイルです。

5つ目は、GitHub の ros2 の common_interfaces の jazzy のブランチで、std_msgs、geometry_msgs、nav_msgs、sensor_msgs、std_srvs などの定義と、各パッケージの説明です。

6つ目は、REP 103、Standard Units of Measure and Coordinate Conventions で、単位と座標の向きの約束です。

原文の最後に、出典の注記があります。文法と型の対応は、公式ドキュメントと、手元の定義ファイル、生成済みのコード、rosidl_adapter から確かめ、自分の言葉でまとめたもの、とあります。公式ドキュメントのライセンスは、CC BY 4.0 です。期待する結果に載せた標準の型の定義は、ros2 interface show の表示で、定義の元は common_interfaces と rcl_interfaces、ライセンスは Apache License 2.0 です。自作の型の定義ファイル、サンプル、文章は、独自に書いたもの、とあります。

## 出典について

この原稿は、SanghunIm1991 さんの [ros2MinimalPhysicalAi の「参考資料: ROS2の標準のデータ型とインターフェース（自作する方法も）」](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/docs/reference_interfaces.md)を、聞くために要約・意訳したものです。図の [reference_interfaces_generate.svg](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/docs/img/reference_interfaces_generate.svg) は、言葉で説明しました。元にしたのは、[2026年10月17日の版](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/41d2c800082a372a810d286ded1bb56d9c05b67e/docs/reference_interfaces.md)です。原文の文章と図と同じく、[クリエイティブ・コモンズ 表示 4.0 国際ライセンス](https://creativecommons.org/licenses/by/4.0/deed.ja)で提供します。

原稿の中に原文の表記のまま書いたコマンドと、型・項目・関数の名前は、原文では [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0) の対象です。ライセンスの全文は、原文のリポジトリの [LICENSE-APACHE-2.0](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/LICENSE-APACHE-2.0) にあります。定義ファイルとコードは写さず、中身と役割を言葉で説明しました。

原文の期待する結果には、ROS2 の標準の型の定義を表示したもの（定義の元は common_interfaces と rcl_interfaces で、Apache License 2.0）があります。この原稿では、その表示は写さず、型と項目の名前と入れ子の形だけを言葉で説明しました。原文では、文法と型の対応は、公式ドキュメント（CC BY 4.0）と手元のファイルから確かめ、自分の言葉でまとめたもの、としています。
