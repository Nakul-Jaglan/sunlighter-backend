from fastapi import APIRouter

from app.api.api_v1.endpoints import auth, users, employments, verification_codes, access_logs

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(employments.router, prefix="/employments", tags=["employments"])
api_router.include_router(verification_codes.router, prefix="/verification-codes", tags=["verification-codes"])
api_router.include_router(access_logs.router, prefix="/access-logs", tags=["access-logs"])
