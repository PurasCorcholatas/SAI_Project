from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from router.router import user, chat, test_usuarios


app = FastAPI()

app.include_router(user)

app.include_router(chat, prefix="/api")
app.include_router(test_usuarios, prefix="/api")

app.include_router(chat)

@app.get("/")
def root():
    return {"status": "ok"}

        
