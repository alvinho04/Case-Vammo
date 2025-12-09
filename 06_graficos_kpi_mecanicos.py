# 07_graficos_pecas.py

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

VAMMO_BLUE = "#0050FF"
VAMMO_LIME = "#8CE000"
VAMMO_MAGENTA = "#FF2E79"
VAMMO_DARK = "#121212"

plt.style.use("default")
plt.rcParams["figure.figsize"] = (10, 4)
plt.rcParams["axes.grid"] = True
plt.rcParams["axes.edgecolor"] = VAMMO_DARK
plt.rcParams["axes.labelcolor"] = VAMMO_DARK
plt.rcParams["xtick.color"] = VAMMO_DARK
plt.rcParams["ytick.color"] = VAMMO_DARK
plt.rcParams["text.color"] = VAMMO_DARK

BASE_DIR = Path(r"C:\Users\alvaro.brandao_kavak\Desktop\projeto_moto")
OUTPUT_DIR = BASE_DIR / "outputs"

print("================ 07_graficos_pecas.py ================")

rank_path = OUTPUT_DIR / "modelo_tempo_pecas_ranking.csv"
dfp = pd.read_csv(rank_path, sep=";")

print("Colunas no ranking de peças:")
print(dfp.columns.tolist())
print("\nAmostra:")
print(dfp.head())

name_col = "piece_type_name" if "piece_type_name" in dfp.columns else "piece_type_id"

# 1) Histograma fator_peca
if "fator_peca" in dfp.columns:
    plt.figure(figsize=(10, 4))
    plt.hist(dfp["fator_peca"].dropna(), bins=30, color=VAMMO_BLUE,
             edgecolor="white", alpha=0.9)
    plt.axvline(1.0, color=VAMMO_MAGENTA, linestyle="--", linewidth=2,
                label="fator = 1,0")
    plt.title("Distribuição do fator de tempo por peça\n(tempo real estimado / tempo de tabela)")
    plt.xlabel("fator_peca")
    plt.ylabel("Número de tipos de peça")
    plt.legend()
    plt.tight_layout()
    plt.show()
else:
    print("[AVISO] Sem coluna 'fator_peca' no CSV, pulei histograma.")

# 2) TOP 10 impacto
if "impacto_minutos_aprox" in dfp.columns:
    top_impacto = dfp.sort_values("impacto_minutos_aprox", ascending=False).head(10)
    labels_impacto = top_impacto[name_col].astype(str)

    plt.figure(figsize=(10, 4))
    plt.bar(labels_impacto, top_impacto["impacto_minutos_aprox"], color=VAMMO_MAGENTA)
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Impacto aprox. (minutos de erro acumulado)")
    plt.title("TOP 10 peças por impacto de erro de estimativa")
    for x, v in zip(labels_impacto, top_impacto["impacto_minutos_aprox"]):
        plt.text(x, v, f"{v:,.0f}", ha="center", va="bottom", rotation=90, fontsize=8)
    plt.tight_layout()
    plt.show()
else:
    print("[AVISO] Sem coluna 'impacto_minutos_aprox', pulei TOP impacto.")

# 3) TOP 10 tempo estimado total
top_tempo = dfp.sort_values("tempo_estimado_total", ascending=False).head(10)
labels_tempo = top_tempo[name_col].astype(str)

plt.figure(figsize=(10, 4))
plt.bar(labels_tempo, top_tempo["tempo_estimado_total"], color=VAMMO_BLUE)
plt.xticks(rotation=45, ha="right")
plt.ylabel("Tempo estimado total (minutos)")
plt.title("TOP 10 peças por tempo estimado total\n(onde está concentrado o tempo das OS)")
for x, v in zip(labels_tempo, top_tempo["tempo_estimado_total"]):
    plt.text(x, v, f"{v:,.0f}", ha="center", va="bottom", rotation=90, fontsize=8)
plt.tight_layout()
plt.show()

print("\n================ FIM 07_graficos_pecas.py ================")
