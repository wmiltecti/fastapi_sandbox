# Prompts para bolt.new - Implementar Aba 2 (Uso de Recursos e Energia)

**Data:** 30/10/2025
**Objetivo:** Implementar front-end para consumir a API da Aba 2 - Uso de Recursos e Energia
**API Endpoint:** `POST /api/v1/uso-recursos-energia`

---

## 📋 PREPARAÇÃO (Antes de começar)

### Informações da API:

1. **URL Base:** 
   - Desenvolvimento: `http://localhost:8000`
   - Produção: `https://fastapi-sandbox-ee3p.onrender.com`

2. **Endpoints:**
   - **POST (Criar/Atualizar):** `/api/v1/uso-recursos-energia`
   - **GET (Buscar):** `/api/v1/uso-recursos-energia/{processo_id}`
   - **DELETE (Deletar):** `/api/v1/uso-recursos-energia/{processo_id}`

3. **Swagger/Documentação:** `https://fastapi-sandbox-ee3p.onrender.com/docs`

---

## 📦 PAYLOAD DE EXEMPLO COMPLETO

```json
{
  "processo_id": "PROC-2025-001",
  "usa_lenha": true,
  "quantidade_lenha_m3": 250,
  "num_ceprof": "CEPROF-12345",
  "possui_caldeira": true,
  "altura_chamine_metros": 15,
  "possui_fornos": true,
  "sistema_captacao": "Sistema de filtros ciclônicos com lavadores de gases",
  "combustiveis_energia": [
    {
      "tipo_fonte": "Lenha",
      "equipamento": "Caldeira Principal",
      "quantidade": 250,
      "unidade": "m³"
    },
    {
      "tipo_fonte": "Gás Natural",
      "equipamento": "Forno Industrial I",
      "quantidade": 500,
      "unidade": "m³"
    },
    {
      "tipo_fonte": "Eletricidade",
      "equipamento": "Linha de Produção",
      "quantidade": 2.5,
      "unidade": "MW"
    }
  ]
}
```

---

## 🎯 PROMPT 1: Criar Interfaces TypeScript

```
Preciso criar as interfaces TypeScript para o formulário de Uso de Recursos e Energia (Etapa 2 de 7).

CONTEXTO:
- Tela: "Uso de Recursos e Energia" (Etapa 2)
- Endpoint POST: /api/v1/uso-recursos-energia
- Endpoint GET: /api/v1/uso-recursos-energia/{processo_id}

ESTRUTURA DE DADOS:

O formulário tem 2 partes principais:
1. Dados de Uso de Recursos (tabela principal)
2. Lista de Combustíveis/Energia (tabela relacionada - array)

TAREFA:
Crie as seguintes interfaces TypeScript:

```typescript
// Interface para item individual de combustível/energia
interface CombustivelEnergiaItem {
  tipo_fonte: string;        // Ex: "Lenha", "Gás Natural", "Eletricidade"
  equipamento: string;       // Ex: "Caldeira Principal", "Forno Industrial I"
  quantidade: number;        // Quantidade consumida
  unidade: string;           // Ex: "m³", "MW", "kWh", "litros"
}

// Interface para resposta da API (item com ID)
interface CombustivelEnergiaResponse extends CombustivelEnergiaItem {
  id: string;
  processo_id: string;
  created_at: string;
  updated_at: string;
}

// Interface principal do formulário (REQUEST - envio para API)
interface UsoRecursosEnergiaRequest {
  processo_id: string;
  
  // Uso de Lenha
  usa_lenha: boolean;
  quantidade_lenha_m3?: number;
  num_ceprof?: string;
  
  // Caldeira
  possui_caldeira: boolean;
  altura_chamine_metros?: number;
  
  // Fornos
  possui_fornos: boolean;
  sistema_captacao?: string;
  
  // Lista de combustíveis e energia
  combustiveis_energia: CombustivelEnergiaItem[];
}

// Interface para resposta completa da API (RESPONSE)
interface UsoRecursosEnergiaResponse {
  id: string;
  processo_id: string;
  usa_lenha: boolean;
  quantidade_lenha_m3?: number;
  num_ceprof?: string;
  possui_caldeira: boolean;
  altura_chamine_metros?: number;
  possui_fornos: boolean;
  sistema_captacao?: string;
  created_at: string;
  updated_at: string;
}

// Interface completa (dados principais + lista de combustíveis)
interface UsoRecursosEnergiaCompleto {
  uso_recursos: UsoRecursosEnergiaResponse;
  combustiveis_energia: CombustivelEnergiaResponse[];
}
```

Crie essas interfaces no arquivo apropriado do projeto.
```

---

## 🎯 PROMPT 2: Criar Estrutura do Formulário (HTML)

```
Agora preciso criar a estrutura HTML do formulário da Etapa 2.

CONTEXTO:
- A Etapa 2 é a aba "Uso de Recursos e Energia"
- Deve seguir o mesmo padrão visual das outras abas/etapas
- O formulário tem 4 seções principais

ESTRUTURA DO FORMULÁRIO:

1️⃣ SEÇÃO 1: Uso de Lenha
- Campo: "Utiliza lenha como combustível?" (checkbox/toggle: usa_lenha)
- Se SIM:
  - Campo numérico: "Quantidade mensal (m³)" (quantidade_lenha_m3)
  - Campo texto: "Número CEPROF" (num_ceprof)

2️⃣ SEÇÃO 2: Caldeira
- Campo: "Possui caldeira?" (checkbox/toggle: possui_caldeira)
- Se SIM:
  - Campo numérico: "Altura da chaminé (metros)" (altura_chamine_metros)

3️⃣ SEÇÃO 3: Fornos
- Campo: "Possui fornos?" (checkbox/toggle: possui_fornos)
- Se SIM:
  - Campo texto longo: "Sistema de captação de emissões atmosféricas" (sistema_captacao)

4️⃣ SEÇÃO 4: Combustíveis e Energia (TABELA DINÂMICA)
- Título: "Combustíveis e Fontes de Energia Utilizados"
- Botão: "+ Adicionar Combustível/Energia"
- Tabela com colunas:
  - Tipo de Fonte (input texto)
  - Equipamento (input texto)
  - Quantidade (input numérico)
  - Unidade (input texto: m³, kWh, MW, litros, etc)
  - Ações (botão Remover)

TAREFA:
Crie o HTML do formulário seguindo a estrutura acima. Use os mesmos estilos e componentes das outras etapas (cards, grids, botões, etc).

IMPORTANTE:
- Use campos condicionais (mostrar apenas se checkbox estiver marcado)
- A tabela de combustíveis deve ser dinâmica (adicionar/remover linhas)
- Adicione validação nos campos numéricos (não permitir negativos)
- Adicione placeholders explicativos nos campos
```

---

## 🎯 PROMPT 3: Implementar Lógica de Estado (React)

```
Preciso implementar a lógica de estado e controle do formulário.

CONTEXTO:
- Formulário da Etapa 2: Uso de Recursos e Energia
- Deve gerenciar estado local antes de enviar para API
- Precisa de funções para adicionar/remover itens da tabela dinâmica

TAREFA:

1. Criar estado inicial do formulário:

```typescript
const [formData, setFormData] = useState<UsoRecursosEnergiaRequest>({
  processo_id: processoId, // Vem do contexto/props
  usa_lenha: false,
  quantidade_lenha_m3: undefined,
  num_ceprof: undefined,
  possui_caldeira: false,
  altura_chamine_metros: undefined,
  possui_fornos: false,
  sistema_captacao: undefined,
  combustiveis_energia: []
});
```

2. Criar funções para gerenciar a tabela de combustíveis:

```typescript
// Adicionar nova linha na tabela
const adicionarCombustivel = () => {
  setFormData({
    ...formData,
    combustiveis_energia: [
      ...formData.combustiveis_energia,
      {
        tipo_fonte: '',
        equipamento: '',
        quantidade: 0,
        unidade: ''
      }
    ]
  });
};

// Remover linha da tabela
const removerCombustivel = (index: number) => {
  const novaLista = formData.combustiveis_energia.filter((_, i) => i !== index);
  setFormData({
    ...formData,
    combustiveis_energia: novaLista
  });
};

// Atualizar campo específico de um item da tabela
const atualizarCombustivel = (index: number, campo: keyof CombustivelEnergiaItem, valor: any) => {
  const novaLista = [...formData.combustiveis_energia];
  novaLista[index] = {
    ...novaLista[index],
    [campo]: valor
  };
  setFormData({
    ...formData,
    combustiveis_energia: novaLista
  });
};
```

3. Criar função para atualizar campos principais:

```typescript
const handleChange = (campo: string, valor: any) => {
  setFormData({
    ...formData,
    [campo]: valor
  });
};
```

Implemente essas funções no componente da Etapa 2.
```

---

## 🎯 PROMPT 4: Implementar Chamadas à API

```
Agora preciso implementar as chamadas à API para salvar e carregar os dados.

CONTEXTO:
- API Base URL: http://localhost:8000 (dev) ou https://fastapi-sandbox-ee3p.onrender.com (prod)
- Endpoint POST: /api/v1/uso-recursos-energia
- Endpoint GET: /api/v1/uso-recursos-energia/{processo_id}
- Endpoint DELETE: /api/v1/uso-recursos-energia/{processo_id}

TAREFA:

1. Criar serviço de API:

```typescript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Salvar/Atualizar dados (UPSERT)
const salvarUsoRecursosEnergia = async (data: UsoRecursosEnergiaRequest) => {
  const response = await fetch(`${API_BASE_URL}/api/v1/uso-recursos-energia`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data)
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Erro ao salvar dados');
  }
  
  return await response.json();
};

// Buscar dados existentes
const buscarUsoRecursosEnergia = async (processoId: string) => {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/uso-recursos-energia/${processoId}`
  );
  
  if (response.status === 404) {
    return null; // Ainda não existe registro
  }
  
  if (!response.ok) {
    throw new Error('Erro ao buscar dados');
  }
  
  return await response.json();
};

// Deletar dados
const deletarUsoRecursosEnergia = async (processoId: string) => {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/uso-recursos-energia/${processoId}`,
    { method: 'DELETE' }
  );
  
  if (!response.ok) {
    throw new Error('Erro ao deletar dados');
  }
};
```

2. Implementar useEffect para carregar dados ao montar componente:

```typescript
useEffect(() => {
  const carregarDados = async () => {
    try {
      const dados = await buscarUsoRecursosEnergia(processoId);
      if (dados) {
        setFormData({
          processo_id: processoId,
          usa_lenha: dados.uso_recursos.usa_lenha,
          quantidade_lenha_m3: dados.uso_recursos.quantidade_lenha_m3,
          num_ceprof: dados.uso_recursos.num_ceprof,
          possui_caldeira: dados.uso_recursos.possui_caldeira,
          altura_chamine_metros: dados.uso_recursos.altura_chamine_metros,
          possui_fornos: dados.uso_recursos.possui_fornos,
          sistema_captacao: dados.uso_recursos.sistema_captacao,
          combustiveis_energia: dados.combustiveis_energia.map(c => ({
            tipo_fonte: c.tipo_fonte,
            equipamento: c.equipamento,
            quantidade: c.quantidade,
            unidade: c.unidade
          }))
        });
      }
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
    }
  };
  
  carregarDados();
}, [processoId]);
```

3. Implementar função de submit:

```typescript
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  
  try {
    const resultado = await salvarUsoRecursosEnergia(formData);
    console.log('Dados salvos com sucesso:', resultado);
    alert('Dados salvos com sucesso!');
  } catch (error) {
    console.error('Erro ao salvar:', error);
    alert('Erro ao salvar dados. Tente novamente.');
  }
};
```

Implemente essas funções no componente.
```

---

## 🎯 PROMPT 5: Validação e Mensagens de Erro

```
Preciso adicionar validação no formulário antes de enviar para a API.

REGRAS DE VALIDAÇÃO:

1. Campo obrigatório: processo_id (deve sempre existir)

2. Se usa_lenha = true:
   - quantidade_lenha_m3 deve ser maior que 0
   - num_ceprof deve ser preenchido

3. Se possui_caldeira = true:
   - altura_chamine_metros deve ser maior que 0

4. Se possui_fornos = true:
   - sistema_captacao deve ser preenchido

5. Para cada item em combustiveis_energia:
   - tipo_fonte não pode estar vazio
   - equipamento não pode estar vazio
   - quantidade deve ser maior que 0
   - unidade não pode estar vazia

TAREFA:

Crie função de validação:

```typescript
const validarFormulario = (): string[] => {
  const erros: string[] = [];
  
  if (!formData.processo_id) {
    erros.push('ID do processo é obrigatório');
  }
  
  if (formData.usa_lenha) {
    if (!formData.quantidade_lenha_m3 || formData.quantidade_lenha_m3 <= 0) {
      erros.push('Quantidade de lenha deve ser maior que zero');
    }
    if (!formData.num_ceprof || formData.num_ceprof.trim() === '') {
      erros.push('Número CEPROF é obrigatório quando utiliza lenha');
    }
  }
  
  if (formData.possui_caldeira) {
    if (!formData.altura_chamine_metros || formData.altura_chamine_metros <= 0) {
      erros.push('Altura da chaminé deve ser maior que zero');
    }
  }
  
  if (formData.possui_fornos) {
    if (!formData.sistema_captacao || formData.sistema_captacao.trim() === '') {
      erros.push('Sistema de captação é obrigatório quando possui fornos');
    }
  }
  
  formData.combustiveis_energia.forEach((item, index) => {
    if (!item.tipo_fonte || item.tipo_fonte.trim() === '') {
      erros.push(`Linha ${index + 1}: Tipo de fonte é obrigatório`);
    }
    if (!item.equipamento || item.equipamento.trim() === '') {
      erros.push(`Linha ${index + 1}: Equipamento é obrigatório`);
    }
    if (!item.quantidade || item.quantidade <= 0) {
      erros.push(`Linha ${index + 1}: Quantidade deve ser maior que zero`);
    }
    if (!item.unidade || item.unidade.trim() === '') {
      erros.push(`Linha ${index + 1}: Unidade é obrigatória`);
    }
  });
  
  return erros;
};
```

Atualize o handleSubmit para usar a validação:

```typescript
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  
  const erros = validarFormulario();
  if (erros.length > 0) {
    alert('Erros de validação:\n' + erros.join('\n'));
    return;
  }
  
  try {
    const resultado = await salvarUsoRecursosEnergia(formData);
    console.log('Dados salvos com sucesso:', resultado);
    alert('Dados salvos com sucesso!');
  } catch (error) {
    console.error('Erro ao salvar:', error);
    alert('Erro ao salvar dados. Tente novamente.');
  }
};
```

Implemente a validação no componente.
```

---

## 🎯 PROMPT 6: Ajustes Finais e Testes

```
Preciso fazer ajustes finais no formulário da Etapa 2.

CHECKLIST FINAL:

1. ✅ Verificar se todos os campos estão renderizando corretamente
2. ✅ Testar campos condicionais (aparecem/desaparecem conforme checkboxes)
3. ✅ Testar tabela dinâmica (adicionar/remover linhas)
4. ✅ Testar validação (campos obrigatórios, valores negativos)
5. ✅ Testar chamada à API (POST e GET)
6. ✅ Verificar feedback visual (loading, success, error)
7. ✅ Verificar responsividade mobile

AJUSTES RECOMENDADOS:

1. Adicionar estado de loading:
```typescript
const [isLoading, setIsLoading] = useState(false);

const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  setIsLoading(true);
  try {
    // ... código de salvamento
  } finally {
    setIsLoading(false);
  }
};
```

2. Adicionar botão de limpar formulário:
```typescript
const limparFormulario = () => {
  setFormData({
    processo_id: processoId,
    usa_lenha: false,
    possui_caldeira: false,
    possui_fornos: false,
    combustiveis_energia: []
  });
};
```

3. Desabilitar botão enquanto salva:
```tsx
<button 
  type="submit" 
  disabled={isLoading}
  className="btn-primary"
>
  {isLoading ? 'Salvando...' : 'Salvar'}
</button>
```

TESTE FINAL:
Use este payload de teste para verificar se tudo funciona:

```json
{
  "processo_id": "PROC-2025-001",
  "usa_lenha": true,
  "quantidade_lenha_m3": 250,
  "num_ceprof": "CEPROF-12345",
  "possui_caldeira": true,
  "altura_chamine_metros": 15,
  "possui_fornos": true,
  "sistema_captacao": "Sistema de filtros ciclônicos",
  "combustiveis_energia": [
    {
      "tipo_fonte": "Lenha",
      "equipamento": "Caldeira Principal",
      "quantidade": 250,
      "unidade": "m³"
    },
    {
      "tipo_fonte": "Gás Natural",
      "equipamento": "Forno Industrial I",
      "quantidade": 500,
      "unidade": "m³"
    }
  ]
}
```

Implemente os ajustes e teste o formulário completo.
```

---

## 📊 ESTRUTURA DE RESPOSTA DA API (GET)

Quando você buscar dados existentes, a API retorna no seguinte formato:

```json
{
  "uso_recursos": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "processo_id": "PROC-2025-001",
    "usa_lenha": true,
    "quantidade_lenha_m3": 250,
    "num_ceprof": "CEPROF-12345",
    "possui_caldeira": true,
    "altura_chamine_metros": 15,
    "possui_fornos": true,
    "sistema_captacao": "Sistema de filtros ciclônicos",
    "created_at": "2025-10-30T10:00:00Z",
    "updated_at": "2025-10-30T10:00:00Z"
  },
  "combustiveis_energia": [
    {
      "id": "223e4567-e89b-12d3-a456-426614174000",
      "processo_id": "PROC-2025-001",
      "tipo_fonte": "Lenha",
      "equipamento": "Caldeira Principal",
      "quantidade": 250,
      "unidade": "m³",
      "created_at": "2025-10-30T10:00:00Z",
      "updated_at": "2025-10-30T10:00:00Z"
    },
    {
      "id": "323e4567-e89b-12d3-a456-426614174000",
      "processo_id": "PROC-2025-001",
      "tipo_fonte": "Gás Natural",
      "equipamento": "Forno Industrial I",
      "quantidade": 500,
      "unidade": "m³",
      "created_at": "2025-10-30T10:00:00Z",
      "updated_at": "2025-10-30T10:00:00Z"
    }
  ]
}
```

---

## 🔗 LINKS ÚTEIS

- **Swagger (Desenvolvimento):** http://localhost:8000/docs
- **Swagger (Produção):** https://fastapi-sandbox-ee3p.onrender.com/docs
- **Repositório Backend:** https://github.com/wmiltecti/fastapi_sandbox
- **Documentação da Implementação:** `docs/copilot/implementacao_uso_recursos_energia.md`

---

## ✅ ORDEM DE EXECUÇÃO RECOMENDADA

1. **PROMPT 1** → Criar interfaces TypeScript
2. **PROMPT 2** → Criar estrutura HTML do formulário
3. **PROMPT 3** → Implementar lógica de estado
4. **PROMPT 4** → Implementar chamadas à API
5. **PROMPT 5** → Adicionar validação
6. **PROMPT 6** → Ajustes finais e testes

**Tempo estimado:** 30-45 minutos (dependendo da familiaridade com bolt.new)

---

**Última atualização:** 30/10/2025
**Versão da API:** v1
**Status:** ✅ Pronto para uso
