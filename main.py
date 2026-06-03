from fastapi import FastAPI
from database import engine,Base
from routers import auth_router, product_router, order_router
from models import *
from logger import RequestLoggingMiddleware
from fastapi.middleware.cors import CORSMiddleware

app=FastAPI(
    title="Order Management System",
    version="1.0"
)

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return{
        "message":"Order Management API is Running!!!"
    }
    
app.add_middleware(RequestLoggingMiddleware)    
    
app.include_router(auth_router.router)
app.include_router(product_router.router)
app.include_router(order_router.router)

app.add_middleware(CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],)
    