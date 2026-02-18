from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
memory_store = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/write")
async def write_memory(data: dict):
    user_id = str(data.get("user_id"))
    memory_store[user_id] = data.get("state")
    return {"status": "ok"}

@app.get("/read")
async def read_memory(user_id: str):
    state = memory_store.get(user_id)
    return {"state": state}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5005)
