# Teste de Integração - Blockchain API

Este arquivo demonstra como testar o endpoint de blockchain com diferentes cenários.

## Pré-requisitos

Certifique-se de que o arquivo `.env` contém:
```env
BLOCKCHAIN_DSKEY=7BBE6BED278B99E193E104B95331C11AAFB19F22DFB7877C991552D15293C622030D40
```

## Teste 1: Registro de Pessoa Física (Exemplo Completo)

### Request (cURL)
```bash
curl -X 'POST' \
  'http://localhost:8000/blockchain/register' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "IdBlockchain": 1,
  "Data": {
    "pkpessoa": "2001327",
    "fkuser": "264637",
    "tipo": "0",
    "status": "",
    "cpf": "859.965.722-49",
    "nome": "ABIMAEL RIBEIRO DE SOUZA",
    "datanascimento": "1986-05-04T00:00:00",
    "naturalidade": "",
    "nacionalidade": "",
    "estadocivil": "",
    "sexo": "0",
    "rg": "00.072.914-0",
    "orgaoemissor": "SESDEC",
    "fkestadoemissor": "22",
    "telefone": "(69) 99921-7501",
    "email": "abimael.ribeiro@sedam.ro.gov.br",
    "nomepessoa": "ABIMAEL RIBEIRO DE SOUZA",
    "numeroidentificacao": "859.965.722-49",
    "nomerazao": "ABIMAEL RIBEIRO DE SOUZA",
    "dataultimaalteracao": "2025-06-16T11:23:03.323000"
  },
  "Fields": [
    {
      "NmField": "LicenciamentoAmbientalPessoaFisica",
      "DsValue": "Pessoa fisica do licenciamento ambiental"
    }
  ]
}'
```

### Request (Python)
```python
import httpx
import json

payload = {
    "IdBlockchain": 1,
    "Data": {
        "pkpessoa": "2001327",
        "cpf": "859.965.722-49",
        "nome": "ABIMAEL RIBEIRO DE SOUZA",
        "email": "abimael.ribeiro@sedam.ro.gov.br"
    },
    "Fields": [
        {
            "NmField": "LicenciamentoAmbientalPessoaFisica",
            "DsValue": "Pessoa fisica do licenciamento ambiental"
        }
    ]
}

response = httpx.post(
    "http://localhost:8000/blockchain/register",
    json=payload,
    timeout=30.0
)

print(f"Status Code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
```

### Expected Response (Sucesso)
```json
{
  "success": true,
  "message": "Dados registrados no blockchain com sucesso",
  "blockchain_response": {
    // Resposta da API Continuus
  },
  "error": null
}
```

---

## Teste 2: Registro Simplificado

### Request
```bash
curl -X 'POST' \
  'http://localhost:8000/blockchain/register' \
  -H 'Content-Type: application/json' \
  -d '{
  "IdBlockchain": 2,
  "Data": {
    "record_type": "teste",
    "timestamp": "2025-10-27T15:00:00"
  },
  "Fields": [
    {
      "NmField": "TipoRegistro",
      "DsValue": "Teste de integração"
    }
  ]
}'
```

---

## Teste 3: Verificar Erro de Autenticação

Para testar erro de autenticação, remova temporariamente a variável `BLOCKCHAIN_DSKEY` do `.env`:

### Request
```bash
curl -X 'POST' \
  'http://localhost:8000/blockchain/register' \
  -H 'Content-Type: application/json' \
  -d '{
  "IdBlockchain": 3,
  "Data": {"teste": "valor"},
  "Fields": [{"NmField": "Teste", "DsValue": "Teste"}]
}'
```

### Expected Response (Erro de Configuração)
```json
{
  "success": false,
  "message": "Erro de configuração: chave de autenticação não encontrada",
  "blockchain_response": null,
  "error": "BLOCKCHAIN_DSKEY não está configurada no arquivo .env"
}
```

---

## Teste 4: Via Swagger UI

1. Acesse: http://localhost:8000/docs
2. Expanda a seção **blockchain**
3. Clique em **POST /blockchain/register**
4. Clique em **Try it out**
5. Use o payload de exemplo:

```json
{
  "IdBlockchain": 1,
  "Data": {
    "pkpessoa": "2001327",
    "cpf": "859.965.722-49",
    "nome": "João Silva"
  },
  "Fields": [
    {
      "NmField": "LicenciamentoAmbientalPessoaFisica",
      "DsValue": "Pessoa fisica do licenciamento ambiental"
    }
  ]
}
```

6. Clique em **Execute**
7. Verifique a resposta

---

## Verificação de Logs

Após executar os testes, verifique os logs no terminal para acompanhar:

```
INFO: Enviando dados para blockchain: IdBlockchain=1
DEBUG: Payload completo: {...}
INFO: Blockchain registrado com sucesso: IdBlockchain=1
```

Ou em caso de erro:
```
ERROR: Erro ao comunicar com blockchain API: Erro HTTP 401: Unauthorized
```

---

## Troubleshooting

### Problema: "Missing dsKey header"
**Causa**: A variável `BLOCKCHAIN_DSKEY` não está configurada ou o servidor não foi reiniciado.

**Solução**:
1. Verifique se `BLOCKCHAIN_DSKEY` está no `.env`
2. Reinicie o servidor (Ctrl+C e rode novamente)

### Problema: "Erro de conexão"
**Causa**: A API do blockchain pode estar indisponível.

**Solução**:
1. Verifique a conectividade com: `http://continuus.miltecti.com.br`
2. Verifique se não há firewall bloqueando

### Problema: "Invalid payload"
**Causa**: O formato do payload está incorreto.

**Solução**:
1. Certifique-se de que `IdBlockchain`, `Data` e `Fields` estão presentes
2. Valide o JSON em um validador online

---

## Headers Enviados

O endpoint automaticamente adiciona os seguintes headers:

```
Content-Type: application/json
dsKey: 7BBE6BED278B99E193E104B95331C11AAFB19F22DFB7877C991552D15293C622030D40
```

**Nota**: O valor do `dsKey` é carregado da variável de ambiente e pode ser alterado sem modificar o código.

---

## Alterando a Chave de Autenticação

Se a chave `dsKey` for alterada futuramente:

1. Edite o arquivo `.env`:
```env
BLOCKCHAIN_DSKEY=NOVA_CHAVE_AQUI
```

2. Reinicie o servidor:
```bash
# Pare o servidor (Ctrl+C)
# Inicie novamente
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Não é necessário alterar código!** ✅
