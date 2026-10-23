<!--
聞くための原稿（読み上げでは読まれない記録）
原文: SanghunIm1991/ros2MinimalPhysicalAi の main ブランチの docs/phase6_1_record.md（図は docs/img/phase6_1_record.svg）
原文のコミット: 41d2c800082a372a810d286ded1bb56d9c05b67e（2026-10-17）
作成: 2026-10-23、Claude Code が手作業で作成（原稿化スキルはまだない）
原文のライセンス: 文章と図は CC BY 4.0、コードとコマンドは Apache-2.0（それぞれ LICENSE の2と1）。期待する結果に載せたコマンドの出力は、LICENSE の「第三者の著作物」にある各ツールの表示（rosbag2・ros2 のコマンド・launch・colcon・pgrep など。rqt_plot の結果は、筆者が想定した形を文章で書いたもの）。原文の末尾に、ros2 bag と rqt_plot の振る舞いは、公式ドキュメント、ローカルのヘルプとソース、使い捨ての環境で実行した結果から筆者が自分の言葉でまとめたもので、サンプルコードと文章は独自に書いたもの、とある。この原稿は、原文を聞くために要約・意訳したもの（改変あり）
方針: 英語の略語や製品名、関数やクラスの名前、短いコマンドは原文の表記のまま書く。単位は「毎秒10メートル」のように読む。サンプルコード（target_node.py・record.launch.py）と、launch と YAML に足す行は、写さずに、ブロックの構成と要の行を言葉で説明し、各行の意味は原文の解説と表に任せた（要の行は、解説と表に出てこない行だけにした）。期待する結果（ros2 bag の表示、ros2 topic echo、--show-args、launch のログ、pgrep、ros2 node list）も、写さずに、何が表示されるかと原文の解説が使う値を言葉で説明した。図と表（ros2 bag info の読み方、よく使うオプション、rqt_plot の部品、record.launch.py の各部分、つまずきやすい点）は言葉で説明する。文字数の上限は設けない
省いたもの: URL、型の定義へのリンク、リンク先のファイル名、mermaid 版の図（SVG と同じ内容）、ログの時刻とプロセス番号、ログの行のうち原文の解説が使わない行（ros2 bag record の Event publisher thread・Listening for topics・Recording...・Topics discovery stopped など）、ros2 bag info の Serialization Format と Service information、5節の Gazebo が終わった行の cmd の部分、4-5節の「長い行は途中で切っている」という注記、ros2 bag info の Start と End の日時、pgrep の表示のインストール先のパス、rqt_gui_py_node の後ろの数字、10節のローカルのソースの置き場所のパス
-->

# フェーズ6-1: 記録して見直す、ros2 bag と rqt_plot（聞くための原稿）

これは、ros2MinimalPhysicalAi という教材の、フェーズ6-1 の手順書の話です。学習計画のフェーズ6 の6-1、元のアイデアのステップ4 に当たります。フェーズ5-3 と5-4 で動かした車両のシミュレーションのトピックを、ros2 bag で記録し、後から再生して rqt_plot で見直します。記録を、決めた時間で自動的に終わらせる仕組みを launch に足し、最後に、フェーズ5-3 と5-4 の記録を同時に再生して、1つのグラフに重ねて比べます。

想定する環境は、WSL2 と Ubuntu 24.04 と ROS2 Jazzy です。前提は2つです。フェーズ5-3 を終え、vehicle_sim.launch.py と target_generator が動くこと。フェーズ5-4 を終え、gazebo_plant.launch.py が動くことです。所要時間の目安は1から2コマで、言語は Python です。launch も Python の形式です。

進め方の囲みです。2節で、手で記録して再生する流れを、ひととおり試します。3節で、再生した値を rqt_plot で見直します。4節で、記録を決めた時間で終わらせる仕組みを作り、条件を変えた記録も取ります。これは4-6節で、フェーズ6-3 で使います。5節で、フェーズ5-4 の一式も同じ方法で記録します。6節で、2つの記録を重ねて比べます。サンプルは、学習の手がかりとして最小限に書いたもので、公式チュートリアルの転載ではありません。コードは、手順書を作るときに、使い捨ての環境でビルドし、記録と再生を実行して確かめました。Gazebo は画面なしで起動したので、画面の見え方と、rqt_plot のグラフは確かめていません。出力が違う場合は、実際の表示を優先します。

期待する結果の出どころの囲みもあります。ros2 bag の record、info、play の表示、2-3節の ros2 topic echo の表示、4-5節のビルドと --show-args の表示、4-5節、4-6節、5節の launch のログ、6節の ros2 node list は、使い捨ての環境で実際に実行した表示です。2-3節の ros2 topic echo は、型を書く前の形のコマンドで確かめましたが、型を書いても表示は変わりません。5節は Gazebo を画面なしで起動し、6節は rqt_plot を画面なしで起動しました。4-6節のログは、YAML を learn_bringup の config に置いてビルドする以前の手順で記録したときのものですが、表示される行は、置き場所によりません。時刻、パス、メッセージの数は、実行ごとに違い、ログは抜粋です。3節と6節の rqt_plot の画面の様子は、rqt_plot のソースと、記録から読み出した数値から、筆者が想定したものです。5節の末尾の pgrep の表示は、ros_gz_sim の launch のファイルが Gazebo を起動するときのコマンドの形から、筆者が想定したものです。

この原稿では、サンプルコードを書き写さずに、ブロックの構成と要の行を言葉で説明します。ツールの表示も、何が表示されるかを言葉で説明します。

## 0. 学習目標と完了の条件

学習目標は4つです。

1つ目。ros2 bag record でトピックを記録し、ros2 bag info で中身を確かめ、ros2 bag play で再生できる。

2つ目。再生した値を rqt_plot で描き、軸の範囲を決めて、画像に保存できる。

3つ目。あるノードが終わったら launch 全体を止める仕組み、つまり on_exit に Shutdown を指定する書き方を使い、決めた時間で記録を終わらせられる。

4つ目。2つの記録を、トピック名を付け替えて同時に再生し、1つのグラフに重ねて比べられる。

完了の条件です。record.launch.py で、フェーズ5-3 と5-4 の一式を、それぞれ記録します。どちらも決めた時間で自動的に終わります。そして、2つの記録を重ねたグラフで、フェーズ5-4 の7節の表の違いを目で確かめます。違いとは、フェーズ5-4 は目標の毎秒10メートルを少し行き過ぎること、落ち着いたときのペダルが0.54 ではなく、ほぼ0 であることです。

## 1. 全体像

フェーズ5-4 の7節では、自作のプラント、つまりフェーズ5-3 と、Gazebo の物理、つまりフェーズ5-4 の追従の違いを、表の数字で比べました。同じ違いを、グラフに重ねて目で見たいところです。ところが、これまでのやり方では難しい理由が2つあります。

1つ目。rqt_plot は、今届いている値を描くだけで、閉じると消えます。後から同じ動きを見直すには、もう一度シミュレーションを最初から動かすしかありません。

2つ目。フェーズ5-3 と5-4 は、どちらも /plant/velocity などの同じトピック名を使います。同時に動かすと値が混ざるうえ、Gazebo も動かすので重くなります。

そこで、動かしたときのトピックを記録しておき、後から再生します。ROS2 では、ros2 bag、つまり rosbag2 が、この役を担います。記録は bag と呼び、トピックに流れたメッセージを、届いた時刻と一緒にファイルへ書き込んだものです。再生すると、同じトピックに、同じ間隔でメッセージが流れます。再生するときにトピック名を付け替えれば、2つの記録を同時に流しても混ざりません。

ここに図が1枚あります。SVG と mermaid の版がありますが、内容は同じです。図は上下2つの破線の枠に分かれています。

上の枠は、横いっぱいの青みがかった灰色の破線の枠で、見出しは、記録する、4節と5節、record.launch.py です。枠の中の左に、薄い青の横長の箱があり、5-3 または5-4 の一式、target_generator は end_time 秒で終わる、と書いてあります。右に、もう1つの薄い青の箱があり、ros2 bag record、3つのトピックを記録、と書いてあります。左の箱から右の箱へ、実線の矢印が伸び、ラベルは、/target_velocity など3つ、です。さらに、左の箱の下から出て、下を回って右の箱に入る、破線の矢印があり、ラベルは、target_generator が終わると、Shutdown で全体が止まる、です。

右の ros2 bag record の箱からは、下へ2本の実線の矢印が下り、上の枠の外に出て、角の丸い薄いオレンジ色の箱、2つに届きます。左が bags の sim_default、右が bags の gz_default で、記録のフォルダです。

下の枠は、左下の薄い緑の破線の枠で、見出しは、重ねて見る、6節です。枠の中には、薄い青の箱が3つあります。真ん中の列に、上下に2つの箱が並び、上は ros2 bag play、そのまま、下は ros2 bag play、/gz/ に付け替え、と書いてあります。左の箱は rqt_plot で、/plant/ と /gz/plant/ を重ねる、と書いてあります。

sim_default のフォルダからは、左へ折れて、上の ros2 bag play、そのまま、の箱へ矢印が届きます。gz_default のフォルダからは、下へ下りてから左へ折れて、下の ros2 bag play、付け替え、の箱へ矢印が届きます。2つの ros2 bag play の箱からは、それぞれ左へ矢印が伸び、rqt_plot の箱に入ります。

まとめると、record.launch.py が、一式と記録を一緒に起動し、target_generator が終わると全体が止まって、記録が2つのフォルダに残る。それを、片方のトピック名を付け替えて同時に再生し、rqt_plot に重ねる、という流れです。

記録の置き場所は、この手順書では、ホームの ros2_ws の bags とします。記録を1回取るごとに、この下にフォルダが1つできます。

## 2. 手で記録して、再生する

### 2-1. 記録する、ros2 bag record

まず、フェーズ5-3 の一式を Gazebo なしで起動し、別のターミナルで記録します。

ターミナル1、つまり T1 で、ros2 launch learn_bringup vehicle_sim.launch.py に、gazebo:=false を付けて起動します。T2 では、mkdir -p でホームの ros2_ws の bags を作って、そこに cd で移り、ros2 bag record に、-o manual と、--topics の後ろに /target_velocity、/plant/velocity、/plant/pedal の3つを付けて実行します。

期待する結果、T2 の分です。rosbag2_recorder のログが続きます。スペースキーで一時停止と再開ができる、つまり Press SPACE for pausing/resuming、manual への記録を始める、トピックを探し始めた、という行のあと、3つのトピックについて、Subscribed to topic、つまりトピックを購読した、の行が1つずつ出ます。そのあと、要求されたトピックをすべて購読したので探すのをやめる、つまり All requested topics are subscribed、と出ます。時刻は実行ごとに変わります。

読み方は3つです。

1つ目。-o manual は、記録を書き出すフォルダの名前です。まだ無い名前にします。同じ名前のフォルダがあると、上書きせずに、エラーで止まります。

2つ目。--topics の後ろに、記録するトピックを並べます。Subscribed to topic の行が3つ出て、All requested topics are subscribed と出れば、3つとも記録が始まっています。3つの Subscribed の行の順は、実行ごとに変わります。

3つ目。Press SPACE for pausing/resuming のとおり、T2 でスペースキーを押すと、記録を一時停止、再開できます。

T1 のログで、目標が毎秒10メートル、5メートル、0 と切り替わるのを待ちます。起動から約90秒です。そして、T2、T1 の順に、Ctrl+C で止めます。記録を先に止めるのは、ノードが止まっていく途中の値を、記録に入れないためです。

期待する結果、T2 で Ctrl+C を押した後の分です。記録を一時停止する、残りのメッセージをキャッシュから bag に書き込む、記録を止めた、つまり Recording stopped、という行が出ます。

Recording stopped が出てプロンプトに戻れば、記録はファイルに書き終わっています。

### 2-2. 中身を確かめる、ros2 bag info

T2 で、ros2 bag info に manual を渡します。

期待する結果です。数値は、記録した長さによって変わります。ファイルは manual_0.mcap、大きさは約863キロバイト、ストレージの種類は mcap、ROS の版は jazzy です。Duration、つまり長さは約101.3秒、メッセージは全部で14803個です。トピックの情報として、3つのトピックが並び、型はどれも std_msgs の msg の Float64 で、数は、/plant/pedal が4624、/plant/velocity が9254、/target_velocity が925 です。最後に、サービスは0 と出ます。

表は2列で、3行あります。列は、行と、読み方です。

1行目は、Files と Storage id の行です。記録は、フォルダ manual の中の manual_0.mcap に入っています。MCAP は、Jazzy の ros2 bag が既定で使うファイルの形式です。フォルダには、中身の一覧を書いた metadata.yaml もあります。

2行目は、Duration の行です。最初のメッセージから、最後のメッセージまでの時間です。

3行目は、Count の行で、トピックごとのメッセージの数です。約93秒の記録で、/plant/velocity は約9千で、vehicle_plant が1秒に100回送ります。/plant/pedal は約4千6百で、pi_controller が1秒に50回。/target_velocity は約9百で、target_generator が1秒に10回です。各ノードの周期と、おおよそ合います。

記録の時刻は PC の現在時刻だ、という注記があります。ros2 bag record は、メッセージが届いた時刻を、PC の時計、つまり現在時刻で書き込みます。PC によっては、たとえば WSL2 では、動いている途中で、時計が時刻合わせで数秒ずつ進められることがあります。フェーズ5-1 の9節の表の、ログの時刻が途中で数秒飛ぶ、という症状です。記録の途中で PC の時計が進められると、その分だけ Duration が実際の長さより長くなり、再生したときにも、同じ長さの間があきます。上の例の Duration の101.3秒も、実際に記録した時間の約93秒より長くなっています。形を見比べるには困りませんが、フェーズ6-3 で、時間を使う指標、たとえば整定時間を計算するときには、この点に気をつけます。時計が飛ばない環境では、Duration は実際に記録した時間とほぼ同じになり、フェーズ6 でこの注記に触れる箇所は、気にしなくてかまいません。

### 2-3. 再生する、ros2 bag play

再生する間は、一式を止めたままにしておきます。2-1節で止めたものです。一式が動いていると、再生したメッセージと、ノードが今送っているメッセージが、同じトピックに混ざります。

T1 の ros2 topic echo には、トピックの型、つまり std_msgs の msg の Float64 を書きます。型を書かないと、ros2 topic echo は、起動したときに、ROS2 のネットワークに、そのトピックの送り手か受け手がいるかを1度だけ調べ、そこから型を知ります。この節では一式を止めているので、再生を始める前には、どちらもいません。そのため、型を調べられずに、トピックはまだ送られていないようだ、という WARNING と、渡されたトピックの型を決められなかった、つまり Could not determine the type for the passed topic を表示して、終わってしまいます。型を書けば、送り手がまだいなくても待ち受けを始め、再生が始まると値を表示します。

T1 で、ros2 topic echo の /target_velocity に、型の std_msgs/msg/Float64 と、--field data を付けて実行します。T2 で、ros2 bag play に manual を渡します。

期待する結果、T1 の分の先頭です。0.0 と、区切りの3つのハイフンが交互に並び、値が1つずつ流れます。

期待する結果、T2 の分です。rosbag2_player のログで、再生の速さを1 にした、キーボードの操作を受け付ける、という行のあと、スペースキーで一時停止と再開、右の矢印キーで次のメッセージを1つ再生、上の矢印キーで速さを10パーセント上げる、下の矢印キーで10パーセント下げる、という案内が並び、最後に、Playback until timestamp、つまり再生を終える時刻が、マイナス1 という行が出ます。

読み方は3つです。

1つ目。T1 には、記録したときと同じように、0.0 と区切りが並んだ後、10.0、5.0 の順に値が流れます。10.0 が流れ始めるのは、T1 の launch を起動してから10秒の時点に当たる位置で、2-1節で記録を始めるまでにかかった時間の分だけ、再生を始めてから10秒より早くなります。ノードは1つも動いていないのに、トピックに値が流れています。

2つ目。最後まで再生すると、T2 は何も表示せずに、プロンプトへ戻ります。途中で止めるときは Ctrl+C です。

3つ目。再生中に、T2 でスペースキーを押すと一時停止、再開、上下の矢印キーで、再生の速さを10パーセントずつ変えられます。

よく使うオプションの表は2列で、4行あります。列は、オプションと意味です。

1行目。-r 2 は、2倍の速さで再生します。長い書き方は --rate です。

2行目。--start-offset 45 は、記録の先頭から45秒の位置から再生します。このオプションは6節でも使います。

3行目。-l は、最後まで再生したら、先頭から繰り返します。長い書き方は --loop です。

4行目。-p は、一時停止の状態で始めます。長い書き方は --start-paused で、スペースキーで再生を始めます。3-1節と6節でも使います。

課題1 です。ros2 bag play manual に、-r 5 と --start-offset 45 を付けて再生し、T1 の5.0 が、目標を毎秒5メートルに下げた直後から流れ始めることと、再生が約5分の1の時間で終わることを確かめます。記録を始めるのが遅れた分だけ、5.0 が流れ始める位置は前後します。

## 3. rqt_plot で見直す

### 3-1. 再生した値を描く

フェーズ5-3 の4-3節と同じコマンドで rqt_plot を開いて、再生した値を描きます。

ただし、rqt_plot を開く前に、再生を、一時停止の状態で準備しておきます。2-3節の表の -p です。rqt_plot は、起動したときに、指定されたトピックが ROS2 のネットワークにあるかを調べ、そこから型を知ります。見つからないトピックは、描く対象に加えず、後で再生が始まっても、加え直しません。rqt_plot のソースの plot_widget.py の振る舞いです。一時停止の状態の ros2 bag play は、まだメッセージを送りませんが、トピックの送り手としては、ネットワークに見えているので、rqt_plot が型を調べられます。

T1 で、ros2 bag play manual に -p を付けて実行します。T2 で、ros2 run rqt_plot rqt_plot に、/target_velocity/data、/plant/velocity/data、/plant/pedal/data の3つを渡します。

rqt_plot のウィンドウが開いたら、T1 でスペースキーを押して、再生を始めます。

期待する結果です。rqt_plot のウィンドウに、フェーズ5-3 の4-3節と同じ形の3本の線が描かれていきます。一式を動かしていないのに、記録したときと同じグラフになります。

横軸は、rqt_plot を起動してからの秒数です。rqt_plot のソースの rosplot.py では、メッセージに時刻の欄、つまり header が無い型は、届いた時刻で横軸を決めます。std_msgs の Float64 には、時刻の欄がありません。そのため、rqt_plot を開いてから、スペースキーで再生を始めるまでの時間の分だけ、グラフは右にずれます。

### 3-2. 軸の範囲を決めて、画像に保存する

rqt_plot のウィンドウには、上の段に、rqt_plot 自身の部品が並び、グラフの近くに、グラフを描いている部品、つまり Python のグラフ描画ライブラリの matplotlib の、道具のボタンが並びます。

表は2列で、6行あります。列は、部品と使い方です。

1行目は、autoscroll のチェックボックスです。外すと、横軸が、新しい値に合わせて動かなくなります。拡大して見たいときに外します。

2行目は、一時停止のボタン、つまり pause plot です。描くのを止めます。再生は止まりません。

3行目は、虫眼鏡のボタン、つまり Zoom です。ドラッグで囲んだ範囲を拡大します。

4行目は、軸の設定のボタン、つまり Figure options で、折れ線グラフの形のアイコンです。横軸と縦軸の最小値と最大値を、数で指定します。たとえば縦軸をマイナス1.2 から11 にすると、ペダルと速度の線を、両方読みやすくなります。

5行目は、保存のボタンで、フロッピーディスクの形のアイコンです。今のグラフを、PNG などの画像に保存します。

6行目は、家の形のボタン、つまり Home です。拡大する前の表示に戻します。

期待する結果です。保存のボタンでファイル名を指定すると、そのときに見えているグラフが、そのままの範囲で画像になります。

描画の部品が違う場合の注記があります。rqt_plot は、PyQtGraph というライブラリが入っていればそちらを、無ければ matplotlib を使って描きます。rqt_plot のソースの、data_plot の __init__.py の振る舞いです。手順書を作るときに使った環境には PyQtGraph が無く、matplotlib で描かれました。PyQtGraph で描かれる場合は、ボタンの並びが上の表と違い、グラフの上で右クリックすると、軸の範囲の指定や、画像の書き出しのメニューが出ます。どちらで描くかは、rqt_plot の設定、つまりプラグインの右上の歯車のボタンから選べます。

課題2 です。2-1節で取った記録 manual を再生しながら、目標を毎秒5メートルに下げた前後、つまり記録の45秒から60秒ごろだけを拡大し、縦軸をマイナス1.2 から11 にそろえた画像を保存します。課題1 と同じく、位置には数秒の幅があります。ブレーキ、つまりペダルがマイナス1 を踏んでいる時間が、加速でアクセル、つまりプラス1 を踏んでいた時間より、ずっと短いことを、画像で確かめます。フェーズ5-3 の4-3節の表の話です。

値を CSV に書き出したい場合の注記もあります。グラフで見るだけでなく、記録した値を、表計算ソフトや自分の Python のスクリプトで扱いたいときは、トピックごとの CSV に書き出せます。ros2 bag には書き出しのコマンドが無いので、記録を再生して ros2 topic echo に --csv を付けて受ける方法か、記録のファイルを Python のライブラリ rosbag2_py で直接読む方法を使います。どちらも、Tips集の13節に、4-5節で取る記録 sim_default を例にした手順とサンプルがあります。2-1節の記録 manual でも、同じ手順で書き出せます。

## 4. 決めた時間で記録を終わらせる

2節では、記録を Ctrl+C で止めました。これだと、止めた時刻が毎回ずれて、記録の長さがそろいません。フェーズ6-3 で条件ごとの記録を比べるときは、同じ長さで記録したいところです。

ros2 bag record 自身には、何秒たったら止まる、という指定がありません。-d は、記録のファイルを一定の時間ごとに分けるオプションで、記録は止まりません。そこで、次の2つを組み合わせます。

1つ目。target_generator に、終わる時刻 end_time を持たせます。目標の階段を送り終えたら、ノードが自分で終わります。4-1節です。

2つ目。launch に、target_generator が終わったら launch 全体を止める、という決まりを足します。4-2節です。全体には記録、つまり ros2 bag record も含まれるので、記録もそこで止まります。

### 4-1. target_generator に終わる時刻を持たせる

フェーズ5-3 の2-2節の target_node.py を書き換えます。変わるのは、end_time の宣言と検証、on_timer の最初の4行、on_params の拒否するパラメータの名前、そしてコメントです。

ファイルは、ros2_ws の src の learn_py の learn_py の target_node.py です。

90行ほどのコードで、ブロックは7つです。import、階段の配列を調べる関数 check_steps、Node を継承した TargetGenerator のクラスの __init__、target_at、on_timer、on_params、そして main です。クラスの前のコメントには、起動からの経過時間に応じて階段状に変わる目標速度を target_velocity へ送るノードで、end_time 秒たったら終わる、とあります。

要の行は1か所で、on_params の中で、実行中の変更を拒否するパラメータの名前を、step_times、step_values、period に、end_time を加えた4つにした行です。階段と周期と終わる時刻は、起動のときにだけ決められる、というわけです。

target_node.py の変更点の解説は、3つです。

1つ目は end_time です。既定値は0.0 で、0 のときは終わりません。フェーズ5-3 までと同じ振る舞いです。負の値は、check_steps と同じく、起動のときに ValueError で止めます。

2つ目は、on_timer の最初の4行です。経過時間が end_time を過ぎたら、ログを1行出して、rclpy.shutdown を呼びます。rclpy.shutdown は、このプロセスの ROS2 を終わらせる関数で、main の rclpy.spin は、ROS2 が終わったことに気づいて戻ってきます。その後は、Ctrl+C のときと同じく、finally で後片付けをして、プロセスが終わります。main は変えなくてかまいません。

3つ目。経過時間は、フェーズ5-3 と同じく、単調増加する時計で測っているので、PC の時計が飛んでも、終わる時刻は早まりません。

### 4-2. ノードが終わったら、launch 全体を止める

フェーズ5-3 の3-3節で書いた vehicle_sim.launch.py と、フェーズ5-4 の6-2節で書いた gazebo_plant.launch.py の、2つのファイルを直します。どちらも、ros2_ws の src の learn_bringup の launch にあります。

直すのは2か所です。1か所目は import の行で、launch.actions から読み込むものの最後に、Shutdown を足し、DeclareLaunchArgument、IncludeLaunchDescription、Shutdown の3つにします。2か所目は、target_generator の Node の部分で、package、executable、name、output、parameters を書いた行の後ろに、on_exit=Shutdown() の1行を足します。

説明は3つです。

1つ目。on_exit= は、そのプロセスが終わったときに実行する動作を指定します。Shutdown は、launch 全体を止める動作で、launch は、まだ動いているプロセスすべてに、割り込み、つまり SIGINT を送って止めます。

2つ目。これは、フェーズ4 では扱わなかったイベントハンドラ、つまり何かが起きたときに、決めた動作をする仕組みの、簡単な書き方です。同じことを、RegisterEventHandler に、OnProcessExit を渡し、その target_action にノードを、on_exit に Shutdown の並びを渡す、と書くこともできます。公式ドキュメントの Using event handlers の話で、10節に挙げています。

3つ目。フェーズ5-3 と5-4 の YAML、つまり vehicle_sim.yaml と gazebo_plant.yaml には end_time を書いていないので、既定値の0 のまま、target_generator は終わりません。そのため、この1行を足しても、フェーズ5-3 と5-4 の手順は、これまでどおりに動きます。target_generator が起動のときのエラー、つまりフェーズ5-3 の3-4節の末尾の、配列の型や長さの誤りで止まった場合は、全体が止まります。

### 4-3. 記録用の YAML

フェーズ5-3 と5-4 の YAML を写して、target_generator に end_time を足した、記録用の YAML を作ります。

cd で、ホームの ros2_ws の src の learn_bringup の config に移り、cp で、vehicle_sim.yaml を vehicle_sim_record.yaml に、gazebo_plant.yaml を gazebo_plant_record.yaml に写します。

写したファイルの target_generator の部分に、1行ずつ足します。

vehicle_sim_record.yaml の target_generator の部分は、step_times が10.0、50.0、80.0、step_values が10.0、5.0、0.0 で、そこに end_time の100.0 を足します。

gazebo_plant_record.yaml の target_generator の部分は、step_times が15.0、55.0、85.0、step_values が10.0、5.0、0.0 で、そこに end_time の105.0 を足します。

どちらも、目標を0 にしてから20秒後に終わります。ファイルの先頭のコメントの行も、記録用と分かるように書き換えておくとよい、とあります。

### 4-4. 記録用の launch、record.launch.py

ファイルは、ros2_ws の src の learn_bringup の launch の record.launch.py です。

35行ほどのコードで、ブロックは、import と、generate_launch_description の関数の2つです。関数の前のコメントには、フェーズ5-3 の vehicle_sim か、フェーズ5-4 の gazebo_plant の一式を、記録用の YAML で起動し、目標、速度、ペダルを ros2 bag record で記録する、とあります。

関数は、まず4つの変数を用意します。引数 scenario の値、learn_bringup のパッケージの share のフォルダ、取り込む launch のファイルのパス、そして記録用の YAML のパスです。そのあと、LaunchDescription に5つの要素を並べて返します。引数の宣言が3つ、つまり scenario、bag、params_file、一式の launch の取り込みが1つ、ros2 bag record を起動する ExecuteProcess が1つです。

要の行は1か所で、一式の launch を取り込むときの launch_arguments で、params_file に、この launch の引数 params_file の値を、そのまま渡す行です。この行があるので、record.launch.py に渡した YAML が、取り込んだ一式の各ノードに届き、4-6節で YAML を差し替えられます。

record.launch.py の解説です。役割は、フェーズ5-3 か5-4 の一式を、記録用の YAML で起動し、同時に ros2 bag record も起動することです。止めるのは、4-2節で一式の側に足した on_exit=Shutdown() の役目で、このファイルには、止める仕組みを書いていません。

表は2列で、5行あります。列は、部分と、何をしているか、です。

1行目は、scenario と、文字列の .launch.py を並べたリストの部分です。置換、つまり LaunchConfiguration と、文字列を並べたリストは、つながって1つの文字列になります。フェーズ5-4 の6-2節の gz_args と同じです。scenario:=gazebo_plant なら、gazebo_plant.launch.py と gazebo_plant_record.yaml になります。ファイル名の付け方をそろえておくと、引数1つで、両方を切り替えられます。

2行目は、bag の DeclareLaunchArgument です。既定値の無い引数で、起動するときに、bag:= を必ず指定します。指定しないと、エラーで止まります。記録のフォルダの名前を、毎回自分で決めるためです。

3行目は、params_file の DeclareLaunchArgument です。既定は記録用の YAML です。条件を変えた記録を取るときは、別の YAML に差し替えます。4-6節です。

4行目は、launch_arguments に、gazebo を false として渡す部分です。取り込む側の引数を渡します。gazebo は vehicle_sim.launch.py の引数で、記録では、表示用の Gazebo を外します。gazebo_plant.launch.py には、この引数がありませんが、使われない値を渡しても、問題はありません。

5行目は、ExecuteProcess の cmd に ros2 bag record を渡す部分です。ROS2 のノードではないコマンドを、launch から起動します。ros2 bag record も、ほかのプロセスと同じく、Shutdown で割り込みを受けて止まります。

### 4-5. ビルドして、記録する

learn_bringup の CMakeLists.txt は変えなくてかまいません。launch と config の中の新しいファイルも、フェーズ4 の3-3節の install の DIRECTORY でインストールされます。ただ、新しいファイルなので、ビルドは要ります。

cd でホームの ros2_ws に移り、colcon build に、--symlink-install と、--packages-select の learn_py と learn_bringup を付けてビルドし、source install/setup.bash をしてから、ros2 launch learn_bringup record.launch.py に --show-args を付けて実行します。

期待する結果です。ビルドは、2つのパッケージについて Finished が出て、2つのパッケージが終わった、という要約で終われば成功です。--show-args は、3つの引数を、説明付きで並べます。scenario は、記録する一式、vehicle_sim または gazebo_plant、という説明で、既定は vehicle_sim です。bag は、記録を書き出すフォルダ、まだ無い名前にする、という説明です。params_file は、各ノードのパラメータを書いた YAML ファイル、既定は scenario の名前に _record.yaml を付けたもの、という説明で、既定値は、learn_bringup の share を探して、config と、scenario の値に _record.yaml をつないだものを並べる置換の式として表示されます。

読み方は2つです。

1つ目。bag には、既定値の行がありません。既定値の無い、必ず指定する引数です。

2つ目。フェーズ5-3 の3-4節と違い、取り込んだ launch の引数、たとえば gazebo は並びません。取り込むファイルの名前が scenario の値で決まり、起動するまで、どのファイルか分からないためです。

記録します。ros2 launch learn_bringup record.launch.py に、bag:= で、ドル記号の HOME の ros2_ws の bags の sim_default を渡します。

期待する結果、抜粋です。vehicle_plant と pi_controller のログは省いてあり、時刻、pid、パスは実行ごとに変わります。まず、vehicle_plant-1、pi_controller-2、target_generator-3、ros2-4 の4つのプロセスが起動し、ros2-4 が、sim_default への記録を始める、と出します。target_generator は、0.1秒で目標を0.00 にし、記録の側は、要求されたトピックをすべて購読した、と出します。そのあと、target_generator が、10.1秒で目標を毎秒10メートルに、50.0秒で5メートルに、80.0秒で0 にした、と出し、100.0秒で、end_time に達したので終わる、つまり end_time reached, shutting down と出します。続いて、target_generator-3 がきれいに終わった、つまり finished cleanly、そして launch が、target_generator-3 について、止めることになっていたプロセスが終わったので、起動したシステムを止める、と出します。ros2-4、pi_controller-2、vehicle_plant-1 に SIGINT を送った、という行が続き、記録の側が Recording stopped を出し、残りの3つのプロセスも finished cleanly で終わります。

読み方は4つです。

1つ目。ros2 bag record は、ros2-4 という名前のプロセスとして起動します。ros2 のコマンドとして起動したためです。

2つ目。100秒たつと、target_generator が end_time reached を出して終わり、launch が、was required: shutting down launched system、つまり止めることになっていたプロセスが終わったので全体を止める、と出して、残りのプロセスに割り込みを送ります。記録は Recording stopped で閉じられ、launch もプロンプトに戻ります。

3つ目。手で Ctrl+C を押したときと違い、Python のノードに Traceback は出ず、すべて finished cleanly で終わります。フェーズ5-3 の4-4節で見た Traceback は、端末と launch から、割り込みが2回届いたためでした。ここでは割り込みが launch から1回だけ届くので、後片付けが中断されません。

4つ目。行の先頭の秒数、つまり target_generator の経過時間は、単調増加する時計で測っているので、PC の時計が飛ぶ環境でも飛びません。ログの時刻のほうは、飛ぶことがあります。2-2節の注記の話です。

終わったら、2-2節と同じく、ros2 bag info で中身を確かめられます。何度記録しても、目標の切り替えと記録の長さがそろいます。

### 4-6. 条件を変えた記録も取る

フェーズ6-3 では、条件の違う記録を比べます。そのために、ブレーキの遅れ tau_brake を1.0秒にした記録を、もう1つ取っておきます。フェーズ5-3 の4-5節と同じ条件です。

フェーズ5-3 の4-5節の slow_brake.yaml と同じく、ホームの ros2_ws の config に、記録用の YAML を写して、vehicle_plant の tau_brake の0.2 を、1.0 に書き換えます。cp で、learn_bringup の config の vehicle_sim_record.yaml を、ros2_ws の config の slow_brake_record.yaml に写します。

書き換えたら、params_file:= で渡して記録します。チルダではなく、ドル記号の HOME と書く理由は、フェーズ5-3 の4-5節にあります。YAML を絶対パスで渡すので、この YAML のためにビルドし直す必要はありません。ros2 launch learn_bringup record.launch.py に、params_file:= で、HOME の ros2_ws の config の slow_brake_record.yaml を、bag:= で、HOME の ros2_ws の bags の slow_brake を渡します。

期待する結果、抜粋です。target_generator と記録のログと、止まる部分だけです。target_generator が0.1秒で目標0.00 を出し、記録の側が slow_brake への記録を始め、10.0秒、50.0秒、80.0秒で目標を切り替え、100.0秒で end_time reached を出します。launch が、起動したシステムを止める、と出し、記録の側が Recording stopped を出します。

4-5節と同じく、100秒で止まれば記録できています。YAML の end_time と目標の階段は vehicle_sim_record.yaml と同じなので、sim_default と同じ長さの記録になり、違うのはブレーキの遅れだけです。この記録 slow_brake は、6節の末尾の課題3 と、フェーズ6-3 で使います。

## 5. フェーズ5-4 の一式も記録する

同じ launch で、scenario:=gazebo_plant を指定します。Gazebo のウィンドウが開きます。ros2 launch learn_bringup record.launch.py に、scenario:=gazebo_plant と、bag:= で、HOME の ros2_ws の bags の gz_default を渡します。

期待する結果、止まる部分だけの抜粋です。target_generator-5 が、105.1秒で end_time reached を出し、finished cleanly で終わります。launch が、起動したシステムを止める、と出し、ros2-6、pi_controller-4、gz_plant-3、parameter_bridge-2、gazebo-1 に SIGINT を送ります。parameter_bridge、ros2、pi_controller、gz_plant は finished cleanly で終わります。gazebo-1 だけは、ERROR として、SIGINT を受けてから5秒たっても止まらなかったので SIGTERM に強める、と出て、SIGTERM を送った、という行のあと、ERROR として、プロセスが終了コード マイナス15 で死んだ、と出ます。

読み方は4つです。

1つ目。105秒たつと、4-5節と同じ流れで全体が止まり、Gazebo のウィンドウも閉じます。

2つ目。Gazebo は、割り込み、つまり SIGINT を受けてから5秒以内に止まらなかったので、launch が、より強い止める合図、つまり SIGTERM を送り直しています。ERROR の行が出ますが、記録は先に閉じられているので、問題ありません。

3つ目。ただし、Gazebo の本体、つまり gz sim のサーバーが、この後も裏で動き続けることがあります。残ったままだと、次に起動したときに、車両が2台ずつ見えるなど、動きがおかしくなります。記録が終わったら、この節の末尾の手順で確かめます。

4つ目。PC が重い場合は、フェーズ5-4 の6-3節の、PC が重い場合、と同じく、gz_args に -s、つまり画面なしを足して記録できます。record.launch.py に指定した gz_args:= は、取り込んだ gazebo_plant.launch.py に、そのまま渡ります。手順書を作るときの確認は、この方法で行った、とあります。

フェーズ5-4 の記録の時刻についての注記があります。フェーズ5-4 の一式は、シミュレーション時刻で動いています。フェーズ5-4 の5節の話です。一方、target_generator は現実の時間で目標を切り替え、ros2 bag record も現実の時刻で記録します。Gazebo の計算が PC の負荷で現実より遅れている、つまり RTF が100パーセントを下回ると、記録の中の車両の動きは、現実の時間で見て、少しゆっくりになります。この手順書では、記録を現実の時刻のまま扱います。ros2 bag record には、シミュレーション時刻で記録する --use-sim-time もあります。

記録が終わったら、Gazebo の本体が残っていないかを確かめ、残っていれば止めます。pgrep -af は、コマンドの行に gz sim を含むプロセスを、番号の pid と、コマンドの行の全体で一覧にします。pkill -INT -f は、同じ条件に合うプロセスに、Ctrl+C と同じ割り込みの SIGINT を送って止めます。条件に合うプロセスはすべて止まるので、pkill の前に、1回目の pgrep に出た行が、Gazebo の gz sim の行だけであることを確かめます。

pgrep -af に、引用符で囲んだ gz sim を渡し、pkill -INT -f に、同じく gz sim を渡し、もう一度 pgrep -af を実行します。

期待する結果、Gazebo が残っていた場合の例です。pid とパスは実行ごとに変わり、行の形は環境によって違うことがあります。1回目の pgrep には、pid と、ruby で gz sim を、-r と、worlds の vehicle_force.sdf と、--force-version 8 を付けて動かしている、というコマンドの行が1行出ます。pkill は何も表示せず、2回目の pgrep も何も表示しません。

読み方は2つです。

1つ目。1回目の pgrep で行が出れば、Gazebo が残っています。同じコマンドの行が複数出ることもあります。Gazebo の本体が、内部でサーバーと画面のプロセスに分かれるためです。何も出なければ、残っていないので、pkill は要りません。

2つ目。pkill は、止めたときに何も表示しません。止まるまで数秒かかることがあるので、少し待ってから、2回目の pgrep を実行します。何も出なければ、止まっています。

## 6. 2つの記録を重ねる

4-5節の sim_default、つまりフェーズ5-3 と、5節の gz_default、つまりフェーズ5-4 を、同時に再生して、1つのグラフに重ねます。フェーズ5-4 の記録のトピックは、再生するときに、/gz で始まる名前に付け替えて、フェーズ5-3 と混ざらないようにします。

重ねる前に、予想しておきます。フェーズ5-4 の7節の表から、次の2点は、グラフのどこにどう表れるでしょうか。1つ目は、フェーズ5-4 は、目標の毎秒10メートルを少し行き過ぎること。2つ目は、目標の毎秒10メートルで落ち着いたときのペダルが、フェーズ5-3 は0.54、フェーズ5-4 はほぼ0 であることです。

ターミナルを3つ使います。3-1節と同じ理由で、T1 と T2 で、2つの再生を一時停止の状態で準備してから、T3 で rqt_plot を開きます。

T1 では、ホームの ros2_ws の bags に移り、ros2 bag play に sim_default と -p を付けて実行します。

T2 では、同じフォルダで、ros2 bag play に gz_default を渡し、-p と、--start-offset 5 と、--remap を付けます。--remap の後ろには、/target_velocity を /gz/target_velocity に、/plant/velocity を /gz/plant/velocity に、/plant/pedal を /gz/plant/pedal に付け替える指定と、最後に __node:=player_gz を並べます。

T3 では、ros2 run rqt_plot rqt_plot に、/target_velocity/data、/plant/velocity/data、/gz/plant/velocity/data、/plant/pedal/data、/gz/plant/pedal/data の5つを渡します。

rqt_plot のウィンドウが開いたら、T1 と T2 で、スペースキーを、なるべく続けて押して、2つの再生を始めます。

説明は3つです。

1つ目は、--start-offset 5 です。フェーズ5-4 の記録は、目標の最初の切り替えが15秒、フェーズ5-3 は10秒なので、先頭の5秒を飛ばして、切り替えの時刻をそろえます。

2つ目は、--remap に、元の名前:= 新しい名前、を並べる指定です。再生するトピックの名前を付け替えます。最後の __node:=player_gz は、トピックではなく、再生するノード自身の名前を付け替える指定で、2つの再生のノードの名前が重ならないようにします。どちらも、既定は rosbag2_player です。

3つ目。/gz/target_velocity は、--start-offset でフェーズ5-3 とそろえてあるので、グラフには描きません。

再生している間に、別のターミナルでノードの一覧を見ると、再生のノードが2つと、rqt_plot のノードが並びます。T4 で、ros2 node list を実行します。

期待する結果です。/player_gz、/rosbag2_player、そして rqt_gui_py_node_ の後ろに数字の付いたノード、の3つが並びます。後ろの数字は実行ごとに変わり、rqt_plot のプロセスの番号です。

期待する結果、rqt_plot の分です。手順書を作るときに取った2つの記録から読み出した数値をもとに、筆者が想定した形です。目標を毎秒10メートルにした後、2本の速度の線は、最初の2秒ほどは、ほぼ重なって上がります。その後、フェーズ5-3 の線は曲がり始めます。速度に比例する抵抗が効いてくるためです。約8秒で毎秒9.3メートルになってから、20秒ほどかけて、ゆっくり10 に近づきます。フェーズ5-4 の線は、ほぼまっすぐ上がり続け、約6秒で10 を少し超え、最高で毎秒10.3メートルになり、すぐ10 に戻ります。ペダルの線は、フェーズ5-3 がプラス1 から下がって、プラス0.54 の高さで平らになり、フェーズ5-4 は、約5秒でプラス1 から一気に下がって、0 の付近で平らになります。目標を毎秒5メートルに下げた直後は、フェーズ5-4 の速度の線だけが、5 を少し下回り、最低で毎秒4.5メートルになります。

注意が2つあります。

1つ目。T1 と T2 の再生を手で続けて始めるので、2つの記録には、1秒ほどの時間のずれが残ります。形を見比べるには十分で、正確に比べるのは、フェーズ6-3 で数にしてから行います。

2つ目。5節の注記のとおり、フェーズ5-4 の記録は、PC の負荷によって、車両の動きが少しゆっくりになっていることがあります。目標の切り替えは現実の時間で行っているので、切り替えの位置はずれず、切り替えた後の速度の変わり方が、フェーズ5-3 の線よりゆっくりに見えます。切り替えの位置が左右にずれる原因は、1つ目の、手で再生を始めるずれと、2-2節の注記の、記録ごとに違う PC の時計の飛びです。

課題3 です。4-6節で記録した slow_brake を、/gz の代わりに /slow で始まる名前に付け替えて、sim_default と重ねます。目標を毎秒5メートルに下げたとき、tau_brake が1.0 の速度の線だけが、毎秒4メートル前後まで下がりすぎる様子を確かめます。フェーズ5-3 の4-5節の話です。

## 7. 本フェーズのまとめ

5つあります。

1つ目。ros2 bag record に、-o でフォルダを、--topics でトピックを指定して記録し、ros2 bag info で中身、つまり長さとトピックごとの数を確かめ、ros2 bag play で再生できます。再生すると、ノードを動かさずに、記録したときと同じメッセージが、同じ間隔で流れます。

2つ目。記録の時刻は PC の現在時刻なので、PC の時計が飛ぶと、記録の長さや再生の間隔にも表れます。

3つ目。rqt_plot は、再生した値も、そのまま描けます。autoscroll を外し、軸の範囲を決めて、画像に保存できます。

4つ目。launch の on_exit=Shutdown() で、あるプロセスが終わったら、全体を止められます。target_generator に終わる時刻を持たせると、ros2 bag record を含めた一式が、決めた時間で止まり、同じ長さの記録がそろいます。

5つ目。ros2 bag play の --remap でトピック名を、__node:= でノード名を付け替えれば、2つの記録を同時に再生して重ねられます。--start-offset で、記録の先頭をそろえられます。

## 8. つまずきやすい点

表は2列で、9行あります。列は、症状と、確認することです。

1行目。ros2 bag record がすぐにエラーで止まる場合です。-o のフォルダがすでにあります。別の名前にするか、要らない記録のフォルダを消します。

2行目。記録の Count が0 のトピックがある場合です。記録している間に、そのトピックを送るノードが動いていたか。トピック名の綴りを確かめます。

3行目。再生の前に起動した ros2 topic echo が、does not appear to be published yet、つまりまだ送られていないようだ、の後に、Could not determine the type for the passed topic と出て終わる場合です。トピックの型、つまり std_msgs/msg/Float64 を書いたかを確かめます。2-3節の話です。型を書かないと、トピックの送り手も受け手もいないうちは、型を調べられません。

4行目。再生した値が、ほかの値と混ざる、ギザギザになる場合です。再生する前に、同じトピックを送る一式を止めたかを確かめます。2-3節です。

5行目。rqt_plot に線が出ない場合です。rqt_plot のトピックの指定が、トピック名の後ろに /data を付けた形になっているか。付け替えた記録は、付け替えた後の、/gz で始まる名前で指定します。rqt_plot を、ros2 bag play の -p より先に開いていないか。これは3-1節の話です。そのときは、ウィンドウの Topic の欄から足すか、rqt_plot を閉じて開き直します。フェーズ5-3 の4-3節の注記の話です。

6行目。record.launch.py が、bag の指定が無いと言って止まる場合です。bag:= でフォルダを指定します。4-4節です。チルダではなく、ドル記号の HOME か、絶対パスで書きます。

7行目。決めた時間になっても止まらない場合です。使っている YAML に end_time があるか。これは4-3節の話です。launch の target_generator の Node に on_exit=Shutdown() を足して、ビルドし直したか。これは4-2節の話です。

8行目。記録の後も Gazebo が残る場合、つまり次に起動したとき、車両が2台ずつ見える、動きがおかしい場合です。前回の gz sim のサーバーが、裏で動き続けています。pgrep -af の gz sim で確かめ、残っていれば pkill -INT -f の gz sim で止めます。5節の末尾の話です。

9行目。2つの記録の線が、大きく左右にずれる場合です。T1 と T2 のスペースキーを、続けて押したか。フェーズ5-4 の記録に、--start-offset 5 を付けたかを確かめます。6節の話です。

## 9. 次へ

フェーズ6-3、記録から指標を計算して比べる、で、この手順書で取った記録から、行き過ぎ量や整定時間などの指標を計算して、条件ごとに比べます。任意の寄り道のフェーズ6-2、条件で記録を終わらせる、では、時間の代わりに、車両がゴールの地点に着いたことをきっかけに、記録を終わらせます。フェーズ6-3 は、フェーズ6-2 を読んでいなくても進められます。作成の状況は、学習計画の、手順書一覧で確かめられます。

## 10. 公式のドキュメントと参考資料

確かめた状況は、2026年9月27日の時点です。公式の3つは、GitHub にある文書のソース、つまり ros2 の ros2_documentation の jazzy のブランチと、ros2 の rosbag2 の jazzy のブランチの README が、実在することを確かめました。ros2 bag のオプションは、手元の環境の ros2 bag record と ros2 bag play の -h、つまりヘルプで確かめました。rqt_plot の横軸と、描画の部品の選び方は、手元の環境に導入した rqt_plot のソースで確かめました。

公式の資料は3つです。

1つ目は、ROS 2 Documentation の Jazzy の、Recording and playing back data です。ros2 bag の record、info、play の基本です。

2つ目は、同じく Using event handlers です。RegisterEventHandler、OnProcessExit、Shutdown など、launch のイベントハンドラを扱います。

3つ目は、GitHub の ros2 の rosbag2 の、jazzy のブランチの README です。ros2 bag のオプションの一覧と、記録のファイルの形式があります。

原文の最後には、出典の注記があります。ros2 bag と rqt_plot の振る舞いは、公式ドキュメント、手元の環境のヘルプとソース、使い捨ての環境で実行した結果から、筆者が自分の言葉でまとめたものです。サンプルコードと文章は、独自に書いたもの、とあります。

以上で、フェーズ6-1 の話を終わります。

## 出典について

この原稿は、SanghunIm1991 さんの [ros2MinimalPhysicalAi の「フェーズ6-1 手順書: 記録して見直す（ros2 bag と rqt_plot）」](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/docs/phase6_1_record.md)を、聞くために要約・意訳したものです。図の [phase6_1_record.svg](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/docs/img/phase6_1_record.svg) は、言葉で説明しました。元にしたのは、[2026年10月17日の版](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/41d2c800082a372a810d286ded1bb56d9c05b67e/docs/phase6_1_record.md)です。原文の文章と図と同じく、[クリエイティブ・コモンズ 表示 4.0 国際ライセンス](https://creativecommons.org/licenses/by/4.0/deed.ja)で提供します。

原稿の中に原文の表記のまま書いたコマンドと、コードの関数やクラスの名前は、原文では [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0) の対象です。ライセンスの全文は、原文のリポジトリの [LICENSE-APACHE-2.0](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/LICENSE-APACHE-2.0) にあります。サンプルコードは写さず、構成と要の行を言葉で説明しました。

期待する結果の表示の例は、原文では、rosbag2・ros2 のコマンド・launch・colcon・pgrep などの各ツールの表示で（rqt_plot の結果は、筆者が想定した形を文章で書いたもの）、この原稿では、写さずに言葉で説明しました。原文では、ros2 bag と rqt_plot の振る舞いを、[ROS 2 Documentation](https://docs.ros.org/en/jazzy/)（Open Robotics、CC BY 4.0）の公式ドキュメントと、ヘルプとソースと実行した結果から、筆者が自分の言葉でまとめたとしています。
