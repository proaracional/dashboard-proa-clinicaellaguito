import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Dashboard PROA", layout="wide")

archivo = "MICRO-LAG.xlsx"

# ========================
# ✅ CABECERA CON LOGO
# ========================

col1, col2 = st.columns([1, 6])

with col1:
    st.image("logo_proa.png")

with col2:
    st.markdown(
        """
        <h1 style='margin-bottom:0; font-size:44px;'>
        Perfil microbiológico 2025
        </h1>
        <h3 style='color:gray; margin-top:5px;'>
        Programa de Optimización de Antimicrobianos (PROA)
        </h3>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")

# ========================
# CARGA
# ========================

df = pd.read_excel(archivo)

df["Microorganismo"] = df["Código de microorganismo local"].astype(str)
df["Servicio"] = df["Servicio"].astype(str).str.lower()
df["Tipo"] = df["Código de muestra local"].astype(str).str.lower()

# ========================
# CLASIFICACIÓN
# ========================

def clasificar_muestra(x):
    x = str(x).lower()

    if "orina" in x:
        return "Urocultivos"
    elif "sang" in x:
        return "Hemocultivos"
    elif any(p in x for p in [
        "aspirado traqueal","bronquial","empiema","empiema pleural",
        "esputo","esputo inducido","faringe","mini-bal","pulmon",
        "respiratorio","traqueal"
    ]):
        return "Respiratorias"
    elif any(p in x for p in [
        "abdomen","absceso abdominal","duodeno","fistula","higado",
        "liquido abdominal","pancreas","pelvis","vesicula"
    ]):
        return "Abdominales"
    else:
        return "Excluir"

df["Grupo_muestra"] = df["Tipo"].apply(clasificar_muestra)
df = df[df["Grupo_muestra"] != "Excluir"]

df["Grupo_servicio"] = df["Servicio"].map({
    "med": "Hospitalización",
    "icu": "UCI"
})

# ========================
# ✅ SIDEBAR CON LOGO (SIN WARNING)
# ========================

st.sidebar.image(
    r"D:\Users\Usuario\Desktop\logo_proa.png",
    use_container_width=True  # ✅ reemplazo correcto
)

st.sidebar.title("🔎 Filtros")

# ========================
# FILTROS
# ========================

servicio = st.sidebar.multiselect(
    "Servicio",
    options=df["Grupo_servicio"].dropna().unique(),
    default=df["Grupo_servicio"].dropna().unique()
)

muestra = st.sidebar.multiselect(
    "Foco infeccioso",
    options=sorted(df["Grupo_muestra"].unique()),
    default=sorted(df["Grupo_muestra"].unique())
)

micro = st.sidebar.multiselect(
    "Microorganismo",
    options=sorted(df["Microorganismo"].dropna().unique())
)

# ========================
# FILTRADO
# ========================

df_f = df.copy()

if servicio:
    df_f = df_f[df_f["Grupo_servicio"].isin(servicio)]

if muestra:
    df_f = df_f[df_f["Grupo_muestra"].isin(muestra)]

if micro:
    df_f = df_f[df_f["Microorganismo"].isin(micro)]

# ========================
# INFO
# ========================

st.markdown(f"**Aislamientos:** {len(df_f)}")

if df_f.empty:
    st.warning("Sin datos")
    st.stop()

# ========================
# ✅ FRECUENCIA ARRIBA
# ========================

top = df_f["Microorganismo"].value_counts().reset_index()
top.columns = ["Microorganismo","Frecuencia"]

st.plotly_chart(
    px.bar(top, x="Microorganismo", y="Frecuencia",
           title="Frecuencia de microorganismos"),
    use_container_width=True
)

# ========================
# ✅ PERFIL MICROBIOLÓGICO
# ========================

if micro:
    df_g = df_f[df_f["Microorganismo"] == micro[0]]
    germen = micro[0].lower()
    st.subheader(f"🔬 Perfil microbiológico: {micro[0]}")
else:
    df_g = df_f
    germen = "global"
    st.subheader("🔬 Perfil microbiológico global")

# ========================
# PANEL CLÍNICO
# ========================

if "pseudomonas" in germen:
    panel = {
        "AMK": "Amikacina",
        "FEP": "Cefepime",
        "TZP": "Piperacilina tazobactam",
        "MEM": "Meropenem",
        "CIP": "Ciprofloxacino"
    }

elif "acinetobacter" in germen:
    panel = {
        "FEP": "Cefepime",
        "TZP": "Piperacilina tazobactam",
        "MEM": "Meropenem",
        "CIP": "Ciprofloxacino",
        "SAM": "Ampicilina sulbactam"
    }

elif "staphyl" in germen:
    panel = {
        "OXA": "Oxacilina",
        "SXT": "Trimetoprim sulfametoxazol",
        "CLI": "Clindamicina",
        "TET": "Tetraciclina"
    }

elif "stenotrophomonas" in germen:
    panel = {
        "SXT": "Trimetoprim sulfametoxazol",
        "LVX": "Levofloxacina"
    }

elif "burkholderia" in germen:
    panel = {
        "SXT": "Trimetoprim sulfametoxazol",
        "LVX": "Levofloxacina",
        "MEM": "Meropenem",
        "CAZ": "Ceftazidime"
    }

elif "candida" in germen:
    panel = {
        "FLU": "Fluconazol",
        "CAS": "Caspofungina",
        "VOR": "Voriconazol",
        "AMB": "Anfotericina B"
    }

else:
    panel = {
        "AMK": "Amikacina",
        "SAM": "Ampicilina sulbactam",
        "CZO": "Cefazolina",
        "CXM": "Cefuroxima",
        "CRO": "Ceftriaxona",
        "FEP": "Cefepime",
        "TZP": "Piperacilina tazobactam",
        "ETP": "Ertapenem",
        "MEM": "Meropenem",
        "CIP": "Ciprofloxacino",
        "SXT": "Trimetoprim sulfametoxazol"
    }

# Fosfomicina solo en urocultivos
if "Urocultivos" in df_f["Grupo_muestra"].unique():
    panel["FOS"] = "Fosfomicina"

# ========================
# CÁLCULO PERFIL
# ========================

perfil = []

for cod, nombre in panel.items():
    if cod in df_g.columns:
        total = df_g[cod].notna().sum()
        r = df_g[cod].isin(["R"]).sum()

        porcentaje = round(r / total * 100, 1) if total > 0 else 0
    else:
        porcentaje = 0

    perfil.append({
        "Antibiótico": nombre,
        "Resistencia (%)": porcentaje
    })

perfil_df = pd.DataFrame(perfil)

# ========================
# COLORES PROA
# ========================

def nivel(x):
    if x <= 20:
        return "Baja"
    elif x <= 30:
        return "Moderada"
    else:
        return "Alta"

perfil_df["Nivel"] = perfil_df["Resistencia (%)"].apply(nivel)

# ========================
# GRÁFICO FINAL
# ========================

st.plotly_chart(
    px.bar(
        perfil_df,
        x="Antibiótico",
        y="Resistencia (%)",
        color="Nivel",
        color_discrete_map={
            "Baja": "green",
            "Moderada": "gold",
            "Alta": "red"
        }
    ),
    use_container_width=True
)