Documentação técnica – Pipeline de análise 
Visão geral do pipeline

Este conjunto de scripts trabalha em cima das bases de manutenção de motos para:

Limpar e padronizar os dados brutos (CSV).

Criar uma tabela mestra de OS com tempos reais e estimados.

Calcular baselines operacionais (tempos médios, mediana, percentis).

Montar KPIs por mecânico.

Ajustar o modelo de tempo por peça para priorização.

Gerar gráficos para facilitar a leitura dos resultados.

Ordem sugerida de execução:

01_importacao_limpeza.py 

02_criar_tabela_mestra_os.py 

03_baseline_operacional.py 

04_kpi_mecanicos.py 

05_modelo_tempo_pecas_e_priorizacao.py 

06_graficos_kpi_mecanicos.py 

07_graficos_pecas.py 

Objetivo

Ler os CSVs brutos, fazer uma limpeza mínima (tipos, datas, IDs) e salvar versões padronizadas em formato pickle, que são mais rápidos de carregar para os próximos scripts. 

01_importacao_limpeza

Entradas (CSV)

int_maintenance_os_metrics.csv

OS.csv

piece.csv

piece_usage.csv

service.csv

service_usage.csv

piece_type.csv

Saídas (PKL)

int_metrics_clean.pkl

os_df_clean.pkl

piece_clean.pkl

piece_usage_clean.pkl

service_clean.pkl

service_usage_clean.pkl

piece_type_clean.pkl

O que o script faz

Define as pastas base (BASE_DIR, RAW_DIR, OUTPUT_DIR).

Lê todos os CSVs de uma vez e mostra o tamanho de cada um.

Converte IDs do formato "12,345" para inteiro, usando uma função auxiliar (to_int).

Converte colunas de data/hora para datetime.

Garante que colunas numéricas (queue_time, busy_mechanic_minutes, quantity, time_target, etc.) estejam como número e não texto.

Salva as versões limpas em OUTPUT_DIR para uso nos próximos passos.

02_criar_tabela_mestra_os.py – Montagem da df_os_master

Objetivo

Construir a tabela mestra de OS (df_os_master), juntando:

Métricas de OS (tempo total, busy, fila).

Quantidade de serviços e peças.

Tempo estimado via peças e serviços.

Informação do mecânico (e-mail e um ID numérico). 

02_criar_tabela_mestra_os

Entradas

Pickles limpos do passo anterior (todos os *_clean.pkl).

Saídas

df_os_master.pkl (na pasta outputs).

O que o script faz

Junta int_metrics com OS pela coluna os_id.

Calcula:

tempo_total_os = last_updated_at - created_at (em minutos).

tempo_nao_produtivo = tempo_total_os - busy_mechanic_minutes_num - queue_time_minutes.

Calcula tempo estimado via peças:

Junta piece_usage → piece → piece_type.

Usa time_target * quantity para cada linha.

Agrega por os_id para obter tempo_estimado_pecas_os.

Calcula tempo estimado via serviços:

Junta service_usage com service.

Usa time_target por serviço.

Agrega por os_id para obter tempo_estimado_servicos_os.

Soma estimativas:

tempo_estimado_os = tempo_estimado_pecas_os + tempo_estimado_servicos_os.

Cria mechanic_email e um mechanic_id numérico (via factorize).

Ajusta valores negativos para zero e seleciona as colunas principais que vão para a master.

03_baseline_operacional.py – Baseline geral e por tipo de serviço

Objetivo

Calcular um baseline de tempos (estatísticas descritivas) no nível geral e por tipo de serviço, usando a base mestra de OS. 

03_baseline_operacional

Entrada

df_os_master.pkl

Saídas

baseline_por_service_type.csv

df_os_master.csv (export da base mestra para Excel/Power BI).

O que o script faz

Valida se colunas importantes existem (tempo_total_os, busy_mechanic_minutes_num, tempo_nao_produtivo, queue_time_minutes).

Ajusta tempos negativos para zero em:

tempo_nao_produtivo_ajustado

queue_time_minutes

Imprime um resumo (describe + percentis) para:

Tempo total da OS.

Tempo produtivo (busy).

Tempo não produtivo (ajustado).

Tempo de fila.

Se tiver service_type, agrupa por tipo e gera uma tabela com:

Quantidade de OS.

Mediana de tempo total, tempo busy, tempo não produtivo, fila.

Salva os resultados em CSV na pasta outputs.

04_kpi_mecanicos.py – KPIs por mecânico

Objetivo

Calcular KPIs por mecânico usando uma janela de 90 dias, considerando apenas OS com busy positivo e mecânico identificado. 

04_kpi_mecanicos

Entrada

df_os_master.pkl

Saídas

kpi_mecanicos_full.csv

kpi_mecanicos_top10.csv

kpi_mecanicos_bottom10.csv

O que o script faz

Define a data máxima (last_updated_at) e calcula o corte de 90 dias.

Filtra:

last_updated_at >= cutoff

busy_mechanic_minutes_num > 0

mechanic_email não nulo.

Cria flags:

tem_estimativa → se tempo_estimado_os > 0.

is_return → se service_type == "return".

Agrega por mecânico:

os_count_total

os_com_estimativa

tempo_estimado_total

busy_total_estimado

busy_total_geral

return_count

Calcula KPIs:

KPI1 – eficiência técnica = tempo_estimado_total / busy_total_estimado.


Aplica filtro mínimo de amostra (ex.: pelo menos 15 OS no período).

Gera top 10 e bottom 10 por eficiência e salva tudo em CSV.

05_modelo_tempo_pecas_e_priorizacao.py – Modelo de tempo por peça

Objetivo

Avaliar, por tipo de peça, como está o tempo real de execução em relação ao tempo de tabela (time_target), para apoiar priorização de ajustes. 

05_modelo_tempo_pecas_e_prioriz…

Entradas

df_os_master.pkl

piece_clean.pkl

piece_usage_clean.pkl

piece_type_clean.pkl

Saídas

modelo_tempo_pecas_ranking.csv

modelo_tempo_pecas_ranking_erro.csv

modelo_tempo_pecas_ranking_potencial.csv

O que o script faz

Filtra OS com:

busy_mechanic_minutes_num > 0

tempo_estimado_pecas_os > 0

Monta uma tabela OS x peça x tipo de peça, juntando:

piece_usage (os_id, piece_id, quantity)

piece (piece_type_id)

piece_type (nome da peça, time_target)

Para cada linha de peça:

Calcula tempo_estimado_linha = time_target * quantity.

Soma por OS (tempo_estimado_os_calc).

Calcula o peso da peça na OS (peso_peca).

Distribui o busy da OS proporcionalmente para cada peça (busy_peca).

Depois, agrega por tipo de peça:

os_count (nº de OS onde aparece)

qtd_total (quantidade total de itens)

tempo_estimado_total

busy_total

time_target (mediana)

fator_peca = busy_total / tempo_estimado_total

tempo_real_estimado_unit = busy_total / qtd_total

erro_relativo vs time_target

impacto_minutos_aprox (erro relativo * tempo estimado total)

Aplica um filtro mínimo de volume (ex.: pelo menos X OS e Y itens).

Gera três rankings:

Completo.

Ordenado por maior impacto de erro.

Ordenado por maior tempo estimado total (onde está o “bolo” de tempo).

06_graficos_kpi_mecanicos.py – Gráficos dos KPIs por mecânico

Objetivo

Gerar gráficos para facilitar a leitura dos KPIs dos mecânicos, com base nos arquivos gerados em 04_kpi_mecanicos.py. 

06_graficos_kpi_mecanicos

Entradas

kpi_mecanicos_full.csv (e/ou kpi_mecanicos_completo.csv)

kpi_top10.csv

kpi_bottom10.csv

O que o script faz (versão ajustada abaixo)

Configura um tema visual (cores, tamanho de figura, grade).

Lê o arquivo de KPIs dos mecânicos.

Gera:

Histograma da eficiência técnica.

Gráfico de barras dos top 10 mecânicos em eficiência.

(Opcional) scatter relacionando eficiência com complexidade média.

07_graficos_pecas.py – Gráficos do modelo de peças

Objetivo

Visualizar, de forma mais intuitiva, os resultados do modelo de tempo por peça. 

07_graficos_pecas

Entrada

modelo_tempo_pecas_ranking.csv

O que o script faz

Configura tema visual (cores, figuras, grade).

Lê o ranking de peças.

Gera:

Histograma do fator_peca (quanto maior, mais o tempo real está acima do tempo de tabela).

Gráfico de barras das 10 peças com maior impacto de erro (impacto_minutos_aprox).
