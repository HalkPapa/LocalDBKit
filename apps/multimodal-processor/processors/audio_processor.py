"""
Audio Processor
Transcribes audio files using OpenAI Whisper
"""
import whisper
from typing import Dict, Any
import logging
import tempfile
import os

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Processes audio files and generates transcriptions"""

    def __init__(self, model_size: str = "base"):
        """
        Initialize Audio Processor

        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
        """
        self.model_size = model_size
        self.model = None

    def _load_model(self):
        """Load Whisper model (lazy loading)"""
        if self.model is None:
            logger.info(f"Loading Whisper model: {self.model_size}")
            self.model = whisper.load_model(self.model_size)

    async def transcribe(
        self, audio_data: bytes, language: str = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text

        Args:
            audio_data: Audio file bytes
            language: Optional language code (e.g., 'en', 'ja')

        Returns:
            Dictionary with transcription and metadata
        """
        try:
            self._load_model()

            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".audio"
            ) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name

            try:
                # Transcribe
                result = self.model.transcribe(
                    temp_path,
                    language=language,
                    verbose=False,
                )

                # Extract segments
                segments = []
                for segment in result.get("segments", []):
                    segments.append({
                        "start": segment["start"],
                        "end": segment["end"],
                        "text": segment["text"].strip(),
                    })

                return {
                    "text": result["text"].strip(),
                    "language": result.get("language", "unknown"),
                    "segments": segments,
                    "segment_count": len(segments),
                }

            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)

        except Exception as e:
            logger.error(f"Audio transcription error: {e}")
            raise

    async def transcribe_with_timestamps(
        self, audio_data: bytes, language: str = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio with word-level timestamps

        Args:
            audio_data: Audio file bytes
            language: Optional language code

        Returns:
            Dictionary with detailed transcription and timestamps
        """
        try:
            self._load_model()

            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".audio"
            ) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name

            try:
                # Transcribe with word timestamps
                result = self.model.transcribe(
                    temp_path,
                    language=language,
                    word_timestamps=True,
                    verbose=False,
                )

                # Extract words with timestamps
                words = []
                for segment in result.get("segments", []):
                    for word_info in segment.get("words", []):
                        words.append({
                            "word": word_info["word"].strip(),
                            "start": word_info["start"],
                            "end": word_info["end"],
                            "probability": word_info.get("probability", 0),
                        })

                return {
                    "text": result["text"].strip(),
                    "language": result.get("language", "unknown"),
                    "words": words,
                    "word_count": len(words),
                }

            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)

        except Exception as e:
            logger.error(f"Audio transcription with timestamps error: {e}")
            raise

    async def detect_language(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Detect language of audio

        Args:
            audio_data: Audio file bytes

        Returns:
            Dictionary with language detection results
        """
        try:
            self._load_model()

            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".audio"
            ) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name

            try:
                # Detect language
                audio = whisper.load_audio(temp_path)
                audio = whisper.pad_or_trim(audio)

                mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
                _, probs = self.model.detect_language(mel)

                # Get top 5 languages
                top_langs = sorted(
                    probs.items(), key=lambda x: x[1], reverse=True
                )[:5]

                return {
                    "detected_language": max(probs, key=probs.get),
                    "confidence": max(probs.values()),
                    "top_languages": [
                        {"language": lang, "probability": prob}
                        for lang, prob in top_langs
                    ],
                }

            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)

        except Exception as e:
            logger.error(f"Language detection error: {e}")
            raise
