# Troubleshooting - Integração Blockchain Continuus

**Data:** 27 de Outubro de 2025  
**Status:** Em investigação - Aguardando especificações da API

---

## ✅ O que está funcionando

### 1. Autenticação
- ✅ Header `dsKey` está **correto**
- ✅ Chave está **ativa e válida**
- ✅ Endpoint de verificação funcionando:

```bash
curl -X 'GET' \
  'http://continuus.miltecti.com.br/continuus_api/api/Auth/CheckAuth' \
  -H 'dsKey: 7BBE6BED278B99E193E104B95331C11AAFB19F22DFB7877C991552D15293C622030D40'
```

**Response:**
```json
{
  "HTTPStatus": 200,
  "authenticated": true,
  "message": "Chave válida."
}
```

### 2. Nossa Implementação
- ✅ FastAPI enviando headers corretamente
- ✅ Payload sendo serializado corretamente
- ✅ Variável de ambiente `BLOCKCHAIN_DSKEY` configurada
- ✅ Timeout e tratamento de erros implementados

---

## ❌ O que NÃO está funcionando

### Endpoint: POST /api/Block/Register

**Erro recebido:**
```json
{
  "HTTPStatus": 400,
  "Executed": false,
  "ValidToken": false,
  "Message": "Value cannot be null. (Parameter 's')",
  "Block": null
}
```

### Testes realizados:

#### Teste 1: Payload completo do arquivo pessoafisica.json
```bash
Status: 400
Message: "Value cannot be null. (Parameter 's')"
```

#### Teste 2: Payload simplificado (somente campos principais)
```json
{
  "IdBlockchain": 1,
  "Data": {
    "pkpessoa": "2001327",
    "cpf": "859.965.722-49",
    "nome": "ABIMAEL RIBEIRO DE SOUZA"
  },
  "Fields": [
    {
      "NmField": "LicenciamentoAmbientalPessoaFisica",
      "DsValue": "Pessoa fisica do licenciamento ambiental"
    }
  ]
}
```
**Resultado:** Mesmo erro 400

#### Teste 3: Variações de headers
Testamos todas as variações de nome de header:
- `dskey` → 400 (reconhece header, mas chave inválida no contexto)
- `dsKey` → 400 (reconhece header, mas chave inválida no contexto)
- `DsKey` → 400 (reconhece header, mas chave inválida no contexto)
- `DSKEY` → 400 (reconhece header, mas chave inválida no contexto)
- `ds-key` → 401 "Missing dsKey header" (não reconhece)
- `DS-KEY` → 401 "Missing dsKey header" (não reconhece)

**Conclusão:** O header correto é `dsKey` (camelCase sem hífen)

---

## 🔍 Análise do Erro

### "Value cannot be null. (Parameter 's')"

Possíveis causas:
1. **Campo obrigatório faltando** no payload
2. **Formato de dados incorreto** em algum campo
3. **Validação interna** da API rejeitando o payload
4. **Parâmetro 's'** pode ser um campo interno que a API espera

### Observações:
- ✅ Autenticação está OK (`CheckAuth` retorna sucesso)
- ❌ Mas `ValidToken:false` no erro do registro
- ❓ Pode haver **dois níveis de autenticação** ou **validação adicional** no endpoint de registro

---

## 📋 Informações Necessárias da API Continuus

Para resolver este problema, precisamos da equipe responsável pela API Continuus:

### 1. Exemplo Funcional ⭐ URGENTE
Por favor, forneçam um exemplo **completo** de requisição que funcione:
```bash
# Exemplo de curl ou Postman que FUNCIONA
curl -X 'POST' \
  'http://continuus.miltecti.com.br/continuus_api/api/Block/Register' \
  -H 'Content-Type: application/json' \
  -H 'dsKey: CHAVE_AQUI' \
  -d '{...payload completo...}'
```

### 2. Documentação da API
- Quais campos são **obrigatórios** em `Data`?
- Quais campos são **obrigatórios** em `Fields`?
- Há algum campo **adicional** não mencionado?
- Qual o formato esperado para datas, números, etc.?

### 3. Especificação do Erro
- O que significa **"Parameter 's'"**?
- Por que `ValidToken` é `false` se a autenticação passa?
- Há alguma **validação adicional** além do header `dsKey`?

### 4. Ambiente
- Estamos usando o ambiente **correto** (produção/homologação)?
- A chave tem **permissões suficientes** para registrar blocos?
- Há algum **limite de rate** ou **quota**?

---

## 🧪 Testes que Funcionam

### Verificação de Autenticação
```python
import httpx

response = httpx.get(
    "http://continuus.miltecti.com.br/continuus_api/api/Auth/CheckAuth",
    headers={"dsKey": "7BBE6BED278B99E193E104B95331C11AAFB19F22DFB7877C991552D15293C622030D40"}
)
print(response.json())
# {"HTTPStatus":200,"authenticated":true,"message":"Chave válida."}
```

### Nossa Implementação Atual
```python
# Endpoint: POST /blockchain/register
# Headers sendo enviados:
# - Content-Type: application/json
# - dsKey: 7BBE6BED278B99E193E104B95331C11AAFB19F22DFB7877C991552D15293C622030D40

# Status: Enviando corretamente, mas API retorna 400
```

---

## 📊 Código de Status Recebidos

| Endpoint | Status | Mensagem | Diagnóstico |
|----------|--------|----------|-------------|
| GET /Auth/CheckAuth | 200 | "authenticated":true | ✅ Autenticação OK |
| POST /Block/Register | 400 | "ValidToken":false | ❌ Payload inválido |
| POST /Block/Register (sem dsKey) | 401 | "Missing dsKey header" | ❌ Header ausente |

---

## 🔧 Próximos Passos

### Imediato:
1. [ ] Contatar equipe Continuus para exemplo funcional
2. [ ] Revisar documentação da API (se disponível)
3. [ ] Validar permissões da chave

### Após resposta da equipe:
1. [ ] Ajustar payload conforme especificação
2. [ ] Adicionar validação de campos obrigatórios
3. [ ] Testar com dados reais
4. [ ] Atualizar documentação

---

## 📝 Informações Técnicas

### Ambiente
- **API URL**: http://continuus.miltecti.com.br/continuus_api/api/Block/Register
- **Servidor**: Microsoft-IIS/10.0
- **Framework**: ASP.NET
- **Timeout**: 30 segundos
- **Método**: POST
- **Content-Type**: application/json

### Nossa Stack
- **Framework**: FastAPI 3.0.0
- **HTTP Client**: httpx (assíncrono)
- **Python**: 3.11
- **Deploy**: Render + Local

### Chave de Autenticação
- **Variável**: BLOCKCHAIN_DSKEY
- **Tamanho**: 70 caracteres
- **Formato**: Hexadecimal
- **Status**: ✅ Válida (confirmado via CheckAuth)

---

## 📞 Contatos para Suporte

**Equipe Continuus:**
- [ ] Fornecer contato do responsável pela API
- [ ] Canal de suporte (email, Slack, etc.)
- [ ] Documentação online (se disponível)

---

## 🎯 Resumo Executivo

**Status atual:** Integração parcialmente implementada
- ✅ Autenticação funcionando
- ✅ Código pronto para enviar requisições
- ❌ Payload sendo rejeitado pela API
- ⏳ Aguardando especificações técnicas da equipe Continuus

**Bloqueador:** Falta de documentação e exemplo funcional da API de registro de blocos.

**Próxima ação:** Contatar equipe Continuus para obter exemplo de payload válido.

---

**Atualizado em:** 27/10/2025 - 17:00  
**Por:** Análise técnica integração blockchain
