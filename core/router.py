import ollama
import asyncio

async def classify_intent(user_message: str) -> str:
    """사용자의 메시지를 로컬 LLM(Llama 3.1)으로 분석하여 의도를 분류합니다."""
    # 프롬프트를 간결하고 명확한 영어로 최적화하여 연산 속도를 극대화합니다.
    system_prompt = (
        "You are the intent router for a laboratory AI agent.\n"
        "Analyze the user's message and classify it strictly into one of two categories:\n\n"
        "1. \"SIMPLE\": General chat, casual greetings, simple questions about general knowledge, "
        "or questions that do NOT require reading/writing files, checking directory contents, running scripts, or executing terminal commands.\n\n"
        "2. \"COMPLEX\": Any request that involves interacting with the computer system, such as:\n"
        "- Creating, reading, writing, modifying, or deleting files/folders (e.g., '텍스트 파일 만들어줘', '안에 적어줘')\n"
        "- Checking directory contents, listing files, or searching paths (e.g., '뭐뭐 있는지 알려줘', '목록 보여줘', '디렉토리 확인')\n"
        "- Writing or executing Python scripts, machine learning training, data processing\n"
        "- Running terminal commands, checking git status, commit, push\n\n"
        "Rules:\n"
        "- Output ONLY one word: either 'SIMPLE' or 'COMPLEX'.\n"
        "- No explanations, no punctuation, no extra text."
    )

    try:
        client = ollama.AsyncClient()
        response = await client.chat(
            model='llama3.1',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_message}
            ],
            keep_alive=-1,
            options={"temperature": 0.0}  # 무작위성을 없애고 속도와 정확도 향상
        )

        result = response['message']['content'].strip().upper()
        return "COMPLEX" if "COMPLEX" in result else "SIMPLE"

    except Exception as e:
        print(f"[Router Error] Ollama 통신 오류: {e}")
        return "SIMPLE"


async def generate_simple_response(user_message: str) -> str:
    """SIMPLE로 분류된 단순 대화나 질문에 대해 로컬 LLM이 직접 답변을 생성합니다."""
    # 한국어 중심 답변이되 영어 혼용을 허용하고, 불필요한 연산 과정 설명을 차단합니다.
    system_prompt = (
        "당신은 친절한 연구실 AI 비서입니다. "
        "사용자의 질문에 한국어로 명확하게 답변하세요. "
        "필요한 경우 자연스러운 **영어 및 기술 용어 혼용을 허용**합니다. "
        "절대 'API를 통해', '정보를 받고 있습니다' 등 자신의 연산 과정이나 내부 동작을 설명하는 멘트나 괄호 부가 설명을 출력하지 마세요. "
        "오직 최종 답변 내용만 출력하세요."
    )

    try:
        client = ollama.AsyncClient()
        response = await client.chat(
            model='llama3.1',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_message}
            ],
            keep_alive=-1,
            options={"temperature": 0.3}  # 엉뚱한 말을 줄이기 위해 온도를 낮춤
        )
        return response['message']['content'].strip()
    except Exception as e:
        print(f"[Router Error] 답변 생성 오류: {e}")
        return "죄송합니다. 일시적인 로컬 모델 통신 오류가 발생했습니다."

    
if __name__ == "__main__":
    async def test():
        print("분류 테스트:", await classify_intent("오늘 기분 어때?"))
        print("답변 테스트:", await generate_simple_response("지금 몇 시야?"))
    asyncio.run(test())