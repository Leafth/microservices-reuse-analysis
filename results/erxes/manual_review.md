# Fluxo de análise e validação manual do Erxes

Revisão do clone `b7afb882a9`, conforme as etapas de **Fluxo de análise** e **Resultados e validação manual** do [README](../../README.md). As 24 decisões individuais estão em [manual_review.csv](manual_review.csv); as contagens reproduzíveis estão em [flow_analysis.json](../flow_analysis.json).

| Etapa | Resultado |
| --- | --- |
| 1. Extração | 15 serviços; 139 declarações em `dependencies` e 1 em `devDependencies`; 82 nomes distintos. |
| 2. Dependências comuns | 24 nomes declarados por pelo menos dois serviços. |
| 3. Referências | 2.677 ocorrências para candidatos exportados, em 2.029 arquivos; 23 candidatos com referência e 1 sem referência. |
| 4. Pacotes internos | 25 manifestos com nome, todos com nomes distintos; `erxes-api-shared` é o único candidato interno com referências em pelo menos dois serviços. |
| 5. Exportação | 24 candidatos: 23 `unverified` e 1 `internal_candidate`. O nome interno também estava no agrupamento de dependências comuns e foi consolidado em uma linha. |

Na validação, 19 candidatos foram confirmados por declaração e importação em pelo menos dois serviços; 5 ficaram inconclusivos. [`erxes-api-shared`](../../projects/erxes/backend/erxes-api-shared/package.json) é importado pelos 15 serviços configurados, incluindo [`core-api`](../../projects/erxes/backend/core-api/src/connectionResolvers.ts#L120) e [`gateway`](../../projects/erxes/backend/gateway/src/connectionResolver.ts#L1). `graphql-tag` é usado em 12 serviços, como mostram [`core-api`](../../projects/erxes/backend/core-api/src/apollo/typeDefs.ts#L3) e [`accounting_api`](../../projects/erxes/backend/plugins/accounting_api/src/apollo/typeDefs.ts#L3).

As referências de `zod` abrangem 12 serviços, mas apenas 2 manifestos de serviço declaram diretamente o pacote; para `mongodb`, são 6 serviços com referência e 4 com declaração direta. O CSV registra como confirmados somente os serviços com declaração correspondente. Referências adicionais podem depender do manifesto raiz ou de dependências transitivas, o que esta análise não resolveu. `aws-sdk` aparece no código de `core-api` sem declaração direta naquele serviço e não demonstra reuso entre dois serviços.

O número de referências representa importações detectadas, não execuções nem intensidade de reuso. Os arquivos [candidates.json](candidates.json) e [candidates.csv](candidates.csv) permanecem como saída original da coleta.
