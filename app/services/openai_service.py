from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from app.config.settings import settings
from app.models.enums import SupportedLanguage


class LanguageDetectionResponse(BaseModel):
    """Response model for language detection with structured output."""
    language: SupportedLanguage
    confidence: float


class OpenAIService:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model=settings.MANAGER_AGENT_MODEL,
            temperature=settings.MANAGER_AGENT_TEMPERATURE,
            max_tokens=settings.MANAGER_AGENT_MAX_TOKENS
        )
        
        # Set up structured output parser
        self.parser = PydanticOutputParser(pydantic_object=LanguageDetectionResponse)
        
        # Create prompt template for language detection
        self.language_prompt = PromptTemplate(
            template="""Analyze the following text and determine which of these supported languages it is written in:
- English (en)
- German (de) 
- Spanish (es)

Text to analyze: {text}

{format_instructions}

Provide a confidence score between 0.0 and 1.0 indicating how certain you are about the language detection.
If the text doesn't clearly match any of the supported languages, default to English.""",
            input_variables=["text"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )

    def detect_language(self, text: str) -> str:
        try:
            # Create the chain
            chain = self.language_prompt | self.llm | self.parser
            
            # Execute the chain
            result = chain.invoke({"text": text})
            
            print(f"🌍 Language detection result: {result.language} (confidence: {result.confidence:.2f})")
            return result.language.value
            
        except Exception as e:
            print(f"Language detection failed: {e}")
            return SupportedLanguage.ENGLISH.value

openai_service = OpenAIService()
