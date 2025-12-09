# ================================================================
# 01_importacao_limpeza.py
# Lê as bases brutas em CSV, faz limpeza mínima e salva em pickle.
# ================================================================

import os
from pathlib import Path
import pandas as pd

# ----------------------------------------------------------------
# CONFIGURAÇÃO DE PASTAS
# ----------------------------------------------------------------
BASE_DIR = Path(r"C:\Users\alvaro.brandao_kavak\Desktop\projeto_moto")
RAW_DIR = BASE_DIR / "csv"
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

print("\n================ 01_importacao_limpeza.py ================")

# ----------------------------------------------------------------
# 1. FUNÇÃO AUXILIAR PARA LIMPAR IDs NUMÉRICOS COM VÍRGULA
# ----------------------------------------------------------------
def to_int(series):
    """
    Converte colunas de ID do tipo '12,345' para inteiro.
    Retorna Int64 (nullable).
    """
    return (
        series.astype(str)
        .str.replace(",", "", regex=False)
        .pipe(pd.to_numeric, errors="coerce")
        .astype("Int64")
    )

# ----------------------------------------------------------------
# 2. CARREGAR CSVs BRUTOS
# ----------------------------------------------------------------
path_int_metrics   = RAW_DIR / "int_maintenance_os_metrics.csv"
path_os            = RAW_DIR / "OS.csv"
path_piece         = RAW_DIR / "piece.csv"
path_piece_usage   = RAW_DIR / "piece_usage.csv"
path_service       = RAW_DIR / "service.csv"
path_service_usage = RAW_DIR / "service_usage.csv"
path_piece_type    = RAW_DIR / "piece_type.csv"

int_metrics   = pd.read_csv(path_int_metrics)
os_df         = pd.read_csv(path_os)
piece         = pd.read_csv(path_piece)
piece_usage   = pd.read_csv(path_piece_usage)
service       = pd.read_csv(path_service)
service_usage = pd.read_csv(path_service_usage)
piece_type    = pd.read_csv(path_piece_type)

print("int_metrics   :", int_metrics.shape)
print("os_df         :", os_df.shape)
print("piece         :", piece.shape)
print("piece_usage   :", piece_usage.shape)
print("service       :", service.shape)
print("service_usage :", service_usage.shape)
print("piece_type    :", piece_type.shape)

# ----------------------------------------------------------------
# 3. LIMPAR TIPOS BÁSICOS (IDs, DATAS, NÚMEROS)
# ----------------------------------------------------------------

# int_metrics
int_metrics["os_id"] = to_int(int_metrics["os_id"])
int_metrics["service_created_at"] = pd.to_datetime(
    int_metrics["service_created_at"], errors="coerce"
)

int_metrics["queue_time_minutes"] = pd.to_numeric(
    int_metrics["queue_time"], errors="coerce"
)
int_metrics["busy_mechanic_minutes_num"] = pd.to_numeric(
    int_metrics["busy_mechanic_minutes"], errors="coerce"
)

# OS
os_df["os_id"] = to_int(os_df["id"])
os_df["created_at"] = pd.to_datetime(os_df["created_at"], errors="coerce")
os_df["last_updated_at"] = pd.to_datetime(os_df["last_updated_at"], errors="coerce")

# piece
piece["id"] = pd.to_numeric(piece["id"], errors="coerce")
piece["piece_type_id"] = pd.to_numeric(piece["piece_type_id"], errors="coerce")

# piece_usage
piece_usage["os_id"] = to_int(piece_usage["os_id"])
piece_usage["piece_id"] = pd.to_numeric(piece_usage["piece_id"], errors="coerce")
piece_usage["quantity"] = pd.to_numeric(piece_usage["quantity"], errors="coerce").fillna(0)
piece_usage["modified_at"] = pd.to_datetime(piece_usage["modified_at"], errors="coerce")

# service
service["id"] = pd.to_numeric(service["id"], errors="coerce")
service["time_target"] = pd.to_numeric(service["time_target"], errors="coerce").fillna(0)

# service_usage
service_usage["os_id"] = to_int(service_usage["os_id"])
service_usage["service_id"] = pd.to_numeric(service_usage["service_id"], errors="coerce")
service_usage["modified_at"] = pd.to_datetime(service_usage["modified_at"], errors="coerce")

# piece_type
piece_type["id"] = pd.to_numeric(piece_type["id"], errors="coerce")
piece_type["time_target"] = pd.to_numeric(piece_type["time_target"], errors="coerce").fillna(0)

# ----------------------------------------------------------------
# 4. SALVAR PICKLES LIMPOS
# ----------------------------------------------------------------
int_metrics.to_pickle(OUTPUT_DIR / "int_metrics_clean.pkl")
os_df.to_pickle(OUTPUT_DIR / "os_df_clean.pkl")
piece.to_pickle(OUTPUT_DIR / "piece_clean.pkl")
piece_usage.to_pickle(OUTPUT_DIR / "piece_usage_clean.pkl")
service.to_pickle(OUTPUT_DIR / "service_clean.pkl")
service_usage.to_pickle(OUTPUT_DIR / "service_usage_clean.pkl")
piece_type.to_pickle(OUTPUT_DIR / "piece_type_clean.pkl")

print("\nBases limpas salvas em:", OUTPUT_DIR)
print("================ FIM 01_importacao_limpeza.py ================\n")
