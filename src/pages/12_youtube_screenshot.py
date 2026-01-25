# 12_youtube_screenshot.py (MoviePy版)
import base64
import datetime

# import subprocess
import tempfile

import streamlit as st
from pathlib import Path
from moviepy import VideoFileClip
from yt_dlp import YoutubeDL

# --- 設定の集約 ---
TEMP_BASE = Path(tempfile.gettempdir())
IMAGE_DIR = TEMP_BASE / "stapp_images"
IMAGE_DIR.mkdir(exist_ok=True)

APP_TITLE = "YouTube Local Screenshoter"


def convert_short_url(url: str) -> str:
    if "youtube.com/shorts" in url:
        id = url.split("/")[-1].split("?")[0]
        return f"https://youtu.be/{id}"
    elif url is None:
        return ""
    else:
        return url


def get_video_id(url: str) -> str | None:
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    return None


def download_video_low_res(url: str) -> Path | None:
    video_id = get_video_id(url)
    st.session_state.video_id = video_id
    st.session_state.video_url = url
    if not video_id:
        return None

    # /tmp/video_id.mp4
    output_path = TEMP_BASE / f"{video_id}.mp4"
    if output_path.exists():
        return output_path

    # yt-dlp ライブラリ用のオプション設定
    ydl_opts = {
        # 1. 映像と音声をセットで取得し、かつ「一番マシな低画質」を狙う
        "format": "bestvideo[ext=mp4][vcodec^=avc1]+"
        + "bestaudio[ext=m4a]/worst[ext=mp4]/worst",
        "outtmpl": str(output_path),
        # 2. 強制的にmp4として結合（FFmpegが必要）
        "merge_output_format": "mp4",  # 強制的にmp4で結合
        "quiet": True,
        "no_warnings": True,
    }
    try:
        with st.spinner("低画質動画を /tmp に準備中..."):
            with YoutubeDL(ydl_opts) as ydl:
                # downloadメソッドはリスト形式でURLを受け取ります
                ydl.download([url])
        return output_path
    except Exception as e:
        st.error(f"DL失敗: {e}")
        return None


def seconds_to_hms(seconds: float) -> str:
    return str(datetime.timedelta(seconds=int(seconds)))


def initialize_session_state() -> None:
    if "video_url" not in st.session_state:
        st.session_state.video_url = None
    if "video_path" not in st.session_state:
        st.session_state.video_id = None
    if "video_path" not in st.session_state:
        st.session_state.video_path = None
    if "last_img" not in st.session_state:
        st.session_state.last_img = None
    if "current_ts" not in st.session_state:
        st.session_state.current_ts = "00:00:00"
    if "target_sec" not in st.session_state:
        st.session_state.target_sec = 0


def main():
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    st.page_link("main.py", label="Back to Home", icon="🏠")
    st.title(f"📸 {APP_TITLE}")

    # 1. URL入力と準備
    video_url = st.text_input(
        label="YouTube URL",
        placeholder="https://...",
        # value=st.session_state.video_url,
    )
    video_url = convert_short_url(video_url)

    # ダウンロード前のプレビュー
    # if video_url and not st.session_state.video_path:
    if video_url:
        st.video(video_url)
        st.divider()
        if st.session_state.video_path is None:
            st.subheader("1. 動画を取得")
            if st.button("📥 この動画を取得して編集を開始する", type="primary"):
                path = download_video_low_res(video_url)
                if path:
                    st.session_state.video_path = path
                    st.rerun()

    # 2. メイン操作エリア（ダウンロード後）
    if st.session_state.video_path:
        video_path = Path(st.session_state.video_path)
        st.success(f"準備完了: {video_path.name}")

        # col_video, col_ctrl = st.columns([1.5, 1])
        col_left, col_right = st.columns([1, 1.5])

        # with col_video:
        #     st.subheader("1. 動画を再生して時間を確認")
        #     # バイナリ読み込みで再生を安定化
        #     st.video(video_path.read_bytes())
        #     st.info("再生バーに表示される時間を下の入力欄に入れてください。")

        # with col_ctrl:
        with col_left:
            st.subheader("2. スクショ確定")

            # --- 入力方式の選択 ---
            switch_second = st.toggle("秒数で指定")
            target_sec = 0

            if switch_second:
                target_sec = st.number_input(
                    "秒数を指定",
                    min_value=0,
                    # value=0,
                    value=st.session_state.target_sec,
                    step=1,
                    help="秒数を入力してください",
                )

            else:
                time_str = st.text_input(
                    "時刻を指定 (hh:mm:ss)",
                    # value="00:00:00",
                    value=st.session_state.current_ts,
                    help="例: 01:23:45",
                )

                try:
                    h, m, s = map(int, time_str.split(":"))
                    target_sec = h * 3600 + m * 60 + s
                    current_hms = time_str
                except ValueError:
                    st.error("時刻は hh:mm:ss 形式で入力してください")
                    current_hms = "00:00:00"

            # HMS形式で確認表示
            current_hms = seconds_to_hms(target_sec)
            st.metric("ターゲット時間", f"{current_hms} ({target_sec})")

            if st.button(
                "📸 スクリーンショットを保存",
                type="primary",
                use_container_width=True,
            ):
                # 要件通りのファイル名形式: screenshot-hh-mm-ss.png
                safe_ts = current_hms.replace(":", "-")
                img_path = IMAGE_DIR / f"screenshot-{safe_ts}.png"

                try:
                    with st.spinner("MoviePyでフレームを抽出中..."):
                        with VideoFileClip(str(video_path)) as clip:
                            clip.save_frame(str(img_path), t=target_sec)
                        st.session_state.last_img = img_path
                        st.session_state.target_sec = target_sec
                        st.session_state.current_ts = current_hms
                except Exception as e:
                    st.error(f"抽出エラー: {e}")

        with col_right:
            # 3. 取得結果の表示（コントロールカラム内に配置）
            st.subheader("3. コピー／ダウンロード")
            if st.session_state.last_img:
                # st.divider()
                img_p = Path(st.session_state.last_img)
                st.image(
                    str(img_p),
                    caption=f"確定時刻: {st.session_state.current_ts}",
                )

                # Base64表示
                b64 = base64.b64encode(img_p.read_bytes()).decode("utf-8")
                st.markdown("**Base64データ (imgタグ用)**")
                st.code(f"data:image/png;base64,{b64}", language="text")

                st.download_button(
                    "⬇️ PNGをダウンロード",
                    img_p.read_bytes(),
                    file_name=f"screenshot-{st.session_state.current_ts}.png",
                    mime="image/png",
                    use_container_width=True,
                )

        st.divider()
        if st.button("🔄 別の動画に変更"):
            st.session_state.video_path = None
            st.session_state.clear()
            st.rerun()



if __name__ == "__main__":
    initialize_session_state()
    main()
