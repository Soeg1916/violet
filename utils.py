import os
import cv2
import logging
import tempfile
import shutil
from typing import List, Optional

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

def create_temp_dir() -> str:
    """Create a temporary directory for storing frames."""
    temp_dir = tempfile.mkdtemp()
    logger.info(f"Created temporary directory: {temp_dir}")
    return temp_dir

def cleanup_temp_files(file_paths: List[str], temp_dir: str) -> None:
    """Clean up temporary files and directory."""
    # Delete individual files
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {str(e)}")
    
    # Delete the temporary directory
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    except Exception as e:
        logger.error(f"Error deleting directory {temp_dir}: {str(e)}")

def extract_frames(
    video_path: str, 
    output_dir: str, 
    interval: int = 1, 
    max_duration: int = 30
) -> List[str]:
    """
    Extract frames from a video at specified intervals.
    
    Args:
        video_path (str): Path to the video file
        output_dir (str): Directory to save the extracted frames
        interval (int): Interval in seconds to extract frames
        max_duration (int): Maximum video duration to process in seconds
        
    Returns:
        List[str]: List of paths to the extracted frames
    """
    try:
        # Open the video file
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            logger.error(f"Could not open video file: {video_path}")
            return []
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            logger.error(f"Invalid FPS value: {fps}")
            return []
            
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        
        logger.info(f"Video info - FPS: {fps}, Duration: {duration}s, Total frames: {total_frames}")
        
        # Check if video is too long
        if duration > max_duration:
            logger.warning(f"Video duration ({duration}s) exceeds maximum allowed ({max_duration}s)")
            # We'll still process up to max_duration
            duration = max_duration
        
        # Calculate frames to extract
        frame_indices = []
        for second in range(0, int(duration) + 1, interval):
            frame_indices.append(int(second * fps))
        
        # Extract frames
        frame_paths = []
        for i, frame_idx in enumerate(frame_indices):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            
            if not ret:
                logger.warning(f"Failed to extract frame at index {frame_idx}")
                continue
            
            # Save the frame
            output_path = os.path.join(output_dir, f"frame_{i+1:03d}.jpg")
            cv2.imwrite(output_path, frame)
            frame_paths.append(output_path)
            
            logger.info(f"Extracted frame {i+1}/{len(frame_indices)} at {(i+1)}s")
        
        # Release the video capture
        cap.release()
        
        return frame_paths
    
    except Exception as e:
        logger.error(f"Error extracting frames: {str(e)}")
        return []
