# LastPass移行計画

## 概要

このプロジェクトは、LastPass からエクスポートしたパスワードデータを Google Chrome 形式に変換し、差分比較や統計レポートを生成する Python ツール群です。

## ディレクトリ構成

```
input/    ... 入力用CSVファイル格納ディレクトリ
output/   ... 出力ファイル格納ディレクトリ
lastpass_to_chrome.py         ... LastPass CSVをChrome形式に変換
lastpass_chrome_diff.py       ... LastPassとChromeのパスワード差分を比較
lp_chrome_utils.py            ... 各種ユーティリティ
diff_template.md.j2           ... 差分レポート用テンプレート
stats_template.md.j2          ... 統計レポート用テンプレート
データ構造.md                 ... データ構造の説明
```

## 使い方

1. 必要なCSVファイルを `input/` フォルダに配置します。
   - 例: `lastpass_vault_export.csv`, `Chrome パスワード.csv`
2. Pythonスクリプトを実行して変換・比較・レポート生成を行います。

### 例

```sh
# LastPass → Chrome形式への変換
python lastpass_to_chrome.py

# 差分比較・レポート生成
python lastpass_chrome_diff.py
```

出力ファイルは `output/` フォルダに生成されます。

## 必要な環境

- Python 3.x

## セットアップ手順

1. 仮想環境（venv）の作成・有効化（推奨）

```sh
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate  # Windows の場合
```

2. 必要なパッケージのインストール

```sh
pip install -r requirements.txt
```

## 注意事項

- `.csv` や `.md` ファイルは `.gitignore` で除外されています。
- 詳細なデータ構造やテンプレート仕様は `データ構造.md` を参照してください。
