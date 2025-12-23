"""
Gemini AI Service for BAMF Case Management System.

This module provides integration with Google's Gemini API for natural language
processing, document analysis, translation, and form field extraction.

The service uses a singleton pattern for connection pooling to minimize latency
and ensure efficient resource usage.
"""

import logging
import os
import time
from typing import Optional, Dict, Any, AsyncGenerator, Union

import google.generativeai as genai
from google.generativeai.types import GenerationConfig

from backend.services.context_manager import ContextManager

logger = logging.getLogger(__name__)


class GeminiService:
    """
    Service class for interacting with Google Gemini API.

    This service handles all AI-powered functionality including:
    - Natural language chat responses
    - Document summarization and translation
    - Structured data extraction for form filling
    - Context-aware responses based on case information

    The service implements a singleton pattern to maintain a single
    model instance for connection pooling and performance optimization.
    """

    _instance: Optional['GeminiService'] = None
    _model: Optional[Any] = None
    _context_manager: Optional[ContextManager] = None

    def __new__(cls) -> 'GeminiService':
        """
        Implement singleton pattern for GeminiService.

        Ensures only one instance of the service exists throughout
        the application lifecycle.

        Returns:
            GeminiService: The singleton instance.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initialize the Gemini service.

        Configures the Gemini API client using the API key from environment
        variables and initializes the generative model and context manager.

        Raises:
            ValueError: If GEMINI_API_KEY is not found in environment.
        """
        if self._model is None:
            self._initialize_client()
        if self._context_manager is None:
            self._initialize_context_manager()

    def _initialize_client(self) -> None:
        """
        Initialize the Gemini API client and model.

        Loads the API key from environment variables and configures
        the generative model with appropriate settings.

        Raises:
            ValueError: If GEMINI_API_KEY is not configured.
        """
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            logger.error("GEMINI_API_KEY not found in environment variables")
            raise ValueError("API key not configured")

        try:
            # Configure the Gemini API
            genai.configure(api_key=api_key)

            # Initialize the generative model
            # Using gemini-2.5-flash for text generation (fast, cost-effective, latest)
            self._model = genai.GenerativeModel('gemini-2.5-flash')

            logger.info("Gemini service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Gemini service: {str(e)}")
            raise

    def _initialize_context_manager(self) -> None:
        """
        Initialize the context manager for case-instance context loading.

        Creates a ContextManager instance for loading case-level and
        folder-level context from the filesystem.
        """
        try:
            self._context_manager = ContextManager()
            logger.info("Context manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize context manager: {str(e)}")
            raise

    async def generate_response(
        self,
        prompt: str,
        case_id: Optional[str] = None,
        folder_id: Optional[str] = None,
        document_content: Optional[str] = None,
        stream: bool = False
    ) -> Union[str, AsyncGenerator[str, None]]:
        """
        Generate an AI response using Gemini API with case-instance context.

        Processes user prompts with case-specific context loaded from the
        case's context directory. Automatically loads case-level and
        folder-level context based on case_id and folder_id parameters.

        Args:
            prompt: The user's question or instruction.
            case_id: Case identifier for loading case-specific context
                    (e.g., "ACTE-2024-001"). If None, no case context loaded.
            folder_id: Folder identifier for loading folder-specific context
                      (e.g., "personal-data"). If None, only case context loaded.
            document_content: Optional document text to analyze.
            stream: If True, enable streaming responses for real-time delivery.

        Returns:
            Union[str, AsyncGenerator[str, None]]: Complete response text if
                stream=False, or async generator yielding chunks if stream=True.

        Raises:
            ValueError: If the model is not initialized.
            Exception: If the API call fails (rate limit, timeout, etc.).

        Example:
            >>> service = GeminiService()
            >>> # Non-streaming
            >>> response = await service.generate_response(
            ...     prompt="Validate this document",
            ...     case_id="ACTE-2024-001",
            ...     folder_id="personal-data",
            ...     document_content="Birth Certificate: Ahmad Ali..."
            ... )
            >>> # Streaming
            >>> async for chunk in await service.generate_response(
            ...     prompt="Summarize", stream=True
            ... ):
            ...     print(chunk, end='')
        """
        if self._model is None:
            raise ValueError("Gemini model not initialized")

        try:
            # Load and merge context based on case_id and folder_id
            merged_context = None
            if case_id:
                merged_context = self._load_context(
                    case_id,
                    folder_id,
                    document_content
                )

            # Build the complete prompt with context and document content
            full_prompt = self._build_prompt(prompt, document_content, merged_context)

            logger.info(
                f"Generating response - "
                f"prompt_length: {len(prompt)}, "
                f"case_id: {case_id or 'none'}, "
                f"stream: {stream}"
            )

            # Configure generation parameters
            generation_config = GenerationConfig(
                temperature=0.7,
                top_p=0.8,
                top_k=40,
                max_output_tokens=2048,
            )

            # Start timing for performance metrics
            start_time = time.perf_counter()
            first_token_time = None

            if stream:
                # Return async generator for streaming mode
                return self._generate_streaming_response(
                    full_prompt,
                    generation_config,
                    start_time,
                    case_id
                )
            else:
                # Non-streaming mode - return complete response
                response = self._model.generate_content(
                    full_prompt,
                    generation_config=generation_config
                )

                # Extract text from response
                response_text = response.text

                # Calculate performance metrics
                end_time = time.perf_counter()
                latency_ms = (end_time - start_time) * 1000
                token_count = len(response_text.split())

                # Log performance metrics
                logger.info(
                    f"Response complete - "
                    f"latency: {latency_ms:.2f}ms, "
                    f"tokens: {token_count}, "
                    f"case_id: {case_id or 'none'}, "
                    f"response_length: {len(response_text)}"
                )

                return response_text

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")

            # Provide user-friendly error messages
            if "quota" in str(e).lower() or "rate" in str(e).lower():
                raise Exception("Service temporarily busy, please try again in a moment")
            elif "timeout" in str(e).lower():
                raise Exception("Request timed out, please try again")
            else:
                raise Exception(f"Failed to generate response: {str(e)}")

    async def _generate_streaming_response(
        self,
        full_prompt: str,
        generation_config: GenerationConfig,
        start_time: float,
        case_id: Optional[str]
    ) -> AsyncGenerator[str, None]:
        """
        Generate streaming response with performance metrics.

        Args:
            full_prompt: Complete prompt with context.
            generation_config: Gemini generation configuration.
            start_time: Request start time for metrics.
            case_id: Case identifier for logging.

        Yields:
            str: Response text chunks as they arrive.

        Raises:
            Exception: If streaming fails.
        """
        try:
            first_token_time = None
            total_tokens = 0
            full_response = []

            # Generate streaming response
            response = self._model.generate_content(
                full_prompt,
                generation_config=generation_config,
                stream=True
            )

            # Yield chunks as they arrive
            for chunk in response:
                if chunk.text:
                    # Record first token timing
                    if first_token_time is None:
                        first_token_time = time.perf_counter()
                        time_to_first_token_ms = (first_token_time - start_time) * 1000
                        logger.info(
                            f"First token received - "
                            f"latency: {time_to_first_token_ms:.2f}ms, "
                            f"case_id: {case_id or 'none'}"
                        )

                    full_response.append(chunk.text)
                    total_tokens += len(chunk.text.split())
                    yield chunk.text

            # Log final metrics
            end_time = time.perf_counter()
            total_latency_ms = (end_time - start_time) * 1000
            response_text = ''.join(full_response)

            logger.info(
                f"Streaming complete - "
                f"total_latency: {total_latency_ms:.2f}ms, "
                f"first_token_latency: {(first_token_time - start_time) * 1000:.2f}ms, "
                f"tokens: {total_tokens}, "
                f"case_id: {case_id or 'none'}, "
                f"response_length: {len(response_text)}"
            )

        except Exception as e:
            logger.error(f"Error in streaming response: {str(e)}")
            raise

    def _load_context(
        self,
        case_id: str,
        folder_id: Optional[str] = None,
        document_content: Optional[str] = None
    ) -> Optional[str]:
        """
        Load and merge case-instance context.

        Loads case-level context, folder-level context (if folder_id provided),
        and merges with document content to create a comprehensive context
        string for the AI prompt.

        Args:
            case_id: Case identifier (e.g., "ACTE-2024-001").
            folder_id: Optional folder identifier (e.g., "personal-data").
            document_content: Optional document text.

        Returns:
            Optional[str]: Merged context string, or None if context
                          loading fails.
        """
        if not self._context_manager:
            logger.warning("Context manager not initialized, skipping context load")
            return None

        try:
            # Load case context
            case_ctx = None
            try:
                case_ctx = self._context_manager.load_case_context(case_id)
                logger.info(f"Loaded case context for: {case_id}")
            except FileNotFoundError:
                logger.warning(f"Case context not found for: {case_id}")
            except Exception as e:
                logger.error(f"Error loading case context: {str(e)}")

            # Load folder context if folder_id provided
            folder_ctx = None
            if folder_id:
                try:
                    folder_ctx = self._context_manager.load_folder_context(
                        case_id,
                        folder_id
                    )
                    if folder_ctx:
                        logger.info(
                            f"Loaded folder context for: {case_id}/{folder_id}"
                        )
                except Exception as e:
                    logger.error(f"Error loading folder context: {str(e)}")

            # Merge contexts
            merged_context = self._context_manager.merge_contexts(
                case_ctx,
                folder_ctx,
                document_content
            )

            return merged_context

        except Exception as e:
            logger.error(f"Failed to load context: {str(e)}")
            return None

    def _build_prompt(
        self,
        prompt: str,
        document_content: Optional[str] = None,
        context: Optional[str] = None,
        context_sources: Optional[list] = None
    ) -> str:
        """
        S2-004: Build a complete prompt with context, document content, and source labels.

        Combines user prompt, case context, and document content into
        a well-structured prompt for the AI model. Enhanced with source
        tracking for AI transparency.

        Args:
            prompt: The user's question or instruction.
            document_content: Optional document text to include.
            context: Optional case/folder context information.
            context_sources: Optional list of context sources for transparency.

        Returns:
            str: The complete formatted prompt with source labels.
        """
        parts = []

        # S2-004: Add system instructions for source citation
        parts.append("# System Instructions")
        parts.append("You are an AI assistant helping with case management.")
        parts.append("When answering questions, cite your sources when the information")
        parts.append("comes from the provided context (case, folder, or document).")
        parts.append("Use format: [Source: <source_name>] when citing specific information.")
        parts.append("")

        # S2-004: Add context sources summary if provided
        if context_sources:
            parts.append("# Available Context Sources")
            for source in context_sources:
                parts.append(f"  - {source}")
            parts.append("")

        # Add context if provided
        if context:
            parts.append("# Case Context")
            parts.append("(Information from case configuration and folder settings)")
            parts.append(context)
            parts.append("")

        # Add document content if provided (highest priority source)
        if document_content:
            parts.append("# Document Content")
            parts.append("(Primary source - extracted from uploaded document)")
            parts.append(document_content)
            parts.append("")

        # Add user prompt
        parts.append("# User Request")
        parts.append(prompt)

        # S2-004: Append source citation reminder
        parts.append("")
        parts.append("# Response Guidelines")
        parts.append("- Answer the user's request based on the provided context")
        parts.append("- When information comes from a specific source, cite it")
        parts.append("- If information is not found in the context, say so clearly")

        return "\n".join(parts)

    def is_initialized(self) -> bool:
        """
        Check if the Gemini service is properly initialized.

        Returns:
            bool: True if the service is ready to use, False otherwise.
        """
        return self._model is not None
