from langchain_community.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import ChatPromptTemplate
from .config import PROMPT_TEMPLATE

def init_chat_chain(vector_store):
    """대화 체인 초기화"""
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.7,
    )
    
    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        output_key="answer",
        return_messages=True
    )
    
    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
        memory=memory,
        combine_docs_chain_kwargs={"prompt": prompt},
        return_source_documents=True
    ) 