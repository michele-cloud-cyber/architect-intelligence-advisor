Architect Advisor - Vista completa per Windows
================================================

Launcher disponibili
---------------------
- start_app.bat: versione stabile esistente (streamlit_app.py)
- start_foundation_app.bat: foundation multi-cloud (demo_streamlit_app.py)
- start_complete_app.bat: Vista completa modulare (unified_app.py)

La Vista completa coordina panoramica multi-cloud, Project Designer, simulazioni,
storico, Terraform, validazione, CI/CD, governance e orchestratore. FinOps viene
mostrato come Degraded finché la relativa interfaccia opzionale non è implementata.

Sicurezza e fallback
--------------------
I tre entry point rimangono separati. Il fallback cambia solamente la vista attiva
e non elimina né sovrascrive file. Ogni modulo è racchiuso in un confine di errore.
Il pacchetto usa soltanto dati demo: nessuna connessione cloud, nessuna credenziale,
nessuna pubblicazione e nessun terraform apply.

Avvio consigliato
-----------------
1. Estrai lo ZIP in una cartella scrivibile.
2. Fai doppio clic su start_complete_app.bat.
3. Usa il selettore laterale per Vista completa, Versione stabile, Foundation o
   Modalità diagnostica.
4. Premi CTRL+C nella finestra del prompt per arrestare l'applicazione.

Al primo avvio serve Internet esclusivamente per installare le dipendenze Python.
