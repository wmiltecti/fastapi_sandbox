# API de Pessoas Jurídicas

## Novo Endpoint: Listar Pessoas Jurídicas

### Endpoint
```
GET /pessoas/juridicas
```

### Descrição
Lista todas as pessoas jurídicas cadastradas no sistema.

### Response Model
Usa o mesmo PessoaResponse existente, focando nos campos relevantes para PJ:
- id (pkpessoa)
- cnpj
- razaosocial (usado como nome)
- outros campos do endereço

### Implementação

```python
@app.get("/pessoas/juridicas", response_model=list[PessoaResponse], tags=["pessoas"], 
         summary="Listar pessoas jurídicas")
async def list_pessoas_juridicas():
    """Lista todas as pessoas jurídicas cadastradas."""
    try:
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                query = """
                    SELECT p.*, e.nome as municipio, e.uf
                    FROM f_pessoa p
                    LEFT JOIN f_endereco e ON e.fkpessoa = p.pkpessoa
                    WHERE p.cnpj IS NOT NULL
                    AND p.cnpj != ''
                    ORDER BY p.razaosocial
                """
                await cur.execute(query)
                rows = await cur.fetchall()
                return [dict(row) for row in rows]
    except Exception as e:
        logger.exception("Erro ao listar pessoas jurídicas")
        raise HTTPException(status_code=500, detail=str(e))
```

### URL de Acesso
```
https://fastapi-sandbox-ee3p.onrender.com/pessoas/juridicas
```

### Retorno Esperado
```json
[
    {
        "id": 123,
        "cnpj": "12345678000190",
        "nome": "Empresa XYZ Ltda",
        "razaosocial": "Empresa XYZ Ltda",
        "municipio": "São Paulo",
        "uf": "SP"
        // ... outros campos do PessoaResponse
    },
    // ... mais empresas
]
```