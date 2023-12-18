from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse 
from langchain.llms import OpenAI

from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


class Item(BaseModel):
    question: str
    code: str


@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

@app.post("/check_code/")
async def check_code(item: Item):
    llm = OpenAI(temperature=0.9)
    text = item.question + "\n" + item.code
    response = llm(text)
    return {"response": response}


# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)