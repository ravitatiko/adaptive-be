"""
Generic LLM Service for content generation with different result types.
Supports multiple LLM providers and flexible content generation.
"""

import json
import logging
from typing import Dict, Any, List, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field
import asyncio
import google.generativeai as genai
from app.core.config import settings

logger = logging.getLogger(__name__)


class ResultType(str, Enum):
    """Supported result types for LLM generation."""
    QUIZ_MCQ = "quiz_mcq"
    EXPLANATION = "explanation"
    SUMMARY = "summary"
    STORY = "story"
    MEME_DESCRIPTION = "meme_description"
    ANALOGY = "analogy"
    CODE_EXAMPLE = "code_example"
    STEP_BY_STEP = "step_by_step"
    CUSTOM = "custom"


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    GOOGLE = "google"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"


class QuizQuestion(BaseModel):
    """Model for quiz question structure."""
    question: str
    options: List[str] = Field(min_items=2, max_items=6)
    correct_answer: int = Field(ge=0)
    explanation: Optional[str] = None


class QuizMCQ(BaseModel):
    """Model for multiple choice quiz."""
    title: str
    questions: List[QuizQuestion] = Field(min_items=1)
    difficulty: Optional[str] = "medium"


class LLMRequest(BaseModel):
    """Request model for LLM generation."""
    content: str = Field(description="The input content/description")
    result_type: ResultType = Field(description="Type of result to generate")
    additional_params: Optional[Dict[str, Any]] = Field(default_factory=dict)
    provider: LLMProvider = LLMProvider.GOOGLE
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7


class LLMResponse(BaseModel):
    """Response model for LLM generation."""
    success: bool
    result: Union[Dict[str, Any], str, List[Dict[str, Any]]]
    result_type: ResultType
    provider: LLMProvider
    tokens_used: Optional[int] = None
    error_message: Optional[str] = None


class PromptTemplate:
    """Template manager for different result types."""
    
    TEMPLATES = {
        ResultType.QUIZ_MCQ: """
Based on the following content, create a multiple choice quiz with {num_questions} questions.

Content: {content}

Requirements:
- Create {num_questions} multiple choice questions
- Each question should have {num_options} options
- Include the correct answer index (0-based)
- Add brief explanations for correct answers
- Difficulty level: {difficulty}

IMPORTANT: Return ONLY valid JSON in the exact format below. Do not include any markdown formatting, explanations, or additional text.

{{
    "title": "Quiz about the given content",
    "questions": [
        {{
            "question": "Question text here?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": 0,
            "explanation": "Brief explanation of why this is correct"
        }}
    ],
    "difficulty": "{difficulty}"
}}
""",

        ResultType.EXPLANATION: """
Provide a clear and comprehensive explanation of the following content:

Content: {content}

Style: {style}
Target audience: {audience}

Requirements:
- Make it easy to understand
- Include key concepts and definitions
- Use examples where appropriate
- Structure the explanation logically

Return a well-formatted explanation.
""",

        ResultType.SUMMARY: """
Create a concise summary of the following content:

Content: {content}

Requirements:
- Highlight the main points
- Keep it concise but comprehensive
- Use bullet points if appropriate
- Length: {length} words approximately

Return a well-structured summary.
""",

        ResultType.STORY: """
Create an engaging story that explains the following concept:

Content: {content}

Requirements:
- Use storytelling to make the concept memorable
- Include characters and a plot
- Make it educational and entertaining
- Target audience: {audience}
- Story length: {length}

Return an engaging story that teaches the concept.
""",

        ResultType.MEME_DESCRIPTION: """
Create a meme description that explains the following concept in a humorous way:

Content: {content}

Requirements:
- Use popular meme formats or cultural references
- Make it funny but educational
- Include visual description for the meme
- Keep it relatable and memorable

Return a meme description with:
- Meme format/template
- Visual description
- Text/caption
- Educational message
""",

        ResultType.ANALOGY: """
Create a clear analogy to explain the following concept:

Content: {content}

Requirements:
- Use a real-world, relatable comparison
- Make the analogy accurate and helpful
- Explain how the analogy relates to the concept
- Make it memorable and easy to understand

Return a detailed analogy explanation.
""",

        ResultType.CODE_EXAMPLE: """
Create a practical code example for the following concept:

Content: {content}

Requirements:
- Programming language: {language}
- Include comments explaining the code
- Make it practical and runnable
- Show best practices
- Include example usage

Return well-commented code with explanations.
""",

        ResultType.STEP_BY_STEP: """
Create a step-by-step guide for the following content:

Content: {content}

Requirements:
- Break down into clear, actionable steps
- Number each step
- Include any prerequisites
- Add tips or warnings where appropriate
- Make it easy to follow

Return a detailed step-by-step guide.
""",

        ResultType.CUSTOM: """
{custom_prompt}

Content: {content}

{additional_instructions}
"""
    }

    @classmethod
    def get_prompt(cls, result_type: ResultType, content: str, **kwargs) -> str:
        """Get formatted prompt for the specified result type."""
        template = cls.TEMPLATES.get(result_type)
        if not template:
            raise ValueError(f"No template found for result type: {result_type}")
        
        # Set default values for common parameters
        params = {
            'content': content,
            'num_questions': kwargs.get('num_questions', 5),
            'num_options': kwargs.get('num_options', 4),
            'difficulty': kwargs.get('difficulty', 'medium'),
            'style': kwargs.get('style', 'clear and engaging'),
            'audience': kwargs.get('audience', 'general learners'),
            'length': kwargs.get('length', 'medium'),
            'language': kwargs.get('language', 'Python'),
            'custom_prompt': kwargs.get('custom_prompt', ''),
            'additional_instructions': kwargs.get('additional_instructions', ''),
            **kwargs
        }
        
        return template.format(**params)


class LLMService:
    """Generic LLM service for content generation."""
    
    def __init__(self):
        self.openai_client = None
        self.google_client = None
        self.setup_providers()
    
    def setup_providers(self):
        """Initialize LLM provider clients."""
        try:
            # Setup Google Gemini
            if hasattr(settings, 'google_api_key') and settings.google_api_key:
                genai.configure(api_key=settings.google_api_key)
                self.google_client = genai.GenerativeModel('gemini-1.5-flash')
            else:
                logger.warning("Google API key not configured")
            
            # Setup OpenAI
            if hasattr(settings, 'openai_api_key') and settings.openai_api_key:
                self.openai_client = OpenAI(api_key=settings.openai_api_key)
            else:
                logger.warning("OpenAI API key not configured")
        except Exception as e:
            logger.error(f"Error setting up LLM providers: {e}")
    
    async def generate_content(self, request: LLMRequest) -> LLMResponse:
        """
        Generate content using the specified LLM provider and result type.
        
        Args:
            request: LLM request with content, result type, and parameters
            
        Returns:
            LLMResponse with generated content
        """
        try:
            # Build prompt using template
            prompt = PromptTemplate.get_prompt(
                request.result_type,
                request.content,
                **request.additional_params
            )
            
            # Generate content based on provider
            if request.provider == LLMProvider.GOOGLE:
                response = await self._generate_google(prompt, request)
            elif request.provider == LLMProvider.OPENAI:
                response = await self._generate_openai(prompt, request)
            elif request.provider == LLMProvider.ANTHROPIC:
                response = await self._generate_anthropic(prompt, request)
            elif request.provider == LLMProvider.LOCAL:
                response = await self._generate_local(prompt, request)
            else:
                raise ValueError(f"Unsupported provider: {request.provider}")
            
            # Parse and validate response based on result type
            parsed_result = self._parse_response(response, request.result_type)
            
            return LLMResponse(
                success=True,
                result=parsed_result,
                result_type=request.result_type,
                provider=request.provider,
                tokens_used=getattr(response, 'usage', {}).get('total_tokens') if hasattr(response, 'usage') else None
            )
            
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            return LLMResponse(
                success=False,
                result="",
                result_type=request.result_type,
                provider=request.provider,
                error_message=str(e)
            )
    
    async def _generate_google(self, prompt: str, request: LLMRequest) -> Any:
        """Generate content using Google Gemini API."""
        if not self.google_client:
            raise ValueError("Google client not initialized")
        
        try:
            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=request.max_tokens,
                temperature=request.temperature,
            )
            
            response = await asyncio.to_thread(
                self.google_client.generate_content,
                prompt,
                generation_config=generation_config
            )
            return response
        except Exception as e:
            logger.error(f"Google API error: {e}")
            raise
    
    async def _generate_openai(self, prompt: str, request: LLMRequest) -> Any:
        """Generate content using OpenAI API."""
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized")
        
        try:
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model=request.additional_params.get('model', 'gpt-3.5-turbo'),
                messages=[
                    {"role": "system", "content": "You are a helpful educational content generator. Always follow the specified format and requirements."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                response_format={"type": "json_object"} if request.result_type == ResultType.QUIZ_MCQ else None
            )
            return response
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    async def _generate_anthropic(self, prompt: str, request: LLMRequest) -> Any:
        """Generate content using Anthropic API."""
        # Placeholder for Anthropic implementation
        raise NotImplementedError("Anthropic provider not yet implemented")
    
    async def _generate_local(self, prompt: str, request: LLMRequest) -> Any:
        """Generate content using local LLM."""
        # Placeholder for local LLM implementation
        raise NotImplementedError("Local provider not yet implemented")
    
    def _parse_response(self, response: Any, result_type: ResultType) -> Union[Dict[str, Any], str, List[Dict[str, Any]]]:
        """Parse and validate LLM response based on result type."""
        try:
            # Extract content from response based on provider
            if hasattr(response, 'choices') and response.choices:
                # OpenAI response format
                content = response.choices[0].message.content
            elif hasattr(response, 'text'):
                # Google Gemini response format
                content = response.text
            else:
                content = str(response)
            
            # Parse based on result type
            if result_type == ResultType.QUIZ_MCQ:
                # Try to parse as JSON for structured data
                try:
                    if not content or content.strip() == "":
                        logger.warning("Empty content received from LLM")
                        return {"error": "Empty response from LLM", "raw_content": content}
                    
                    # Clean the content - sometimes LLM adds markdown formatting
                    cleaned_content = content.strip()
                    if cleaned_content.startswith("```json"):
                        cleaned_content = cleaned_content.replace("```json", "").replace("```", "").strip()
                    elif cleaned_content.startswith("```"):
                        cleaned_content = cleaned_content.replace("```", "").strip()
                    
                    parsed = json.loads(cleaned_content)
                    # Validate quiz structure
                    quiz = QuizMCQ(**parsed)
                    return quiz.dict()
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"Failed to parse quiz JSON: {e}")
                    logger.warning(f"Raw content: {repr(content)}")
                    return {"error": "Failed to parse quiz format", "raw_content": content, "cleaned_content": cleaned_content if 'cleaned_content' in locals() else content}
            
            elif result_type in [ResultType.EXPLANATION, ResultType.SUMMARY, 
                               ResultType.STORY, ResultType.MEME_DESCRIPTION, 
                               ResultType.ANALOGY, ResultType.CODE_EXAMPLE, 
                               ResultType.STEP_BY_STEP]:
                # Return as formatted text
                return {"content": content, "type": result_type.value}
            
            elif result_type == ResultType.CUSTOM:
                # Try to parse as JSON first, fallback to text
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    return {"content": content, "type": "custom"}
            
            else:
                return {"content": content, "type": result_type.value}
                
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            return {"error": f"Failed to parse response: {str(e)}"}


# Singleton instance
llm_service = LLMService()


# Convenience functions for common use cases
async def generate_quiz(content: str, num_questions: int = 5, difficulty: str = "medium") -> LLMResponse:
    """Generate a multiple choice quiz from content."""
    request = LLMRequest(
        content=content,
        result_type=ResultType.QUIZ_MCQ,
        additional_params={
            "num_questions": num_questions,
            "difficulty": difficulty,
            "num_options": 4
        }
    )
    return await llm_service.generate_content(request)


async def generate_explanation(content: str, style: str = "clear and engaging", audience: str = "general learners") -> LLMResponse:
    """Generate an explanation of the content."""
    request = LLMRequest(
        content=content,
        result_type=ResultType.EXPLANATION,
        additional_params={
            "style": style,
            "audience": audience
        }
    )
    return await llm_service.generate_content(request)


async def generate_story(content: str, audience: str = "students", length: str = "medium") -> LLMResponse:
    """Generate a story that explains the content."""
    request = LLMRequest(
        content=content,
        result_type=ResultType.STORY,
        additional_params={
            "audience": audience,
            "length": length
        }
    )
    return await llm_service.generate_content(request)


async def generate_custom_content(content: str, custom_prompt: str, additional_instructions: str = "") -> LLMResponse:
    """Generate custom content with user-defined prompt."""
    request = LLMRequest(
        content=content,
        result_type=ResultType.CUSTOM,
        additional_params={
            "custom_prompt": custom_prompt,
            "additional_instructions": additional_instructions
        }
    )
    return await llm_service.generate_content(request)
