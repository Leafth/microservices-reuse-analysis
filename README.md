# microservices-reuse-analysis

Ferramenta em Python para identificar possíveis componentes compartilhados entre microsserviços Node.js/npm em projetos de código aberto. O repositório faz parte de uma pesquisa sobre reuso de software da Universidade Federal do Ceará (UFC).

**Os resultados são candidatos a componentes compartilhados e precisam de validação manual.**

## Estrutura

| Caminho | Conteúdo |
| --- | --- |
| `projects/exemplo/` | Projeto de exemplo com três serviços e um pacote em `packages/shared-utils/`. |
| `scripts/` | Scripts de extração, análise e exportação. |
| `results/exemplo/` | Arquivos `candidates.json` e `candidates.csv` do exemplo. |

## Requisitos e configuração

Use Python 3, com apenas a biblioteca padrão. A análise lê os arquivos do projeto localmente e dispensa a instalação de Node.js ou das dependências npm.

Execute os comandos a partir da raiz do repositório. A configuração vem preenchida com o projeto `exemplo`. Para analisar outro projeto, coloque seus arquivos em `projects/<projeto>/` e ajuste em `scripts/export_results.py`:

- `PROJECT_NAME` define o subdiretório de saída em `results/`.
- `PROJECT_PATH` aponta para a raiz do projeto, onde a busca por pacotes internos começa.
- `SERVICES` lista os diretórios dos microsserviços, cada um com seu `package.json`.

## Execução

```sh
python scripts/export_results.py
```

O comando cria o diretório de saída quando necessário e sobrescreve `candidates.json` e `candidates.csv` a cada execução. Se estiver preenchendo a validação manual, preserve uma cópia do CSV antes de executar novamente.

Os comandos abaixo executam as etapas isoladamente e imprimem os resultados em JSON no terminal. Para usar outro projeto nessas execuções, ajuste a lista de serviços no próprio script e, no caso de `find_internal_components.py`, também o caminho do projeto.

```sh
python scripts/extract_dependencies.py
python scripts/find_shared_dependencies.py
python scripts/find_references.py
python scripts/find_internal_components.py
```

## Fluxo de análise

1. **Extração de dependências.** Lê `dependencies` e `devDependencies` do `package.json` de cada serviço configurado.
2. **Identificação de dependências comuns.** Agrupa as declarações pelo nome do pacote e seleciona nomes declarados em pelo menos dois serviços, independentemente da versão.
3. **Busca de referências.** Procura, nos serviços configurados, referências por nome de pacote em instruções `import`, chamadas `require()` e `import()` com argumento literal, e reexportações `export … from`. Registra arquivo, linha e trecho encontrado.
4. **Identificação de pacotes internos.** Busca manifestos `package.json` na árvore do projeto e usa o campo `name` para procurar referências. Um pacote entra como candidato interno quando aparece em pelo menos dois serviços.
5. **Exportação.** Consolida os candidatos em JSON e CSV. Se um nome também for identificado como candidato interno, a exportação usa apenas o registro interno.

## Resultados e validação manual

Cada registro inclui projeto, nome do componente, origem, localização quando disponível e status `candidate`. A origem `unverified` indica uma dependência declarada em comum. A origem `internal_candidate` indica um pacote localizado na árvore do projeto com referências em múltiplos serviços.

- `declared_services` lista os serviços que declaram a dependência comum e fica vazio para candidatos internos. `services_with_references` lista os serviços em que a busca encontrou evidências.
- `services_count` conta serviços com declarações para dependências em comum e serviços com referências para candidatos internos.
- No JSON, `references` contém registros com serviço, arquivo, linha, módulo referenciado e trecho de código. No CSV, `evidence` reúne os arquivos, linhas e trechos em uma coluna.

Na revisão, abra os arquivos nas linhas indicadas, confronte as referências com os manifestos e verifique como o pacote é resolvido e utilizado em cada serviço. No exemplo versionado, `express` é declarado por três serviços e tem referências detectadas em dois. O CSV oferece as colunas `validation_status`, `component_type`, `organization`, `reuse_mechanism` e `reviewer_notes`, inicialmente vazias, para registrar a decisão, a classificação e as observações.
