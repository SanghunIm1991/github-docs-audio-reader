<!--
聞くための原稿（読み上げでは読まれない記録）
原文: SanghunIm1991/ros2MinimalPhysicalAi の main ブランチの docs/phase3_5_actions.md（図は docs/img/phase3_5_action_seq.svg と docs/img/phase3_5_goal_states.svg）
原文のコミット: 86dc0ed3d606c4a05d1e087421bb10318a37e521（2026-10-14）
作成: 2026-10-20、Claude Code が手作業で作成（原稿化スキルはまだない）
原文のライセンス: 文章と図は CC BY 4.0、コードとコマンドは Apache-2.0（LICENSE の1と2）。ros2 interface show で表示する型の定義（example_interfaces、Apache License 2.0）は、LICENSE の「第三者の著作物」にある。原文の末尾に、API の使い方は公式チュートリアル（ROS 2 Documentation、CC BY 4.0）を参考にした、とある。この原稿は、原文を聞くために要約・意訳したもの（改変あり）
方針: 英語の略語や製品名、関数やクラスの名前、短いコマンドは原文の表記のまま書く。サンプルコード4本と、package.xml・CMakeLists.txt・setup.py に足す行は、写さずに、ブロックの役割と要の行を言葉で説明した。型の定義は写さず、項目の名前と型だけを言葉で書いた。期待する結果（ログ、ros2 action の表示）も、何が表示されるかを言葉で説明した。図と表（サービスとの違い、仕様、主な API、Python版と C++版の対応、言語の組み合わせ、違いのまとめ、つまずきやすい点）は言葉で説明する。文字数の上限は設けない
省いたもの: URL、型の定義へのリンク、ログの時刻の数字、ゴールの ID
-->

# フェーズ3-5: アクション、つまり途中経過つきで中断できる長い処理（聞くための原稿）

これは、ros2MinimalPhysicalAi という教材の、フェーズ3-5 の手順書の話です。時間のかかる処理に対して、ゴールの送信、途中経過、つまりフィードバック、最終の結果、そして中断を扱う通信、アクションを扱います。概要をつかむ程度でよく、サンプルは Python の版と C++ の版の両方が載っています。

想定する環境は、WSL2 と Ubuntu 24.04 と ROS2 Jazzy です。前提は、フェーズ3-1 から3-3 を終えていることです。フェーズ3-4 のサービスは任意で、済ませていなくてかまいません。サービスは、フェーズ1 の3-5節でコマンドラインから使った、要求から応答の通信のことです。所要時間の目安は、概要をつかむだけなら半コマで、1節、2節、6-1節を読みます。サンプルまで書いて動かす場合は、コードの量が多いので2コマです。言語は、サンプルは Python と C++ の両方で、作る場合も C++ の版は任意です。使う標準のインターフェースは、example_interfaces の action の Fibonacci で、WSL の /opt/ros/jazzy の下の share の example_interfaces の action にある、Fibonacci.action のファイルで中身を確かめてあります。

原文には、位置づけの囲みがあります。アクションは、このプロジェクトのゴールであるフェーズ5 の車両のシミュレーションでは使いません。フェーズ5 は、プラント、PI 制御、目標の速度の3つのノードをトピックでつなぎ、ゲインをパラメータで調整します。ここで身に付けたいのは、アクションは、時間のかかる処理に、ゴール、途中経過の feedback、結果の result、中断の cancel を付けた通信で、サービスとはこう使い分ける、という考え方までです。ナビゲーションの Nav2 や、アームの軌道の実行など、将来アクションを使う OSS に触れたときに、何をしているかが分かれば十分です。

概要だけをつかむ場合は、1節の全体像、2節の仕様、6-1節のコマンドラインから使う所の期待する結果、の順に読めばよい、とあります。サービスとの使い分けは、1節の表にあります。7節の違いのまとめは、4節と5節のサンプルを読んだ人に向けたものです。3節から5節のサンプルコード、特に C++ の版と、中断を受け付けるための実行の仕組み、つまりマルチスレッドの executor や別のスレッドは、余力があるときの発展として扱ってかまいません。フェーズ1 の3-7節で、turtlesim のアクションの rotate_absolute を、コマンドラインから一度使っているので、その体験と結び付けて読むと分かりやすい、とあります。

サンプルまで書いて動かす場合の進め方です。今までより長いので、まず Python を完成させ、動きを理解してから C++ に進みます。主な API の表で、サーバとクライアントの作り方、goal_handle のプロパティとメソッドをつかみ、サンプルコードと解説を読んで理解します。分かったら、フィボナッチの数列の代わりに別の計算にする、フィードバックの頻度を変える、などの改造をすると身に付きます。サンプルは、手順書を作るときにビルドを確かめ、手順は2026年9月27日に実機で確かめています。期待する結果は、実機で手順を実行して問題が無いことを確かめてありますが、表示を1つずつ見比べてはいない、とあります。時刻や ID などの細部は、実行ごとに違います。

この原稿では、サンプルコードと型の定義を書き写さず、役割と要の行を言葉で説明します。

## 0. 学習目標と完了の条件

必須、つまり概要をつかむための条件は2つです。

1つ目。ゴール、フィードバック、結果、中断、つまり goal、feedback、result、cancel の流れを説明できる。

2つ目。サービスとアクションの使い分けを説明できる。

任意の発展の条件も2つです。3つ目は、アクションのサーバとクライアントを、Python と C++ の両方で書けること。4つ目は、サーバの処理の途中で中断の要求を受け付けるために、実行の仕組み、つまり Python ではマルチスレッドの executor、C++ では別のスレッドが必要なことを説明できることです。

## 1. 全体像

原文の図は2つで、どちらも SVG と mermaid の版があります。

1つ目の図は、ゴールの送信から結果までの流れを表すシーケンス図です。左に fibonacci_client、右に fibonacci_server の箱があり、それぞれから下へ点線が伸びています。まず、クライアントからサーバへ、「goal、order が5、を送る」の矢印があります。次に、サーバからクライアントへ、点線で「受理、accepted」が返ります。その下に、「1秒ごとに」と書かれた loop の枠があり、その中で、サーバからクライアントへ、点線で「feedback、途中までの数列」が送られます。枠の下で、サーバからクライアントへ、点線で「result、完成した数列と、status が SUCCEEDED」が返ります。一番下に黄色の注記があり、途中でクライアントが cancel を送ると、サーバは処理を止めて CANCELED を返す、と書かれています。

2つ目の図は、ゴールの状態の移り変わりを表す状態遷移図です。左端の黒い丸、つまり始まりから、「ゴール受理」の矢印で ACCEPTED の箱へ進み、「実行開始」の矢印で EXECUTING の箱へ進みます。EXECUTING からは、矢印が3本に分かれます。上へ曲がる矢印は「完了」で、SUCCEEDED へ。まっすぐ右の矢印は「中断要求」で、CANCELING へ進み、そこから「中断完了」の矢印で CANCELED へ。下へ曲がる矢印は「サーバが失敗と判断」で、ABORTED へ。SUCCEEDED、CANCELED、ABORTED の3つの箱から、それぞれ右端の、二重の丸、つまり終わりへ矢印が出ています。

次に、インターフェースを確かめます。ros2 interface show で、example_interfaces/action/Fibonacci を表示します。

期待する結果は、こうです。型の定義は、ハイフン3つの行で、3つに分かれています。上から、ゴールが int32 の order、結果が int32 の配列の sequence、フィードバックも int32 の配列の sequence です。それぞれの段の先頭に、Goal、Result、Feedback という見出しのコメントがあります。int32 の後に角括弧を付けたものは、整数の配列で、長さは自由、という意味です。

サービスとの違いは、観点、サービス、アクションの3列の表で、3行にまとめられています。途中経過は、サービスには無く、アクションには feedback が有る。中断は、サービスではできず、アクションでは cancel でできる。向く処理は、サービスは短いもの、アクションは数秒から数分かかるもの、です。

## 2. 仕様

仕様は、ノード、役割、アクションの名前と型、動作、の4列の表で、2行あります。

1行目、fibonacci_server。役割はサーバ。アクションの名前は fibonacci で、型は example_interfaces/action/Fibonacci。動作は、こうです。1以上のゴールの order を受け、0 と1 の数列から始めて、1秒ごとに次の項を足し、その時点の数列をフィードバックとして送る。order 引く1 回の足し算を終えたら、結果に完成した数列、つまり order 足す1 項を入れて、成功で終わる。order が1 より小さいゴールは拒否する。処理の途中で中断の要求を受けたら、処理を止めて、CANCELED で終わる。

2行目、fibonacci_client。役割はクライアント。アクションの名前は fibonacci。動作は、こうです。ROS のパラメータの order、つまり整数で既定は5 で、ゴールを送り、フィードバックをログに出し、結果を受けて終わる。パラメータの cancel_after、つまり秒の実数で既定は0.0 が正なら、ゴールが受理されてからその秒数の後に、中断の要求を送る。サーバがいなければ、5秒待ってあきらめる。

例えば order が5 なら、結果の数列は、0、1、1、2、3、5 の6項です。

## 3. 準備: 依存の追加

Python では、learn_py の package.xml に、action_msgs の depend の行を足します。action_msgs は、クライアントが結果の状態、つまり成功や中断などを表す型、action_msgs の msg の GoalStatus を使うために要ります。

C++ では、learn_cpp の package.xml に、rclcpp_action の depend の行を足します。rclcpp_action は、C++ でアクションのサーバとクライアントを作るためのライブラリです。CMakeLists.txt の、すでにある find_package の並びにも、rclcpp_action の find_package を、REQUIRED を付けて足します。

example_interfaces の依存は、フェーズ3-4 を飛ばした場合だけ必要です。使うアクションの型の Fibonacci は、example_interfaces のパッケージのものです。フェーズ3-4 の3節を済ませていれば、依存は足してあるので、読み飛ばしてかまいません。飛ばした場合は、package.xml に example_interfaces の depend の行を足します。Python の版は learn_py に、C++ の版を作る場合は learn_cpp にも足します。C++ の版を作る場合は、CMakeLists.txt に example_interfaces の find_package も足します。これが無いと、5節の ament_target_dependencies で、ビルドがエラーになります。example_interfaces は Desktop Install に含まれていて、1節の ros2 interface show で定義が表示されれば、導入済みです。

## 4. Python の版、learn_py

learn_py の内側の learn_py のフォルダに、fibonacci_server.py と fibonacci_client.py を作ります。

主な API は、やりたいことと API の2列の表で、9行あります。

サーバを作るには、ActionServer に、ノード、型、アクションの名前と、キーワードの引数で、execute_callback、goal_callback、cancel_callback を渡す。

ゴールを受けるかを決めるのは goal_callback で、GoalResponse の ACCEPT か REJECT を返す。

中断を受けるかを決めるのは cancel_callback で、CancelResponse の ACCEPT か REJECT を返す。

実行の処理は execute_callback で、goal_handle を受け取る。goal_handle の request が、受けたゴールです。goal_handle の publish_feedback でフィードバックを送り、succeed() か canceled() を呼び、最後に結果を返します。

中断を見つけるのは、goal_handle の is_cancel_requested。

クライアントを作るには、ActionClient に、ノード、型、アクションの名前を渡す。

ゴールを送るには、client の send_goal_async に、ゴールと feedback_callback を渡す。Future を返します。

結果を得るには、goal_handle の get_result_async() を呼ぶ。Future を返し、add_done_callback で受けます。

中断を要求するには、goal_handle の cancel_goal_async() を呼ぶ。

表の Future は、後で結果が入る入れ物です。送った関数はすぐ戻り、返事が届くと、この入れ物に結果が入ります。add_done_callback は、結果が入ったらこの関数を呼んでほしい、という登録です。

重要、という囲みもあります。中断の仕組みについてです。サーバの実行の処理が time.sleep で待っている間、普通の単一のスレッドの executor では、ほかのコールバック、つまり中断の要求の受け付けが動けません。そこで、MultiThreadedExecutor と ReentrantCallbackGroup を使い、実行の処理と並行して、中断の要求を処理できるようにします。C++ の版では、代わりに、実行の処理を別のスレッドで行います。

### fibonacci_server.py

fibonacci_server.py は、60行あまりのコードです。ブロックは、クラスの __init__、3つのコールバック、つまりゴールを受けるかを決める on_goal、中断を受けるかを決める on_cancel、実行の本体の execute、そして main です。要の行は3つです。__init__ で ActionServer に、3つのコールバックと、callback_group に ReentrantCallbackGroup() を渡す行。execute のループの中で、is_cancel_requested を確かめる行と、publish_feedback で途中経過を送る行。そして main で、rclpy.spin に MultiThreadedExecutor を渡す行です。

原文の解説の要点です。役割は、ゴールを受け、1秒ごとに数列を伸ばしながら feedback を返し、最後に result を返すことです。流れは4段です。1つ目、ゴールが届くと on_goal が受理か拒否かを決める。2つ目、受理されたら、つまり ACCEPTED なら、execute が呼ばれて実行に入る、つまり EXECUTING。3つ目、ループの各回で中断の要求を確かめ、無ければ項を足して feedback を出し、1秒待つ。4つ目、終われば succeed() で SUCCEEDED、中断の要求があれば canceled() で CANCELED、のどちらかで終わる。1節の状態遷移図のうち、サーバの側が受け持つのがこの部分です。

ActionServer の引数。1つ目から3つ目は、ノード、アクションの型、アクションの名前です。execute_callback は、受理したゴールを実際に処理する関数、goal_callback は、届いたゴールを受けるかを決める関数、cancel_callback は、中断の要求を受けるかを決める関数です。goal_callback と cancel_callback は省くこともでき、省いた場合の既定は、ゴールは受理、中断の要求は拒否、です。中断を受け付けたいなら、cancel_callback で受理を返す必要があります。これは実機での確認はしていない、とあります。この手順書では、動きを見るために明示しています。

on_goal で REJECT を返すと、クライアントには拒否されたことが届き、execute は呼ばれません。仕様の、order が1 より小さいものは拒否、はここで実現しています。

on_cancel で ACCEPT を返すと、ゴールが CANCELING に入り、is_cancel_requested が True になります。REJECT を返せば、中断できないゴールとして扱えます。

execute について。Feedback と Result は、送るメッセージの入れ物を先に作っておいて、使い回しています。1 から order の手前までのループは、order 引く1 回まわり、初めの2項と合わせて order 足す1 項になり、仕様のとおりです。

publish_feedback は、呼んだ瞬間に feedback がクライアントへ飛びます。ループの先頭で1回目を出してから1秒待つので、最初の feedback はほぼすぐに、それ以降は約1秒の間隔で届きます。

succeed() と canceled() は、どちらもゴールの最後の状態を宣言する呼び出しで、戻り値として結果を返すのとは別です。宣言の後に、return で結果の本体をクライアントへ渡します。宣言を忘れると、execute が戻ったときに警告が出て、ゴールは ABORTED の扱いになります。これも実機での確認はしていない、とあります。canceled() は、中断の要求を受け付けた後、つまり CANCELING のときに呼ぶ、という順も守ります。

なぜ MultiThreadedExecutor と ReentrantCallbackGroup が要るのか。execute は time.sleep を含む長い処理で、その間ずっと executor のスレッドを占めます。単一のスレッドの executor だと、その間に届いた中断の要求、つまり on_cancel は順番待ちになり、execute が終わるまで処理されません。複数のスレッドの executor に変えたうえで、ReentrantCallbackGroup、つまり同じグループのコールバックを同時に動かしてよい、という設定にしておくと、execute の実行中に、別のスレッドで on_cancel が動けます。6-2節の課題3 は、この効果を外して確かめるものです。同じ理由で、6-2節の課題4 のように、2つのゴールを並行して処理できるのも、この2つのおかげです。

main では、rclpy.spin に executor を渡すのが要点です。

つまずきやすい点と観察のポイントは3つです。1つ目。中断の要求はループの先頭でしか確かめていないので、クライアントの cancel から反応までに、最大1秒ほど遅れます。ログの、中断が要求された、と、ゴールが中断された、の時刻の差に注目するとよい。2つ目。最後の回の sleep の間に中断の要求が届いた場合は、ループを抜けた後に確かめないので、そのまま succeed() に進みます。学習用のコードでは許していますが、厳密には、succeed() の前にも is_cancel_requested を確かめた方がよい、発展の課題です。3つ目。フィードバックに数列を入れる行は、同じリストを指しているだけで、コピーではありません。この例では送るたびにシリアライズされるので問題ありませんが、別のスレッドで書き換えるコードを書く場合は注意します。

### fibonacci_client.py

fibonacci_client.py は、80行ほどのコードです。先頭に、結果の状態を名前に直す辞書の STATUS_NAMES があり、クラスには6つのメソッドがあります。__init__、ゴールを送る send_goal、受理か拒否の返事を受ける on_goal_response、中断を要求する on_cancel_timer、途中経過を受ける on_feedback、最後の結果を受ける on_result です。要の行は3つです。send_goal で、send_goal_async にゴールと feedback_callback を渡し、返った Future の add_done_callback に on_goal_response を登録する行。on_goal_response で、get_result_async() の add_done_callback に on_result を登録する行。そして main で、done が True になるまで rclpy.spin_once を繰り返す行です。

原文の解説の要点です。役割は、ゴールを送り、feedback をログに出し、結果を受けて終わる、設定があれば途中で中断の要求も送る、ことです。クライアントは、サーバと違って、待ち受ける処理が、非同期の連鎖になります。send_goal で送り、on_goal_response で受理か拒否の返事を受け、on_feedback を何度も受け、on_result で最後の結果を受ける、と、それぞれ前の段の Future やコールバックが終わったときに、次が動きます。

STATUS_NAMES について。結果の status は GoalStatus の整数の値で、そのままでは読みにくいので、名前に直す辞書を用意しています。1節の状態遷移図の、終わりの3つに対応します。

パラメータの order と cancel_after は、起動のときに -p で渡せるようにしています。フェーズ3-3 の復習です。

self.done は、終わりの判定のためのフラグで、main のループがこれを見て抜けます。ゴールの拒否、サーバの不在、結果の受信、のどの場合も True にしないと、終わらなくなります。

send_goal について。wait_for_server は、サーバが見つかるまで最大5秒待ちます。send_goal_async は、ゴールを送るとすぐ戻り、Future を返します。add_done_callback で、返事が来たらこの関数を呼ぶ、と登録しています。この時点では、返事はまだ来ていません。

on_goal_response について。Future の result() が goal_handle、つまりゴールを見分けて操作するための取っ手です。accepted が False なら、拒否されたということです。受理なら、get_result_async() で、最後の結果を取る Future を得て、これにも完了のコールバックの on_result をつなぎます。ここで結果を待ち始めますが、実際の結果は、ゴールが終わった後に届きます。

cancel_after の扱い。create_timer は周期のタイマーなので、コールバックの中で自分を cancel して、1回で止めています。中断は cancel_goal_async() で要求します。これも Future を返しますが、この例では結果を待ちません。中断の要求が受け入れられると、サーバが canceled() を宣言し、on_result に CANCELED の結果が届きます。

on_feedback の引数は、フィードバックのメッセージそのものではなく、それを包んだもので、中身は feedback の属性で取り出します。on_result では、応答の status が最後の状態、result が結果のメッセージです。

main とスピンについて。Future の完了のコールバックやタイマーは、スピンして初めて動きます。スピンしないと、何も起きません。spin ではなく spin_once のループにしたのは、done のフラグで、自分の好きなときに抜けるためです。

サーバの側との違い。クライアントは単一のスレッドでかまいません。コールバックはどれも一瞬で終わり、待つ処理を持たないからです。

観察のポイントとつまずきは3つです。1つ目。order を10、cancel_after を3.0 にすると、feedback が3回か4回出た後に、クライアントの、中断の要求を送る、のログ、サーバの、中断が要求された、のログ、そしてクライアントの、CANCELED の結果のログ、の順に並びます。結果の数列は、中断した時点までのものです。2つ目。中断の後も、on_result は必ず呼ばれます。中断とは、結果が来なくなることではなく、結果の status が CANCELED になることです。3つ目。サーバを起動していないと、5秒待って、使えない、というエラーで終わります。先にサーバを起動しているか確かめます。

### 登録とビルド

setup.py の entry_points に、fibonacci_server と fibonacci_client の2行を足し、ビルドし直します。cd で ~/ros2_ws に移り、colcon build --symlink-install に --packages-select learn_py を付けてビルドし、source install/setup.bash を実行します。期待する結果は、learn_py の Finished と、1つのパッケージが終わったという Summary が出ることです。

## 5. C++ の版、learn_cpp

learn_cpp の src に、fibonacci_server.cpp と fibonacci_client.cpp を作ります。

主な API は、rclcpp_action のもので、rclcpp_action/rclcpp_action.hpp を include して使います。やりたいことと API の2列の表で、8行あります。

サーバを作るには、rclcpp_action の create_server に、山括弧で型を付け、this、アクションの名前、ゴールの処理、中断の処理、受理した後の処理、を渡す。

ゴールを受理するかの判断では、GoalResponse の ACCEPT_AND_EXECUTE か REJECT を返す。

中断を受理するかの判断では、CancelResponse の ACCEPT か REJECT を返す。

受理した後の実行は、受理した後の処理の中で、std::thread で別のスレッドを起こして実行する。executor を塞がないためです。

実行の途中の操作は、goal_handle の矢印の publish_feedback、is_canceling()、そして succeed か canceled に結果を渡す。

クライアントを作るには、rclcpp_action の create_client に、山括弧で型を付け、this とアクションの名前を渡す。

ゴールを送るには、client の矢印の async_send_goal に、ゴールと options を渡す。options には、goal_response_callback、feedback_callback、result_callback を設定します。

中断を要求するには、client の矢印の async_cancel_goal に、goal_handle を渡す。

Python との違いの見どころは、Python は Future の完了のコールバックをつなぐのに対して、C++ は送るときに、options に3つのコールバックをまとめて渡すことです。

### fibonacci_server.cpp

fibonacci_server.cpp は、80行ほどのコードです。コンストラクタで create_server に3つのラムダ式を渡し、実行の本体は private の execute にあります。要の行は2つです。3つ目のラムダ、つまり受理した後の処理で、std::thread で execute を呼ぶスレッドを作り、detach する行。そして execute のループの中で、is_canceling() を確かめ、publish_feedback で途中経過を送る行です。

原文の解説です。Python の版と同じ仕事をします。原文は、Python の版と C++ の版の2列の表で、対応を7行にしています。

on_goal は、create_server の3つ目の引数のラムダ、つまりゴールの処理。

on_cancel は、4つ目の引数のラムダ、つまり中断の処理。

executor が呼ぶ execute は、5つ目の引数のラムダ、つまり受理した後の処理が起こす、別のスレッドで呼ぶ execute。

succeed() か canceled() をして結果を return するのは、succeed か canceled に結果を渡すことで、戻り値は void。

is_cancel_requested は、is_canceling()。

time.sleep の1.0秒は、rclcpp::Rate の1 と、rate の sleep()。

MultiThreadedExecutor は、要らない。実行を別のスレッドにするからです。

さらに、8つの点が説明されています。

型の別名。Fibonacci はアクションの型、GoalHandle は、サーバの側でゴールを操作する取っ手です。ヘッダは、fibonacci.hpp のように、型の名前を小文字にしたファイルの名前になります。

create_server の引数。1つ目と2つ目はノードとアクションの名前で、残りの3つはコールバックです。順に、ゴールを受けるか、中断を受けるか、受理したゴールをどう実行するか。Python と違い、C++ では3つとも必須で、実行の処理も自分で起動します。

ゴールの処理の引数は、ゴールの UUID と、ゴールの本体です。UUID は使わないので、名前を付けずに受けています。戻り値の ACCEPT_AND_EXECUTE は、受理して、すぐ実行に進む、という意味で、REJECT は拒否です。実行を後回しにする ACCEPT_AND_DEFER という選択もありますが、ここでは使いません。

中断の処理で CancelResponse の ACCEPT を返すと、ゴールが CANCELING に移り、is_canceling() が真になります。

受理した後の処理と std::thread。ここが最も大事な所です。受理した後に呼ばれるこのコールバックは、executor のスレッドで動きます。もしここで直接 execute を呼ぶと、1秒ごとの待ちを含む処理が終わるまで executor が塞がり、中断の要求も処理されません。そこで、新しいスレッドを作って execute を任せ、すぐに戻ります。goal_handle は shared_ptr なので、値で取り込んでおけば、スレッドが生きている間は片付けられません。detach() は、スレッドを切り離して、ひとりで走らせる指定です。

execute について、Python との違いが4つ挙げられています。1つ目。feedback と result は make_shared で作ります。auto の参照の sequence は、フィードバックの中の配列への参照で、0 と1 で初期化し、push_back で伸ばします。publish_feedback を呼ぶたびに、その時点の中身が送られます。2つ目。ループの条件の rclcpp::ok() は、Ctrl+C などでシャットダウンされたら、ループを抜けるための保険です。3つ目。canceled と succeed は、状態の宣言と結果の受け渡しを、1回で行います。中断の側では、呼んだ後に return で関数を終えます。4つ目。rate の sleep() は、前の sleep からの経過を考えて、周期を保つ待ち方です。time.sleep と違い、処理の時間が長引いても、間隔がずれにくい。

main は、普通の、単一のスレッドの rclcpp::spin でかまいません。長い処理は別のスレッドにあるので、executor はいつも空いていて、中断の要求をすぐに処理できます。

メンバの server_ は、サーバを持つ SharedPtr で、持たないと、コンストラクタを出た時点で片付けられ、サーバが消えます。

つまずきやすい点は3つです。1つ目。detach したスレッドは、ノードが片付けられるのを待ちません。処理の途中で Ctrl+C を押すと、スレッドが残ったまま終わりの処理に入り、エラーが出ることがあります。本格的なコードでは、スレッドを持っておいて、終わるときに join するか、専用の executor やコールバックグループで処理します。2つ目。Python の版と同じく、中断の確認は各回の先頭だけで、最後の回の途中に届いた中断の要求は見落とされ、succeed に進むことがあります。3つ目。ラムダの this は、ノード自身へのポインタを持ち込む指定で、get_logger() などのメンバ関数をラムダの中で使うために必要です。

観察のポイント。Python の版のサーバと比べて、feedback の間隔や、cancel のときの反応がほぼ同じになることを確かめます。同じ結果が出るなら、片方の言語で書いたクライアントから、もう片方のサーバを使えます。

### fibonacci_client.cpp

fibonacci_client.cpp は、100行あまりのコードです。ブロックは、数列を文字列にする補助の関数の to_text、クラスのコンストラクタと send_goal、そして main です。send_goal が中心で、SendGoalOptions の options に、goal_response_callback、feedback_callback、result_callback の3つのラムダを設定してから、async_send_goal にゴールと options を渡して送ります。要の行は、その async_send_goal の行と、result_callback の最後で rclcpp::shutdown を呼ぶ行です。

原文の解説です。Python の版のクライアントと同じ役割です。構造の違いは、Python が Future に完了のコールバックを1つずつつなぐのに対し、C++ は、送るときに SendGoalOptions へ、3つのコールバックをまとめて設定する点です。原文は、Python の版と、C++ の版の options のメンバ、の2列の表で、対応を4行にしています。

Future の add_done_callback に on_goal_response を登録するのは、goal_response_callback。

feedback_callback に on_feedback を渡すのは、feedback_callback。

get_result_async() の add_done_callback に on_result を登録するのは、result_callback。

done を True にして main のループを抜けるのは、rclcpp::shutdown() で spin を終わらせること。

さらに、8つの点が説明されています。

to_text は、数列を角括弧の形の文字列にする補助の関数です。RCLCPP_INFO の %s の書式には、配列をそのまま渡せないからです。c_str() で const char のポインタに直して渡しています。

コンストラクタについて。declare_parameter で、宣言と同時に値を受け取ります。このフェーズの Python の版は、コンストラクタで宣言だけしておき、ゴールを送るときなどに get_parameter の value で読んでいます。C++ の版は、宣言と同時に受け取った値を、メンバに保存する形にしました。なお、Python の declare_parameter も値の入った Parameter を返すので、宣言と同時に値を受け取ることもできます。ROS の整数のパラメータは64ビットなので int64_t で、ゴールに入れるときに int32_t へ static_cast しています。

send_goal について。wait_for_action_server は、サーバが見つかるまで最大5秒止まります。見つからなければ shutdown して終えます。ここは spin の前に呼んでいるので、待っている間はほかのコールバックが動きませんが、まだ何も登録していないので問題ありません。

goal_response_callback の引数は、GoalHandle の SharedPtr です。拒否されたときは空、つまり null で渡るので、空かどうかで判定します。受理なら goal_handle_ に保存して、後の中断で使います。cancel_after_ が0.0 より大きければタイマーを作り、そのコールバックで1回だけ async_cancel_goal を呼びます。create_wall_timer は周期のタイマーなので、Python の版と同じく、cancel() で自分を止めます。

feedback_callback は、1つ目の引数のゴールの取っ手を使わないので、名前を付けずに受け、2つ目の引数のフィードバックから sequence を取ります。

result_callback の WrappedResult は、最後の状態の code と、結果の本体の result の組です。switch で code を名前にして表示し、最後に rclcpp::shutdown() を呼ぶことで、main の spin が戻り、プロセスが終わります。これを忘れると、終わらない、という症状になります。

async_send_goal は、送って戻ります。戻り値の future は使っていませんが、結果は options のコールバックで受けられるので、問題ありません。main では、send_goal の後で spin し、spin して初めて、返事、feedback、結果、タイマーのコールバックが動きます。

つまずきやすい点は3つです。1つ目。コールバックの引数の型は、ROS の版で変わっています。Jazzy の型は、本文のとおりです。ネットの上の古い記事にある、std::shared_future を受ける形は、そのまま書くとエラーになります。2つ目。各コールバックはラムダで、this を取り込んでいます。ノードが片付けられた後に動くと危ないのですが、この例では、ノードが spin の間ずっと生きているので問題ありません。3つ目。クライアントも、単一のスレッドの executor でかまいません。待つ処理、つまり sleep が無いからです。

観察のポイント。cancel_after を3.0 にして、Python の版のクライアントと同じ、feedback、中断の要求を送る、CANCELED の結果、というログの並びになることを確かめます。

### CMakeLists.txt とビルド

CMakeLists.txt に追記し、install(TARGETS ...) に名前を足します。これまでの分は残しますが、前のフェーズで C++ の版を作らなかったノードの名前は書きません。足すのは、fibonacci_server と fibonacci_client のそれぞれの add_executable と、rclcpp、rclcpp_action、example_interfaces の ament_target_dependencies です。そして install(TARGETS ...) を、hello から fibonacci_client までの14の名前に並べ直します。

cd で ~/ros2_ws に移り、colcon build --symlink-install に --packages-select learn_cpp を付けてビルドし、source install/setup.bash を実行します。期待する結果は、learn_cpp の Finished と、1つのパッケージが終わったという Summary が出ることです。

## 6. 実験

### 6-1. コマンドラインから使う

T1 で ros2 run learn_py fibonacci_server を実行します。T2 で、3つのコマンドを実行します。ros2 action list -t、ros2 action info /fibonacci、そして ros2 action send_goal で、/fibonacci に、example_interfaces/action/Fibonacci の型で、引用符と波括弧で囲んだ、order が5 のゴールを送り、--feedback を付けます。

期待する結果を説明します。

action list -t では、/fibonacci と、その Fibonacci 型の1行が表示されます。

action info では、アクションの名前が /fibonacci で、アクションのクライアントが0、アクションのサーバが1 で /fibonacci_server、と表示されます。

send_goal では、まず、アクションのサーバが使えるようになるのを待っている、という行が出て、order が5 のゴールを送ったこと、ゴールが受理されて ID が付いたことが表示されます。ID は毎回変わります。続いて、Feedback の見出しの下に、sequence が、0、1、1 と、1つの要素を1行ずつの形で表示されます。1秒後に、0、1、1、2 の Feedback が出て、さらに2回、1項ずつ増えた Feedback が1秒おきに出ます。最後に、Result の見出しの下に、0、1、1、2、3、5 の sequence が表示され、ゴールが SUCCEEDED の状態で終わった、と表示されます。

T1 のサーバの側には、order が5 のゴールを受理した、というログと、約4秒後に、ゴールが成功した、というログに、0、1、1、2、3、5 の数列が添えられて出ます。これは Python の版の場合で、C++ の版の最後の行は、ゴールが成功した、だけで、数列は付きません。

読み方は2つです。1つ目。配列は、YAML の箇条書き、つまり、ハイフンと値の形で、1つの要素を1行で表示されます。2つ目。order が5 では、feedback が4回、つまり3項から6項まで届き、約4秒で結果になります。結果は、2節の例のとおり6項です。

フィードバックが1秒ごとに流れ、最後に結果が出ます。処理の途中で Ctrl+C を押すと、中断の要求が送られ、サーバの側のログに、中断が要求された、と出ます。

### 6-2. 自作のクライアントから使う

T1 で ros2 run learn_py fibonacci_server を実行し、T2 で ros2 run learn_py fibonacci_client を、-p で order を6 にして実行します。中断も試すために、order を10、cancel_after を3.0 にしても実行します。

order が6 で、最後まで実行した場合の、T2 のクライアントの期待する結果は、こうです。まず、ゴールが受理された、というログが出ます。続いて、feedback のログが5回、約1秒おきに出ます。数列は、0、1、1 から始まり、1項ずつ増えて、最後は 0、1、1、2、3、5、8 になります。そして、SUCCEEDED の結果のログに、同じ 0、1、1、2、3、5、8 の数列が添えられて出ます。結果を受け取ると、クライアントは自分で終わり、プロンプトに戻ります。サーバは、次のゴールを待って動き続けます。

order が10、cancel_after が3.0 で、中断した場合の期待する結果は、こうです。T2 のクライアントには、ゴールが受理された、のログに続いて、feedback のログが3回、つまり、0、1、1、と、0、1、1、2、と、0、1、1、2、3、が出ます。そして、中断の要求を送る、のログが出て、CANCELED の結果のログに、0、1、1、2、3 の数列が添えられて出ます。T1 のサーバには、order が10 のゴールを受理した、中断が要求された、ゴールが中断された、の3つのログが出ます。

中断の要求と、サーバのループが、同じくらいの時刻、つまり約3秒後に重なるので、中断の前の feedback が3回か4回か、結果の数列がどこまで伸びているかは、実行ごとに変わりえます。見るべき点は、結果の status が CANCELED で、数列が、order が10 の完成した形の11項より短いことです。

この節の末尾の課題1、つまり order を0 にした場合は、クライアントは、ERROR の印で、ゴールが拒否された、というログを出して、すぐに終わります。サーバには、WARN の印で、order が0 のゴールを拒否する、というログが出ます。拒否されたゴールには、feedback も結果も届きません。

言語の組み合わせを試すこともできます。C++ の版を作った場合の任意の実験で、原文は、組み合わせ、T1、T2 の3列の表で、4行を挙げています。Python のサーバと Python のクライアント、Python のサーバと C++ のクライアント、C++ のサーバと Python のクライアント、C++ のサーバと C++ のクライアントです。

課題は5つです。

課題1 は、order を0 にしてゴールを送り、拒否されることを、クライアントとサーバの両方のログで確かめることです。

課題2 は、cancel_after を3.0 にして、フィードバックが3回ほど流れた後に中断され、結果の status が CANCELED になることを確かめることです。

課題3 は、Python の版のサーバで、MultiThreadedExecutor を外して、つまり rclpy.spin にノードだけを渡す形にして、ReentrantCallbackGroup も外し、中断の要求がどうなるかを確かめることです。処理が終わるまで中断が届かない、またはゴールが最後まで走ることを観察します。確かめた後は、元に戻します。

課題4 は、サーバが動いている間に、クライアントを2つ同時に起動して、2つのゴールが並行して処理されることを確かめることです。Python の版では、ReentrantCallbackGroup が効いています。

課題5 は発展で、rqt_graph で、アクションが内部では、サービス3つとトピック2つでできていることを、ros2 topic list -t と ros2 service list -t で見つけることです。サービスは、_action の send_goal、cancel_goal、get_result、トピックは、_action の feedback と status です。

## 7. Python の版と C++ の版の違いのまとめ

原文は、観点、Python、C++ の3列の表で、4行にまとめています。

1行目、サーバの構成。Python は、ActionServer に、execute_callback、goal_callback、cancel_callback の3つを、キーワードの引数で渡す。C++ は、create_server に、3つの処理を、位置の引数のラムダとして順に渡す。

2行目、実行の処理の動かし方。Python は、MultiThreadedExecutor と ReentrantCallbackGroup で、executor のスレッドを複数にして、中断の要求と実行の処理を並行させる。C++ は、受理した後に呼ばれる3つ目のラムダの中で、std::thread を作って detach し、実行の execute を、明示的に別のスレッドへ逃がす。学習用の簡易な策で、終わるときにスレッドが残りうる点は、8節の注意にあります。

3行目、クライアントの結果の受け方。Python は、send_goal_async の Future に add_done_callback で受理か拒否の応答を受け、get_result_async() にも add_done_callback で最後の結果を受ける、Future の連鎖。C++ は、SendGoalOptions の変数 options に、goal_response_callback、feedback_callback、result_callback を設定し、async_send_goal にゴールと options を渡して送る。

4行目、コードの行数。サーバとクライアントを合わせて、概要のコメントの行を除くと、Python は136行で、サーバが63行、クライアントが73行。C++ は175行で、サーバが74行、クライアントが101行。

実行のモデルの違い、つまり Python は executor とコールバックグループ、C++ は明示的なスレッドの生成、というのが、アクションで初めて表に出る、Python と C++ の一番大きな差です。どちらも、長い処理の間もサーバがほかの要求に応えられるようにする、という同じ目的のための工夫ですが、手段が違います。

## 8. つまずきやすい点

原文では、症状と、確かめることの2列の表で、7行あります。

1行目。Python で、中断の要求が効かない場合は、MultiThreadedExecutor と ReentrantCallbackGroup を使っているか。time.sleep の間は、ほかのコールバックが動けません。

2行目。Python で、クライアントが終わらない場合は、on_result で done を True にしているか。ゴールが拒否された場合も、done にしているか。

3行目。C++ で、rclcpp_action が見つからない、というビルドのエラーになる場合は、package.xml の rclcpp_action の depend、rclcpp_action の find_package、そして ament_target_dependencies。

4行目。C++ の goal_response_callback で、型のエラーになる場合。Jazzy では、引数は GoalHandle の SharedPtr で、ゴールが拒否されると空になります。古い資料の std::shared_future の形は使いません。

5行目。Ctrl+C で終わるときに、C++ のサーバでエラーや異常な終わりが出る場合。実行の処理を、detach した別のスレッドで動かしているので、処理の途中のスレッドが残りえます。学習用としては許します。本格的に作る場合は、スレッドを管理して、終わるときに待ちます。

6行目。実行が終わっても、プロセスが残る場合は、C++ のクライアントが、結果のコールバックで rclcpp::shutdown() を呼んでいるか。

7行目。ros2 action send_goal で、型が見つからない場合は、型の名前の綴り。example_interfaces/action/Fibonacci のように、action が入ります。

## 9. 次へ

フェーズ4 で、これまでのノードを launch ファイルで束ねます。

フェーズ3 の総括、つまり学習の計画の1-7 の振り返りは、フェーズ3-1 から3-5 と、フェーズ2 の、それぞれの Python の版と C++ の版の違いのまとめの節を読み返して、コードの量、型の扱い、ビルドの手順、つまずきの傾向を、自分の言葉で整理する形に変えた、とあります。各手順書にすでに答えが書いてあるので、新しく空欄の比べる表を埋める作業は要りません。

## 10. 公式ドキュメントと参考資料

確認の状況が書かれています。2026年9月20日の時点で、下の資料は企画の文書に載せた URL で、今回は確かめ直していません。docs.ros.org は、ボット対策で本文の取得が拒否されます。

公式の資料は、ROS 2 Jazzy の3つです。Python でアクションのサーバとクライアントを書くチュートリアル、C++ で書くチュートリアル、そして中級のチュートリアルの目次です。

公式のチュートリアルは、独自の .action の定義、つまり action_tutorials_interfaces を使いますが、この手順書は、標準の example_interfaces を使います。公式のドキュメントと食い違う場合は、公式を優先する、とあります。

原文の最後には、出典の注記があります。各サンプルの API の使い方は、公式のチュートリアルを参考にしました。ROS 2 のドキュメントは CC BY 4.0 です。ノードの名前、仕様、コード、文章は独自に書いたもので、一語ずつの転載ではありません。期待する結果に載せた ros2 interface show の表示は、example_interfaces の型の定義で、Apache License 2.0 です。

以上で、フェーズ3-5 の手順書の話を終わります。

## 出典について

この原稿は、SanghunIm1991 さんの [ros2MinimalPhysicalAi の「フェーズ3-5 手順書: アクション（途中経過つき・中断できる長い処理）」](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/docs/phase3_5_actions.md)を、聞くために要約・意訳したものです。図の [phase3_5_action_seq.svg](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/docs/img/phase3_5_action_seq.svg) と [phase3_5_goal_states.svg](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/docs/img/phase3_5_goal_states.svg) は、言葉で説明しました。元にしたのは、[2026年10月14日の版](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/86dc0ed3d606c4a05d1e087421bb10318a37e521/docs/phase3_5_actions.md)です。原文の文章と図と同じく、[クリエイティブ・コモンズ 表示 4.0 国際ライセンス](https://creativecommons.org/licenses/by/4.0/deed.ja)で提供します。

原稿の中に原文の表記のまま書いたコマンドと、コードの関数やクラスの名前は、原文では [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0) の対象です。ライセンスの全文は、原文のリポジトリの [LICENSE-APACHE-2.0](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/LICENSE-APACHE-2.0) にあります。サンプルコードは写さず、役割と要の行を言葉で説明しました。

原文のうち、ros2 interface show の表示として載せた型の定義は、[example_interfaces](https://github.com/ros2/example_interfaces)（Apache License 2.0）のものです。この原稿では、それを写さず、項目の名前と型を言葉で説明しました。原文では、API の使い方を [ROS 2 Documentation](https://docs.ros.org/en/jazzy/)（Open Robotics、[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)）の公式チュートリアルを参考にしたとしています。表示の例は、各ツールの表示を言葉で説明したものです。
