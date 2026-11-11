import os
import datetime
from pydantic_ai import Agent
from dotenv import load_dotenv

# 분리된 도구들 임포트 (change_directory 및 get_current_dir 추가)
from tools.execution_tools import run_command, change_directory, get_current_dir
from tools.file_tools import read_file, write_file
from tools.google_tools import add_google_schedule, delete_google_schedule
from tools.notion_tools import add_notion_schedule, delete_notion_schedule, update_notion_schedule
from tools.git_tools import git_init_and_push, init_and_connect_repo, commit_and_push

load_dotenv()

# 시스템 현재 날짜와 요일 동적 계산
days_ko = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
today = datetime.datetime.now()
today_str = f"{today.year}년 {today.month}월 {today.day}일 ({days_ko[today.weekday()]})"

agent = Agent(
    'groq:openai/gpt-oss-120b',
    system_prompt=(
        "당신은 Windows(PowerShell) 환경에서 연구실 서버 및 파일을 관리하고 프로젝트 일정을 조율하는 자율형 AI 에이전트입니다.\n\n"
        "⚠️ **[필수 작업 규칙 - 절대 엄수]**\n"
        "1. **폴더 이동 및 생성**: 작업 디렉토리(폴더)를 이동하거나 새 폴더로 들어갈 때는 절대 `run_command`로 `cd`, `mkdir`, `Set-Location`, `Test-Path` 등을 조합해 실행하지 마세요. 무조건 **`change_directory` 도구**를 호출하세요. (폴더가 없으면 알아서 생성 후 이동합니다.)\n"
        "2. **파일 읽기 및 쓰기**: 파일을 생성하거나 수정할 때는 터미널 명령어를 쓰지 말고 반드시 **`write_file` 도구**를 사용하세요.\n"
        "3. **Windows 명령어 규칙**: `run_command`는 파이썬 스크립트 실행, 패키지 설치(`pip`), 디렉토리 조회(`dir` 또는 `Get-Location`) 등 시스템 명령이 필요할 때만 단일 명령어로 사용하세요. 리눅스 명령어(`mkdir -p`, `ls -la`, `rm -rf`, `touch`)는 절대 금지합니다.\n"
        "4. **에러 대처**: 명령어 실행 중 에러가 발생하면 무작정 반복 재시도하지 말고 원인을 분석해 보고하세요.\n\n"
        "📅 **[일정 및 Git 관리 규칙]**\n"
        f"5. **현재 기준 날짜는 {today_str}입니다.** 프로젝트 일정 추가 요청 시 **'어디에 저장할까요? (노션, 구글 캘린더, 또는 둘 다)'**라고 먼저 물어보세요.\n"
        "6. 저장 위치가 확정되면 상대적 날짜('다음주 화요일' 등)를 정확한 YYYY-MM-DD로 계산하여 `add_notion_schedule` 또는 `add_google_schedule`을 호출하세요.\n"
        "7. 일정 삭제 시 위치를 명시하지 않았다면 어디서 지울지 먼저 묻고 `delete_notion_schedule` 또는 `delete_google_schedule`을 호출하세요. 일정 수정은 `update_notion_schedule`을 호출하세요.\n"
        "8. Git 레포지토리 연결은 `manage_git_init`, 작업 내역 커밋 및 푸시는 적절한 커밋 메시지를 작성해 `manage_git_commit`을 호출하세요."
    )
)

# 도구 등록 (change_directory 추가 등록)
agent.tool_plain(change_directory)
agent.tool_plain(read_file)
agent.tool_plain(write_file)
agent.tool_plain(run_command)
agent.tool_plain(add_google_schedule)
agent.tool_plain(delete_google_schedule)
agent.tool_plain(add_notion_schedule)
agent.tool_plain(delete_notion_schedule)
agent.tool_plain(update_notion_schedule)

@agent.tool_plain
def manage_git_init(repo_url: str) -> str:
    """새로운 깃허브 레포지토리 URL을 현재 작업 중인 로컬 저장소와 연결할 때 사용합니다."""
    return init_and_connect_repo(get_current_dir(), repo_url)

@agent.tool_plain
def manage_git_commit(commit_message: str) -> str:
    """현재 작업 디렉토리의 파일 변경사항을 깃허브에 커밋하고 푸시할 때 사용합니다."""
    return commit_and_push(get_current_dir(), commit_message)

@agent.tool_plain
def manage_git_upload(repo_url: str, commit_message: str) -> str:
    """현재 작업 디렉토리의 변경사항을 깃허브에 커밋하고 일괄 푸시합니다."""
    return git_init_and_push(get_current_dir(), repo_url, commit_message)

chat_history = []

async def run_complex_task(user_message: str) -> str:
    """사용자의 복잡한 명령을 에이전트에게 전달하고 결과를 반환합니다."""
    global chat_history
    try:
        result = await agent.run(user_message, message_history=chat_history)
        
        if hasattr(result, 'all_messages'):
            chat_history = result.all_messages()
        
        if hasattr(result, 'data') and result.data is not None:
            return str(result.data)
        elif hasattr(result, 'output') and result.output is not None:
            return str(result.output)
        elif hasattr(result, 'content') and result.content is not None:
            return str(result.content)
        else:
            return str(result)
            
    except Exception as e:
        return f"에이전트 실행 중 오류 발생: {e}"