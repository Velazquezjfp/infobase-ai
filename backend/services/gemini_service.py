"""
Gemini AI Service for BAMF Case Management System.

This module historically wrapped Google's Gemini API directly. As of
S001-F-001 it delegates every model call to backend.services.llm_provider so
the same code path serves both the closed-environment LiteLLM backend and the
opt-in external Gemini backend without changes to its callers. The class name
GeminiService is preserved to avoid touching dozens of import sites; rename
is tracked as a follow-up.

The service still uses a singleton pattern for connection pooling to minimize
latency and ensure efficient resource usage.
"""

import logging
import time
import json
from typing import Optional, Dict, Any, AsyncGenerator, Union, Tuple, List

from markdownify import markdownify

from backend.services.context_manager import ContextManager
from backend.services.conversation_manager import get_conversation_manager
from backend.services.llm_provider import LLMProvider, get_provider
from backend.config import ENABLE_CHAT_HISTORY

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
    _provider: Optional[LLMProvider] = None
    _context_manager: Optional[ContextManager] = None
    _conversation_manager: Optional[Any] = None

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
        Initialize the service.

        Resolves the active LLM provider via llm_provider.get_provider() and
        wires up context/conversation managers. Provider selection is driven
        by LLM_BACKEND.
        """
        if self._provider is None:
            self._initialize_client()
        if self._context_manager is None:
            self._initialize_context_manager()
        if self._conversation_manager is None:
            self._initialize_conversation_manager()

    def _initialize_client(self) -> None:
        """
        Resolve the active LLM provider and store it on the instance.

        Raises whatever the provider raises (ValueError on misconfigured
        LLM_BACKEND, missing GEMINI_API_KEY for the external backend, etc.).
        """
        try:
            self._provider = get_provider()
            logger.info(
                "GeminiService bound to provider: %s",
                type(self._provider).__name__,
            )
        except Exception as e:
            logger.error(f"Failed to initialize LLM provider: {str(e)}")
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

    def _initialize_conversation_manager(self) -> None:
        """
        Initialize the conversation manager for chat history (S5-010).

        Creates a ConversationManager instance for managing in-memory
        conversation history when ENABLE_CHAT_HISTORY is enabled.
        """
        try:
            self._conversation_manager = get_conversation_manager()
            logger.info(
                f"Conversation manager initialized "
                f"(chat history: {'enabled' if ENABLE_CHAT_HISTORY else 'disabled'})"
            )
        except Exception as e:
            logger.error(f"Failed to initialize conversation manager: {str(e)}")
            raise

    async def generate_response(
        self,
        prompt: str,
        case_id: Optional[str] = None,
        folder_id: Optional[str] = None,
        document_content: Optional[str] = None,
        stream: bool = False,
        language: str = 'de'
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
            language: Language code ('de' or 'en') for AI response language (S5-014).

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
        if self._provider is None:
            raise ValueError("LLM provider not initialized")

        try:
            # Load and merge context based on case_id and folder_id
            # S5-011: Now returns both merged_context and document_tree
            merged_context = None
            document_tree = None
            if case_id:
                merged_context, document_tree = self._load_context(
                    case_id,
                    folder_id,
                    document_content
                )

            # S5-010: Get conversation history if enabled
            conversation_history = []
            if ENABLE_CHAT_HISTORY and case_id and self._conversation_manager:
                conversation_history = self._conversation_manager.prepare_history_for_prompt(case_id)
                if conversation_history:
                    logger.info(
                        f"Including conversation history: {len(conversation_history)} messages "
                        f"for case {case_id}"
                    )

            # S5-011: Build the complete prompt with context, document content, conversation history, language, and tree view
            full_prompt = self._build_prompt(
                prompt,
                document_content,
                merged_context,
                conversation_history=conversation_history,
                language=language,
                document_tree=document_tree
            )

            logger.info(
                f"Generating response - "
                f"prompt_length: {len(prompt)}, "
                f"case_id: {case_id or 'none'}, "
                f"stream: {stream}"
            )

            # Provider-neutral generation parameters; LLMProvider
            # implementations translate these to backend-specific kwargs.
            gen_kwargs = dict(
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
                # S5-010: Pass prompt for conversation history saving
                return self._generate_streaming_response(
                    full_prompt,
                    gen_kwargs,
                    start_time,
                    case_id,
                    user_prompt=prompt
                )
            else:
                # Non-streaming mode - return complete response
                response_text = await self._provider.generate(
                    full_prompt, **gen_kwargs
                )

                # S5-009: Format response (HTML to markdown, JSON to tables)
                formatted_response = self.format_response(response_text)

                # S5-010: Save conversation history if enabled
                if ENABLE_CHAT_HISTORY and case_id and self._conversation_manager:
                    self._conversation_manager.add_message(case_id, "user", prompt)
                    self._conversation_manager.add_message(case_id, "assistant", formatted_response)
                    logger.debug(f"Saved conversation turn to history for case {case_id}")

                # Calculate performance metrics
                end_time = time.perf_counter()
                latency_ms = (end_time - start_time) * 1000
                token_count = len(formatted_response.split())

                # Log performance metrics
                logger.info(
                    f"Response complete - "
                    f"latency: {latency_ms:.2f}ms, "
                    f"tokens: {token_count}, "
                    f"case_id: {case_id or 'none'}, "
                    f"response_length: {len(formatted_response)}"
                )

                return formatted_response

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
        gen_kwargs: Dict[str, Any],
        start_time: float,
        case_id: Optional[str],
        user_prompt: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        Generate streaming response with performance metrics.

        Args:
            full_prompt: Complete prompt with context.
            gen_kwargs: Provider-neutral generation kwargs (temperature etc.).
            start_time: Request start time for metrics.
            case_id: Case identifier for logging.
            user_prompt: Original user prompt (for conversation history, S5-010).

        Yields:
            str: Response text chunks as they arrive.

        Raises:
            Exception: If streaming fails.
        """
        try:
            first_token_time = None
            total_tokens = 0
            full_response = []

            # Yield chunks as they arrive from the provider
            async for chunk_text in self._provider.generate_streaming(
                full_prompt, **gen_kwargs
            ):
                if not chunk_text:
                    continue
                # Record first token timing
                if first_token_time is None:
                    first_token_time = time.perf_counter()
                    time_to_first_token_ms = (first_token_time - start_time) * 1000
                    logger.info(
                        f"First token received - "
                        f"latency: {time_to_first_token_ms:.2f}ms, "
                        f"case_id: {case_id or 'none'}"
                    )

                full_response.append(chunk_text)
                total_tokens += len(chunk_text.split())
                yield chunk_text

            # Log final metrics
            end_time = time.perf_counter()
            total_latency_ms = (end_time - start_time) * 1000
            response_text = ''.join(full_response)
            ttft_ms = (first_token_time - start_time) * 1000 if first_token_time else 0.0

            logger.info(
                f"Streaming complete - "
                f"total_latency: {total_latency_ms:.2f}ms, "
                f"first_token_latency: {ttft_ms:.2f}ms, "
                f"tokens: {total_tokens}, "
                f"case_id: {case_id or 'none'}, "
                f"response_length: {len(response_text)}"
            )

            # S5-010: Save conversation history if enabled
            if ENABLE_CHAT_HISTORY and case_id and user_prompt and self._conversation_manager:
                self._conversation_manager.add_message(case_id, "user", user_prompt)
                self._conversation_manager.add_message(case_id, "assistant", response_text)
                logger.debug(f"Saved streaming conversation turn to history for case {case_id}")

        except Exception as e:
            logger.error(f"Error in streaming response: {str(e)}")
            raise

    def _load_context(
        self,
        case_id: str,
        folder_id: Optional[str] = None,
        document_content: Optional[str] = None
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Load and merge case-instance context.
        S5-011: Enhanced to return document tree view separately.

        Loads case-level context, folder-level context (if folder_id provided),
        and merges with document content to create a comprehensive context
        string for the AI prompt. Also extracts the document tree view for
        separate inclusion in the prompt.

        Args:
            case_id: Case identifier (e.g., "ACTE-2024-001").
            folder_id: Optional folder identifier (e.g., "personal-data").
            document_content: Optional document text.

        Returns:
            Tuple[Optional[str], Optional[str]]: (merged_context, document_tree_view)
                          Returns (None, None) if context loading fails.
        """
        if not self._context_manager:
            logger.warning("Context manager not initialized, skipping context load")
            return None, None

        try:
            # Load case context
            case_ctx = None
            document_tree = None
            try:
                case_ctx = self._context_manager.load_case_context(case_id)
                logger.info(f"Loaded case context for: {case_id}")

                # S5-011: Extract document tree view if present
                if case_ctx and 'documentTreeView' in case_ctx:
                    document_tree = case_ctx.get('documentTreeView')
                    logger.debug(f"Extracted document tree view for {case_id}")

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

            # Inject pre-extracted regulation texts (offline content grounding).
            # When an operator has pre-populated extractedText on a regulation
            # entry in case.json, include it in the prompt so the LLM can answer
            # questions about that regulation's substance. The URL is kept only as
            # a citation marker; no live HTTP fetch is made.
            if case_ctx and 'regulations' in case_ctx:
                reg_sections: list[str] = []
                for reg in case_ctx['regulations']:
                    text = reg.get('extractedText')
                    if text:
                        url_citation = reg.get('url', 'N/A')
                        reg_id = reg.get('id', 'unknown')
                        reg_sections.append(
                            f"  [{reg_id}] (source: {url_citation})\n  {text}"
                        )
                if reg_sections:
                    extra = "\n=== REGULATION CONTENT (pre-extracted) ===\n"
                    extra += "\n\n".join(reg_sections) + "\n"
                    merged_context = (merged_context or "") + extra

            return merged_context, document_tree

        except Exception as e:
            logger.error(f"Failed to load context: {str(e)}")
            return None, None

    def _build_prompt(
        self,
        prompt: str,
        document_content: Optional[str] = None,
        context: Optional[str] = None,
        context_sources: Optional[list] = None,
        conversation_history: Optional[list] = None,
        language: str = 'de',
        document_tree: Optional[str] = None
    ) -> str:
        """
        S2-004: Build a complete prompt with context, document content, and source labels.
        S5-010: Enhanced with conversation history support.
        S5-011: Enhanced with document tree view for global document awareness.
        S5-014: Enhanced with language parameter for AI response language.

        Combines user prompt, case context, document content, conversation
        history, and document tree view into a well-structured prompt for the AI model.
        Enhanced with source tracking for AI transparency and language-specific responses.

        Args:
            prompt: The user's question or instruction.
            document_content: Optional document text to include.
            context: Optional case/folder context information.
            context_sources: Optional list of context sources for transparency.
            conversation_history: Optional list of previous conversation turns (S5-010).
            language: Language code ('de' or 'en') for AI response language (S5-014).
            document_tree: Optional document tree view for document awareness (S5-011).

        Returns:
            str: The complete formatted prompt with source labels and history.
        """
        parts = []

        # S2-004: Add system instructions for source citation
        # S5-014: Add language instruction based on parameter
        language_name = 'German' if language == 'de' else 'English'
        parts.append("# System Instructions")
        parts.append("You are an AI assistant helping with case management.")
        parts.append(f"IMPORTANT: Respond in {language_name} language.")
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

        # S5-011: Add document tree view if provided
        if document_tree:
            parts.append("# Available Documents (Tree View)")
            parts.append("(Complete overview of all documents in this case)")
            parts.append(document_tree)
            parts.append("")
            parts.append("IMPORTANT: Use this tree view to:")
            parts.append("- Answer questions about what documents are available")
            parts.append("- Locate specific documents by name or type")
            parts.append("- Correct user misconceptions (e.g., if user says 'I don't have X' but X exists in tree)")
            parts.append("- Understand document organization in folders")
            parts.append("")

        # Add document content if provided (highest priority source)
        if document_content:
            parts.append("# Document Content")
            parts.append("(Primary source - extracted from uploaded document)")
            parts.append(document_content)
            parts.append("")

        # S5-010: Add conversation history if provided
        if conversation_history:
            parts.append("# Conversation History")
            parts.append("(Previous messages in this conversation)")
            for msg in conversation_history:
                role_label = "User" if msg["role"] == "user" else "Assistant"
                parts.append(f"{role_label}: {msg['content']}")
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

    def _is_json_data(self, text: str) -> bool:
        """
        Detect if text contains JSON data structures.

        Checks for JSON object or array patterns in the text.

        Args:
            text: Text content to check.

        Returns:
            bool: True if JSON data is detected.
        """
        text = text.strip()
        # Check for JSON object or array patterns
        return (
            (text.startswith('{') and text.endswith('}')) or
            (text.startswith('[') and text.endswith(']'))
        )

    def _format_json_as_markdown_table(self, json_str: str) -> str:
        """
        Convert JSON data to markdown table format.

        Transforms JSON objects or arrays into markdown tables
        for better readability in chat responses.

        Args:
            json_str: JSON formatted string.

        Returns:
            str: Markdown table representation of the JSON data.
        """
        try:
            data = json.loads(json_str)

            # Handle array of objects (most common case for tables)
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                # Get headers from first object
                headers = list(data[0].keys())

                # Build markdown table
                lines = []
                lines.append('| ' + ' | '.join(headers) + ' |')
                lines.append('| ' + ' | '.join(['---'] * len(headers)) + ' |')

                for item in data:
                    row = [str(item.get(h, '')) for h in headers]
                    lines.append('| ' + ' | '.join(row) + ' |')

                return '\n'.join(lines)

            # Handle single object as key-value table
            elif isinstance(data, dict):
                lines = []
                lines.append('| Property | Value |')
                lines.append('| --- | --- |')

                for key, value in data.items():
                    lines.append(f'| {key} | {value} |')

                return '\n'.join(lines)

            # For other types, return as-is
            return json_str

        except json.JSONDecodeError:
            # If not valid JSON, return as-is
            return json_str
        except Exception as e:
            logger.warning(f"Error formatting JSON as table: {str(e)}")
            return json_str

    def format_response(self, raw_response: str) -> str:
        """
        S5-009: Format AI response by converting HTML to Markdown if needed.

        Processes raw AI responses to ensure proper markdown formatting
        and structured data presentation. Converts HTML to markdown and
        transforms JSON data into readable tables.

        Args:
            raw_response: Raw response text from Gemini API.

        Returns:
            str: Formatted response in markdown format.

        Example:
            >>> service = GeminiService()
            >>> formatted = service.format_response("<p>Hello <strong>world</strong></p>")
            >>> print(formatted)
            Hello **world**
        """
        response = raw_response

        # Convert HTML to Markdown if HTML detected
        if '<p>' in response or '<ul>' in response or '<div>' in response:
            try:
                response = markdownify(
                    response,
                    heading_style="ATX",  # Use # style headings
                    bullets="-",  # Use - for bullet points
                    strip=['script', 'style']  # Remove dangerous elements
                )
                logger.debug("Converted HTML response to markdown")
            except Exception as e:
                logger.warning(f"Failed to convert HTML to markdown: {str(e)}")
                # Continue with original response if conversion fails

        # Convert JSON data to markdown table if applicable
        if self._is_json_data(response):
            try:
                table_response = self._format_json_as_markdown_table(response)
                if table_response != response:  # If conversion was successful
                    response = table_response
                    logger.debug("Converted JSON data to markdown table")
            except Exception as e:
                logger.warning(f"Failed to format JSON as table: {str(e)}")
                # Continue with original response if conversion fails

        return response

    async def semantic_search(
        self,
        query: str,
        document_text: str,
        query_lang: str = 'en',
        doc_lang: str = 'en'
    ) -> List[Dict[str, Any]]:
        """
        S5-003: Perform semantic search using Gemini API.

        Analyzes a document and finds all passages relevant to the user's query
        using semantic understanding. Supports cross-language search where the
        query and document can be in different languages.

        Args:
            query: The search query in natural language
            document_text: The full text content of the document to search
            query_lang: Language code of the query (ISO 639-1: en, de, etc.)
            doc_lang: Language code of the document (ISO 639-1: en, de, etc.)

        Returns:
            List[Dict[str, Any]]: List of highlight dictionaries with:
                - matched_text: Exact text from document
                - start_position: Character index where match starts
                - end_position: Character index where match ends
                - relevance_score: Float 0.0-1.0 indicating match quality
                - context: Brief explanation of why this matches

        Raises:
            ValueError: If model is not initialized
            Exception: If API call fails

        Example:
            >>> service = GeminiService()
            >>> highlights = await service.semantic_search(
            ...     query="passport number",
            ...     document_text="Reisepassnummer: 123456789",
            ...     query_lang="en",
            ...     doc_lang="de"
            ... )
            >>> print(highlights[0]['matched_text'])
            Reisepassnummer: 123456789
        """
        if self._provider is None:
            raise ValueError("LLM provider not initialized")

        try:
            # Build the semantic search prompt
            prompt = f"""Analyze the following document and find all passages relevant to the user's query.

Query (in {query_lang}): {query}

Document (in {doc_lang}):
{document_text}

Return a JSON array of all relevant text passages with their exact positions in the document.
If the query and document languages differ, match by semantic meaning, not literal translation.

Important Instructions:
- Find the EXACT text from the document (character-perfect match)
- Calculate precise character positions (0-indexed)
- Assign relevance scores from 0.0 to 1.0
- Provide brief context explaining why each passage matches
- Return empty array [] if no matches found

Format:
[
  {{
    "matched_text": "exact text from document",
    "start_position": 0,
    "end_position": 25,
    "relevance_score": 0.95,
    "context": "brief explanation of why this matches"
  }}
]

Return ONLY the JSON array, no additional text."""

            logger.info(
                f"Performing semantic search - "
                f"query: '{query}' ({query_lang}), "
                f"document length: {len(document_text)} chars ({doc_lang})"
            )

            # Lower temperature for deterministic outputs
            start_time = time.perf_counter()
            response_text = await self._provider.generate(
                prompt,
                temperature=0.3,
                top_p=0.8,
                top_k=40,
                max_output_tokens=2048,
            )
            response_text = (response_text or "").strip()

            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                # Remove ```json and ``` markers
                response_text = response_text.replace('```json', '').replace('```', '').strip()

            # Parse JSON response
            highlights = json.loads(response_text)

            # Validate response is an array
            if not isinstance(highlights, list):
                logger.warning(f"Gemini returned non-array response: {type(highlights)}")
                highlights = []

            # Validate and clean highlight objects
            cleaned_highlights = []
            for h in highlights:
                if not isinstance(h, dict):
                    continue

                # Ensure all required fields exist
                if not all(k in h for k in ['matched_text', 'start_position', 'end_position']):
                    logger.warning(f"Skipping malformed highlight: {h}")
                    continue

                # Add default relevance and context if missing
                if 'relevance_score' not in h:
                    h['relevance_score'] = 0.5

                if 'context' not in h:
                    h['context'] = 'Semantic match'

                cleaned_highlights.append(h)

            # Calculate performance metrics
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000

            logger.info(
                f"Semantic search complete - "
                f"found {len(cleaned_highlights)} matches, "
                f"latency: {latency_ms:.2f}ms"
            )

            return cleaned_highlights

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini JSON response: {str(e)}")
            logger.error(f"Raw response: {response_text[:500]}")
            # Return empty results on parse error
            return []

        except Exception as e:
            logger.error(f"Error in semantic search: {str(e)}")
            raise

    def is_initialized(self) -> bool:
        """
        Check whether the underlying LLM provider has the configuration it
        needs to serve requests.

        Returns:
            bool: True if the provider is ready, False otherwise.
        """
        return self._provider is not None and self._provider.is_initialized()
