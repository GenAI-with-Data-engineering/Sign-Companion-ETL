
import streamlit as st
from pytube import Playlist
from IPython.display import YouTubeVideo

def get_playlist_info(playlist_url):
    playlist = Playlist(playlist_url)
    video_info = [{"title": video.title, "video_id": video.video_id} for video in playlist.videos]
    return video_info

def main():
    st.title("ASL Learning Module")

    beginner_model = st.selectbox("Select Beginner's Model", ["Numbers", "Learn How to Sign ASL", "ASL Basics"])
    st.write(f"You selected: {beginner_model}")

    if beginner_model == "Numbers":
        playlist_url = ("https://www.youtube.com/watch?v=Y4stD_ypaAI&list=PLMN7QCuj6dfaO7v-Oqkg3Bjq0XOT3c07X")
    
    if beginner_model == "Learn How to Sign ASL":
        playlist_url = ("https://www.youtube.com/watch?v=6w1ZDaE-whc&list=PLMN7QCuj6dfaUwmtdkdKhINGZzyGwp7Q1")

    if beginner_model == "ASL Basics":
        playlist_url = ("https://www.youtube.com/watch?v=0FcwzMq4iWg&list=PLMN7QCuj6dfYD8DfG1rN6rEo1b1RyvgKF&pp=iAQB")

    if playlist_url:
        video_info = get_playlist_info(playlist_url)

        selected_video_info = st.selectbox("Select Video", video_info, format_func=lambda video: video["title"])

        if st.button("Watch Video"):
            video_url = f"https://www.youtube.com/watch?v={selected_video_info['video_id']}"
            st.video(video_url)
        


if __name__ == "__main__":
    main()
