<!--
聞くための原稿（読み上げでは読まれない記録）
原文: SanghunIm1991/ros2MinimalPhysicalAi の main ブランチの docs/interlude_urdf_rviz.md（図は docs/img/interlude_urdf_rviz_overview.svg）
原文のコミット: 331724d61c947ff6ef4324772abf207e102f3913（2026-10-17）
作成: 2026-10-23、Claude Code が手作業で作成（原稿化スキルはまだない）
原文のライセンス: 文章と図は CC BY 4.0、コマンドは Apache-2.0（それぞれ LICENSE の2と1）。cat・diff・grep・sed・xacro の表示として抜粋した URDF と xacro のファイルの中身（urdf_tutorial、David V. Lu!! ほか、BSD 3-Clause License）は、LICENSE の「第三者の著作物」にある。原文の末尾に、説明と表は公式チュートリアル（CC BY 4.0）の流れに沿って要点を独自にまとめ直したもの、10節は RobotCAD（LGPL-2.1-or-later）と FreeCAD の公開の情報から事実を自分の言葉でまとめたもの、ツールの表示は urdf_tutorial・urdf_launch・robot_state_publisher・joint_state_publisher・RViz2・tf2_ros・ros2cli・urdfdom（BSD License・Apache License 2.0）の出力、コマンドは公式チュートリアルの例と同等、とある。この原稿は、原文を聞くために要約・意訳したもの（改変あり）
方針: 英語の略語や製品名、要素やノードの名前、短いコマンドは原文の表記のまま書く。urdf_tutorial のファイルの中身（cat・diff・grep・sed・xacro の表示）は写さず、どの要素がどの値で、前のファイルから何が変わったかを、原文の解説に沿って言葉で説明した。ほかのツールの表示（apt・ls・check_urdf・--show-args・ログ・ros2 topic・tf2_echo・sha256sum）も写さず、何が表示されるかと原文の解説が使う値を言葉で説明した。この章には原文のリポジトリ自身のコードは無い。図と表（ファイルと公式チュートリアルの対応、関節の種類、つまずきやすい点）は言葉で説明する。文字数の上限は設けない
省いたもの: URL（FreeCAD のダウンロードの URL を含む）、型の定義へのリンク、apt list の版と日付、ログの時刻・プロセス番号・ログの置き場所のパス、stamp と At time の時刻、10節と12節に書かれた版の番号（RobotCAD・urdf_tutorial・urdf_launch・joint_state_publisher）、AppImage の大きさの MiB の値、RobotCAD が依存を入れる先のフォルダのパス、ドキュメントのリポジトリのブランチ名
-->

# 間章: URDF でロボットを記述し、RViz2 で見る（聞くための原稿）

これは、ros2MinimalPhysicalAi という教材の、フェーズ5 の補足の間章の話です。フェーズ5-4 までを読み終えた人向けの、任意の章です。フェーズ5 では、Gazebo に付属する2輪車を走らせ、速度の数字やグラフで動きを確かめてきました。車体や車輪の形は付属のファイルに書かれていて、どの部品がどこに付き、どの関節がどう回るのかを、ROS2 の側から見る場面はありませんでした。実際のロボットの開発では、ロボットの形と関節を1つのファイルに書き、関節の角度から各部品の位置を計算して、3D の画面で見ながら確かめる、という作業を何度も繰り返します。その標準の道具が、ロボットの記述の形式の URDF と、可視化のツールの RViz2 です。この章では、ROS2 の公式チュートリアルが使うパッケージ、urdf_tutorial を導入し、円柱1本から始めて、R2D2 に似たロボットができあがるまでの8つのファイルを順に開いて、URDF の書き方と、RViz2 に映るまでの仕組みを見ていきます。

想定する環境は、WSL2 と Ubuntu 24.04 と ROS2 Jazzy で、2節で urdf_tutorial のパッケージを追加で導入します。前提はフェーズ5-4 ですが、内容としては、フェーズ4 までのトピック、パラメータ、launch の使い方が分かれば読めます。フェーズ6 と7 の本文は、この章に依存しません。所要時間の目安は1から2コマです。用意されたファイルを開いて読み、コマンドで表示するだけで、コードやファイルは書きません。

この章の位置づけの囲みです。ROS 2 の公式チュートリアルの URDF の章のうち、urdf_tutorial を使う4本、つまり見た目を作る、関節を動かす、衝突と物理の性質、xacro の流れに沿った、読み物と小さな体験です。使うファイルは、どれも urdf_tutorial に入っているもので、自分では書きません。原文に載せたファイルの中身は、要点だけを抜粋したもので、全体は、各自の環境に導入したファイルか、GitHub の urdf_tutorial で読みます。説明は、公式チュートリアルを日本語に訳したものではなく、要点を自分の言葉でまとめ直したもの、とあります。

期待する結果の出どころの囲みもあります。apt list、ls、cat、diff、grep、sed、check_urdf、xacro、ros2 launch の --show-args の表示は、章を作るときに実際に実行した表示です。4-4節のトピックと TF の表示は、作るときに、display.launch.py が起動するノードのうち、RViz2 を除く robot_state_publisher と joint_state_publisher を、画面なしで起動して読んだ表示で、時刻は実行ごとに違います。スライダーのウィンドウを出す joint_state_publisher_gui も、ウィンドウを出さない設定で起動し、同じ関節の名前と角度を送ることを確かめてあります。3-1節の display.launch.py のログは、作るときに各ノードを画面なしで個別に起動したときのログから組み立てたもので、行の順番、時刻、pid は実行ごとに変わります。7-3節の表示は、3-1節と4-4節の表示から想定したもので、作るときには、この形で起動していません。RViz2 の画面は、作るときには開いて確かめていません。画面の見え方は、公式チュートリアルの説明と画面の例、urdf_tutorial の RViz2 の設定のファイルから、筆者が想定したものです。10節の RobotCAD の導入と使い方は、作るときには導入して確かめておらず、期待する結果は、RobotCAD と FreeCAD の公式の説明とソースから、筆者が想定したものです。

この原稿では、urdf_tutorial のファイルの中身や、ツールの表示を書き写さず、何が書かれ、何が表示されるかを、言葉で説明します。

## 0. この章で得てほしいこと

5つあります。

1つ目。URDF の基本の要素、つまり robot、link、joint、visual、origin、material を読み、リンクが関節で木の形につながることを説明できる。

2つ目。関節の原点、つまり joint の中の origin と、形の原点、つまり visual の中の origin の違いを説明できる。

3つ目。固定以外の関節の種類、つまり continuous、revolute、prismatic と、axis と limit の意味を説明できる。

4つ目。robot_state_publisher、joint_state_publisher、RViz2 が、トピック、つまり /robot_description、/joint_states、/tf、/tf_static でつながり、スライダーの角度が RViz2 の絵になるまでの流れを説明できる。

5つ目。衝突の形、つまり collision と、慣性、つまり inertial が何のためにあるかと、xacro の3つの仕組み、つまりプロパティ、式、マクロを説明できる。

完了の条件です。2節から6節の体験で、8つのファイルを順に表示し、ファイルの中身の違い、つまり diff の表示と、RViz2 の絵の違いを対応づけて説明できること。4節で、スライダーで動かした関節の角度が /joint_states に載り、robot_state_publisher が計算した TF で RViz2 の絵が動く流れを、トピックの表示で確かめられることです。

## 1. 全体像

ここに図が1枚あります。左端に、薄い灰色の箱が1つあり、URDF のファイル、01 から07 は拡張子が urdf、08 は urdf.xacro、と書いてあります。その右に、灰色の破線の大きな枠があり、見出しは、display.launch.py が起動する範囲、です。URDF のファイルの箱は、この枠の外にあります。

枠の中の上の段には、左から3つの箱が並びます。左は薄い青の箱で、xacro、展開して URDF の文字列にする。真ん中は薄い青の箱で、robot_state_publisher、関節の角度から TF を計算して配る。右は薄いオレンジ色の箱で、RViz2、RobotModel と TF で3D に表示する、と書いてあります。枠の中の下の段、robot_state_publisher の真下には、薄いオレンジ色の箱が1つあり、joint_state_publisher_gui、スライダーで角度、と書いてあります。

矢印は5本で、どれも実線です。

1本目は、左端の URDF のファイルから、xacro へ向かいます。

2本目は、xacro から robot_state_publisher へ、URDF の文字列、のラベルで向かいます。

3本目は、robot_state_publisher から RViz2 へ向かいます。ラベルは2行で、上が /robot_description、下が /tf と /tf_static です。

4本目は、robot_state_publisher から、下の joint_state_publisher_gui へ、/robot_description のラベルで下りる矢印です。

5本目は、その隣に並んで、joint_state_publisher_gui から robot_state_publisher へ、/joint_states のラベルで上がる矢印です。

まとめると、ファイルを xacro が文字列にし、robot_state_publisher が、URDF と TF を RViz2 に配り、URDF をスライダーのノードにも配り、スライダーのノードから角度を受け取る、という流れです。

この章で使う部品と仕組みは、次の5つです。

1つ目は、URDF、つまり Unified Robot Description Format です。ロボットの形と関節を書く、XML の書き方です。ロボットは、部品、つまりリンクを、関節でつないだ木の形として書きます。ROS2 の多くの道具、つまり RViz2、Gazebo、MoveIt、ros2_control が読める、共通の形式です。

2つ目は、robot_state_publisher です。URDF をパラメータ robot_description で受け取り、同じ中身をトピック /robot_description、型は std_msgs の msg の String に送っておくノードです。さらに、関節の角度、つまり /joint_states を受け取って、各リンクの位置と向きを計算し、TF として配ります。

3つ目は、TF です。ロボットの部品ごとの座標系、つまりフレームの間の、位置と向きの関係、つまり座標変換を、ROS2 の中で配る仕組み、tf2 です。動く関節の先のフレームはトピック /tf に、固定の関節の先のフレームは /tf_static に送られます。型は、どちらも tf2_msgs の msg の TFMessage です。

4つ目は、joint_state_publisher です。URDF から固定でない関節を探し、その角度を /joint_states、型は sensor_msgs の msg の JointState に送るノードです。GUI の版の joint_state_publisher_gui は、関節ごとのスライダーのウィンドウを出し、スライダーの値を送ります。実際のロボットや Gazebo では、関節の角度はセンサやシミュレータから届くので、このノードは、それが無いときに、手で角度を決めるための道具です。

5つ目は、RViz2 です。TF と、センサのデータ、ロボットのモデルなどを、3D の画面に重ねて描く、可視化のツールです。この章では、ロボットの形を描く表示の RobotModel と、フレームの軸を描く表示の TF を使います。

urdf_tutorial の display.launch.py は、指定した URDF のファイルを xacro で展開し、robot_state_publisher、joint_state_publisher_gui、RViz2 の3つを起動します。xacro は6節で扱います。展開する仕組みの無い URDF でも、そのまま通ります。この章では、ファイルを替えながら、この launch を何度も起動します。

## 2. 導入して、入ったものを確かめる

### 2-1. 導入する

urdf_tutorial は、apt で導入できます。依存するパッケージ、つまり表示用の launch をまとめた urdf_launch と、joint_state_publisher、joint_state_publisher_gui も、まとめて入ります。RViz2、robot_state_publisher、xacro は、環境構築で導入した ROS2 のデスクトップ版に入っています。

sudo apt update をしてから、sudo apt install に -y を付けて、ros-jazzy-urdf-tutorial を入れます。

期待する結果です。パスワードを入力すると、パッケージの一覧の更新と、ダウンロードと導入の表示が続き、エラーが出ずにプロンプトに戻ります。表示の中身は、PC の状態によって違います。

入ったことを、apt list に --installed を付けて、ros-jazzy-urdf で始まるものと、ros-jazzy-joint-state-publisher で始まるものを並べて確かめます。

期待する結果です。最初に、apt はスクリプトから使うと安定しない、という WARNING の行が出て、そのあと、導入済みのパッケージが並びます。ros-jazzy-joint-state-publisher-gui、ros-jazzy-joint-state-publisher、ros-jazzy-urdf-launch、ros-jazzy-urdf-parser-plugin、ros-jazzy-urdf-tutorial の5つで、それぞれ版の番号と、導入済みの印が付きます。版の番号は、導入した時期によって違います。

ros-jazzy-urdf-tutorial と、依存として自動で入ったことを示す印の付いた、joint_state_publisher、joint_state_publisher_gui、urdf_launch が並べば成功です。urdf_parser_plugin は、デスクトップ版に前から入っているもので、名前が urdf で始まるので、一緒に表示されます。先頭の WARNING は、apt をスクリプトから使うときの注意で、気にしなくてかまいません。

### 2-2. 入ったファイルを確かめる

パッケージのファイルは、ros2 pkg prefix に --share を付けたものが示すフォルダの下にあります。2つ目のターミナルを開き、そのフォルダの urdf に移ります。この章では、このターミナル2 でファイルを読み、1つ目のターミナル1 で launch を起動します。

ターミナル2 で、cd で、ros2 pkg prefix に --share と urdf_tutorial を付けた結果の、urdf のフォルダに移り、pwd と ls を実行します。

期待する結果です。pwd は、ROS2 のインストール先の share の、urdf_tutorial の urdf のフォルダを表示します。ls は、8つのファイルを表示します。01-myfirst.urdf、02-multipleshapes.urdf、03-origins.urdf、04-materials.urdf、05-visual.urdf、06-flexible.urdf、07-physics.urdf、08-macroed.urdf.xacro です。

8つのファイルは、番号の順に少しずつ書き足したもので、公式チュートリアルの4本に対応しています。この章の節の番号も、それに合わせてあります。

表は4列で、8行あります。列は、ファイル、内容、公式チュートリアル、この章の節です。

01-myfirst.urdf は、円柱1本です。公式チュートリアルは、見た目を作る、つまり Building a visual robot model from scratch で、この章の3-1節です。

02-multipleshapes.urdf は、箱を関節でつなぐもので、同じチュートリアル、3-2節です。

03-origins.urdf は、原点をずらして並べるもので、同じチュートリアル、3-3節です。

04-materials.urdf は、色を付けるもので、同じチュートリアル、3-4節です。

05-visual.urdf は、車輪、頭、つかむ手を足して仕上げるもので、同じチュートリアル、3-5節です。

06-flexible.urdf は、関節を動くようにするものです。公式チュートリアルは、関節を動かす、つまり Building a movable robot model で、この章の4節です。

07-physics.urdf は、衝突の形と慣性を足すものです。公式チュートリアルは、衝突と物理の性質、つまり Adding physical and collision properties で、この章の5節です。

08-macroed.urdf.xacro は、07 と同じロボットを、xacro で短く書くものです。公式チュートリアルは、xacro、つまり Using Xacro to clean up your code で、この章の6節です。

同じパッケージの meshes には、つかむ手の形のファイル、拡張子 dae が、rviz には、RViz2 の設定のファイル urdf.rviz が、launch には、表示用の display.launch.py が入っています。

### 2-3. launch の引数を確かめる

ターミナル1 で、ros2 launch urdf_tutorial display.launch.py に --show-args を付けて実行します。

期待する結果です。7つの引数が、説明と既定値付きで並びます。最初の3つは、gui、rvizconfig、model です。gui は、joint_state_publisher_gui を有効にするかどうかで、true か false、既定は true です。rvizconfig は、RViz2 の設定のファイルの絶対パスで、既定は、urdf_tutorial の share を探して、rviz と urdf.rviz をつなぐ置換の式です。model は、urdf_tutorial のパッケージからのロボットの URDF のファイルの相対パスで、既定値は、urdf と01-myfirst.urdf をつなぐ置換の式が、引用符に入った文字列として表示されます。後ろの4つは、jsp_gui、rviz_config、urdf_package、urdf_package_path です。

使うのは、上の3つ、つまり gui、rvizconfig、model です。後ろの4つは、中で取り込んでいる urdf_launch の display.launch.py の引数で、urdf_tutorial の側から値が渡されます。フェーズ5-3 の3-4節と同じく、--show-args は、取り込んだ launch の引数も並べます。

model は、表示するファイルの、urdf_tutorial のパッケージのフォルダからの相対パスで、たとえば urdf の01-myfirst.urdf です。gui は、true、つまり既定ならスライダーのウィンドウを出す joint_state_publisher_gui を、false ならウィンドウを出さない joint_state_publisher を起動します。rvizconfig は、RViz2 の設定のファイルで、既定は urdf_tutorial の rviz の urdf.rviz です。

model の既定値の表示は、urdf の01-myfirst.urdf ではなく、置換の式を書いた文字列になっています。これは、この launch の既定値の書き方の不具合で、model:= を省いて起動すると、この文字列がそのままファイルの名前として使われ、xacro が、No such file or directory、つまり、そのファイルやフォルダは無い、というエラーで失敗します。作るときに、同じ文字列を渡して確かめた、とあります。そのため、この章では、毎回 model:= を付けて起動します。

## 3. 見た目を作る、チュートリアル1

### 3-1. 円柱1本のロボット

まず、ターミナル2 で、cat で01-myfirst.urdf の中身を見ます。

期待する結果は、10行ほどの短い XML です。

その中身は、myfirst という名前のロボットに、base_link という名前のリンクが1つだけあり、リンクの見た目、visual の形、geometry は、長さ0.6メートル、半径0.2メートルの円柱、cylinder です。URDF の長さの単位はメートル、角度の単位はラジアンで、形には、円柱のほかに、箱の box、球の sphere、形のファイルの mesh があります。

URDF として正しく読めるかは、check_urdf で確かめられます。ターミナル2 で、check_urdf に01-myfirst.urdf を渡します。

期待する結果は3行です。ロボットの名前の行、Successfully Parsed XML の行、そして根のリンクの行です。Successfully Parsed XML、つまり XML の読み込みに成功した、が出れば、読めています。最後の行は、木の根のリンク、root Link が base_link で、子のリンクが0個であることを示します。

表示します。ターミナル1 で、ros2 launch urdf_tutorial display.launch.py に、model:= で urdf の01-myfirst.urdf を渡します。WSLg のウィンドウが2つ開きます。

期待する結果、ターミナル1 の表示です。各ノードを個別に起動したときのログから組み立てたもので、行の順番、時刻、pid は実行ごとに変わり、RViz2 のログの行は、PC のグラフィックスによって違います。launch のログの置き場所と、既定のログの詳しさの行のあと、robot_state_publisher-1、joint_state_publisher_gui-2、rviz2-3 の3つのプロセスが起動した、と出ます。続いて、robot_state_publisher が、ロボットを初期化した、つまり Robot initialized と出します。joint_state_publisher は、robot_description のトピックに URDF が送られるのを待っている、Centering、記述を受け取ったのでロボットを設定する、つまり Got description, configuring robot、もう一度 Centering、と出します。RViz2 は、ステレオ表示に対応していない、という行と、OpenGL の版の行を出します。

3つのノードが起動し、robot_state_publisher が Robot initialized、つまり URDF を読み込んだ、を出し、joint_state_publisher が Got description, configuring robot、つまり /robot_description から URDF を受け取って関節を探した、を出せば成功です。Centering は、スライダーを初期値に戻した、という表示です。初期値は0 で、範囲に0 が入らない関節では、範囲の中央です。4-4節で扱います。

画面では、2つのウィンドウが開きます。

1つ目は RViz2 です。中央の暗い色の3D の画面に、格子、つまり Grid と、その中心に立つ円柱が描かれます。円柱の形の原点は、既定では形の中心にあるので、円柱の下半分は、格子より下にあります。左の Displays の欄には、Global Options、Grid、RobotModel、TF が並びます。

2つ目は、Joint State Publisher、つまりスライダーのウィンドウです。このロボットには動く関節が無いので、スライダーは無く、Randomize と Center のボタンだけがあります。4節で使います。

RViz2 の画面の読み方の要点は、次の5つです。画面の例は、公式チュートリアルの、見た目を作るページにあります。

1つ目は、Global Options の中の Fixed Frame です。3D の画面の基準にするフレームで、格子の中心が、このフレームの原点になります。urdf.rviz では base_link に設定されています。基準は本来、世界に対して動かないフレーム、たとえば地図の map などを選ぶものですが、この章のロボットは床の上を走らないので、ロボットの根のリンクを基準にしています。

2つ目は RobotModel です。Description Topic の欄の /robot_description の URDF と、TF から、ロボットの形を描く表示です。urdf.rviz では、少し透けるように、不透明度、つまり Alpha を0.8 にしています。

3つ目は TF です。フレームごとに、赤、緑、青の矢印、つまり x、y、z 軸と、名前を描く表示です。リンクが1つなら、base_link の軸だけが描かれます。

4つ目は、マウスの操作です。左ボタンでドラッグすると視点が回り、中ボタン、つまりホイールを押してドラッグすると視点の中心が動き、ホイールを回すか、右ボタンでドラッグすると、近づいたり遠ざかったりします。

5つ目。表示の名前の左の三角を開くと、設定の項目が並びます。問題があると、Status の項目に、Warning や Error と、その理由が出ます。

確かめたら、ターミナル1 で Ctrl+C を押して止めます。2つのウィンドウも閉じます。以降の節も、表示を確かめたら同じように止めてから、次のファイルを起動します。

### 3-2. 箱を関節でつなぐ

1つ前のファイルとの違いを、diff で見ます。小なりの記号の行が前のファイル、大なりの記号の行が後のファイルの中身です。ターミナル2 で、diff に01-myfirst.urdf と02-multipleshapes.urdf を渡します。

期待する結果は、2行目の robot の名前が変わったことと、9行目の後ろに14行ほどが足されたことの表示です。

ロボットの名前、つまり multipleshapes のほかに、2つの要素が足されています。

1つ目は、リンクの right_leg、つまり右脚です。形は、0.6メートル、0.1メートル、0.2メートルの箱で、box の size の属性に、x、y、z の順に書きます。

2つ目は、関節の base_to_right_leg です。親、つまり parent の base_link に、子、つまり child の right_leg をつなぐ、固定、つまり type が fixed の関節です。

URDF では、リンクを並べただけでは、どこに置くかが決まりません。リンクは必ず関節で親につなぎ、子のリンクの位置は、親のリンクの位置を基準に決まります。親は1つだけで、根のリンクも1つだけなので、ロボット全体は、根から枝分かれする木の形になります。輪になったつながりは書けません。

ターミナル1 で、model:= を urdf の02-multipleshapes.urdf にして、display.launch.py を起動します。

期待する結果です。ターミナル1 には、3-1節と同じ形のログが出ます。RViz2 では、円柱と、横に寝た箱が、重なって描かれます。関節にも形にも位置を指定していないので、2つのリンクの原点が同じ場所、つまり base_link の原点にあり、重なってしまいます。

### 3-3. 原点をずらして並べる

ターミナル2 で、diff に02-multipleshapes.urdf と03-origins.urdf を渡します。

期待する結果は、robot の名前が origins に変わったことと、origin の行が2か所に足されたことの表示です。

origin、つまり原点が2か所に足されています。1つ目、16行目は right_leg の visual の中、2つ目、23行目は関節 base_to_right_leg の中です。xyz は位置、メートルで、rpy は向き、つまり x 軸、y 軸、z 軸のまわりの回転、ロール、ピッチ、ヨーのラジアンです。この2つは、意味が違います。

関節の原点、つまり joint の中の origin は、子のリンクのフレームを、親のリンクのフレームのどこに置くか、を決めます。ここでは、base_link から、y 方向にマイナス0.22メートル、つまりロボットの右側、z 方向に0.25メートル、つまり上の位置に、right_leg のフレームの原点を置きます。rpy を書いていないので、向きは親と同じです。

形の原点、つまり visual の中の origin は、リンクのフレームの中で、形の中心をどこに置くか、を決めます。ここでは、箱の中心を、right_leg のフレームの原点から0.3メートル下げ、y 軸のまわりに1.57075ラジアン、つまりほぼ2分の パイ、90度回して、長い辺を縦にしています。こうすると、脚の上端が、フレームの原点、つまり関節の位置に来ます。

関節の原点は TF、つまりフレームの位置関係を決め、形の原点は、そのフレームの中での絵の置き方だけを決めます。

ターミナル1 で、model:= を urdf の03-origins.urdf にして起動します。

期待する結果です。RViz2 では、円柱の右上の横に、縦長の箱が、上端を付けてぶら下がって描かれます。TF の表示では、base_link の軸のほかに、少し右上、つまり関節の位置に right_leg の軸が描かれます。脚の箱は、軸の位置から下に伸びています。

### 3-4. 色を付ける

ターミナル2 で、diff に03-origins.urdf と04-materials.urdf を渡します。

期待する結果は、robot の名前が materials に変わったことと、いくつかの行のまとまりが足されたことの表示です。

足されたものは3つです。

1つ目。robot のすぐ下に、名前を付けた色、つまり material を2つ定義しています。color の rgba は、赤、緑、青、不透明度の4つの値で、それぞれ0 から1 です。blue は青だけが0.8、white は全部1 です。

2つ目。各リンクの visual の中の、material の name で、定義した色を名前で使います。円柱は青、脚は白になります。色は、visual の中で直接定義してもかまいません。

3つ目。左脚、つまり left_leg も足しています。右脚と同じ形で、関節の原点の y だけが、プラス0.22メートル、つまりロボットの左側になっています。

ターミナル1 で、model:= を urdf の04-materials.urdf にして起動します。

期待する結果です。RViz2 では、青い円柱の左右に、白い脚が1本ずつぶら下がって描かれます。RobotModel の不透明度が0.8 なので、少し透けて見えます。

### 3-5. 仕上げる

05 では、足先の台、車輪、つかむ手、頭を足して、ロボットを仕上げています。ファイルは245行あり、diff の表示も長いので、新しく出てくる形だけを探します。ターミナル2 で、grep に -n と -E を付けて、05-visual.urdf から sphere か mesh を含む行を探します。

期待する結果は、行番号付きの5行です。

頭、つまり220行目は、半径0.2メートルの球、sphere です。

つかむ手の指、つまり170行目、184行目、198行目、212行目は、形のファイル、mesh で描き、l_finger.dae と l_finger_tip.dae を使います。package のあとにコロンとスラッシュ2つを付けて、urdf_tutorial の meshes の下のファイルを指す書き方は、パッケージ urdf_tutorial のフォルダの下の meshes、という意味で、PC ごとにインストール先が違っても、同じ URDF で読めます。左右の指は同じファイルを使い、右の指、つまり right_gripper と right_tip は、visual の形の原点の rpy を、マイナス3.1415、0、0 にして、x 軸のまわりに半回転させ、左右対称に置いています。grep に -n と、手前の4行も出す -B4 を付けて、l_finger を探すと、各指の origin を見られます。

木の形は、check_urdf で見られます。ターミナル2 で、check_urdf に05-visual.urdf を渡します。

期待する結果は、ロボットの名前の行と Successfully Parsed XML の行のあと、根のリンクから始まる木の形が、字下げで並ぶ表示です。

根の base_link、つまり胴体に、4つの枝、つまり左脚、右脚、つかむ手の棒の gripper_pole、頭の head がつながり、脚の先には、足先の台、つまり名前が base で終わるリンクと、前後の車輪、棒の先には、左右の指と指先、つまり名前が tip で終わるリンク、頭には目の箱、box がつながっています。リンクは全部で16個あります。

ターミナル1 で、model:= を urdf の05-visual.urdf にして起動します。

期待する結果です。RViz2 では、R2D2 に似たロボット、つまり青い胴体、白い球の頭、左右の脚と黒い車輪、前に伸びた棒の先の指が描かれます。TF の表示では、16個のリンクのフレームの軸と名前が、重なって並びます。多すぎて読みにくい場合は、7-1節の方法、つまり TF の表示の Show Names と Show Axes のチェックを外す方法で減らせます。関節はまだすべて固定なので、スライダーのウィンドウには、スライダーがありません。

## 4. 関節を動かす、チュートリアル2

### 4-1. 関節の種類

URDF の関節は、type で動き方を決めます。

表は3列で、6行あります。列は、type、動き方、必要な要素です。

fixed は、動きません。3節のすべての関節がこれです。必要な要素はありません。

continuous は、軸のまわりに、制限なく回ります。車輪などです。必要な要素は axis です。

revolute は、軸のまわりに、決めた範囲だけ回ります。腕や指などです。必要な要素は、axis と limit で、範囲はラジアンです。

prismatic は、軸の向きに、決めた範囲だけ伸び縮みします。伸びる腕などです。必要な要素は、axis と limit で、範囲はメートルです。

planar は、平面の中を動き、2つの値で決まります。必要な要素は axis で、平面に垂直な向きを書きます。

floating は、空間の中を自由に動き、6つの値で決まります。必要な要素はありません。

planar と floating は、1つの数で位置が決まらないので、公式チュートリアルでは扱っていません。joint_state_publisher も、スライダーを作りません。

axis の xyz は、回る、または伸び縮みする向きのベクトルで、関節のフレーム、つまり関節の原点に置かれた、子のリンクのフレームで表します。書かなければ、x 軸、つまり1、0、0 になります。limit の lower と upper は動ける範囲、velocity と effort は、速さと力の上限です。速さと力の上限は、RViz2 での表示には使われませんが、revolute と prismatic では、書く決まりになっています。

### 4-2. 関節を動くようにした違い

05 と06 の違いは、関節の部分だけで、diff の表示は44行です。後半を見ます。ターミナル2 で、diff に05-visual.urdf と06-flexible.urdf を渡します。

期待する結果の抜粋です。関節ごとに、type が fixed の行が、別の type の行に置き換わり、axis や limit の行が足されています。抜粋の前には、残りの3つの車輪の関節が、同じ形で並びます。抜粋に出てくるのは、left_back_wheel_joint が continuous になって y 軸の axis が足されたこと、gripper_extension が prismatic になって、下限マイナス0.38、上限0 の limit が足されたこと、left_gripper_joint と right_gripper_joint が revolute になって、それぞれ z 軸と、マイナスの z 軸の axis と、下限0.0、上限0.548 の limit が足されたこと、head_swivel が continuous になって z 軸の axis が足されたこと、です。

8つの関節が、固定から動く関節に変わっています。

4つの車輪、つまり名前が wheel_joint で終わる関節は、y 軸、つまり0、1、0 の車軸の向きのまわりに回る continuous です。axis に rpy の属性も書かれていますが、これは、URDF の仕様、つまり参考資料の urdf の XML のページの axis には無い属性で、向きは xyz だけで決まります。

頭、つまり head_swivel は、z 軸、つまり0、0、1 の上向きのまわりに回る continuous です。首を振るように回ります。

つかむ手の棒、つまり gripper_extension は prismatic です。axis を書いていないので、x 軸、つまり前向きの向きに、マイナス0.38 から0 メートルの範囲で引っ込みます。

左右の指、つまり left_gripper_joint と right_gripper_joint は revolute です。0 から0.548ラジアン、つまり約31度の範囲で開きます。軸の向きが左右で逆、つまり0、0、1 と、0、0、マイナス1 なので、同じ角度で、左右対称に開きます。

### 4-3. スライダーで動かす

ターミナル1 で、model:= を urdf の06-flexible.urdf にして起動します。

期待する結果です。ターミナル1 には、3-1節と同じ形のログが出ます。RViz2 には、3-5節と同じロボットが描かれます。スライダーのウィンドウには、固定でない8つの関節のスライダーが並び、どれも0 の位置にあります。

動かし方は3つです。

1つ目。スライダーを動かすと、RViz2 のロボットの、その関節の先が動きます。head_swivel なら頭と目の箱が回り、gripper_extension なら棒と指が胴体の中へ引っ込み、left_gripper_joint なら左の指が開きます。

2つ目。車輪と頭、つまり continuous のスライダーは、マイナス パイ から パイ、つまり約マイナス3.14 から3.14 の範囲です。制限の無い関節でも、スライダーには範囲が要るので、1回転分にしています。

3つ目。Randomize を押すと、すべてのスライダーが、範囲の中のでたらめな値になり、Center を押すと、初期値に戻ります。

### 4-4. 裏側をトピックで見る

スライダーの値が RViz2 の絵になるまでを、トピックで確かめます。ターミナル1 の launch は動かしたまま、ターミナル2 で、ros2 topic list に -t を付けて実行します。

期待する結果です。6つのトピックが、型付きで並びます。/joint_states が sensor_msgs の JointState、/parameter_events が rcl_interfaces の ParameterEvent、/robot_description が std_msgs の String、/rosout が rcl_interfaces の Log、/tf と /tf_static が tf2_msgs の TFMessage です。

1節の図の4つのトピック、つまり /joint_states、/robot_description、/tf、/tf_static が並びます。残りの2つは、どのノードにもある標準のトピックです。RViz2 の設定によっては、RViz2 が送るトピックが加わることがあります。

続けて、ターミナル2 で、ros2 topic echo の /joint_states に --once を付けて実行します。

期待する結果、スライダーを動かす前の表示です。header の stamp は送った時刻で、実行ごとに違い、frame_id は空です。name には、right_front_wheel_joint、right_back_wheel_joint、left_front_wheel_joint、left_back_wheel_joint、gripper_extension、left_gripper_joint、right_gripper_joint、head_swivel の8つが並び、position には、8つとも0.0 が並びます。velocity と effort は、空の並びです。

name に、固定でない8つの関節の名前が、position に、同じ順で角度が並びます。prismatic の gripper_extension だけは、角度でなく長さです。スライダーを動かしてから、もう一度実行すると、動かした関節の値が変わっています。joint_state_publisher は、URDF から固定でない関節を探し、それぞれの初期値を0、範囲に0 が入らない関節は範囲の中央にして、1秒に10回、つまりパラメータ rate の既定値の回数で送ります。

robot_state_publisher は、この角度と、URDF の関節の原点と軸から、各リンクのフレームの位置と向きを計算して、TF として送ります。2つのフレームの間の関係は、tf2_echo で読めます。ここでは、胴体、つまり base_link から見た、左の指、つまり left_gripper のフレームを読みます。ターミナル2 で、ros2 run tf2_ros tf2_echo に、base_link と left_gripper を渡します。

期待する結果、スライダーをすべて0 にしたときの表示です。最初の数行は、Waiting for transform、つまり base_link から left_gripper への変換を待っている、と、frame does not exist、つまり base_link というフレームは存在しない、という表示です。そのあと、時刻の行に続いて、Translation、つまり位置が、0.390、0.010、0.200 と表示され、Rotation、つまり向きは、クォータニオンで0、0、0、1、ロール、ピッチ、ヨーで、ラジアンでも度でもすべて0 と表示されます。最後に、4行4列の変換の行列が表示されます。止めるまで、1秒ごとに同じ形の表示が続きます。

最初の数行の、Waiting for transform と frame does not exist の表示は、tf2_echo が起動した直後で、まだ TF を1つも受け取っていない、という意味で、すぐに消えます。その後の Translation が位置、メートルで、Rotation が向きです。左の指のフレームは、胴体から見て、前に0.39メートル、左に0.01メートル、上に0.2メートルにあります。これは、URDF の2つの関節の原点の足し算、つまり gripper_extension の、0.19、0、0.2 と、left_gripper_joint の、0.2、0.01、0 の足し算になっています。これは、4-2節の diff の表示の外の行です。

スライダーで gripper_extension をマイナス0.38 にすると、Translation の x が0.39 から0.01 に減り、left_gripper_joint を開くと、Rotation のロール、ピッチ、ヨーのうち、ヨー、つまり3つ目が増えるはずです。これは URDF の関節の軸と範囲から考えた値で、作るときには、スライダーを動かして確かめていない、とあります。止めるときは、ターミナル2 で Ctrl+C を押します。

TF が2つのトピックに分かれているのは、送る回数を減らすためです。固定の関節の先のフレーム、つまり脚、足先の台、指先、目の箱の関係は変わらないので、robot_state_publisher は、/tf_static に一度だけ送り、後から購読したノードにも届く設定、つまり QoS の transient_local にしています。動く関節の先のフレーム、つまり車輪、頭、棒、指の関係は、/joint_states を受け取るたびに計算し直して、/tf に送ります。

## 5. 衝突と物理の性質、チュートリアル3

07 では、06 のロボットの16個のリンクのすべてに、衝突の形、collision と、慣性、inertial を足しています。RViz2 での見た目は06 と同じで、この2つは、物理シミュレーション、たとえば Gazebo や、動きの計画、たとえば MoveIt で、物どうしがぶつかるかを調べたり、力から動きを計算したりするために使います。

ターミナル2 で、grep の -c で、07-physics.urdf の中の collision の始まりのタグと、inertial の始まりのタグの数を数えます。期待する結果は、どちらも16 です。

胴体、つまり base_link の部分を、sed の -n で、07-physics.urdf の14行目から30行目を表示して見ます。

期待する結果です。base_link の link の中に、visual、collision、inertial の3つのまとまりがあります。visual と collision は、どちらも3-1節と同じ長さ0.6、半径0.2 の円柱で、inertial は、質量10 と、対角の3つが0.001、対角の外の3つが0 の慣性モーメントです。

### 5-1. 衝突の形

collision は、visual と同じ階層に書き、形の geometry と、原点の origin の書き方も、visual と同じです。多くの場合は、見た目と同じ形にしますが、あえて変えることもあります。理由は2つです。

1つ目は、計算を軽くするためです。細かな形のファイル、mesh どうしがぶつかるかの計算は重いので、衝突の形には、円柱、箱、球などの単純な形を使います。

2つ目は、近づけたくない範囲を作るためです。壊れやすい部品のまわりに、見た目より大きな衝突の形を置いておくと、動きを計画する道具が、その範囲に物を近づけないようにします。

RViz2 では、RobotModel の表示の項目の、Collision Enabled にチェックを入れると衝突の形が描かれ、Visual Enabled のチェックを外すと見た目が描かれなくなるので、2つを見比べられます。

### 5-2. 慣性

inertial には、リンクの質量、つまり mass、キログラムと、回しにくさ、つまり慣性モーメント、inertia を書きます。慣性モーメントは、3行3列の対称な行列なので、対角の3つ、ixx、iyy、izz と、対角の外の3つ、ixy、ixz、iyz の6つで表します。origin を書くと、重心の位置と、慣性モーメントを表すフレームの向きを、リンクのフレームからずらせます。

公式チュートリアルは、慣性モーメントの値の決め方について、3つの目安を挙げています。

1つ目。円柱、箱、球のような単純な形なら、質量が中に均一に散らばっていると考えて、形ごとの式で計算できます。複雑な形なら、形を作ったソフトウェアで計算できることが多いです。

2つ目。分からないときの仮の値として、中くらいのリンクなら、対角の3つを0.001 以下にするとよい、とあります。これは、1辺0.1メートル、質量0.6キログラムの箱に当たります。対角を1 にする、つまり単位行列は、ずっと大きすぎて、同じ大きさの箱で質量600キログラムに当たるので、よくありません。

3つ目。慣性を0 や、0 に近い値にすると、シミュレーションで、ロボットの形が崩れることがあります。

07 の値は、この仮の値、0.001 を、すべてのリンクに使ったもので、物理として正しい値ではありません。たとえば胴体を、質量10キログラム、半径0.2メートル、長さ0.6メートルの均一な円柱と考えると、横の軸のまわりの慣性モーメントは次のように求まります。3 かける0.2 の2乗に、0.6 の2乗を足すと0.48、それに10 を掛けて12 で割ると0.4キログラム平方メートルで、0.001 の400倍になります。これは筆者の計算です。RViz2 での表示には慣性は使われないので、このチュートリアルでは、形をそろえることを優先しています。シミュレーションに使うときは、形と質量から計算した値に直します。

### 5-3. 接触と関節の動きの性質

公式チュートリアルは、さらに2つの要素を紹介しています。どちらも07 のファイルには書かれていません。

1つ目は、接触の係数です。collision の中の contact_coefficients の属性で、摩擦係数の mu、硬さの kp、減衰の kd を書きます。

2つ目は、関節の動きの性質です。joint の中の dynamics の属性で、静止摩擦の friction と、減衰の damping を書きます。単位は、prismatic なら、ニュートンと、メートル毎秒あたりのニュートン、回る関節なら、ニュートンメートルと、ラジアン毎秒あたりのニュートンメートルです。書かなければ0 になります。

ターミナル1 で、model:= を urdf の07-physics.urdf にして起動し、5-1節の Collision Enabled と Visual Enabled を切り替えてみます。

期待する結果です。RViz2 には、06 と同じロボットが描かれ、スライダーも06 と同じ8つが並びます。Collision Enabled にチェックを入れると、見た目と同じ位置に、衝突の形が重なって描かれます。07 の衝突の形は、ほとんどが見た目と同じ形で、指は、形のファイルと同じものを使っています。grep に -n と、後ろの3行も出す -A3 を付けて、07-physics.urdf の collision の始まりのタグを探すと、各リンクの衝突の形を見られます。

## 6. xacro で短く書く、チュートリアル4

### 6-1. xacro の3つの仕組み

07 は417行あり、同じ形の脚、車輪、指を、名前と位置だけ変えて、何度も書いています。脚の長さを変えたくなったら、脚の形、関節の位置、足先の台の位置を、左右で何か所も直すことになります。xacro、つまり XML Macros は、URDF に、次の3つの仕組みを足した書き方で、xacro のコマンドで、ふつうの URDF に展開してから使います。08 は、07 と同じロボットを、xacro で237行に書いたものです。

1つ目はプロパティ、つまり名前を付けた値です。xacro の property の要素で、name と value を書いて定義し、ドル記号と中かっこで名前を囲んで使います。

2つ目は式です。ドル記号と中かっこの中で、四則演算、符号の反転、かっこと、サインやコサインなどの関数、円周率の pi を使えます。

3つ目はマクロ、つまり部品のひな形です。xacro の macro の要素で、name と params を書いて定義し、xacro の、そのマクロの名前の要素に引数を書くと、中身が展開されます。引数は、プロパティと同じく、ドル記号と中かっこで使います。

xacro のファイルは、先頭の robot に、xacro の名前空間、つまり xmlns の xacro の属性を書く決まりになっています。

ターミナル2 で、sed の -n で、08-macroed.urdf.xacro の4行目から9行目と、23行目から28行目を表示します。

期待する結果は、前半の6行の、xacro の property の並びと、後半の6行の、default_inertial という名前の xacro の macro です。

前半は、寸法の6つのプロパティで、胴体の半径の width が0.2、脚の長さの leglen が0.6 などです。後半の default_inertial は、5-2節の仮の慣性を、質量だけを引数にして書くマクロで、各リンクの中で、xacro の default_inertial の要素に、mass を10 のように書いて使います。

脚は、1本分をマクロ leg にまとめ、左右で2回使っています。ターミナル2 で、sed の -n で、08-macroed.urdf.xacro の90行目から94行目と、119行目から120行目を表示します。

期待する結果は、前半の5行の、leg のマクロの中の関節の部分と、後半の2行の、マクロを使う行です。後半の2行は、xacro の leg の要素に、prefix を right、reflect をマイナス1 と書いた行と、prefix を left、reflect を1 と書いた行です。

ここに、xacro のよく使う工夫が3つあります。

1つ目は、名前の頭に引数を付けることです。base_to_ に prefix を付けた名前は、prefix が right なら base_to_right_leg になります。同じ形の部品に、別々の名前を付けられます。

2つ目は、位置を寸法から計算することです。関節の y の位置を、胴体の半径に0.02メートルを足した値、つまり width プラス0.02 で計算しています。胴体を太くすれば、脚の位置も、自動で外へずれます。

3つ目は、左右を符号で切り替えることです。reflect を、マイナス1、つまり右と、1、つまり左にして掛けると、同じマクロで、左右対称の位置に置けます。

### 6-2. 展開して確かめる

xacro のコマンドで展開すると、ふつうの URDF が表示されます。脚の関節の部分を探します。ターミナル2 で、xacro に08-macroed.urdf.xacro を渡し、その出力から、grep に後ろの4行も出す -A4 を付けて、名前が base_to_ で始まり _leg で終わる joint を探します。

期待する結果は、base_to_right_leg と base_to_left_leg の2つの関節の表示です。

reflect かける、width プラス0.02 の式が、右でマイナス0.22、左で0.22 に計算され、3-4節の04、そして07 の脚の関節と同じ値になっています。展開した結果の木の形、つまり check_urdf の表示も、3-5節の05 と同じ16個のリンクになります。

check_urdf は xacro を展開しないので、xacro のファイルを直接渡すと失敗します。ターミナル2 で、check_urdf に08-macroed.urdf.xacro を直接渡してみます。

期待する結果です。Error として、length に入っている、ドル記号と中かっこで bodylen を囲んだ文字列は is not a valid float、つまり正しい小数ではない、という行と、それが urdf_parser のソースの link.cpp の何行目で見つかったかの行が出て、さらに、Could not parse visual element、つまり base_link のリンクの visual の要素を読めなかった、という Error が出ます。

bodylen の式が、数でないまま読まれています。xacro のファイルを点検するときは、xacro で展開した結果をファイルに書き出してから、check_urdf に渡します。たとえば、xacro の出力をホームの macroed.urdf に書き出してから、check_urdf にそのファイルを渡します。

### 6-3. 表示する

ターミナル1 で、model:= を urdf の08-macroed.urdf.xacro にして起動します。

期待する結果です。RViz2 には07 と同じロボットが描かれ、スライダーも同じ8つが並びます。display.launch.py は、01 から07 のときも、毎回ファイルを xacro に通してから robot_state_publisher に渡していました。1節の図のとおりです。xacro の仕組みを使っていないファイルは、展開しても中身が変わらないので、違いが見えなかっただけです。

## 7. RViz2 の表示を変える

### 7-1. 表示の項目を変える

06 から08 のどれかを表示した状態で、RViz2 の左の Displays の欄の項目を変えると、表示の働きが分かります。3つの操作があります。

1つ目は、TF の名前と軸を減らすことです。TF の表示の三角を開き、Show Names のチェックを外すと名前が、Show Axes のチェックを外すと軸が消えます。Frames の中では、フレームごとに表示を切り替えられます。

2つ目は、Fixed Frame を変えることです。Global Options の Fixed Frame を、base_link から head に変えて、スライダーで head_swivel を動かします。今度は、頭が止まって見え、胴体と脚のほうが回ります。Fixed Frame は画面の基準なので、基準にしたフレームが動かないように描かれます。

3つ目は、表示を足すことです。左下の Add を押すと、足せる表示の種類の一覧が出ます。センサの点群、カメラの画像、地図などです。この章のロボットにはセンサが無いので、ここでは一覧を眺めるだけでかまいません。

変えた設定は、メニューの File の Save Config As で、別の名前の設定のファイルに保存でき、次から、rviz2 に -d とそのファイルを渡すか、display.launch.py の引数 rvizconfig:= に、そのファイルの絶対パスを渡して開けます。urdf_tutorial の urdf.rviz は、書き換えません。パッケージのファイルは、更新のときに上書きされるからです。

### 7-2. RViz2 だけを開いた場合

display.launch.py を使わずに、設定のファイルを指定せずに rviz2 だけを起動すると、自分で保存した既定の設定、つまりホームの .rviz2 フォルダの default.rviz が無い場合は、rviz_common に付属の default.rviz で開き、Fixed Frame は map になっています。このロボットの TF には map のフレームが無いので、Global Status に、Fixed Frame が無い、という意味のエラーが出ます。ロボットを描くには、次の2つが要ります。

1つ目。Fixed Frame を、ロボットにあるフレーム、たとえば base_link に変えます。

2つ目。Add で RobotModel を足し、その Description Topic を /robot_description にします。足した直後の値は、作るときには確かめていない、とあります。空なら選びます。

urdf_tutorial の urdf.rviz は、この2つを設定済みの、設定のファイルです。

### 7-3. 自分の URDF を表示する場合

display.launch.py の model は、urdf_tutorial のパッケージのフォルダからの相対パスなので、ホームのフォルダなどに置いた自分のファイルは渡せません。その場合は、1節の図の3つのノードを、別々のターミナルで起動すればよい、とあります。

ターミナル1 では、ros2 run robot_state_publisher robot_state_publisher に、--ros-args と、-p で robot_description に、自分のファイルを xacro で展開した結果をその場で渡して起動します。ターミナル2 では、ros2 run joint_state_publisher_gui joint_state_publisher_gui を起動します。ターミナル3 では、rviz2 に -d で、urdf_tutorial の share の rviz の urdf.rviz を渡して起動します。

ドル記号とかっこで xacro のコマンドを囲むのはシェルの書き方で、展開した結果の文字列を、その場でパラメータに渡します。joint_state_publisher_gui は、robot_state_publisher が送る /robot_description を受け取って、スライダーを作ります。4-4節のとおりです。RViz2 の設定は urdf_tutorial のものを借りているので、Fixed Frame は base_link になります。根のリンクの名前が違う場合は、7-1節の方法で Fixed Frame を変えます。

期待する結果です。ターミナル1 に Robot initialized、ターミナル2 に Got description, configuring robot が出て、3-1節と同じ2つのウィンドウが開き、RViz2 に、自分のロボットが描かれます。止めるときは、ターミナル3、2、1 の順に Ctrl+C で止めます。

## 8. この章のまとめ

まとめは6つです。

1つ目。URDF は、ロボットを、リンク、つまり link を、関節、つまり joint でつないだ木の形として書きます。根のリンクは1つで、子のリンクの位置は、親のリンクのフレームを基準に、関節の原点、つまり origin で決まります。

2つ目。リンクの見た目、visual は、形、つまり円柱、箱、球、形のファイルと、リンクのフレームの中での形の原点と、色、つまり material で書きます。関節の原点は TF を決め、形の原点は、絵の置き方だけを決めます。

3つ目。動く関節は、continuous、つまり制限なく回る、revolute、つまり範囲を決めて回る、prismatic、つまり範囲を決めて伸び縮みする、の3つで、軸の axis と、範囲の limit を書きます。

4つ目。robot_state_publisher は、URDF を /robot_description に配り、/joint_states の角度から各リンクのフレームを計算して、固定の関節の先は /tf_static に一度、動く関節の先は /tf に繰り返し送ります。joint_state_publisher_gui は、スライダーの値を /joint_states に送ります。RViz2 は、URDF と TF から、Fixed Frame を基準に、ロボットを描きます。

5つ目。衝突の形、collision と、慣性、inertial は、シミュレーションや動きの計画に使います。衝突の形は単純な形にすることが多く、慣性は、形と質量から計算した値を書きます。チュートリアルの0.001 は仮の値です。

6つ目。xacro は、プロパティ、式、マクロで、URDF の繰り返しを減らします。xacro のコマンドで、ふつうの URDF に展開してから使い、display.launch.py も、毎回 xacro を通しています。

## 9. つまずきやすい点

2列の表で、10行あります。列は、症状と、確かめることです。

1行目。display.launch.py が、置換の式を書いた名前について No such file or directory、つまりファイルやフォルダは無い、というエラーで失敗する場合。model:= を付け忘れています。2-3節のとおりです。model:= を urdf の01-myfirst.urdf のように、毎回付けます。

2行目。model:= は付けたのに、display.launch.py が、ファイルが無いというエラーで失敗する場合。model は、urdf_tutorial のパッケージのフォルダからの相対パスで、urdf から書きます。ファイル名の番号とつづり、たとえば06-flexible.urdf などが合っているかを確かめます。自分のファイルは渡せません。7-3節のとおりです。

3行目。Package 'urdf_tutorial' not found、つまりパッケージ urdf_tutorial が見つからない、と出る場合。2-1節の導入が済んでいるか、導入した後に開いたターミナルかを確かめます。開いたままのターミナルでは、source で /opt/ros/jazzy の setup.bash を読み込み直します。

4行目。RViz2 の画面にロボットが出ない、または Global Status がエラーの場合。Fixed Frame が、ロボットにあるフレーム、たとえば base_link かを確かめます。7-2節のとおりです。RobotModel の Description Topic が /robot_description か、ターミナル1 に Robot initialized が出ているかも確かめます。

5行目。一部のリンクだけ、原点に重なって描かれ、RobotModel の Status に、No transform from、つまり、そのリンクからの変換が無い、と出る場合。そのリンクの先の、動く関節の角度が届いていません。joint_state_publisher_gui、または joint_state_publisher が動いているか、ros2 topic echo の /joint_states に --once を付けて、その関節の名前が載っているかを確かめます。4-4節のとおりです。

6行目。スライダーのウィンドウにスライダーが無い場合。表示しているファイルの関節が、すべて固定、つまり fixed かを確かめます。01 から05 は固定だけなので、スライダーはありません。3-5節のとおりです。06 より後を表示します。

7行目。check_urdf が、is not a valid float、つまり正しい小数ではない、というエラーで失敗する場合。xacro のファイルを直接渡しています。xacro で展開してから渡します。6-2節のとおりです。

8行目。FreeCAD の AppImage が起動せず、libfuse.so.2 が見つからない、というエラーが出る場合。10-3節の (1) の libfuse2t64 を入れたかを確かめます。

9行目。RobotCAD を選んでも、一部の道具が使えない、足りないパッケージが表示される場合。10-3節の (6) の Check and install dependencies で、足りないパッケージを入れたかを確かめます。

10行目。RViz2 の画面が真っ黒のまま、またはすぐに落ちる場合。WSLg で、OpenGL の描画がうまくいっていないことがあります。ターミナル1 で、export LIBGL_ALWAYS_SOFTWARE=1 を実行してから起動すると、GPU を使わずにソフトウェアで描くので、遅くはなりますが、表示されることがあります。

## 10. 参考: CAD の画面で URDF を作る、RobotCAD

この章では、用意された URDF を読んで表示しました。自分のロボットを作るときも、小さなうちは、テキストのエディタで URDF や xacro を書けば足ります。ところが、部品が増え、形が複雑になると、関節の原点の座標を数字で合わせるのも、形と質量から慣性を計算するのも、手では大変になります。そこで、CAD の画面で部品を組み立て、そこから URDF を書き出す道具が使われます。

ROS 2 の公式の文書には、こうした書き出しの道具の一覧、つまり Exporting an URDF File のページがあります。Blender 用の Phobos、FreeCAD 用の RobotCAD、Fusion 360 用、Onshape 用、SolidWorks 用の道具などが並んでいます。どれもコミュニティが作ったもので、ROS 2 の開発者は保守しておらず、品質も保証していない、と同じ文書に注意書きがあります。この節では、その中から、無料の CAD の FreeCAD で動き、ROS 2 のパッケージまで作る RobotCAD を紹介します。

この節の扱いの囲みです。参考の紹介で、この章の体験には含めません。この節の内容は、2026年10月17日の時点の、RobotCAD と FreeCAD の公式の説明とソースから筆者がまとめたもので、作るときには導入して確かめていません。期待する結果も、それらから想定したものです。道具の更新は速いので、導入する前に、参考資料の RobotCAD の README で、最新の手順を確かめます。

### 10-1. RobotCAD でできること

RobotCAD は、FreeCAD に足して使う作業の画面、つまりワークベンチです。FreeCAD で ROS 用の記述を作る CROSS から分かれた、つまりフォークしたもので、ROS 2 向けの機能が足されています。ライセンスは LGPL-2.1-or-later です。主にできることは、次の4つです。

1つ目。FreeCAD で作った部品を選んで、リンクと関節を作り、リンクの親子と、関節の原点を画面で決めます。この章の link、joint、origin にあたります。

2つ目。材料を割り当てて、質量、慣性、重心を自動で計算します。5-2節で、手で書くのが大変だと述べた inertial を、形から求められます。

3つ目。部品の外形を囲む箱、球、円柱から、衝突の形、つまり5-1節のものを作ります。

4つ目。Export to URDF で、ROS 2 のパッケージを書き出します。RobotCAD のソースの記述から、パッケージの名前は、_description で終えるものと想定されている、とあります。パッケージには、URDF、つまり xacro と、形のファイルの meshes、RViz2 の設定、Gazebo のワールドと、launch の display.launch.py、gazebo.launch.py などの launch が入ります。

書き出したパッケージの表示の仕組みは、この章と同じです。launch が robot_state_publisher に URDF を渡し、関節の角度から TF を計算し、RViz2 がそれを描きます。1節の図のとおりです。

### 10-2. 導入する前に確かめること

確かめることは5つです。

1つ目はセキュリティで、次の4つの点を踏まえて、導入するかどうかを決めます。まず、RobotCAD は、コミュニティが作った第三者のプログラムで、FreeCAD の中で動きます。FreeCAD も RobotCAD も、自分のユーザーの権限で動き、ホームのフォルダの下のファイルを読み書きできます。次に、アドオンの管理画面から入れると、その時点の main ブランチの最新のコードが入ります。版は固定されず、この節が前提にした版と同じとは限りません。さらに、初めて使うときに、足りない Python のパッケージ、たとえば xacro、urdf_parser_py、mujoco などを、PyPI からダウンロードして入れます。入る先は、FreeCAD の専用のフォルダで、システムの Python や ROS 2 の環境には入りません。これは RobotCAD のソースの記述からの話です。これらのパッケージも、自分の権限で動きます。最後に、10-3節の (1) は、sudo で管理者の権限を使って、Ubuntu のパッケージを入れる操作です。

2つ目は大きさです。FreeCAD の実行ファイル、つまり AppImage は、1つで約820メガバイトあります。

3つ目は画面です。FreeCAD は画面のあるアプリなので、WSL2 では、WSLg でウィンドウが開きます。3-1節の RViz2 と同じです。

4つ目は、CROSS とは同時に使えないことです。CROSS を入れている場合は、先に外します。これは RobotCAD の README の注意です。

5つ目は、FreeCAD の版です。RobotCAD の README は、FreeCAD の1.1系の AppImage を勧めているので、この節ではそれを使います。AppImage は、インストールせずに、ファイル1つで動く形式です。1.1系の AppImage の中の Python は3.11 で、ファイル名の py311 がそれを表します。README には、FreeCAD の中の Python は3.12 以上、という記述もありますが、アドオンの定義、つまり package.xml の下限は3.11 なので、この節では3.11 の版を使います。別の Python の版の AppImage を選ぶと、上の依存の入る先のフォルダの名前の末尾の py311 も変わります。

### 10-3. 導入の手順

手順は6つです。

(1) AppImage を動かすための部品を入れます。AppImage は、FUSE 2 というファイルシステムの仕組みを使います。Ubuntu 24.04 では、そのライブラリが libfuse2t64 という名前になっています。sudo apt update をしてから、sudo apt install に -y を付けて、libfuse2t64 を入れます。期待する結果は、apt の表示の最後に、エラーが出ずに終わることです。すでに入っていれば、それが最新の版だ、と出ます。

(2) FreeCAD の AppImage と、そのチェックサムを取ってきます。置き場所は、ホームの apps のフォルダとします。ファイルの名前と版は、FreeCAD の GitHub のリリースのページで、最新の安定版を確かめてから書き換えます。mkdir -p で apps を作って移り、wget で、FreeCAD の GitHub のリリースから、1.1.4 の、Linux の x86_64 の py311 の AppImage と、その SHA256 のチェックサムのファイルを取ってきて、sha256sum の -c で、チェックサムのファイルを使って確かめます。

期待する結果、sha256sum の分です。AppImage のファイル名のあとに、OK と出ます。OK と出れば、ダウンロードの途中でファイルが壊れていません。ただし、チェックサムも同じリリースのページから取っているので、配布元でファイルがすり替えられた場合までは、見分けられません。FAILED と出た場合は、ファイルを消して取り直し、それでも合わなければ使いません。

(3) 実行できるようにして、起動します。chmod +x で AppImage に実行の権限を付け、AppImage のパスを打って起動します。期待する結果は、FreeCAD のウィンドウが開くことです。起動したターミナルは、FreeCAD を閉じるまで戻りません。

(4) RobotCAD のリポジトリを、アドオンの管理画面に登録します。FreeCAD のメニューの Edit、Preferences で設定の画面を開き、Addon Manager の設定の Custom repositories の欄のプラスを押して、2つを書きます。リポジトリの URL として、GitHub の drfenixion の freecad.robotcad と、ブランチの main です。

(5) RobotCAD を入れます。メニューの Tools、Addon Manager で、アドオンの管理画面を開き、RobotCAD を探して Install を押します。入ったら、FreeCAD を閉じて、(3) の2つ目のコマンドで起動し直します。

(6) 足りない Python のパッケージを入れます。作業の画面の一覧、つまりツールバーの、ワークベンチを選ぶ欄で、RobotCAD を選びます。足りないパッケージがあると、そのことが表示されます。About RobotCAD、つまり RobotCAD のメニューかツールバーにある項目から、Check and install dependencies を開き、Install missing を押します。この操作で、10-2節のとおり、PyPI からパッケージがダウンロードされます。

(4) から (6) の期待する結果です。画面の操作なので、ターミナルに載せる表示はありません。依存の画面に、パッケージごとに installed と出て、最後に、すべての依存が入った、つまり All dependencies are installed と出れば、使える状態になっています。メニューの名前は英語の画面のもので、FreeCAD を日本語の画面で使っている場合は、日本語の名前になります。

### 10-4. 使い方の流れと、ROS 2 での確かめ方

RobotCAD の Wiki の、Common usage plan の流れを、この章の言葉でまとめると、次の5つの段階になります。画面の操作の詳しい説明は、参考資料の Wiki を見ます。

1つ目。FreeCAD の部品の設計の画面、つまり PartDesign で、部品の形を作ります。関節を置く場所には、部品の中に座標系、つまり LCS、Local Coordinate System を置いておきます。ほかの CAD で作った形を読み込んでもかまいません。

2つ目。RobotCAD の画面で、ロボット、つまり Robot を作り、リンクと関節を作ります。リンクには、実際の形、Real と、見た目、Visual の部品を割り当てます。

3つ目。関節ごとに、親と子のリンクを決め、関節の原点を、1つ目で置いた座標系に合わせます。3-3節の、関節の原点を決めることにあたります。

4つ目。衝突の形を作り、つまり5-1節、材料を割り当てて、Calculate mass and inertia で、質量と慣性を計算します。つまり5-2節です。形を変えたら、計算し直します。

5つ目。Robot のプロパティの Output Path、つまり OutputPath に、書き出す先を書きます。ワークスペースの src からの相対パス、たとえば my_robot_description で書きます。ソースの説明では、ワークスペースの中の絶対パスも受け付け、src からの相対パスに直します。ワークスペースがまだ決まっていないと、ワークスペースのフォルダ、つまりホームの ros2_ws を選ぶ画面が出ます。これもソースの記述からの話です。Robot を選んで Export to URDF を押すと、ros2_ws の src の my_robot_description に、パッケージが書き出されます。

書き出したパッケージは、ふだんのパッケージと同じく、ワークスペースでビルドして使います。FreeCAD を起動したターミナルとは、別のターミナルで行います。my_robot_description は、5つ目で決めたパッケージの名前に読み替えます。ros2_ws に移り、colcon build に --packages-select my_robot_description を付けてビルドし、source install/setup.bash をしてから、ros2 launch my_robot_description display.launch.py に --show-args を付けて実行します。

期待する結果です。colcon build の最後に、my_robot_description が終わった、という行が出て、--show-args に、use_sim_time、gui、既定は True、model、rvizconfig の4つの引数が出ます。2-3節と同じく、引数の名前、説明、既定値が並びます。引数は、RobotCAD が書き出す launch のひな形のソースから想定した、とあります。引数を確かめたら、--show-args を外して起動します。RViz2 のウィンドウが開き、CAD で組み立てたロボットが描かれます。gui が True のときは、joint_state_publisher_gui も起動するので、動く関節があれば、3-1節と同じスライダーのウィンドウも開きます。

## 11. 次へ

この章は任意の補足なので、本筋はフェーズ6-1 へ進みます。

## 12. 公式のドキュメントと参考資料

確かめた状況は、2026年10月16日の時点です。公式チュートリアルの4本と、RViz のユーザーガイドは、公式のドキュメントのソースで本文を確かめました。urdf_tutorial、urdf_launch、joint_state_publisher は、作るときに導入し、入ったファイルが、GitHub の同じ版と同じであることを確かめました。display.launch.py の構成と引数、model の既定値の不具合、joint_state_publisher の初期値、送る回数、continuous のスライダーの範囲は、ソースを読み、画面なしで起動して確かめました。RViz2 の表示の項目の名前、たとえば Description Topic、Collision Enabled、Show Names などは、導入した RViz2 のプラグインに含まれる文字列で確かめましたが、画面は開いていません。RViz2 の画面の見え方と、スライダーのウィンドウの見た目、7-2節の RobotModel を足した直後の Description Topic の値、7-3節の3つのノードを別々に起動する手順、9節の RViz2 の描画の不具合の対処は、作るときには確かめていない、とあります。10節の RobotCAD は、README と Wiki、アドオンの定義、つまり package.xml、依存を入れる処理、書き出しの処理と launch のひな形のソースを、2026年10月17日に読んで確かめました。FreeCAD 1.1.4 の AppImage の名前と大きさ、チェックサムのファイルの形は、GitHub のリリースで確かめました。書き出しの道具の一覧のページは、公式のドキュメントのソースで、RobotCAD が載っていることと、保守についての注意を確かめました。導入と画面の操作は、作るときには確かめていない、とあります。

公式の資料は12項目あります。ROS 2 Jazzy の、URDF で見た目のロボットのモデルを一から作るチュートリアル、つまり3節で、形、原点、色を扱い、RViz2 の画面の例があります。動くロボットのモデルを作るチュートリアル、つまり4節で、関節の種類とスライダーを扱います。物理と衝突の性質を足すチュートリアル、つまり5節で、衝突の形、慣性、接触の係数、関節の動きの性質を扱います。xacro でコードを整理するチュートリアル、つまり6節で、プロパティ、式、マクロを扱います。Python で URDF を robot_state_publisher と使うチュートリアルは、自分のパッケージに URDF を置き、ノードから関節の角度を送って動かすもので、この章では扱っていません。RViz のユーザーガイドは、RViz2 の画面、表示の足し方、Fixed Frame、視点の操作を扱います。tf2 の紹介のチュートリアルは、TF の考え方と、tf2_echo などの道具を扱います。ROS Wiki の urdf の XML のページは、URDF の要素の仕様で、ROS1 の時代の文書ですが、ROS 2 でも同じ書き方を使います。GitHub の ros の urdf_tutorial は、この章で使ったファイルの全体です。GitHub の ros の urdf_launch は、display.launch.py が取り込む表示用の launch です。GitHub の ros の joint_state_publisher は、joint_state_publisher と joint_state_publisher_gui のソースです。そして、Exporting an URDF File のページは、10節で使った、CAD などから URDF を書き出す道具の一覧で、ROS 2 の開発者は保守していない旨の注意があります。

RobotCAD の資料は、コミュニティのもので公式ではない、として、4項目あります。GitHub の drfenixion の freecad.robotcad は、README に、導入の方法、つまりアドオンの管理画面、Docker、Conda と、機能の一覧があり、ライセンスは LGPL-2.1-or-later です。RobotCAD の Wiki は、Common usage plan に、部品の用意から書き出しまでの流れがあります。GitHub の galou の freecad.cross は、RobotCAD の元になった CROSS です。FreeCAD 1.1.4 のリリースのページは、AppImage とチェックサムのファイルがあるページで、最新の版はリリースの一覧で確かめます。

原文の最後には、出典の注記があります。この章の説明と表は、公式チュートリアルの流れに沿って、要点を独自にまとめ直したもので、転載ではありません。公式チュートリアルは CC BY 4.0 です。10節は、RobotCAD の README、Wiki、ソースと、FreeCAD のリリースのページから、事実を自分の言葉でまとめたもので、文章もコードも転載していません。RobotCAD のライセンスは LGPL-2.1-or-later です。メニューと画面の文字は、操作のために名前だけを書いた、とあります。コマンドは、公式チュートリアルの例と同等のものです。cat、diff、grep、sed、xacro の表示として載せた URDF と xacro のファイルの中身は、urdf_tutorial のファイルの一部を抜粋したものです。urdf_tutorial は David V. Lu!! ほかのもので、ライセンスは BSD 3-Clause License です。--show-args の表示は urdf_tutorial と urdf_launch の出力で、ライセンスは BSD 3-Clause License です。ノードのログとトピック、TF の表示は、robot_state_publisher と joint_state_publisher の出力で BSD License、RViz2 と tf2_ros と ros2cli の出力で BSD License と Apache License 2.0 です。check_urdf の表示は urdfdom の出力で、BSD License です。

以上で、URDF と RViz2 の間章の話を終わります。

## 出典について

この原稿は、SanghunIm1991 さんの [ros2MinimalPhysicalAi の「間章: URDFでロボットを記述し、RViz2で見る（フェーズ5の補足）」](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/docs/interlude_urdf_rviz.md)を、聞くために要約・意訳したものです。図の [interlude_urdf_rviz_overview.svg](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/docs/img/interlude_urdf_rviz_overview.svg) は、言葉で説明しました。元にしたのは、[2026年10月17日の版](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/331724d61c947ff6ef4324772abf207e102f3913/docs/interlude_urdf_rviz.md)です。原文の文章と図と同じく、[クリエイティブ・コモンズ 表示 4.0 国際ライセンス](https://creativecommons.org/licenses/by/4.0/deed.ja)で提供します。

原稿の中に原文の表記のまま書いたコマンドは、原文では [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0) の対象で、原文では、コマンドは公式チュートリアルの例と同等だとしています。ライセンスの全文は、原文のリポジトリの [LICENSE-APACHE-2.0](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/LICENSE-APACHE-2.0) にあります。この章には、原文のリポジトリ自身のコードはありません。

原文の期待する結果に抜粋された URDF と xacro のファイルの中身は、[urdf_tutorial](https://github.com/ros/urdf_tutorial)（David V. Lu!! ほか、BSD 3-Clause License）のものです。この原稿では、それを写さず、どの要素がどの値で、何が変わったかを言葉で説明しました。ほかの表示の例も、各ツールの表示を言葉で説明したものです。ツールのライセンスは、check_urdf の urdfdom と、robot_state_publisher・joint_state_publisher が BSD License、RViz2・tf2_ros・ros2cli が BSD License と Apache License 2.0 です。原文では、説明の流れを [ROS 2 Documentation](https://docs.ros.org/en/jazzy/)（Open Robotics、CC BY 4.0）の公式チュートリアルに沿ってまとめ直し、コマンドはその例と同等だとしています。10節の [RobotCAD](https://github.com/drfenixion/freecad.robotcad)（LGPL-2.1-or-later）と FreeCAD は、公開の情報から事実をまとめたものです。
