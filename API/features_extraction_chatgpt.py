from utils import get_secret
import openai

def generate_prompt(text, document_type, chatgpt_api_key):
    """
    # 0 -> certifications
    # 1 -> DPE
    # 2 -> fichier descprtif
    # 3 -> rapport d'expertise 
    """
    openai.api_key = chatgpt_api_key
    
    prompts = {}

    prompts[0] = (f"Je veux extraire les informations suivantes:"

                    "BREEAM Certification Level,"
                    "WELL Certification Level," 
                    "LEED Certification Level," 
                    "WIRESCORE Certification Level,"
                    "avec les dates."

                    "Affichier les résults sous la forme d'un tableau avec 3 colonnes certification Type, level et la date."

                    "Ne pas donner des explications où détails sur les résultats."
                
                    "Si les informations n'exsitant pas renvoyer NA."

                    f"```{text}```")

    prompts[1] = (f"Je veux extraire des informations dans ce document."
                     
                        "Est ce que ces valeurs exsite dans le document:"
                        "système de production"
                        "d'Energie renouvelable?"
                     
                        "Est ce que tu peux me fournir ces valeurs à partir du docuement:"
                     
                        "surface utile"  
                        "Consommation réelle"
                        "Estimation des émissions"
                        "Diagnostic performance GES et GHG"
                        "Performance énergétique du bâtiment"
                         
                        "Ne pas donner des explications où détails sur les résultats."

                        "Si les informations n'exsitant pas renvoyer NA."
                         
                        f"```{text}```")
    
    prompts[2] = (f"Tu peux trouver les informations suivantes dans le document:"
                             
                    "Crèche, Gardien, Salle de formation, Services numériques"
                    "Services de réunions publiques, air de livraison" 
                    "Télécom sécurisé, GTB, GTC, BMS, Réduction COV"
                    "Réverbération, isolation acoustique, ventilation"
                    "Âge CVC, Hygrométrie, système d'extinction, Désenfumage"
                    "locaux déchets, ventilo-convecteurs, Parking CO2, Recyclage des eaux"
                    "Tri des déchets, Isolation des murs, compteur d'énergie autonome"
                    "Présence d'un monte-charge, faux plafonds, Faux plancher."
                    "EFFECTIF THEORIQUE, Nombre de Parkings, âge du système d'éclairage,"
                    "âge du système de régulation thermique, hauteur de dalle à dalle, "
                    "Last refurbishment age, Refurbishment workspace age, Ceiling height,"
                    "Densité maximale (capacitaire)."
                    
                    "Affichier les résultats sous la forme d'un tableau."
                    
                    "Ne pas donner des explications où détails sur les résultats."
                    
                    "Si les informations n'exsitant pas renvoyer NA."
                    
                    f"```{text}```")

    prompts[3] = (f"Tu peux trouver les informations suivantes dans le document:"
                             
                    "Appraised net capital value, Net Market Value, area, Gross value,"
                    "lettable area, Equivalent yield, initial yield, reversionary yield,"
                    "Rent, Vacancy rate"
                    "EFFECTIF THEORIQUE, Nombre de Parkings, âge du système d'éclairage,"
                    "âge du système de régulation thermique, hauteur de dalle à dalle,"
                    "Last refurbishment age, Refurbishment workspace age,"
            
                    "Affichier les résultats sous la forme d'un tableau."
                        
                    "Ne pas donner des explications où détails sur les résultats."
                        
                    "Si les informations n'exsitant pas renvoyer NA."
                        
                    f"```{text}```")

    prompt_template = prompts.get(document_type)
    if not prompt_template:
        raise ValueError(f"Unsupported document type: {document_type}")
    
    return prompt_template.format(text=text)

def get_document_information(prompt):

    response = openai.ChatCompletion.create(
        model='gpt-4-1106-preview',  # Vous pouvez aussi essayer "gpt-3.5-turbo"
        messages=[{"role": "user", "content": prompt}],
        max_tokens=550,
        n=1,
        stop=None,
        temperature=0.7
    )
    answer = response.choices[0].message['content'].strip()

    return answer

def chatgpt_pipeline(text, document_type, chatgpt_api_key):
    text_with_prompt = generate_prompt(text.strip(), document_type, chatgpt_api_key)
    chatgpt_answer = get_document_information(text_with_prompt)
    return chatgpt_answer
