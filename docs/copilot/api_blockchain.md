# API de Blockchain - Integração Continuus

## Implementação Realizada - #licenciamentoambiental

### Endpoint: Registrar dados no Blockchain
- **Método**: POST
- **Path**: `/blockchain/register`
- **Descrição**: Registra dados no blockchain Continuus para auditoria e rastreabilidade

---

## Estrutura da Requisição

### Request Body (BlockchainRegisterRequest)

```json
{
  "IdBlockchain": 1,
  "Data": {
    "pkpessoa": "2001327",
    "fkuser": "264637",
    "tipo": "0",
    "status": "",
    "cpf": "859.965.722-49",
    "nome": "ABIMAEL RIBEIRO DE SOUZA",
    "datanascimento": "1986-05-04T00:00:00",
    "rg": "00.072.914-0",
    "orgaoemissor": "SESDEC",
    "telefone": "(69) 99921-7501",
    "email": "abimael.ribeiro@sedam.ro.gov.br",
    "nomepessoa": "ABIMAEL RIBEIRO DE SOUZA",
    "numeroidentificacao": "859.965.722-49"
  },
  "Fields": [
    {
      "NmField": "LicenciamentoAmbientalPessoaFisica",
      "DsValue": "Pessoa fisica do licenciamento ambiental"
    }
  ]
}
```

### Campos do Modelo

#### BlockchainRegisterRequest
- **IdBlockchain** (int, obrigatório): ID único do registro no blockchain
- **Data** (object, obrigatório): Objeto com os dados a serem registrados
- **Fields** (array, obrigatório): Lista de campos customizados

#### BlockchainField
- **NmField** (string, obrigatório): Nome do campo customizado
- **DsValue** (string, obrigatório): Descrição ou valor do campo

---

## Estrutura da Resposta

### Response Body (BlockchainRegisterResponse)

#### Sucesso (200)
```json
{
  "success": true,
  "message": "Dados registrados no blockchain com sucesso",
  "blockchain_response": {
    "transactionHash": "0xabc123...",
    "blockNumber": 12345,
    "status": "confirmed"
  },
  "error": null
}
```

#### Erro (200 com success: false)
```json
{
  "success": false,
  "message": "Erro ao registrar no blockchain",
  "blockchain_response": null,
  "error": "Erro HTTP 500: Internal Server Error"
}
```

### Campos do Response
- **success** (boolean): Indica se o registro foi bem sucedido
- **message** (string): Mensagem descritiva do resultado
- **blockchain_response** (object, opcional): Resposta da API do blockchain
- **error** (string, opcional): Detalhes do erro, se houver

---

## Integração com API Externa

### URL da API Continuus
```
http://continuus.miltecti.com.br/continuus_api/api/Block/Register
```

### Autenticação
A API requer autenticação através de um header customizado:

**Header obrigatório:**
- **dsKey**: Chave de autenticação do cliente

**Configuração:**
A chave é armazenada na variável de ambiente `BLOCKCHAIN_DSKEY` no arquivo `.env`:
```env
BLOCKCHAIN_DSKEY=7BBE6BED278B99E193E104B95331C11AAFB19F22DFB7877C991552D15293C622030D40
```

⚠️ **IMPORTANTE**: Esta chave pode ser alterada futuramente. Para atualizar, basta modificar o valor no arquivo `.env` e reiniciar a aplicação.

### Configuração da Requisição
- **Método HTTP**: POST
- **Content-Type**: application/json
- **Headers**: 
  - `Content-Type: application/json`
  - `dsKey: <valor_da_chave>`
- **Timeout**: 30 segundos

---

## Variáveis de Ambiente

Adicione ao arquivo `.env`:

```env
# Blockchain API Key
BLOCKCHAIN_DSKEY=7BBE6BED278B99E193E104B95331C11AAFB19F22DFB7877C991552D15293C622030D40
```
- **Content-Type**: application/json
- **Timeout**: 30 segundos

---

## Exemplos de Uso

### Exemplo 1: Registrar Pessoa Física

#### Request
```bash
curl -X 'POST' \
  'http://localhost:8000/blockchain/register' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
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
}'
```

#### Response
```json
{
  "success": true,
  "message": "Dados registrados no blockchain com sucesso",
  "blockchain_response": {
    "status": "registered"
  }
}
```

---

### Exemplo 2: Registrar CAR (Cadastro Ambiental Rural)

#### Request
```bash
curl -X 'POST' \
  'http://localhost:8000/blockchain/register' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "IdBlockchain": 2,
  "Data": {
    "pkcar": "12345",
    "numerocar": "CAR-2025-001",
    "situacaocar": "Inscrito para Análise",
    "pessoacadastrantedocumento": "859.965.722-49",
    "pessoacadastrantenome": "ABIMAEL RIBEIRO DE SOUZA",
    "datainscricao": "2025-10-27"
  },
  "Fields": [
    {
      "NmField": "LicenciamentoAmbientalCAR",
      "DsValue": "Cadastro Ambiental Rural"
    }
  ]
}'
```

---

### Exemplo 3: Registrar Mudança de Status

#### Request
```bash
curl -X 'POST' \
  'http://localhost:8000/blockchain/register' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "IdBlockchain": 3,
  "Data": {
    "numerocar": "CAR-2025-001",
    "status_anterior": "DADOS_GERAIS",
    "status_novo": "EM_ANALISE",
    "data_mudanca": "2025-10-27T14:30:00",
    "usuario_responsavel": "ABIMAEL RIBEIRO DE SOUZA"
  },
  "Fields": [
    {
      "NmField": "MudancaStatusCAR",
      "DsValue": "Mudança de status do CAR para auditoria"
    }
  ]
}'
```

---

## Tratamento de Erros

### Tipos de Erro

#### 1. Erro de Configuração (Chave não configurada)
```json
{
  "success": false,
  "message": "Erro de configuração: chave de autenticação não encontrada",
  "error": "BLOCKCHAIN_DSKEY não está configurada no arquivo .env"
}
```

**Solução**: Adicione a variável `BLOCKCHAIN_DSKEY` no arquivo `.env`

#### 2. Erro de Autenticação (401/403)
```json
{
  "success": false,
  "message": "Erro ao registrar no blockchain",
  "error": "Erro HTTP 401: Unauthorized - Invalid dsKey"
}
```

**Solução**: Verifique se a chave `BLOCKCHAIN_DSKEY` está correta

#### 3. Erro de Conexão
```json
{
  "success": false,
  "message": "Erro de conexão com blockchain",
  "error": "Erro de conexão: Connection timeout"
}
```

#### 4. Erro HTTP (4xx/5xx)
```json
{
  "success": false,
  "message": "Erro ao registrar no blockchain",
  "error": "Erro HTTP 400: Bad Request - Invalid payload format"
}
```

#### 5. Erro Inesperado
```json
{
  "success": false,
  "message": "Erro inesperado",
  "error": "KeyError: 'required_field'"
}
```

---

## Logs e Monitoramento

### Logs Gerados

O endpoint gera logs em diferentes níveis:

#### INFO - Registro bem sucedido
```
INFO: Enviando dados para blockchain: IdBlockchain=1
INFO: Blockchain registrado com sucesso: IdBlockchain=1
```

#### DEBUG - Payload completo
```
DEBUG: Payload completo: {
  "IdBlockchain": 1,
  "Data": {...},
  "Fields": [...]
}
```

#### ERROR - Falhas
```
ERROR: Erro ao comunicar com blockchain API: Erro HTTP 500: Internal Server Error
ERROR: Erro de requisição para blockchain API: Erro de conexão: Connection timeout
```

---

## URLs de Acesso

- **Local**: http://localhost:8000/blockchain/register
- **Swagger UI**: http://localhost:8000/docs#/blockchain
- **Render (Produção)**: https://fastapi-sandbox.onrender.com/blockchain/register

---

## Casos de Uso no Licenciamento Ambiental

### 1. Auditoria de Cadastros
Registrar criação/atualização de:
- Pessoas físicas
- Pessoas jurídicas
- Imóveis
- CARs

### 2. Rastreabilidade de Processos
Registrar mudanças de:
- Status de processos
- Etapas do licenciamento
- Aprovações/reprovações

### 3. Prova de Existência
Registrar:
- Submissão de documentos (hash)
- Pareceres técnicos
- Licenças emitidas

### 4. Transparência Pública
Permitir verificação:
- Histórico de processos
- Alterações realizadas
- Responsáveis por ações

---

## Próximos Passos (Roadmap)

### Fase 1 - Atual ✅
- [x] Endpoint básico de registro
- [x] Integração com API Continuus
- [x] Tratamento de erros
- [x] Logs estruturados

### Fase 2 - Planejado
- [ ] Endpoint de consulta de registros
- [ ] Verificação de integridade (hash)
- [ ] Tabela `blockchain_records` no PostgreSQL
- [ ] Registro automático em eventos (triggers)

### Fase 3 - Futuro
- [ ] Dashboard de auditoria
- [ ] Portal público de consulta
- [ ] Webhooks para notificações
- [ ] Integração com smart contracts

---

## Considerações de Segurança

### Dados Sensíveis
⚠️ **ATENÇÃO**: Evite enviar dados pessoais sensíveis em texto claro para o blockchain.

**Boas práticas:**
- Enviar apenas hashes de dados sensíveis
- Manter dados completos no PostgreSQL
- Usar IDs e referências no blockchain
- Conformidade com LGPD

### Exemplo Seguro
```json
{
  "IdBlockchain": 1,
  "Data": {
    "record_id": "2001327",
    "record_type": "pessoa_fisica",
    "data_hash": "0x3f7a9c2b...",
    "timestamp": "2025-10-27T14:30:00"
  },
  "Fields": [
    {
      "NmField": "LicenciamentoAmbiental",
      "DsValue": "Registro de cadastro"
    }
  ]
}
```

---

## Suporte e Documentação

- **API Swagger**: http://localhost:8000/docs
- **Documentação Blockchain**: `docs/copilot/blockchain-licenciamento-ambiental.md`
- **Arquivo de exemplo**: `docs/blockchain/pessoafisica.json`

---

**Documento atualizado em:** 27/10/2025  
**Versão:** 1.0  
**Status:** Implementado e testado
