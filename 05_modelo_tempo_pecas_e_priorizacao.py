# ================================================================
# 05_modelo_tempo_pecas_e_priorizacao.py
# Parte 3: modelo de tempo por peça + priorização.
# ================================================================

from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(r"C:\Users\alvaro.brandao_kavak\Desktop\projeto_moto")
OUTPUT_DIR = BASE_DIR / "outputs"

print("\n================ 05_modelo_tempo_pecas_e_priorizacao.py ================")

# ----------------------------------------------------------------
# 1. CARREGAR BASES
# ----------------------------------------------------------------
df_os      = pd.read_pickle(OUTPUT_DIR / "df_os_master.pkl")
piece      = pd.read_pickle(OUTPUT_DIR / "piece_clean.pkl")
piece_usage = pd.read_pickle(OUTPUT_DIR / "piece_usage_clean.pkl")
piece_type = pd.read_pickle(OUTPUT_DIR / "piece_type_clean.pkl")

print("df_os_master shape       :", df_os.shape)
print("piece_usage_clean shape  :", piece_usage.shape)
print("piece_clean shape        :", piece.shape)
print("piece_type_clean shape   :", piece_type.shape)

# ----------------------------------------------------------------
# 2. FILTRAR OS VÁLIDAS
#    (busy > 0 e tempo_estimado_pecas_os > 0)
# ----------------------------------------------------------------
df_os_valid = df_os[
    (df_os["busy_mechanic_minutes_num"] > 0)
    & (df_os["tempo_estimado_pecas_os"] > 0)
][["os_id", "busy_mechanic_minutes_num", "tempo_estimado_pecas_os"]]

print("\nOS consideradas (busy>0 e tempo_estimado_pecas_os>0):", len(df_os_valid))

# ----------------------------------------------------------------
# 3. MONTAR TABELA OS x PEÇA x TYPE
# ----------------------------------------------------------------
dfp = df_os_valid.merge(
    piece_usage[["os_id", "piece_id", "quantity"]],
    on="os_id",
    how="inner",
)

dfp = dfp.merge(
    piece[["id", "piece_type_id"]],
    left_on="piece_id",
    right_on="id",
    how="left",
)

dfp = dfp.merge(
    piece_type[["id", "piece_type", "time_target"]],
    left_on="piece_type_id",
    right_on="id",
    how="left",
    suffixes=("", "_pt"),
)

dfp = dfp.dropna(subset=["time_target", "quantity"])
dfp["quantity"] = pd.to_numeric(dfp["quantity"], errors="coerce").fillna(0)
dfp = dfp[dfp["quantity"] > 0]

print("Linhas em dfp (OS x peça com estimativa > 0):", dfp.shape)

# ----------------------------------------------------------------
# 4. DISTRIBUIR BUSY POR PEÇA (modelo multiplicativo)
# ----------------------------------------------------------------
dfp["tempo_estimado_linha"] = dfp["time_target"] * dfp["quantity"]

dfp["tempo_estimado_os_calc"] = dfp.groupby("os_id")["tempo_estimado_linha"].transform("sum")

dfp["peso_peca"] = np.where(
    dfp["tempo_estimado_os_calc"] > 0,
    dfp["tempo_estimado_linha"] / dfp["tempo_estimado_os_calc"],
    0.0,
)

dfp["busy_peca"] = dfp["peso_peca"] * dfp["busy_mechanic_minutes_num"]

# sanity: busy total
busy_total_os = df_os_valid["busy_mechanic_minutes_num"].sum()
busy_total_pecas = dfp["busy_peca"].sum()

print("\nBusy total (OS consideradas) :", busy_total_os)
print("Busy total alocado nas peças:", busy_total_pecas)

# ----------------------------------------------------------------
# 5. AGREGAR POR TIPO DE PEÇA
# ----------------------------------------------------------------
agg = (
    dfp.groupby("piece_type_id")
    .agg(
        os_count=("os_id", "nunique"),
        qtd_total=("quantity", "sum"),
        tempo_estimado_total=("tempo_estimado_linha", "sum"),
        busy_total=("busy_peca", "sum"),
        time_target=("time_target", "median"),
        piece_type=("piece_type", "first"),
    )
    .reset_index()
)

# filtrar peças com volume mínimo
agg = agg[(agg["os_count"] >= 20) & (agg["qtd_total"] >= 30)].copy()

# fator_peca = busy_total / tempo_estimado_total
agg["fator_peca"] = np.where(
    agg["tempo_estimado_total"] > 0,
    agg["busy_total"] / agg["tempo_estimado_total"],
    np.nan,
)

# tempo real estimado por unidade
agg["tempo_real_estimado_unit"] = agg["busy_total"] / agg["qtd_total"]

# erro relativo vs time_target
agg["erro_relativo"] = np.where(
    agg["time_target"] > 0,
    (agg["tempo_real_estimado_unit"] - agg["time_target"]) / agg["time_target"],
    np.nan,
)

# impacto aproximado em minutos
agg["impacto_minutos_aprox"] = agg["erro_relativo"].abs() * agg["tempo_estimado_total"].abs()

print("\nPeças com dados suficientes:", len(agg))

# ----------------------------------------------------------------
# 6. RANKINGS
# ----------------------------------------------------------------
# ranking completo
agg.to_csv(OUTPUT_DIR / "modelo_tempo_pecas_ranking.csv", sep=";", index=False)

# ordenado por impacto de erro
agg.sort_values("impacto_minutos_aprox", ascending=False).to_csv(
    OUTPUT_DIR / "modelo_tempo_pecas_ranking_erro.csv", sep=";", index=False
)

# ordenado por tempo estimado total
agg.sort_values("tempo_estimado_total", ascending=False).to_csv(
    OUTPUT_DIR / "modelo_tempo_pecas_ranking_potencial.csv", sep=";", index=False
)

# prints para conferência
print("\nTOP 10 peças por impacto de erro (absoluto):")
print(
    agg.sort_values("impacto_minutos_aprox", ascending=False)
    .head(10)[[
        "piece_type_id",
        "piece_type",
        "os_count",
        "qtd_total",
        "time_target",
        "tempo_real_estimado_unit",
        "fator_peca",
        "erro_relativo",
        "impacto_minutos_aprox",
    ]]
)

print("\nTOP 10 peças por tempo estimado total (potencial operacional):")
print(
    agg.sort_values("tempo_estimado_total", ascending=False)
    .head(10)[[
        "piece_type_id",
        "piece_type",
        "os_count",
        "qtd_total",
        "time_target",
        "tempo_estimado_total",
        "fator_peca",
    ]]
)

print("\nRankings salvos em:", OUTPUT_DIR)
print("================ FIM 05_modelo_tempo_pecas_e_priorizacao.py ================\n")
