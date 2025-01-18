import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Normes Administratives Collèges Privés Alibori",
    page_icon="📊",
    layout="wide"
)

# Chargement des données
@st.cache_data
def load_data():
    return pd.read_excel("Données contrôle.xlsx")

df = load_data()


st.title(":blue[Contrôle du respect des normes administratives dans les collèges privés de l'Alibori]")

st.write(":blue[Application web développée par : GOUNOU N'GOBI Chabi Zimé, Planificateur de l'éducation, Data Analyst/Data Manager]")
st.write("")


st.header(":blue[Couverture des établissements privés par le contrôle]")

col1, col2, col3 = st.columns(3)

# Métriques clés

with col1:
    st.metric("Nombre total d'établissements privés fonctionnels", len(df)+1)
with col2:
    st.metric("Nombre total d'établissements couverts", len(df))
with col3:
    taux = float(len(df))/(float(len(df))+1) * 100
    st.metric("Taux de couverture", f"{taux:.2f}%")

st.write("")
# Navigation avec descriptions et boutons
st.markdown("### Navigation sur cette page web")

# Section Analyse Globale
st.markdown("""
**📊 Analyse Globale**
- Analyse globale des infrastructures et équipements
- État de la salubrité et de l'hygiène
- Situation du personnel administratif et enseignant
- Respect de quelques dispositions pédagogiques
""")
st.markdown("👇 Cliquez ci-dessous pour accéder à l'analyse globale")
st.page_link("pages/1_📊_Analyse_Globale.py", label="Accéder à l'Analyse Globale")
st.write("")

# Section Classement
st.markdown("""
**🏆 Classement**
- Classement général des établissements par scrores obtenus
- 13 meilleurs établissements
- 13 établissements restants
""")
st.markdown("👇 Cliquez ci-dessous pour accéder au classement des établissements")
st.page_link("pages/2_🏆_Classement.py", label="Accéder au Classement")
st.write("")

# Section Points d'Amélioration
st.markdown("""
**📝 Points d'Amélioration**
- Analyse personnalisée par établissement
- Visualisation des forces et faiblesses
- Recommandations spécifiques d'amélioration
""")
st.markdown("👇 Cliquez ci-dessous pour accéder aux points d'amélioration")
st.page_link("pages/3_📝_Points_d'Amelioration.py", label="Accéder aux Points d'Amélioration")
st.write("")

# À propos
st.markdown("""
### Méthodologie d'évaluation

L'évaluation des établissements est basée sur cinq critères principaux :

1. **Infrastructures de base (20%)**
   - Point d'eau, électricité, latrines

2. **Infrastructures et mobiliers scolaires (20%)**
   - Salles de classe, mobiliers, aire de récréation, aire d'EPS

3. **Salubrité et hygiène (20%)**
   - Propreté, dispositifs sanitaires, trousse de secours

4. **Personnel (25%)**
   - Enseignants, administration

5. **Quelques dispositions pédagogiques (15%)**
   - Guide, programmes et quotas horaires
""")