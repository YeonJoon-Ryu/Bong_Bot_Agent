import os
import subprocess

def git_init_and_push(target_dir: str, repo_url: str, commit_message: str, branch: str = "main") -> str:
    """지정된 경로에서 Git 저장소를 초기화하고 커밋 및 푸시를 일괄 수행합니다."""
    commands = [
        "git init",
        "git add .",
        f'git commit -m "{commit_message}"',
        f"git branch -M {branch}",
        "git remote remove origin",
        f"git remote add origin {repo_url}",
        f"git push -u origin {branch}"
    ]
    
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    
    results = []
    for cmd in commands:
        try:
            check_error = False if "remote remove" in cmd else True
            res = subprocess.run(
                cmd, shell=True, capture_output=True, text=True,
                encoding='utf-8', errors='replace', check=check_error, cwd=target_dir, env=env
            )
            results.append(f"> {cmd}\n완료: {res.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            err_msg = e.stderr.strip() if e.stderr else str(e)
            results.append(f"> {cmd}\n실패: {err_msg}")
            
            if "nothing to commit" not in err_msg and "remote remove" not in cmd:
                break
                
    return "\n".join(results)

def init_and_connect_repo(target_dir: str, repo_url: str, branch: str = "main") -> str:
    """Git 저장소를 초기화하고 원격 레포지토리에 연결합니다."""
    commands = [
        "git init",
        f"git branch -M {branch}",
        f"git remote add origin {repo_url}"
    ]
    
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    
    results = []
    for cmd in commands:
        try:
            res = subprocess.run(
                cmd, shell=True, capture_output=True, text=True,
                encoding='utf-8', errors='replace', check=True, cwd=target_dir, env=env
            )
            results.append(f"> {cmd}\n완료: {res.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            err_msg = e.stderr.strip() if e.stderr else str(e)
            results.append(f"> {cmd}\n실패: {err_msg}")
            break
            
    return "\n".join(results) + "\n✅ 로컬 저장소 초기화 및 원격 레포지토리 연결이 완료되었습니다."

def commit_and_push(target_dir: str, commit_message: str, branch: str = "main") -> str:
    """변경된 모든 파일을 스테이지에 올리고 커밋한 뒤 원격 저장소로 푸시합니다."""
    commands = [
        "git add .",
        f'git commit -m "{commit_message}"',
        f"git push -u origin {branch}"
    ]
    
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    
    results = []
    for cmd in commands:
        try:
            res = subprocess.run(
                cmd, shell=True, capture_output=True, text=True,
                encoding='utf-8', errors='replace', check=True, cwd=target_dir, env=env
            )
            results.append(f"> {cmd}\n완료: {res.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            err_msg = e.stderr.strip() if e.stderr else str(e)
            results.append(f"> {cmd}\n실패: {err_msg}")
            # 커밋할 내용이 없는 경우는 정상적인 상황이므로 에러 처리하지 않고 중단
            if "nothing to commit" not in err_msg:
                break
                
    return "\n".join(results) + f"\n✅ 성공적으로 '{branch}' 브랜치에 커밋 및 푸시되었습니다."