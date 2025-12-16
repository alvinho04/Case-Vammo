# Case Vammo

Este repositório reúne um **case de dados aplicado à operação de oficina**, com foco em:

- entender o comportamento das Ordens de Serviço (OS),
- medir produtividade dos mecânicos,
- avaliar a qualidade das estimativas de tempo,
- modelar o tempo “real” por tipo de peça,
- priorizar onde atacar primeiro (peças e serviços) para ganhar eficiência.

Os dados são estruturados em arquivos CSV de manutenção (OS, peças, serviços, métricas de tempo) e o fluxo inteiro é implementado em Python usando principalmente **pandas** e **matplotlib**.
---

## 1. Visão geral da solução

O case parte de bases brutas de operação e passa por três grandes etapas:

1. **Ingestão + limpeza mínima** das tabelas operacionais (OS, peças, serviços, métricas de tempo) e padronização de tipos (IDs, datas, números).
2. **Criação de uma tabela mestra de OS** (`df_os_master`), consolidando:
   - tempos de ciclo da OS (total, busy do mecânico, fila, tempo não produtivo),
   - estimativas de tempo por OS (somando serviços e peças),
   - informações de mecânico, tipo de serviço, retornos, etc.
3. **Camada analítica**, dividida em:
   - baseline operacional (geral e por tipo de serviço),
   - KPIs por mecânico,
   - modelo de tempo por peça + ranking de priorização,
   - geração de gráficos exploratórios para consumo visual.

  Toda a lógica é organizada em scripts numerados de `01_` a `07_`, que podem devem ser executados na ordem numérica.

 
