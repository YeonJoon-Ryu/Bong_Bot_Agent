# 🤖 H.A.L.O (Hybrid Agentic Loop Operator)
**Discord 기반 하이브리드 AI 에이전트 시스템**

H.A.L.O는 Discord를 인터페이스로 활용하여 연구실 서버 자원을 자율적으로 제어하고 프로젝트 일정을 관리하는 **하이브리드 워크플로우 기반의 AI 에이전트 시스템**입니다. 로컬 LLM과 클라우드 LLM을 결합하여 비용을 최적화하고, 샌드박싱과 Human-in-the-Loop(HITL)를 통해 강력한 시스템 보안을 확보했습니다.

---

## ✨ 핵심 기능 (Key Features)

* **하이브리드 의도 라우팅 (Hybrid Intent Routing)**
  * 사용자의 명령을 로컬 LLM(Ollama 기반)이 일상 대화(SIMPLE)와 시스템 제어(COMPLEX)로 1차 분류하여 불필요한 API 호출 비용을 절감합니다.
* **자율형 시스템 제어 (Autonomous Execution)**
  * 상용 LLM 기반의 에이전트가 파일 읽기/쓰기, 터미널 명령어 실행, 작업 경로 변경 등을 스스로 판단하여 수행합니다. 
* **Human-in-the-Loop (HITL) 보안 통제**
  * 치명적인 시스템 제어 명령어 실행 전, Discord 인터랙티브 버튼(UI)을 통해 관리자의 [실행 승인] / [취소]를 강제하여 무단 코드 덮어쓰기나 시스템 접근을 방지합니다.
* **자가 치유 (Self-Healing) 워크플로우**
  * 명령어 실행 중 에러 발생 시, 에이전트가 에러 로그를 분석하여 수정안을 제안합니다. 사용자의 승인을 얻으면 코드를 자동 수정 및 재실행합니다.
* **스마트 스케줄링 연동 (Notion & Google Calendar)**
  * 사용자의 지시에 따라 프로젝트 일정을 노션 데이터베이스 및 구글 캘린더에 자동으로 등록/수정/삭제합니다 (상대적 날짜 계산 지원).

---

## 🏗️ 시스템 아키텍처 (Architecture)

1. **명령 수신 및 라우팅 (Local LLM):** Discord 봇이 명령을 수신하면 로컬 환경의 Ollama(Llama-3 8B)가 의도를 파악하여 SIMPLE / COMPLEX로 라우팅합니다.
2. **계획 수립 및 도구 호출 (Agent Brain):** COMPLEX 작업 시 Pydantic AI 프레임워크와 에이전트가 파이썬 함수(Tools)를 활용해 실행 계획을 수립합니다.
3. **상태 변경 및 승인 대기 (HITL):** 시스템 파일 수정이나 터미널 권한 요청 시 Discord UI에 승인 대기 버튼을 생성합니다.
4. **결과 실행 및 자가 치유:** 승인 시 격리된 환경에서 도구를 실행하며, 에러 발생 시 Context History를 바탕으로 수정안을 제시합니다.

---

## 🛠️ 기술 스택 (Tech Stack)

* **Interface:** Python `discord.py`
* **Agent Framework:** Pydantic AI
* **Local LLM (Router):** Ollama
* **Cloud LLM (Brain):** Groq API (gpt-oss-120b)
* **Integrations:** Notion API, Google Calendar API, `subprocess`, `os`

---

## 📁 디렉토리 구조 (Directory Structure)

```text
lab_ai_agent/
├── .env                        # Discord 토큰, API 키 등 환경변수 보관 (Git 제외)
├── requirements.txt            # 파이썬 패키지 목록
├── bot.py                      # Discord 봇 실행 진입점 (UI 버튼 및 이벤트)
├── core/                       
│   ├── __init__.py
│   ├── router.py               # 로컬 LLM 의도 분류 라우터
│   └── pydantic_agent.py       # Pydantic AI 에이전트 두뇌 및 프롬프트
├── tools/                      
│   ├── __init__.py
│   ├── execution_tools.py      # 터미널 명령어 실행 (한글 인코딩 및 경로 유지)
│   ├── file_tools.py           # 파일 입출력 관리
│   ├── google_tools.py         # 구글 캘린더 연동 로직
│   └── notion_tools.py         # 노션 일정 등록/수정/삭제 로직
└── sandbox/                    
    └── workspace/              # AI에게 마운트해 줄 제한된 안전 작업 폴더