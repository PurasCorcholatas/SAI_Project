from fastapi import FastAPI

app = FastAPI()
memory_store = {}

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
