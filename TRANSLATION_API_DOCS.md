# Translation API Documentation

## Overview

The Translation API provides educational content translation services using Google Gemini AI. It supports translating content from English to Hindi and Telugu, with specialized prompts for educational content.

## Features

- **Language Support**: English (en), Hindi (hi), Telugu (te)
- **Educational Focus**: Specialized prompts for educational content translation
- **Database Integration**: Stores translations in the same assets collection
- **Batch Processing**: Support for translating multiple assets at once
- **Authentication**: All endpoints require user authentication (except test endpoints)

## Database Schema

### Assets Collection (Extended)

```json
{
  "_id": "ObjectId",
  "name": "Asset Name",
  "style": "original",
  "content": "HTML content...",
  "code": "ASSET_CODE_001",
  "language": "en|hi|te",
  "source_asset_id": "ObjectId (for translations)",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## API Endpoints

### 1. Translate Asset

**POST** `/api/v1/translations/translate`

Translates an asset's content to the specified language.

**Request Body:**

```json
{
  "asset_code": "GEN_AI_001",
  "target_language": "hi",
  "content": "<h1>Generative AI</h1><p>Content to translate...</p>"
}
```

**Response:**

```json
{
  "_id": "68bc206f62e053d8ddd4103f",
  "name": "Asset Name",
  "style": "original",
  "content": "Translated content...",
  "code": "GEN_AI_001",
  "language": "hi",
  "source_asset_id": "68bc206f62e053d8ddd4102e",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### 2. Get Asset Translations

**GET** `/api/v1/translations/asset/{asset_code}/translations`

Gets all available translations for a specific asset.

**Response:**

```json
{
  "asset_code": "GEN_AI_001",
  "available_languages": ["en", "hi", "te"],
  "translations": {
    "en": {
      "id": "68bc206f62e053d8ddd4102e",
      "name": "Asset Name",
      "content": "Original content...",
      "language": "en"
    },
    "hi": {
      "id": "68bc206f62e053d8ddd4103f",
      "name": "Asset Name",
      "content": "Hindi content...",
      "language": "hi"
    }
  }
}
```

### 3. Get Asset by Language

**GET** `/api/v1/translations/asset/{asset_code}/language/{language}`

Gets a specific asset in a specific language.

**Response:**

```json
{
  "_id": "68bc206f62e053d8ddd4103f",
  "name": "Asset Name",
  "content": "Content in specified language...",
  "code": "GEN_AI_001",
  "language": "hi"
}
```

### 4. Batch Translation

**POST** `/api/v1/translations/translate/batch`

Translates multiple assets in batch.

**Request Body:**

```json
[
  {
    "asset_code": "GEN_AI_001",
    "target_language": "hi",
    "content": "Content 1..."
  },
  {
    "asset_code": "GEN_AI_002",
    "target_language": "te",
    "content": "Content 2..."
  }
]
```

**Response:**

```json
{
    "total_requests": 2,
    "successful": 1,
    "failed": 1,
    "results": [
        {
            "asset_code": "GEN_AI_001",
            "target_language": "hi",
            "status": "success",
            "translation": {...}
        },
        {
            "asset_code": "GEN_AI_002",
            "target_language": "te",
            "status": "error",
            "error": "Error message"
        }
    ]
}
```

## Test Endpoints (No Authentication)

### Test Translation

**POST** `/test-translate`

Test endpoint for translation without authentication.

**Parameters:**

- `asset_code`: Asset code
- `target_language`: Target language (hi/te)
- `content`: Content to translate

## Educational Translator Prompt

The API uses a specialized prompt for educational content translation:

```
You are an expert educational content creator and translator specializing in translating educational materials while maintaining their instructional value and clarity.

TASK: Translate the following educational content from English to [TARGET_LANGUAGE].

TRANSLATION GUIDELINES:
1. Maintain the educational structure and flow
2. Preserve technical terms and concepts accurately
3. Use appropriate educational terminology in [TARGET_LANGUAGE]
4. Keep the same HTML structure and formatting
5. Ensure the translation is natural and easy to understand for students
6. Maintain the same level of formality and tone
```

## Setup Instructions

### 1. Environment Variables

```bash
export GOOGLE_API_KEY="your_google_gemini_api_key"
export DATABASE_URL="mongodb://localhost:27017/adaptive_learning"
```

### 2. Install Dependencies

```bash
pip install google-generativeai
```

### 3. Start MongoDB

```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

### 4. Start the Server

```bash
python3 -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Usage Examples

### cURL Examples

#### Translate to Hindi

```bash
curl -X POST "http://localhost:8000/test-translate" \
  -d "asset_code=GEN_AI_001" \
  -d "target_language=hi" \
  -d "content=<h1>Generative AI</h1><p>This is educational content about AI.</p>"
```

#### Translate to Telugu

```bash
curl -X POST "http://localhost:8000/test-translate" \
  -d "asset_code=GEN_AI_001" \
  -d "target_language=te" \
  -d "content=<h1>Generative AI</h1><p>This is educational content about AI.</p>"
```

#### Get Available Translations

```bash
curl -X GET "http://localhost:8000/api/v1/translations/asset/GEN_AI_001/translations" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Error Handling

### Common Errors

1. **Invalid Language**: `Target language must be 'hi' (Hindi) or 'te' (Telugu)`
2. **Missing API Key**: `GOOGLE_API_KEY environment variable not set`
3. **Asset Not Found**: `Original asset with code 'ASSET_CODE' not found`
4. **Translation Exists**: `Translation for asset 'ASSET_CODE' in language 'hi' already exists`

### Error Response Format

```json
{
  "detail": "Error message",
  "status_code": 400
}
```

## Testing

### Test Structure

```bash
python3 test_translation_structure.py
```

### Test Translation API

```bash
python3 test_translation_api.py
```

## Integration with Course API

The translation API integrates seamlessly with the existing course API:

1. **Asset Codes**: Uses the same asset codes from the course system
2. **Database**: Stores translations in the same assets collection
3. **Language Support**: Extends the course API with multi-language support
4. **User Progress**: Can be combined with user progress tracking

## Future Enhancements

- [ ] Support for more languages
- [ ] Translation quality scoring
- [ ] Caching for improved performance
- [ ] Translation history tracking
- [ ] Custom translation prompts per course
- [ ] Real-time translation updates
