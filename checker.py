import tkinter as tk
from tkinter import ttk, messagebox
import requests
import subprocess
import webbrowser
import urllib.parse
import sys


class Application(tk.Frame):
    def __init__(self, master=None, checker=None):
        super().__init__(master)
        self.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.checker = checker
        # 現在のバージョン情報
        self.current_version = checker.current_version
        self.latest_version = checker.latest_version
        self.create_widgets()

    def create_widgets(self):
        # タイトル
        title_label = tk.Label(self, text="アップデート確認",
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))

        # 現在のバージョン情報
        version_frame = tk.LabelFrame(self, text="バージョン情報",
                                      padx=10, pady=10)
        version_frame.pack(fill=tk.X, pady=(0, 15))

        self.current_label = tk.Label(version_frame, text=f"現在のバージョン: {self.current_version}",
                                      anchor="w")
        self.current_label.pack(fill=tk.X)

        self.latest_label = tk.Label(version_frame, text=f"最新バージョン: {self.latest_version}",
                                     anchor="w")
        self.latest_label.pack(fill=tk.X)

        # ステータス表示
        status_frame = tk.LabelFrame(self, text="ステータス",
                                     padx=10, pady=10)
        status_frame.pack(fill=tk.X, pady=(0, 15))

        self.status_label = tk.Label(status_frame, text="アップデートを確認してください",
                                     anchor="w")
        self.status_label.pack(fill=tk.X)

        # アップデート情報表示エリア
        info_frame = tk.LabelFrame(self, text="更新情報",
                                   padx=10, pady=10)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # テキストエリア（スクロールバー付き）
        text_frame = tk.Frame(info_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        self.info_text = tk.Text(text_frame, height=8, wrap=tk.WORD, state=tk.DISABLED,
                                 relief="sunken", bd=1)
        scrollbar = tk.Scrollbar(
            text_frame, orient=tk.VERTICAL, command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=scrollbar.set)

        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # ボタンフレーム
        button_frame = tk.Frame(self)
        button_frame.pack(fill=tk.X)

        self.check_button = tk.Button(button_frame, text="アップデートを確認",
                                      relief="raised", padx=10, pady=5, command=self.check_update)
        self.check_button.pack(side=tk.LEFT, padx=(0, 10))

        self.change_log_button = tk.Button(button_frame, text="詳細",
                                           state=tk.DISABLED, relief="raised", padx=10, pady=5)
        self.change_log_button.pack(side=tk.LEFT, padx=(0, 10))

        self.close_button = tk.Button(button_frame, text="閉じる",
                                      command=self.quit, relief="raised", padx=10, pady=5)
        self.close_button.pack(side=tk.RIGHT)

        # 初期メッセージ
        self.update_info_text(self.checker.latest_info_json.get(
            "body", "アップデートを確認するには「アップデートを確認」ボタンをクリックしてください。"))
        if self.current_version is not None and self.latest_version is not None:
            self.check_update(False)

    def update_info_text(self, text):
        """情報表示エリアのテキストを更新"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, text)
        self.info_text.config(state=tk.DISABLED)

    def open_change_log(self):
        webbrowser.open(
            f"https://github.com/{self.checker.owner}/{self.checker.repo}/compare/{self.checker.current_version}...{self.checker.latest_version}")

    def start_update(self):
        self.status_label.config(text="アップデートを実行しています...")
        try:
            self.checker.update(False)
        except Exception as e:
            self.status_label.config(text=f"アップデート中にエラーが発生しました: {e}",
                                     fg="red")
        else:
            self.status_label.config(text="アップデートが完了しました。")
            messagebox.showinfo("アップデート完了", "アップデートが完了しました。")
            self.quit()
            sys.exit(0)

    def check_update(self, check=True):
        self.update_info_text("アップデートを確認しています...")
        try:
            if self.checker.check_update(check):
                self.status_label.config(text="新しいバージョンがあります！", fg="blue")
                self.check_button.config(text="アップデートを実行",
                                         command=self.start_update)
                self.change_log_button.config(state=tk.NORMAL,
                                              command=self.open_change_log)
                self.update_info_text(
                    f"新しいバージョン {self.latest_version} が利用可能です。")
            else:
                self.status_label.config(text="最新バージョンです。", fg="green")
            self.current_version = self.checker.current_version
            self.latest_version = self.checker.latest_version
            info = self.checker.latest_info_json
            self.update_info_text(info["body"])
        except:
            self.status_label.config(text="エラーが発生しました。", fg="red")
            self.update_info_text("エラーが発生しました。")
        self.current_label.config(text=f"現在のバージョン: {self.current_version}")
        self.latest_label.config(text=f"最新バージョン: {self.latest_version}")


class ReleaseChecker:
    def __init__(self):
        self.owner = None
        self.repo = None
        self.latest_version = None
        self.current_version = self.get_current_version()
        self.latest_info_json = {}

    def get_latest_version_info(self, owner, repo):
        url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(
                f"Failed to get release info: {response.status_code}")
        data = response.json()
        self.latest_version = data["tag_name"]
        self.latest_info_json = data
        return data

    def get_latest_version(self, owner, repo):
        info = self.get_latest_version_info(owner, repo)
        return self.latest_version

    def get_current_version(self):
        try:
            tag = subprocess.check_output(
                ["git", "describe", "--tags", "--abbrev=0"],
                stderr=subprocess.STDOUT
            ).decode("utf-8").strip()
            self.current_version = tag
            return tag
        except subprocess.CalledProcessError:
            return None

    def get_repo_info(self):
        try:
            git_url = urllib.parse.urlparse(subprocess.check_output(
                ["git", "remote", "get-url", "origin"],
                stderr=subprocess.STDOUT
            ).decode("utf-8"))
        except subprocess.CalledProcessError:
            return {"owner": None, "repo": None}
        self.owner = git_url.path.split("/")[1]
        self.repo = git_url.path.split("/")[2].replace(".git", "")
        return {"owner": self.owner, "repo": self.repo}

    def check_update(self, check=True):
        if check:
            repo_info = self.get_repo_info()
            owner = repo_info["owner"]
            repo = repo_info["repo"]
            if not owner or not repo:
                raise Exception("Failed to get repository info")
            self.current_version = self.get_current_version()
            self.latest_version = self.get_latest_version(owner, repo)
        if self.current_version != self.latest_version:
            return True
        else:
            return False

    def update(self, exit=True):
        commands = [
            ["git", "checkout", "main"],
            ["git", "pull"],
            ["pip", "install", "-r", "requirements.txt"]
        ]
        for command in commands:
            try:
                result = subprocess.check_output(
                    command, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                raise Exception(
                    f"Command {' '.join(command)} failed with return code {e.returncode} \n{e.output.decode('utf-8')}")
        print("Update completed. Please restart the application.")
        if exit:
            sys.exit(0)

    def gui(self):
        root = tk.Tk()
        app = Application(master=root, checker=self)
        root.title("アップデート")
        root.resizable(False, False)
        app.mainloop()

    def cui(self):
        try:
            if self.check_update():
                print(
                    f"現在のバージョン: {self.current_version} \n 新しいバージョン {self.latest_version} が利用可能です。")
                print("更新情報:\n" + self.latest_info_json["body"] + "\n")
                choice = input("アップデートを実行しますか？ (y/n): ").strip().lower()
                if choice == 'y':
                    self.update()
                else:
                    print("アップデートをキャンセルしました。")
            else:
                print("最新バージョンです。")
        except Exception as e:
            print(f"エラーが発生しました: {e}")
