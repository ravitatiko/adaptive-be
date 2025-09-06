# Course API Usage Example

This document provides examples of how to use the new Course API endpoints.

## Main Endpoint

The main endpoint you requested is:

```
GET /api/v1/course/{course_id}/assets
```

This endpoint returns a course with all its modules and populated assets.

## Example Usage

### 1. Create an Asset

```bash
curl -X POST "http://localhost:8000/api/v1/course/assets/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "What is Generative AI?",
    "style": "original",
    "content": "<!doctype html><html><body><h1>What is Generative AI?</h1><p>Generative AI is a type of artificial intelligence...</p></body></html>"
  }'
```

### 2. Create a Course with Modules

```bash
curl -X POST "http://localhost:8000/api/v1/course/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Generative AI",
    "modules": [
      {
        "type": "module",
        "assets": ["ASSET_ID_FROM_STEP_1"]
      }
    ]
  }'
```

### 3. Get Course with Populated Assets (Main Endpoint)

```bash
curl -X GET "http://localhost:8000/api/v1/course/COURSE_ID/assets" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Example Response

```json
{
  "_id": "68bc14e817fa5a8d69dc67f5",
  "name": "Generative AI",
  "modules": [
    {
      "type": "module",
      "assets": [
        {
          "_id": "68bc14d817fa5a8d69dc67f4",
          "name": "What is Generative AI?",
          "style": "original",
          "content": "<!doctype html><html><body><h1>What is Generative AI?</h1><p>Generative AI is a type of artificial intelligence...</p></body></html>"
        }
      ]
    }
  ],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

## Authentication

All endpoints require authentication. First, get a token:

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=your_username&password=your_password"
```

Then use the returned token in the Authorization header:

```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## Available Endpoints

| Method  | Endpoint                                | Description                             |
| ------- | --------------------------------------- | --------------------------------------- |
| GET     | `/api/v1/course/`                       | List all courses                        |
| POST    | `/api/v1/course/`                       | Create a new course                     |
| GET     | `/api/v1/course/{course_id}`            | Get a specific course                   |
| PUT     | `/api/v1/course/{course_id}`            | Update a course                         |
| DELETE  | `/api/v1/course/{course_id}`            | Delete a course                         |
| **GET** | **`/api/v1/course/{course_id}/assets`** | **Get course with populated assets** ⭐ |
| GET     | `/api/v1/course/assets/`                | List all assets                         |
| POST    | `/api/v1/course/assets/`                | Create a new asset                      |
| GET     | `/api/v1/course/assets/{asset_id}`      | Get a specific asset                    |
| DELETE  | `/api/v1/course/assets/{asset_id}`      | Delete an asset                         |

## Data Structures

### Course Structure

```json
{
  "_id": "ObjectId",
  "name": "string",
  "modules": [
    {
      "type": "module",
      "assets": ["ObjectId1", "ObjectId2"]
    }
  ],
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Asset Structure

```json
{
  "_id": "ObjectId",
  "name": "string",
  "style": "string",
  "content": "string"
}
```

## Setup Requirements

1. **MongoDB**: Make sure MongoDB is running and configured
2. **Environment Variables**: Set up your `.env` file with MongoDB connection string
3. **Authentication**: Create a user account to get authentication tokens

## MongoDB Configuration

Add to your `.env` file:

```
DATABASE_URL=mongodb://localhost:27017/adaptive_learning
```

Or for MongoDB Atlas:

```
DATABASE_URL=mongodb+srv://username:password@cluster.mongodb.net/adaptive_learning
```
