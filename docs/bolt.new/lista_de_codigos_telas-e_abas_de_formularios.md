Lista Completa de Códigos - Telas e Abas de Formulários
1. FORMULÁRIOS PRINCIPAIS (Wizards)
FormWizard.tsx - Formulário Principal com 7 Etapas
Localização: /src/components/FormWizard.tsx
Etapas:
Características do Empreendimento (Step1Caracteristicas)
Uso de Recursos e Energia (Step2RecursosEnergia)
Uso de Água (Step3UsoAgua)
Combustíveis (Step2Combustiveis)
Resíduos (Step4Residuos)
Outras Informações (Step5OutrasInfo)
Revisão Final (StepRevisao)
Funcionalidades:
Navegação entre etapas com progresso visual
Botão "Preencher" com dados mockados
Salvar rascunho
Barra de progresso animada
FormWizardLicenciamento.tsx - Formulário de Licenciamento com 6 Etapas
Localização: /src/components/FormWizardLicenciamento.tsx
Etapas:
Características (StepCaracteristicasEmpreendimento)
Recursos e Energia (RecursosEnergiaStep)
Água (AguaStep)
Combustíveis (CombustiveisStep)
Resíduos (ResiduosStep)
Outras Informações (OutrasInformacoesStep)
Funcionalidades:
Navegação simplificada
Salvar rascunho
Validação por etapa
2. SISTEMA DE INSCRIÇÃO (Layout com Rotas)
InscricaoLayout.tsx - Container Principal de Inscrição
Localização: /src/components/InscricaoLayout.tsx
Estrutura:
Header com navegação
Stepper (InscricaoStepper)
Outlet para páginas de etapas
Botões: Salvar Rascunho, Reiniciar
Rotas:
/inscricao/participantes → ParticipantesPage
/inscricao/imovel → ImovelPage
/inscricao/empreendimento → EmpreendimentoPage
/inscricao/revisao → RevisaoPage
InscricaoStepper.tsx - Navegação Visual de Etapas
Localização: /src/components/InscricaoStepper.tsx
Etapas:
Participantes (Requerente, procurador e responsável técnico)
Imóvel (Localização e características)
Empreendimento (Atividade e detalhes)
Revisão (Conferir dados e finalizar)
Estados: completed, current, upcoming, disabled
3. COMPONENTES DE ETAPAS (Steps) - FormWizard
Step1Caracteristicas.tsx
Localização: /src/components/Step1Caracteristicas.tsx
Campos:
Área do empreendimento
Porte (Pequeno/Médio/Grande)
Potencial poluidor
Código CNAE
Licença anterior
Número de empregados
Horário de funcionamento
Step2RecursosEnergia.tsx
Localização: /src/components/Step2RecursosEnergia.tsx
Campos:
Uso de lenha (quantidade, CEPROF)
Caldeira (altura da chaminé)
Fornos (sistema de captação)
Lista de combustíveis dinâmica
Step3UsoAgua.tsx
Localização: /src/components/Step3UsoAgua.tsx
Campos:
Origens de água (múltipla seleção)
Consumo humano
Consumo outros usos
Volume de despejo
Destino final
Lista de outorgas dinâmica
Step2Combustiveis.tsx
Localização: /src/components/Step2Combustiveis.tsx
Campos:
Lista dinâmica de combustíveis
Tipo de fonte (Energia Elétrica, GLP, Óleo, etc.)
Equipamento
Quantidade
Unidade de medida
Step4Residuos.tsx
Localização: /src/components/Step4Residuos.tsx
Campos:
Resíduos Grupo A (Infectantes)
Resíduos Grupo B (Químicos)
Resíduos Gerais (Sólidos/Líquidos)
Sistema de tratamento
Destinação final
Step5OutrasInfo.tsx
Localização: /src/components/Step5OutrasInfo.tsx
Campos:
Questionário ambiental (10 perguntas sim/não)
Usa recursos naturais?
Gera efluentes líquidos?
Gera emissões atmosféricas?
Localizado em área protegida?
Campo de observações livres
StepRevisao.tsx
Localização: /src/components/StepRevisao.tsx
Funcionalidades:
Resumo de todas as etapas
Navegação para editar etapas específicas
Botão de finalizar
Visualização consolidada dos dados
4. PÁGINAS DE INSCRIÇÃO (Rotas)
ParticipantesPage.tsx
Localização: /src/pages/inscricao/ParticipantesPage.tsx
Seções:
Requerente (busca por CPF/CNPJ)
Procurador (opcional)
Responsável Técnico (opcional)
Funcionalidades:
Busca e autocomplete
Campos dinâmicos por tipo de pessoa
Validação de documentos
ImovelPage.tsx
Localização: /src/pages/inscricao/ImovelPage.tsx
Campos:
Endereço completo
CEP com busca automática
Coordenadas geográficas
Matrícula do imóvel
Área total
Tipo de propriedade
Upload de documentos
EmpreendimentoPage.tsx
Localização: /src/pages/inscricao/EmpreendimentoPage.tsx
Campos:
Nome do empreendimento
Atividade principal (CNAE)
Porte do empreendimento
Potencial poluidor
Descrição detalhada
Documentos técnicos
RevisaoPage.tsx
Localização: /src/pages/inscricao/RevisaoPage.tsx
Funcionalidades:
Resumo completo de todas as páginas
Editar seções específicas
Validação final
Submeter inscrição
Imprimir/exportar dados
5. COMPONENTE ESPECIAL DE LICENCIAMENTO
StepCaracteristicasEmpreendimento.tsx
Localização: /src/components/licenciamento/StepCaracteristicasEmpreendimento.tsx
Campos:
Características técnicas do empreendimento
Dados operacionais
Parâmetros ambientais
6. COMPONENTES DE AUTENTICAÇÃO
Login.tsx
Localização: /src/pages/Login.tsx
Campos:
Tipo de pessoa (PF/PJ/Passaporte/Estrangeiro)
Tipo de identificação (CPF/CNPJ/Passaporte/ID Estrangeira)
Número de identificação
Senha
Sistema: Autenticação via API Backend (FastAPI)
LoginModal.tsx
Localização: /src/components/LoginModal.tsx
Campos:
Email
Senha
Nome completo (cadastro)
Perfil de usuário (cadastro)
Sistema: Autenticação via Bolt Database Auth
Modos: Login / Cadastro
7. ESTRUTURA DE NAVEGAÇÃO

App.tsx (Rotas principais)
├── /login → Login.tsx
├── / → Dashboard.tsx (protegido)
│   └── Pode abrir NewProcessModal
│       └── Navegação para InscricaoLayout
└── /inscricao → InscricaoLayout.tsx
    ├── /participantes → ParticipantesPage.tsx
    ├── /imovel → ImovelPage.tsx
    ├── /empreendimento → EmpreendimentoPage.tsx
    └── /revisao → RevisaoPage.tsx
8. MODAIS E COMPONENTES AUXILIARES
NewProcessModal.tsx - Modal para iniciar novo processo
ProcessDetailsModal.tsx - Detalhes de processo existente
PessoaFisicaDetailsModal.tsx - Detalhes de pessoa física
PessoaJuridicaDetailsModal.tsx - Detalhes de pessoa jurídica
DocumentViewer.tsx - Visualizador de documentos
CollaborationPanel.tsx - Painel de colaboração
ProtectedRoute.tsx - Proteção de rotas autenticadas
9. PÁGINAS ADMINISTRATIVAS
Dashboard.tsx - Painel principal do sistema
PessoasFisicas.tsx - Gerenciamento de pessoas físicas
PessoasJuridicas.tsx - Gerenciamento de pessoas jurídicas
10. COMPONENTES ADMINISTRATIVOS
AdminLayout.tsx - Layout administrativo
AdminDashboard.tsx - Dashboard admin
GenericCRUD.tsx - CRUD genérico
GenericForm.tsx - Formulário genérico
ActivityForm.tsx - Formulário de atividades
BillingConfigurationForm.tsx - Configuração de cobrança
Resumo por Tipo de Uso
Para Formulários de Licenciamento Completos:

Use FormWizard.tsx (7 etapas) ou FormWizardLicenciamento.tsx (6 etapas)
Para Processo de Inscrição com Rotas:

Use InscricaoLayout.tsx + páginas de inscrição (4 etapas com navegação por URL)
Para Autenticação:

Login.tsx (página completa com API Backend)
LoginModal.tsx (modal com Bolt Database Auth)
Para Administração:

Componentes em /components/admin/
Páginas em /pages/