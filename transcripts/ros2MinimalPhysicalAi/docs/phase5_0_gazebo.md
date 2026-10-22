<!--
聞くための原稿（読み上げでは読まれない記録）
原文: SanghunIm1991/ros2MinimalPhysicalAi の main ブランチの docs/phase5_0_gazebo.md（図は docs/img/phase5_0_bridge.svg、画面は docs/img/phase5_0_gazebo.png）
原文のコミット: 132df7b64d48d560def7ec7149f7003938d3d8e5（2026-10-14）
作成: 2026-10-21、Claude Code が手作業で作成（原稿化スキルはまだない）
原文のライセンス: 文章と図は CC BY 4.0、コードとコマンドは Apache-2.0（それぞれ LICENSE の2と1）。冒頭の画面に写る Gazebo Sim の画面と、付属のワールド diff_drive.sdf の中身は、LICENSE の「第三者の著作物」にある（Open Source Robotics Foundation、Apache License 2.0）。原文の末尾に、導入のコマンドは Gazebo の公式ドキュメントの手順と同等のもの、デモの構成と設定値は導入したパッケージのファイルを読んで自分の言葉でまとめたもの、とある。この原稿は、原文を聞くために要約・意訳したもの（改変あり）
方針: 英語の略語や製品名、関数やクラスの名前、短いコマンドは原文の表記のまま書く。サンプルコード gz_drive.py と、package.xml・setup.py に足す行は、写さずに、ブロックの役割と要の行を言葉で説明した。期待する結果（apt、ros2 pkg list、gz sim --version、gz topic -l、ros2 launch の --show-args と --print、ブリッジのログ、ros2 topic の各表示、gz service の表示）も、何が表示されるかを言葉で説明した。画面のスクリーンショットと図と表（入れるパッケージ、2台の車両、Odometry の読み方、主な API、疑似プラントとの比較、つまずきやすい点）は言葉で説明する。文字数の上限は設けない
省いたもの: URL、型の定義へのリンク、ログの時刻とアドレスの数字、Gazebo の版の細かな数字、ワールドファイルのフルパス、ビルドにかかった秒数、作成に使った PC での RTF の値（作業環境の記述のため）、日本語の記事の名前
-->

# フェーズ5-0: Gazebo を導入し、用意されたロボットを ROS2 から動かす（聞くための原稿）

これは、ros2MinimalPhysicalAi という教材の、フェーズ5-0 の手順書の話です。学習計画のフェーズ5 の冒頭、元のアイデアのステップ5 にあたります。3D の物理シミュレータの Gazebo、版は Harmonic を導入し、公式のデモ集の ros_gz_sim_demos に入っている2輪の車両を、ROS2 のトピックで走らせます。フェーズ5-1 から後で自作する車両の速度の制御を、物理シミュレータの車両で、先に体験しておく位置づけです。

原文の冒頭には、Gazebo の画面のスクリーンショットがあります。2-1節の gz sim diff_drive.sdf で開く画面で、再生のボタンを押す前の、一時停止の状態です。ウィンドウの題名は Gazebo Sim です。左上に、箱、球、円柱などの形を置くボタンと、選択、移動、回転などのボタンが2段に並びます。画面の大部分は、格子の線が引かれた灰色の地面で、手前に車両が2台、左右に並んでいます。左が青紫の車両、右が緑の車両で、どちらも細長い直方体の車体の両側に、黒い球のような車輪が付いています。右側には縦長の欄があり、上半分は World の設定の一覧で、物理エンジンや、ワールドの名前の diff_drive などが並びます。下半分は Entity Tree、つまりワールドに置かれたものの一覧で、ワールド自身の default の下に、ground_plane、vehicle_blue、vehicle_green、sun が並びます。左下には、オレンジ色の丸い再生のボタンなどが並び、右下には、RTF の値、0.00 パーセントが出ています。この2台の車両を、Gazebo のコマンドと、ROS2 のトピック、5節では自作のノードで走らせます。

想定する環境は、WSL2 と Ubuntu 24.04 と ROS2 Jazzy です。前提は、フェーズ1、つまり ros2 topic pub で Twist を送れることと、フェーズ3-1、つまり Publisher を書けて、ros2_ws の src に learn_py があることです。launch ファイルは起動するだけで、フェーズ4 で学ぶ書き方は知らなくてかまいません。1節から3節だけなら、フェーズ1 の後に寄り道として試せます。所要時間の目安は1から2コマです。導入と観察は言語によらず、自作のノードは Python です。

原文の進め方の囲みです。前半の1節から4節は、Gazebo を導入し、用意されたデモをコマンドだけで動かして、仕組みを観察します。後半の5節で、フェーズ3-1 の Publisher を応用した小さなノードを書いて、車両を走らせます。サンプルは学習の手がかりとして最小限に書いたもので、公式のチュートリアルの転載ではありません。コードは手順書を作るときにビルドと import まで確かめ、手順は2026年9月26日に実機で確かめてあります。出力が細部で違うときは、実機の表示を優先します。

フェーズ1 の後に寄り道して試す場合の囲みもあります。Gazebo で車両が動く様子を早く見てみたい場合は、フェーズ1 を終えた時点で、この手順書の1節から3節だけを試してかまいません。目的は動くものを楽しむことで、仕組みを完全に理解することは求めません。注意は5つです。

1つ目。1節の導入と、2節の、Gazebo だけで開いて青の車両を走らせるところは、そのまま進められます。

2つ目。3節では、launch ファイル、つまり複数のプログラムをまとめて起動する設定のファイルが出てきます。書き方はフェーズ4 で学びます。ブリッジ、つまり Gazebo のトピックと ROS2 のトピックを中継するプログラムは、2節の図のとおりです。分からないところは読み流してよく、3-1節の --show-args と --print は飛ばして、3-2節のターミナル1 のコマンドから始めてもかまいません。そのコマンドの rviz:=false は、重い可視化のツール、RViz2 を一緒に開かないための指定です。

3つ目。3-3節の ros2 topic pub と、3-4節の ros2 topic echo は、フェーズ1 で turtlesim に使ったのと同じコマンドです。値を変えて、車両の動きがどう変わるかを試してみるとよい、とあります。

4つ目。4節と5節は、ワークスペースと Publisher の書き方が要るので、まだ行いません。フェーズ2 と3-1 で学びます。フェーズ3-1 を終えた後で、この手順書に戻り、改めて通して進めます。1節の導入は済んでいるので、2節からです。4-2節の QoS の相性は、フェーズ3-2b で詳しく学びます。

5つ目。試し終えたら、ターミナル1 で Ctrl+C を押してデモを止め、フェーズ2 へ進みます。Gazebo のウィンドウを閉じただけでは、ブリッジが止まりません。これは8節の表にあります。

期待する結果の出どころの囲みです。冒頭の画面は、2-1節の手順を実機で実行して撮ったものです。導入の確かめ、Gazebo のトピックの一覧、launch の引数と展開の結果、ブリッジのトピックの情報は、実機で確かめた表示です。5-4節のビルドの表示は、使い捨ての環境で確かめた表示の形です。それ以外、つまりインストール中の表示と、Gazebo やノードを起動した後の表示は、デモの設定ファイルと ROS2 の仕様から筆者が想定したもので、Gazebo やノードを起動した後の表示は、実機で実行して確かめてあります。時刻や数値の細部は、実行ごとに違います。

この原稿では、サンプルコードを書き写さず、ブロックの役割と要の行を言葉で説明します。

## 0. 学習目標と完了の条件

学習目標は4つです。

1つ目。Gazebo の Harmonic と、ROS2 と連携するパッケージ ros_gz を導入し、ROS2 の版と Gazebo の版の対応を説明できる。

2つ目。ros_gz_sim_demos の2輪車のデモを起動し、ros2 topic pub で車両を走らせられる。

3つ目。Gazebo の側のトピックと ROS2 の側のトピックは別の仕組みで、ros_gz_bridge が型を変換して橋渡ししていることを説明できる。

4つ目。フェーズ3-1 の Publisher を応用した自作のノードで車両を走らせ、オドメトリ、つまり車輪の回転から推定した位置と速度を購読して観察できる。

完了の条件は、5節の自作のノード gz_drive で緑の車両を走らせ、ログに出る速度が指令の値に近づくこと、そして、ノードを止めても車両が走り続ける理由を、4-3節に沿って説明できることです。

## 1. Gazebo の導入

### 1-1. どの Gazebo を入れるか

Gazebo には、古くからの Gazebo Classic と、その後継の新しい Gazebo があります。新しい方は、以前は Ignition と呼ばれていた系統です。Gazebo Classic はサポートが終わる系統なので、この教材では新しい Gazebo を使います。

新しい Gazebo には、Harmonic、Ionic などの名前の付いた版があります。ROS2 の版ごとに、勧められる組み合わせが決まっていて、ROS2 Jazzy には Gazebo Harmonic が勧められています。Jazzy からは、Gazebo が ROS2 の apt のリポジトリから、vendor パッケージ、つまり ROS2 の配布物として Gazebo のライブラリを同梱したものとして配られるので、Gazebo の本家の apt のリポジトリを別に足さなくてかまいません。

入れるものは2つで、表は2列、2行です。

ros-jazzy-ros-gz は、vendor パッケージを通した Gazebo Harmonic の本体と、ROS2 と連携するための、起動用の ros_gz_sim、トピックの橋渡しの ros_gz_bridge などです。

ros-jazzy-ros-gz-sim-demos は、公式のデモ集です。この手順書で動かす2輪車のデモが入っています。

### 1-2. インストール

sudo apt update をしてから、sudo apt install で、ros-jazzy-ros-gz と ros-jazzy-ros-gz-sim-demos を入れます。依存するパッケージ、たとえば RViz2、rqt_plot、xacro などもまとめて入るので、ダウンロードとインストールにしばらくかかります。

PC の負荷についての囲みがあります。Gazebo は、3D の描画と物理の計算を同時に行うので、ここまでの turtlesim や rqt より、はるかに重いです。WSL2 に割り当てたメモリが少ない環境では、動かす間は、ブラウザなど他のアプリを閉じておくとよい、とあります。

期待する結果です。パッケージの数や容量は環境によって違います。新しく入るパッケージの一覧に、gz-sim の vendor、ros-gz、ros-gz-bridge、ros-gz-sim、ros-gz-sim-demos などが並び、続けるかどうかを、Y か n で尋ねられます。Y で続け、最後に、E とコロンで始まるエラーの行が出ずに、プロンプトへ戻れば成功です。

### 1-3. 入ったことを確かめる

インストールした直後のターミナルでは、新しく入ったパッケージの設定が読み込まれていません。新しいターミナルを開いてから、次を実行します。新しいターミナルでは、bashrc で、/opt/ros/jazzy の setup.bash が読み込まれます。

実行するのは、ros2 pkg list を ros_gz で grep したものと、gz sim --version です。

期待する結果です。1つ目では、ros_gz、ros_gz_bridge、ros_gz_image、ros_gz_interfaces、ros_gz_sim、ros_gz_sim_demos が並びます。ros_gz_bridge、ros_gz_sim、ros_gz_sim_demos が並べば、ROS2 の側の連携のパッケージが入っています。2つ目では、Gazebo Sim の版が、8 で始まる番号で表示され、著作権とライセンスの行が続きます。版の細かな数字は、導入した時期によって違います。8 と出れば、Gazebo Harmonic、つまり Gazebo Sim の8系が使えます。

gz のコマンドが見つからない、と出る場合は、インストールの前から開いていたターミナルで試していないかを確かめます。gz のコマンドは、/opt/ros/jazzy の下の、gz_tools_vendor の bin に入り、setup.bash を読み込んだときに PATH へ足されます。そのため、ros2 は動くのに gz だけが見つからない、ということが起きます。

## 2. 全体像

この手順書で動かすのは、Gazebo に付属するワールド、diff_drive.sdf です。平らな地面に、2輪とキャスター、つまり向きが自由に変わる補助の輪の車両が、2台置かれています。

2台の車両の表は、5列で、2行あります。列は、車両、初めの位置、最高の速度、加速度の上限、オドメトリの送信の周期です。

1行目は vehicle_blue、青の車両です。初めの位置は、y が2メートルで、x 軸の正の向きを向いています。最高の速度は、前後が毎秒0.5メートル、旋回が毎秒1ラジアンです。加速度の上限は、前後が毎秒毎秒1メートル、旋回が毎秒毎秒2ラジアンです。オドメトリの送信の周期は1ヘルツです。

2行目は vehicle_green、緑の車両です。初めの位置は、y がマイナス2メートルで、x 軸の正の向きを向いています。最高の速度と加速度の上限は、青と同じです。オドメトリの送信の周期は50ヘルツで、これは既定値です。

どちらの車両にも、Gazebo の DiffDrive プラグインが付いています。DiffDrive は、左右の車輪の回転の速さの差で、進んだり曲がったりする2輪車を動かす部品です。速度の指令、つまり前進の速さと旋回の速さを受け取って左右の車輪を回し、車輪の回転からオドメトリを計算して送り出します。表の値は、ワールドファイルから読み取ったものです。

ここで大事なのは、Gazebo は、ROS2 とは別の通信の仕組み、gz-transport でトピックをやり取りする、という点です。Gazebo の車両が待っている指令は、ROS2 の geometry_msgs の msg の Twist ではなく、Gazebo の型の gz.msgs.Twist で届く必要があります。この2つの世界をつなぐのが、ros_gz_bridge の parameter_bridge で、型を変換しながらメッセージを中継します。

ここに図が1枚あります。左右に3つの領域が並びます。

左は、薄い青の破線の枠で、見出しは、ROS2 の世界、DDS です。中に、薄い青の箱が上下に2つあります。上の箱は、指令を送る側で、ros2 topic pub と、5節の gz_drive と書いてあります。下の箱は、観察する側で、ros2 topic echo と、5節の gz_drive と書いてあります。

真ん中には、薄いオレンジ色の縦長の箱が1つあり、parameter_bridge、ros_gz_bridge、型を変換して中継する、と書いてあります。

右は、薄い緑の破線の枠で、見出しは、Gazebo の世界、gz-transport です。中に、薄い緑の縦長の箱があり、gz sim、vehicle_green、DiffDrive プラグイン、と書いてあります。

矢印は4本で、どれも実線です。上の段では、指令を送る側から、ブリッジへ、/model/vehicle_green/cmd_vel と geometry_msgs の msg の Twist というラベルの矢印があり、ブリッジから Gazebo の箱へ、gz.msgs.Twist というラベルの矢印が続きます。下の段では、Gazebo の箱から、ブリッジへ、gz.msgs.Odometry というラベルの矢印があり、ブリッジから観察する側へ、/model/vehicle_green/odometry と nav_msgs の msg の Odometry というラベルの矢印が続きます。指令は左から右へ、オドメトリは右から左へ、どちらもブリッジで型を変えて流れる、という絵です。

2節から4節で、この図を順に確かめていきます。まず Gazebo だけで動かし、ROS2 からは見えないことを確かめ、次にブリッジを挟んで、ROS2 から動かします。

### 2-1. Gazebo だけでワールドを開く

ROS2 を使わずに、Gazebo だけでワールドを開きます。コマンドは gz sim diff_drive.sdf です。

期待する結果です。Gazebo のウィンドウが開き、灰色の地面の上に、青と緑の車両が1台ずつ見えます。この手順書の冒頭の画面です。最初の起動は、描画の準備に時間がかかることがあります。

ウィンドウの左下に、再生のボタンがあります。gz sim は一時停止の状態で始まるので、再生のボタンを押すまで、物理の時間は進みません。-r を付けて起動すると、始めから再生されます。

再生のボタンを押すと、右下の RTF、つまり Real Time Factor が動き出します。シミュレーションの時間が、現実の時間の何倍の速さで進んでいるかを表す値です。100パーセントに近ければ現実と同じ速さで、PC が重くて追いつかないと、100パーセントを下回ります。100パーセントを少し下回る程度なら、手順どおりに進められる、とあります。

画面の操作は、左ドラッグで平行移動、右ドラッグかホイールで拡大と縮小、ホイールを押しながらドラッグで回転です。

ウィンドウが開かない、真っ黒になる場合は、8節の表を見ます。

別のターミナルから、gz topic -l で、Gazebo のトピックを見ます。

期待する結果です。一時停止のままでも、再生中でも同じです。20あまりのトピックが並び、その中に、clock、stats、gui の下のカメラなどのトピック、world の diff_drive の下の時計、姿勢、シーン、状態などのトピックがあります。車両のものは、model の vehicle_blue と vehicle_green のそれぞれに、odometry、tf、cmd_vel、enable の4つずつです。末尾の行は、実行ごとに1行ほど増えたり減ったりすることがあります。

並びは名前の順ではないので、車両の名前で探します。model の車両名の cmd_vel が、指令を受け付けるトピック、model の車両名の odometry が、オドメトリを送り出すトピックです。これらの名前は、DiffDrive プラグインの既定の決まり、つまり model のモデル名の下に置く、という決まりで付いています。トピックはワールドを開いた時点で用意されるので、再生のボタンを押す前から一覧に出ます。

再生のボタンを押して再生した状態で、Gazebo のコマンドで、青の車両に指令を送ってみます。一時停止のままだと、物理の時間が進まないので、車両は動きません。コマンドは、gz topic の -t に /model/vehicle_blue/cmd_vel、-m に gz.msgs.Twist、-p に、linear の x を0.5、angular の z を0.3 にした値を渡します。

期待する結果です。コマンドは何も表示せずにすぐ終わり、Gazebo の画面で、青の車両が左回りの円を描いて走り出します。1回送っただけで走り続けるのは、DiffDrive が、最後に受け取った指令を持ち続けるためです。これは4-3節で扱います。止めるには、同じコマンドで、linear の x と angular の z を0.0 にした、速度0 の指令を送ります。

すると、コマンドは何も表示せずにすぐ終わり、青の車両が止まります。加速度に上限があるので、その場でぴたりとは止まらず、少し進みながら減速して止まります。

最後に、同じトピックが ROS2 から見えるかを、ros2 topic list で確かめます。

期待する結果は、/parameter_events と /rosout の2つだけです。model のトピックは1つも出てきません。Gazebo のトピックは gz-transport の上にあり、ROS2 の通信、DDS とは別の仕組みだからです。これが、ブリッジが要る理由です。

確かめたら、Gazebo のウィンドウを閉じるか、起動したターミナルで Ctrl+C を押します。

課題1。車両の最高の速度は、毎秒0.5メートルに制限されています。2節の表のとおりです。linear の x を2.0 にして送ると、画面の上の速さが、0.5 のときと変わらないことを確かめます。制限は、DiffDrive プラグインの設定、max_linear_velocity でかかっています。

## 3. デモを起動し、ROS2 のコマンドで車両を走らせる

### 3-1. launch の中身を確かめる

ros_gz_sim_demos の diff_drive.launch.py は、次の3つを起動します。

1つ目は Gazebo です。ros_gz_sim の gz_sim.launch.py を取り込み、gz sim に -r と diff_drive.sdf を付けて起動します。-r なので、再生された状態で始まります。

2つ目は parameter_bridge です。2節の図のブリッジで、青と緑の2台分、cmd_vel と odometry の、合わせて4本を中継します。

3つ目は RViz2、つまり ROS2 の可視化のツールです。引数 rviz で、起動するかどうかを切り替えます。

起動する前に、引数と展開の結果を確かめます。この段階では、ノードは起動しません。launch ファイルは、起動の設定を変えるための引数を受け付けることがあり、ros2 launch のパッケージとファイルの後ろに、名前、コロン、イコール、値の形で渡します。--show-args を付けると、受け付ける引数の名前、説明、既定値を一覧にして終わります。

ros2 launch ros_gz_sim_demos diff_drive.launch.py に --show-args を付けて実行します。

期待する結果、抜粋です。gz_args は、Gazebo Sim に渡す引数で、既定は空です。on_exit_shutdown は、gz-sim が終わったときに全体を終えるかどうかで、既定は false です。rviz は、RViz を開くかどうかで、既定は true です。

rviz の既定は true なので、何も指定しないと RViz2 も一緒に開きます。Gazebo と同時に開くと重いので、この手順書では rviz:=false を付けて起動します。on_exit_shutdown が false なので、Gazebo のウィンドウを閉じても、ブリッジは止まりません。止めるときは、launch のターミナルで Ctrl+C を押します。

次に、--print を付けて、この launch ファイルが何を起動するのかを一覧にします。--print を付けると、ros2 launch は launch ファイルを読み込んで、中身、つまり起動する予定のプロセスとその引数を、木の形で表示するだけで終わります。Gazebo もブリッジも起動しません。launch ファイルは Python のコードなので、ファイルを開いて読むより、読み込まれた結果を見る方が早い、とあります。ここでの目的は、ブリッジにどのトピックが渡されるか、つまり ROS2 から見えるようになるトピックはどれかを、起動する前に確かめることです。--print の詳しい読み方は、フェーズ4 の4-1節で扱います。

コマンドは、同じ ros2 launch に、rviz:=false と --print を付けたものです。

期待する結果です。木の中に、IncludeLaunchDescription と DeclareLaunchArgument が1つずつと、ExecuteProcess が2つあります。1つ目の ExecuteProcess は、ros_gz_bridge の parameter_bridge で、引数が4本並びます。青と緑のそれぞれについて、cmd_vel を、ROS2 の geometry_msgs の Twist と、Gazebo の gz.msgs.Twist で変換するものと、odometry を、ROS2 の nav_msgs の Odometry と、Gazebo の gz.msgs.Odometry で変換するものです。2つ目の ExecuteProcess は、rviz2 を、デモの rviz の設定ファイル付きで起動するものです。オブジェクトのアドレスは、実行ごとに変わります。

ブリッジの引数は、トピック名、アットマーク、ROS2 の型、アットマーク、Gazebo の型、の形で、1本ずつ、どのトピックを、どの型どうしで変換するかを指定しています。区切りのアットマークは、両方の向きの中継を意味します。片方の向きだけにしたいときは、ROS2 から Gazebo へを、閉じの角かっこ、Gazebo から ROS2 へを、開きの角かっこで書きます。RViz2 の行が残っているのは、--print が起動の条件、つまり rviz:=false を評価せずに一覧を出すためで、実際に起動したときは、RViz2 は開きません。

### 3-2. 起動して、ROS2 からトピックを見る

ターミナルを2つ使います。ターミナル1 で、ros2 launch ros_gz_sim_demos diff_drive.launch.py に rviz:=false を付けて起動します。

期待する結果です。2-1節と同じ Gazebo のウィンドウが開き、今度は初めから再生された状態になります。ターミナル1 には、ブリッジが作った中継の一覧が出ます。たとえば、Gazebo から ROS2 への中継として、vehicle_blue の odometry を、gz.msgs.Odometry から nav_msgs の Odometry へ、という行と、ROS2 から Gazebo への中継として、vehicle_blue の cmd_vel を、geometry_msgs の Twist から gz.msgs.Twist へ、という行が出ます。GZ から ROS と、ROS から GZ の両方の向きが、トピックごとに作られていれば成功です。

ターミナル2 で、ros2 topic list を実行します。

期待する結果です。vehicle_blue と vehicle_green の、それぞれの cmd_vel と odometry の4つと、/parameter_events、/rosout が並びます。2-1節では見えなかった model のトピックが、今度は ROS2 から見えます。ブリッジが、ROS2 の側に、同じ名前のトピックを作ったためです。

### 3-3. ros2 topic pub で走らせる

ターミナル2 から、緑の車両に指令を送ります。フェーズ1 で turtlesim に送ったのと同じ、Twist の型です。コマンドは、ros2 topic pub に --once を付け、/model/vehicle_green/cmd_vel に、geometry_msgs の msg の Twist で、linear の x を0.5、angular の z を0.3 にした値を送るものです。

期待する結果です。publisher がループを始めた、という行と、1番目の publish として、linear の x が0.5、angular の z が0.3 の Twist を送った、という行が出ます。Gazebo の画面では、緑の車両が左回りの円を描き始めます。--once で1回送っただけなのに走り続けるのは、2-1節と同じく、DiffDrive が最後の指令を持ち続けるためです。止めるには、同じ ros2 topic pub に --once を付けて、中かっこだけの空の値を送ります。空の中かっこは、全部のフィールドが既定値の0 の Twist、という意味です。

課題2。旋回だけ、つまり angular の z を0.5 にしたものと、後退、つまり linear の x をマイナス0.3 にしたものを送り、車両の動きが Twist の値と対応していることを確かめます。turtlesim と同じく、使うのは linear の x、つまり前進と、angular の z、つまり旋回だけです。

### 3-4. オドメトリを観察する

緑の車両を走らせた状態、つまり3-3節の最初の指令を送った状態で、ros2 topic echo に --once を付けて、/model/vehicle_green/odometry を1回だけ表示します。

期待する結果です。header の下に、stamp の秒とナノ秒、frame_id の vehicle_green の odom が出ます。child_frame_id は vehicle_green の chassis です。pose の pose には、position の x、y、z と、orientation の x、y、z、w が出ます。例では、x が0.93、y が0.28 のような値です。その下の covariance は、0.0 が36行並びます。twist の twist には、linear の x が0.5、angular の z が0.3 で、ほかは0.0 です。その下の covariance も、0.0 が36行です。時刻と、位置や向きの値は、走らせた時間によって変わります。

nav_msgs の msg の Odometry の読み方の表は、2列で、6行あります。

header の stamp は、いつの値かです。シミュレーションの時刻、つまり Gazebo を起動してからの時間で、現実の時刻ではありません。

header の frame_id は、位置の基準になる座標系です。vehicle_green の odom は、走り始めた地点を原点とする座標系です。

child_frame_id は、動いている物体の座標系で、車両の車体、chassis です。

pose の pose は、位置と向きです。位置の position はメートルで、向きの orientation は、クォータニオンという4つの数で向きを表す形です。

twist の twist は、速度です。車体から見た前進の速さ、linear の x が毎秒メートルで、旋回の速さ、angular の z が毎秒ラジアンです。

pose の covariance と twist の covariance は、位置と速度の値が、どのくらい不確かかを表す共分散です。36個の数で、6行6列の表を表します。このデモでは、すべて0.0 です。

twist の twist の linear の x が、指令の0.5 に、angular の z が0.3 に近ければ、指令どおりに走っています。フェーズ5 で扱う現在の速度にあたるのが、この linear の x です。

オドメトリは推定値だ、という囲みがあります。DiffDrive は、車輪の回転の角度から走った距離を計算して、オドメトリを出しています。車輪が滑ると、実際の位置とずれていきます。実物のロボットでも、同じ問題が起きます。

共分散についての囲みもあります。共分散は、推定値がどのくらい当てにならないかを表す数です。pose と twist に、それぞれ36個ずつあり、6行6列の表を、1行目から順に並べたものです。定義は、geometry_msgs の PoseWithCovariance にあります。表の行と列は、x、y、z と、X 軸、Y 軸、Z 軸のまわりの回転の6つです。対角、つまり1番目、8番目、15番目、22番目、29番目、36番目が、それぞれの値の分散で、大きいほど不確かです。それ以外は、2つの値のずれ方の関係を表します。

このデモですべて0.0 なのは、誤差が無い、という意味ではなく、誰も値を入れていないからです。Gazebo のオドメトリの型、gz.msgs.Odometry には、共分散の欄がそもそもありません。ブリッジはこれを nav_msgs の Odometry に変換するときに、covariance を0.0 のままにしておきます。

共分散は、いくつものセンサーを組み合わせて位置を推定するとき、たとえばオドメトリと IMU を重ねる robot_localization で、どのセンサーをどのくらい信用するか、の重みとして使われます。そのため、実物のロボットのドライバは、車輪の滑りやすさなどから見積もった値を入れて送るのが普通です。フェーズ5 で扱う速度の制御は、twist の twist の linear の x しか使わないので、0.0 のままで困ることはありません。

次に、2台のオドメトリの送信の周期を比べます。ターミナル2 で、ros2 topic hz の /model/vehicle_green/odometry を実行し、Ctrl+C で止めてから、/model/vehicle_blue/odometry でも実行します。

期待する結果です。値は少し揺れます。緑は、平均の頻度が50 で、間隔は約0.02秒です。青は、平均の頻度が1 で、間隔は1秒です。

緑は約50ヘルツ、青は約1ヘルツです。青の車両だけ、ワールドファイルで odom_publish_frequency が1 に設定されているためで、ブリッジは、Gazebo から届いた分をそのまま中継しているだけ、ということが分かります。速度の変化を細かく見たいときは、緑の車両を使います。5節の自作のノードも、緑を使います。RTF が100パーセントを大きく下回っている環境では、ros2 topic hz の値も小さくなります。現実の時間で測っているからです。

課題3。3-3節の停止の指令を送り、ros2 topic echo の /model/vehicle_green/odometry に、--field で twist.twist.linear.x を指定して、速度が0.5 から0 へ下がっていく様子を見ます。加速度の上限が毎秒毎秒1メートルなので、毎秒0.5メートルから止まるまでにかかるのは約0.5秒で、その間の値が、数十行にわたって少しずつ減っていきます。50ヘルツで流れるからです。

## 4. 仕組み、ブリッジと QoS と、指令を持ち続けること

この節のコマンドは、3-2節で起動したデモ、つまり Gazebo とブリッジが動いたままであることを前提にします。閉じてしまった場合は、3-2節のターミナル1 のコマンドで起動し直してから、ターミナル2 で実行します。

### 4-1. parameter_bridge の役割

parameter_bridge は、ROS2 のノードであると同時に、gz-transport のクライアントでもあります。3-1節の引数1本ごとに、指定された向きの中継を作ります。このデモの引数は、区切りがアットマーク、つまり両方の向きなので、1本ごとに、次の2つの向きが両方できます。

ROS2 から Gazebo への向きは、ROS2 の Subscriber で受けたメッセージを Gazebo の型に詰め替え、Gazebo のトピックへ送ります。cmd_vel の指令が通るのは、こちらです。geometry_msgs の Twist から、gz.msgs.Twist へです。

Gazebo から ROS2 への向きは、Gazebo から受けたメッセージを ROS2 の型に詰め替え、ROS2 の Publisher で送ります。odometry が通るのは、こちらです。gz.msgs.Odometry から、nav_msgs の Odometry へです。

ros2 node list を見ると、ブリッジは1つの ROS2 のノードとして見えます。ノード名は ros_gz_bridge です。

ターミナル2 で、ros2 node list と、ros2 topic info の /model/vehicle_green/cmd_vel を実行します。

期待する結果です。ros2 node list には /ros_gz_bridge が出ます。ros2 topic info には、型が geometry_msgs の msg の Twist、publisher の数が1、subscription の数が1 と出ます。

subscription と publisher の1つずつは、どちらもブリッジです。subscription の1 は、ROS2 から Gazebo への向きの Subscriber で、指令を受けて Gazebo へ送る、本来の役目の側です。publisher の1 は、Gazebo から ROS2 への向きの Publisher です。引数をアットマーク、つまり両方の向きで書いたので、cmd_vel にもこちらの向きが作られています。Gazebo の側の cmd_vel に届いたメッセージを ROS2 へ流すためのもので、ROS2 から車両を動かすだけなら使いません。cmd_vel を、閉じの角かっこ、つまり ROS2 から Gazebo への向きだけで書けば、この Publisher は作られません。

ros2 topic pub や、5節の自作のノードを動かしている間は、それが Publisher として加わり、publisher の数が1つ増えます。

### 4-2. QoS、指令は reliable で受ける

cmd_vel を受けるブリッジの Subscriber の信頼性、reliability は reliable です。QoS の相性の決まり、つまりフェーズ3-2b の6節の、QoS の互換性のまとめでは、Subscriber が reliable のとき、Publisher が best_effort だと、つながりません。

Subscriber の設定は、-v を付けた ros2 topic info で確かめられます。ターミナル2 で、ros2 topic info に -v を付けて、/model/vehicle_green/cmd_vel を見ます。

期待する結果、抜粋です。型が Twist で、publisher の数が1 と出たあと、その Publisher のノード名が ros_gz_bridge、エンドポイントの種類が PUBLISHER と出ます。続いて、subscription の数が1 と出て、その Subscriber のノード名も ros_gz_bridge、エンドポイントの種類が SUBSCRIPTION、QoS のプロファイルの Reliability が RELIABLE と出ます。

Publisher の側も Subscriber の側も、ノード名はブリッジです。4-1節のとおり、両方の向きの中継のためです。確かめるのは、受ける側、つまりエンドポイントの種類が SUBSCRIPTION の方の Reliability が、RELIABLE であることです。

launch ファイルの QoS の指定についての囲みがあります。diff_drive.launch.py には、ブリッジのパラメータとして、qos_overrides の、model の vehicle_green の、subscriber の reliability を reliable にする指定が書かれています。ただし、このキーのトピック名の部分、つまり model の vehicle_green は、実際のトピック名、model の vehicle_green の cmd_vel と一致していないので、この指定が効いているかどうかは疑わしい、とあります。手順書を作るときには確かめていません。いずれにしても、ROS2 の Subscriber の既定は reliable なので、上の表示で確かめた設定が、実際の値です。

ros2 topic pub と、フェーズ3-1 の書き方、つまり create_publisher に型、トピック名、10 を渡す書き方は、どちらも既定で reliable なので、この組み合わせではつながります。自分で QoS を best_effort にしたノードから送ると、車両が動かなくなる、という点だけ覚えておきます。

### 4-3. DiffDrive は最後の指令を持ち続ける

2-1節と3-3節で見たとおり、DiffDrive は、新しい指令が届くまで、最後に受け取った速度を出し続けます。指令が途絶えたら止まる、という仕組み、つまりタイムアウトを持っていません。このため、指令を送っていたノードを Ctrl+C で止めても、車両は最後の速度で走り続けます。止めたいときは、速度0 の指令を送ります。

実物のロボットでは、通信が途切れたときに走り続けるのは危ないので、一定の時間、指令が来なければ止まる、という仕組みを入れるのがふつうです。シミュレーションの車両では、止め忘れても、壁や物にぶつかるだけで済みますが、この違いは覚えておくとよい、とあります。フェーズ5-1 の5-2節では、この仕組み、つまり指令の元になる速度が0.5秒届かなければ、停止の指令を送る仕組みを、表示用のノード gz_display に、自分で入れます。

## 5. 自作のノードで走らせ、オドメトリを観察する

フェーズ3-1 の talker、つまり Publisher と、listener、つまり Subscriber を、1つのノードにまとめたものを書きます。

### 5-1. 仕様

ノード名と実行ファイル名は gz_drive で、パッケージは learn_py です。

送るのは、/model/vehicle_green/cmd_vel、型は geometry_msgs の msg の Twist で、前進の毎秒0.3メートル、旋回なしを、0.1秒ごとに送ります。

受けるのは、/model/vehicle_green/odometry、型は nav_msgs の msg の Odometry で、これを購読し、前進の速さ、つまり twist の twist の linear の x と、位置の x 座標、つまり pose の pose の position の x を、1秒に1回、ログに出します。

主な API、つまりフェーズ3-1 で使ったもの以外の表は、2列で、3行あります。

geometry_msgs の msg の Twist は、速度の指令の型です。linear の x、つまり前進の毎秒メートルと、angular の z、つまり旋回の毎秒ラジアンを使います。

nav_msgs の msg の Odometry は、オドメトリの型です。3-4節の表のとおり、msg の twist の twist の linear の x のように、2段の入れ子をたどって値を取り出します。

get_logger の info に throttle_duration_sec の1.0 を付けると、同じ行のログを、指定した秒数に1回だけ出します。50ヘルツで届くメッセージを全部ログに出すと読めないので、間引くために使います。

### 5-2. 依存の追加

Twist は geometry_msgs、Odometry は nav_msgs のパッケージの型なので、learn_py の package.xml の depend の並びに、geometry_msgs と nav_msgs の2行を足します。フェーズ3-2a で geometry_msgs を既に足している場合は、nav_msgs の1行だけでかまいません。nav_msgs は、ros-jazzy-ros-gz か、ROS2 の本体と一緒に入っているので、追加の導入は要りません。

### 5-3. サンプルコードと解説

サンプルは、learn_py の learn_py フォルダの gz_drive.py です。

gz_drive.py は、45行ほどのコードで、ブロックは4つです。1つ目は import で、rclpy、Twist、Odometry、ExternalShutdownException、Node を読み込みます。2つ目は、Node を継承した GzDrive のクラスの __init__ で、ノード名を gz_drive にし、Twist の Publisher を /model/vehicle_green/cmd_vel に、Odometry の購読を /model/vehicle_green/odometry に、どちらもキューの深さ10 で作り、0.1秒のタイマーで on_timer を呼ぶようにします。3つ目は2つのコールバックです。要の行は、on_timer で、空の Twist を作って linear の x だけを0.3 にして publish する行と、on_odom で、msg の twist の twist の linear の x を速さとして、msg の pose の pose の position の x を位置として取り出し、速さと位置を小数で整えた1行を、throttle_duration_sec の1.0 を付けてログに出す行です。4つ目は main で、フェーズ3-1 の talker と同じく、init のあと spin で回し、KeyboardInterrupt か ExternalShutdownException を受けたら抜けて、finally で destroy_node と try_shutdown をします。

原文の解説の要点です。役割は、一定の速度の指令を10ヘルツで送り続けながら、車両から返ってくるオドメトリを見ることです。フェーズ3-1 の talker、つまりタイマーで送るものと、listener、つまり届いたら処理するものを、1つのノードにまとめた形で、骨組みは同じです。__init__ で通信の口を作り、コールバックに処理を書き、main の spin で回します。

__init__ では、Publisher、Subscription、タイマーを1つずつ作ります。1つのノードにいくつ持たせてもよく、spin が、タイマーの満了とメッセージの到着の両方を待って、それぞれのコールバックを呼びます。トピック名は、スラッシュから始まる絶対名で、3-2節の ros2 topic list に出た名前と、一字一句同じにします。つづりを間違えるとエラーは出ず、単に車両が動かない、ログが出ない、というだけになります。

on_timer では、Twist は全部のフィールドが0 で作られるので、linear の x だけを0.3 にすれば、旋回なしの前進になります。DiffDrive は最後の指令を持ち続けるので、4-3節のとおり、この車両を動かすだけなら1回送れば足ります。それでも周期的に送っているのは、送り続けるのが、ROS2 での速度の指令のふつうの形だからです。実物のロボットは、4-3節のとおり、指令が途絶えたら止まるように作ることが多いからです。

on_odom では、引数の msg が、届いた Odometry です。速度は msg の twist の twist の linear の x、位置は msg の pose の pose の position の x のように、入れ子をたどって取り出します。twist と pose が2回続くのは、外側が、値と誤差の大きさ、つまり covariance の組で、内側が値そのもの、という型の作りのためです。緑の車両のオドメトリは50ヘルツで届くので、throttle_duration_sec の1.0 で、1秒に1回に間引いています。

main は、フェーズ3-1 の talker と同じです。

観察のポイントです。車両が止まった状態から起動すると、最初のログの speed は0 に近く、すぐに0.3 のあたりに落ち着きます。加速度の上限が毎秒毎秒1メートルなので、毎秒0.3メートルに達するまでは約0.3秒で、1秒おきのログでは、途中の値はほとんど見えません。x は、1秒に約0.3メートルずつ増えていきます。

### 5-4. 実行ファイルとして登録し、ビルドする

learn_py の setup.py の entry_points に、1行足します。今ある行は、すべて残します。フェーズ3-1 まで進めた状態なら、console_scripts の一覧に、hello、talker、listener、sine_pub、sine_sub の行があり、その後ろに、gz_drive を learn_py の gz_drive の main に結び付ける行を足します。フェーズ3-2a より後の行、たとえば turtle_circle がある場合も、それらは残して、gz_drive の行を足します。

そのあと、ros2_ws で、colcon build に --symlink-install と --packages-select learn_py を付けてビルドし、source install/setup.bash をします。

期待する結果です。learn_py を始めて、終わったという行と、1つのパッケージが終わった、という要約が出ます。秒数は環境によって変わります。

### 5-5. 動かす

3-3節や課題2で車両を走らせた後は、車両の向きとオドメトリの値が、初めの状態からずれています。このままだと、このあとの期待する結果、つまり x が0 から増えて、まっすぐ前へ進む、にならないので、先にターミナル1 を Ctrl+C で止めて、3-2節と同じコマンドで起動し直します。ワールドが初めの状態に戻ります。起動し直さずに、Gazebo のリセットで戻す方法もあり、この節の最後で扱います。そのうえで、ターミナル2 で、ros2_ws に移って source install/setup.bash をし、ros2 run learn_py gz_drive を起動します。

期待する結果です。gz_drive のログが1秒に1行出ます。1行目は、speed が0.012、x が0.00 のような値で、2行目からは、speed が0.300 で、x が0.21、0.51、0.81 と、1秒に約0.3メートルずつ増えていきます。時刻と数値の細部は違います。

ログが1秒に1行出て、speed が0.300 のあたりで落ち着き、x が1秒に約0.3メートルずつ増えていれば成功です。Gazebo の画面では、緑の車両が、まっすぐ前、つまり x 軸の正の向きへ進みます。

x は、オドメトリの座標系、つまり走り始めた地点が原点の座標系での値なので、ワールドの上の位置、つまり初めの位置の y がマイナス2メートルの位置とは、原点が違います。

ログが1行も出ない場合は、トピック名のつづりと、ターミナル1 のデモが動いているかを確かめます。ros2 topic list に /model/vehicle_green/odometry があるかを見ます。RTF が100パーセントを大きく下回る環境では、x の増え方が、現実の1秒あたり0.3メートルより遅くなります。

Ctrl+C で gz_drive を止めても、車両は走り続けます。4-3節のとおりです。止めるには、ターミナル2 で、3-3節と同じ、空の値の停止の指令を送ります。

走らせすぎて、車両が画面の外へ出たときも、同じようにターミナル1 を起動し直せば、初めの状態に戻ります。

Gazebo のリセットの囲みです。ターミナル1 を起動し直さなくても、Gazebo の機能で、ワールドを初めの状態に戻せます。コマンドで行う場合は、Gazebo のサービス、つまりワールドの操作を受け付ける /world/diff_drive/control に、全体を戻す指示を送ります。gz service に、-s でサービス名、--reqtype に gz.msgs.WorldControl、--reptype に gz.msgs.Boolean、--timeout に3000、--req に、reset の all を true にした値を渡します。

期待する結果は、data が true という1行です。Gazebo が指示を受け付けた、という意味です。車両が初めの位置に戻り、右下のシミュレーションの時刻も0 に戻ります。Gazebo の画面の左下の、再生のボタンの近くに、リセットのボタンが出ている場合は、それを押して、確認のダイアログで Reset を選んでも同じです。

自作のノード gz_drive を動かしたままリセットすると、ノードが指令を送り続けるので、車両はすぐにまた走り出します。先に gz_drive を Ctrl+C で止めてから、リセットします。

課題が3つあります。

課題4。linear の x を0.8 にすると、ログの speed はいくつで落ち着くか。予想してから確かめます。2節の表の最高の速度が手がかりです。

課題5。angular の z に0.2 を足すと、x の増え方はどう変わるか。円を描くので、x は増えたあと、減り始めます。pose の pose の position の y もログに足すと分かりやすい、とあります。

課題6、発展です。ノードに、10秒走ったら速度0 を送って止まる処理を足します。ノードを始めてからの時間は、get_clock の now の差で測れます。止まるまでの speed の変化を見ると、加速度の上限の、毎秒毎秒1メートルで減速している様子が分かります。ただし、この時計は PC の現在の時刻なので、時刻合わせで数秒飛ぶと、止まるのが早まることがあります。経過した時間を測るのに向いた時計、つまり単調に増える時計は、フェーズ5-1 の5-2節の gz_display の解説で扱います。

## 6. フェーズ5-1 より後とのつながり

フェーズ5-1 では、1次元の車両の疑似プラント、つまり、ペダルの指令を受けて、慣性で少し遅れて現在の速度が変わるノードを自作し、フェーズ5-2 で PI 制御をつないで、目標の速度に追いつかせます。この手順書で動かした Gazebo の車両も、指令を受けて、現在の速度を返す、という同じ形をしています。

比較の表は、3列で、4行あります。列は、観点、フェーズ5-1 で自作する疑似プラント、そしてこの手順書の Gazebo の車両です。

入力は、疑似プラントでは、ペダルの指令です。トピックは /plant/pedal、型は std_msgs の msg の Float64 で、マイナス1 から1 の値です。Gazebo の車両では、Twist の linear の x で、トピックは /model/vehicle_green/cmd_vel です。

出力は、疑似プラントでは、現在の速度です。トピックは /plant/velocity、型は Float64 で、毎秒メートルです。Gazebo の車両では、Odometry の twist の twist の linear の x で、トピックは /model/vehicle_green/odometry です。

動きの決まり方は、疑似プラントでは、自分で書いた運動の式です。1次元の質点と、一次遅れと、オイラーの積分で、中身はフェーズ5-1 の2節で扱います。Gazebo の車両では、Gazebo の物理エンジンと、DiffDrive の設定、つまり最高の速度と加速度の上限で決まります。

中身を変えられるかは、疑似プラントでは、式もパラメータも自由に変えられます。Gazebo の車両では、ワールドファイルの設定の範囲で変えられます。

ただし、この車両は、DiffDrive が速度の指令をほぼそのまま実現してしまいます。加速度の上限の範囲で、一定の割合で、指令の速度へ近づきます。そのため、制御の効き方を観察する題材には向きません。そこで、フェーズ5 では、Gazebo の車両を次の2段階で使います。

フェーズ5-1 から5-3 では、表示器として使います。制御のループは自作のノードだけで閉じ、プラントが計算した速度を、縮尺をかけて、この手順書の緑の車両の cmd_vel へ送ります。DiffDrive が、送られた速度をそのままなぞることを、逆に表示に利用します。

フェーズ5-4 では、プラントとして使います。この手順書のワールドファイルを写して、緑の車両の DiffDrive を外し、車輪にトルク、つまり回す力をかけて動かす形に改造します。Gazebo の物理エンジンそのものをプラントにして、フェーズ5-2 の制御のノードを変えずに、つなぎ替えます。

## 7. このフェーズのまとめ

まとめは4つです。

1つ目。Jazzy に勧められるのは Gazebo Harmonic で、ros-jazzy-ros-gz を入れると、ROS2 の apt のリポジトリからまとめて導入できます。

2つ目。Gazebo のトピック、つまり gz-transport と、ROS2 のトピック、つまり DDS は別の仕組みで、ros_gz_bridge の parameter_bridge が、トピック名、ROS2 の型、Gazebo の型をアットマークでつないだ指定に従って、型を変換しながら中継します。

3つ目。2輪車の速度の指令は、turtlesim と同じ geometry_msgs の msg の Twist です。返ってくる状態は nav_msgs の msg の Odometry で、twist の twist の linear の x が、現在の前進の速さです。

4つ目。DiffDrive は最後の指令を持ち続けるので、指令を送るノードを止めても、車両は止まりません。

## 8. つまずきやすい点

2列の表で、7行あります。列は、症状と、確かめることです。

1行目。gz のコマンドが見つからない場合。インストールの前から開いていたターミナルで試していないかを確かめます。1-3節のとおりで、新しいターミナルを開きます。

2行目。Gazebo のウィンドウが開かない、真っ黒、すぐ落ちる場合。WSL2 の GUI、つまり WSLg で、3D の描画がうまくいかない場合があります。よく知られた回避策は、ソフトウェアで描画させる、export LIBGL_ALWAYS_SOFTWARE=1 を実行してから、同じターミナルで起動することです。描画は遅くなります。GPU のドライバが WSL2 に対応した版かも確かめます。手順書を作るときには、これらの回避策の効き目は確かめていない、とあります。

3行目。2-1節で、画面は出るが車両が動かない場合。左下の再生のボタンを押したかを確かめます。gz sim は一時停止で始まります。

4行目。ROS2 から送っても車両が動かない場合。ros2 topic list に /model/vehicle_green/cmd_vel があるか、つまりブリッジが動いているかと、トピック名のつづり、そして QoS を best_effort にしていないかを確かめます。4-2節のとおりです。

5行目。車両が止まらない場合。DiffDrive は最後の指令を持ち続けるので、速度0 を送ります。4-3節のとおりです。

6行目。動きが重い、RTF が低い場合。rviz:=false を付けて起動しているかを確かめ、他のアプリを閉じます。RTF が低いと、シミュレーションの1秒が、現実の1秒より長くなります。

7行目。Gazebo を閉じても launch が終わらない場合。on_exit_shutdown の既定が false のためです。launch のターミナルで Ctrl+C を押します。

## 9. 次へ

フェーズ5-1 で、1次元の車両の疑似プラントを自作し、計算した速度を、この手順書の緑の車両で見せます。フェーズ5-1 ではパラメータ、つまりフェーズ3-3 を使います。フェーズ5-3 からは launch、つまりフェーズ4 も使うので、それまでにフェーズ4 を終えておきます。この手順書のデモ、diff_drive.launch.py はフェーズ5-1 から5-3 で、ワールドファイル diff_drive.sdf はフェーズ5-4 で、再び使います。

## 10. 公式のドキュメントと参考資料

確かめた状況は、2026年9月24日の時点で、9月26日に書き足しています。Gazebo の公式の2つのページは、手順書を作るときに本文を確かめました。9月26日に、説明のページとして、Gazebo の、ロボットを動かすページと、ROS 2 を使って Gazebo とやり取りするページ、DiffDrive の API のリファレンス、ros_gz_sim_demos のパッケージのドキュメント、ROS 2 の Gazebo のチュートリアルを足しました。Gazebo と ROS 2 のチュートリアルは本文を確かめ、パッケージのドキュメントは、検索の結果で、実在と内容の概要だけを確かめた、とあります。docs.ros.org は、ボット対策で本文を取得できないためです。DiffDrive プラグインの既定値、つまりオドメトリの送信の周期の50ヘルツと、トピック名の決まり、そして指令のタイムアウトが無いことは、GitHub の gz-sim の、gz-sim8 のブランチのソースで確かめた、とあります。日本語の記事は、元のアイデアの文書に載せたもので、今回は確かめ直していない、とあります。

公式の資料は8つです。1つ目は、ROS と一緒に Gazebo を入れるページで、ROS2 の版と Gazebo の版の対応と、Jazzy での導入の方法を扱います。2つ目は、ROS 2 のドキュメントの、ロボットのシミュレーションを用意するページで、ROS 2 の公式の入り口です。導入の確かめまでで、その先は Gazebo のチュートリアルへ案内しています。3つ目は、ROS 2 を使って Gazebo とやり取りするページで、parameter_bridge の使い方、つまりアットマークと角かっこの向きの書き分け、YAML での設定、QoS の上書きを扱います。4つ目は、ロボットを動かすページで、DiffDrive プラグインをロボットに付けて、Gazebo のコマンドで動かすチュートリアルです。ROS 2 は使いません。5つ目は、Gazebo Sim 8 の API リファレンスの DiffDrive のページで、パラメータの一覧と既定値を扱います。6つ目は、Jazzy の ros_gz_sim_demos のパッケージのドキュメントで、デモの一覧と起動の方法を扱います。7つ目は、GitHub の gazebosim の ros_gz の、ros_gz_sim_demos のソースで、launch ファイルとブリッジの設定があります。8つ目は、GitHub の gazebosim の gz-sim の、DiffDrive プラグインのソースで、パラメータの説明は、ヘッダの DiffDrive.hh のコメントにあります。

日本語の記事も2つ挙げてあります。どちらも、ROS 2 と Gazebo を連携してロボットを動かす、個人による解説の記事です。記事は非公式の解説で、版によって違う場合があり、公式のドキュメントと食い違う場合は、公式を優先する、とあります。

原文の最後には、出典の注記があります。導入のコマンドは、Gazebo の公式のドキュメントの手順と同等のものです。デモの構成、トピック名、車両の設定値は、導入したパッケージ、つまり ros_gz_sim_demos と gz_sim_vendor のファイルを読んで、自分の言葉でまとめたもので、ファイルの転載ではありません。どちらも Apache 2.0 です。サンプルコードと文章は、独自に書いたものです。

以上で、フェーズ5-0 の手順書の話を終わります。

## 出典について

この原稿は、SanghunIm1991 さんの [ros2MinimalPhysicalAi の「フェーズ5-0 手順書: Gazeboを導入し、用意されたロボットをROS2から動かす」](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/docs/phase5_0_gazebo.md)を、聞くために要約・意訳したものです。図の [phase5_0_bridge.svg](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/docs/img/phase5_0_bridge.svg) と、画面の [phase5_0_gazebo.png](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/docs/img/phase5_0_gazebo.png) は、言葉で説明しました。元にしたのは、[2026年10月14日の版](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/132df7b64d48d560def7ec7149f7003938d3d8e5/docs/phase5_0_gazebo.md)です。原文の文章と図と同じく、[クリエイティブ・コモンズ 表示 4.0 国際ライセンス](https://creativecommons.org/licenses/by/4.0/deed.ja)で提供します。

原稿の中に原文の表記のまま書いたコマンドと、コードの関数やクラスの名前は、原文では [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0) の対象です。ライセンスの全文は、原文のリポジトリの [LICENSE-APACHE-2.0](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/LICENSE-APACHE-2.0) にあります。サンプルコードは写さず、役割と要の行を言葉で説明しました。

原文の冒頭の画面に写っている Gazebo Sim の画面と、付属のワールド diff_drive.sdf の中身は、[Gazebo](https://gazebosim.org/)（Open Source Robotics Foundation、Apache License 2.0）のものです。この原稿では、画面の様子と、ワールドの設定値を言葉で説明しました。表示の例は、apt、ros2、gz などの各ツールの表示を言葉で説明したものです。
