import csv

CHROME_FIELDS = ['name', 'url', 'username', 'password', 'note']
LASTPASS_FIELDS = ['url', 'username', 'password', 'totp', 'extra', 'name', 'grouping', 'fav']

def load_chrome_csv(path):
    """Chrome形式CSVを辞書で読み込む (key: (url, username))"""
    chrome_data = {}
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row.get('url', '').strip(), row.get('username', '').strip())
            chrome_data[key] = {
                'name': row.get('name', ''),
                'url': row.get('url', ''),
                'username': row.get('username', ''),
                'password': row.get('password', ''),
                'note': row.get('note', '')
            }
    return chrome_data

def load_lastpass_csv_as_chrome(path):
    """LastPass CSVをChrome形式のリストに変換（不要な列はドロップ）"""
    chrome_rows = []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            chrome_row = {
                'name': row.get('name', ''),
                'url': row.get('url', ''),
                'username': row.get('username', ''),
                'password': row.get('password', ''),
                'note': row.get('extra', '')
            }
            # Chromeのデータ構造に存在しない列は除外
            chrome_row = {k: chrome_row[k] for k in CHROME_FIELDS}
            chrome_rows.append(chrome_row)
    return chrome_rows

def compare_lastpass_chrome(lastpass_rows, chrome_data):
    """
    lastpass_rows: Chrome形式のリスト
    chrome_data: Chrome形式のdict (key: (url, username))
    return: (lastpass_only, lastpass_diff)
    """
    only = []
    diff = []
    for row in lastpass_rows:
        key = (row['url'].strip(), row['username'].strip())
        if key not in chrome_data:
            only.append(row)
        else:
            chrome_row_cmp = chrome_data[key]
            if row['password'] != chrome_row_cmp['password'] or row['note'] != chrome_row_cmp['note']:
                diff.append(row)
    return only, diff

def write_chrome_csv(path, rows):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=CHROME_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
