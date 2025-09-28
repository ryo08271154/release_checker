# Release Checker

GitHubリポジトリの最新リリースを確認し、アップデートを支援するライブラリです。メインスクリプトから呼び出して使用します。

## 機能

- GitHubリリースの自動チェック
- GUI/CUIでのアップデート実行
- 更新情報の表示
- 差分ログの表示

## 必要要件

- Python 3.7以上
- Git（設定済みのリポジトリ）

## セットアップ

1. release_checkerを組み込みたいプロジェクトのサブモジュールとして追加

```bash
git submodule add https://github.com/ryo08271154/release_checker.git release_checker
```

2. 依存パッケージのインストール

```bash
pip install requests
```

## 使用方法

メインスクリプトでの呼び出し

```python
from release_checker import ReleaseChecker

checker = ReleaseChecker()

# GUIで更新確認
checker.gui()

# CUIで更新確認
checker.cui()
```

## 利用可能なメソッド

- `check_update()`: 更新の有無を確認（戻り値: bool）
- `update(exit=True)`: 更新を実行（exit=Trueの場合、完了時にプログラム終了）
- `gui()`: GUIウィンドウを表示
- `cui()`: 対話形式でアップデートを実行

## 注意事項

- Gitリポジトリ内から呼び出す必要があります
- リポジトリにタグが付いている必要があります
- アップデート実行時はインターネット接続が必要です
- アップデート完了後はアプリケーションの再起動が必要です
