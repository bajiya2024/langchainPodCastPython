import streamlit as st
import helperClass


def main():
    st.title("Convert any youtube video into podcast(Hindi)")

    # Text input
    input_text = st.text_input("Enter Youtube Url:")
    # Language selection (optional)
    language = st.selectbox("Select Language:", ["hi"])

    if st.button("Generate Audio"):

        audio_file_path = helperClass.YouTubeVideoToHindiAudio(input_text).run()

        st.success("Audio generated successfully!")

        # Audio player
        st.audio(audio_file_path, format="audio/mp3")

        # Download link
        st.markdown(f"Download [audio file](/{audio_file_path})")


if __name__ == "__main__":
    main()
