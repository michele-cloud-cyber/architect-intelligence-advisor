AI Architect Advisor - Demo locale per Windows
================================================

Contenuto
---------
Questa distribuzione include la foundation dimostrativa multi-cloud locale:
panoramica AWS/Azure/GCP con dati sintetici, modello comune, scenari locali,
Governance Control Plane, orchestratore e registro plugin. Rimangono disponibili
Project Designer, scoring, simulazione S3, generazione Terraform in memoria,
controlli Policy as Code ed esempio CI/CD.

Non contiene credenziali, account reali, state Terraform, access key o connettori
cloud. Non usa SDK cloud, non esegue terraform apply e non modifica infrastrutture.

Requisiti
---------
- Windows 10 o Windows 11
- Python 3.11 o superiore (Python 3.12 consigliato)
- Connessione Internet al primo avvio per installare Streamlit

Avvio
-----
1. Estrai completamente lo ZIP in una cartella scrivibile.
2. Fai doppio clic su start_app.bat.
3. Attendi l'installazione iniziale.
4. Streamlit aprira la dashboard nel browser predefinito.
5. Per arrestare l'app premi CTRL+C nella finestra del prompt.

L'ambiente virtuale .venv viene creato nella cartella estratta e puo essere
eliminato in qualsiasi momento senza perdere dati del progetto.
