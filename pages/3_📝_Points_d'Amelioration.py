import streamlit as st
import pandas as pd
import plotly.express as px
import pandas as pd
import numpy as np


st.set_page_config(page_title="Points d'Amélioration")

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
        scores['suffisance_salles'] +
        (df['2.14. Disponibilité de salles de classes aérées et bien éclairées'] == 'Oui').astype(int) +
        (df['2.5. Etat de la toiture des salles de classe'] == 'Bon').astype(int) +
        (df['2.6. Disponibilité d\'une cour de récréation '] == 'Oui').astype(int) +
        (df['2.8. Disponibilité d\'un réfectoire scolaire'] == 'Oui').astype(int) +
        (df['2.9. Disponibilité d\'aire d\'EPS'] == 'Oui').astype(int) +
        scores['suffisance_places']
    ) / 8

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

st.title(":blue[Points d'Amélioration par Collège]")

selected_school = st.selectbox('Sélectionner un établissement:', df['1.4. Nom de l\'établissement'].unique())
school_data = df_with_scores[df_with_scores['1.4. Nom de l\'établissement'] == selected_school].iloc[0]

col1, col2 = st.columns([2,1])

with col1:
    # Graphique radar des scores
    categories = ['Infrastr. de base', 'Infrastr. et mobiliers', 'Salubrité', 'Personnel', 'Programmes.']
    scores = [school_data['infra_base'], school_data['infra_mobilier'], 
             school_data['salubrite'], school_data['personnel'], 
             school_data['normes_peda']]
    
    fig = px.line_polar(r=scores, theta=categories, line_close=True)
    fig.update_traces(fill='toself')
    st.plotly_chart(fig)

with col2:
    st.subheader("Score total")
    st.metric("Score", f"{school_data['score_total']:.2f}")

st.subheader(":blue[Points à améliorer]")


improvements = []
def check_category(score, threshold, category, details):
    if score < threshold:
        improvements.extend(details)

check_category(school_data['infra_base'], 0.75, "Infrastructures de base", [
    "- Disposer d'un point d'eau potable" if school_data['2.10. Disponibilité de point d\'eau potable'] != 'Oui' else None,
    "- Disposer d'une source d'électricité" if school_data['2.11. Disponibilité d\'énergie électrique'] != 'Oui' else None,
    "- Construire des latrines pour les élèves" if school_data['3.6. Disponibilité de latrines ou sanitaires'] != 'Oui' else None,
    "- Construire des latrines pour l'administration" if school_data['3.8. Disponibilité de latrines ou sanitaires pour personnel administratif et enseignant'] != 'Oui' else None
])

check_category(school_data['infra_mobilier'], 0.75, "Infrastructures et mobiliers", [
    "- Clôturer entièrement le collège" if school_data['2.1. Clôture de l\'établissement'] != 'établissement entièrement clôturé' else None,
    "- Construire de salles de classe" if not school_data['suffisance_salles'] else None,
    "- Améliorer l'aération et l'éclairage des salles de classe" if school_data['2.14. Disponibilité de salles de classes aérées et bien éclairées'] != 'Oui' else None,
    "- Réfectionner la toiture des salles de classe" if school_data['2.5. Etat de la toiture des salles de classe'] != 'Bon' else None,
    "- Disposer d'une cour de récréation exclusivement pour le collège" if school_data['2.6. Disponibilité d\'une cour de récréation '] != 'Oui' else None,
    "- Disposer d'un réfectoire" if school_data['2.8. Disponibilité d\'un réfectoire scolaire'] != 'Oui' else None,
    "- Disposer d'une aire d'EPS" if school_data['2.9. Disponibilité d\'aire d\'EPS'] != 'Oui' else None,
    "- Acquérir de tables-bancs complémetaires" if not school_data['suffisance_places'] else None
])

check_category(school_data['salubrite'], 0.75, "Salubrité et hygiène", [
    "- Améliorer la salubrité de la cour" if school_data['3.1. Salubrité dans la cour de l\'établissement'] != 'Bonne' else None,
    "- Améliorer la salubrité du réfectoire" if school_data['3.4. Hygiène et salubrité au réfectoire scolaire'] != 'Bonne' else None,
    "- Disposer de poubelles" if school_data['3.2. Disponibilité de poubelles'] != 'Oui' else None,
    "- Installer des Dispositifs de Lavage des Mains fonctionnels" if school_data['3.3. Disponibilité de dispositifs de lavage de main'] != 'Oui' else None,
    "- Faire faire des visites médicales aux vendeuses" if school_data['3.5. Visite médicale des vendeuses du réfectoire'] != 'Oui' else None,
    "- Disposer d'une trousse de secours" if school_data['3.9. Disponibilité de boite à pharmacie'] != 'Oui' else None
])

def check_missing_admin_roles(school_data):
    required_roles = ['Directeur/Drectrice', 'Censeur(e)', 'Surveillant(e)']
    admin_roles = str(school_data['4.1. Personnel administratif']).split()
    
    # Vérifier quels postes manquent
    missing_roles = [role for role in required_roles if role not in admin_roles]
    
    if missing_roles:
        return f"- Pourvoir en personnel le/les poste(s) de {', '.join(missing_roles)} "
    return None


check_category(school_data['personnel'], 0.75, "Personnel", [
    check_missing_admin_roles(school_data),
    "- Disposer d'une autorisation de diriger pour le Directeur" if school_data['4.2. Possession de l\'autorisation de diriger par le Directeur'] != 'Oui' else None,
    "- Améliorer la proportion d'enseignants permanents" if school_data['prop_permanents'] < 1/3 else None,
    "- Améliorer la proportion d'enseignants autorisés" if school_data['prop_autorises'] < 0.5 else None,
    "- Améliorer la proportion d'enseignants qualifiés" if not school_data['qualified_teachers'] else None
])

check_category(school_data['normes_peda'], 0.75, "Normes pédagogiques", [
    "- Respecter les quotas horaires par discipline" if school_data['4.8. Respect des quotas horaires hebdomadaires'] != 'Oui' else None,
    "- Disposer de guides et programmes" if school_data['2.17. Disponibilité de guides et programmes'] != 'Oui' else None,
    "- Disposer de planning de progression" if school_data['2.18. Disponibilité de planning de progression des SA'] != 'Oui' else None
])

improvements = [imp for imp in improvements if imp is not None]

if improvements:
    for imp in improvements:
        st.write(imp)
else:
    st.write("Cet établissement respecte bien les normes dans l'ensemble.")

st.write("")
st.markdown("👇 Retour à la page d'accueil")
st.page_link("Home.py", label="Accéder à la page d'accueil")
