# Fluxo de análise e validação manual do Novu

Revisão do clone `ca0e9fe337`, conforme as etapas de **Fluxo de análise** e **Resultados e validação manual** do [README](../../README.md). As 96 decisões individuais estão em [manual_review.csv](manual_review.csv); as contagens reproduzíveis estão em [flow_analysis.json](../flow_analysis.json).

| Etapa | Resultado |
| --- | --- |
| 1. Extração | 9 aplicativos com manifesto; 382 declarações em `dependencies` e 157 em `devDependencies`; 317 nomes distintos. |
| 2. Dependências comuns | 93 nomes declarados por pelo menos dois aplicativos nos dois campos lidos pelo script. |
| 3. Referências | 10.158 ocorrências para candidatos exportados, em 4.104 arquivos; 68 candidatos com referência e 28 sem referência. Inclui código de testes. |
| 4. Pacotes internos | 68 manifestos nomeados, correspondentes a 67 nomes distintos; 10 pacotes com referências em pelo menos dois aplicativos. A contagem inclui `.deepsec/package.json`. |
| 5. Exportação | 96 candidatos: 86 `unverified` e 10 `internal_candidate`. Sete nomes internos também estavam entre as dependências comuns e foram consolidados; três vêm de dependências opcionais, fora dos campos da etapa 1. |

Na validação, 55 candidatos foram confirmados e 41 ficaram inconclusivos. [`@novu/shared`](../../projects/novu/packages/shared/package.json) é importado por seis aplicativos, entre eles [`api`](../../projects/novu/apps/api/admin/remove-user-account.ts#L3), [`dashboard`](../../projects/novu/apps/dashboard/src/main.tsx#L2) e [`inbound-mail`](../../projects/novu/apps/inbound-mail/src/config/env.config.ts#L3). `@nestjs/common` é declarado e importado por quatro aplicativos.

Pacotes como `vitest`, `@faker-js/faker`, `@nestjs/testing`, `chai`, `sinon`, `@playwright/test` e `@novu/testing` têm evidência compartilhada em testes. Isso confirma reuso no desenvolvimento, sem demonstrar uso em execução. Os três candidatos enterprise `@novu/ee-auth`, `@novu/ee-billing` e `@novu/ee-translation` foram mantidos inconclusivos: os aplicativos os declaram em `optionalDependencies` e importam condicionalmente, mas o `src` dos pacotes é um arquivo que aponta para `.source`, ausente no clone. A implementação não pôde ser conferida.

O extrator da etapa 1 não lê `optionalDependencies`. A revisão manual considerou esse campo para explicar as três linhas internas adicionais, sem alterar os resultados originais de [candidates.json](candidates.json) e [candidates.csv](candidates.csv).
