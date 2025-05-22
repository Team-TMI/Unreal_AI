from fastapi import FastAPI
from route import router  
import uvicorn

app = FastAPI(root_path="/service3")
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)