import streamlit as st
from src.document_loader import load_documents
from src.embeddings import init_pinecone, create_vector_store
from src.chat import init_chat_chain

def display_code_with_metadata(doc):
    """소스 코드와 메타데이터 표시"""
    st.code(doc.page_content, language="typescript")
    
    if doc.metadata.get("props_interface"):
        st.subheader("Props 인터페이스")
        st.code(doc.metadata["props_interface"], language="typescript")

def main():
    st.title("디자인 시스템 Assistant")
    
    # Pinecone 초기화
    init_pinecone()
    
    # 사이드바
    with st.sidebar:
        st.subheader("설정")
        if st.button("문서 다시 로드"):
            st.session_state.vector_store = create_vector_store(load_documents())
            st.success("문서가 업데이트되었습니다!")
    
    # 초기화
    if 'vector_store' not in st.session_state:
        texts = load_documents()
        st.session_state.vector_store = create_vector_store(texts)
    
    if 'chat_chain' not in st.session_state:
        st.session_state.chat_chain = init_chat_chain(st.session_state.vector_store)
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # 채팅 히스토리 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # 사용자 입력
    if prompt := st.chat_input("디자인 시스템에 대해 물어보세요"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.write(prompt)
        
        with st.chat_message("assistant"):
            response = st.session_state.chat_chain.invoke({"question": prompt})
            st.write(response["answer"])
            
            # 소스 코드 표시
            with st.expander("관련 컴포넌트 코드"):
                for doc in response["source_documents"]:
                    display_code_with_metadata(doc)
            
            st.session_state.messages.append({"role": "assistant", "content": response["answer"]})

if __name__ == "__main__":
    main()