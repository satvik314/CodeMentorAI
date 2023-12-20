from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Initialize the OpenAI API
llm = OpenAI(temperature=0.9)

# Define the prompt template
prompt = PromptTemplate(
    input_variables=["question", "code"],
    template="Check if the following code is correct. If it is incorrect, provide a detailed explanation of why it is incorrect and how it can be corrected. Do not return 'Correct'. Question: {question} Code: {code}",
)

# Create a chain
chain = LLMChain(llm=llm, prompt=prompt)

@app.get("/")
def form_post(request: Request):
    return templates.TemplateResponse('form.html', context={'request': request})

@app.post("/")
async def form_post(request: Request):
    form_data = await request.form()
    question = form_data.get('question')
    code = form_data.get('code')
    output = chain.run(question=question, code=code)
    return templates.TemplateResponse('form.html', context={'request': request, 'output': output})