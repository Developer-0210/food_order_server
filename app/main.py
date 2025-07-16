from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import superuser, admin_auth, menu, table, order, qr, otp

app = FastAPI(title="Multi-Tenant Food Ordering API")

# ✅ CORS configuration
origins = [
    "https://food-order-client-2pir.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or use ["*"] in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ⚠️ DO NOT include this if you're using Alembic for migrations:
# from app.db import Base, engine
# Base.metadata.create_all(bind=engine)

# ✅ API Routers
app.include_router(admin_auth.router)
app.include_router(superuser.router)
app.include_router(menu.router)
app.include_router(table.router)
app.include_router(order.router)
app.include_router(qr.router, prefix="/api")
app.include_router(otp.router)

# ✅ Optional: Health check route
@app.get("/")
def read_root():
    return {"message": "🚀 Food Ordering API is live!"}
