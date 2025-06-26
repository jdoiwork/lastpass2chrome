import pandas as pd
from jinja2 import Environment, FileSystemLoader
import numpy as np
from pathlib import Path

# 柔軟なディレクトリ指定
INPUT_DIR = Path('input')
OUTPUT_DIR = Path('output')
INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# 入力ファイル
lastpass_file = INPUT_DIR / 'lastpass_vault_export.csv'
chrome_file = INPUT_DIR / 'Chrome パスワード.csv'
# 出力ファイル
lastpass_only_file = OUTPUT_DIR / 'lastpass_only.csv'
lastpass_diff_file = OUTPUT_DIR / 'lastpass_diff.csv'
lastpass_diff_md_file = OUTPUT_DIR / 'lastpass_diff_compare.md'
stats_md_file = OUTPUT_DIR / 'lastpass_chrome_stats.md'

def main():
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

    # ノートが空でないものだけを抽出して別ファイルに出力
    only_lp_note = only_lp[only_lp['note'].replace({np.nan: ''}).astype(str).str.strip() != '']
    lastpass_only_note_file = OUTPUT_DIR / 'lastpass_only_note.csv'
    only_lp_note.to_csv(lastpass_only_note_file, index=False)

    # 2. 両方に存在し内容が異なるデータ（urlとusernameが主キー、passwordかnoteが異なる場合のみ）
    merged = pd.merge(lp_chrome, ch_chrome, on=['url', 'username'], suffixes=('_lp', '_ch'))
    diff = merged[(merged['password_lp'] != merged['password_ch']) | (merged['note_lp'] != merged['note_ch'])]
    # LastPass側のデータのみCSV出力
    cols = ['name_lp', 'url', 'username', 'password_lp', 'note_lp']
    diff_out = diff[cols].rename(columns={
        'name_lp': 'name',
        'password_lp': 'password',
        'note_lp': 'note'
    })
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

    # 統計データ出力（Jinja2テンプレート版）
    def make_stats_md_jinja(lp_df, ch_df, md_path, template_path):
        env = Environment(loader=FileSystemLoader('.'), trim_blocks=True, lstrip_blocks=True)
        template = env.get_template(template_path)
        lp_sites = set(zip(lp_df['url'], lp_df['username']))
        ch_sites = set(zip(ch_df['url'], ch_df['username']))
        stats = {
            'lastpass_count': len(lp_df),
            'chrome_count': len(ch_df),
            'lastpass_sites': len(lp_sites),
            'chrome_sites': len(ch_sites),
            'lastpass_usernames': len(set(lp_df['username'])),
            'chrome_usernames': len(set(ch_df['username'])),
            'lastpass_passwords': len(set(lp_df['password'])),
            'chrome_passwords': len(set(ch_df['password'])),
            'lastpass_only_sites': len(lp_sites - ch_sites),
            'chrome_only_sites': len(ch_sites - lp_sites),
            'both_sites': len(lp_sites & ch_sites),
            # ノートが空でないものの数
            'lastpass_note_count': lp_df['note'].replace({np.nan: ''}).astype(str).str.strip().replace('', np.nan).dropna().shape[0],
            'chrome_note_count': ch_df['note'].replace({np.nan: ''}).astype(str).str.strip().replace('', np.nan).dropna().shape[0],
        }
        md = template.render(stats=stats)
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md)

    make_stats_md_jinja(lp_chrome, ch_chrome, stats_md_file, 'stats_template.md.j2')

    print(f'LastPassのみ: {lastpass_only_file}')
    print(f'差分あり: {lastpass_diff_file}')
    print(f'差分比較Markdown: {lastpass_diff_md_file}')
    print(f'統計Markdown: {stats_md_file}')

if __name__ == '__main__':
    main()
