import streamlit as st
import pandas as pd
import plotly.express as px
import pandas as pd
import numpy as np

@st.cache_data
def load_data():
    return pd.read_excel("Données contrôle.xlsx")

df = load_data()

def calculate_school_scores(df):
    scores = pd.DataFrame(index=df.index)
    
    # 1. Infrastructures de base
    scores['infra_base'] = (
        (df['2.10. Disponibilité de point d\'eau potable'] == 'Oui').astype(int) +
        (df['2.11. Disponibilité d\'énergie électrique'] == 'Oui').astype(int) +
        (df['3.6. Disponibilité de latrines ou sanitaires'] == 'Oui').astype(int) +
        (df['3.8. Disponibilité de latrines ou sanitaires pour personnel administratif et enseignant'] == 'Oui').astype(int)
    ) / 4

    # 2. Infrastructures et mobiliers scolaires
    scores['suffisance_salles'] = (df['2.15. Nombre de salles de classes'] >= df['1.10. Nombre total de Groupes Pédagogiques']).astype(int)
    scores['suffisance_places'] = (df['2.16.b. Nombre de tables bancs à 2 places'] * 2 + df['2.16.a. Nombre de tables bancs à 1 place'] >= df['1.9. Effectif total des élèves']).astype(int)
    
    scores['infra_mobilier'] = (
        (df['2.1. Clôture de l\'établissement'] == 'établissement entièrement clôturé').astype(int) +
        scores['suffisance_salles'] *2 +
        (df['2.14. Disponibilité de salles de classes aérées et bien éclairées'] == 'Oui').astype(int) +
        (df['2.5. Etat de la toiture des salles de classe'] == 'Bon').astype(int) +
        (df['2.6. Disponibilité d\'une cour de récréation '] == 'Oui').astype(int) +
        (df['2.8. Disponibilité d\'un réfectoire scolaire'] == 'Oui').astype(int) +
        (df['2.9. Disponibilité d\'aire d\'EPS'] == 'Oui').astype(int) +
        scores['suffisance_places'] *2 
    ) / 10

    # 3. Salubrité
    scores['salubrite'] = (
        (df['3.1. Salubrité dans la cour de l\'établissement'] == 'Bonne').astype(int) +
        (df['3.4. Hygiène et salubrité au réfectoire scolaire'] == 'Bonne').astype(int) +
        (df['3.2. Disponibilité de poubelles'] == 'Oui').astype(int) +
        (df['3.3. Disponibilité de dispositifs de lavage de main'] == 'Oui').astype(int) +
        (df['3.5. Visite médicale des vendeuses du réfectoire'] == 'Oui').astype(int) +
        (df['3.9. Disponibilité de boite à pharmacie'] == 'Oui').astype(int)
    ) / 6

    # 4. Personnel
    def check_admin_composition(row):
        required_roles = ['Directeur/Drectrice', 'Censeur(e)', 'Surveillant(e)']
        admin_roles = str(row['4.1. Personnel administratif']).split()
        
        # Compter combien de rôles requis sont présents
        points = sum(1 for role in required_roles if role in admin_roles)
        
        # Calculer le score final (nombre de points divisé par 3)
        return points / 3

    scores['admin_complete'] = df.apply(check_admin_composition, axis=1)
    
    scores['prop_permanents'] = np.where(
        df['4.3. Nombre total d\'enseignants (chargé de cours)'] > 0,
        df['4.4. Nombre d\'enseignants permanents'] / df['4.3. Nombre total d\'enseignants (chargé de cours)'],
        0
    )
    
    scores['prop_autorises'] = np.where(
        df['4.4. Nombre d\'enseignants permanents'] > 0,
        df['4.5. Nombre d\'enseignants permanents possédant d\'autorisation d\'enseigner'] / df['4.4. Nombre d\'enseignants permanents'],
        0
    )
    
    def check_qualified_teachers(row):
        extension_class = str(row['Classe(s) concernée(s) par l\'extension'])
        has_terminal = any(cycle.endswith(('Tle A', 'Tle B', 'Tle C', 'Tle D')) for cycle in extension_class)
        
        if has_terminal:
            return (row['4.6. Nombre d\'enseignants de la classe de 3ième titulaires d\'un diplôme professionnel (BAPES ou CAPES)'] >= 7 and 
                   row['4.7. Nombre d\'enseignants des classes de terminale titulaires d\'un CAPES'] >= 7)
        else:
            return row['4.6. Nombre d\'enseignants de la classe de 3ième titulaires d\'un diplôme professionnel (BAPES ou CAPES)'] >= 7
    
    scores['qualified_teachers'] = df.apply(check_qualified_teachers, axis=1).astype(int)
    
    scores['personnel'] = (
        scores['admin_complete'] +
        (df['4.2. Possession de l\'autorisation de diriger par le Directeur'] == 'Oui').astype(int) +
        scores['prop_permanents'] +
        scores['prop_autorises'] +
        scores['qualified_teachers']
    ) / 5

    # 5. Normes pédagogiques
    scores['normes_peda'] = (
        (df['4.8. Respect des quotas horaires hebdomadaires'] == 'Oui').astype(int) +
        (df['2.17. Disponibilité de guides et programmes'] == 'Oui').astype(int) +
        (df['2.18. Disponibilité de planning de progression des SA'] == 'Oui').astype(int)
    ) / 3

    # Score total
    scores['score_total'] = (
        scores['infra_base'] * 0.2 +
        scores['infra_mobilier'] * 0.2 +
        scores['salubrite'] * 0.2 +
        scores['personnel'] * 0.25 +
        scores['normes_peda'] * 0.15
    )
    
    return scores


scores = calculate_school_scores(df)
df_with_scores = pd.concat([df, scores], axis=1)

df_with_scores.rename({'1.4. Nom de l\'établissement':'Nom de l\'établissement'}, axis=1, inplace=True)

st.title(":blue[Classement des Collèges]")
top_13 = df_with_scores.nlargest(13,'score_total')[['Nom de l\'établissement', 'score_total', 'infra_base', 'infra_mobilier', 'salubrite', 'personnel', 'normes_peda']].reset_index(drop=True)
bottom_13 = df_with_scores.nsmallest(13, 'score_total')[['Nom de l\'établissement', 'score_total', 'infra_base', 'infra_mobilier', 'salubrite', 'personnel', 'normes_peda']].reset_index(drop=True)

# Trier par score_total de manière décroissante et réinitialiser l'index
bottom_13 = bottom_13.sort_values('score_total', ascending=False).reset_index(drop=True)


st.header(":blue[Classement des établissements]")
fig_top = px.bar(top_13, x='Nom de l\'établissement', y='score_total', text='score_total',
                    title="13 meilleurs établissements")
fig_top.update_xaxes(title=None)
fig_top.update_traces(texttemplate='%{text:.3f}', textposition='inside')
st.plotly_chart(fig_top)
#st.dataframe(top_13.round(3))


st.header(":blue[Classement des établissements (suite)]")
fig_bottom = px.bar(bottom_13, x='Nom de l\'établissement', y='score_total',text='score_total',
                    title="13 établissements restant",)
fig_bottom.update_xaxes(title=None)
fig_bottom.update_traces(texttemplate='%{text:.3f}', textposition='inside')
st.plotly_chart(fig_bottom)
#st.dataframe(bottom_13.round(3))

st.markdown("👇 Retour à la page d'accueil")
st.page_link("Home.py", label="Accéder à la page d'accueil")
st.write("")

st.markdown("👇 Cliquez ci-dessous pour accéder aux points d'amélioration")
st.page_link("pages/3_📝_Points_d'Amelioration.py", label="Accéder aux Points d'Amélioration")