# Implementação do Endpoint de Pessoas Jurídicas

Adicione o seguinte código no arquivo `main.py`, logo após o endpoint `/pessoas/cnpj/{cnpj}`:

```python
@app.get("/pessoas/juridicas", response_model=list[PessoaResponse], tags=["pessoas"], summary="Listar pessoas jurídicas ativas")
async def list_pessoas_juridicas():
    """Lista todas as pessoas jurídicas ativas cadastradas."""
    try:
        with pool.connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT p.*, e.nome as municipio, e.uf
                FROM f_pessoa p
                LEFT JOIN f_endereco e ON e.fkpessoa = p.pkpessoa
                WHERE p.cnpj IS NOT NULL
                AND p.cnpj != ''
                AND p.status = 1
                ORDER BY p.razaosocial
            """)
            rows = cur.fetchall()
            if not rows:
                return []
            
            columns = [desc[0] for desc in cur.description]
            result = [dict(zip(columns, row)) for row in rows]
            cur.close()
            return result
    except Exception as e:
        logger.exception("Erro ao listar pessoas jurídicas")
        raise HTTPException(status_code=500, detail=str(e))
```

## Notas importantes:

1. O endpoint usa:
   - O mesmo modelo `PessoaResponse` já existente
   - A mesma pool de conexão do restante da aplicação
   - O mesmo padrão de tratamento de erros

2. A query filtra por:
   - CNPJ não nulo e não vazio
   - Status ativo (1)
   - Ordenação por razão social

3. O endpoint está disponível em:
   ```
   https://fastapi-sandbox-ee3p.onrender.com/pessoas/juridicas
   ```

4. Retorno esperado:
   ```json
   [
       {
           "id": 123,
           "cnpj": "12345678000190",
           "nome": "Empresa XYZ Ltda",
           "razaosocial": "Empresa XYZ Ltda",
           "municipio": "São Paulo",
           "uf": "SP",
           "status": 1
       },
       // ... mais empresas
   ]
   ```

5. Documentação Swagger:
   - Tag: "pessoas"
   - Summary: "Listar pessoas jurídicas ativas"
   - Response model: list[PessoaResponse]