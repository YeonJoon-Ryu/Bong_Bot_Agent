import os
from tools.execution_tools import get_current_dir

def read_file(file_path: str) -> str:
    try:
        target_path = os.path.normpath(os.path.join(get_current_dir(), file_path))
        with open(target_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return content[:3000] + "\n...(생략)..." if len(content) > 3000 else content
    except Exception as e:
        return f"파일 읽기 실패: {e}"

def write_file(file_path: str, content: str) -> str:
    try:
        target_path = os.path.normpath(os.path.join(get_current_dir(), file_path))
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(content if content else "")
        return f"{target_path} 저장 성공."
    except Exception as e:
        return f"파일 쓰기 실패: {e}"