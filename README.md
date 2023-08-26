# stock-aggregator
auカブコム証券のKabuステーションAPIを利用して受信したティック情報を集計します。

## 設定
### プロパティファイル
以下項目を記載したconfig.iniをディレクトリ直下に置く。

| Section | Key | Type | Value（Description） |
| --- | --- | --- | --- |
| DEFAULT | tickdata_directory | str | ティック情報を出力するディレクトリパスです。 |
| DEFAULT | target_filename | str | 通知対象銘柄リストのCSVファイル名です。 |

``` ini
[Section]
Key = Value
.
.
.
```
## 起動
``` shell
python -m stock-aggregator --day <YYYYMMDD> --close <10-15>
```
### オプション
| オプション名 | デフォルト | 内容 |
| --- | --- | --- |
| --day | None | 集計対象の日付を「YYYYMMDD」形式で指定する。全データを対象とする場合は指定しない。 |
| --close | 15 | 集計の終了時間を指定する。 |
