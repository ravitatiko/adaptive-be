import google.generativeai as genai
from typing import Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class SummaryService:
    def __init__(self):
        """Initialize the Google Generative AI service."""
        if not settings.google_api_key:
            logger.warning("Google API key not configured. Summarization will not work.")
            return
        
        try:
            genai.configure(api_key=settings.google_api_key)
            # Use the correct model name for the current API version
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("Google Generative AI service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Google Generative AI: {e}")
            self.model = None

    async def summarize_text(
        self, 
        text: str, 
        max_length: Optional[int] = None,
        style: str = "concise"
    ) -> dict:
        """
        Summarize text using Google's Generative AI.
        
        Args:
            text: The text to summarize
            max_length: Maximum length of summary (optional)
            style: Summary style - "concise", "detailed", "bullet_points"
        
        Returns:
            dict: Contains summary, word_count, and metadata
        """
        if not self.model:
            return {
                "error": "Google API not configured",
                "summary": None,
                "word_count": 0,
                "original_word_count": len(text.split())
            }
        
        if not text.strip():
            return {
                "error": "Empty text provided",
                "summary": None,
                "word_count": 0,
                "original_word_count": 0
            }

        try:
            # Create prompt based on style
            prompt = self._create_prompt(text, max_length, style)
            
            # Generate summary
            response = self.model.generate_content(prompt)
            
            if not response.text:
                return {
                    "error": "No summary generated",
                    "summary": None,
                    "word_count": 0,
                    "original_word_count": len(text.split())
                }
            
            summary = response.text.strip()
            word_count = len(summary.split())
            original_word_count = len(text.split())
            
            return {
                "summary": summary,
                "word_count": word_count,
                "original_word_count": original_word_count,
                "compression_ratio": round(original_word_count / word_count, 2) if word_count > 0 else 0,
                "style": style,
                "max_length": max_length
            }
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return {
                "error": f"Failed to generate summary: {str(e)}",
                "summary": None,
                "word_count": 0,
                "original_word_count": len(text.split())
            }

    def _create_prompt(self, text: str, max_length: Optional[int], style: str) -> str:
        """Create a prompt for the AI model based on the desired style."""
        
        base_prompt = f"Please summarize the following text:\n\n{text}\n\n"
        
        if style == "concise":
            style_instruction = "Provide a concise summary that captures the main points."
        elif style == "detailed":
            style_instruction = "Provide a detailed summary that includes key points and supporting details."
        elif style == "bullet_points":
            style_instruction = "Provide a summary in bullet point format, highlighting the main ideas."
        else:
            style_instruction = "Provide a clear and informative summary."
        
        if max_length:
            style_instruction += f" Keep the summary under {max_length} words."
        
        return base_prompt + style_instruction

    async def extract_key_points(self, text: str, num_points: int = 5) -> dict:
        """
        Extract key points from text.
        
        Args:
            text: The text to analyze
            num_points: Number of key points to extract
        
        Returns:
            dict: Contains key points and metadata
        """
        if not self.model:
            return {
                "error": "Google API not configured",
                "key_points": [],
                "word_count": 0
            }
        
        try:
            prompt = f"""
            Extract the {num_points} most important key points from the following text:
            
            {text}
            
            Format each key point as a clear, concise statement. Number them 1-{num_points}.
            """
            
            response = self.model.generate_content(prompt)
            
            if not response.text:
                return {
                    "error": "No key points extracted",
                    "key_points": [],
                    "word_count": 0
                }
            
            # Parse the response to extract numbered points
            key_points = []
            lines = response.text.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('•') or line.startswith('-')):
                    # Remove numbering/bullets and clean up
                    point = line.split('.', 1)[-1].strip() if '.' in line else line
                    point = point.lstrip('•- ').strip()
                    if point:
                        key_points.append(point)
            
            return {
                "key_points": key_points[:num_points],
                "word_count": len(text.split()),
                "extracted_count": len(key_points)
            }
            
        except Exception as e:
            logger.error(f"Error extracting key points: {e}")
            return {
                "error": f"Failed to extract key points: {str(e)}",
                "key_points": [],
                "word_count": len(text.split())
            }

    async def analyze_sentiment(self, text: str) -> dict:
        """
        Analyze the sentiment of the text.
        
        Args:
            text: The text to analyze
        
        Returns:
            dict: Contains sentiment analysis results
        """
        if not self.model:
            return {
                "error": "Google API not configured",
                "sentiment": None,
                "confidence": 0
            }
        
        try:
            prompt = f"""
            Analyze the sentiment of the following text and provide:
            1. Overall sentiment (positive, negative, neutral)
            2. Confidence level (0-100%)
            3. Brief explanation
            
            Text: {text}
            
            Format your response as:
            Sentiment: [positive/negative/neutral]
            Confidence: [percentage]
            Explanation: [brief explanation]
            """
            
            response = self.model.generate_content(prompt)
            
            if not response.text:
                return {
                    "error": "No sentiment analysis generated",
                    "sentiment": None,
                    "confidence": 0
                }
            
            # Parse the response
            lines = response.text.strip().split('\n')
            sentiment = "neutral"
            confidence = 0
            explanation = ""
            
            for line in lines:
                line = line.strip()
                if line.startswith('Sentiment:'):
                    sentiment = line.split(':', 1)[1].strip().lower()
                elif line.startswith('Confidence:'):
                    try:
                        confidence = int(line.split(':', 1)[1].strip().rstrip('%'))
                    except:
                        confidence = 0
                elif line.startswith('Explanation:'):
                    explanation = line.split(':', 1)[1].strip()
            
            return {
                "sentiment": sentiment,
                "confidence": confidence,
                "explanation": explanation,
                "word_count": len(text.split())
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {
                "error": f"Failed to analyze sentiment: {str(e)}",
                "sentiment": None,
                "confidence": 0
            }


# Create a singleton instance
summary_service = SummaryService()

