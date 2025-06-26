from lp_chrome_utils import load_lastpass_csv_as_chrome, write_chrome_csv

# 入力ファイルと出力ファイルのパス
input_file = 'lastpass_vault_export.csv'
output_file = 'lastpass_to_chrome.csv'

# LastPassデータをChrome形式に変換
chrome_rows = load_lastpass_csv_as_chrome(input_file)
write_chrome_csv(output_file, chrome_rows)

print(f'変換が完了しました: {output_file}')
