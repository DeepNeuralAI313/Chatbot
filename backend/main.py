from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database.db import init_database
from services.rag_service import initialize_rag
from routes import chat, admin, conversation, user

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    print("Initializing database...")
    init_database()
    
    print("Initializing RAG system...")
    initialize_rag()
    
    print("Application startup complete!")
    
    yield
    
    # Shutdown
    print("Application shutdown")

# Create FastAPI app
app = FastAPI(
    title="Mini AI Chatbot API",
    description="RAG-powered chatbot with admin panel",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(admin.router)
app.include_router(conversation.router)
app.include_router(user.router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Mini AI Chatbot API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
