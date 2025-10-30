# Prompts para bolt.new - Atualizar Formulário Etapa 1 (Dados Gerais)

**Data:** 30/10/2025
**Objetivo:** Atualizar o front-end para consumir os novos campos da API dados-gerais
**API Endpoint:** `PUT /api/v1/processos/{processo_id}/dados-gerais`

---

## 📋 PREPARAÇÃO (Antes de começar)

### Informações necessárias para fornecer ao bolt.new:

1. **URL da API:** `http://localhost:8000` (desenvolvimento) ou URL do Render (produção)
2. **Endpoint:** `PUT /api/v1/processos/{processo_id}/dados-gerais`
3. **Payload de exemplo completo** (copiar do final deste documento)

---

## 🎯 PROMPT 1: Atualizar Interface TypeScript

```
Preciso atualizar a interface TypeScript do formulário de Dados Gerais (Etapa 1).

CONTEXTO:
- Tela: "Características do Empreendimento" (Etapa 1 de 7)
- Endpoint: PUT /api/v1/processos/{processo_id}/dados-gerais
- A API foi atualizada com 11 novos campos

NOVOS CAMPOS A ADICIONAR NA INTERFACE:

1. Características do Empreendimento:
   - area_total: number (área em m²)
   - cnae_codigo: string (ex: "1011-2/01")
   - cnae_descricao: string (ex: "Frigorífico - abate de bovinos")

2. Licença Anterior:
   - possui_licenca_anterior: boolean
   - tipo_licenca_anterior: string (ex: "LO - Licença de Operação")
   - numero_licenca_anterior: string (ex: "12345/2023")
   - ano_emissao_licenca: number (ano: 2023)
   - validade_licenca: string (data: "2025-12-31")

3. Informações Operacionais:
   - numero_empregados: number
   - horario_funcionamento_inicio: string (formato: "07:00")
   - horario_funcionamento_fim: string (formato: "17:00")

TAREFA:
Atualize a interface TypeScript existente `DadosGerais` adicionando esses 11 novos campos como opcionais (todos com `?`). Mantenha todos os campos existentes.

Exemplo da interface atualizada:

```typescript
interface DadosGerais {
  // Campos existentes (manter)
  processo_id: string;
  tipo_pessoa?: 'PF' | 'PJ';
  cpf?: string;
  cnpj?: string;
  razao_social?: string;
  nome_fantasia?: string;
  porte?: string;
  potencial_poluidor?: string;
  descricao_resumo?: string;
  contato_email?: string;
  contato_telefone?: string;
  
  // NOVOS CAMPOS - Características do Empreendimento
  area_total?: number;
  cnae_codigo?: string;
  cnae_descricao?: string;
  
  // NOVOS CAMPOS - Licença Anterior
  possui_licenca_anterior?: boolean;
  tipo_licenca_anterior?: string;
  numero_licenca_anterior?: string;
  ano_emissao_licenca?: number;
  validade_licenca?: string;
  
  // NOVOS CAMPOS - Informações Operacionais
  numero_empregados?: number;
  horario_funcionamento_inicio?: string;
  horario_funcionamento_fim?: string;
}
```

Mostre-me a interface atualizada completa.
```

---

## 🎯 PROMPT 2: Adicionar Campos no Formulário (Parte 1 - Área e CNAE)

```
Agora preciso adicionar os campos visuais no formulário da Etapa 1.

TAREFA 1: Adicionar campo "Área Total"

Localize a seção "Características do Empreendimento" e adicione após o campo "Unidade de Medida":

```tsx
<div className="form-group">
  <label htmlFor="area_total">
    Área Total <span className="required">*</span>
  </label>
  <div className="input-with-unit">
    <input
      type="number"
      id="area_total"
      name="area_total"
      value={formData.area_total || ''}
      onChange={handleInputChange}
      placeholder="5000"
      min="0"
      step="0.01"
      required
    />
    <span className="unit">m²</span>
  </div>
</div>
```

TAREFA 2: Adicionar campo "CNAE" com autocomplete

Adicione após o campo "Potencial Poluidor":

```tsx
<div className="form-group">
  <label htmlFor="cnae_codigo">
    CNAE <span className="required">*</span>
  </label>
  <input
    type="text"
    id="cnae_codigo"
    name="cnae_codigo"
    value={formData.cnae_codigo || ''}
    onChange={handleInputChange}
    placeholder="Frigorífico - abate de bovinos"
    required
  />
  {formData.cnae_codigo && (
    <div className="info-box success">
      <span>Selecionado: {formData.cnae_codigo} - {formData.cnae_descricao}</span>
    </div>
  )}
</div>
```

NOTA: Por enquanto, o CNAE será texto livre. Autocomplete será implementado depois.

Implemente essas mudanças e mostre-me o código atualizado da seção "Características do Empreendimento".
```

---

## 🎯 PROMPT 3: Adicionar Seção de Licença Anterior

```
Agora vou adicionar uma nova seção completa: "Licença Anterior".

Adicione esta seção APÓS a seção "Características do Empreendimento":

```tsx
{/* Seção: Licença Anterior */}
<div className="form-section">
  <h3>Informações sobre Licença Anterior</h3>
  
  {/* Pergunta: Possui Licença Anterior? */}
  <div className="form-group">
    <label>Possui Licença Anterior? <span className="required">*</span></label>
    <div className="radio-group">
      <label className="radio-option">
        <input
          type="radio"
          name="possui_licenca_anterior"
          value="true"
          checked={formData.possui_licenca_anterior === true}
          onChange={(e) => handleInputChange({
            target: { name: 'possui_licenca_anterior', value: true }
          })}
        />
        <span>Sim</span>
      </label>
      <label className="radio-option">
        <input
          type="radio"
          name="possui_licenca_anterior"
          value="false"
          checked={formData.possui_licenca_anterior === false}
          onChange={(e) => handleInputChange({
            target: { name: 'possui_licenca_anterior', value: false }
          })}
        />
        <span>Não</span>
      </label>
    </div>
  </div>
  
  {/* Campos condicionais: mostrar apenas se possui_licenca_anterior = true */}
  {formData.possui_licenca_anterior && (
    <div className="conditional-fields">
      <div className="form-row">
        <div className="form-group">
          <label htmlFor="tipo_licenca_anterior">Tipo de Licença</label>
          <select
            id="tipo_licenca_anterior"
            name="tipo_licenca_anterior"
            value={formData.tipo_licenca_anterior || ''}
            onChange={handleInputChange}
          >
            <option value="">Selecione...</option>
            <option value="LO - Licença de Operação">LO - Licença de Operação</option>
            <option value="LI - Licença de Instalação">LI - Licença de Instalação</option>
            <option value="LP - Licença Prévia">LP - Licença Prévia</option>
            <option value="LAC - Licença Ambiental por Compromisso">LAC - Licença Ambiental por Compromisso</option>
            <option value="LAR - Licença Ambiental de Regularização">LAR - Licença Ambiental de Regularização</option>
          </select>
        </div>
        
        <div className="form-group">
          <label htmlFor="numero_licenca_anterior">Número da Licença</label>
          <input
            type="text"
            id="numero_licenca_anterior"
            name="numero_licenca_anterior"
            value={formData.numero_licenca_anterior || ''}
            onChange={handleInputChange}
            placeholder="12345/2023"
          />
        </div>
      </div>
      
      <div className="form-row">
        <div className="form-group">
          <label htmlFor="ano_emissao_licenca">Ano de Emissão</label>
          <input
            type="number"
            id="ano_emissao_licenca"
            name="ano_emissao_licenca"
            value={formData.ano_emissao_licenca || ''}
            onChange={handleInputChange}
            placeholder="2023"
            min="1900"
            max="2100"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="validade_licenca">Validade</label>
          <input
            type="date"
            id="validade_licenca"
            name="validade_licenca"
            value={formData.validade_licenca || ''}
            onChange={handleInputChange}
          />
        </div>
      </div>
    </div>
  )}
</div>
```

Implemente essa seção e mostre-me o resultado.
```

---

## 🎯 PROMPT 4: Adicionar Campos Operacionais (Empregados e Horário)

```
Agora adicione os campos de "Informações Operacionais".

Adicione APÓS a seção de Licença Anterior:

```tsx
{/* Seção: Informações Operacionais */}
<div className="form-section">
  <h3>Informações Operacionais</h3>
  
  {/* Número de Empregados */}
  <div className="form-group">
    <label htmlFor="numero_empregados">
      Número de Empregados <span className="required">*</span>
    </label>
    <input
      type="number"
      id="numero_empregados"
      name="numero_empregados"
      value={formData.numero_empregados || ''}
      onChange={handleInputChange}
      placeholder="150"
      min="0"
      required
    />
  </div>
  
  {/* Horário de Funcionamento */}
  <div className="form-group">
    <label>Horário de Funcionamento <span className="required">*</span></label>
    <div className="form-row">
      <div className="form-group">
        <label htmlFor="horario_funcionamento_inicio">Início</label>
        <input
          type="time"
          id="horario_funcionamento_inicio"
          name="horario_funcionamento_inicio"
          value={formData.horario_funcionamento_inicio || ''}
          onChange={handleInputChange}
          required
        />
      </div>
      
      <div className="form-group">
        <label htmlFor="horario_funcionamento_fim">Término</label>
        <input
          type="time"
          id="horario_funcionamento_fim"
          name="horario_funcionamento_fim"
          value={formData.horario_funcionamento_fim || ''}
          onChange={handleInputChange}
          required
        />
      </div>
    </div>
  </div>
</div>
```

Implemente e mostre-me o código completo do formulário.
```

---

## 🎯 PROMPT 5: Atualizar Estado Inicial do Formulário

```
Agora preciso atualizar o estado inicial do formulário para incluir os novos campos.

Localize a declaração do `useState` ou `initialState` do formulário e adicione os novos campos:

```typescript
const [formData, setFormData] = useState<DadosGerais>({
  processo_id: '',
  
  // Campos existentes
  tipo_pessoa: undefined,
  cpf: '',
  cnpj: '',
  razao_social: '',
  nome_fantasia: '',
  porte: '',
  potencial_poluidor: '',
  descricao_resumo: '',
  contato_email: '',
  contato_telefone: '',
  
  // NOVOS CAMPOS
  area_total: undefined,
  cnae_codigo: '',
  cnae_descricao: '',
  possui_licenca_anterior: undefined,
  tipo_licenca_anterior: '',
  numero_licenca_anterior: '',
  ano_emissao_licenca: undefined,
  validade_licenca: '',
  numero_empregados: undefined,
  horario_funcionamento_inicio: '',
  horario_funcionamento_fim: '',
});
```

Atualize o estado inicial do formulário.
```

---

## 🎯 PROMPT 6: Atualizar Função de Submissão (PUT API)

```
Agora preciso garantir que a função de submissão envie os novos campos para a API.

IMPORTANTE: A função de submissão já deve estar funcionando. Precisamos apenas verificar que ela envia TODOS os campos do formData.

Verifique se a função que faz o PUT está assim:

```typescript
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/processos/${processoId}/dados-gerais`,
      {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          // Adicionar Authorization se necessário
        },
        body: JSON.stringify(formData), // Envia TODOS os campos
      }
    );
    
    if (!response.ok) {
      throw new Error('Erro ao salvar dados gerais');
    }
    
    const result = await response.json();
    console.log('Dados salvos com sucesso:', result);
    
    // Navegar para próxima etapa ou mostrar sucesso
    onSuccess?.(result);
    
  } catch (error) {
    console.error('Erro:', error);
    // Mostrar mensagem de erro ao usuário
  }
};
```

Se a função já existe e envia `formData` completo, está OK! Apenas confirme que funciona.

Se não existe, crie essa função de submissão.
```

---

## 🎯 PROMPT 7: Adicionar Validações no Front-end

```
Agora vamos adicionar validações importantes no formulário.

VALIDAÇÃO 1: Horário de término deve ser posterior ao início

```typescript
// Adicione esta função de validação
const validateHorario = (inicio: string, fim: string): boolean => {
  if (!inicio || !fim) return true; // Se não preenchido, não valida
  
  const [horaInicio, minInicio] = inicio.split(':').map(Number);
  const [horaFim, minFim] = fim.split(':').map(Number);
  
  const minutosTotalInicio = horaInicio * 60 + minInicio;
  const minutosTotalFim = horaFim * 60 + minFim;
  
  return minutosTotalFim > minutosTotalInicio;
};

// Use no handleInputChange para horários:
const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
  const { name, value, type } = e.target;
  
  const newValue = type === 'number' ? parseFloat(value) : value;
  
  setFormData(prev => {
    const updated = { ...prev, [name]: newValue };
    
    // Validação de horário
    if (name === 'horario_funcionamento_inicio' || name === 'horario_funcionamento_fim') {
      if (!validateHorario(
        updated.horario_funcionamento_inicio || '',
        updated.horario_funcionamento_fim || ''
      )) {
        // Mostrar erro
        setErrors(prev => ({
          ...prev,
          horario: 'Horário de término deve ser posterior ao horário de início'
        }));
      } else {
        // Limpar erro
        setErrors(prev => ({ ...prev, horario: undefined }));
      }
    }
    
    return updated;
  });
};
```

VALIDAÇÃO 2: Se possui_licenca_anterior = true, campos de licença devem ser preenchidos

```typescript
const validateLicenca = (data: DadosGerais): boolean => {
  if (data.possui_licenca_anterior) {
    return !!(
      data.tipo_licenca_anterior &&
      data.numero_licenca_anterior &&
      data.validade_licenca
    );
  }
  return true;
};

// Use no handleSubmit antes de enviar
if (!validateLicenca(formData)) {
  alert('Se possui licença anterior, preencha todos os campos de licença');
  return;
}
```

Implemente essas validações.
```

---

## 🎯 PROMPT 8: Testar Integração com API

```
Agora vamos testar a integração completa.

TESTE 1: Preencher formulário com todos os campos

Use esses dados de exemplo para teste:

```json
{
  "processo_id": "550e8400-e29b-41d4-a716-446655440001",
  "tipo_pessoa": "PJ",
  "cnpj": "12.345.678/0001-90",
  "razao_social": "Frigorífico Exemplo LTDA",
  "nome_fantasia": "Frigorífico Exemplo",
  "porte": "Médio Porte",
  "potencial_poluidor": "Médio",
  "area_total": 5000,
  "cnae_codigo": "1011-2/01",
  "cnae_descricao": "Frigorífico - abate de bovinos",
  "possui_licenca_anterior": true,
  "tipo_licenca_anterior": "LO - Licença de Operação",
  "numero_licenca_anterior": "12345/2023",
  "ano_emissao_licenca": 2023,
  "validade_licenca": "2025-12-31",
  "numero_empregados": 150,
  "horario_funcionamento_inicio": "07:00",
  "horario_funcionamento_fim": "17:00",
  "contato_email": "empresa@exemplo.com",
  "contato_telefone": "(11) 3333-4444"
}
```

TAREFA:
1. Preencha o formulário com esses dados
2. Clique em "Avançar"
3. Verifique no console do navegador se o payload está correto
4. Verifique se a API retorna 200 OK
5. Mostre-me o resultado no console

Se houver erro, mostre-me a mensagem completa.
```

---

## 🎯 PROMPT 9: Ajustar Estilos CSS (Opcional)

```
Se necessário, ajuste os estilos para os novos campos.

Adicione estas classes CSS se ainda não existirem:

```css
/* Seção condicional (licença anterior) */
.conditional-fields {
  margin-top: 1rem;
  padding: 1rem;
  background-color: #f8f9fa;
  border-left: 4px solid #007bff;
  border-radius: 4px;
}

/* Input com unidade (m²) */
.input-with-unit {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.input-with-unit input {
  flex: 1;
}

.input-with-unit .unit {
  font-weight: 600;
  color: #6c757d;
  white-space: nowrap;
}

/* Radio buttons */
.radio-group {
  display: flex;
  gap: 1.5rem;
  margin-top: 0.5rem;
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.radio-option input[type="radio"] {
  width: auto;
  margin: 0;
}

/* Form row (2 colunas) */
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}

/* Info box (CNAE selecionado) */
.info-box {
  margin-top: 0.5rem;
  padding: 0.75rem;
  border-radius: 4px;
  font-size: 0.9rem;
}

.info-box.success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}
```

Adicione esses estilos ao arquivo CSS do formulário.
```

---

## 🎯 PROMPT 10: Revisão Final e Testes

```
Vamos fazer uma revisão final completa.

CHECKLIST:
- [ ] Interface TypeScript atualizada com 11 novos campos
- [ ] Campos visuais adicionados no formulário
- [ ] Seção "Licença Anterior" com campos condicionais
- [ ] Seção "Informações Operacionais"
- [ ] Estado inicial do formulário atualizado
- [ ] Função de submissão enviando todos os campos
- [ ] Validações implementadas (horário e licença)
- [ ] Estilos CSS ajustados
- [ ] Teste com dados de exemplo funcionando
- [ ] Console sem erros
- [ ] API retornando 200 OK

TESTE FINAL:
1. Preencha o formulário completo
2. Teste com possui_licenca_anterior = Não (campos devem sumir)
3. Teste com possui_licenca_anterior = Sim (campos devem aparecer)
4. Teste validação de horário (fim antes de início deve dar erro)
5. Submeta e verifique resposta da API

Mostre-me o resultado final e confirme que tudo está funcionando.
```

---

## 📦 PAYLOAD DE EXEMPLO COMPLETO

```json
{
  "processo_id": "550e8400-e29b-41d4-a716-446655440001",
  "numero_processo_externo": "PROC-2025-002",
  "tipo_pessoa": "PJ",
  "cnpj": "12.345.678/0001-90",
  "razao_social": "Frigorífico Exemplo LTDA",
  "nome_fantasia": "Frigorífico Exemplo",
  "porte": "Médio Porte",
  "potencial_poluidor": "Médio",
  "descricao_resumo": "Frigorífico para abate de bovinos",
  "area_total": 5000.0,
  "cnae_codigo": "1011-2/01",
  "cnae_descricao": "Frigorífico - abate de bovinos",
  "possui_licenca_anterior": true,
  "tipo_licenca_anterior": "LO - Licença de Operação",
  "numero_licenca_anterior": "12345/2023",
  "ano_emissao_licenca": 2023,
  "validade_licenca": "2025-12-31",
  "numero_empregados": 150,
  "horario_funcionamento_inicio": "07:00",
  "horario_funcionamento_fim": "17:00",
  "contato_email": "empresa@exemplo.com",
  "contato_telefone": "(11) 3333-4444"
}
```

---

## 📝 NOTAS IMPORTANTES

### Para o bolt.new entender melhor:

1. **Todos os novos campos são opcionais** (não quebra formulários existentes)
2. **Campos condicionais:** Licença Anterior só aparece se `possui_licenca_anterior = true`
3. **Validações no front-end:** Horário fim > início
4. **Formato de dados:**
   - Datas: "YYYY-MM-DD"
   - Horários: "HH:MM"
   - Números: sem formatação (5000, não "5.000")
5. **API retorna:** Mesmo payload enviado + campos gerados (`protocolo_interno`, `created_at`, etc)

---

## 🚀 ORDEM DE EXECUÇÃO RECOMENDADA

1. **PROMPT 1** → Interface TypeScript
2. **PROMPT 2** → Campos Área e CNAE
3. **PROMPT 3** → Seção Licença Anterior
4. **PROMPT 4** → Campos Operacionais
5. **PROMPT 5** → Estado inicial
6. **PROMPT 6** → Função de submissão
7. **PROMPT 7** → Validações
8. **PROMPT 8** → Testes de integração
9. **PROMPT 9** → Estilos CSS (se necessário)
10. **PROMPT 10** → Revisão final

---

**Fim do documento - Prompts para bolt.new**
