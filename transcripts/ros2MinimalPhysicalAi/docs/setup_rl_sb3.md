<!--
聞くための原稿（読み上げでは読まれない記録）
原文: SanghunIm1991/ros2MinimalPhysicalAi の main ブランチの docs/setup_rl_sb3.md
原文のコミット: 132df7b64d48d560def7ec7149f7003938d3d8e5（2026-10-14）
作成: 2026-10-23、Claude Code が手作業で作成（原稿化スキルはまだない）
原文のライセンス: 文章は CC BY 4.0、コマンドは Apache-2.0（それぞれ LICENSE の2と1）。4節の、SB3 の公式の導入の案内の2通りのコマンドは、Stable-Baselines3 の公式の文書（Copyright (c) 2019 Antonin Raffin、MIT License）からの抜粋で、LICENSE の「第三者の著作物」にある。原文の末尾に、gymnasium[classic-control] を入れる案内は Gymnasium の公式の文書（Copyright (c) 2016 OpenAI、Copyright (c) 2022 Farama Foundation、MIT License）に基づき、3節のコマンドは PyTorch の公式の案内と同等の形で、説明の文章は公式の文書を参考に自分の言葉で書いたもの、とある。この原稿は、原文を聞くために要約・意訳したもの（改変あり）
方針: 英語の略語や製品名、パッケージ名、コマンドは原文の表記のまま書く。ただし、4節の SB3 の公式の文書から抜粋した2通りのコマンドは写さず、何を入れる形かを言葉で説明した（MIT License の部分を原稿に入れないため）。期待する結果（各ツールの表示）も、写さずに、何が表示されるかと原文の解説が使う値を言葉で説明した。表（つまずきやすい点）は言葉で説明する。文字数の上限は設けない
省いたもの: URL、型の定義へのリンク、リンク先のファイル名、apt の表示のパッケージの版、pip のダウンロードの行のファイル名の細部と大きさ、Successfully installed の行のうち原文の解説が使わないパッケージの名前と版、Traceback の途中の行とファイルの行番号、ホームのフォルダのユーザー名の部分
-->

# 環境構築: 強化学習のライブラリ、Stable-Baselines3（聞くための原稿）

これは、ros2MinimalPhysicalAi という教材の、環境構築の手順書の話です。フェーズ7、つまり強化学習で使うライブラリを、ROS2 とは別の仮想環境、つまり venv に導入します。使うのは、4つです。強化学習のアルゴリズムを集めたライブラリの Stable-Baselines3、以下 SB3。その追加の部品集の sb3-contrib。学習させる環境の共通の形を決めるライブラリの Gymnasium。そして、ニューラルネットワークの計算に使う PyTorch の、CPU 版です。

想定する環境は、WSL2 と Ubuntu 24.04 と ROS2 Jazzy の環境構築を済ませた Ubuntu 24.04 で、Python は3.12 です。所要時間の目安は30分程度で、ダウンロードの時間を含み、回線の速さで前後します。必要なディスクの空きは2ギガバイト程度で、導入後の仮想環境の大きさは、4節の期待する結果で見ます。

この手順書の位置づけの囲みです。フェーズ7、つまり7-0 から7-6 は、ひととおり作成を終えた段階です。今後の見直しで、導入するライブラリと版を改めることがある、とあります。

期待する結果の出どころの囲みもあります。期待する結果は、筆者の環境に、2026年10月2日に導入したときに、実際に表示されたものです。ただし、画面の記録が残っていなかった分は、仮想環境に導入されたものから書き起こしています。それは、3節のダウンロードの行のファイル名と、2節の pip の更新と、4節の導入の、Successfully installed の行です。ダウンロードの行は、導入された PyTorch の記録にある版と、対応する環境の名前から、Successfully installed の行は、導入された版の一覧からの抜粋です。版の数字、所要時間、ディスクの大きさは、導入した時期と環境によって違います。

2026年10月6日に追加した7節の表示の出どころは、次のとおりです。import rclpy の失敗は、筆者の仮想環境で実際に実行した表示です。pip install pyyaml==6.0.3 の Successfully installed の行は、PyTorch などを入れていない、使い捨ての仮想環境に入れたときの表示です。その仮想環境の site-packages を PYTHONPATH に足して、筆者の仮想環境の Python で、rclpy: OK と表示されることを確かめました。PyTorch を入れていない仮想環境では、launch-ros は setuptools を必要とする、という ERROR の行も出ましたが、3節で入れる PyTorch が setuptools を一緒に入れるので、手順書のとおりの仮想環境では出ない見込みです。7節の末尾の注意書きの、generate-parameter-library-py は typeguard を必要とする、という表示は、Gazebo の物理の間章の5節のパッケージを入れた環境で、7節の pip install pyyaml==6.0.3 を実行したときに、2026年10月12日に実際に出たものです。3節の導入で、同じパッケージについて出る行は、確かめておらず、pip の仕組み、つまり入れるパッケージと、それに依存する入れ済みのパッケージだけを点検する、という仕組みから想定したものです。

この原稿では、ツールの表示を書き写さず、何が表示されるかを言葉で説明します。

## 目的とゴール

ROS2 のシステムの Python、つまり apt で入ったものを汚さずに、強化学習のライブラリを使える仮想環境を作ります。

完了の判定基準は4つで、すべて満たしたら完了です。

1つ目。仮想環境のホームの rl_venv を有効にすると、プロンプトの先頭に、かっこ付きの rl_venv が付く。2節です。

2つ目。PyTorch が CPU 版で入り、torch.cuda.is_available() が False を返す。3節です。

3つ目。SB3、sb3-contrib、Gymnasium の版が表示され、Pendulum-v1 の環境を作れる。4節です。

4つ目。フェーズ7-3 の前に、仮想環境から、ROS2 の rclpy を読み込める。7節です。

## 注意

注意は4つです。

1つ目。導入の作業は、自分の手で行います。コマンドの意味が分からないまま、貼り付けて実行しません。

2つ目。sudo pip install や、仮想環境を有効にしないままの pip install はしません。ROS2 の Python のパッケージは、apt で入れたシステムの Python に依存しています。システム側に別の版のライブラリを入れると、ROS2 のノードが動かなくなることがあります。Ubuntu 24.04 では、システムの Python への pip install は、既定で拒否されます。externally-managed-environment のエラーです。

3つ目。仮想環境は、ワークスペース、つまりホームの ros2_ws の外に作ります。ワークスペースの中に置くと、colcon build が仮想環境の中のパッケージまで探しに行き、ビルドが遅くなったり、失敗したりします。

4つ目。導入するものはすべて、公式の配布元から取得します。Ubuntu の apt、Python Package Index、つまり PyPI、そして PyTorch の公式の配布元です。

### なぜ仮想環境を使うのか

仮想環境、つまり venv は、Python のパッケージを入れる場所を、フォルダ1つに閉じ込める仕組みです。有効にしている間だけ、python と pip が、そのフォルダの中を向きます。強化学習のライブラリは、numpy などの共通のライブラリに、新しい版を求めることがあり、ROS2 が使う版とぶつかりえます。仮想環境に分けておけば、ぶつからないうえ、要らなくなったら、フォルダごと消して元に戻せます。6節で扱います。

## 手順

### 1. 仮想環境を作る部品を入れる

Ubuntu 24.04 の既定の状態では、Python の仮想環境を作る部品、つまり venv の ensurepip が、入っていないことがあります。apt で入れます。

sudo apt update をしてから、sudo apt install で python3-venv を入れます。

期待する結果、sudo apt install の分の抜粋です。新しく入るパッケージとして、python3-pip-whl、python3-setuptools-whl、python3-venv、python3.12-venv の4つが並び、最後に、python3.12-venv と python3-venv を設定した、という行が出ます。

python3-venv と、それが依存する python3.12-venv が入れば成功です。すでに入っている場合は、python3-venv はすでに最新の版だ、と表示されます。版の数字は、時期によって違います。

### 2. 仮想環境を作って有効にする

ホームディレクトリの下に、仮想環境 rl_venv を作ります。

python3 -m venv で、ホームの rl_venv を作り、source で、ホームの rl_venv の bin の activate を読み込んで、仮想環境を有効にします。続けて、python --version と、which python pip を実行します。

期待する結果です。python --version は、Python 3.12.3 と表示します。which python pip は、ホームの rl_venv の bin の python と、同じフォルダの pip を、1行ずつ表示します。

プロンプトの先頭に、かっこ付きの rl_venv が付き、python と pip が、ホームの rl_venv の bin の下を指していれば、仮想環境が有効になっています。Python の版の細かい数字の3.12.3 は、Ubuntu の更新の状況で違うことがあります。

仮想環境は、ターミナルごとに有効にします。新しいターミナルを開いたら、source で、ホームの rl_venv の bin の activate を読み込んでから使います。やめるときは、deactivate を実行します。プロンプトの、かっこ付きの rl_venv が消えます。

続けて、仮想環境の中の pip を、新しくしておきます。python -m pip install に、--upgrade と pip を付けて実行します。

期待する結果、抜粋です。pip の26.2.1 を入れた、つまり Successfully installed の行が出ます。版は、時期によって違います。

### 3. PyTorch、CPU 版を入れる

SB3 より先に、PyTorch の CPU 版を入れます。先に SB3 を入れると、依存関係として、PyPI から、GPU、つまり CUDA 向けの PyTorch が入ります。こちらは、GPU の計算用のライブラリを含むため、数ギガバイトあり、GPU が無い PC では、使わない部分がほとんどになります。

PyTorch の公式の案内、Get Started で、Linux、Pip、Python、CPU を選んだときと同じく、配布元に CPU 版を指定して入れます。この教材では torchvision を使わないので、torch だけを入れます。

pip install torch に、--index-url で、PyTorch の公式の配布元の、CPU 版の場所を指定して実行します。

期待する結果、抜粋です。版は、時期によって違います。最初に、指定した CPU 版の配布元を見ている、という行が出て、torch を集め始め、torch のファイルをダウンロードします。ファイル名には、版の2.14.1 などが入っています。最後に、Successfully installed の行で、torch と、それが依存するライブラリ、たとえば jinja2、networkx、setuptools、sympy などが並びます。

ファイル名に、プラスの cpu と、cp312、つまり Python 3.12 向け、が入っていれば、CPU 版が選ばれています。

launch-ros は pyyaml を必要とするが入っていない、と出る場合の注意書きがあります。末尾の Successfully installed の直前に、ERROR の行が出ることがあります。pip の依存関係の解決は、入っているパッケージのすべてを考えに入れているわけではなく、それが次の依存関係の衝突の元になっている、という文の後に、launch-ros の0.26.12 は pyyaml を必要とするが、入っていない、という行が続きます。4節の導入でも、出ることがあります。

これは導入の失敗ではなく、無視してかまいません。理由はこうです。ホームの .bashrc で ROS2 を読み込んでいると、環境変数 PYTHONPATH に、ROS2 の Python のパッケージの場所、つまり ROS2 のインストール先の、Python 3.12 の site-packages が入ります。そのため、仮想環境の pip にも、ROS2 の launch_ros が見えます。launch_ros が必要とする pyyaml は、apt でシステムの Python の側に、python3-yaml として入っていますが、仮想環境からは、システムの側のパッケージが見えません。そのため pip は、pyyaml が無い、と報告します。

仮想環境の中では ROS2 の launch を使わないので、学習には影響しません。ROS2 のコマンドは、システムの Python で動くので、こちらも影響を受けません。フェーズ7-0 から7-2 では、このまま進めてかまいません。フェーズ7-3 からは、仮想環境の中で ROS2 の rclpy を使うので、7節で pyyaml を入れます。入れた後は、この行は出なくなります。版の数字の0.26.12 は、ROS2 の更新の状況で違うことがあります。Gazebo の物理の間章の5節で、ros2_control のパッケージを入れている場合は、同じ理由で、generate-parameter-library-py が何かを必要とする、という行も出ることがあります。7節の末尾の注意書きで扱います。

入ったことを確かめます。python -c で、torch を import して、torch の版と、torch.cuda.is_available() の結果を表示します。

期待する結果は、torch の版と、GPU を使えるかどうかを並べた1行です。版は、時期によって違います。

版の末尾に、プラスの cpu が付き、torch.cuda.is_available() が False、つまり GPU を使わない、になっていれば成功です。

GPU のある PC で使う場合の注意書きもあります。NVIDIA の GPU を積んだ PC では、PyTorch の公式の案内で、その PC の CUDA の版に合う配布元を選んで入れます。フェーズ7 の7-0 から7-6 の規模では、CPU 版で足ります。GPU が効いてくるのは、二足歩行を本格的に学習させる段階からです。フェーズ7-6 の6節で、その道具と要件を読みます。

### 4. SB3、sb3-contrib、Gymnasium を入れる

SB3 の公式の導入の案内、Installation は、2通りの入れ方を示しています。1つは、stable-baselines3 に、extra という追加の部品の指定を付けて入れる形です。もう1つは、何も付けずに、stable-baselines3 だけを入れる形です。原文は、この2つのコマンドを、公式の文書から抜粋して載せています。

前者は、学習の記録の表示、つまり TensorBoard、画像の処理、つまり OpenCV、Atari のゲームの環境、つまり ale-py などの、追加の部品もまとめて入れます。この教材では Atari のゲームを使わないので、後者の最小の形を基本にし、要る部品だけを足します。足すものは2つです。

1つ目は、gymnasium に、classic-control という指定を付けたものです。振り子、つまり Pendulum などの、古典的な制御の環境を、画面に表示するための部品を含めて入れます。その部品は pygame-ce で、ゲームを作るライブラリの pygame の、コミュニティによる派生版です。Gymnasium の公式の入門、Basic Usage の最初の例も、この形で入れるよう案内しています。

2つ目は、sb3-contrib です。記憶を持つポリシー、つまり RecurrentPPO など、SB3 の追加のアルゴリズムです。フェーズ7 の本編では使いません。フェーズ7-4 の5-2節の末尾で触れる、NN の方策を改良する手がかり、たとえば記憶を持つ方策を使うことを、自分で試すときのために入れておきます。

この手順書を作った時点、2026年9月29日の最新版に固定して入れます。2026年10月2日に、この版で導入して確かめた、とあります。版を固定すると、手順書と同じ結果を再現しやすいです。新しい版を使う場合は、イコール2つ以降を外します。

pip install に、stable-baselines3 の2.9.0、sb3-contrib の2.9.0、そして引用符で囲んだ、classic-control の指定付きの gymnasium の1.3.0 を、それぞれイコール2つで版を固定して渡します。

期待する結果、抜粋です。依存するライブラリの版は、時期によって違います。Successfully installed の行に、cloudpickle などの依存するライブラリと、numpy の2.5.3、pygame-ce の2.5.8、そして入れた3つのパッケージが並びます。

末尾の Successfully installed の行に、stable-baselines3 の2.9.0、sb3-contrib の2.9.0、gymnasium の1.3.0 があれば成功です。torch がもう一度ダウンロードされていないことも確かめます。3節で入れた CPU 版が、そのまま使われます。

版を確かめ、振り子の環境を1つ作ってみます。コマンドは3つです。

1つ目は、python -c で、stable_baselines3、sb3_contrib、gymnasium を import して、3つの版を表示します。

2つ目は、python -c で、gymnasium を gym という名前で import し、gym.make で Pendulum-v1 の環境を作って、その observation_space と action_space を表示します。

3つ目は、du -sh で、ホームの rl_venv の大きさを表示します。

期待する結果です。版と du の大きさは、時期によって違います。1つ目は、2.9.0、2.9.0、1.3.0 と表示します。2つ目は、2行を表示します。1行目は、Box で、下限がマイナス1、マイナス1、マイナス8、上限が1、1、8、形が3つ、型が float32 です。2行目は、Box で、下限がマイナス2.0、上限が2.0、形が1つ、型が float32 です。3つ目は、1010メガバイトと、ホームの rl_venv のフォルダの名前を表示します。

読み方は3つです。

1つ目。1つ目のコマンドの表示は、SB3、sb3-contrib、Gymnasium の版です。

2つ目。2つ目のコマンドの1行目の Box は、振り子の環境が返す観測、つまり3つの数の範囲で、2行目の Box は、エージェントが与える行動、つまりトルク1つの範囲です。中身は、フェーズ7-0 で読みます。

3つ目。仮想環境の大きさは、1ギガバイト前後になります。ほとんどが PyTorch です。

### 5. ROS2 と一緒に使うときの注意

注意は3つです。

1つ目。colcon build は、仮想環境を無効にしたターミナルで行います。仮想環境を有効にしたままビルドすると、ノードの起動用のスクリプトが、仮想環境の Python を指すことがあり、ROS2 のノードの動きが、環境によって変わります。

2つ目。学習のスクリプトは、仮想環境を有効にしたターミナルで動かします。ホームの .bashrc で ROS2 を読み込んでいても、仮想環境の中から、強化学習のライブラリを使えます。ROS2 の Python のパッケージのパスには、SB3 が使うライブラリと、名前がぶつかるものはありません。ただし、環境変数 PYTHONPATH に入っている場所、つまり ROS2 のインストール先や、source したワークスペースの install は、仮想環境のパッケージより先に探されます。ワークスペースで作ったパッケージが、SB3 などと同じ名前にならないようにします。

3つ目。学習した制御器を ROS2 のノードで動かすとき、つまりフェーズ7-5 では、ノード側で仮想環境を要らなくする方法、つまり学習した重みを numpy だけで計算する方法を扱います。フェーズ7-4 の2-2節と4-2節、そしてフェーズ7-5 の話です。

### 6. 作り直すとき、消すとき

仮想環境はフォルダ1つなので、消せば、導入前の状態に戻ります。1節の python3-venv は残ります。版を入れ替えたいときや、導入に失敗したときは、消して、2節から作り直します。

deactivate をしてから、rm -rf で、ホームの rl_venv を消します。

期待する結果です。何も表示されません。deactivate は、プロンプトの、かっこ付きの rl_venv を消します。rm -rf は、確認なしに消すので、実行する前に、消す対象、つまりホームの rl_venv を見直します。ROS2 やワークスペースには、影響しません。

### 7. ROS2 の Python のライブラリを使う準備、フェーズ7-3 の前に

フェーズ7-3 からは、学習の環境の中で、ROS2 の Python のライブラリ rclpy を使い、Gazebo とトピックやサービスでやりとりします。ROS2 を読み込んだターミナル、つまり ROS2 の setup.bash を source 済みのターミナルでは、rclpy そのものは、環境変数 PYTHONPATH に入った ROS2 の場所から見つかります。ところが、rclpy が使うライブラリのうち、YAML の読み書きをする PyYAML、つまり import yaml で読み込むものは、apt でシステムの Python の側に入っていて、仮想環境の中からは見えません。3節の注意書きと同じ理由です。仮想環境の中にあるのは、自分で入れたものだけだからです。

まず、仮想環境を有効にしたターミナルで、rclpy を読み込めないことを確かめます。python -c で、import rclpy を実行します。

期待する結果、抜粋です。途中の行は省いてあります。Traceback、つまりエラーの経路の表示が出て、ROS2 のインストール先の rclpy の parameter.py の中の、import yaml の行で、yaml という名前のモジュールが無い、つまり ModuleNotFoundError で止まっています。

rclpy は見つかっていて、ROS2 のインストール先のファイルが読まれていますが、その中の import yaml で止まっています。足りないのは yaml だけなので、PyYAML を仮想環境に入れます。4節と同じく、この手順書を作った時点、2026年10月6日の最新版に固定します。

pip install で、pyyaml の6.0.3 を、イコール2つで版を固定して入れます。続けて、python -c で、rclpy を import し、nav_msgs の msg から Odometry を import して、rclpy: OK と表示させます。

期待する結果です。pip install は、途中の行のあと、Successfully installed の行を出します。python -c は、1行を表示します。

Successfully installed の pyyaml の6.0.3 の後、rclpy: OK と表示されれば、仮想環境の Python から、ROS2 のライブラリと、メッセージの型を使えます。ここでのメッセージの型は、オドメトリの、nav_msgs の msg の Odometry です。

generate-parameter-library-py は typeguard を必要とする、と出る場合の注意書きがあります。Gazebo の物理の間章の5節で、ros2_control のパッケージ、たとえば ros-jazzy-ros2-controllers などを入れていると、pip install pyyaml==6.0.3 の Successfully installed の直前に、ERROR の行が出ます。3節と同じ、依存関係の解決についての文の後に、generate-parameter-library-py の0.7.6 は typeguard を必要とするが、入っていない、という行が続きます。

これも、3節の注意書きの launch-ros と同じ理由で、導入の失敗ではなく、無視してかまいません。generate_parameter_library_py は、ros2_control のパッケージが依存して apt で入る、ROS2 の Python のパッケージで、コントローラのパラメータを扱うコードを、ビルドの時に作る道具です。PYTHONPATH を通して、仮想環境の pip にも見え、それが必要とする typeguard がシステムの側にしか無いため、無い、と報告されます。仮想環境の中では使わないので、typeguard を入れる必要はありません。rclpy: OK と表示されていれば、7節は済んでいます。

pip は、入れるパッケージと、それに依存する入れ済みのパッケージだけを点検するので、この行は、generate_parameter_library_py が使うもの、つまり jinja2、pyyaml、setuptools、typeguard を入れるときに出ます。3節の導入でも、PyTorch が jinja2 と setuptools を一緒に入れるので、同じパッケージについて、typeguard や pyyaml が無いという行が出ることがあります。版の数字の0.7.6 は、ROS2 の更新の状況で違うことがあります。

仮想環境と ROS2 のライブラリの組み合わせ方について、補足の囲みがあります。3つの点です。

1つ目は、一般的な方法です。ROS2 の公式の文書、Using Python Packages with ROS 2 は、特別なオプションを付けずに仮想環境を作り、要るパッケージを、仮想環境に pip で入れる形を示しています。注意として挙げているのは、ROS2 を作ったのと同じ Python、つまり Ubuntu 24.04 ではシステムの python3 で、仮想環境を作ることで、2節の作り方は、これを満たしています。

2つ目は、ほかの方法との違いです。仮想環境を作るときに、--system-site-packages を付けると、apt で入った Python のパッケージも、すべて見えるようになり、PyYAML を入れなくても rclpy を読めます。その代わり、仮想環境とシステムのパッケージが混ざり、どちらの版が読み込まれたのかが、分かりにくくなります。たとえば numpy は、仮想環境に入る版と、apt の版で、大きく違います。この教材では、仮想環境の中にあるのは自分で入れたものだけ、という形を保つため、足りないものを1つずつ入れます。

3つ目は、実務の目安です。仮想環境で使うパッケージを、pip freeze で書き出しておくと、別の PC やコンテナで、同じ環境を作り直せます。仮想環境の中で ROS2 の launch など、ほかのライブラリも使うようになったら、足りないと言われたものを、同じように足します。

## つまずきやすい点

表は2列で、9行あります。列は、症状と、確認することです。

1行目。python3 -m venv で、ensurepip is not available、つまり ensurepip が使えない、と出る場合です。1節の python3-venv を入れたかを確かめます。

2行目。pip install で、externally-managed-environment と出る場合です。仮想環境を有効にしたか、つまりプロンプトに、かっこ付きの rl_venv があるかを確かめます。新しいターミナルでは、有効にし直します。

3行目。導入に長い時間がかかり、nvidia で始まる名前のパッケージが、次々にダウンロードされる場合です。3節より先に SB3 を入れて、GPU 向けの PyTorch が選ばれています。Ctrl+C で止め、6節で消して作り直します。

4行目。pip install の最後に、launch-ros は pyyaml を必要とするが入っていない、という ERROR が出る場合です。Successfully installed の行が出ていれば、導入は成功しています。ROS2 を読み込んだターミナルで出ることがあり、無視してかまいません。3節の注意書きの話です。7節で PyYAML を入れた後は、出なくなります。

5行目。pip install の最後に、generate-parameter-library-py は typeguard を必要とするが入っていない、という ERROR が出る場合です。Successfully installed の行が出ていれば、導入は成功しています。Gazebo の物理の間章の5節で ros2_control のパッケージを入れていると出ることがあり、無視してかまいません。7節の末尾の注意書きの話です。7節で PyYAML を入れた後も、jinja2 や setuptools などを入れ直すときに出ることがあります。

6行目。import rclpy で、yaml という名前のモジュールが無い、と出る場合です。7節の PyYAML を、仮想環境を有効にしたターミナルで入れたかを確かめます。

7行目。import rclpy で、rclpy という名前のモジュールが無い、と出る場合です。ROS2 を読み込んだターミナルかを確かめます。ROS2 の setup.bash を source しますが、ホームの .bashrc で読み込んでいれば、要りません。

8行目。import gymnasium で、gymnasium という名前のモジュールが無い、と出る場合です。仮想環境を有効にしたか。which python が、ホームの rl_venv の bin の python を指しているかを確かめます。

9行目。ROS2 のノードが、ビルドし直した後に動かなくなった場合です。仮想環境を有効にしたまま、colcon build しなかったかを確かめます。5節の話です。deactivate してから、ワークスペースの build と install のフォルダを消して、ビルドし直します。

## 次へ

フェーズ7-0、強化学習の概要と最初の一歩、へ進みます。強化学習の用語を押さえ、Gymnasium の環境をでたらめに動かしてから、SB3 で振り子を学習させ、手書きの制御器と比べます。

## 公式のドキュメント

参考資料は7つで、どれも公式で英語です。

1つ目は、Stable-Baselines3 のドキュメントの Installation です。

2つ目は、Gymnasium のドキュメントの Basic Usage です。

3つ目は、PyTorch の Get Started です。

4つ目は、Python の公式の文書の、venv、仮想環境の作り方のページです。

5つ目は、ROS 2 の公式の文書の原稿、jazzy の、Using Python Packages with ROS 2 です。7節の補足で使いました。

6つ目は、PyPI の PyYAML のページです。7節で入れるパッケージで、ライセンスは MIT License です。

7つ目は、PyPI の、stable-baselines3、sb3-contrib、gymnasium のページです。

原文の最後には、出典の注記があります。4節の SB3 の2通りのコマンドは、Stable-Baselines3 の公式の文書、Installation からの抜粋です。4節の、gymnasium に classic-control の指定を付けて入れる案内は、Gymnasium の公式の文書、Basic Usage に基づきます。3節のコマンドは、PyTorch の公式の案内と同等の形です。説明の文章は、公式の文書を参考に、自分の言葉で書いたもの、とあります。

以上で、強化学習のライブラリの環境構築の話を終わります。

## 出典について

この原稿は、SanghunIm1991 さんの [ros2MinimalPhysicalAi の「環境構築 手順書: 強化学習のライブラリ（Stable-Baselines3）」](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/docs/setup_rl_sb3.md)を、聞くために要約・意訳したものです。元にしたのは、[2026年10月14日の版](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/132df7b64d48d560def7ec7149f7003938d3d8e5/docs/setup_rl_sb3.md)です。原文の文章と同じく、[クリエイティブ・コモンズ 表示 4.0 国際ライセンス](https://creativecommons.org/licenses/by/4.0/deed.ja)で提供します。

原稿の中に原文の表記のまま書いたコマンドは、原文では [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0) の対象です。ライセンスの全文は、原文のリポジトリの [LICENSE-APACHE-2.0](https://github.com/SanghunIm1991/ros2MinimalPhysicalAi/blob/main/LICENSE-APACHE-2.0) にあります。原文では、3節のコマンドは PyTorch の公式の案内と同等の形だとしています。

原文の4節の、SB3 の公式の導入の案内の2通りのコマンドは、[Stable-Baselines3](https://stable-baselines3.readthedocs.io/) の公式の文書（Antonin Raffin、MIT License）からの抜粋です。この原稿では、そのコマンドを写さず、何を入れる形かを言葉で説明しました。gymnasium に classic-control の指定を付けて入れる案内は、原文では [Gymnasium](https://gymnasium.farama.org/) の公式の文書（OpenAI、Farama Foundation、MIT License）に基づくとしています。表示の例は、各ツールの表示を言葉で説明したものです。
