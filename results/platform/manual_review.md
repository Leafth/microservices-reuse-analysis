# Fluxo de análise e validação manual do Huly Platform

Revisão do clone `a1dd19d4f7`, conforme as etapas de **Fluxo de análise** e **Resultados e validação manual** do [README](../../README.md). As 118 decisões individuais estão em [manual_review.csv](manual_review.csv); as contagens reproduzíveis estão em [flow_analysis.json](../flow_analysis.json).

| Etapa | Resultado |
| --- | --- |
| 1. Extração | 39 serviços; 814 declarações em `dependencies` e 829 em `devDependencies`; 315 nomes distintos. |
| 2. Dependências comuns | 118 nomes declarados por pelo menos dois serviços. |
| 3. Referências | 1.314 ocorrências para candidatos exportados, em 353 arquivos; 82 candidatos com referência e 36 sem referência. |
| 4. Pacotes internos | 507 manifestos nomeados, correspondentes a 499 nomes distintos; 49 pacotes com referências em pelo menos dois serviços. |
| 5. Exportação | 118 candidatos: 69 `unverified` e 49 `internal_candidate`. Todos os 49 nomes internos também estavam entre as dependências comuns e foram consolidados. |

Na validação, 73 candidatos foram confirmados e 45 ficaram inconclusivos. [`@hcengineering/core`](../../projects/platform/foundations/core/packages/core/package.json) é importado por 37 serviços, como [`pods/account`](../../projects/platform/pods/account/src/__start.ts#L7) e [`services/mail/pod-mail`](../../projects/platform/services/mail/pod-mail/src/main.ts#L23). `mammoth` é compartilhado por [`pod-print`](../../projects/platform/services/print/pod-print/src/convert.ts#L4) e [`rekoni`](../../projects/platform/services/rekoni/src/extractors/docx.ts#L13).

O nome `@hcengineering/client` consta de dois manifestos locais. Os quatro consumidores declaram `workspace:^0.7.19`, compatível com `plugins/client` (`0.7.19`); `foundations/core/packages/client` declara `0.7.0`. Essa identificação é inferida das versões declaradas, sem instalação das dependências. `esbuild` é confirmado somente como ferramenta compartilhada de build, pois as importações estão em [`love-agent/esbuild.config.js`](../../projects/platform/services/ai-bot/love-agent/esbuild.config.js#L1) e [`rekoni/esbuild.js`](../../projects/platform/services/rekoni/esbuild.js#L1).

Os 36 candidatos sem referência incluem ferramentas de desenvolvimento e tipos que podem ser usados por CLI ou compilador, fora da busca do script. A ausência de importação detectada não prova ausência de uso. Os arquivos [candidates.json](candidates.json) e [candidates.csv](candidates.csv) permanecem como saída original da coleta.
