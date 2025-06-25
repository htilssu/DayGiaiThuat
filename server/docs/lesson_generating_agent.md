# Lesson Generating Agent

## Overview

The Lesson Generating Agent is a RAG (Retrieval-Augmented Generation) AI agent that retrieves relevant information from Pinecone vector store and generates comprehensive lesson content. It's designed to create educational content for programming and algorithm topics.

## Features

- **RAG Integration**: Retrieves relevant context from Pinecone vector store
- **Structured Content Generation**: Creates lessons with multiple sections (text, code, quiz)
- **Contextual Compression**: Uses advanced retrieval techniques for better context extraction
- **Flexible Configuration**: Supports different difficulty levels and lesson types
- **Error Handling**: Robust error handling with fallback content generation

## Architecture

### Components

1. **LessonGeneratingAgent**: Main agent class that orchestrates the generation process
2. **Document Store**: Pinecone vector store integration for context retrieval
3. **LLM Model**: Google Gemini model for content generation
4. **Prompt Templates**: Structured prompts for lesson structure and content generation

### Flow

1. **Context Retrieval**: Query Pinecone for relevant documents
2. **Structure Generation**: Create lesson structure based on retrieved context
3. **Content Generation**: Generate detailed content for each section
4. **Schema Validation**: Validate and return structured lesson data

## Usage

### Basic Usage

```python
from app.core.agents.lesson_generating_agent import LessonGeneratingAgent
from app.schemas.lesson_schema import GenerateLessonRequestSchema

# Create agent
agent = LessonGeneratingAgent()

# Create request
request = GenerateLessonRequestSchema(
    topic_name="Thuật toán sắp xếp",
    lesson_title="Bubble Sort - Thuật toán sắp xếp nổi bọt",
    lesson_description="Học về thuật toán sắp xếp bubble sort",
    difficulty_level="beginner",
    lesson_type="mixed",
    include_examples=True,
    include_exercises=True,
    max_sections=5
)

# Generate lesson
lesson = agent.act(request)
```

### API Usage

```bash
# Generate lesson via API
curl -X POST "http://localhost:8000/lessons/generate?topic_id=1&order=1" \
  -H "Content-Type: application/json" \
  -d '{
    "topic_name": "Thuật toán sắp xếp",
    "lesson_title": "Bubble Sort",
    "lesson_description": "Học về bubble sort",
    "difficulty_level": "beginner",
    "lesson_type": "mixed",
    "include_examples": true,
    "include_exercises": true,
    "max_sections": 5
  }'
```

## Configuration

### Request Parameters

- `topic_name`: Name of the topic (used for context retrieval)
- `lesson_title`: Title of the lesson
- `lesson_description`: Description of the lesson
- `difficulty_level`: "beginner", "intermediate", "advanced"
- `lesson_type`: "theory", "practice", "mixed"
- `include_examples`: Whether to include code examples
- `include_exercises`: Whether to include quiz questions
- `max_sections`: Maximum number of sections to generate

### Environment Variables

Ensure these are set in your environment:

```bash
GOOGLE_API_KEY=your_google_api_key
PINECONE_API_KEY=your_pinecone_api_key
AGENT_LLM_MODEL=gemini-1.5-flash
CREATIVE_LLM_MODEL=gemini-1.5-pro
```

## Output Structure

The agent generates lessons with the following structure:

```json
{
  "external_id": "lesson_topic_name_5",
  "title": "Lesson Title",
  "description": "Lesson Description",
  "topic_id": 1,
  "order": 1,
  "sections": [
    {
      "type": "text",
      "content": "Introduction content...",
      "order": 1
    },
    {
      "type": "code",
      "content": "Code example with explanation...",
      "order": 2
    },
    {
      "type": "quiz",
      "content": "Question content...",
      "options": { "A": "...", "B": "...", "C": "...", "D": "..." },
      "answer": 0,
      "explanation": "Explanation of the answer...",
      "order": 3
    }
  ]
}
```

## Section Types

1. **text**: Theoretical content with explanations
2. **code**: Code examples with detailed explanations
3. **quiz**: Multiple choice questions with options and explanations

## Error Handling

The agent includes comprehensive error handling:

- **Context Retrieval Errors**: Falls back to default context
- **Structure Generation Errors**: Uses basic fallback structure
- **Content Generation Errors**: Provides error messages in content
- **JSON Parsing Errors**: Handles malformed LLM responses

## Testing

Run the test script to verify functionality:

```bash
cd server
python test_lesson_agent.py
```

## Integration

The agent is integrated into the FastAPI application through:

1. **LessonService**: Service layer for database operations
2. **LessonRouter**: API endpoints for lesson management
3. **Database Models**: SQLAlchemy models for persistence

## Dependencies

- `langchain`: LLM framework
- `langchain-google-genai`: Google Gemini integration
- `langchain-pinecone`: Pinecone vector store integration
- `pinecone-client`: Pinecone client library
- `pydantic`: Data validation
- `sqlalchemy`: Database ORM

## Best Practices

1. **Context Quality**: Ensure Pinecone has high-quality, relevant documents
2. **Prompt Engineering**: Fine-tune prompts for better content quality
3. **Error Monitoring**: Monitor generation errors and adjust prompts
4. **Content Review**: Always review generated content before publishing
5. **Rate Limiting**: Implement rate limiting for API endpoints

## Troubleshooting

### Common Issues

1. **No Context Retrieved**: Check Pinecone index and document quality
2. **Poor Content Quality**: Adjust prompts or increase context retrieval
3. **JSON Parsing Errors**: Check LLM response format
4. **API Key Issues**: Verify Google and Pinecone API keys

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```
