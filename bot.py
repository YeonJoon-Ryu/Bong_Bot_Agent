import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# 우리가 만든 모듈들 불러오기
from core.router import classify_intent, generate_simple_response
from core.pydantic_agent import run_complex_task

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(
    command_prefix="!", 
    intents=intents,
    allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False)
)

# --- 1. 플랫폼 선택 버튼 UI (노션 / 구글 캘린더) ---
class DestinationSelectView(discord.ui.View):
    def __init__(self, original_command: str):
        super().__init__(timeout=None)
        self.original_command = original_command

    @discord.ui.button(label="📝 노션", style=discord.ButtonStyle.primary)
    async def btn_notion(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_choice(interaction, "노션으로 진행해 줘.")

    @discord.ui.button(label="📅 구글 캘린더", style=discord.ButtonStyle.primary)
    async def btn_google(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_choice(interaction, "구글 캘린더로 진행해 줘.")

    @discord.ui.button(label="✅ 둘 다", style=discord.ButtonStyle.success)
    async def btn_both(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_choice(interaction, "노션과 구글 캘린더 둘 다 진행해 줘.")

    async def process_choice(self, interaction: discord.Interaction, choice_text: str):
        await interaction.response.edit_message(content=f"⚙️ **선택 완료 ({choice_text}):** 에이전트가 작업을 수행 중입니다...", view=None)
        
        combined_command = f"{self.original_command}\n[사용자 추가 지시: {choice_text}]"
        agent_response = await run_complex_task(combined_command)
        
        # 로그 저장
        self.save_log(combined_command, agent_response)

        await interaction.channel.send(
            f"{interaction.user.mention} 🤖 **에이전트 최종 보고:**\n{agent_response}",
            allowed_mentions=discord.AllowedMentions(users=True)
        )

    def save_log(self, command, response):
        try:
            with open("chat_history_log.txt", "a", encoding="utf-8") as f:
                f.write(f"--- 명령어 ---\n{command}\n\n--- 에이전트 응답 ---\n{response}\n\n{'='*50}\n\n")
        except Exception as e:
            print(f"로그 저장 실패: {e}")

# --- 2. 시스템 제어 승인/거절 버튼 UI ---
class ApprovalView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = None

    @discord.ui.button(label="✅ 실행 승인", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        await interaction.response.defer()
        self.stop()

    @discord.ui.button(label="❌ 실행 취소", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = False
        await interaction.response.defer()
        self.stop()

# --- 3. 에러 복구 제안 (Self-Healing) 승인/거절 버튼 UI ---
class SelfHealingView(discord.ui.View):
    def __init__(self, original_command: str, agent_proposal: str):
        super().__init__(timeout=None)
        self.original_command = original_command
        self.agent_proposal = agent_proposal

    @discord.ui.button(label="✅ 제안 승인 및 자동 수정", style=discord.ButtonStyle.green)
    async def confirm_healing(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content=f"🛠️ **자가 치유 시작:** 승인되었습니다. 에이전트가 제안한 방식대로 코드를 수정하고 재실행합니다...", 
            view=None
        )
        
        # 에이전트가 제안한 해결책을 포함하여 명령 재수행
        combined_command = f"{self.original_command}\n[사용자 추가 지시: 네가 제안한 해결책({self.agent_proposal})대로 코드를 수정하고 다시 실행해 줘.]"
        
        agent_response = await run_complex_task(combined_command)
        
        # 결과를 chat_history_log.txt 파일에 로컬 저장
        self.save_log(combined_command, agent_response)

        await interaction.channel.send(
            f"{interaction.user.mention} 🤖 **자가 치유 결과 보고:**\n{agent_response}",
            allowed_mentions=discord.AllowedMentions(users=True)
        )

    @discord.ui.button(label="❌ 제안 거절 (내가 직접 수정함)", style=discord.ButtonStyle.red)
    async def cancel_healing(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content="🛑 **자가 치유 취소됨:** 에이전트의 수정 제안을 거절했습니다. 수동으로 명령을 내려주세요.", 
            view=None
        )

    def save_log(self, command, response):
        try:
            with open("chat_history_log.txt", "a", encoding="utf-8") as f:
                f.write(f"--- 자가 치유 명령어 ---\n{command}\n\n--- 에이전트 응답 ---\n{response}\n\n{'='*50}\n\n")
        except Exception as e:
            print(f"로그 저장 실패: {e}")

@bot.event
async def on_ready():
    print(f"✅ {bot.user} 봇이 성공적으로 준비되었습니다!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    print(f"[{message.author}] 수신된 명령: {message.content}")

    content = message.content.strip()
    intent = "SIMPLE"

    if content.startswith("!"):
        intent = "COMPLEX"
        message.content = content[1:].strip() 
        print(f"🛠️ [수동 지정] 사용자가 강제로 COMPLEX 작업으로 지정했습니다.")
    else:
        intent = await classify_intent(content)
    
    if intent == "SIMPLE":
        answer = await generate_simple_response(message.content)
        await message.channel.send(f"🧠 {answer}", allowed_mentions=discord.AllowedMentions.none())
        
    elif intent == "COMPLEX":
        view = ApprovalView()
        confirm_msg = await message.channel.send(
            f"⚠️ **시스템 제어 경고:**\n`{message.content}`\n\n이 명령을 에이전트에게 전달하여 시스템을 제어하거나 캘린더에 접근하도록 허가하시겠습니까?", 
            view=view,
            allowed_mentions=discord.AllowedMentions.none()
        )
        
        await view.wait()
        
        if view.value is True:
            await confirm_msg.edit(content="⚙️ **승인 완료:** 에이전트가 코드를 작성하고 시스템을 제어 중입니다...", view=None, allowed_mentions=discord.AllowedMentions.none())
            
            # 에이전트 실행
            agent_response = await run_complex_task(message.content)
            
            # 대화 로그 로컬 저장
            try:
                with open("chat_history_log.txt", "a", encoding="utf-8") as f:
                    f.write(f"--- 명령어 ---\n{message.content}\n\n--- 에이전트 응답 ---\n{agent_response}\n\n{'='*50}\n\n")
            except Exception as e:
                print(f"로그 저장 실패: {e}")
            
            # 1. 캘린더 플랫폼 선택이 필요한 경우
            if ("노션" in agent_response and "구글" in agent_response) and ("어디" in agent_response or "어느" in agent_response or "옵션" in agent_response or "저장" in agent_response or "삭제" in agent_response):
                select_view = DestinationSelectView(message.content)
                await message.channel.send(
                    f"{message.author.mention} 📍 **플랫폼 선택:**\n어느 서비스로 작업을 진행할까요?", 
                    view=select_view,
                    allowed_mentions=discord.AllowedMentions(users=True)
                )
            # 2. 에러 감지 및 해결책 제안 (자가 치유 뷰 출력)
            elif "오류" in agent_response and ("수정" in agent_response or "해결" in agent_response or "진행할까요" in agent_response or "볼까요" in agent_response):
                healing_view = SelfHealingView(message.content, agent_response)
                await message.channel.send(
                    f"{message.author.mention} ⚠️ **에러 감지 및 해결책 제안:**\n{agent_response}\n\n이 제안대로 에이전트가 코드를 자동 수정하도록 허가하시겠습니까?", 
                    view=healing_view,
                    allowed_mentions=discord.AllowedMentions(users=True)
                )
            # 3. 일반적인 완료 보고 (@ 멘션 포함)
            else:
                await message.channel.send(
                    f"{message.author.mention} 🤖 **에이전트 최종 보고:**\n{agent_response}",
                    allowed_mentions=discord.AllowedMentions(users=True)
                )
        else:
            await confirm_msg.edit(content="❌ **작업 취소됨:** 관리자가 실행을 거절하여 시스템이 안전하게 보호되었습니다.", view=None, allowed_mentions=discord.AllowedMentions.none())

    await bot.process_commands(message)

if __name__ == "__main__":
    bot_token = os.getenv("DISCORD_BOT_TOKEN")
    if not bot_token:
        print("에러: .env 파일에 DISCORD_BOT_TOKEN이 없습니다.")
    else:
        bot.run(bot_token)