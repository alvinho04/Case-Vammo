# ================================================================
# 03_baseline_operacional.py
# Calcula baseline geral e por tipo de serviço.
# ================================================================

from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(r"C:\Users\alvaro.brandao_kavak\Desktop\projeto_moto")
OUTPUT_DIR = BASE_DIR / "outputs"

print("\n================ 03_baseline_operacional.py ================")

df = pd.read_pickle(OUTPUT_DIR / "df_os_master.pkl")

# garantir colunas
for col in [
    "tempo_total_os",
    "busy_mechanic_minutes_num",
    "tempo_nao_produtivo",
    "queue_time_minutes",
]:
    if col not in df.columns:
        raise ValueError(f"Coluna obrigatória ausente: {col}")

# Ajuste de negativos
df["tempo_nao_produtivo_ajustado"] = df["tempo_nao_produtivo"].clip(lower=0)
df["queue_time_minutes"] = df["queue_time_minutes"].clip(lower=0)

def resumo_tempo(serie, nome):
    desc = serie.describe(percentiles=[0.5, 0.75, 0.9, 0.95, 0.99])
    print(f"\n==== {nome} ====")
    print(desc)

print("\n================= BASELINE GERAL =================")

resumo_tempo(df["tempo_total_os"], "Tempo total da OS (min)")
resumo_tempo(df["busy_mechanic_minutes_num"], "Tempo produtivo (busy) (min)")
resumo_tempo(df["tempo_nao_produtivo_ajustado"], "Tempo não produtivo (ajustado) (min)")
resumo_tempo(df["queue_time_minutes"], "Tempo de fila (queue_time) (min)")

# ----------------------------------------------------------------
# BASELINE POR TIPO DE SERVIÇO
# ----------------------------------------------------------------
if "service_type" not in df.columns:
    print("\nAtenção: df_os_master não tem service_type. Baseline por tipo não será gerado.")
else:
    grp = (
        df.groupby("service_type")
        .agg(
            os_count=("os_id", "count"),
            busy_med=("busy_mechanic_minutes_num", "median"),
            total_med=("tempo_total_os", "median"),
            nao_prod_med=("tempo_nao_produtivo_ajustado", "median"),
            fila_med=("queue_time_minutes", "median"),
        )
        .reset_index()
        .sort_values("os_count", ascending=False)
    )

    print("\n================= BASELINE POR TIPO DE SERVIÇO =================")
    print(grp)

    grp.to_csv(OUTPUT_DIR / "baseline_por_service_type.csv", index=False)
    df.to_csv(OUTPUT_DIR / "df_os_master.csv", index=False)

    print("\nArquivos salvos em:", OUTPUT_DIR)

print("\n================ FIM 03_baseline_operacional.py ================\n")
