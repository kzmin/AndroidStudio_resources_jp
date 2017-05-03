AndroidStudio_resources_jp
=================
## 概要
Android Studio の日本語化リソースです。
一部のみ翻訳済みです。

AndroidStudioのlibディレクトリにコピーしてください。

    Windows: C:\Program Files\Android\Android Studio\lib

    Mac: AndroidStudio.app/Contents/lib/

    Linux: /opt/android-studio/lib/



以下の環境で動作確認済み

    OS: Mac OS Sierra ver10.12.4

    AndroidStudio version: ver2.3.1

----

## 翻訳作業用DB
大量にある.propertiesファイルの翻訳を行うために、
内容をsqlite3に落とし込んでいます。(manage/properties_ja.sqlite3)

#### スキーマ
    #.propertiesファイル
    CREATE TABLE properties_files (
    id INTEGER NOT NULL, 
    name VARCHAR(256), #ファイル名
    PRIMARY KEY (id)
    );

    #プロパティ(key-value形式)
    CREATE TABLE properties (
    id INTEGER NOT NULL, 
    name VARCHAR(256), #プロパティ名
    "fileId" INTEGER, #ファイルID(properties_files.id)
    line INTEGER, #定義行番号
    value VARCHAR(1000), #プロパティ値
    "hasArgs" BOOLEAN, #引数を取るプロパティか
    "isMultiline" BOOLEAN, #複数行に渡っているか
    "isTranslated" BOOLEAN, #翻訳済みか
    PRIMARY KEY (id), 
    CONSTRAINT "unique_idx_name_fileId" UNIQUE (name, "fileId"), 
    FOREIGN KEY("fileId") REFERENCES properties_files (id), 
    CHECK ("hasArgs" IN (0, 1)), 
    CHECK ("isMultiline" IN (0, 1)), 
    CHECK ("isTranslated" IN (0, 1))
    );

    #コメント
    CREATE TABLE comments (
    id INTEGER NOT NULL, 
    content VARCHAR(256), #コメント内容
    "fileId" INTEGER, #ファイルID(properties_files.id)
    line INTEGER, #定義行番号
    PRIMARY KEY (id), 
    FOREIGN KEY("fileId") REFERENCES properties_files (id)
    );

#### 変換

manage/properties2sqlite.pyを使用して、
.propertiesファイル群とデータベースを互いに変換することができます。

1. properties -> sqlite3

        python properties2sqlite.py properties_ja.sqlite3 <outputdir>

2. sqlite3 -> properties

        python --reverse properties2sqlite.py properties_ja.sqlite3 <outputdir>

**※ DebuggerBundle_ja.propertiesの"action.maximizeContent.text"は、なぜかkey-value形式でないため、DBに取り込んでいません。マージする際はご注意を。**

----
## その他

AndroidStudioのだいたいの操作の把握のために翻訳しただけなので、完全版は目指しておりません。悪しからず。
