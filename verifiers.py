from langchain_ollama import ChatOllama
import json
import os

BASE_URL = os.getenv('base_URL')


answer_checker = ChatOllama(
    model='llama3.1',
    format='json',
    base_url=BASE_URL,
    temperature=0
)



def check_answer(question,generation, **kwargs):

    template =f""" <|begin_of_text|><|start_header_id|>system<|end_header_id|> You are a grader assessing whether
    an answer is useful to resolve a question. Give a binary score 'yes' or 'no' score to indicate whether the answer is useful to resolve a question.
    provide the binary score as a JSON with a single key 'score' and no preamble or explanation. <|eot_id|><|start_header_id|>user<|end_header_id|>
    here is the answer:
    \n -------- \n
    {generation}
    \n -------- \n
    Here is the question: {question} <|eot_id|><|start_header_id|>assistant<|end_header_id|>"""

    response =answer_checker.invoke(template)
    return json.loads(response.content)
