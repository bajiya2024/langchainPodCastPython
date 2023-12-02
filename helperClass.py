import os
from typing import Any, Dict, Optional, Union

from langchain.utils import get_from_dict_or_env
from langchain_core.pydantic_v1 import root_validator
from langchain.document_loaders import YoutubeLoader
from langchain.text_splitter import  RecursiveCharacterTextSplitter
from enum import Enum


import elevenlabs
import uuid
from googletrans import Translator
from dotenv import load_dotenv
load_dotenv()


# Create a directory if it doesn't exist
output_folder = "AudioFile"
os.makedirs(output_folder, exist_ok=True)


class LangchainModels(str, Enum):
    """Models which going to use"""
    LANGCHAIN_YOUTUBE_MODEL = "text-davinci-003"
    ELEVEN_LABS_TXT_SPEECH_MODEL = "eleven_multilingual_v1"


class YouTubeVideoToHindiAudio:
    def __init__(self, yt_url):
        self.ty_url = yt_url
        self.output_folder = 'AudioFile'
        # Create a directory if it doesn't exist
        os.makedirs(self.output_folder, exist_ok=True)

    model: Union[LangchainModels, str] = LangchainModels

    @root_validator(pre=True)
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that api key exists in environment."""
        _ = get_from_dict_or_env(values, "eleven_api_key", "ELEVEN_API_KEY")

        return values

    @staticmethod
    def video_to_transcript(ty_url) -> list:
        loader = YoutubeLoader.from_youtube_url(ty_url)
        transcript = loader.load()
        if transcript:
            text_spliter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            docs = text_spliter.split_documents(transcript)

            return docs
        else:
            raise RuntimeError("Error while running video_to_text")

    @staticmethod
    def chunk_text(text, chunk_size):
        chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
        return chunks

    def convert_english_to_hindi(self, text_docs):
        """
        :text_docs : english transcript list
        :return:
        """
        docs_page_content = " ".join([d.page_content for d in text_docs])
        # Specify the chunk size (4000 characters)
        chunk_size = 4000
        # Get the chunks
        text_chunks = self.chunk_text(docs_page_content, chunk_size)
        hindi_text = ""
        if text_chunks:
            for i, chunk in enumerate(text_chunks):
                translator = Translator()
                translation = translator.translate(chunk, src="en", dest='hi')
                if translation and translation is not None and hasattr(translation, 'text'):
                    hindi_text = hindi_text + translation.text
        # for api limit
        print("English to hindi 100 text==>", hindi_text[0:100])
        return hindi_text[0:200]

    def text_to_speech(self, query_text: str, video_id: str):
        if query_text and len(query_text) > 0:
            el_model = self.model.ELEVEN_LABS_TXT_SPEECH_MODEL
            try:
                speech = elevenlabs.generate(text=query_text, model=el_model)
                output_file_path = os.path.join(self.output_folder, f'{video_id}.wav')
                # f'{video_id}.wav'
                with open(output_file_path, mode='bx') as f:
                    f.write(speech)
                return output_file_path
            except Exception as e:
                raise RuntimeError(f"Error while running ElevenLabsText2SpeechTool: {e}")

        raise RuntimeError(f"No text fount text to speech")

    def run(self):
        video_to_text = self.video_to_transcript(self.ty_url)
        # convert english text to hindi
        eng_to_hindi = self.convert_english_to_hindi(video_to_text)
        # convert hindi text to audio
        audio_file = self.text_to_speech(eng_to_hindi, str(uuid.uuid4()))
        print("Audio File path==>", audio_file)
        return audio_file


# youtube_url = 'https://www.youtube.com/watch?v=gY3DKOO9Mfo'
# YouTubeVideoToHindiAudio(youtube_url).run()
