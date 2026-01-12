# 12_youtube_screenshot.py (MoviePy版)
import base64
import subprocess
import streamlit as st
from pathlib import Path
from moviepy import VideoFileClip

# ディレクトリ設定
TEMP_DIR = Path("temp_images")
DOWNLOAD_DIR = Path("downloads")
TEMP_DIR.mkdir(exist_ok=True)
DOWNLOAD_DIR.mkdir(exist_ok=True)

APP_TITLE = "YouTube Local Screenshoter"


def get_video_id(url: str) -> str | None:
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    return None


def download_video_low_res(url: str) -> Path | None:
    """yt-dlpを使って低画質動画をダウンロードする"""
    video_id = get_video_id(url)
    if not video_id:
        return None

    # 拡張子はmp4に固定（視聴互換性のため）
    output_path = DOWNLOAD_DIR / f"{video_id}.mp4"

    if output_path.exists():
        return output_path

    try:
        with st.spinner("動画を低画質で取得中..."):
            # -f "worst" で最低画質を指定
            # --merge-output-format mp4 でブラウザ再生可能な形式を担保
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
    st.title(f"🎬 {APP_TITLE}")

    # 1. URL入力エリア
    video_url = st.text_input(
        "YouTube URLを入力してください", placeholder="https://..."
    )

    # セッション状態の初期化
    if "local_video_path" not in st.session_state:
        st.session_state.local_video_path = None

    if video_url:
        # 動画取得ボタン
        if st.button("📥 動画を取得（複製ファイル作成）"):
            path = download_video_low_res(video_url)
            if path:
                st.session_state.local_video_path = path
                st.success("ダウンロード完了！")

    # 2. ダウンロード済みの場合の表示
    if st.session_state.local_video_path:
        video_path = st.session_state.local_video_path

        st.divider()
        col_video, col_ctrl = st.columns([2, 1])

        with col_video:
            st.subheader("視聴エリア")
            # ローカルファイルを再生
            st.video(str(video_path))

        with col_ctrl:
            st.subheader("スクショ操作")
            timestamp = st.text_input("取得秒数 (hh:mm:ss)", value="00:00:01")

            if st.button("📸 スクリーンショットを取得", type="primary"):
                t_sec = timestamp_to_seconds(timestamp)
                safe_ts = timestamp.replace(":", "-")
                img_path = TEMP_DIR / f"screenshot-{safe_ts}.png"

                try:
                    with VideoFileClip(str(video_path)) as clip:
                        clip.save_frame(str(img_path), t=t_sec)
                    st.session_state.last_img = img_path
                except Exception as e:
                    st.error(f"抽出失敗: {e}")

        # 3. 結果表示
        if "last_img" in st.session_state:
            img_p = st.session_state.last_img
            st.divider()
            res_col1, res_col2 = st.columns(2)

            with res_col1:
                st.image(str(img_p), caption=f"取得時刻: {timestamp}")
                with open(img_p, "rb") as f:
                    st.download_button(
                        "⬇️ PNGダウンロード", f, file_name=img_p.name
                    )

            with res_col2:
                b64 = image_to_base64(img_p)
                st.markdown("**Base64データ**")
                st.code(
                    f'<img src="data:image/png;base64,{b64}"/>',
                    language="html",
                )


if __name__ == "__main__":
    main()
