from pydantic_ai import Agent
from dotenv import load_dotenv

# 분리된 도구들 임포트
from tools.execution_tools import run_command
from tools.file_tools import read_file, write_file
from tools.google_tools import add_google_schedule, delete_google_schedule
from tools.notion_tools import add_notion_schedule, delete_notion_schedule, update_notion_schedule

load_dotenv()

agent = Agent(
    'groq:openai/gpt-oss-120b',
    system_prompt=(
        "당신은 연구실 서버 및 파일을 관리하고 프로젝트 일정을 조율하는 자율형 AI 에이전트입니다. "
        "1. 사용자가 특정 폴더에 파일을 만들거나 들어가라고 지시하면, 해당 폴더가 존재하는지 확인하고 필요시 생성한 뒤 경로에 맞게 파일을 생성하세요. "
        "2. 터미널 명령어 실행 시 작업 디렉토리(경로) 상태가 유지되므로 'cd' 명령어로 이동한 위치가 기억됩니다. "
        "3. **현재 기준 날짜는 2026년 11월 9일 (월요일)입니다.** 사용자가 프로젝트 일정을 추가해 달라고 요청하면, "
        "**'어디에 저장할까요? (노션, 구글 캘린더, 또는 둘 다)'라고 먼저 사용자에게 물어보세요.** "
        "4. 사용자가 대답하여 저장할 곳이 확정되면, '다음주 화요일' 등의 상대적 표현을 계산하여 정확한 YYYY-MM-DD 날짜를 도출하고, "
        "사용자의 선택에 맞춰 `add_notion_schedule` 또는 `add_google_schedule` (둘 다라면 각각 호출) 도구를 호출하세요. "
        "5. 사용자가 일정을 삭제해 달라고 할 때 위치를 명시하지 않았다면 어디서 지울지 묻고, 사용자의 선택에 따라 `delete_notion_schedule` 또는 `delete_google_schedule` 도구를 호출하세요. "
        "6. 수정 요청 시에는 `update_notion_schedule` 도구를 호출하세요."
    )
)

agent.tool_plain(read_file)
agent.tool_plain(write_file)
agent.tool_plain(run_command)
agent.tool_plain(add_google_schedule)
agent.tool_plain(delete_google_schedule)
agent.tool_plain(add_notion_schedule)
agent.tool_plain(delete_notion_schedule)
agent.tool_plain(update_notion_schedule)

async def run_complex_task(user_message: str) -> str:
    """사용자의 복잡한 명령을 에이전트에게 전달하고 결과를 반환합니다."""
    try:
        result = await agent.run(user_message)
        
        if hasattr(result, 'data'):
            return str(result.data)
        elif hasattr(result, 'output'):
            return str(result.output)
        elif hasattr(result, 'content'):
            return str(result.content)
        else:
            return str(result)
            
    except Exception as e:
        return f"에이전트 실행 중 오류 발생: {e}"