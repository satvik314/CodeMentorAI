from fastapi import FastAPI, Request
from starlette.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.templating import Jinja2Templates
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from fastapi.staticfiles import StaticFiles
from langchain.chains import LLMChain
from langchain.chains.openai_functions import (
    create_openai_fn_chain,
    create_openai_fn_runnable,
    create_structured_output_chain,
    create_structured_output_runnable,
)
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import json
from langchain_core.pydantic_v1 import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="testapplication")
# Mount the "static" folder to "/static" URL
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Initialize the OpenAI API
llm = OpenAI(temperature=0.9)


# Defining class for output
class Code_Eval(BaseModel):
    """Identifying information about a person."""

    correct: bool = Field(..., description="Whether the code is correct or not")
    explanation: str = Field(..., description="Explanation about the correctness or incorrectness of the code.")
    suggestion: str = Field(..., description="Additional suggestion on the code.")


# Define the prompt template
prompt = PromptTemplate(
    input_variables=["question", "code"],
    template="Check if the following code is correct. If it is incorrect, provide a detailed explanation of why it is "
             "incorrect and how it can be corrected. DO NOT PROVIDE CORRECT SOLUTION, LET THE STUDENT FIGURE OUT ANSWER. Question: {question} Code: {code}",
)

# Create a chain
chain = LLMChain(llm=llm, prompt=prompt)

llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0)
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful AI assistant. Your job is to provide the best assistance to the user.",
        ),
        (
            "human",
            "Check if the following code is correct. If it is incorrect, provide a detailed explanation of why it is "
            "incorrect and how it can be corrected. Do not return 'Correct'. Question: {question} Code: {code}",
        ),
        ("human", "Tip: Make sure to answer in the correct format"),
    ]
)

runnable = create_structured_output_runnable(Code_Eval, llm, prompt)

with open("static/problems.json", "r", encoding="utf-8") as file:
    questions_data = json.load(file)


@app.get("/")
def form_post(request: Request):
    return templates.TemplateResponse('form.html', context={'request': request})


@app.post("/")
async def form_post(request: Request):
    form_data = await request.form()
    topic = form_data.get('topics')
    topic_name = questions_data[int(topic) - 1]['title']
    question = form_data.get('question')
    code = form_data.get('code')
    # output = chain.run(question=question, code=code)
    output = runnable.invoke({"question": question, "code": code})
    print(output)

    return templates.TemplateResponse('results.html',
                                      context={'request': request, "topic": topic_name, "code": code,
                                               "question": question,
                                               'correct': str(output.correct), "explanation": output.explanation,
                                               "suggestion": output.suggestion})
