import httpx

class MemoryClient:

    def __init__(self, base_url: str):
        self.base_url = base_url

    async def write(self, user_id: int, state: dict):
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{self.base_url}/write",
                json={
                    "user_id": user_id,
                    "state": state
                }
            )

    async def read(self, user_id: int):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/read",
                params={"user_id": user_id}
            )
            return response.json()
