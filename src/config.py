import os
from dotenv import load_dotenv

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