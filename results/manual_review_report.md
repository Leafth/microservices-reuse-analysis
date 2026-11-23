# Validação dos candidatos de reuso em Erxes, Novu e Huly Platform

Revisão estática dos resultados gerados para os clones locais de Erxes (`b7afb882a9`), Novu (`ca0e9fe337`) e Huly Platform (`a1dd19d4f7`), em 22/11/2026. As decisões para cada um dos 238 candidatos estão nos arquivos `manual_review.csv` de [Erxes](erxes/manual_review.csv), [Novu](novu/manual_review.csv) e [Platform](platform/manual_review.csv). Os relatórios individuais incluem o fluxo de análise de [Erxes](erxes/manual_review.md), [Novu](novu/manual_review.md) e [Platform](platform/manual_review.md). Os arquivos `candidates.json` e `candidates.csv` originais foram preservados.

## Fluxo de análise por projeto

As contagens das etapas 1, 2 e 4 foram reconstruídas dos manifestos locais; as referências e a exportação foram conferidas com os JSONs já gerados. A busca de código não foi executada novamente. Os dados estruturados da conferência estão em [flow_analysis.json](flow_analysis.json). “Declarações” conta ocorrências nos manifestos de serviço; “referências” conta registros de código nos candidatos exportados, não importações de todos os pacotes do projeto.

| Etapa do README | Erxes | Novu | Huly Platform |
| --- | ---: | ---: | ---: |
| 1. Serviços configurados | 15 | 9 | 39 |
| 1. Declarações em `dependencies` / `devDependencies` | 139 / 1 | 382 / 157 | 814 / 829 |
| 1. Nomes declarados distintos | 82 | 317 | 315 |
| 2. Nomes declarados em pelo menos dois serviços | 24 | 93 | 118 |
| 3. Referências dos candidatos exportados | 2.677 | 10.158 | 1.314 |
| 3. Arquivos com essas referências | 2.029 | 4.104 | 353 |
| 4. Nomes de pacotes internos encontrados | 25 | 67 | 499 |
| 4. Candidatos internos com referência em múltiplos serviços | 1 | 10 | 49 |
| 5. Nomes presentes nas etapas 2 e 4, consolidados | 1 | 7 | 49 |
| 5. Candidatos exportados | 24 | 96 | 118 |

No Novu, os três candidatos internos além dos 93 nomes da etapa 2 vêm de `optionalDependencies`, que o extrator não lê. No Erxes e no Platform, todos os candidatos internos já constavam do agrupamento da etapa 2. A igualdade entre a contagem esperada após consolidação e as linhas exportadas foi conferida nos três projetos.

## Como as decisões foram tomadas

A revisão seguiu a seção **Resultados e validação manual** do [README](../README.md#resultados-e-validação-manual). Comparei as referências de cada candidato com os manifestos dos serviços configurados e, para pacotes internos, com o manifesto localizado na árvore do projeto. Considerei também `optionalDependencies` e `peerDependencies`, além dos dois campos lidos pelo extrator, para conferir a resolução declarada. Uma importação foi atribuída a um serviço confirmado somente quando seu manifesto contém o pacote. Casos representativos e exceções foram abertos no código-fonte.

O status **confirmado** exige importação em pelo menos dois serviços que declaram o pacote. O status **inconclusivo** cobre importação em menos de dois serviços declarantes, ausência de importação detectada ou implementação local indisponível para conferência. A classificação distingue código de serviço, testes e scripts de build; a confirmação de um componente de teste ou build não implica uso em execução.

## Resultado por projeto

| Projeto | Candidatos | Confirmados | Inconclusivos | Principal evidência |
| --- | ---: | ---: | ---: | --- |
| Erxes | 24 | 19 | 5 | `erxes-api-shared` é importado pelos 15 serviços analisados. |
| Novu | 96 | 55 | 41 | Sete pacotes internos e 48 dependências externas têm importações em múltiplos aplicativos. |
| Huly Platform | 118 | 73 | 45 | 49 pacotes internos e 24 dependências externas têm importações em múltiplos serviços; `esbuild` é uso de build. |
| **Total** | **238** | **147** | **91** | |

### Erxes

O pacote interno [`erxes-api-shared`](../projects/erxes/backend/erxes-api-shared/package.json) é importado pelo [`core-api`](../projects/erxes/backend/core-api/src/connectionResolvers.ts#L120), pelo [`gateway`](../projects/erxes/backend/gateway/src/connectionResolver.ts#L1) e pelos plugins, alcançando os 15 serviços configurados. `graphql-tag` também aparece em 12 serviços, por exemplo em [`core-api`](../projects/erxes/backend/core-api/src/apollo/typeDefs.ts#L3) e [`accounting_api`](../projects/erxes/backend/plugins/accounting_api/src/apollo/typeDefs.ts#L3).

Algumas referências excedem as declarações diretas: `zod` aparece em 12 serviços, mas só dois manifestos de serviço o declaram; `mongodb` aparece em seis, com declaração direta em quatro. O CSV conta apenas os serviços com declaração direta como confirmados e registra os demais para investigação da resolução por dependência raiz ou transitiva. `aws-sdk` é importado no `core-api`, mas não consta do manifesto desse serviço; seu reuso permanece inconclusivo.

### Novu

[`@novu/shared`](../projects/novu/packages/shared/package.json) é usado por seis aplicativos, incluindo [`api`](../projects/novu/apps/api/admin/remove-user-account.ts#L3), [`dashboard`](../projects/novu/apps/dashboard/src/main.tsx#L2) e [`inbound-mail`](../projects/novu/apps/inbound-mail/src/config/env.config.ts#L3). `@nestjs/common` é declarado e importado em quatro aplicativos. Pacotes como `vitest`, `@faker-js/faker`, `@nestjs/testing`, `chai`, `sinon`, `@playwright/test` e `@novu/testing` mostram reuso em testes; esse escopo aparece no CSV.

Os três candidatos `@novu/ee-auth`, `@novu/ee-billing` e `@novu/ee-translation` permanecem **inconclusivos**. Os aplicativos os declaram como dependências opcionais e fazem importações condicionais, como `@novu/ee-billing` em [`api`](../projects/novu/apps/api/src/app.module.ts#L83) e [`worker`](../projects/novu/apps/worker/src/app/workflow/workflow.module.ts#L105). Entretanto, o `src` desses pacotes no clone é um arquivo que aponta para `.source`, ausente localmente. Sem a implementação, a resolução e o uso efetivo não puderam ser conferidos.

### Huly Platform

[`@hcengineering/core`](../projects/platform/foundations/core/packages/core/package.json) é importado por 37 serviços, por exemplo em [`pods/account`](../projects/platform/pods/account/src/__start.ts#L7) e [`services/mail/pod-mail`](../projects/platform/services/mail/pod-mail/src/main.ts#L23). `@hcengineering/server-core` aparece em 36. Entre dependências externas, `express` e `cors` aparecem em 22 serviços cada; `mammoth` é importado em [`pod-print`](../projects/platform/services/print/pod-print/src/convert.ts#L4) e [`rekoni`](../projects/platform/services/rekoni/src/extractors/docx.ts#L13).

O nome `@hcengineering/client` ocorre em dois manifestos locais. Os quatro serviços consumidores declaram `workspace:^0.7.19`, compatível com `plugins/client` (`0.7.19`), enquanto `foundations/core/packages/client` declara `0.7.0`; a decisão e essa resolução inferida estão registradas no CSV. `esbuild` tem importações em dois scripts de build, não em dois processos em execução.

## Limites e continuidade da revisão

A confirmação se refere a manifestos e referências no código-fonte. Não foram instaladas dependências nem executados serviços; compatibilidade de versões, resolução real do gerenciador de pacotes e comportamento em produção permanecem fora desta revisão. Referências dinâmicas, comandos de CLI e usos por compilador podem escapar do detector. Os 91 candidatos inconclusivos não devem ser contados como reuso confirmado sem evidência adicional. Os CSVs de revisão são separados das saídas do exportador para que uma nova coleta não apague as decisões.
