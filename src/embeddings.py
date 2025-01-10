import os
import pinecone
import streamlit as st
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Pinecone

def init_pinecone():
    pinecone.init(
        api_key=os.getenv("PINECONE_API_KEY"),
        environment=os.getenv("PINECONE_ENVIRONMENT")
    )

def create_vector_store(texts):
    """임베딩 생성 및 Pinecone에 저장"""
    embeddings = OpenAIEmbeddings({
        "model": "text-embedding-3-large",
    })

    index_name = "lrim-design-system-chatbot"
    
    ensure_index_exists(index_name)

    return Pinecone.from_documents(
        documents=texts,
        embedding=embeddings,
        index_name=index_name,
        namespace="design-system"
    )

def ensure_index_exists(index_name):
    if index_name not in pinecone.list_indexes():
        pinecone.create_index(
            name=index_name,
            metric="cosine",
            dimension=3072
        ) 