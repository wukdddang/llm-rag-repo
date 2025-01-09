import os
import streamlit as st
from dotenv import load_dotenv
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import ChatPromptTemplate
import re

# 환경변수 로드
load_dotenv()

# 상수 정의
MONOREPO_PATH = os.path.normpath(os.getenv("MONOREPO_PATH"))
COMPONENTS_PATH = os.path.normpath(os.path.join(MONOREPO_PATH, "packages/ui/src"))

# 프롬프트 템플릿
PROMPT_TEMPLATE = """당신은 사내 디자인 시스템 전문가입니다.
주어진 컴포넌트 코드를 기반으로 사용자의 질문에 답변해주세요.

컴포넌트 관련 정보:
{context}

사용자 질문: {question}

답변 형식:
1. 컴포넌트 개요
2. Props 설명
3. 사용 예제
4. 주의사항 (있는 경우)

답변:"""

def extract_component_info(content: str) -> dict:
    """컴포넌트 코드에서 중요 정보 추출"""
    info = {}
    
    # Props 인터페이스 추출
    props_match = re.search(r"interface\s+(\w+Props)\s*{([^}]+)}", content)
    if props_match:
        info["props_interface"] = props_match.group(0)
    
    # 컴포넌트 정의 추출
    component_match = re.search(r"(export\s+(?:default\s+)?(?:const|function)\s+\w+)[^{]*{", content)
    if component_match:
        info["component_definition"] = component_match.group(0)
    
    return info

def load_documents():
    """모노레포에서 컴포넌트 문서 로드"""
    st.info("문서를 로딩하고 있습니다...")
    
    try:
        # 경로가 존재하는지 확인
        if not os.path.exists(COMPONENTS_PATH):
            raise ValueError(f"Component path does not exist: {COMPONENTS_PATH}")
        
        st.write(f"검색 경로: {COMPONENTS_PATH}")
        
        # 실제 파일 목록 확인
        import glob
        files = glob.glob(os.path.join(COMPONENTS_PATH, "**/*.tsx"), recursive=True)
        files.extend(glob.glob(os.path.join(COMPONENTS_PATH, "**/*.ts"), recursive=True))
        
        if not files:
            raise ValueError(f"No .tsx or .ts files found in {COMPONENTS_PATH}")
        
        st.write(f"발견된 파일들: {files}")
        
        # 컴포넌트 파일 로드 - glob 패턴 수정
        tsx_loader = DirectoryLoader(
            COMPONENTS_PATH,
            glob="**/*.tsx",  # .tsx 파일만 먼저 로드
            show_progress=True
        )
        ts_loader = DirectoryLoader(
            COMPONENTS_PATH,
            glob="**/*.ts",   # .ts 파일 따로 로드
            show_progress=True
        )
        
        st.write("TSX 파일 로딩 시작...")
        tsx_documents = tsx_loader.load()
        st.write(f"TSX 파일 {len(tsx_documents)}개 로드 완료")
        
        st.write("TS 파일 로딩 시작...")
        ts_documents = ts_loader.load()
        st.write(f"TS 파일 {len(ts_documents)}개 로드 완료")
        
        documents = []
        documents.extend(tsx_documents)
        documents.extend(ts_documents)
        
        st.write(f"로드된 문서 수: {len(documents)}")
        
        if not documents:
            raise ValueError("No documents were loaded. Check if files are readable.")
        
        # 메타데이터 추가
        for doc in documents:
            component_info = extract_component_info(doc.page_content)
            doc.metadata.update(component_info)
        
        # 청크 분할
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=200,
            separators=["\n\nconst", "\nexport", "\nfunction", "\ninterface"]
        )
        texts = text_splitter.split_documents(documents)
        
        st.write(f"분할된 텍스트 청크 수: {len(texts)}")
        
        if not texts:
            raise ValueError("No texts were extracted from the documents. Please check your document files.")
        
        # 임베딩 생성 및 벡터 DB 저장
        embeddings = OpenAIEmbeddings()
        vector_store = FAISS.from_documents(texts, embeddings)
        
        return vector_store
    
    except Exception as e:
        st.error(f"문서 로딩 중 오류 발생: {str(e)}")
        raise

def init_chat_chain(vector_store):
    """대화 체인 초기화"""
    llm = ChatOpenAI(temperature=0.7)
    
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

def display_code_with_metadata(doc):
    """소스 코드와 메타데이터 표시"""
    st.code(doc.page_content, language="typescript")
    
    if doc.metadata.get("props_interface"):
        st.subheader("Props 인터페이스")
        st.code(doc.metadata["props_interface"], language="typescript")

def main():
    st.title("디자인 시스템 Assistant")
    
    # 사이드바
    with st.sidebar:
        st.subheader("설정")
        if st.button("문서 다시 로드"):
            st.session_state.vector_store = load_documents()
            st.success("문서가 업데이트되었습니다!")
    
    # 초기화
    if 'vector_store' not in st.session_state:
        st.session_state.vector_store = load_documents()
    
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
            response = st.session_state.chat_chain({"question": prompt})
            st.write(response["answer"])
            
            # 소스 코드 표시
            with st.expander("관련 컴포넌트 코드"):
                for doc in response["source_documents"]:
                    display_code_with_metadata(doc)
            
            st.session_state.messages.append({"role": "assistant", "content": response["answer"]})

if __name__ == "__main__":
    main()