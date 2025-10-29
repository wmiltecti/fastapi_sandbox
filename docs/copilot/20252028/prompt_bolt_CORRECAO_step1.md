# 🎯 PROMPT CORREÇÃO: Integração API na Aba Dados Gerais

## 📌 Contexto
A API FastAPI está funcionando perfeitamente via Swagger. Preciso integrar APENAS a primeira aba do formulário (Dados Gerais/Características) para consumir corretamente as duas APIs do backend.

**NÃO ALTERE:** Outras abas, rotas, componentes ou funcionalidades existentes.

---

## 🔧 PROMPT PARA BOLT.NEW

```
Preciso corrigir a integração da API na primeira aba do formulário de licenciamento. A API está funcionando via Swagger mas não está salvando quando chamo do React.

**LOCALIZAÇÃO:**
- Arquivo: `src/components/Step1Caracteristicas.tsx` (ou similar)
- Ou: Primeiro step do FormWizard/FormWizardLicenciamento

**PROBLEMA:**
Ao clicar em "Salvar" ou "Avançar" na aba de Dados Gerais, os dados NÃO estão sendo enviados para a API.

**SOLUÇÃO NECESSÁRIA:**

1. **Configuração da API (se não existir):**
```typescript
const API_BASE_URL = 'http://localhost:8000';

// Função 1: Criar processo
const createProcesso = async (user_id: string) => {
  const response = await fetch(`${API_BASE_URL}/api/v1/processos/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id, status: 'draft' })
  });
  
  if (!response.ok) throw new Error('Erro ao criar processo');
  return response.json(); // { id: "uuid", user_id: "...", status: "draft" }
};

// Função 2: Salvar dados gerais
const saveDadosGerais = async (processo_id: string, dados: any) => {
  const response = await fetch(`${API_BASE_URL}/api/v1/processos/${processo_id}/dados-gerais`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ processo_id, ...dados })
  });
  
  if (!response.ok) throw new Error('Erro ao salvar dados gerais');
  return response.json(); // { protocolo_interno: "2025/000001", ... }
};
```

2. **Lógica ao clicar "Salvar" ou "Avançar":**
```typescript
const handleSave = async () => {
  try {
    // Passo 1: Criar processo (se não existir)
    let processoId = localStorage.getItem('processo_id'); // ou state
    
    if (!processoId) {
      const processoData = await createProcesso('user_123'); // user_id real aqui
      processoId = processoData.id;
      localStorage.setItem('processo_id', processoId);
    }
    
    // Passo 2: Salvar dados gerais
    const dadosGerais = {
      processo_id: processoId,
      tipo_pessoa: formData.tipoPessoa, // "PF" ou "PJ"
      cpf: formData.cpf || null,
      cnpj: formData.cnpj || null,
      razao_social: formData.razaoSocial || null,
      nome_fantasia: formData.nomeFantasia || null,
      porte: formData.porte || null,
      potencial_poluidor: formData.potencialPoluidor || null,
      descricao_resumo: formData.descricao || null,
      contato_email: formData.email || null,
      contato_telefone: formData.telefone || null,
      numero_processo_externo: formData.numeroExterno || null
    };
    
    const resultado = await saveDadosGerais(processoId, dadosGerais);
    
    console.log('✅ Dados salvos! Protocolo:', resultado.protocolo_interno);
    
    // Exibir protocolo no header (se tiver componente)
    // setProtocolo(resultado.protocolo_interno);
    
    // Avançar para próxima aba
    // goToNextStep();
    
  } catch (error) {
    console.error('❌ Erro ao salvar:', error);
    alert('Erro ao salvar dados. Verifique o console.');
  }
};
```

3. **Vincular ao botão:**
```tsx
<button onClick={handleSave}>
  Salvar e Avançar
</button>
```

**IMPORTANTE:**
- Use os valores do formulário existente (formData, state, etc)
- Substitua 'user_123' pelo ID real do usuário logado
- Adicione console.log para debug (ver no F12 → Console)
- Verifique Network tab (F12 → Network) se requests estão sendo enviadas
- NÃO altere outras abas ou componentes

**TESTE:**
1. Preencha formulário da aba 1
2. Clique em "Salvar"
3. Verifique console: deve aparecer "✅ Dados salvos! Protocolo: 2025/XXXXXX"
4. Verifique Network tab: deve ter 2 requests (POST /processos e PUT /dados-gerais)
5. Confira no Swagger se dados apareceram no banco

Implemente APENAS essa lógica na primeira aba do formulário.
```

---

## 📋 Checklist de Validação

Após implementação, verificar:

- [ ] Console mostra "✅ Dados salvos! Protocolo: 2025/XXXXXX"
- [ ] Network tab mostra 2 requests (POST + PUT)
- [ ] Ambas retornam status 200/201
- [ ] Dados aparecem no banco via Swagger GET
- [ ] Protocolo é retornado na resposta
- [ ] localStorage guarda processo_id

---

## 🚨 Se Ainda Não Funcionar

Adicione debug extremo:

```typescript
const handleSave = async () => {
  console.log('[1] Iniciando salvamento...');
  console.log('[2] Dados do form:', formData);
  
  try {
    let processoId = localStorage.getItem('processo_id');
    console.log('[3] processo_id existente:', processoId);
    
    if (!processoId) {
      console.log('[4] Criando novo processo...');
      const processoData = await createProcesso('user_123');
      console.log('[5] Processo criado:', processoData);
      processoId = processoData.id;
      localStorage.setItem('processo_id', processoId);
    }
    
    console.log('[6] Montando dados gerais...');
    const dadosGerais = { /* ... */ };
    console.log('[7] Payload:', JSON.stringify(dadosGerais, null, 2));
    
    console.log('[8] Enviando PUT /dados-gerais...');
    const resultado = await saveDadosGerais(processoId, dadosGerais);
    console.log('[9] ✅ Sucesso! Resultado:', resultado);
    
  } catch (error) {
    console.error('[ERROR]', error);
  }
};
```

E me mostre todos os logs do console [1] a [9].
