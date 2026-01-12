# 12_youtube_screenshot.py (MoviePy版)
import base64
import datetime
import subprocess
import tempfile

import streamlit as st
from pathlib import Path
from moviepy import VideoFileClip

# --- 設定 ---
# システムの一時フォルダを取得（Linuxなら通常 /tmp）
TEMP_BASE = Path(tempfile.gettempdir())
IMAGE_DIR = TEMP_BASE / "stapp_images"
IMAGE_DIR.mkdir(exist_ok=True)
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

APP_TITLE = "YouTube Local Screenshoter"


def get_video_id(url: str) -> str | None:
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    return None


def download_video_low_res(url: str) -> Path | None:
    video_id = get_video_id(url)
    if not video_id:
        return None

    # /tmp/video_id.mp4 として保存
    output_path = TEMP_BASE / f"{video_id}.mp4"

    if output_path.exists():
        return output_path

    try:
        with st.spinner("YouTubeから低画質動画を取得中..."):
            # 再生互換性を高めるため mp4 を強制
            subprocess.run(
                [
                    "yt-dlp",
                    "-f",
                    "worst[ext=mp4]/worst",
                    "-o",
                    str(output_path),
                    url,
                ],
                check=True,
                capture_output=True,
            )
        return output_path
    except Exception as e:
        st.error(f"ダウンロード失敗: {e}")
        return None


def seconds_to_hms(total_seconds: float) -> str:
    """秒数を hh:mm:ss 形式に変換"""
    return str(datetime.timedelta(seconds=int(total_seconds)))


def timestamp_to_seconds(ts_str: str) -> float:
    try:
        parts = list(map(int, ts_str.split(":")))
        if len(parts) == 3:
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
        if len(parts) == 2:
            return parts[0] * 60 + parts[1]
        return float(parts[0])
    except Exception as e:
        st.error(f"conver timestamp failed: {e}")
        return 0.0


def image_to_base64(image_path: Path) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def main():
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    st.title(f"📸 {APP_TITLE}")

    # セッション状態の初期化
    if "video_path" not in st.session_state:
        st.session_state.video_path = None
    if "last_img" not in st.session_state:
        st.session_state.last_img = None

    # 1. 入力エリア
    video_url = st.text_input("YouTube URL", placeholder="https://...")

    if video_url:
        with st.expander(
            "動画を確認する（ここでの再生位置は取得できません）", expanded=True
        ):
            st.video(video_url)

        if st.button("📥 動画を取得する"):
            path = download_video_low_res(video_url)
            if path:
                st.session_state.video_path = path
                st.rerun()

    # 2. メインエリア
    if st.session_state.video_path:
        video_path = Path(st.session_state.video_path)

        st.divider()
        # col_v, col_c = st.columns([2, 1])
        col_c, col_i = st.columns(2)

        # with col_v:
        #     st.caption(f"動画保存先: {video_path}")
        #     if st.button("動画再生"):
        #         # 【重要】パスではなくバイナリを渡すことで再生トラブルを回避
        #         video_bytes = video_path.read_bytes()
        #         st.video(video_bytes)

        with col_c:
            st.subheader("スクショ操作")

            # 秒単位での指定（1秒毎の表示に対応しやすい）
            target_sec = st.number_input(
                "抽出したい秒数 (秒)",
                min_value=0,
                value=0,
                step=1,
                help="再生バーの時間を入力してください",
            )

            st.info(f"確定予定時刻: {seconds_to_hms(target_sec)}")

            if st.button("📸 この瞬間のスクショを確定", type="primary"):
                safe_ts = seconds_to_hms(target_sec).replace(":", "-")
                img_path = IMAGE_DIR / f"screenshot-{safe_ts}.png"

                try:
                    with st.spinner("画像を抽出中..."):
                        with VideoFileClip(str(video_path)) as clip:
                            clip.save_frame(str(img_path), t=target_sec)
                        st.session_state.last_img = img_path
                        st.session_state.current_ts = seconds_to_hms(
                            target_sec
                        )
                except Exception as e:
                    st.error(f"抽出失敗: {e}")

        # 3. 結果表示
        with col_i:
            if st.session_state.last_img:
                img_p = Path(st.session_state.last_img)
                st.divider()
                r_col1, r_col2 = st.columns(2)
                st.image(
                    str(img_p),
                    caption=f"確定時刻: {st.session_state.current_ts}",
                )
                b64 = base64.b64encode(img_p.read_bytes()).decode("utf-8")
                st.code(
                    # f'<img src="data:image/png;base64,{b64}"/>',
                    f"data:image/png;base64,{b64}",
                    language="html",
                )
                st.download_button(
                    "⬇️ ダウンロード", img_p.read_bytes(), file_name=img_p.name
                )


if __name__ == "__main__":
    main()
