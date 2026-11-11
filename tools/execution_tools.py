import os
import subprocess

CURRENT_DIR = os.getcwd()

def get_current_dir() -> str:
    """현재 유지되고 있는 작업 디렉토리를 반환합니다."""
    return CURRENT_DIR

def run_command(command: str) -> str:
    global CURRENT_DIR
    try:
        cmd_str = command.strip()
        if cmd_str.startswith("cd "):
            target_dir = cmd_str[3:].strip().strip('"').strip("'")
            new_path = os.path.normpath(os.path.join(CURRENT_DIR, target_dir))
            if os.path.exists(new_path) and os.path.isdir(new_path):
                CURRENT_DIR = new_path
                return f"경로 변경됨: {CURRENT_DIR}"
            return f"이동 실패: 경로 없음 ({new_path})"
        
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        result = subprocess.run(
            cmd_str, shell=True, capture_output=True, text=True, 
            encoding='utf-8', errors='replace', check=True, cwd=CURRENT_DIR, env=env
        )
        return f"[현재 위치: {CURRENT_DIR}]\n명령어 실행 성공:\n{result.stdout[:3000]}"
    except subprocess.CalledProcessError as e:
        return f"[현재 위치: {CURRENT_DIR}]\n실패 (코드 {e.returncode}):\n{str(e.stderr)[:2000]}"