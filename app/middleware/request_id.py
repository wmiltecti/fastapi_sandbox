"""
Middleware para injetar Request-ID único em cada requisição.
Adiciona header X-Request-ID na resposta para rastreamento.
"""
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware que adiciona um Request-ID único (UUID4) em cada requisição.
    
    O ID é injetado no header X-Request-ID da resposta, permitindo
    rastreamento e correlação de logs.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Gerar UUID único para esta requisição
        request_id = str(uuid.uuid4())
        
        # Processar requisição
        response = await call_next(request)
        
        # Adicionar Request-ID no header da resposta
        response.headers["X-Request-ID"] = request_id
        
        return response
