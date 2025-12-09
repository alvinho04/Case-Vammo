# ================================================================
# 04_kpi_mecanicos.py
# KPIs por mecânico (Parte 2 do case).
# ================================================================

from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(r"C:\Users\alvaro.brandao_kavak\Desktop\projeto_moto")
OUTPUT_DIR = BASE_DIR / "outputs"

print("\n================ 04_kpi_mecanicos.py ================")

df = pd.read_pickle(OUTPUT_DIR / "df_os_master.pkl")

# ---------------------------------------------------------------
# 1. DEFINIR JANELA DE 90 DIAS
# ---------------------------------------------------------------
if "last_updated_at" not in df.columns:
    raise ValueError("df_os_master precisa da coluna last_updated_at")

data_max = df["last_updated_at"].max()
cutoff = data_max - pd.Timedelta(days=90)

df90 = df[
    (df["last_updated_at"] >= cutoff)
    & (df["busy_mechanic_minutes_num"] > 0)
    & (df["mechanic_email"].notna())
].copy()

print("OS na janela de 90 dias:", len(df90))

# flags auxiliares
df90["tem_estimativa"] = df90["tempo_estimado_os"] > 0
df90["is_return"] = df90["service_type"] == "return"

# ---------------------------------------------------------------
# 2. AGREGAR POR MECÂNICO
# ---------------------------------------------------------------
def sum_if(s, cond):
    return s.where(cond, 0).sum()

agg = (
    df90.groupby(["mechanic_id", "mechanic_email"])
    .apply(
        lambda g: pd.Series(
            {
                "os_count_total": len(g),
                "os_com_estimativa": g["tem_estimativa"].sum(),
                "tempo_estimado_total": g.loc[g["tem_estimativa"], "tempo_estimado_os"].sum(),
                "busy_total_estimado": g.loc[g["tem_estimativa"], "busy_mechanic_minutes_num"].sum(),
                "busy_total_geral": g["busy_mechanic_minutes_num"].sum(),
                "return_count": g["is_return"].sum(),
            }
        )
    )
    .reset_index()
)

# KPI1: eficiência técnica (apenas onde há estimativa)
agg["eficiencia"] = np.where(
    agg["busy_total_estimado"] > 0,
    agg["tempo_estimado_total"] / agg["busy_total_estimado"],
    np.nan,
)

# KPI2: cobertura de estimativa
agg["cobertura_estimativa"] = agg["os_com_estimativa"] / agg["os_count_total"]

# KPI3: complexidade média
agg["complexidade_media"] = np.where(
    agg["os_com_estimativa"] > 0,
    agg["tempo_estimado_total"] / agg["os_com_estimativa"],
    np.nan,
)

# KPI4: taxa de return
agg["taxa_return"] = agg["return_count"] / agg["os_count_total"]

# filtro mínimo de amostra (ex: pelo menos 15 OS)
agg = agg[agg["os_count_total"] >= 15].copy()

# ordenar por eficiência (só para visualização rápida)
top10 = agg.sort_values("eficiencia", ascending=False).head(10)
bottom10 = agg.sort_values("eficiencia", ascending=True).head(10)

print("\nTOP 10 (por eficiência):")
print(top10[[
    "mechanic_id",
    "mechanic_email",
    "os_count_total",
    "eficiencia",
    "cobertura_estimativa",
    "complexidade_media",
    "taxa_return",
]])

print("\nBOTTOM 10 (por eficiência):")
print(bottom10[[
    "mechanic_id",
    "mechanic_email",
    "os_count_total",
    "eficiencia",
    "cobertura_estimativa",
    "complexidade_media",
    "taxa_return",
]])

# salvar tudo
agg.to_csv(OUTPUT_DIR / "kpi_mecanicos_full.csv", index=False, sep=";")
top10.to_csv(OUTPUT_DIR / "kpi_mecanicos_top10.csv", index=False, sep=";")
bottom10.to_csv(OUTPUT_DIR / "kpi_mecanicos_bottom10.csv", index=False, sep=";")

print("\nKPIs por mecânico salvos em:", OUTPUT_DIR)
print("================ FIM 04_kpi_mecanicos.py ================\n")
