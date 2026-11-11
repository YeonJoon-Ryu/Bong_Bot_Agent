import os
import subprocess

# 프로젝트 루트 기준 sandbox/workspace를 기본 시작 경로로 고정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_WORKSPACE = os.path.join(BASE_DIR, "sandbox", "workspace")
os.makedirs(DEFAULT_WORKSPACE, exist_ok=True)

CURRENT_DIR = DEFAULT_WORKSPACE

def get_current_dir() -> str:
    """현재 유지되고 있는 작업 디렉토리를 반환합니다."""
    return CURRENT_DIR

def change_directory(target_dir: str, raw_cmd: str = None) -> str:
    """작업 디렉토리를 변경합니다. 에이전트가 입력한 명령어와 이동 결과를 터미널에 출력합니다."""
    global CURRENT_DIR
    try:
        clean_target = target_dir.strip().strip('"').strip("'")
        display_cmd = raw_cmd if raw_cmd else f"cd {clean_target} (change_directory 도구 호출)"
        
        # 👇 1. 에이전트가 실제로 어떤 명령을 내렸는지 먼저 출력
        print(f"\n💻 [Windows 터미널 실행] ({CURRENT_DIR})\n> {display_cmd}")

        new_path = os.path.normpath(os.path.join(CURRENT_DIR, clean_target))
        
        if not os.path.exists(new_path):
            os.makedirs(new_path, exist_ok=True)
            
        if os.path.isdir(new_path):
            CURRENT_DIR = new_path
            print(f"📂 [작업 경로 변경 완료] 현재 위치: {CURRENT_DIR}")
            print("-------------------------------------------")
            return f"작업 디렉토리가 변경되었습니다. 현재 위치: {CURRENT_DIR}"
        else:
            print(f"❌ [디렉토리 이동 실패] 경로가 올바르지 않습니다: {new_path}")
            print("-------------------------------------------")
            return f"디렉토리 이동 실패: 올바른 폴더 경로가 아닙니다 ({new_path})"
    except Exception as e:
        print(f"❌ [디렉토리 이동 오류] {e}")
        print("-------------------------------------------")
        return f"디렉토리 이동 중 오류 발생: {e}"

def run_command(command: str) -> str:
    """Windows PowerShell 명령어를 실행하고 실시간 명령어와 결과 로그를 모두 출력합니다."""
    global CURRENT_DIR
    try:
        cmd_str = command.strip()
        
        # 에이전트가 run_command로 cd 나 Set-Location을 입력했을 때 원본 명령어를 보존하여 전달
        if cmd_str.lower().startswith("cd ") or cmd_str.lower() == "cd.." or cmd_str.lower().startswith("set-location "):
            if cmd_str.lower() == "cd..":
                return change_directory("..", raw_cmd=cmd_str)
            parts = cmd_str.split(maxsplit=1)
            if len(parts) > 1 and ";" not in parts[1] and "&&" not in parts[1]:
                return change_directory(parts[1], raw_cmd=cmd_str)

        # 👇 일반 명령어 실행 시 에이전트가 친 명령어를 실시간 출력
        print(f"\n💻 [Windows 터미널 실행] ({CURRENT_DIR})\n> {cmd_str}")

        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"

        # -NoProfile 옵션으로 C:\Users\RYU 초기화 방지 + UTF-8 인코딩 적용
        ps_command = f"[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; {cmd_str}"
        
        result = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_command], 
            shell=False, 
            capture_output=True, 
            text=True, 
            encoding='utf-8',
            errors='replace',
            cwd=CURRENT_DIR,
            env=env
        )
        
        output = result.stdout.strip() if result.stdout else ""
        err_output = result.stderr.strip() if result.stderr else ""
        
        if output:
            print(f"📤 [실행 결과]\n{output}")
        if err_output:
            print(f"⚠️ [경고/에러]\n{err_output}")
        if not output and not err_output:
            print("📤 [실행 결과] (출력 없음)")
        print("-------------------------------------------")

        full_result = f"[현재 위치: {CURRENT_DIR}]\n"
        if output:
            full_result += f"출력:\n{output}\n"
        if err_output:
            full_result += f"에러/경고:\n{err_output}\n"
        if not output and not err_output:
            full_result += "명령어가 출력 없이 완료되었습니다."

        if len(full_result) > 3000:
            full_result = full_result[:3000] + "\n...(출력 결과가 너무 길어 일부 생략됨)..."

        return full_result
        
    except Exception as e:
        err_msg = str(e)
        print(f"❌ [시스템 예외 발생]\n{err_msg}\n-------------------------------------------")
        return f"[현재 위치: {CURRENT_DIR}]\n명령어 실행 중 예외 발생: {err_msg}"