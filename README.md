# stock-aggregator
auカブコム証券のKabuステーションAPIを利用して受信したティック情報を集計する。

## 設定
### プロパティファイル
以下項目を記載したconfig.iniをディレクトリ直下に置く。

| Section | Key | Type | Value（Description） |
| --- | --- | --- | --- |
| DEFAULT | tickdata_directory | str | ティック情報を出力するディレクトリパスを設定する。 |
| DEFAULT | target_filename | str | 集計対象銘柄リストのCSVファイル名を設定する。 |
| DEFAULT | output_csvname | str | CSV出力する場合の出力先ファイル名を設定する。 |

``` ini
[Section]
Key = Value
.
.
.
```
## 起動
``` shell
python -m stock-aggregator --mode console --day <YYYYMM[DD]> --close <10-15>
```
### オプション
| オプション名 | デフォルト | 内容 |
| --- | --- | --- |
| --mode | console | 起動モードを指定する。<br> - console: コンソール出力する。 <br> - csv: CSV出力する。出力先の設定が必要となる。 |
| --day | None | 集計対象の日付を「YYYYMMDD」形式、または年月を「YYYYMM」形式で指定する。<br>全データを対象とする場合は指定しない。 |
| --close | 15 | 集計の終了時間を指定する。 |
| --buy | 1 | 集計の開始価格の買大約定数を指定する。 |
| --sell | 1 | 集計の終了価格の売大約定数を指定する。 |
