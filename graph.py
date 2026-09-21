from typing import TypedDict

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

from config import CHAT_MODEL, LM_STUDIO_API_KEY, LM_STUDIO_BASE_URL
from retriever import hybrid_search


class GraphState(TypedDict):
    question: str
    context: str
    answer: str


llm = ChatOpenAI(
    model=CHAT_MODEL,
    base_url=LM_STUDIO_BASE_URL,
    api_key=LM_STUDIO_API_KEY,
    temperature=0.1,
)


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an HR policy assistant for the company. "
            "Answer the question using ONLY the context below, which comes from "
            "company_policy.pdf. Be clear and concise. "
            "If the answer is not in the context, reply exactly: "
            "'I could not find this in the company policy. "
            "Please contact the HR department.'\n\n"
            "Context:\n{context}",
        ),
        ("human", "{question}"),
    ]
)


def format_docs(docs):
    parts = []
    for doc in docs:
        page = doc.metadata.get("page")
        label = f"[Page {page + 1}] " if isinstance(page, int) else ""
        parts.append(f"{label}{doc.page_content}")
    return "\n\n".join(parts)


def retrieve(state: GraphState):
    docs = hybrid_search(state["question"])
    return {"context": format_docs(docs)}


def generate(state: GraphState):
    response = (prompt | llm).invoke(
        {
            "question": state["question"],
            "context": state["context"],
        }
    )

    return {"answer": response.content}


graph = StateGraph(GraphState)

graph.add_node("retrieve", retrieve)
graph.add_node("generate", generate)

graph.add_edge(START, "retrieve")
graph.add_edge("retrieve", "generate")
graph.add_edge("generate", END)

app = graph.compile()


def ask_hr_bot(question):
    result = app.invoke(
        {
            "question": question,
            "context": "",
            "answer": "",
        }
    )

    return result["answer"]