import re

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