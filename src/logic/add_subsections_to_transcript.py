# add_subsections_to_transcript.py
import re
from typing import List


def add_subsections_to_transcript(text: str) -> str:
    """
    YouTubeトランスクリプトにサブセクション見出し（###）を追加する。

    ルール概要:
    - 時刻形式: m:ss / mm:ss / h:mm:ss / hh:mm:ssではない単独行で、
      かつ「次の行が時刻」の場合、その行をサブセクションとみなす。
    - サブセクション行は元の位置から削除し、
      直後に続く最初の時刻行の直前に `### ` を付けて挿入する。
    - サブセクションの前後には空行を1行ずつ入れる。
    - 冒頭の「文字起こし」「## 文字起こし」ブロックは変更しない。

    Args:
        text: 元のトランスクリプト全文

    Returns:
        サブセクションを付与したトランスクリプト文字列
    """
    # time_pattern = re.compile(r"^\d{1,2}:\d{2}$")
    time_pattern = re.compile(r"^\d{1,2}:\d{2}(:\d{2})?$")
    lines = text.splitlines()

    def is_time(line: str) -> bool:
        return bool(time_pattern.match(line.strip()))

    output: List[str] = []
    pending_subsection: str | None = None

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        prev_line = lines[i - 1].strip() if i > 0 else ""
        next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""

        is_subsection_candidate = (
            stripped
            and not is_time(stripped)
            and not is_time(prev_line)
            and is_time(next_line)
            and stripped not in {"文字起こし", "## 文字起こし"}
        )

        if is_subsection_candidate:
            pending_subsection = stripped
            i += 1
            continue

        if is_time(stripped) and pending_subsection:
            if output and output[-1] != "":
                output.append("")
            output.append(f"### {pending_subsection}")
            # output.append("")
            pending_subsection = None

        output.append(line)
        i += 1

    return "\n".join(output).rstrip() + "\n"
