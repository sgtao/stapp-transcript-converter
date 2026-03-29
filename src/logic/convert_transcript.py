# convert_transcript.py
import re
from typing import List


def convert_transcript(text: str) -> str:
    """
    新フォーマットのYouTubeトランスクリプトを変換する。

    入力フォーマット: タイムスタンプと日本語秒数読み上げが同一行に混在
        0:088 秒ですよ。
        0:1616 秒ですね
        1:031 分 3 秒たりとか...
        チャプター 1: タイトル

    出力フォーマット: `{timestamp} {transcription}`
        0:08 ですよ。
        0:16 ですね
        1:03 たりとか...
        ### チャプター 1: タイトル

    Args:
        text: 元のトランスクリプト全文

    Returns:
        変換後のトランスクリプト文字列
    """
    # タイムスタンプ + 日本語秒数読み上げ（オプション）+ テキスト
    timestamp_line_pattern = re.compile(
        r"^(\d{1,2}:\d{2}(?::\d{2})?)"   # タイムスタンプ (M:SS / MM:SS / H:MM:SS)
        r"(?:\d+ 分 \d+ 秒|\d+ 秒)?"       # 日本語秒数読み上げ（オプション）
        r"(.*)$"                           # 実際のテキスト
    )
    skip_lines = {"文字起こし", "## 文字起こし"}

    output: List[str] = []
    after_timestamp_only = False  # タイムスタンプのみの行の直後かどうか

    for line in text.splitlines():
        stripped = line.strip()

        if not stripped or stripped in skip_lines:
            continue

        # タイムスタンプ行の処理
        m = timestamp_line_pattern.match(stripped)
        if m:
            timestamp = m.group(1)
            content = m.group(2).strip()
            if not content:
                # タイムスタンプのみの行 → そのまま出力し、次行をテキスト行として扱う
                output.append(timestamp)
                after_timestamp_only = True
                continue
            # タイムスタンプ + テキスト → `{timestamp} {text}`
            output.append(f"{timestamp} {content}")
            after_timestamp_only = False
            continue

        if after_timestamp_only:
            # タイムスタンプの次の行はそのまま出力
            output.append(stripped)
        else:
            # タイムスタンプに紐づかない行 → セクション見出し
            output.append(f"### {stripped}")
        after_timestamp_only = False

    return "\n".join(output).rstrip() + "\n"
