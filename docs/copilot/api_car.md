# API de CAR (Cadastro Ambiental Rural)

## Implementação Realizada - #licenciamentoambiental

### Endpoint: Listar CARs
- **Método**: GET
- **Path**: `/car`
- **Descrição**: Lista todos os CARs cadastrados no sistema com suporte a paginação

### Parâmetros
- **Query params**:
  - `skip` (int, opcional): Número de registros para pular (offset para paginação). Default: 0
  - `limit` (int, opcional): Número máximo de registros a retornar (máximo 100). Default: 100

### Estrutura da Tabela PostgreSQL
```sql
create table public.f_car (
  pkcar bigserial not null,
  fkimovel bigint not null,
  numerocar text not null,
  situacaocar text null default 'Inscrito para Análise'::text,
  pessoacadastrantedocumento text null,
  pessoacadastrantenome text null,
  datainscricao date null,
  situacaopagamento text null default 'Isento'::text,
  etapaatual text null default 'DADOS_GERAIS'::text,
  created_at timestamp with time zone null default now(),
  updated_at timestamp with time zone null default now(),
  constraint f_car_pkey primary key (pkcar)
)
```

### Modelo de Resposta (CarResponse)
```python
class CarResponse(BaseModel):
    """Response model para representar um CAR."""
    id: int = Field(..., alias='pkcar')
    fkimovel: int
    numerocar: str
    situacaocar: Optional[str] = None
    pessoacadastrantedocumento: Optional[str] = None
    pessoacadastrantenome: Optional[str] = None
    datainscricao: Optional[date] = None
    situacaopagamento: Optional[str] = None
    etapaatual: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
```

### Consulta SQL Implementada
```sql
SELECT
  pkcar,
  fkimovel,
  numerocar,
  situacaocar,
  pessoacadastrantedocumento,
  pessoacadastrantenome,
  datainscricao,
  situacaopagamento,
  etapaatual,
  created_at,
  updated_at
FROM {PGSCHEMA}.f_car
ORDER BY pkcar;
```

### Exemplo de Uso

#### Request
```bash
curl -X 'GET' \
  'http://localhost:8000/car?skip=0&limit=10' \
  -H 'accept: application/json'
```

#### Response (200)
```json
[
  {
    "id": 1,
    "fkimovel": 123,
    "numerocar": "CAR-2025-001",
    "situacaocar": "Inscrito para Análise",
    "pessoacadastrantedocumento": "12345678900",
    "pessoacadastrantenome": "João Silva",
    "datainscricao": "2025-10-27",
    "situacaopagamento": "Isento",
    "etapaatual": "DADOS_GERAIS",
    "created_at": "2025-10-27T10:00:00Z",
    "updated_at": "2025-10-27T10:00:00Z"
  }
]
```

### URLs de Acesso
- **Local**: http://localhost:8000/car
- **Swagger UI**: http://localhost:8000/docs
- **Render**: https://fastapi-sandbox.onrender.com/car

### Características
- Paginação automática (máximo 100 registros por página)
- Ordenação por `pkcar` (chave primária)
- Tratamento de erros com mensagens detalhadas
- Seguiu o mesmo padrão dos outros endpoints da API

### Correções Realizadas
1. **Problema inicial**: O modelo estava baseado na estrutura SQL Server do arquivo `f_car.sql`
2. **Solução**: Adaptou o modelo e consulta para a estrutura real do PostgreSQL
3. **Campos corrigidos**: Mudança de `id` para `pkcar`, `imovel_id` para `fkimovel`, etc.

### Tags
- **Tag API**: `car`
- **Tag Projeto**: `#licenciamentoambiental`

### Status
✅ **Implementado e funcionando** - Endpoint criado seguindo o padrão estabelecido, testado e disponível para uso.