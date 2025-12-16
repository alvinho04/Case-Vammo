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

  Toda a lógica é organizada em scripts numerados de `01_` a `07_`, que podem ser executados na ordem para reconstruir o pipeline completo.

  int_maintenance_os_metrics.csv – métricas de tempo por OS (timestamps, medições internas).


OS.csv – cadastro das Ordens de Serviço (datas, status, mecânico, retornos, etc.).
piece.csv – cadastro de peças.

piece_usage.csv – uso de peças por OS (quantidade, peça associada à OS).

service.csv – cadastro de serviços.

service_usage.csv – uso de serviços por OS.

piece_type.csv – agrupamento de peça em “tipo de peça”, com alvos de tempo (time_target).

Os nomes dos arquivos estão definidos no script 01_importacao_limpeza.py.

Pipeline e scripts
01_importacao_limpeza.py – Importação e limpeza básica

Lê os CSVs brutos da pasta csv/.

Faz limpeza mínima de tipos:

conversão de IDs com vírgula para inteiro (to_int),

conversão de colunas de data para datetime,

conversão de colunas numéricas com tratamento de erros.

Salva versões limpas em formato pickle na pasta outputs/:

*_clean.pkl para cada base (OS, peças, serviços, etc.).

02_criar_tabela_mestra_os.py – Tabela mestra de OS

Carrega os pickles limpos gerados no passo anterior.

Consolida tudo em um único dataframe df_os_master, contendo, por OS:

tempos de ciclo:

tempo_total_os – diferença entre criação e último update,

busy_mechanic_minutes_num – tempo produtivo do mecânico,

queue_time_minutes – tempo de fila/espera,

tempo_nao_produtivo – resto do tempo (gap entre total e busy+fila),

estimativa de tempo da OS:

soma do tempo-alvo de serviços utilizados,

soma do tempo-alvo de peças utilizadas,

características da OS:

tipo de serviço (service_type),

indicadores de retorno/qualidade,

identificação do mecânico (mechanic_id, mechanic_email).

Saída principal:

outputs/df_os_master.pkl
(e depois, em scripts seguintes, df_os_master.csv para exploração).

03_baseline_operacional.py – Baseline geral e por tipo de serviço

Lê df_os_master.pkl.

Garante a presença das colunas de tempo mais importantes.

Ajusta valores negativos (por exemplo, não permite tempo não produtivo negativo).

Calcula um baseline operacional com agregações como:

número de OS,

tempo total da OS,

tempo produtivo (busy),

tempo de fila,

tempo não produtivo.

Gera saídas:

baseline geral (todos os tipos de serviço),

baseline por service_type.

Saídas:

outputs/baseline_por_service_type.csv

outputs/df_os_master.csv (versão em CSV da tabela mestra).

04_kpi_mecanicos.py – KPIs por mecânico

Usa df_os_master.pkl para montar indicadores de desempenho por mecânico.

Considera uma janela móvel de 90 dias (baseada em last_updated_at).

Filtra:

OS com busy_mechanic_minutes_num > 0,

mecânicos com identificação válida,

amostra mínima (ex.: pelo menos 15 OS).

Calcula KPIs como:

eficiencia – relação entre tempo estimado x tempo busy de fato.

cobertura_estimativa – % de OS que possuem estimativa preenchida.

complexidade_media – tempo estimado médio das OS atendidas.

taxa_return – % de OS marcadas como retorno.

Gera:

outputs/kpi_mecanicos_full.csv – todos os mecânicos com seus KPIs.

outputs/kpi_mecanicos_top10.csv – TOP 10 por eficiência.

outputs/kpi_mecanicos_bottom10.csv – BOTTOM 10 por eficiência.

05_modelo_tempo_pecas_e_priorizacao.py – Modelo de tempo por peça + ranking

Este script é a parte “modelo” do case.

Passos principais:

Carrega:

df_os_master.pkl,

piece_clean.pkl,

piece_usage_clean.pkl,

piece_type_clean.pkl.

Filtra OS válidas:

busy_mechanic_minutes_num > 0,

tempo_estimado_pecas_os > 0.

Monta uma tabela OS x peça x tipo de peça, com:

quantidade utilizada na OS,

time_target da peça (tempo-alvo),

tempo estimado por linha (time_target * quantity).

Distribui o tempo busy da OS entre as peças (modelo multiplicativo):

calcula o peso de cada peça dentro da OS,

aloca o busy_mechanic_minutes_num proporcionalmente,

obtém um “tempo real aproximado” por peça.

Agrega por peça (ou tipo de peça) e calcula métricas, incluindo:

os_count, qtd_total,

tempo_estimado_total,

busy_total,

tempo_real_estimado_unit,

fator_peca (relação busy / tempo estimado),

erro_relativo vs time_target,

impacto_minutos_aprox (erro * volume estimado).

Aplica filtros de volume mínimo (ex.: ≥ 20 OS e ≥ 30 unidades), para garantir robustez.

Saídas de ranking:

outputs/modelo_tempo_pecas_ranking.csv – ranking completo de peças.

outputs/modelo_tempo_pecas_ranking_erro.csv – ordenado por impacto de erro.

outputs/modelo_tempo_pecas_ranking_potencial.csv – ordenado por potencial de tempo estimado.

A ideia é usar esse ranking para priorizar:

quais tipos de peça ajustarem primeiro,

onde focar para reduzir erro de estimativa e ganho de eficiência.

06_graficos_kpi_mecanicos.py – Gráficos de KPIs por mecânico

Lê kpi_mecanicos_full.csv.

Usa matplotlib para gerar gráficos exploratórios, por exemplo:

distribuição de eficiência,

relação entre volume de OS e eficiência,

comparações entre mecânicos.

O script está pensado para uso exploratório (exibir com plt.show()),
mas pode ser adaptado para salvar as figuras em arquivo.

07_graficos_pecas.py – Gráficos de peças e modelo de tempo

Lê modelo_tempo_pecas_ranking.csv.

Gera visualizações como:

histograma do fator_peca,

dispersão de tempo estimado vs tempo real aproximado,

TOP 10 peças por impacto_minutos_aprox.
