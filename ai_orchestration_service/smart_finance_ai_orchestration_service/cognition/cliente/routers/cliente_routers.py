# routers/cliente_routers.py
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, Request

from cognition.cliente.domain.cliente import Cliente
from cognition.cliente.service import ClienteService

# 1) o router precisa existir ANTES de qualquer @cliente_router.get/post
cliente_router = APIRouter(prefix="/cliente", tags=["cliente"])

# 2) o provider precisa existir ANTES de ser usado em Depends(...)
def get_cliente_service(request: Request) -> ClienteService:
    return request.app.state.cliente_service

# 3) schemas do endpoint de chat (desserialização + validação declarativa)
class ChatRequest(BaseModel):
    cliente_id: int
    mensagem: str = Field(min_length=1, max_length=4000)

class ChatResponse(BaseModel):
    resposta: str

# 4) endpoints
@cliente_router.get("/{cliente_id}")
async def get_cliente(
    cliente_id: int,
    service: ClienteService = Depends(get_cliente_service),
) -> Cliente:
    cliente = await service.profile(cliente_id)
    if cliente is None:
        raise HTTPException(status_code=404, detail="cliente não encontrado")
    return cliente

@cliente_router.post("/chat", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    service: ClienteService = Depends(get_cliente_service),
) -> ChatResponse:
    resultado = await service.chat(req.cliente_id, req.mensagem)
    return ChatResponse(resposta=resultado)