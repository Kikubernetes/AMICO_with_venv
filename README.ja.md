
日本語 | [English](README.md)

> 本ドキュメントは AMICO 公式 README.md の日本語要約と実装例である。  
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
公式 Wiki にまとめられている。

👉 https://github.com/daducci/AMICO/wiki

---

## 実装例

まずは一度公式のチュートリアルどおりExample datasetでの実行がおすすめ。  
自分のデータで実行する場合の例を以下に記載。

### 0. このリポジトリをクローン

```bash
git clone https://github.com/Kikubernetes/AMICO_with_venv.git
```

### 1. venv作成（推奨）

クローンしたリポジトリに移動

```bash
cd AMICO_with_venv
```

venv環境作成

```bash
 python3 -m venv .venv
 source .venv/bin/activate
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

### 3. （オプション）必要に応じてb値を丸める

b値のゆれ(1000の設定に対し995、1005など)が許容されないことがある。  
b0が認識されないとエラーになるので、b値を丸める必要がある。


```bash
    0, 5, 10 etc.　⇨ 0  
    995, 990, 1005 etc. ⇨ 1000
```

マニュアルでも作成可能だが、ここではround_bvals.pyを使用。  
使い方は以下の通り。

```bash
# 元のファイルは bvals.orig, 丸めたあとのファイル名は bvalsとする
# b値が0,1500,3000で設計されており、50以下の違いを丸める場合の例を示す

mv bvals bvals.orig
python3 round_bvals.py bvals.orig bvals --shells 0,1500,3000 --b0_thr 50
```

### 4. amico_with_venvを実行

複数の被験者に対して連続してAMICO-noddiを実行する場合、
被験者ID名のサブディレクトリにファイルを用意する（上記2.参照）。  
ここではディレクトリ名をnoddi_dirとする.


```bash
./amico_with_venv.sh path/to/noddi_dir
```

出力先は `sub01/AMICO/NODDI` になる.


---

## 参考文献

Daducci et al., 2015  
Accelerated Microstructure Imaging via Convex Optimization  
NeuroImage  
DOI: https://doi.org/10.1016/j.neuroimage.2014.10.026
