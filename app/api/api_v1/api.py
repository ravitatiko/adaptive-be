from fastapi import APIRouter

from app.api.api_v1.endpoints import users, items, auth, learning_resources, summary, users_collection, content_transformer, courses, translations, llm, quiz, asset_summary


api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(learning_resources.router, prefix="/learning-resources", tags=["learning-resources"])
api_router.include_router(summary.router, prefix="/summary", tags=["text-analysis"])
api_router.include_router(users_collection.router, prefix="/users-collection", tags=["users-collection"])
api_router.include_router(content_transformer.router, prefix="/content-transformer", tags=["content-transformer"])
api_router.include_router(courses.router, prefix="/course", tags=["courses"])

api_router.include_router(llm.router, prefix="/llm", tags=["llm"])
api_router.include_router(quiz.router, prefix="/quiz", tags=["quiz"])

api_router.include_router(translations.router, prefix="/translations", tags=["translations"])
api_router.include_router(asset_summary.router, prefix="/asset-summary", tags=["asset-summary"])

