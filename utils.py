from typing import List, Dict
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
from pydantic import BaseModel, Field
from models import CodeCheckResponse


def CodeCheck(question, code, llm):
    # Define the prompt
    prompt = f"""
    Check if the following code is correct. If it is, return 'Correct'. If it is not, return 'Incorrect'. 
    If it is incorrect, provide a detailed explanation of why it is incorrect and how it can be corrected. 
    NEVER OUTPUT THE CORRECT CODE. 
    Question: 
    {question} 

    Code: 
    {code}

    Please provide the scores and feedback to the candidate in the following format:

    Correctness: {{Correct or Incorrect}}
    Explanation: {{Detailed explanation of why the code is incorrect and how it can be improved.}}
    Efficiency: {{If the code is incorrect mention "None". If the code is correct, give suggestions on how the code can be optimised. Also, suggest some alternate ways of implementation.}}
    
    """
    # Ask the LLM to score the resume and provide feedback
    response = llm.predict(prompt)

    parser = OutputFixingParser.from_llm(parser=PydanticOutputParser(pydantic_object=CodeCheckResponse), llm=llm)
    format_instructions = parser.get_format_instructions()

    codecheck = parser.parse(response)

    return codecheck


def runcode(code):
    try:
        exec(code)
    except Exception as e:
        print(f"Error occurred: {e}")
        return f"Error occurred: {e}"


#### 
# example for run code
code = """
def larger(a,b):
    if a>b:
        return a
    elif b>a:
        return b
    else:
        return None

print(larger(3,4))

"""

runcode(code)
###### 