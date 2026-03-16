"""
Video Processor
Extracts frames, audio, and metadata from video files
"""
import cv2
from moviepy.editor import VideoFileClip
from typing import Dict, Any, List
import logging
import tempfile
import os
import numpy as np

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Processes video files and extracts content"""

    async def extract_metadata(self, video_data: bytes) -> Dict[str, Any]:
        """
        Extract metadata from video

        Args:
            video_data: Video file bytes

        Returns:
            Dictionary with video metadata
        """
        try:
            # Save video to temporary file
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".mp4"
            ) as temp_file:
                temp_file.write(video_data)
                temp_path = temp_file.name

            try:
                # Open video with OpenCV
                cap = cv2.VideoCapture(temp_path)

                # Get video properties
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                duration = frame_count / fps if fps > 0 else 0

                cap.release()

                # Get audio info using moviepy
                try:
                    clip = VideoFileClip(temp_path)
                    has_audio = clip.audio is not None
                    audio_duration = clip.duration if has_audio else 0
                    clip.close()
                except:
                    has_audio = False
                    audio_duration = 0

                return {
                    "duration_seconds": round(duration, 2),
                    "fps": round(fps, 2),
                    "frame_count": frame_count,
                    "width": width,
                    "height": height,
                    "resolution": f"{width}x{height}",
                    "has_audio": has_audio,
                    "audio_duration": round(audio_duration, 2),
                }

            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)

        except Exception as e:
            logger.error(f"Video metadata extraction error: {e}")
            raise

    async def extract_frames(
        self, video_data: bytes, num_frames: int = 10
    ) -> Dict[str, Any]:
        """
        Extract frames from video at regular intervals

        Args:
            video_data: Video file bytes
            num_frames: Number of frames to extract

        Returns:
            Dictionary with frame information
        """
        try:
            # Save video to temporary file
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".mp4"
            ) as temp_file:
                temp_file.write(video_data)
                temp_path = temp_file.name

            try:
                cap = cv2.VideoCapture(temp_path)
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                fps = cap.get(cv2.CAP_PROP_FPS)

                # Calculate frame intervals
                interval = max(1, total_frames // num_frames)

                frames = []
                for i in range(0, total_frames, interval):
                    if len(frames) >= num_frames:
                        break

                    cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                    ret, frame = cap.read()

                    if ret:
                        timestamp = i / fps if fps > 0 else 0
                        frames.append({
                            "frame_number": i,
                            "timestamp": round(timestamp, 2),
                            "shape": frame.shape,
                        })

                cap.release()

                return {
                    "total_frames": total_frames,
                    "extracted_frames": len(frames),
                    "frames": frames,
                }

            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)

        except Exception as e:
            logger.error(f"Frame extraction error: {e}")
            raise

    async def extract_audio(self, video_data: bytes) -> Dict[str, Any]:
        """
        Extract audio from video

        Args:
            video_data: Video file bytes

        Returns:
            Dictionary with audio extraction info
        """
        try:
            # Save video to temporary file
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".mp4"
            ) as temp_file:
                temp_file.write(video_data)
                temp_path = temp_file.name

            try:
                clip = VideoFileClip(temp_path)

                if clip.audio is None:
                    clip.close()
                    return {
                        "has_audio": False,
                        "message": "Video has no audio track",
                    }

                # Get audio properties
                duration = clip.audio.duration
                fps = clip.audio.fps
                nchannels = clip.audio.nchannels

                clip.close()

                return {
                    "has_audio": True,
                    "duration": round(duration, 2),
                    "sample_rate": fps,
                    "channels": nchannels,
                }

            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)

        except Exception as e:
            logger.error(f"Audio extraction error: {e}")
            raise

    async def detect_scenes(
        self, video_data: bytes, threshold: float = 30.0
    ) -> Dict[str, Any]:
        """
        Detect scene changes in video

        Args:
            video_data: Video file bytes
            threshold: Threshold for scene change detection

        Returns:
            Dictionary with scene change information
        """
        try:
            # Save video to temporary file
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".mp4"
            ) as temp_file:
                temp_file.write(video_data)
                temp_path = temp_file.name

            try:
                cap = cv2.VideoCapture(temp_path)
                fps = cap.get(cv2.CAP_PROP_FPS)

                scenes = []
                prev_frame = None
                frame_num = 0

                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break

                    # Convert to grayscale
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                    if prev_frame is not None:
                        # Calculate difference
                        diff = cv2.absdiff(prev_frame, gray)
                        mean_diff = np.mean(diff)

                        # Detect scene change
                        if mean_diff > threshold:
                            timestamp = frame_num / fps if fps > 0 else 0
                            scenes.append({
                                "frame_number": frame_num,
                                "timestamp": round(timestamp, 2),
                                "difference": round(mean_diff, 2),
                            })

                    prev_frame = gray
                    frame_num += 1

                cap.release()

                return {
                    "scene_count": len(scenes),
                    "scenes": scenes,
                    "threshold_used": threshold,
                }

            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)

        except Exception as e:
            logger.error(f"Scene detection error: {e}")
            raise
