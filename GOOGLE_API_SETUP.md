# Google API Setup for Text Summarization

## Getting Your Google API Key

1. **Go to Google AI Studio**

   - Visit: https://aistudio.google.com/
   - Sign in with your Google account

2. **Create an API Key**

   - Click on "Get API Key" in the left sidebar
   - Click "Create API Key"
   - Choose "Create API key in new project" or select an existing project
   - Copy the generated API key

3. **Set up your environment**
   - Copy `env.example` to `.env`:
     ```bash
     cp env.example .env
     ```
   - Edit `.env` and replace `your-google-api-key-here` with your actual API key:
     ```
     GOOGLE_API_KEY=your-actual-api-key-here
     ```

## Testing the API

1. **Install dependencies** (if not already done):

   ```bash
   pip install -r requirements.txt
   ```

2. **Start the server**:

   ```bash
   python run.py
   ```

3. **Test the endpoints**:
   - Visit: http://localhost:8000/docs
   - Or run the test script: `python test_summary_api.py`

## Available Endpoints

- `POST /api/v1/summary/summarize` - Summarize text
- `POST /api/v1/summary/key-points` - Extract key points
- `POST /api/v1/summary/sentiment` - Analyze sentiment
- `POST /api/v1/summary/analyze` - Comprehensive text analysis
- `GET /api/v1/summary/health` - Health check

## Example Usage

### Using curl:

```bash
curl -X POST "http://localhost:8000/api/v1/summary/summarize" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Your text to summarize here...",
       "max_length": 50,
       "style": "concise"
     }'
```

### Using Python:

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/summary/summarize",
    json={
        "text": "Your text to summarize here...",
        "max_length": 50,
        "style": "concise"
    }
)

print(response.json())
```

## Troubleshooting

- **404 Model Error**: Make sure you're using a valid Google API key
- **Connection Error**: Ensure the FastAPI server is running on port 8000
- **API Key Error**: Verify your API key is correctly set in the `.env` file
