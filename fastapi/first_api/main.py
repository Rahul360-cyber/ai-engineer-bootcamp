from fastapi import FastAPI
app = FastAPI()

@app.get("/")
async def root():
    return {"message" : "hello Rahul"}

@app.get("/about")
async def intro():
    return {"name":"RAHUL","GOAL":"AI ENGINEER"}

@app.get("/square/{number}")
async def square(number):
    return {"number": number , "square" : (number)**2}

@app.get("/greet")
async def greeting(name : str):
    return f"hello {name}" 