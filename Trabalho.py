# ==========================================================
# TRABALHO DE MÉTODOS COMPUTACIONAIS
#
# Pergunta de pesquisa:
# A criação do Microempreendedor Individual (MEI), em 2009,
# esteve associada ao aumento do número de empresas
# formalizadas no Brasil?
#
# Fonte dos dados:
# CEMPRE / IBGE (Tabela 992)
#
# Variável:
# Número de empresas e outras organizações
# ==========================================================


# ==========================================================
# Bibliotecas
# ==========================================================
def formato_brasileiro(valor, casas=0):
    """
    Formata números no padrão brasileiro:
    ponto para milhar e vírgula para decimal.
    """
    return f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")

import os
import requests
import pandas as pd
import matplotlib.pyplot as plt

os.makedirs("Dados", exist_ok=True)
os.makedirs("Gráficos", exist_ok=True)

# ==========================================================
#  Baixar dados do setor pela API SIDRA
# ==========================================================
def baixar_setor(nome_setor, codigo_cnae):

    url = (
        f"https://apisidra.ibge.gov.br/values/"
        f"t/992/"
        f"n1/all/"
        f"v/2585/"
        f"p/all/"
        f"c12762/{codigo_cnae}/"
        f"c319/104029/"
        f"c2703/117933"
    )

    resposta = requests.get(url)
    dados = resposta.json()
    
    df = pd.DataFrame(dados[1:])
    df = df[["D3N", "V"]]
    df.columns = ["ano", "empresas"]
    
    df["ano"] = pd.to_numeric(df["ano"])
    df["empresas"] = pd.to_numeric(
        df["empresas"],
        errors="coerce"
    )
    
    df = df.dropna(subset=["empresas"])
    df["setor"] = nome_setor
    
    return df

veiculos = baixar_setor(
    "Comércio e reparação de veículos",
    117364
)
alimentacao = baixar_setor(
    "Alojamento e alimentação",
    117543
)
reparacao = baixar_setor(
    "Reparação e manutenção",
    117875
)
print(veiculos.head())
print(alimentacao.head())
print(reparacao.head())

df = pd.concat(
    [
        veiculos,
        alimentacao,
        reparacao
    ],
    ignore_index=True
)
df.to_csv(
    "Dados/dados_setores.csv",
    index=False
)



resumo_setores = (
    df.groupby("setor")["empresas"]
    .agg(
        Média="mean",
        Mínimo="min",
        Máximo="max"
    )
    .round(0)
    .reset_index()
    .rename(columns={"setor": "Setor"})
)

resumo_setores.style\
    .hide(axis="index")\
    .format({
        "Média": lambda x: formato_brasileiro(x, 0),
        "Mínimo": lambda x: formato_brasileiro(x, 0),
        "Máximo": lambda x: formato_brasileiro(x, 0)
    })\
    .set_properties(**{
        "text-align": "center"
    })\
    .set_table_styles([
        {
            "selector": "th",
            "props": [
                ("text-align", "center"),
                ("border-bottom", "2px solid black")
            ]
        },
        {
            "selector": "td",
            "props": [
                ("border-bottom", "1px solid #ddd")
            ]
        }
    ])

print("A base final possui 48 observações e 3 variáveis. Cada linha representa um setor em determinado ano, com a respectiva quantidade de empresas registradas no CEMPRE.\n\nA tabela acima apresenta estatísticas descritivas básicas dos setores analisados, incluindo número de observações, média, valor mínimo e valor máximo do número de empresas registradas ao longo da série histórica.")

# ==========================================================
# Tabela-resumo de crescimento por setor
# ==========================================================

df_pivot = df.pivot(
    index="ano",
    columns="setor",
    values="empresas"
)

tabela_crescimento = pd.DataFrame({
    "Setor": df_pivot.columns,
    "Cresc. 2006–2009 (%)": (
        (df_pivot.loc[2009] / df_pivot.loc[2006] - 1) * 100
    ).values,
    "Cresc. 2009–2021 (%)": (
        (df_pivot.loc[2021] / df_pivot.loc[2009] - 1) * 100
    ).values,
    "Cresc. 2006–2021 (%)": (
        (df_pivot.loc[2021] / df_pivot.loc[2006] - 1) * 100
    ).values
})

tabela_crescimento = tabela_crescimento.round(2)

tabela_crescimento.style\
    .hide(axis="index")\
    .format({
    "Cresc. 2006–2009 (%)": lambda x: formato_brasileiro(x, 2),
    "Cresc. 2009–2021 (%)": lambda x: formato_brasileiro(x, 2),
    "Cresc. 2006–2021 (%)": lambda x: formato_brasileiro(x, 2)
    })\
    .set_properties(**{
        "text-align": "center"
    })\
    .set_table_styles([
        {
            "selector": "th",
            "props": [
                ("text-align", "center"),
                ("border-bottom", "2px solid black")
            ]
        },
        {
            "selector": "td",
            "props": [
                ("border-bottom", "1px solid #ddd")
            ]
        }
    ])


# ==========================================================
#Gráfico em Valor Absoluto 
# ==========================================================
plt.figure(figsize=(12,6))
for setor in df["setor"].unique():
    dados_setor = df[df["setor"] == setor]
    plt.plot(
        dados_setor["ano"],
        dados_setor["empresas"],
        marker="o",
        label=setor
    )
plt.axvline(
    x=2009,
    color="red",
    linestyle="--",
    linewidth=2,
    label="Criação do MEI (2009)"
)
plt.title(
    "Número de Empresas Formais por Setor"
)
plt.xlabel("Ano")
plt.ylabel("Número de Empresas")
plt.legend()
plt.grid(True)
plt.savefig(
    "Gráficos/grafico_setores.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()

#===========================================================
#Criação do índice base 100
#===========================================================
df_indice = df.copy()
for setor in df_indice["setor"].unique():

    base = df_indice[
        (df_indice["setor"] == setor) &
        (df_indice["ano"] == 2006)
    ]["empresas"].iloc[0]

    df_indice.loc[
        df_indice["setor"] == setor,
        "indice"
    ] = (
        df_indice.loc[
            df_indice["setor"] == setor,
            "empresas"
        ] / base
    ) * 100


# ==========================================================
#Gráfico em Base 100
# ==========================================================
plt.figure(figsize=(12,6))
for setor in df_indice["setor"].unique():
    dados = df_indice[df_indice["setor"] == setor]
    plt.plot(
        dados["ano"],
        dados["indice"],
        marker="o",
        label=setor
    )
plt.axvline(
    x=2009,
    color="red",
    linestyle="--",
    linewidth=2,
    label="Criação do MEI (2009)"
)
plt.title("Evolução Relativa das Empresas Formais (2006 = 100)")
plt.xlabel("Ano")
plt.ylabel("Índice (2006 = 100)")
plt.legend()
plt.grid(True)
plt.savefig(
    "Gráficos/grafico_base100.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()   




