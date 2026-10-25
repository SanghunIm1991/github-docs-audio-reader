<!--
聞くための原稿（読み上げでは読まれない記録）
原文: SanghunIm1991/ros2MinimalPhysicalAi の main ブランチの docs/tips.md のうち、2節（CMakeLists.txt の読み方）。あわせて、冒頭の説明、項目の一覧の2節の行、出どころのうち2節に関わる部分、15節の参考資料のうち2節に関わるもの
原文のコミット: 56e5e3044ad955d0b57c9300d1f03f2306cc64ae（2026-10-17）
作成: 2026-10-25、Claude Code が手作業で作成（原稿化スキルはまだない）
原文のライセンス: 文章は CC BY 4.0、コードとコマンドは Apache-2.0（それぞれ LICENSE の2と1）で、2節にはコードのブロックがない。2-2節の表で引用している CMakeLists.txt の各行は、ros2 pkg create の雛形（ros2pkg、Apache License 2.0）のもので、LICENSE の「第三者の著作物」にある。この原稿は、原文を聞くために要約・意訳したもの（改変あり）
方針: Tips集は、テーマごとに docs/tips/ に番号を付けて分ける（2026-10-19 にユーザーが決定）。1つのテーマだけを聞いても分かるよう、頭に Tips集の冒頭の説明と、このテーマの関係する手順書・出どころを置き、末尾に、このテーマの参考資料を置く（01_use_sim_time.md と同じ形）。英語の略語や製品名、CMake の命令・キーワード・関数の名前は原文の表記のまま書く。2-2節の表の雛形の行は写さず、各行を「N行目は、命令の名前の行です」と言い、原文の行と説明に出てくる値のうち説明に要るもの（3.8、learn_cpp、PUBLIC、C++17 と C99、rclcpp と std_msgs、hello と src の hello.cpp、install の先のフォルダ）は、説明の側で1回だけ読んで、役割を言葉で説明した。install(TARGETS ...) は、phase3 の原稿にそろえて原文の表記のまま書いた。原文の表がすべての行を説明しているので、要の行は立てなかった。表（雛形の行と意味、PUBLIC・PRIVATE・INTERFACE）は、行と列の数を言い、行ごとに全部読んだ。変数の参照は、原文の説明が変数の名前で参照しているので「PROJECT_NAME という変数」、ジェネレータ式は「ドル記号と山括弧で囲む形」と言い換えた。参考資料は、リンクの題名と括弧の説明を読んだ。文字数の上限は設けない
省いたもの: URL、リンク先のファイル名、冒頭の対象のうち14節の SB3 の版、期待する結果の出どころ（2節には表示がない）、出どころのうち、ほかの節に関わる部分、項目の一覧のほかの節の行、15節の参考資料のうち、ほかの節に関わるものと、その確認状況、15節の出典の注記のうち、ほかの節に関わる部分、2-2節の表の、警告のオプションの名前（3つ）と、コンパイラを調べる条件の書き方、include_directories と add_definitions の括弧の中の省略の記号、-std=c++17 のオプションの書き方（「C++17 を使うオプション」と言い換えた）、target_include_directories・ジェネレータ式・install(TARGETS ...) の括弧の中の省略の記号、install の行の DESTINATION のキーワード
-->

# Tips集 2: CMakeLists.txt の読み方、モダン CMake の要点（聞くための原稿）

これは、ros2MinimalPhysicalAi という教材の、Tips集の2つ目の項目です。

Tips集は、手順書、つまりフェーズの本文に入れると流れが途切れる、分量の少ない補足をまとめた資料です。どの項目も独立しているので、関係する手順書を読んでいるときや、疑問を持ったときに、その項目だけを読めばよい、とあります。

対象は、ROS2 Jazzy と Ubuntu 24.04 です。版に依存する記述は、この資料を作ったときに、/opt/ros/jazzy と Ubuntu のパッケージに入っていたもので確かめた、とあります。所要の目安は、1項目あたり5 から15分の読み物です。

この項目に関係する手順書は、フェーズ2 の2-3節から後と、C++ のサンプルのすべてです。

出どころについて、断りがあります。内容は、/opt/ros/jazzy のソースや、ros2 pkg create が作る雛形などを読んで確かめ、自分の言葉で書いたもので、ソースやドキュメントの転載ではない、とあります。

この原稿では、CMakeLists.txt の行を書き写さずに、命令の名前と役割を言葉で説明します。

## 2. CMakeLists.txt の読み方（モダン CMake の要点）

### 2-1. モダン CMake とは

CMake は、C++ のビルドの手順を書くための道具です。長く使われてきた道具なので、書き方には、古い流儀と新しい流儀があります。おおよそ CMake 3.0、つまり2014年ごろから広まった新しい流儀を、モダン CMake と呼びます。考え方の中心は、次の1点です。

設定は、ターゲットごとに付ける、ということです。ターゲットとは、add_executable、つまり実行ファイルや、add_library、つまりライブラリで作る、ビルドの成果物の1つ1つのことです。古い流儀では、include_directories や add_definitions のように、そのフォルダの CMakeLists.txt の、全部の成果物にまとめて効く命令で設定していました。モダン CMake では、target_ で始まる命令で、どのターゲットに、何が必要かを、1つずつ書きます。成果物が増えても、互いの設定が混ざりません。

フェーズ2 の ros2 pkg create が作った雛形も、この流儀で書かれています。C++ のコードそのもの、つまり C++17 とは別の話で、C++ を書いた経験があっても、CMake を使ったことがなければ、なじみのない書き方だ、とあります。

### 2-2. 雛形を1行ずつ読む

フェーズ2 の2-3節で作った、learn_cpp の CMakeLists.txt の主な行を、上から順に表にしています。ros2 pkg create に、マイナス2つの build-type で ament_cmake を指定したときの雛形で、使い捨ての環境で作って確かめた、とあります。テストの部分、つまり BUILD_TESTING の if の中は省いています。

表は2列で10行です。列は、CMakeLists.txt の行と、その意味です。

1行目は、cmake_minimum_required の行です。このファイルを読むのに必要な、CMake の最低の版を、3.8 と宣言します。版によって使える命令が違うので、最初に宣言します。

2行目は、project の行です。プロジェクトの名前を、learn_cpp に決めます。これより後は、PROJECT_NAME という変数で、この名前を参照できます。

3行目は、コンパイラを調べる if と、add_compile_options の組です。コンパイラが GCC か Clang なら、警告を多めに出すオプションを付けます。add_compile_options は、ターゲットごとでなく全体に効く、古い流儀の命令です。ただ、このパッケージは全部、警告を多めに、という方針なので、全体に掛けている、とあります。

4行目は、find_package の行です。外部のパッケージ、ここでは rclcpp を探して、使えるようにします。付いている REQUIRED は、見つからなければ、ここでエラーにする、という意味です。探す先は、source した環境、例えば /opt/ros/jazzy の、パッケージが置いている設定ファイルです。

5行目は、add_executable の行です。hello という名前のターゲット、つまり実行ファイルを、src の hello.cpp から作ります。これより後の target_ の命令は、この名前で対象を指します。

6行目は、target_include_directories の行です。hello をビルドするとき、ヘッダを探す場所を足します。PUBLIC が付いています。詳しくは2-3節で扱います。

7行目は、target_compile_features の行で、ここにも PUBLIC が付いています。hello には、C++17 と C99 に対応したコンパイルが必要だ、と宣言します。古い流儀では、C++17 を使うオプションを直接書きましたが、この書き方なら、CMake がコンパイラに合ったオプションを選びます。

8行目は、ament_target_dependencies の行です。hello が rclcpp と std_msgs を使う、と宣言します。ament_cmake が用意している関数で、CMake の標準の命令ではありません。中では、それぞれのパッケージのヘッダの場所とライブラリを、hello に結び付けています。CMake の標準の target_include_directories と target_link_libraries を、まとめて呼ぶのに近い、とあります。

9行目は、install(TARGETS ...) の行です。ビルドした hello を、install の learn_cpp の lib の learn_cpp へ置きます。ros2 run は、この場所から実行ファイルを探します。これはフェーズ2 の2-6節で扱いました。

10行目は、ament_package です。ROS2 のパッケージとして必要な情報、例えば索引への登録などを書き出します。ファイルの最後に置く決まりです。

フェーズ3-1 から後で、C++ のサンプルを足すたびに書く、add_executable、ament_target_dependencies、install(TARGETS ...) の3点セットは、この表の同じ行の繰り返しです。

### 2-3. PUBLIC と PRIVATE と、ドル記号と山括弧の書き方

target_ の命令には、PUBLIC、PRIVATE、INTERFACE のどれかを書きます。これは、その設定を、このターゲットを使う側にも伝えるか、の指定です。

表は3列で3行です。列は、キーワードと、このターゲット自身のビルドに使うか、このターゲットを使う側にも伝えるか、です。

1行目は PRIVATE で、自身のビルドに使い、使う側には伝えません。

2行目は PUBLIC で、自身のビルドに使い、使う側にも伝えます。

3行目は INTERFACE で、自身のビルドには使わず、使う側に伝えます。

違いが効いてくるのは、ライブラリを作って、別のターゲットやパッケージから使わせるとき、例えば間章のコンポーネントのような場合です。実行ファイルはほかから使われないので、どれを書いても、結果はほぼ同じになります。フェーズ3-2b で、共通部品のヘッダを読むときに PRIVATE を書いたのは、このターゲットの中だけで使う、ということをはっきりさせるためです。

雛形の target_include_directories には、BUILD_INTERFACE と INSTALL_INTERFACE を、ドル記号と山括弧で囲んだ書き方があります。これはジェネレータ式と呼ばれる書き方です。ドル記号と山括弧の中に、条件、コロン、値を書く形で、条件に合うときだけ値を使う、という意味になります。ここでは、ビルドするときはソースの include を、インストールした後は install の中の include の learn_cpp を、ヘッダの探し先にしています。ヘッダをライブラリとして公開する場合のための書き方で、実行ファイルがパッケージの中のヘッダを読むだけなら、フェーズ3-2b のように短く書いてよい、とあります。フェーズ3-2b の該当する箇所の補足にも、同じ説明があります。

### 2-4. 読むときのコツ

コツは3つです。

1つ目は、ターゲットの名前を追うことです。add_executable で生まれた名前が、target_ の命令、ament_target_dependencies、install(TARGETS ...) に、何度も出てきます。同じ名前の行を拾えば、1つの成果物に必要な設定がそろいます。

2つ目は、依存は3か所、ということです。C++ では、package.xml の depend の要素、find_package、ament_target_dependencies の3か所に、依存を書きます。これは、フェーズ3-2a の、Python の版と C++ の版の違いのまとめでも整理します。find_package は、探して使える状態にするもの、ament_target_dependencies は、どのターゲットがそれを使うかを示すもので、役割が違います。

3つ目は、ament_ で始まるものは、ROS2 の追加分だ、ということです。CMake の標準の命令と見分けがつけば、CMake の一般的な解説と、ROS2 の解説の、どちらを調べればよいかが分かる、とあります。

## 参考資料

確認の状況は、2026年9月25日の時点のものです。原文の参考資料のうち、この項目に関わるものは2つです。どちらも、この資料を作ったときに、実在を Web 検索で確かめたが、本文は読み直していない、とあります。

1つ目は、ROS2 Jazzy の公式ドキュメントの、ament_cmake user documentation です。ament_target_dependencies などの、ament_ の関数が書かれています。

2つ目は、CMake の公式ドキュメントの、cmake-buildsystem のページです。ターゲットと、PUBLIC、PRIVATE、INTERFACE の考え方が書かれています。

原文には、文章は自分の言葉で書いたもので、ドキュメントやソースの転載ではない、とあります。CMakeLists.txt の各行は、ROS2 の雛形を、説明に必要な範囲で引用した、とあります。

## 出典について

この原稿は、SanghunIm1991 さんの [ros2MinimalPhysicalAi の「Tips集: 手順書の本文に入れなかった小さな補足」](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/docs/tips.md)のうち、2節を、聞くために要約・意訳したものです。元にしたのは、[2026年10月17日の版](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/56e5e3044ad955d0b57c9300d1f03f2306cc64ae/docs/tips.md)です。原文の文章と同じく、[クリエイティブ・コモンズ 表示 4.0 国際ライセンス](https://creativecommons.org/licenses/by/4.0/deed.ja)で提供します。

原文のコードとコマンドは、[Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0) の対象です。ライセンスの全文は、原文のリポジトリの [LICENSE-APACHE-2.0](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/LICENSE-APACHE-2.0) にあります。2節にはコードのブロックがなく、原稿に原文の表記のまま書いた CMake の命令や関数の名前は、次の段落の雛形の行から取ったものです。

原文の2-2節の表で引用している CMakeLists.txt の各行は、ros2 pkg create の雛形、つまり [ros2cli](https://github.com/ros2/ros2cli) の ros2pkg（Apache License 2.0）のものです。この原稿では、その行を写さず、命令の名前と、原文の説明に出てくる値だけを言い、役割を言葉で説明しました。原文では、参考資料に [ROS 2 Documentation](https://docs.ros.org/en/jazzy/)（Open Robotics、[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)）と、[CMake](https://cmake.org/) の公式ドキュメントのページを挙げています。
