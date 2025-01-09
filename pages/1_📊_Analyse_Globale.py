import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(layout="wide", page_title="Analyse des Normes Administratives - Collèges Privés Alibori")

@st.cache_data
def load_data():
    return pd.read_excel("Données contrôle.xlsx")

df = load_data()

st.title(":blue[Analyse Globale des Normes Administratives]")

# 1. Analyse des infrastructures de base
st.header(":blue[1. Infrastructures et mobiliers]")
col1, col2 = st.columns(2)

with col1:
    infra_base = pd.DataFrame({
        'Infrastructure': ['Point d\'eau', 'Électricité', 'Latrines élèves', 'Latrines Ens.'],
        'Disponible': [
            sum(df['2.10. Disponibilité de point d\'eau potable'] == 'Oui'),
            sum(df['2.11. Disponibilité d\'énergie électrique'] == 'Oui'),
            sum(df['3.6. Disponibilité de latrines ou sanitaires'] == 'Oui'),
            sum(df['3.8. Disponibilité de latrines ou sanitaires pour personnel administratif et enseignant'] == 'Oui')
        ],
        'Non Disponible': [
            sum(df['2.10. Disponibilité de point d\'eau potable'] == 'Non'),
            sum(df['2.11. Disponibilité d\'énergie électrique'] == 'Non'),
            sum(df['3.6. Disponibilité de latrines ou sanitaires'] == 'Non'),
            sum(df['3.8. Disponibilité de latrines ou sanitaires pour personnel administratif et enseignant'] == 'Non')
        ]
    })
    
    fig_infra = go.Figure(data=[
        go.Bar(name='Disponible', x=infra_base['Infrastructure'], y=infra_base['Disponible']),
        go.Bar(name='Non Disponible', x=infra_base['Infrastructure'], y=infra_base['Non Disponible'])
    ])
    fig_infra.update_layout(barmode='stack', title='Disponibilité des infrastructures de base')
    st.plotly_chart(fig_infra)



with col2:
    # Analyse des salles de classe
    salles_suffisantes = sum(df['2.15. Nombre de salles de classes'] >= df['1.10. Nombre total de Groupes Pédagogiques'])
    places_suffisantes = sum((df['2.16.b. Nombre de tables bancs à 2 places'] * 2 + df['2.16.a. Nombre de tables bancs à 1 place']) >= df['1.9. Effectif total des élèves'])
    
    infra_scolaire = pd.DataFrame({
        'Critère': ['Salles suffisantes', 'Places suffisantes', 'Salles aérées', 'Bonne toiture des salles', 'Cour récréation', 'Aire EPS'],
        'Conforme/Disponible': [
            salles_suffisantes,
            places_suffisantes,
            sum(df['2.14. Disponibilité de salles de classes aérées et bien éclairées'] == 'Oui'),
            sum(df['2.5. Etat de la toiture des salles de classe'] == 'Bon'),
            sum(df['2.6. Disponibilité d\'une cour de récréation '] == 'Oui'),
            sum(df['2.9. Disponibilité d\'aire d\'EPS'] == 'Oui')
        ],
        'Non Conforme/Non Disponible': [
            len(df) - salles_suffisantes,
            len(df) - places_suffisantes,
            sum(df['2.14. Disponibilité de salles de classes aérées et bien éclairées'] == 'Non'),
            sum(df['2.5. Etat de la toiture des salles de classe'] != 'Bon'),
            sum(df['2.6. Disponibilité d\'une cour de récréation '] == 'Non'),
            sum(df['2.9. Disponibilité d\'aire d\'EPS'] == 'Non')
        ]
    })
    
    fig_scolaire = go.Figure(data=[
        go.Bar(name='Conforme/Disponible', x=infra_scolaire['Critère'], y=infra_scolaire['Conforme/Disponible']),
        go.Bar(name='Non Conforme/Non Disponible', x=infra_scolaire['Critère'], y=infra_scolaire['Non Conforme/Non Disponible'])
    ])
    fig_scolaire.update_layout(barmode='stack', title='Disponiblilité et État des infrastructures scolaires')
    st.plotly_chart(fig_scolaire)

# 2. Salubrité
st.header(":blue[2. Salubrité et Hygiène]")

salubrite_data = {
    'Critère': ['Salubrité cour', 'Salubrité réfectoire', 'Disponibilité Poubelles', 'DLM', 'Visite médicale Vendeuses', 'Boîte Pharmacie'],
    'Respecté(e)': [
        sum(df['3.1. Salubrité dans la cour de l\'établissement'] == 'Bonne'),
        sum(df['3.4. Hygiène et salubrité au réfectoire scolaire'] == 'Bonne'),
        sum(df['3.2. Disponibilité de poubelles'] == 'Oui'),
        sum(df['3.3. Disponibilité de dispositifs de lavage de main'] == 'Oui'),
        sum(df['3.5. Visite médicale des vendeuses du réfectoire'] == 'Oui'),
        sum(df['3.9. Disponibilité de boite à pharmacie'] == 'Oui')
    ],
    'Non Respecté(e)': [
        sum(df['3.1. Salubrité dans la cour de l\'établissement'] != 'Bonne'),
        sum(df['3.4. Hygiène et salubrité au réfectoire scolaire'] != 'Bonne'),
        sum(df['3.2. Disponibilité de poubelles'] == 'Non'),
        sum(df['3.3. Disponibilité de dispositifs de lavage de main'] == 'Non'),
        sum(df['3.5. Visite médicale des vendeuses du réfectoire'] == 'Non'),
        sum(df['3.9. Disponibilité de boite à pharmacie'] == 'Non')
    ]
}

fig_salubrite = go.Figure(data=[
    go.Bar(name='Respecté(e)', x=salubrite_data['Critère'], y=salubrite_data['Respecté(e)']),
    go.Bar(name='Non Respecté(e)', x=salubrite_data['Critère'], y=salubrite_data['Non Respecté(e)'])
])
fig_salubrite.update_layout(
    title='État de la salubrité et de l\'hygiène',
    barmode='stack'
)
st.plotly_chart(fig_salubrite)

# 3. Personnel
st.header(":blue[3. Personnel Administratif et Enseignant]")
col3, col4 = st.columns(2)
# Statistiques du personnel
with col3:

    personnel_stats = {
        'Total enseignants': df['4.3. Nombre total d\'enseignants (chargé de cours)'].sum(),
        'Enseignants permanents': df['4.4. Nombre d\'enseignants permanents'].sum(),
        'Enseignants autorisés': df['4.5. Nombre d\'enseignants permanents possédant d\'autorisation d\'enseigner'].sum(),
        'Enseignants de 3ième Qualifiés': df['4.6. Nombre d\'enseignants de la classe de 3ième titulaires d\'un diplôme professionnel (BAPES ou CAPES)'].sum()
    }

    fig_personnel = go.Figure(data=[go.Bar(x=list(personnel_stats.keys()), y=list(personnel_stats.values()))])
    fig_personnel.update_layout(title='Répartition du personnel enseignant')
    st.plotly_chart(fig_personnel)

with col4:
    # Proportion d'établissements avec administration complète
    admin_roles = df['4.1. Personnel administratif'].str.split()
    admin_complet = sum(['Directeur/Drectrice' in str(roles) and 'Censeur(e)' in str(roles) and 'Surveillant(e)' in str(roles) for roles in admin_roles])

    fig_admin = go.Figure(data=[go.Pie(
        labels=['Administration complète', 'Administration incomplète'],
        values=[admin_complet, len(df) - admin_complet]
    )])
    fig_admin.update_layout(title='Proportion d\'établissements avec administration complète')
    st.plotly_chart(fig_admin)

# 4. Normes pédagogiques
st.header(":blue[4. Exécution des programmes]")
col5, col6 = st.columns(2)
with col5:
    normes_peda = pd.DataFrame({
        'Norme': ['Quotas horaires par discipline', 'Disponibilité des guides et programmes', 'Disponibilité du planning progression'],
        'Respectée': [
            sum(df['4.8. Respect des quotas horaires hebdomadaires'] == 'Oui'),
            sum(df['2.17. Disponibilité de guides et programmes'] == 'Oui'),
            sum(df['2.18. Disponibilité de planning de progression des SA'] == 'Oui')
        ],
        'Non respectée': [
            sum(df['4.8. Respect des quotas horaires hebdomadaires'] == 'Non'),
            sum(df['2.17. Disponibilité de guides et programmes'] == 'Non'),
            sum(df['2.18. Disponibilité de planning de progression des SA'] == 'Non')
        ]
    })

    fig_peda = go.Figure(data=[
        go.Bar(name='Respectée', x=normes_peda['Norme'], y=normes_peda['Respectée']),
        go.Bar(name='Non respectée', x=normes_peda['Norme'], y=normes_peda['Non respectée'])
    ])
    fig_peda.update_layout(barmode='stack', title='Exécution des programmes scolaires')
    st.plotly_chart(fig_peda)