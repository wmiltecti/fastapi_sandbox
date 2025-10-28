# 🎯 Prompts bolt.new - Sistema de Protocolo e Integração API Dados Gerais

## 📋 Contexto
Integrar o sistema de protocolo automático (formato YYYY/NNNNNN) da API FastAPI com o frontend React do bolt.new. O protocolo deve ser exibido permanentemente no cabeçalho do formulário, independente da aba ativa. Todos os campos disponíveis na API devem ser preenchidos no Step1Caracteristicas.

---

## 🚀 PROMPT 1: Criar Hook de Comunicação com API e Header de Protocolo

```
Preciso integrar meu frontend React com uma API FastAPI para gerenciamento de processos de licenciamento ambiental. 

**REQUISITOS:**

1. **Configuração da API:**
   - Base URL: `http://localhost:8000` (usar variável de ambiente VITE_API_BASE_URL)
   - Autenticação: Bearer token no header Authorization
   - Content-Type: application/json

2. **Criar hook customizado `useProcessoAPI`:**
   - Função `createProcesso(user_id)`: POST /api/v1/processos/
   - Função `upsertDadosGerais(processo_id, data)`: PUT /api/v1/processos/{processo_id}/dados-gerais
   - Ambas devem incluir token de autenticação
   - Tratamento de erros com try/catch
   - Retornar dados e loading state

3. **Criar componente `ProcessoHeader`:**
   - Exibir protocolo interno (formato: 2025/000001) em destaque
   - Exibir número de processo externo (se houver)
   - Design: barra fixa no topo do formulário wizard
   - Estilo: fundo azul escuro, texto branco, fonte bold para protocolo
   - Deve aparecer após criação do processo
   - Permanecer visível em todas as abas do wizard

4. **Estrutura de dados esperada:**
   - Resposta POST /processos: `{ id: string, user_id: string, status: string }`
   - Resposta PUT /dados-gerais: `{ id: string, processo_id: string, protocolo_interno: string, numero_processo_externo: string|null, ... }`

Implemente o hook e o componente header mantendo boas práticas React e TypeScript.
```

---

## 🎨 PROMPT 2: Atualizar Step1Caracteristicas com TODOS os Campos da API

```
Preciso atualizar o componente `Step1Caracteristicas.tsx` para integrar com a API de dados gerais e incluir TODOS os campos disponíveis.

**CAMPOS DA API (DadosGeraisUpsert):**

1. **Identificação:**
   - `numero_processo_externo` (opcional) - input text
   - Tipo de pessoa: `tipo_pessoa` (PF/PJ) - radio buttons

2. **Pessoa Física (quando tipo_pessoa = "PF"):**
   - `cpf` - input com máscara XXX.XXX.XXX-XX

3. **Pessoa Jurídica (quando tipo_pessoa = "PJ"):**
   - `cnpj` - input com máscara XX.XXX.XXX/XXXX-XX
   - `razao_social` - input text
   - `nome_fantasia` - input text
   - `porte` - select (MEI, ME, EPP, Pequeno, Médio, Grande)

4. **Dados da Atividade:**
   - `potencial_poluidor` - select (baixo, médio, alto)
   - `descricao_resumo` - textarea (descrição do empreendimento)

5. **Contatos:**
   - `contato_email` - input email
   - `contato_telefone` - input com máscara (XX) XXXXX-XXXX

**REQUISITOS DE IMPLEMENTAÇÃO:**

1. **Lógica de Formulário:**
   - Campos PF/PJ devem ser condicionais (mostrar baseado em tipo_pessoa)
   - Validação: CPF/CNPJ obrigatório conforme tipo
   - Email deve validar formato
   - Todos os campos devem ter labels descritivos

2. **Integração com API:**
   - Usar hook `useProcessoAPI` criado no Prompt 1
   - Ao clicar em "Avançar" ou "Salvar":
     - Se processo não existe: criar processo (POST) e depois dados gerais (PUT)
     - Se processo existe: apenas atualizar dados gerais (PUT)
   - Após sucesso do PUT, extrair `protocolo_interno` da resposta
   - Passar protocolo para o componente `ProcessoHeader`

3. **UX/UI:**
   - Agrupar campos em seções visuais (cards):
     - Seção "Identificação do Processo"
     - Seção "Dados do Requerente" (PF ou PJ)
     - Seção "Dados da Atividade"
     - Seção "Contatos"
   - Loading state durante chamadas API
   - Mensagens de erro/sucesso (toast ou alert)
   - Manter estilo consistente com o wizard existente

4. **Estado do Formulário:**
   - Usar React Hook Form ou Formik para gerenciar estado
   - Validação em tempo real nos campos
   - Persistir dados no localStorage (rascunho)

Refatore completamente o Step1Caracteristicas para incluir todos esses campos mantendo boa organização e usabilidade.
```

---

## 🔗 PROMPT 3: Integrar Header de Protocolo no FormWizard

```
Preciso integrar o componente `ProcessoHeader` criado anteriormente no wizard principal de formulários.

**CONTEXTO:**
- Tenho um wizard multi-step (FormWizard.tsx ou FormWizardLicenciamento.tsx)
- O Step1 agora retorna `protocolo_interno` após salvar dados gerais
- O header deve aparecer após criação do processo e permanecer visível em TODAS as abas

**REQUISITOS:**

1. **Estado Global do Processo:**
   - Criar contexto `ProcessoContext` com:
     - `processoId: string | null`
     - `protocoloInterno: string | null`
     - `numeroProcessoExterno: string | null`
     - `setProcessoData(data)` - função para atualizar
   - Provider deve envolver o FormWizard

2. **Modificar FormWizard:**
   - Adicionar `ProcessoHeader` no topo (acima do stepper)
   - Header só aparece quando `protocoloInterno !== null`
   - Deve ser fixo e sempre visível independente da aba ativa

3. **Conectar Step1Caracteristicas ao Contexto:**
   - Após sucesso do PUT /dados-gerais, chamar `setProcessoData({ processoId, protocoloInterno, numeroProcessoExterno })`
   - Header deve atualizar automaticamente

4. **Estilo do Header:**
   - Sticky position (fixa no scroll)
   - Z-index alto para ficar sobre outros elementos
   - Animação de entrada (fade in) quando aparecer
   - Responsivo (mobile-friendly)

5. **Funcionalidades Extras:**
   - Botão para copiar protocolo interno (clipboard)
   - Tooltip explicando cada tipo de protocolo
   - Indicador visual quando número externo está preenchido

Implemente o contexto, modifique o wizard e conecte tudo mantendo arquitetura limpa.
```

---

## 🧪 PROMPT 4: Adicionar Loading States e Error Handling

```
Preciso melhorar a experiência do usuário adicionando estados de loading e tratamento de erros robusto na integração com a API.

**REQUISITOS:**

1. **Loading States:**
   - Spinner/skeleton durante POST /processos
   - Spinner durante PUT /dados-gerais
   - Desabilitar botões "Avançar" e "Salvar" durante requests
   - Indicador de progresso no header quando salvando

2. **Error Handling:**
   - Erros 401 (não autenticado): redirecionar para login
   - Erros 422 (validação): mostrar erros específicos nos campos
   - Erros 500 (servidor): mensagem genérica + opção de retry
   - Erros de rede: mensagem "Sem conexão" + retry automático

3. **Toast/Notifications:**
   - Sucesso ao salvar: "Dados salvos com sucesso! Protocolo: XXXX/XXXXXX"
   - Erro ao salvar: "Erro ao salvar dados. Tente novamente."
   - Warning ao mudar de aba sem salvar: "Você tem alterações não salvas"

4. **Retry Logic:**
   - Função de retry automático (3 tentativas) para erros temporários
   - Botão manual de retry em caso de falha
   - Exponential backoff entre tentativas

5. **Validação de Dados:**
   - Validar CPF/CNPJ antes de enviar para API
   - Validar formato de email
   - Validar telefone
   - Mostrar mensagens de validação inline nos campos

Implemente essas melhorias no hook `useProcessoAPI`, no `Step1Caracteristicas` e crie componentes auxiliares se necessário.
```

---

## 💾 PROMPT 5: Implementar Sistema de Rascunho Local

```
Preciso que o formulário salve automaticamente os dados no localStorage para não perder informações em caso de fechamento acidental.

**REQUISITOS:**

1. **Auto-save Local:**
   - Salvar dados do Step1 no localStorage a cada 30 segundos
   - Salvar também ao trocar de aba
   - Chave: `processo_rascunho_{user_id}`

2. **Recuperação de Rascunho:**
   - Ao abrir o formulário, verificar se existe rascunho
   - Modal perguntando: "Encontramos um rascunho não salvo. Deseja recuperar?"
   - Opções: "Recuperar" ou "Começar novo"

3. **Sincronização com API:**
   - Rascunho local é prioritário até primeiro salvamento na API
   - Após criar processo na API, marcar rascunho como "sincronizado"
   - Limpar rascunho local após submit final com sucesso

4. **Indicadores Visuais:**
   - Badge "Rascunho local" no header quando dados não estão sincronizados
   - Badge "Sincronizado" quando dados estão salvos na API
   - Timestamp do último salvamento

5. **Gestão de Múltiplos Rascunhos:**
   - Se usuário tiver múltiplos rascunhos, listar todos
   - Permitir excluir rascunhos antigos
   - Limite de 5 rascunhos por usuário

Implemente o sistema de rascunho usando hooks customizados e localStorage API.
```

---

## 🎭 PROMPT 6: Melhorias de UX - Máscaras, Validação e Feedback

```
Preciso adicionar máscaras de input, validações em tempo real e feedback visual melhor no Step1Caracteristicas.

**REQUISITOS:**

1. **Máscaras de Input:**
   - CPF: XXX.XXX.XXX-XX
   - CNPJ: XX.XXX.XXX/XXXX-XX
   - Telefone: (XX) XXXXX-XXXX ou (XX) XXXX-XXXX
   - Usar biblioteca react-input-mask ou similar

2. **Validações em Tempo Real:**
   - Validar dígitos verificadores de CPF/CNPJ
   - Email: formato válido + domínio existente (opcional)
   - Telefone: DDD válido + 8 ou 9 dígitos
   - Mostrar ícone ✓ verde quando campo válido
   - Mostrar ícone ✗ vermelho quando inválido

3. **Autocomplete e Busca:**
   - CNPJ: opção de buscar dados na Receita Federal (se disponível)
   - CEP: buscar endereço automaticamente (integração futura)
   - Email: sugestão de domínios comuns (@gmail, @hotmail, etc)

4. **Campos Condicionais Animados:**
   - Transição suave ao alternar entre PF/PJ
   - Fade in/out nos campos que aparecem/desaparecem
   - Altura do formulário deve animar (não dar "pulo")

5. **Tooltips e Ajuda Contextual:**
   - Tooltip explicando "Potencial Poluidor"
   - Tooltip explicando "Porte da Empresa"
   - Link "?" ao lado de campos complexos abrindo modal de ajuda

6. **Preview de Dados:**
   - Card de resumo no final do Step1 mostrando todos os dados preenchidos
   - Opção de editar campos diretamente do resumo
   - Confirmação visual antes de avançar para próxima aba

Implemente essas melhorias focando em usabilidade e acessibilidade.
```

---

## 📊 PROMPT 7: Dashboard de Visualização de Protocolos

```
Preciso criar uma tela no Dashboard para visualizar todos os processos criados com seus respectivos protocolos.

**REQUISITOS:**

1. **Tabela de Processos:**
   - Colunas: Protocolo Interno, Número Externo, Tipo Pessoa, Nome/Razão Social, Status, Data Criação
   - Filtros: Status, Tipo de Pessoa, Data (range)
   - Busca por protocolo ou nome
   - Paginação (20 itens por página)

2. **Card de Processo:**
   - Ao clicar em uma linha, abrir modal com detalhes completos
   - Mostrar todos os dados gerais
   - Botão "Continuar edição" que abre o wizard na aba correta

3. **Ações em Massa:**
   - Selecionar múltiplos processos
   - Exportar para Excel/CSV
   - Imprimir lista de protocolos

4. **Estatísticas:**
   - Total de processos criados
   - Processos em rascunho vs finalizados
   - Gráfico de processos por mês
   - Protocolos gerados no ano atual

5. **API Integration:**
   - Criar endpoint GET /api/v1/processos?status=&tipo_pessoa=&page=
   - Endpoint para buscar detalhes: GET /api/v1/processos/{id}/completo
   - Cache de resultados no frontend (React Query ou SWR)

Crie a página do dashboard, a tabela e a modal de detalhes usando componentes reutilizáveis.
```

---

## 🔧 PROMPT 8: Configuração de Ambiente e Variáveis

```
Preciso configurar corretamente as variáveis de ambiente para diferentes ambientes (dev, staging, prod).

**CRIAR ARQUIVOS:**

1. **.env.development:**
```
VITE_API_BASE_URL=http://localhost:8000
VITE_ENABLE_MOCKS=false
VITE_AUTO_SAVE_INTERVAL=30000
VITE_MAX_DRAFT_AGE_DAYS=7
```

2. **.env.production:**
```
VITE_API_BASE_URL=https://api.seudominio.com
VITE_ENABLE_MOCKS=false
VITE_AUTO_SAVE_INTERVAL=60000
VITE_MAX_DRAFT_AGE_DAYS=30
```

3. **Criar arquivo `src/config/env.ts`:**
   - Exportar constantes tipadas do ambiente
   - Validação de variáveis obrigatórias
   - Fallbacks para valores padrão

4. **Atualizar .gitignore:**
   - Ignorar .env.local
   - Manter .env.example versionado

5. **Documentar no README.md:**
   - Como configurar variáveis de ambiente
   - Quais variáveis são obrigatórias
   - Exemplos para cada ambiente

Crie os arquivos de configuração e documente o processo de setup.
```

---

## 📝 RESUMO DA IMPLEMENTAÇÃO

### Ordem de Execução Recomendada:
1. **PROMPT 8** - Configurar ambiente primeiro
2. **PROMPT 1** - Criar base de comunicação com API + Header
3. **PROMPT 2** - Refatorar Step1 com todos os campos
4. **PROMPT 3** - Integrar header no wizard (contexto)
5. **PROMPT 4** - Adicionar loading states e error handling
6. **PROMPT 5** - Sistema de rascunho local
7. **PROMPT 6** - Melhorias de UX (máscaras, validações)
8. **PROMPT 7** - Dashboard de visualização (opcional, mas recomendado)

### Campos que Devem Estar no Step1Caracteristicas:
- ✅ numero_processo_externo (opcional)
- ✅ tipo_pessoa (PF/PJ)
- ✅ cpf (se PF)
- ✅ cnpj, razao_social, nome_fantasia, porte (se PJ)
- ✅ potencial_poluidor
- ✅ descricao_resumo
- ✅ contato_email
- ✅ contato_telefone

### Protocolos Exibidos no Header:
- 🔹 **Protocolo Interno:** 2025/000001 (gerado automaticamente)
- 🔹 **Número Externo:** PROC-2025-001 (informado pelo usuário)
- 🔹 **Número Oficial:** (reservado - não editável)

---

## 🎯 CHECKLIST FINAL

Após executar todos os prompts, você terá:
- ✅ Hook de API funcional com autenticação
- ✅ Header de protocolo sempre visível
- ✅ Step1 com TODOS os campos da API
- ✅ Contexto global de processo
- ✅ Loading states e error handling
- ✅ Sistema de rascunho local
- ✅ Máscaras e validações em tempo real
- ✅ Dashboard de visualização (opcional)
- ✅ Configuração de ambiente documentada

**Resultado Esperado:** Formulário completamente integrado com a API, salvando todos os dados disponíveis e exibindo protocolo gerado automaticamente no cabeçalho de forma permanente.
