from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config.llm_config import get_llm_singleton

load_dotenv()
llm = get_llm_singleton(temperature=0)

system  = """You are a grader assessing relevance of a retrieved document to a user question.
If the document contains keyword(s) or semantic meaning related to the question, respond with exactly 'yes' or 'no'."""

grade_prompt    = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "Retrieved document: \n\n {document} \n\n User question: {question}\n\nAnswer with 'yes' or 'no' only.")
    ]
)

retrieval_grader    = grade_prompt | llm | StrOutputParser()

