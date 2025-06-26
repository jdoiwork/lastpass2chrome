import pandas as pd
from jinja2 import Environment, FileSystemLoader
import numpy as np

# 入力ファイル
lastpass_file = 'lastpass_vault_export.csv'
chrome_file = 'Chrome パスワード.csv'
# 出力ファイル
lastpass_only_file = 'lastpass_only.csv'
lastpass_diff_file = 'lastpass_diff.csv'
lastpass_diff_md_file = 'lastpass_diff_compare.md'
stats_md_file = 'lastpass_chrome_stats.md'

# CSV読み込み
lp = pd.read_csv(lastpass_file)
ch = pd.read_csv(chrome_file)

# キー列を作成
lp['key'] = lp['url'].fillna('') + '|' + lp['username'].fillna('')
ch['key'] = ch['url'].fillna('') + '|' + ch['username'].fillna('')

# LastPassをChrome形式に変換
def lp_to_chrome(row):
    return pd.Series({
        'name': row.get('name', ''),
        'url': row.get('url', ''),
        'username': row.get('username', ''),
        'password': row.get('password', ''),
        'note': row.get('extra', '')
    })
lp_chrome = lp.apply(lp_to_chrome, axis=1)
lp_chrome['key'] = lp['key']

# Chromeのカラム名に揃える
def ch_to_chrome(row):
    return pd.Series({
        'name': row.get('name', ''),
        'url': row.get('url', ''),
        'username': row.get('username', ''),
        'password': row.get('password', ''),
        'note': row.get('note', '')
    })
ch_chrome = ch.apply(ch_to_chrome, axis=1)
ch_chrome['key'] = ch['key']

# 1. LastPassにしかないデータ
only_lp = lp_chrome.loc[~lp_chrome['key'].isin(ch_chrome['key'])]
only_lp.drop(columns=['key'], inplace=True)
only_lp.to_csv(lastpass_only_file, index=False)

# 2. 両方に存在し内容が異なるデータ
merged = pd.merge(lp_chrome, ch_chrome, on='key', suffixes=('_lp', '_ch'))
diff = merged[(merged['password_lp'] != merged['password_ch']) | (merged['note_lp'] != merged['note_ch'])]
# LastPass側のデータのみCSV出力
cols = ['name_lp', 'url_lp', 'username_lp', 'password_lp', 'note_lp']
diff_out = diff[cols].rename(columns={c: c[:-3] for c in cols})
diff_out.to_csv(lastpass_diff_file, index=False)

# Markdown形式で比較用ファイルをJinja2テンプレートで出力
def make_diff_md_jinja(diff_df, md_path, template_path):
    env = Environment(loader=FileSystemLoader('.'), trim_blocks=True, lstrip_blocks=True)
    template = env.get_template(template_path)
    # DataFrameをdictのリストに変換し、nanを空文字に変換
    items = diff_df.replace({np.nan: ''}).to_dict(orient='records')
    md = template.render(items=items)
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md)

make_diff_md_jinja(diff, lastpass_diff_md_file, 'diff_template.md.j2')

# 統計データ出力
def make_stats_md(lp_df, ch_df, md_path):
    lp_sites = set(zip(lp_df['url'], lp_df['username']))
    ch_sites = set(zip(ch_df['url'], ch_df['username']))
    lp_usernames = set(lp_df['username'])
    ch_usernames = set(ch_df['username'])
    lp_passwords = set(lp_df['password'])
    ch_passwords = set(ch_df['password'])
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write('# LastPass/Chrome パスワード統計\n\n')
        f.write(f'- LastPass 登録件数: {len(lp_df)}\n')
        f.write(f'- Chrome 登録件数: {len(ch_df)}\n')
        f.write(f'- LastPass サイト数: {len(lp_sites)}\n')
        f.write(f'- Chrome サイト数: {len(ch_sites)}\n')
        f.write(f'- LastPass ユーザー名種類: {len(lp_usernames)}\n')
        f.write(f'- Chrome ユーザー名種類: {len(ch_usernames)}\n')
        f.write(f'- LastPass パスワード種類: {len(lp_passwords)}\n')
        f.write(f'- Chrome パスワード種類: {len(ch_passwords)}\n')
        f.write('\n')
        f.write('## LastPassのみのサイト数\n')
        f.write(f'- {len(lp_sites - ch_sites)}\n')
        f.write('## Chromeのみのサイト数\n')
        f.write(f'- {len(ch_sites - lp_sites)}\n')
        f.write('## 両方に存在するサイト数\n')
        f.write(f'- {len(lp_sites & ch_sites)}\n')
make_stats_md(lp_chrome, ch_chrome, stats_md_file)

print(f'LastPassのみ: {lastpass_only_file}')
print(f'差分あり: {lastpass_diff_file}')
print(f'差分比較Markdown: {lastpass_diff_md_file}')
print(f'統計Markdown: {stats_md_file}')
