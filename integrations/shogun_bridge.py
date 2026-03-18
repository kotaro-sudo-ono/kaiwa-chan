# file: integrations/shogun_bridge.py
import subprocess
import time
from pathlib import Path

# 将軍tmuxペイン
_SHOGUN_PANE = "shogun:0.0"

# 完了を示すキーワード（将軍の返答に含まれる）
_DONE_MARKERS = ["完了", "done", "Done", "実装完了", "任務完了", "Worked for", "✓", "報告"]

# まだ作業中を示すキーワード
_BUSY_MARKERS = ["実行中", "Running", "Bash(", "Write(", "Edit(", "Read("]


class ShogunBridge:
    """
    kaiwa-chan (Windows) から multi-agent-shogun (WSL2) へのブリッジ。

    Administrator が「上様」として将軍に命令を下し、
    7体の足軽が並列実装したレポートを受け取る。

    DeveloperAgent の implement() と同じインターフェースを持つ。
    """

    def implement(self, task: str, review_notes: str = "", project_path: str = "") -> dict:
        """
        将軍に命令を送り、完了を待って結果を返す。

        Args:
            project_path: 作業対象プロジェクトのパス（例: ~/projects/sample_app/my-kyudo-app）

        Returns:
            {"summary": str, "skill_proposals": list}
        """
        order = self._build_order(task, review_notes, project_path)
        print("[ShogunBridge] 将軍へ命令を送信中...")
        self._send_to_shogun(order)
        dashboard = self._wait_for_completion()
        return self._parse_result(dashboard)

    # ------------------------------------------------------------------

    def _build_order(self, task: str, review_notes: str, project_path: str = "") -> str:
        if project_path:
            order = f"作業ディレクトリ: {project_path}\n以下のタスクを実装せよ:\n\n{task}"
        else:
            order = f"以下のタスクをこのリポジトリで実装せよ:\n\n{task}"
        if review_notes:
            order += f"\n\n## 設計上の考慮事項\n{review_notes}"
        order += (
            "\n\n実装完了後、以下の形式で報告せよ:"
            "\n1. 変更したファイルと内容の概要"
            "\n2. 動作確認方法"
            "\n3. スキル提案があれば「SKILL_PROPOSAL: <名前> - <説明>」の形式で追記"
        )
        return order

    def _ensure_shogun_running(self) -> None:
        """shogun tmuxセッションが起動していなければ起動する。"""
        result = subprocess.run(
            ["wsl", "tmux", "has-session", "-t", "shogun"],
            capture_output=True,
        )
        if result.returncode == 0:
            return

        print("[ShogunBridge] shogunセッション未起動 → 起動します...")
        subprocess.Popen(
            ["wsl", "bash", "-l", "-c",
             "cd ~/projects/multi-agent-shogun && ./shutsujin_departure.sh"],
        )
        # 起動完了を待つ（セッションが現れるまで最大30秒）
        for _ in range(30):
            time.sleep(1)
            check = subprocess.run(
                ["wsl", "tmux", "has-session", "-t", "shogun"],
                capture_output=True,
            )
            if check.returncode == 0:
                print("[ShogunBridge] shogunセッション起動完了")
                time.sleep(5)  # Claude Code の初期化待ち
                return
        raise RuntimeError("[ShogunBridge] shogunセッションの起動がタイムアウトしました")

    def _send_to_shogun(self, order: str) -> None:
        """tmux send-keys で将軍のpaneに直接命令を送る。"""
        self._ensure_shogun_running()
        # 改行をスペースに変換（tmux send-keysはEnterまでを1メッセージとして扱うため）
        single_line = order.replace("\n", " ")
        result = subprocess.run(
            ["wsl", "tmux", "send-keys", "-t", "shogun:0.0", single_line, "Enter"],
            capture_output=True,
            text=True,
            timeout=30,
            encoding="utf-8",
        )
        if result.returncode != 0:
            raise RuntimeError(f"[ShogunBridge] tmux send-keys失敗: {result.stderr}")
        print("[ShogunBridge] 将軍のpaneに命令を送信しました")

    def _wait_for_completion(self, poll_interval: int = 15, timeout: int = 600) -> str:
        """将軍のtmuxペインを監視し、アイドル状態（完了）を検出する。"""
        print(f"[ShogunBridge] 将軍の作業を監視中（最大{timeout//60}分）...")

        # 送信直後は作業開始を待つ
        time.sleep(10)

        elapsed = 10
        last_pane = ""
        idle_count = 0  # アイドル状態が連続した回数

        while elapsed < timeout:
            time.sleep(poll_interval)
            elapsed += poll_interval

            pane = self._capture_shogun_pane()
            if pane != last_pane:
                last_pane = pane
                idle_count = 0
                print(f"[ShogunBridge] 将軍のpane更新検知（{elapsed}秒経過）")
            else:
                idle_count += 1

            # paneが3回連続で変化なし（約45秒）→ 完了とみなす
            if idle_count >= 3:
                print("[ShogunBridge] 将軍のpane変化なし → 作業完了と判断")
                return self._capture_shogun_pane(scrollback=200)

        print("[ShogunBridge] タイムアウト。現在のpane内容を返します")
        return self._capture_shogun_pane(scrollback=200) or "（将軍のpane取得失敗）"

    def _capture_shogun_pane(self, scrollback: int = 0) -> str:
        """tmux capture-pane で将軍のpane内容を取得する。"""
        cmd = ["wsl", "tmux", "capture-pane", "-t", _SHOGUN_PANE, "-p"]
        if scrollback:
            cmd += ["-S", f"-{scrollback}"]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10,
            encoding="utf-8",
        )
        return result.stdout or ""

    def _is_idle(self, pane_content: str) -> bool:
        """アイドルプロンプト（❯）が表示されていて作業中でなければTrue。"""
        if not pane_content:
            return False
        has_prompt = "❯" in pane_content
        is_busy = any(m in pane_content for m in _BUSY_MARKERS)
        return has_prompt and not is_busy

    def _parse_result(self, pane_content: str) -> dict:
        """pane内容からskill_proposalsを抽出し、summaryと分離する。"""
        skill_proposals = []
        summary_lines = []

        for line in pane_content.splitlines():
            if line.startswith("SKILL_PROPOSAL:"):
                skill_proposals.append(line.replace("SKILL_PROPOSAL:", "").strip())
            else:
                summary_lines.append(line)

        return {
            "summary": "\n".join(summary_lines).strip(),
            "skill_proposals": skill_proposals,
        }
