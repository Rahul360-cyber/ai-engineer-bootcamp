from fastapi import FastAPI
from app.routers import users,student,products,movies,about
from app.database.database import base,engine
base()

app = FastAPI()


app.include_router(users.router)
app.include_router(student.router)
app.include_router(products.router)
app.include_router(movies.router)
app.include_router(about.router)
