import os
import glob
import streamlit as st
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from .config import COMPONENTS_PATH
from .utils import extract_component_info

def load_documents():
    """모노레포에서 컴포넌트 문서 로드"""
    st.info("문서를 로딩하고 있습니다...")
    
    try:
        if not os.path.exists(COMPONENTS_PATH):
            raise ValueError(f"Component path does not exist: {COMPONENTS_PATH}")
        
        files = get_component_files()
        documents = load_document_contents(files)
        texts = process_documents(documents)
        
        return texts
    
    except Exception as e:
        st.error(f"문서 로딩 중 오류 발생: {str(e)}")
        raise

def get_component_files():
    files = []
    for ext in ['*.tsx', '*.ts']:
        files.extend(glob.glob(os.path.join(COMPONENTS_PATH, '**', ext), recursive=True))
    
    if not files:
        raise ValueError(f"No .tsx or .ts files found in {COMPONENTS_PATH}")
    
    return files

def load_document_contents(files):
    documents = []
    for file_path in files:
        try:
            documents.extend(load_single_document(file_path))
        except Exception as e:
            st.warning(f"파일 로드 중 오류 발생: {file_path} - {str(e)}")
    
    return documents

def load_single_document(file_path):
    if not os.path.exists(file_path):
        st.warning(f"파일이 존재하지 않음: {file_path}")
        return []
        
    try:
        return load_with_encoding(file_path, 'utf-8')
    except UnicodeDecodeError:
        return load_with_encoding(file_path, 'cp949')

def load_with_encoding(file_path, encoding):
    with open(file_path, 'r', encoding=encoding) as f:
        content = f.read()
        if not content.strip():
            st.warning(f"빈 파일: {file_path}")
            return []
    
    loader = TextLoader(file_path, encoding=encoding)
    return loader.load()

def process_documents(documents):
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
    return text_splitter.split_documents(documents) 