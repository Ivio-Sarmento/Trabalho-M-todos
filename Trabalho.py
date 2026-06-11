# ==========================================================
# TRABALHO DE MÉTODOS COMPUTACIONAIS
#
# Pergunta de pesquisa:
# A criação do Microempreendedor Individual (MEI), em 2009,
# esteve associada à dimminuição nos impostos e ao consequente aumento do número de empresas
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

import requests
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================================
# Função para baixar dados da SIDRA
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
print(df.head())
print(df.shape)
print(df.groupby("setor")["empresas"].describe())

# ==========================================================
#Gráficos
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
plt.show()

#===========================================================
#Base 100
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

#Gráfico base 100
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
plt.show()   




