Se formos fazer um conjunto de prompts para o bolt.new implementar o consumo das apis da tela de formularios por abas, quais seriam os prompts? temos todas as apis disponíveis para todas as abas? quer que eu cole o código da tela para apoio a analise? colei os códigos das telas e abas para apoio a análise.

📋 Análise dos Componentes para Prompts bolt.new
Analisando os componentes do formulário, vejo que você tem um wizard de licenciamento ambiental com 6 etapas. Vou mapear quais APIs estão disponíveis e quais precisam ser implementadas:

📊 Mapeamento API x Componentes:
Etapa	Componente	APIs Necessárias	Status
1️⃣ Características	Step1Caracteristicas	✅ /api/v1/processos/ (POST)<br>✅ /api/v1/processos/{id}/dados-gerais (PUT)	Disponível
2️⃣ Recursos/Energia	Step2RecursosEnergia<br>Step2Combustiveis	❌ /api/v1/processos/{id}/combustiveis (POST, GET, PUT, DELETE)<br>❌ /api/v1/processos/{id}/recursos-energia (POST, GET)	Faltando
3️⃣ Água	Step3UsoAgua	❌ /api/v1/processos/{id}/uso-agua (POST, PUT)<br>❌ /api/v1/processos/{id}/outorgas (POST, GET, DELETE)	Faltando
4️⃣ Combustíveis	Step2Combustiveis	❌ Mesmo da etapa 2	Faltando
5️⃣ Resíduos	Step4Residuos	❌ /api/v1/processos/{id}/residuos (POST, GET, PUT, DELETE)	Faltando
6️⃣ Outras Info	Step5OutrasInfo	❌ /api/v1/processos/{id}/outras-info (PUT)<br>❌ /api/v1/processos/{id}/questionario (PUT)	Faltando
📄 Revisão	StepRevisao	✅ /api/v1/processos/{id}/wizard-status (GET)<br>✅ /api/v1/processos/{id}/submit (POST)	Disponível

🎯 Prompts Sugeridos para bolt.new:
Prompt 1: Configuração Base da API
Prompt 2: Integração Step1 (Características)
Prompt 3: Implementação de APIs Faltantes (Backend)
Prompt 4: Integração Step2 (Combustíveis/Energia)
Prompt 5: APIs Água, Resíduos e Outras Informações
Prompt 6: Integração Completa Steps 3-6
Prompt 7: Wizard Status e Finalização

🚀 Ordem de Implementação Recomendada:
Prompt 1 → Base da comunicação API
Prompt 2 → Etapa 1 funcionando (já temos APIs)
Prompt 3 → Implementar APIs faltantes no backend
Prompt 4 → Etapa 2 funcionando
Prompt 5 → APIs restantes (3, 4, 5, 6)
Prompt 6 → Etapas 3-6 funcionando
Prompt 7 → Finalização e revisão
Quer que eu detalhe algum prompt específico ou precisa de ajustes na estratégia? 🎯
