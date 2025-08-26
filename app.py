import os
import asyncio
from aiohttp import web
from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    TurnContext,
    ConversationState,
    MemoryStorage,
)
from botbuilder.schema import Activity, ActivityTypes

# =======================================
# 🔹 Configurações
# =======================================

# ID do app (bot) que está no catálogo do Teams
BOT_APP_ID = "fda5c020-a78d-4ee9-98be-d1e7b3e84654"
#BOT_APP_ID = "6a6b454f-adee-4896-996b-315674904035"

# Usuário alvo
USER_EMAIL = "afsantos@STESystems.onmicrosoft.com"

APP_ID = os.environ.get("MicrosoftAppId", "6a6b454f-adee-4896-996b-315674904035")
APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "yeL8Q~AuGRiJ5jWAaLvUF~Hmp~sb6coCjzgHOaV5")

adapter_settings = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
adapter = BotFrameworkAdapter(adapter_settings)

memory = MemoryStorage()
conversation_state = ConversationState(memory)

# Armazena referências de conversa
CONVERSATION_REFERENCES = {}


# =========================
# 🔹 BOT BÁSICO
# =========================
class TeamsBot:
    async def on_turn(self, turn_context: TurnContext):
        if turn_context.activity.type == ActivityTypes.message:
            await turn_context.send_activity(f"👋 Você disse: {turn_context.activity.text}")


bot = TeamsBot()


# =========================
# 🔹 ENDPOINT PRINCIPAL
# =========================
async def messages(req: web.Request) -> web.Response:
    body = await req.json()
    activity = Activity().deserialize(body)

    auth_header = req.headers.get("Authorization", "")
    response = await adapter.process_activity(activity, auth_header, bot.on_turn)
    if response:
        return web.json_response(data=response.body, status=response.status)
    return web.Response(status=201)


# =========================
# 🔹 ENVIO PROATIVO
# =========================
async def send_proactive(conversation_reference):
    async def callback(turn_context: TurnContext):
        await turn_context.send_activity("🤖 Olá! Esta é uma mensagem proativa do bot no Teams.")

    await adapter.continue_conversation(conversation_reference, callback, APP_ID)


# =========================
# 🔹 RODAR SERVIDOR
# =========================
app = web.Application()
app.router.add_post("/api/messages", messages)

if __name__ == "__main__":
    try:
        # Azure define a porta dinamicamente
        port = int(os.environ.get("PORT", 3978))
        web.run_app(app, host="0.0.0.0", port=port)
    except Exception as e:
        raise e
