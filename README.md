# 디자인 시스템 Assistant

디자인 시스템 컴포넌트에 대한 질문과 답변을 제공하는 AI 챗봇입니다. LangChain과 OpenAI를 활용하여 컴포넌트 코드를 분석하고 관련 정보를 제공합니다.

## 주요 기능

- 모노레포의 컴포넌트 코드 자동 로딩
- 컴포넌트 관련 질의응답
- Props 인터페이스 자동 추출
- 소스 코드 조회
- 대화 기록 유지

## 설치 방법

1. 저장소 클론

```bash
git clone [repository-url]
cd [repository-name]
```

2. 가상환경 생성 및 활성화

```bash
python -m venv venv
source venv/bin/activate # Windows: .\venv\Scripts\activate
```

3. 의존성 설치

```bash
bash
pip install -r requirements.txt
```

4. 환경변수 설정

```bash
bash
cp .env.example .env
```

`.env` 파일을 열어 다음 값들을 설정:

- `OPENAI_API_KEY`: OpenAI API 키
- `MONOREPO_PATH`: 컴포넌트가 있는 모노레포 경로

## 실행 방법

1. 실행 스크립트 권한 설정

```bash
bash
chmod +x run.sh
```

2. 애플리케이션 실행

```bash
bash
./run.sh
```

또는

```bash
bash
streamlit run app.py
```

## 사용 방법

1. 웹 브라우저에서 `http://localhost:8501` 접속
2. 채팅창에 컴포넌트 관련 질문 입력
3. AI가 컴포넌트 코드를 분석하여 답변 제공
4. "관련 컴포넌트 코드" 섹션에서 소스 코드 확인 가능

## 필수 요구사항

- Python 3.8 이상
- OpenAI API 키
- 컴포넌트가 포함된 모노레포

## 의존성 패키지

- streamlit
- langchain
- langchain-community
- openai
- faiss-cpu
- python-dotenv
- watchdog
- tiktoken
- unstructured
- python-magic-bin

## 라이선스

[라이선스 정보 추가]

이 README.md는 프로젝트의 주요 기능, 설치 방법, 실행 방법, 사용 방법 등을 포함하고 있습니다. 필요에 따라 라이선스 정보나 추가적인 설명을 더하실 수 있습니다.
