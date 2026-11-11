import os
import requests
from pydantic import BaseModel, Field
from typing import Literal

class NotionScheduleInput(BaseModel):
    task_name: str = Field(description="할 일 이름")
    start_date: str = Field(description="시작일 (YYYY-MM-DD)")
    end_date: str = Field(default=None, description="종료일")
    priority: Literal["매우중요", "중요", "보통", "부차적"] = Field(default="보통")
    status: Literal["진행전", "진행중", "진행완료", "연기", "취소"] = Field(default="진행전")

def add_notion_schedule(task_name: str, start_date: str, end_date: str = None, priority: str = "보통", status: str = "진행전") -> str:
    notion_api_key = os.getenv('NOTION_API_KEY')
    database_id = os.getenv('NOTION_DATABASE_ID')
    if not notion_api_key or not database_id: return "노션 설정 오류."
    headers = {"Authorization": f"Bearer {notion_api_key}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
    
    date_data = {"start": start_date}
    if end_date: date_data["end"] = end_date
    data = {
        "parent": {"database_id": database_id},
        "properties": {
            "이름": {"title": [{"text": {"content": task_name}}]},
            "날짜": {"date": date_data},
            "중요도": {"select": {"name": priority}},
            "진행상황": {"select": {"name": status}}
        }
    }
    try:
        res = requests.post("https://api.notion.com/v1/pages", headers=headers, json=data)
        if res.status_code == 200: return f"노션 등록 완료: '{task_name}'"
        return f"노션 등록 실패: {res.text}"
    except Exception as e:
        return f"노션 통신 오류: {e}"

def delete_notion_schedule(task_name: str) -> str:
    notion_api_key = os.getenv('NOTION_API_KEY')
    database_id = os.getenv('NOTION_DATABASE_ID')
    headers = {"Authorization": f"Bearer {notion_api_key}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
    query_url = f"https://api.notion.com/v1/databases/{database_id}/query"
    query_data = {"filter": {"property": "이름", "title": {"equals": task_name}}}
    
    try:
        search_res = requests.post(query_url, headers=headers, json=query_data)
        if search_res.status_code != 200: return "검색 실패"
        results = search_res.json().get("results", [])
        if not results: return "일정을 찾을 수 없습니다."
        
        count = 0
        for page in results:
            requests.patch(f"https://api.notion.com/v1/pages/{page['id']}", headers=headers, json={"archived": True})
            count += 1
        return f"노션에서 '{task_name}' {count}개 삭제 완료."
    except Exception as e:
        return f"오류: {e}"

def update_notion_schedule(task_name: str, priority: str = None, status: str = None) -> str:
    notion_api_key = os.getenv('NOTION_API_KEY')
    database_id = os.getenv('NOTION_DATABASE_ID')
    headers = {"Authorization": f"Bearer {notion_api_key}", "Content-Type": "application/json", "Notion-Version": "2022-06-28"}
    query_url = f"https://api.notion.com/v1/databases/{database_id}/query"
    query_data = {"filter": {"property": "이름", "title": {"equals": task_name}}}
    
    try:
        search_res = requests.post(query_url, headers=headers, json=query_data)
        if search_res.status_code != 200: return "검색 실패"
        results = search_res.json().get("results", [])
        if not results: return "일정을 찾을 수 없습니다."
        
        props = {}
        if priority: props["중요도"] = {"select": {"name": priority}}
        if status: props["진행상황"] = {"select": {"name": status}}
        if not props: return "변경할 속성이 없습니다."

        for page in results:
            requests.patch(f"https://api.notion.com/v1/pages/{page['id']}", headers=headers, json={"properties": props})
        return f"노션 '{task_name}' 수정 완료."
    except Exception as e:
        return f"오류: {e}"