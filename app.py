import streamlit as st
import pandas as pd

# ページ設定
st.set_page_config(
    page_title="LongVideoBench Viewer",
    page_icon="🎥",
    layout="wide"
)

# タイトル
st.title("🎥 LongVideoBench Dataset Viewer")

# データ読み込み
@st.cache_data
def load_data():
    df = pd.read_parquet('data/test-00000-of-00001 (1).parquet')
    return df

try:
    df = load_data()

    # サイドバーでフィルタリング
    st.sidebar.header("フィルター")

    # トピックカテゴリでフィルタ
    topics = ["All"] + sorted(df['topic_category'].unique().tolist())
    selected_topic = st.sidebar.selectbox("トピックカテゴリ", topics)

    # 質問カテゴリでフィルタ
    question_categories = ["All"] + sorted(df['question_category'].unique().tolist())
    selected_question_cat = st.sidebar.selectbox("質問カテゴリ", question_categories)

    # 動画の長さでフィルタ
    duration_groups = ["All"] + sorted(df['duration_group'].unique().tolist())
    selected_duration = st.sidebar.selectbox("動画の長さ（秒）", duration_groups)

    # 動画の実際の長さでフィルタ（スライダー）
    min_duration = float(df['duration'].min())
    max_duration = float(df['duration'].max())
    duration_range = st.sidebar.slider(
        "動画の長さ（実際の秒数）",
        min_value=min_duration,
        max_value=max_duration,
        value=(min_duration, max_duration),
        step=1.0,
        format="%.1f秒"
    )

    # フィルタリング
    filtered_df = df.copy()
    if selected_topic != "All":
        filtered_df = filtered_df[filtered_df['topic_category'] == selected_topic]
    if selected_question_cat != "All":
        filtered_df = filtered_df[filtered_df['question_category'] == selected_question_cat]
    if selected_duration != "All":
        filtered_df = filtered_df[filtered_df['duration_group'] == selected_duration]
    
    # 実際の動画の長さでフィルタ
    filtered_df = filtered_df[
        (filtered_df['duration'] >= duration_range[0]) & 
        (filtered_df['duration'] <= duration_range[1])
    ]

    st.sidebar.write(f"表示件数: {len(filtered_df)} / {len(df)}")

    # 動画選択
    if len(filtered_df) > 0:
        video_options = [f"{row['video_id']} - {row['topic_category']}"
                        for idx, row in filtered_df.iterrows()]
        selected_idx = st.selectbox(
            "動画を選択",
            range(len(filtered_df)),
            format_func=lambda x: video_options[x]
        )

        # 選択された動画の情報
        selected_row = filtered_df.iloc[selected_idx]

        # 2カラムレイアウト
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("動画プレイヤー")

            # YouTubeの埋め込みプレイヤー
            video_id = selected_row['video_id']
            youtube_url = f"https://www.youtube.com/embed/{video_id}"

            st.markdown(
                f"""
                <iframe width="100%" height="500"
                src="{youtube_url}"
                frameborder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowfullscreen>
                </iframe>
                """,
                unsafe_allow_html=True
            )

            # YouTubeリンク
            st.markdown(f"[YouTubeで開く](https://www.youtube.com/watch?v={video_id})")

        with col2:
            st.subheader("基本情報")

            # 基本情報を表示
            info_data = {
                "Video ID": selected_row['video_id'],
                "Duration": f"{selected_row['duration']:.2f}秒",
                "Duration Group": f"{selected_row['duration_group']}秒",
                "Topic Category": selected_row['topic_category'],
                "Question Category": selected_row['question_category'],
                "Video Path": selected_row['video_path'],
                "Subtitle Path": selected_row['subtitle_path'],
            }

            for key, value in info_data.items():
                st.markdown(f"**{key}:** {value}")

        # 質問と選択肢を表示
        st.subheader("質問情報")

        st.markdown(f"**Question:** {selected_row['question']}")

        st.markdown("**Options:**")
        for i in range(5):
            option = selected_row[f'option{i}']
            if option != "N/A":
                is_correct = (i == selected_row['correct_choice'])
                if is_correct:
                    st.markdown(f"- ✅ **Option {i}:** {option}")
                else:
                    st.markdown(f"- Option {i}: {option}")

        # データの詳細表示（折りたたみ可能）
        with st.expander("全データを表示"):
            st.json(selected_row.to_dict())

    else:
        st.warning("選択された条件に一致する動画がありません。")

except FileNotFoundError:
    st.error("データファイルが見つかりません。data/test-00000-of-00001 (1).parquet を確認してください。")
except Exception as e:
    st.error(f"エラーが発生しました: {str(e)}")
