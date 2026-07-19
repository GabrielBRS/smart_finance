from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from cognition.exemplos.agent import SYSTEM_PROMPT
from cognition.exemplos.config import LLM_BASE_URL, LLM_API_KEY, LLM_MODEL

llm = ChatOpenAI(model=LLM_MODEL, base_url=LLM_BASE_URL, api_key=LLM_API_KEY, temperature=0.2)

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("system", "Contexto recuperado:\n{context}"),
    ("user", "{question}"),
])

chain = prompt | llm | StrOutputParser()