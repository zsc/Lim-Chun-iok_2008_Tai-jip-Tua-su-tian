# 台羅轉換工具

將漢字或白話字（POJ）轉換為台灣閩南語羅馬字拼音（Tâi-lô/台羅）的命令列工具。

## 功能

- **漢字轉台羅**：使用詞典將漢字轉換為台羅拼音
- **白話字（POJ）轉台羅**：將傳統的白話字拼音轉換為教育部台羅拼音
- **自動檢測**：自動識別輸入內容為漢字或白話字並進行轉換
- **詞典查詢**：查詢漢字詞條的台羅讀音

## 安裝

```bash
# 克隆專案
git clone https://github.com/zsc/Lim-Chun-iok_2008_Tai-jip-Tua-su-tian.git
cd Lim-Chun-iok_2008_Tai-jip-Tua-su-tian

# 安裝相依套件（選用，用於簡體轉繁體）
pip install opencc-python-reimplemented
```

## 用法

### 基本用法

```bash
# 直接輸入文字轉換
python -m tailo 漢字

# 使用標準輸入
echo "漢字" | python -m tailo

# 轉換白話字
echo "chit8-si3" | python -m tailo
```

### 轉換模式

```bash
# 自動模式（預設）- 自動檢測輸入類型
python -m tailo --mode auto 漢字

# 漢字模式 - 強制將輸入視為漢字
python -m tailo --mode hanzi 漢字

# 白話字模式 - 強制將輸入視為白話字
python -m tailo --mode poj chit8-si3
```

### 詞典查詢

```bash
# 查詢單一漢字的台羅讀音
python -m tailo lookup 一

# 查詢詞組
python -m tailo lookup 台灣
```

### 選項說明

| 選項 | 說明 |
|------|------|
| `--dict PATH` | 指定詞典檔案路徑（預設：`./dict.csv`） |
| `--mode {auto,hanzi,poj}` | 轉換模式（預設：`auto`） |
| `--ambiguous {first,all}` | 多音字處理方式：`first` 顯示第一個，`all` 顯示所有可能 |
| `--unknown {keep,mark}` | 未知漢字處理：`keep` 保留原字，`mark` 標記為 `<?>` |
| `--no-opencc` | 停用簡體轉繁體功能 |
| `--no-orthography` | 僅轉換聲調數字，不進行 POJ→台羅 正字法轉換 |

## 範例

```bash
# 漢字轉台羅
$ python -m tailo "台灣"
tâi-uân

# 白話字轉台羅
$ python -m tailo --mode poj "chit8-si3"
tsi̍t-sì

# 顯示多音字所有讀音
$ python -m tailo --ambiguous all "一"
{tsi̍t/it}

# 使用管道
$ cat input.txt | python -m tailo > output.txt
```

## 詞典格式

預設使用林俊育編輯的《台日大辭典》CSV 格式詞典，詞條需為繁體中文。

## 專案結構

```
├── tailo/
│   ├── __init__.py       # 套件初始化
│   ├── __main__.py       # 命令列介面
│   ├── converter.py      # 漢字轉換邏輯
│   ├── romanize.py       # POJ 轉台羅拼音規則
│   ├── dict_loader.py    # 詞典載入器
│   └── opencc_util.py    # 簡繁轉換工具
└── README.md
```

## 資料來源

本工具使用的詞典來自：[林俊育 2008 台日大辭典](https://github.com/g0v/moedict-data-twblg/)

## 授權

請參考原始詞典資料的授權條款。
