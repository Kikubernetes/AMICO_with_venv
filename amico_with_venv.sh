#!/usr/bin/env bash
# This script is a wrapper for running AMICO with a Python virtual environment.
# You should haveactivated the virtual environment before running this script.
# これはAMICOをPythonの仮想環境で実行するためのラッパースクリプトです。
# このスクリプトを実行する前に、仮想環境をアクティブにしておいてください。

# The directory structure should be as follows:
# ディレクトリ構造は以下のようにする:

# sub01
#   ├── data.nii.gz
#   ├── nodif_brain_mask.nii.gz
#   ├── bvals
#   └── bvecs
# sub02
#   ├── data.nii.gz
#   ├── nodif_brain_mask.nii.gz
#   ├── bvals
#   └── bvecs
# 　・・・

# Example usage: amico_with_venv.sh path/to/noddi_dir(absolute path)

cd "$(dirname "$0")" || exit 1
script_dir=$(pwd)

noddi_dir="$1"
if [ -z "$noddi_dir" ]; then
    echo "Usage: $0 path/to/noddi_dir" >&2
    exit 1
fi

for dir in "$noddi_dir"/*/; do
    if [ -d "$dir" ]; then
        echo "Processing directory: $dir"
        # Run the AMICO script with the virtual environment's Python
        cd "$dir"
        "$script_dir/.venv/bin/python" "$script_dir/run_amico.py"
    else
        echo "Skipping non-directory: $dir"
    fi
done

