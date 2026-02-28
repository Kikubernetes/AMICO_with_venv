
日本語 | [English](README.md)

> 本ドキュメントは AMICO 公式 README.md の日本語要約と実装例である  
> 基準コミット: 7183ee098f400d08e68be097c170ec078e969295  
> 最新情報・詳細な使用方法は公式 Wiki を参照

# AMICO — Convex Optimization を用いた高速拡散MRIマイクロ構造推定

AMICO（Accelerated Microstructure Imaging via Convex Optimization）は、
Daducci et al. (2015) で提案された **線形化＋凸最適化フレームワーク** に基づき、
NODDI などの拡散MRIマイクロ構造モデルを**高速かつ安定的に推定**するための実装  

---

## 主な特徴

- 辞書ベースの線形化による高速フィッティング
- 大規模 multi-shell データへの高いスケーラビリティ
- NODDI を含む複数モデルに対応
- Python API によるスクリプト運用・バッチ処理対応

---

## ドキュメント

インストール方法、チュートリアル、モデル設定方法は
公式 Wiki にまとめられている

👉 https://github.com/daducci/AMICO/wiki

---

## 実装例

まずは一度公式のチュートリアルどおりExample datasetでの実行がおすすめ  
自分のデータで実行する場合の例を以下に記載

以下は最もシンプルな実行方法

### 0. このリポジトリをクローン

```bash
git clone https://github.com/Kikubernetes/AMICO_with_venv.git
```

### 1. venv作成（推奨）

#### venv環境作成

自分が環境を作成したいところに移動（データのある場所、もしくは専用フォルダを作成する等）

```bash
 python3 -m venv amico
 source amico/bin/activate
 python3 -m pip install --upgrade pip
 pip install dmri-amico
```

### 2. データを用意

noddi_dirを準備する。  
ディレクトリ構造は以下のようにする。

```bash
sub01
  ├── data.nii.gz
  ├── nodif_brain_mask.nii.gz
  ├── bvals
  └── bvecs
sub02
  ├── data.nii.gz
  ├── nodif_brain_mask.nii.gz
  ├── bvals
  └── bvecs
　・・・
```

これらのファイルをHCPpipelines Diffusion Preprocessing Pipelineから取得する場合は、Diffusionディレクトリ下（Diffusion空間）、もしくはT1w/Diffusion下（T1w空間）にある。  
* nodif_brain_maskはb0画像から作成したバイナリマスク
* 持っていない場合は以下のようなコマンドで作成できる  

注意：data.nii.gzの1ボリューム目がb0と仮定、要FSL
```bash
fslroi data.nii.gz b0.nii.gz 0 1
bet b0.nii.gz nodif_brain -f 0.3 -R -m
```

[Synthstrip](https://surfer.nmr.mgh.harvard.edu/docs/synthstrip/) が使用可能ならそちらもおすすめ
```bash
mri_synthstrip -i nodif.nii.gz -o nodif_brain.nii.gz -m nodif_brain_mask.nii.gz --no-csf
```

### 3. （オプション）必要に応じてb値を丸める

b値のゆれ(1000の設定に対し995、1005など)が許容されないことがある  
b0が認識されないとエラーになるので、b値を丸める必要がある


```bash
    0, 5, 10 etc.　⇨ 0  
    995, 990, 1005 etc. ⇨ 1000
```

マニュアルでも作成可能だが、ここではround_bvals.pyを使用  
使い方は以下の通り

```bash
# 元のファイルは bvals.orig, 丸めたあとのファイル名は bvalsとする
# b値が0,1500,3000で設計されており、50以下の違いを丸める場合の例を示す

mv bvals bvals.orig
cp path/to/AMICO_with_venv/round_bvals.py . # 実際のパスに置き換える
python3 round_bvals.py bvals.orig bvals --shells 0,1500,3000 --b0_thr 50
```
### 4. run_amico.pyを実行

1例に対して実行する場合は以下の通り

- 被験者ディレクトリに移動
```bash
cd path/to/sub01 # 実際のパスに置き換える
```

- スクリプトをコピー
```bash
cp path/to/AMICO_with_venv/run_amico.py . # 実際のパスに置き換える
```
- 必要に応じて仮想環境をアクティベート
```bash
source amico/bin/activate # 実際のパスに置き換える
```

- 実行
```bash
python run_amico.py
```
出力先は `sub01/AMICO/NODDI` になる


### 5. (オプション)　複数例に実行する場合

複数例に対して連続してAMICO-noddiを実行したい場合、バッチスクリプトを用意してある  
被験者ID名のサブディレクトリにファイルを用意する（上記2.参照）  
ここではディレクトリ名をnoddi_dirとする  

スクリプトにはパスを通す必要がある(以下は一例)
```bash
mkdir -p ~/bin
cp path/to/AMICO_with_venv/run_amico.py ~/bin
cp path/to/AMICO_with_venv/amico_with_venv.sh ~/bin
echo "# set PATH so it includes user's private bin if it exists" >> ~/.bash_aliases
echo "if [ -d "$HOME/bin" ] ; then" >> ~/.bash_aliases
echo 'PATH="$HOME/bin:$PATH"' >> ~/.bash_aliases
echo "fi" >> ~/.bash_aliases
```
ターミナルを再起動し、実行
```bash
source path/to/venvs/amico/bin/activate # 実際のパスに置き換える
amico_with_venv.sh path/to/noddi_dir
```

出力先は `sub../AMICO/NODDI` になる

---

### トラブルシューティング

前処理にすごく時間がかかったり、うまくいかない場合は以下のどちらかを試す
1. 前処理をオフにする
2. preproc.pyを入れ替える（やや難易度高）

#### 1の場合  
run_amico.pyの17-18行目をコメントアウトする
```bash
#ae.set_config('doDebiasSignal', True)
#ae.set_config('DWI-SNR', 30.0)
```
#### 2の場合  
使用しているパッケージの場所を確認する
```
python -c "import amico, inspect; print(amico.__file__)"
```
ここで出てくる`.../site-packages/...`内にpreproc.pyがあるので、
```
mv preproc.py preproc.py.orig
```
として保存しておく。その上でこのレポジトリ内にあるpreproc.pyを同じ場所におく  
（0での除算を防ぐために下限値を設けてある）


---

## 参考文献

Daducci et al., 2015  
Accelerated Microstructure Imaging via Convex Optimization  
NeuroImage  
DOI: https://doi.org/10.1016/j.neuroimage.2014.10.026
