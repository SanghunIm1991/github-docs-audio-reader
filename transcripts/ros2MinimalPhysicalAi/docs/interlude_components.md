<!--
聞くための原稿（読み上げでは読まれない記録）
原文: SanghunIm1991/ros2MinimalPhysicalAi の main ブランチの docs/interlude_components.md（図は docs/img/interlude_components_layout.svg）
原文のコミット: 132df7b64d48d560def7ec7149f7003938d3d8e5（2026-10-14）
作成: 2026-10-21、Claude Code が手作業で作成（原稿化スキルはまだない）
原文のライセンス: 文章と図は CC BY 4.0、コードとコマンドは Apache-2.0（それぞれ LICENSE の2と1）。原文に、サンプルは公式チュートリアルの転載ではなく、API の呼び方は公式の例と同等で、公式ドキュメント（ROS 2 Documentation）は CC BY 4.0、とある。この原稿は、原文を聞くために要約・意訳したもの（改変あり）
方針: 英語の略語や製品名、関数やクラスの名前、短いコマンドは原文の表記のまま書く。サンプルコード（C++ のコンポーネント2本、launch ファイル1本）と、CMakeLists.txt・package.xml に足す行は、写さずに、ブロックの役割と要の行を言葉で説明した。期待する結果（ros2 pkg create、colcon build、ros2 component、ros2 pkg executables、--print、ログ、ros2 node list の表示）も、何が表示されるかを言葉で説明した。図と表（仕様、主な API、フェーズ3-1との違い、launch の各部分、違いのまとめ、マイクロサービスとの対応、つまずきやすい点）は言葉で説明する。文字数の上限は設けない
省いたもの: URL、型の定義へのリンク、ログの時刻とプロセス番号とアドレスの数字、ライブラリの置き場所のパス、ビルドにかかった秒数、ros2 pkg create のメンテナの名前とメールアドレス
-->

# 間章: コンポーネント指向で、ノードを組み立て直す（聞くための原稿）

これは、ros2MinimalPhysicalAi という教材の、フェーズ4 とフェーズ5 の間に置いた間章の手順書の話です。フェーズ3-1 で作った C++ の版の talker と listener を題材に、ROS2 のコンポーネント、Composition の仕組みで、同じ振る舞いのノードを部品として作り直します。フェーズ3 から4 では、1つのファイルに、ノードのクラスが1つと、main の関数が1つ、という形で書いてきました。この章では、その形から main を取り除き、ノードを、どのプロセスで動かすかを後から決められる部品にします。

想定する環境は、WSL2 と Ubuntu 24.04 と ROS2 Jazzy です。前提は、フェーズ3-1 の C++ の版、つまり learn_cpp の talker と listener と、フェーズ4 の learn_bringup と launch を終えていることです。所要時間の目安は1から2コマで、言語は C++ だけです。

C++ だけである理由は、この章の位置づけの囲みにあります。ROS2 のコンポーネントの仕組み、rclcpp_components は C++ 専用で、Python の rclpy には同じような仕組みがありません。Jazzy の環境で、rclpy_components のようなパッケージが存在しないことを確かめた、とあります。そのため、この章は C++ だけで進めます。フェーズ5 の車両のシミュレーションは Python で書くので、フェーズ5 はこの章の成果物に依存しません。この章のねらいは、ノードを部品として作り、配置、つまりどのプロセスに入れるかを後から決める、という考え方に触れておくことです。ナビゲーションの Nav2 など、規模の大きな ROS2 の OSS は、この形で作られています。

進め方の囲みです。2節の仕様は、何を作るかの定義で、API の使い方までは書いていません。4節と5節の冒頭の、主な API の表で必要な API をつかみ、サンプルと解説を読んで、フェーズ3-1 のコードとどこが違うかを確かめながら理解します。サンプルは学習の手がかりとして最小限に書いたもので、公式のチュートリアルの転載ではありません。使っている API の呼び方は、公式の例と同じです。コードは、手順書を作るときに使い捨ての環境で、ビルドと、ros2 component types での登録、launch ファイルの読み込み、つまり --print まで確かめてあります。ノードを実際に起動した結果は確かめていないので、出力が違うときは、実機の表示を優先します。

期待する結果の出どころの囲みもあります。パッケージの作成、ビルド、ros2 component types、--print の表示は、手順書を作るときに実際に確かめたものです。ノードを起動した後の表示は、コードと ROS2 の仕様から筆者が想定したものです。ログの文言は、手元の rclcpp_components と ros2component から確かめてあります。時刻、pid、パスなどの細部は、実行ごとに変わります。

この原稿では、サンプルコードを書き写さず、ブロックの役割と要の行を言葉で説明します。

## 0. 学習目標と完了の条件

完了の条件は4つです。

1つ目。コンポーネントが、ふつうのノードとどこが違うかを説明できる。違いは、main が無いこと、NodeOptions を受け取るコンストラクタ、登録用のマクロ、そして共有ライブラリとしてビルドすることです。

2つ目。フェーズ3-1 の talker と listener をコンポーネントとして書き直してビルドし、ros2 component types で登録を確かめられる。

3つ目。同じコンポーネントを、3通りの方法で動かせる。コンテナへ手で読み込む方法、単独の実行ファイル、そして launch です。

4つ目。ノードの中身と、どのプロセスに配置するかを分けて考えることの利点と、マイクロサービスの考え方との対応を、自分の言葉で説明できる。

## 1. 概要、なぜ部品にするのか

フェーズ3 から4 では、ノードを1つ書くたびに、main の関数も書いてきました。main は rclcpp の init を呼び、ノードを1つ作り、spin で回し続けます。つまり、ノードの中身と、それを動かすプロセスが、1つのファイルの中で固く結び付いていました。talker を動かせば talker 専用のプロセスが1つでき、listener を動かせば、もう1つできます。2つのノードの間の通信は、同じ PC の中であっても、プロセスの境界を越えて DDS を通ります。

この形は分かりやすく、1つのノードが落ちても他を巻き込まない、という長所もあります。一方で、ノードの数が数十に増えると、プロセスの数だけメモリを使い、プロセスの間の通信のたびに、メッセージのコピーが生じます。カメラの画像のような大きなデータを、同じ PC の中のいくつものノードで順に加工する場面では、この負担が無視できなくなります。

コンポーネントは、この結び付きをほどく仕組みです。ノードのクラスから main を取り除いて、共有ライブラリ、つまりドット so のファイルに入れておき、どのプロセスに、どのノードを、いくつ入れるかは、起動するとき、つまり launch やコマンドで決めます。同じ talker を、あるときは単独のプロセスで、あるときは listener と同じプロセス、つまりコンテナに入れて動かせます。同じプロセスに入れたノード同士は、指定すれば、DDS を通らずに、メモリの上で直接メッセージを受け渡せます。これをプロセス内通信と呼びます。指定の方法は7-3節で扱います。7-1節のように指定せずに読み込んだ場合は、同じプロセスの中でも DDS を通ります。

ここに図が1枚あります。上と下の2段に分かれていて、どちらの段も、灰色の破線の枠で囲まれています。

上の段の枠の見出しは、フェーズ3-1、ノードごとに別の実行ファイル、別のプロセス、です。中に薄い青の箱が2つ、左右に並んでいます。左の箱は、プロセス1、talker、main 付き。右の箱は、プロセス2、listener、main 付き。左から右へ、/chatter というラベルの実線の矢印があります。

下の段の枠の見出しは、間章、コンポーネントを1つのコンテナ、つまりプロセスに読み込む、です。左に薄い黄色の箱があり、libpubsub_components.so、その下に、Talker と Listener、main なし、と書いてあります。右には、薄い緑の大きな箱があり、見出しは、プロセス、component_container、コンテナ、です。黄色の箱から緑の箱へ、読み込む、というラベルの破線の矢印があります。緑の箱の中には、薄い青の箱が2つ、talker と listener が並び、talker から listener へ、実線の矢印があります。矢印のラベルは、/chatter と、その下に、プロセス内通信を選べる、です。

この、中身と配置を分ける考え方は、Web のシステムで主流になった、マイクロサービスの考え方と重なる部分が多い、とあります。対応は9節で整理します。

## 2. 仕様

2列の表で、5行あります。

パッケージは learn_components で、ament_cmake で新しく作ります。フェーズ3-1 の learn_cpp は変えず、そのまま残します。

コンポーネントは、learn_components の名前空間の Talker と Listener です。振る舞いは、フェーズ3-1 の talker と listener と同じです。トピックは chatter、型は std_msgs の msg の String で、1秒ごとに hello N を送り、受け取ったら received と出します。

ライブラリは、2つのコンポーネントを、共有ライブラリの libpubsub_components.so にまとめます。

単独の実行ファイルは、talker_node と listener_node です。ビルドのときに自動で作らせ、main は自分では書きません。

launch は、learn_bringup に components.launch.py を足します。コンテナを1つ起動し、2つのコンポーネントを読み込みます。

## 3. パッケージを作る

ros2_ws の src に移り、ros2 pkg create で、ビルドの種類を ament_cmake、依存を rclcpp、rclcpp_components、std_msgs、ライセンスを Apache-2.0 にして、learn_components を作ります。メンテナの名前とメールアドレスも、オプションで指定します。

rclcpp_components は、コンポーネントを登録するためのマクロと、CMake の関数を持つパッケージです。

大事な注意があります。--dependencies は、パッケージ名の直前に置きません。このオプションは値をいくつでも取るので、--dependencies の後ろに3つの依存とパッケージ名を続けて書くと、パッケージ名まで依存の一部として読まれ、パッケージ名が無い、というエラーになります。手順書を作るときに実際に起きた、とあります。原文のコマンドのように、--dependencies の後ろに別のオプションを続ければよい、とあります。

期待する結果です。新しいパッケージを作る、という表示に続いて、パッケージ名が learn_components、ビルドの種類が ament_cmake、依存が rclcpp、rclcpp_components、std_msgs と表示され、learn_components のフォルダ、package.xml、src と include のフォルダ、CMakeLists.txt を作ったことが並びます。--node-name を付けていないので、src は空のフォルダのまま作られます。package.xml には、rclcpp、rclcpp_components、std_msgs の3つの depend が、CMakeLists.txt には、3つの find_package が、あらかじめ書き込まれます。

## 4. コンポーネントを書く

主な API の表は、2列で、3行あります。

読み込む側から設定を受け取るには、コンストラクタの引数で、rclcpp の NodeOptions への const の参照、options を受け取り、それを Node の名前と一緒に、Node へ渡します。

コンポーネントとして登録するには、RCLCPP_COMPONENTS_REGISTER_NODE のマクロに、名前空間付きのクラス名を渡します。ヘッダは、rclcpp_components の register_node_macro.hpp です。

クラス名の衝突を避けるには、namespace learn_components で、クラスを囲みます。

フェーズ3-1 との違いは、次の4点だけです。ノードの中身、つまり Publisher、タイマー、購読、ログは、1行も変えません。

違いの表は、3列で、4行あります。列は、観点、フェーズ3-1 の learn_cpp の talker.cpp、そしてこの章の learn_components の talker_component.cpp です。

コンストラクタは、フェーズ3-1 では、引数なしで、Node に talker という名前だけを渡していました。この章では、explicit を付け、NodeOptions の参照を受け取り、Node に talker という名前と options を渡します。

main の関数は、フェーズ3-1 ではあり、init、spin、shutdown の順に呼びました。この章では無く、読み込む側が用意します。

登録は、フェーズ3-1 では無く、この章では、ファイルの末尾に、RCLCPP_COMPONENTS_REGISTER_NODE の learn_components の Talker を書きます。

名前空間は、フェーズ3-1 では無く、この章では、namespace learn_components で囲みます。

最初のサンプルは、learn_components の src の talker_component.cpp です。

talker_component.cpp は、45行ほどのコードで、ブロックは4つです。1つ目は include で、chrono、memory、string と、rclcpp、rclcpp_components の登録マクロのヘッダ、std_msgs の String を読み込み、using で、1s のような時間の書き方を使えるようにします。2つ目は、namespace learn_components の中の Talker のクラスで、rclcpp の Node を継承します。要の行は、そのコンストラクタで、explicit Talker が NodeOptions の参照の options を受け取り、初期化のところで Node に talker と options を渡します。本体では、フェーズ3-1 と同じく、chatter への Publisher を、キューの深さ10 で作り、1秒ごとのタイマーで on_timer を呼ぶようにします。3つ目は private の部分で、on_timer が、hello と通し番号をつないだ文字列を publish してログに出し、Publisher、タイマー、番号の count_ の3つのメンバを持ちます。4つ目は、名前空間を閉じた後、ファイルの最後の、RCLCPP_COMPONENTS_REGISTER_NODE の learn_components の Talker の1行です。

原文の解説の要点は5つです。

1つ目は、NodeOptions を受け取るコンストラクタです。コンテナは、ノードを作るときに、ノード名の上書き、remap、パラメータ、プロセス内通信を使うかどうか、などの設定を、NodeOptions にまとめて渡してきます。これを Node へそのまま渡すことで、launch やコマンドで指定した設定がノードに届きます。引数なしのコンストラクタのままだと、コンテナはこのクラスを作れません。登録のマクロが、この形のコンストラクタを前提にしているからです。

2つ目は explicit です。引数が1つのコンストラクタで、意図しない暗黙の型の変換を防ぐための、C++ の習慣です。付けなくても動きますが、付けておくのが一般的です。

3つ目は、main が無いことです。ここが、この章の核心です。rclcpp の init も spin も書きません。初期化とスピンは、このクラスを読み込む側、つまりコンテナや、自動で作られる単独の実行ファイルが行います。そのため、コンストラクタの中で、長い処理や、sleep のような待ちを書いてはいけません。コンストラクタが終わらないと、同じコンテナに入る、他のノードの読み込みも止まります。周期的な処理は、フェーズ3-1 と同じく、タイマーで行います。

4つ目は、namespace learn_components です。コンテナは、クラスを、learn_components の Talker という完全な名前で探します。たくさんのパッケージのクラスが、同じコンテナに入り得るので、名前空間で衝突を避けます。

5つ目は、RCLCPP_COMPONENTS_REGISTER_NODE のマクロです。このクラスを、名前で探して作れる部品として登録するマクロです。中では、クラス名と、クラスを作る関数の対応表、つまり class_loader というプラグインの仕組みに登録しています。名前空間の外、ファイルの末尾に書きます。

2つ目のサンプルは、src の listener_component.cpp です。

listener_component.cpp は、30行ほどのコードで、ブロックの形は talker_component.cpp と同じです。include のあと、namespace learn_components の中に、Node を継承した Listener のクラスがあります。要の行はコンストラクタで、NodeOptions の options を受け取って、Node に listener と options を渡し、本体で、chatter の購読を、キューの深さ10 で作ります。届いたときの処理はラムダで書き、received と文字列をログに出します。メンバは購読の sub_ だけで、ファイルの最後に、RCLCPP_COMPONENTS_REGISTER_NODE の learn_components の Listener の1行があります。

原文の解説では、変更点は talker_component.cpp と同じ4点、つまり NodeOptions のコンストラクタ、main を消したこと、名前空間、登録のマクロで、購読とログの部分は、フェーズ3-1 の listener.cpp のまま、とあります。

## 5. CMakeLists.txt でライブラリとして登録する

主な API、こちらは CMake の書き方の表で、2列で、3行あります。

共有ライブラリを作るには、add_library に、ライブラリ名、SHARED、ソースのファイルを渡します。

コンポーネントとして登録し、単独の実行ファイルも作るには、rclcpp_components_register_node に、ライブラリ名、PLUGIN とクラス名、EXECUTABLE と実行ファイル名を渡します。

ライブラリをインストールするには、install の TARGETS にライブラリ名を書き、ARCHIVE と LIBRARY の置き場所を lib、RUNTIME の置き場所を bin にします。

足す場所は、learn_components の CMakeLists.txt の、find_package の並びの後、if BUILD_TESTING の前です。

足す行は、4つのまとまりで15行ほどです。1つ目は add_library で、pubsub_components という SHARED のライブラリを、talker_component.cpp と listener_component.cpp から作ります。2つ目は ament_target_dependencies で、そのライブラリに rclcpp、rclcpp_components、std_msgs をつなぎます。3つ目が要の行で、rclcpp_components_register_node を2回書きます。1回目は PLUGIN を learn_components の Talker、EXECUTABLE を talker_node に、2回目は PLUGIN を learn_components の Listener、EXECUTABLE を listener_node にします。4つ目は install の TARGETS で、pubsub_components を、ARCHIVE と LIBRARY は lib へ、RUNTIME は bin へ置きます。

原文の解説の要点は4つです。

1つ目。add_library の SHARED は、フェーズ3-1 の add_executable、つまり実行ファイルを作る指定の代わりに、共有ライブラリの libpubsub_components.so を作ります。共有ライブラリは、それだけでは実行できず、実行中のプログラムが後から読み込んで使う部品です。2つのコンポーネントを、1つのライブラリにまとめてかまいません。

2つ目。rclcpp_components_register_node は、2つのことをします。1つは、PLUGIN に書いたクラスを、このパッケージのコンポーネントとして、ROS2 の索引、ament index に登録することです。これで ros2 component types に出て、コンテナが名前で探せるようになります。もう1つは、EXECUTABLE に書いた名前で、そのコンポーネントを1つだけ動かす単独の実行ファイルを自動で作り、インストールまですることです。main を自分で書かなくても、ros2 run learn_components talker_node で、これまでどおり単独のプロセスとして動かせます。

3つ目。install の TARGETS は、ライブラリを install の learn_components の lib へ置きます。フェーズ3-1 の実行ファイルの置き場所、つまり lib の下のパッケージ名のフォルダとは、置き場所が違う点に注意します。自動で作られた talker_node などは、登録の関数が自分でインストールするので、ここに書かなくてかまいません。

4つ目。ament_package は、これまでどおり、ファイルの最後に置きます。

## 6. ビルドして登録を確かめる

ros2_ws に移り、colcon build に --symlink-install と --packages-select learn_components を付けてビルドし、source install/setup.bash をします。そのあと、ros2 component types と、ros2 pkg executables の learn_components を実行します。

期待する結果です。ビルドは、learn_components を始めて、終わったという行と、1つのパッケージが終わった、という要約が出ます。ros2 component types の表示には、ROS2 本体のパッケージのコンポーネントもたくさん並びますが、その中に、learn_components というパッケージ名と、その下に字下げして、learn_components の Talker と、learn_components の Listener の2行が出ます。ros2 pkg executables の learn_components には、listener_node と talker_node の2つが出ます。

ros2 component types は、索引に登録されたコンポーネントを、パッケージ名と、その下のクラス名で並べます。ここに2行が出れば、コンテナから読み込める状態になっています。ノードは何も起動していません。索引のファイルを読むだけです。

ros2 pkg executables には、main を書いていないのに、talker_node と listener_node が出ます。5節の EXECUTABLE の指定で、自動で作られたものです。

ls -l で install の learn_components の lib を見ると、ライブラリの libpubsub_components.so が見えます。

## 7. 動かす

同じコンポーネントを3通りの方法で動かし、最後に、フェーズ3-1 の Python の版と組み合わせます。

### 7-1. コンテナに手で読み込む、ros2 component

ターミナル1 で、中身が空のコンテナ、つまりノードを読み込むためのプロセスを起動します。コマンドは、ros2 run rclcpp_components component_container で、Ctrl+C を押すまで動き続けます。

ターミナル2 で、そこへコンポーネントを1つずつ読み込みます。まず ros2 component list で一覧を見ます。次に、ros2 component load で、/ComponentManager に、パッケージ learn_components の、クラス learn_components の Talker を読み込みます。同じように Listener も読み込みます。もう一度 ros2 component list を見たあと、ros2 component unload で、/ComponentManager の1番を取り外します。

期待する結果です。ターミナル2 では、最初の list で /ComponentManager だけが出ます。Talker の load では、1番のコンポーネントを /ComponentManager のコンテナのノードに、/talker として読み込んだ、と出ます。Listener の load では、2番を /listener として読み込んだ、と出ます。2回目の list では、/ComponentManager の下に、1 の /talker と、2 の /listener が並びます。unload では、1番を取り外した、と出ます。

ターミナル1 のコンテナには、Talker を読み込んだところから、ComponentManager のログで、ライブラリを読み込んだ、つまり Load Library と、ライブラリのパスが出ます。続いて、クラスを見つけた、つまり Found class と、作った、つまり Instantiate class の行が、NodeFactoryTemplate の learn_components の Talker という名前付きで出ます。そのあと、talker の publish の hello 0、hello 1 が出ます。Listener を読み込むと、同じ3行の後に、talker の publish の hello 2 と、listener の received の hello 2 が続きます。

この表示の読み方が4つあります。

1つ目。コンテナは、起動しただけでは何も表示しません。ノード名は、既定で /ComponentManager になります。ros2 component list の1行目がそれです。

2つ目。load のたびに、コンテナのターミナルへ、Load Library、Found class、Instantiate class の3行が出て、その直後からノードが動き始めます。プロセスを新しく起動していないのに、ノードが増えていく点が、この節の要点です。

3つ目。load の応答の1 と2 は、コンテナの中での通し番号、ID です。unload には、この番号を渡します。1番を unload した後は、talker のログが止まり、listener は残ったままになります。送り手がいないので、何も受け取りません。

4つ目。talker と listener のログが、同じ1つのターミナル、ターミナル1 に混ざって出ます。同じプロセスの中で動いている証拠です。別のターミナルで、ps でプロセスの番号とコマンド名を並べ、component、talker、listener で grep すると、component_conta という1行だけが出ます。コマンド名は15文字で切れるためです。フェーズ3-1 のように、2つを別々に ros2 run した場合は、talker と listener の2行が出ます。

### 7-2. 単独の実行ファイルとして動かす

ターミナル1 で ros2 run learn_components talker_node、ターミナル2 で ros2 run learn_components listener_node を起動します。

期待する結果です。表示は、フェーズ3-1 の3-3節と同じで、C++ の版ならフェーズ3-1 の4-3節と同じです。ターミナル1 には、talker の publish の hello N が、ターミナル2 には、listener の received の hello N が出ます。

main を1行も書いていない同じコードが、今度は2つの別々のプロセスとして動いています。7-1節と7-2節で変わったのは起動の仕方だけで、コードもビルドも同じです。これが、配置を後から決める、ということです。

### 7-3. launch で、1つのコンテナにまとめて起動する

フェーズ4 の learn_bringup に、launch ファイルを1つ足します。launch からコンテナを起動する専用のアクション、ComposableNodeContainer を使います。

主な API の表は、2列で、3行あります。

コンテナを起動し、中にコンポーネントを入れるのは、launch_ros の actions の ComposableNodeContainer です。name、namespace、package に rclcpp_components、executable に component_container、そして composable_node_descriptions に、入れるもののリストを渡します。

入れるコンポーネントを1つ書くのは、launch_ros の descriptions の ComposableNode です。package、plugin に名前空間付きのクラス名、name、extra_arguments を渡します。

プロセス内通信を使うには、extra_arguments に、use_intra_process_comms を True にした辞書を入れたリストを渡します。

まず、learn_bringup の package.xml の exec_depend の並びに、learn_components と rclcpp_components の2行を足します。

サンプルは、learn_bringup の launch フォルダの components.launch.py です。

components.launch.py は、30行ほどのコードで、ブロックは、先頭の import と、generate_launch_description の関数の2つです。import では、LaunchDescription、ComposableNodeContainer、ComposableNode を読み込みます。関数の中では、container という変数を1つ作り、それだけを LaunchDescription に入れて返します。要の行は、その ComposableNodeContainer で、name は pubsub_container、namespace は空、package は rclcpp_components、executable は component_container、output は screen です。composable_node_descriptions のリストには、ComposableNode を2つ並べます。1つ目は、package が learn_components、plugin が learn_components の Talker、name が talker、2つ目は、plugin が learn_components の Listener、name が listener です。どちらも extra_arguments で、use_intra_process_comms を True にします。

原文の解説の表は、2列で、5行あります。

ComposableNodeContainer は、7-1節で手で起動した component_container を、launch から起動します。name はコンテナ自身のノード名で、ここでは pubsub_container です。既定の ComponentManager を上書きしています。namespace が空なのは、名前空間なし、ということです。

composable_node_descriptions は、コンテナが起動した直後に読み込むコンポーネントの一覧です。7-1節の ros2 component load を、launch が代わりに行います。

ComposableNode の package と plugin は、ros2 component load の2つの引数、つまりパッケージ名とクラス名にあたります。name は、ノード名の指定です。

extra_arguments の use_intra_process_comms を True にする指定は、このノードに、プロセス内通信を使わせる指定です。プロセス内通信は、同じプロセスの中の相手とは、DDS を通さず、メモリの上で受け渡す通信です。この指定は、コンストラクタで受け取る NodeOptions に入って届きます。

output が screen なのは、コンテナのログを端末に出すためです。コンテナの中の全部のノードのログが、まとめて出ます。

フェーズ4 の pubsub.launch.py と比べると、Node が2つ並んでいた、つまりプロセスが2つだったところが、ComposableNodeContainer が1つ、つまりプロセスが1つになり、ノードはその中身として書かれています。

launch ファイルを追加したので、learn_bringup をビルドし直してから起動します。ros2_ws で colcon build をし、source をしてから、ros2 launch learn_bringup components.launch.py を、まず --print 付きで、次に付けずに実行します。

--print の期待する結果です。LaunchDescription の木の下に、ExecuteProcess が1つだけ、つまり rclcpp_components の component_container を起動するものだけが表示されます。アドレスの数字は毎回変わります。起動されるプロセスは component_container の1つだけで、talker や listener は木に出てきません。コンポーネントは、プロセスが起動した後に、コンテナへ読み込まれる中身だからです。

起動したときの期待する結果、抜粋です。component_container-1 のプロセスが起動した、と出たあと、pubsub_container のログで、Load Library、Found class、Instantiate class の3行が Talker について出て、launch_ros の、コンポーザブルなノードを読み込むアクションから、/talker のノードを /pubsub_container のコンテナに読み込んだ、という行が出ます。Listener についても同じ4行が出ます。そのあと、talker の publish の hello 0 と、listener の received の hello 0 が出ます。

行の先頭の、角かっこの component_container-1 が、talker の行にも listener の行にも付きます。フェーズ4 の4-1節では、talker-1 と listener-2 と別々でした。1つのプロセスの中で2つのノードが動いていることが、ログの印からも分かります。

別のターミナルで確かめると、ros2 node list には、/listener、/pubsub_container、/talker の3つが出ます。ros2 component list には、/pubsub_container の下に、1 の /talker と、2 の /listener が並びます。

ros2 node list から見ると、/talker と /listener は、フェーズ3-1 と同じノードで、コンテナのノードの /pubsub_container が1つ増えているだけです。ノードを使う側、つまりトピックの相手や、ros2 topic などのツールからは、そのノードが単独のプロセスなのか、コンテナの中なのかは区別されません。

### 7-4. フェーズ3-1 の Python の版と組み合わせる

7-3節の launch を動かしたまま、別のターミナルで、フェーズ3-1 の Python の版の listener を、ros2 run learn_py listener で起動します。

期待する結果です。Python の版の listener も、コンテナの中の talker からのメッセージを受け取り、received の hello と番号が出ます。

コンテナの中の talker は、同じプロセスの listener にはプロセス内通信で、外の Python の listener には DDS で、同じメッセージを届けています。受け取る側は、相手がコンポーネントかどうかも、C++ か Python かも気にしません。つながりを決めているのは、トピック名と型、つまりインターフェースだけです。なお、ノード名の listener が2つになるので、ros2 node list では、重複の警告が出ることがあります。フェーズ3-1 の6節の課題2と同じ現象です。気になる場合は、ros2 run learn_py listener に --ros-args と、ノード名を py_listener に付け替える remap を付けて、名前を変えます。

課題が4つあります。

課題1。7-1節の手順で、--node-name、短く書くと -n を付けて、Talker を2つ読み込みます。たとえば、ros2 component load の最後に -n talker2 を付けます。1つのプロセスの中に、同じクラスのノードが2つ動くことを確かめます。

課題2。7-1節の手順で、chatter を chatter2 に付け替える -r を付けて Listener を読み込み、talker のメッセージが届かなくなることを確かめます。フェーズ4 の4-6節で見た remap が、コンテナへの読み込みでも同じように使えることを確かめます。

課題3、発展です。component_container の代わりに、component_container_mt、つまり複数のスレッドで回すコンテナがあります。ros2 pkg executables の rclcpp_components で種類を確かめ、どんなときに使い分けるかを調べます。手がかりがあります。ふつうの spin、つまり単一のスレッドは、コールバックを1つずつ順に処理するので、長い処理のコールバックが1つあると、その間は同じプロセスの他のコールバックが待たされます。複数のスレッドなら、別のノード、つまり別の部品のコールバックどうしを、並行して動かせます。同じノードの中のコールバックまで並行させるには、コールバックグループの指定も要ります。任意のフェーズ3-5 を読んだ場合は、その4節の Python の版のアクションサーバで、MultiThreadedExecutor と ReentrantCallbackGroup を使った理由が、これにあたります。

課題4、発展です。プロセス内通信では、publish に std の unique_ptr でメッセージを渡すと、コピーせずに、所有権ごと相手へ渡せます。これをゼロコピーと呼びます。公式のドキュメントの intra-process の説明を調べ、talker_component.cpp をその形に書き換えてみます。

## 8. フェーズ3-1 との違いのまとめ

3列の表で、7行あります。列は、観点、フェーズ3-1 のふつうのノード、この章のコンポーネントです。

1つのファイルの中身は、ふつうのノードでは、ノードのクラスと main です。コンポーネントでは、ノードのクラスと登録のマクロで、main はありません。

ビルドの成果物は、ふつうのノードでは、add_executable で作る実行ファイルです。コンポーネントでは、add_library の SHARED で作る共有ライブラリで、単独の実行ファイルも自動で作れます。

プロセスとノードの関係は、ふつうのノードでは、1つのプロセスに1つのノードと固定です。コンポーネントでは、起動のときに決めます。1つのプロセスに複数でも、1つのプロセスに1つでもかまいません。

ノードの間の通信は、ふつうのノードでは、いつも DDS、つまりプロセスの間の通信です。コンポーネントでは、同じコンテナの中なら、プロセス内通信を選べます。外の相手とは DDS です。

実行中の組み替えは、ふつうのノードではできず、プロセスの起動と停止だけです。コンポーネントでは、ros2 component の load と unload で、プロセスを止めずに、ノードを足したり引いたりできます。

1つのノードの異常の影響は、ふつうのノードでは、そのプロセスだけが落ちます。コンポーネントでは、同じコンテナの全部のノードが巻き込まれます。

対応する言語は、ふつうのノードでは Python と C++、コンポーネントでは、Jazzy の時点で C++ だけです。

コンポーネントは、いつも良いわけではありません。同じコンテナに入れると、効率は上がりますが、1つのノードの不具合、たとえば例外で落ちる、コンストラクタで止まる、が他を巻き込みます。開発中やデバッグ中は、7-2節のように別々のプロセスで動かし、完成したら7-3節のように1つのコンテナにまとめる、という使い分けができるのが、コンポーネントのいちばんの利点だ、とあります。

## 9. マイクロサービスの考え方との対応

マイクロサービスは、1つの大きなアプリケーションを、小さく独立したサービスの集まりとして作る考え方です。各サービスは、Web API のような決められたインターフェースだけでやり取りし、それぞれを別々に作り、別々に配置し、更新できます。ROS2 のノードとコンポーネントは、これとよく似た構造を持っています。

対応の表は、2列で、5行あります。左がマイクロサービスの考え方、右が ROS2 での対応です。

小さく独立したサービスは、1つの役割だけを持つノードにあたります。talker、listener、フェーズ5 のプラントや PI 制御などです。

決められたインターフェースでだけやり取りすることは、トピック名とメッセージの型にあたります。7-4節で、相手の言語や配置を問わずに、つながりました。

配置、つまりどのサーバやコンテナで動かすかを、実装と切り離すことは、コンポーネントの配置を起動のときに決めることにあたります。7-1節から7-3節です。

障害の影響の範囲を小さく保つことは、ノードを別のプロセスに分けることにあたります。8節の最後の段落の、トレードオフの話です。

同じサービスを複数動かすことは、同じクラスのノードを、名前を変えて複数読み込むことにあたります。7節の課題1です。

一方で、違いもあります。一般的なマイクロサービスは、ネットワーク越しの HTTP などで通信し、サービスごとにデータの保存先を分けることが多いのですが、ROS2 のノードは、DDS の出版と購読、つまりトピックが中心で、同じ PC の中での速いやり取りを重視します。また、ここでのコンテナは、ROS2 のコンポーネントを入れるプロセスのことで、Docker のような OS のレベルのコンテナとは別物です。ROS2 のシステムを Docker で配置することもよくありますが、それはまた別の層の話になります。

フェーズ5 は Python で書くので、コンポーネントは使いませんが、この考え方はそのまま生かせます。プラント、PI 制御、目標の速度の各ノードを、それぞれ1つの役割だけを持つ部品として作り、つながりはトピック名と型だけで決めます。ノードのクラスには、起動の手順、つまり main に関する処理を混ぜず、設定はパラメータで外から与えます。そうしておけば、後でノードを差し替えたり、たとえば Python の版のプラントを C++ の版にしたり、配置を変えたりしても、他のノードは変えずに済みます。

## 10. つまずきやすい点

2列の表で、7行あります。列は、症状と、確かめることです。

1行目。ros2 pkg create で、引数の package_name が要る、というエラーが出る場合。--dependencies の直後に、パッケージ名を書いていないかを確かめます。3節のとおり、後ろに別のオプションを続けます。

2行目。ros2 component types に learn_components が出ない場合。rclcpp_components_register_node を書いたか、ビルドの後に source install/setup.bash をしたかを確かめます。

3行目。load で、コンポーネントの読み込みに失敗した、と出る場合。パッケージ名とクラス名、つまり名前空間を含む learn_components の Talker のつづりを確かめます。ros2 component types の表示と一致させます。

4行目。ビルドで、登録のマクロのあたりに、コンストラクタの引数の型が合わない、というエラーが出る場合。コンストラクタが、rclcpp の NodeOptions への const の参照を受け取る形になっているか、引数なしのままになっていないかを確かめます。

5行目。launch やコマンドで付けた remap やパラメータが効かない場合。コンストラクタで受け取った options を、Node に名前と一緒に渡しているかを確かめます。

6行目。コンテナにノードを入れた後、他のノードが読み込まれない場合。コンストラクタの中に、長い処理や、sleep やループのような待ちを書いていないかを確かめます。

7行目。ros2 launch で、components.launch.py が見つからない、と出る場合。launch ファイルを追加した後に、learn_bringup をビルドし直したかを確かめます。

## 11. 次へ

フェーズ5、車両のシミュレーションの本体へ進みます。最初はフェーズ5-0 で、Gazebo を導入して動かします。9節の最後の段落のとおり、ノードを1つの役割を持つ部品として作り、つながりをトピック名と型で決める考え方を、Python のノードの設計に生かします。

## 12. 公式のドキュメントと参考資料

確かめた状況は、2026年9月24日の時点です。下の URL は、Web 検索の結果で実在を確かめました。docs.ros.org は、ボット対策で本文の取得を断られるため、内容の照らし合わせはできていません。API の使い方は、手元の /opt/ros/jazzy、つまり rclcpp_components の CMake の関数の説明、ros2 component load の -h、ros2component のソースで確かめた、とあります。

公式の資料は、ROS 2 Jazzy の4つです。1つ目は、複数のノードを1つのプロセスに組み合わせるチュートリアルで、コンポーネントの作り方と、ros2 component での読み込みを扱います。2つ目は、ROS 2 の launch で、コンポーザブルなノードを起動するハウツーで、launch からコンテナとコンポーネントを起動する方法を扱います。3つ目は、中級の概念の目次で、コンポーネントの考え方、About Composition は、ここからたどります。4つ目は、公式のデモの composition パッケージで、コードを読む場合は、丸ごと写さずに、要点だけを参考にする、とあります。

以上で、コンポーネントの間章の話を終わります。

## 出典について

この原稿は、SanghunIm1991 さんの [ros2MinimalPhysicalAi の「間章 手順書: コンポーネント指向でノードを組み立て直す（フェーズ4とフェーズ5の間）」](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/docs/interlude_components.md)を、聞くために要約・意訳したものです。図の [interlude_components_layout.svg](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/docs/img/interlude_components_layout.svg) は、言葉で説明しました。元にしたのは、[2026年10月14日の版](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/132df7b64d48d560def7ec7149f7003938d3d8e5/docs/interlude_components.md)です。原文の文章と図と同じく、[クリエイティブ・コモンズ 表示 4.0 国際ライセンス](https://creativecommons.org/licenses/by/4.0/deed.ja)で提供します。

原稿の中に原文の表記のまま書いたコマンドと、コードの関数やクラスの名前は、原文では [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0) の対象です。ライセンスの全文は、原文のリポジトリの [LICENSE-APACHE-2.0](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/LICENSE-APACHE-2.0) にあります。サンプルコードは写さず、役割と要の行を言葉で説明しました。

原文では、サンプルは公式チュートリアルの転載ではなく、API の呼び方は [ROS 2 Documentation](https://docs.ros.org/en/jazzy/)（Open Robotics、[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)）の公式の例と同等だとしています。表示の例は、ros2 や colcon などの各ツールの表示を言葉で説明したものです。
