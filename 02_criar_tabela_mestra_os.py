# ================================================================
# 02_criar_tabela_mestra_os.py
# Cria df_os_master com tempos, estimativas e info de mecânico.
# ================================================================

from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(r"C:\Users\alvaro.brandao_kavak\Desktop\projeto_moto")
OUTPUT_DIR = BASE_DIR / "outputs"

print("\n================ 02_criar_tabela_mestra_os.py ================")

# ----------------------------------------------------------------
# 1. CARREGAR BASES LIMPAS
# ----------------------------------------------------------------
int_metrics   = pd.read_pickle(OUTPUT_DIR / "int_metrics_clean.pkl")
os_df         = pd.read_pickle(OUTPUT_DIR / "os_df_clean.pkl")
piece         = pd.read_pickle(OUTPUT_DIR / "piece_clean.pkl")
piece_usage   = pd.read_pickle(OUTPUT_DIR / "piece_usage_clean.pkl")
service       = pd.read_pickle(OUTPUT_DIR / "service_clean.pkl")
service_usage = pd.read_pickle(OUTPUT_DIR / "service_usage_clean.pkl")
piece_type    = pd.read_pickle(OUTPUT_DIR / "piece_type_clean.pkl")

# ----------------------------------------------------------------
# 2. JUNTAR OS + INT_METRICS (NÍVEL OS)
# ----------------------------------------------------------------
df = int_metrics.merge(
    os_df,
    on="os_id",
    how="left",
    suffixes=("_metrics", "_os"),
)

# service_type preferindo o da métrica, mas caindo para o da OS se faltar
df["service_type"] = df["service_type_metrics"].fillna(df["service_type_os"])

# tempo_total_os = diferença entre último update e criação da OS
df["tempo_total_os"] = (
    df["last_updated_at"] - df["created_at"]
).dt.total_seconds() / 60.0

# garantir que busy e queue_time não sejam NaN
df["busy_mechanic_minutes_num"] = df["busy_mechanic_minutes_num"].fillna(0)
df["queue_time_minutes"] = df["queue_time_minutes"].fillna(0)

# tempo não produtivo bruto
df["tempo_nao_produtivo"] = (
    df["tempo_total_os"]
    - df["busy_mechanic_minutes_num"]
    - df["queue_time_minutes"]
)

# ----------------------------------------------------------------
# 3. CALCULAR TEMPO ESTIMADO DA OS (PEÇAS + SERVIÇOS)
# ----------------------------------------------------------------
# 3.1 Peças: piece_usage -> piece -> piece_type (para pegar time_target)
pu = piece_usage.copy()
pc = piece.copy()
pt = piece_type.copy()

df_pu = pu.merge(
    pc[["id", "piece_type_id", "code", "description"]],
    left_on="piece_id",
    right_on="id",
    how="left",
)

df_pu = df_pu.merge(
    pt[["id", "piece_type", "time_target"]],
    left_on="piece_type_id",
    right_on="id",
    how="left",
    suffixes=("", "_pt"),
)

# tempo estimado de cada linha de peça = time_target * quantity
df_pu["tempo_est_peca_os"] = df_pu["time_target"] * df_pu["quantity"]
df_pu["tempo_est_peca_os"] = df_pu["tempo_est_peca_os"].clip(lower=0)

tempo_pecas_os = (
    df_pu.groupby("os_id")["tempo_est_peca_os"]
    .sum()
    .rename("tempo_estimado_pecas_os")
)

# 3.2 Serviços: service_usage -> service (time_target)
su = service_usage.copy()
svc = service.copy()

df_su = su.merge(
    svc[["id", "name", "time_target"]],
    left_on="service_id",
    right_on="id",
    how="left",
)

df_su["tempo_est_serv_os"] = df_su["time_target"].clip(lower=0)

tempo_serv_os = (
    df_su.groupby("os_id")["tempo_est_serv_os"]
    .sum()
    .rename("tempo_estimado_servicos_os")
)

# 3.3 Juntar estimativas na base OS
df = df.merge(tempo_pecas_os, on="os_id", how="left")
df = df.merge(tempo_serv_os, on="os_id", how="left")

df["tempo_estimado_pecas_os"] = df["tempo_estimado_pecas_os"].fillna(0)
df["tempo_estimado_servicos_os"] = df["tempo_estimado_servicos_os"].fillna(0)
df["tempo_estimado_os"] = (
    df["tempo_estimado_pecas_os"] + df["tempo_estimado_servicos_os"]
)

# ----------------------------------------------------------------
# 4. CRIAR ID DE MECÂNICO A PARTIR DO E-MAIL
# ----------------------------------------------------------------
df["mechanic_email"] = df["last_mechanic"]
codes, uniques = pd.factorize(df["mechanic_email"])
df["mechanic_id"] = np.where(df["mechanic_email"].notna(), codes + 1, np.nan)

# ----------------------------------------------------------------
# 5. AJUSTES FINAIS E SELEÇÃO DE COLUNAS
# ----------------------------------------------------------------
df["tempo_total_os"] = df["tempo_total_os"].clip(lower=0)
df["tempo_nao_produtivo"] = df["tempo_nao_produtivo"].fillna(0)

cols_final = [
    "os_id",
    "license_plate",
    "service_type",
    "created_at",
    "last_updated_at",
    "last_status_os",
    "tempo_total_os",
    "busy_mechanic_minutes_num",
    "queue_time_minutes",
    "tempo_nao_produtivo",
    "tempo_estimado_pecas_os",
    "tempo_estimado_servicos_os",
    "tempo_estimado_os",
    "mechanic_email",
    "mechanic_id",
    "user_id_metrics",
    "has_quality_rejection",
    "has_quality_approval",
    "final_quality_result",
]

# nem todas essas colunas podem existir com exatamente esse nome;
# por isso filtramos apenas as que de fato existem
cols_final = [c for c in cols_final if c in df.columns]

df_os_master = df[cols_final].copy()

print("\nSchema df_os_master:")
print(df_os_master.info())
print("\nAmostra df_os_master:")
print(df_os_master.head())

# ----------------------------------------------------------------
# 6. SALVAR
# ----------------------------------------------------------------
df_os_master.to_pickle(OUTPUT_DIR / "df_os_master.pkl")
print("\n=== df_os_master salvo em:", OUTPUT_DIR / "df_os_master.pkl")
print("================ FIM 02_criar_tabela_mestra_os.py ================\n")
