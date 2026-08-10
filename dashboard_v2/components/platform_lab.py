"""Bilingual Streamlit UI for Platform Lab phase 1.1."""

from __future__ import annotations

import streamlit as st

from v2.modules.platform_lab import (
    OperatingMode, ProjectDefinition, analyze_project, evaluate_controls,
    generate_s3_package, github_actions_example, package_zip_bytes,
    simulate_s3_changes, validate_s3_package,
)
from v2.modules.platform_lab.scoring import input_quality, maturity_score, overall_score


TXT = {
"it": {
"title":"AWS Interactive Architecture, Security & Terraform Lab","subtitle":"Progetta → analizza → simula → genera → valida. Nessuna modifica AWS o terraform apply.",
"language":"Lingua / Language","mode":"Modalità operativa","demo":"Demo","simulation":"Simulazione","badge":"MODALITÀ","aws_future":"AWS Read-only è solo predisposto e non è collegato.",
"project":"Progetto","analysis":"Analisi","controls":"Controlli","simulate":"Simulazione","terraform":"Terraform","validation":"Validazione","cicd":"CI/CD",
"designer":"Project Designer","name":"Nome progetto","objective":"Obiettivo","description":"Descrizione libera del progetto","services":"Servizi AWS","accounts":"Account demo","environments":"Ambienti","regions":"Regioni","identities":"Utenti, gruppi e ruoli","sensitivity":"Sensibilità dei dati","network":"Requisiti di rete","security":"Requisiti di sicurezza","compliance":"Conformità e audit","availability":"Disponibilità","backup":"Backup e disaster recovery","budget":"Budget mensile","rto":"RTO (ore)","rpo":"RPO (ore)","constraints":"Vincoli aziendali","analyze":"Analizza progetto","provenance":"Provenienza Demo: configurazione fittizia; nessun controllo AWS eseguito.","current":"Configurazione simulata corrente",
"analysis_title":"Analisi e qualità degli input","missing":"Dati mancanti","contradictions":"Contraddizioni","risks":"Rischi","dependencies":"Dipendenze","technical":"Punteggio tecnico","maturity":"Maturità","quality":"Qualità input","confidence":"Confidence","insufficient":"Dati insufficienti","score_note":"Punteggio tecnico = media ponderata dei controlli valutati. I controlli soddisfatti restano sotto 100 per il rischio residuo. Maturità e qualità degli input sono separate.",
"control_table":"Controlli granulari","select_change":"Simula modifica","control":"Controllo","category":"Categoria","configuration":"Configurazione corrente","status":"Stato","risk":"Rischio","severity":"Severità","reason":"Motivazione","remediation":"Remediation","cost":"Costo indicativo","weight":"Peso","probability":"Probabilità","impact":"Impatto","input_key":"Chiave input",
"simulation_title":"Confronto deterministico prima/dopo","simulation_warning":"SIMULAZIONE LOCALE · Non è una verifica AWS e non dimostra che la configurazione reale sia conforme.","run_sim":"Simula modifiche selezionate","choose":"Seleziona almeno una modifica nella tab Controlli.","before":"Prima","after":"Dopo","absolute":"Punti assoluti","relative":"Variazione percentuale","formula":"Variazione percentuale = punti assoluti ÷ punteggio tecnico iniziale.","contributions":"Contributi dichiarati per controllo","eliminated":"Rischi mitigati","residual":"Rischi residui","new":"Nuovi rischi","none":"Nessuno","operational":"Impatto operativo","estimate":"Costo stimato","category_chart":"Punteggio tecnico per categoria","risk_matrix":"Matrice rischio: probabilità × impatto","matrix_note":"La posizione deriva dai valori dichiarati nelle regole; non da telemetria AWS.",
"decision":"Decisione proposta → Terraform","locked":"Esegui prima una simulazione.","generate":"Genera Terraform","local_only":"Generazione locale: nessun plan, apply, modifica AWS, pubblicazione o backend.","files":"File Terraform","generated_file":"File generato","download":"Scarica pacchetto Terraform ZIP","diff":"Diff configurazione corrente → proposta","resources":"Spiegazione risorse","mapping":"Mapping controllo → risorsa Terraform → test","resource":"Risorsa","explanation":"Spiegazione","test":"Test associato",
"validation_title":"Risultati di validazione e sicurezza","validation_truth":"Solo i controlli custom marcati Superato/Fallito sono stati realmente eseguiti sul testo generato. Gli strumenti esterni restano Non eseguito.","check":"Controllo","command":"Comando","result":"Risultato","rationale":"Motivazione","passed":"Superato","warning":"Avviso","failed":"Fallito","not_executed":"Non eseguito",
"pipeline_title":"Pipeline CI/CD dimostrativa","pipeline_note":"Esempio non pubblicato: PR senza apply; plan come artifact; apply protetto e disabilitato finché non viene configurato esplicitamente.",
},
"en": {
"title":"AWS Interactive Architecture, Security & Terraform Lab","subtitle":"Design → analyze → simulate → generate → validate. No AWS mutation or terraform apply.",
"language":"Language / Lingua","mode":"Operating mode","demo":"Demo","simulation":"Simulation","badge":"MODE","aws_future":"AWS Read-only is architecture-only and not connected.",
"project":"Project","analysis":"Analysis","controls":"Controls","simulate":"Simulation","terraform":"Terraform","validation":"Validation","cicd":"CI/CD",
"designer":"Project Designer","name":"Project name","objective":"Objective","description":"Free project description","services":"AWS services","accounts":"Demo accounts","environments":"Environments","regions":"Regions","identities":"Users, groups and roles","sensitivity":"Data sensitivity","network":"Network requirements","security":"Security requirements","compliance":"Compliance and audit","availability":"Availability","backup":"Backup and disaster recovery","budget":"Monthly budget","rto":"RTO hours","rpo":"RPO hours","constraints":"Business constraints","analyze":"Analyze project","provenance":"Demo provenance: fictional configuration; no AWS check was executed.","current":"Current simulated configuration",
"analysis_title":"Analysis and input quality","missing":"Missing data","contradictions":"Contradictions","risks":"Risks","dependencies":"Dependencies","technical":"Technical score","maturity":"Maturity","quality":"Input quality","confidence":"Confidence","insufficient":"Insufficient data","score_note":"Technical score = weighted average of evaluated controls. Satisfied controls remain below 100 due to residual risk. Maturity and input quality are separate.",
"control_table":"Granular controls","select_change":"Simulate change","control":"Control","category":"Category","configuration":"Current configuration","status":"Status","risk":"Risk","severity":"Severity","reason":"Rationale","remediation":"Remediation","cost":"Indicative cost","weight":"Weight","probability":"Likelihood","impact":"Impact","input_key":"Input key",
"simulation_title":"Deterministic before/after comparison","simulation_warning":"LOCAL SIMULATION · This is not an AWS verification and does not prove real configuration compliance.","run_sim":"Simulate selected changes","choose":"Select at least one change in the Controls tab.","before":"Before","after":"After","absolute":"Absolute points","relative":"Percentage change","formula":"Percentage change = absolute points ÷ initial technical score.","contributions":"Declared contribution by control","eliminated":"Mitigated risks","residual":"Residual risks","new":"New risks","none":"None","operational":"Operational impact","estimate":"Estimated cost","category_chart":"Technical score by category","risk_matrix":"Risk matrix: likelihood × impact","matrix_note":"Positions use declared rule values, not AWS telemetry.",
"decision":"Proposed decision → Terraform","locked":"Run a simulation first.","generate":"Generate Terraform","local_only":"Local generation: no plan, apply, AWS mutation, publication or backend.","files":"Terraform files","generated_file":"Generated file","download":"Download Terraform ZIP package","diff":"Diff current configuration → proposal","resources":"Resource explanations","mapping":"Control → Terraform resource → test mapping","resource":"Resource","explanation":"Explanation","test":"Associated test",
"validation_title":"Validation and security results","validation_truth":"Only custom checks marked Passed/Failed were actually executed against generated text. External tools remain Not executed.","check":"Check","command":"Command","result":"Result","rationale":"Rationale","passed":"Passed","warning":"Warning","failed":"Failed","not_executed":"Not executed",
"pipeline_title":"CI/CD pipeline example","pipeline_note":"Not published: pull requests cannot apply; plan is an artifact; apply is protected and inert until explicitly configured.",
}}

CATEGORY_IT = {"Security":"Sicurezza","IAM & Access Control":"IAM e controllo accessi","Network":"Rete","Audit & Compliance":"Audit e conformità","Data Protection":"Protezione dati","Reliability":"Affidabilità","Operational Excellence":"Eccellenza operativa","Cost Optimization":"Ottimizzazione costi"}


def render_platform_lab() -> None:
    language_label = st.radio("Language / Lingua", ["Italiano", "English"], horizontal=True, key="lab_language")
    lang = "it" if language_label == "Italiano" else "en"
    t = TXT[lang]
    if st.session_state.get("lab_language_previous") != lang:
        st.session_state.pop("lab_simulation", None); st.session_state.pop("lab_package", None)
        st.session_state["lab_language_previous"] = lang
    st.title(t["title"]); st.caption(t["subtitle"])
    mode_label = st.radio(t["mode"], [t["demo"], t["simulation"]], horizontal=True, key=f"lab_mode_{lang}")
    mode = OperatingMode.DEMO if mode_label == t["demo"] else OperatingMode.SIMULATION
    st.markdown(f'<span style="background:#2563eb;color:white;padding:.35rem .75rem;border-radius:999px;font-weight:700">{t["badge"]} · {mode_label.upper()}</span>', unsafe_allow_html=True)
    st.caption(t["aws_future"])
    tabs = st.tabs([t[k] for k in ("project","analysis","controls","simulate","terraform","validation","cicd")])
    with tabs[0]: project = _project_designer(mode, lang, t)
    analysis = analyze_project(project, lang); results, scores = evaluate_controls(project.configuration, lang)
    with tabs[1]: _render_analysis(project, analysis, scores, t, lang)
    with tabs[2]: selected = _render_controls(results, t, lang)
    with tabs[3]: _render_simulation(project, selected, scores, results, t, lang)
    simulation = st.session_state.get("lab_simulation")
    with tabs[4]: _render_terraform(project, simulation, t, lang)
    package = st.session_state.get("lab_package")
    with tabs[5]: _render_validation(package, t, lang)
    with tabs[6]: _render_pipeline(t)


def _project_designer(mode, lang, t):
    st.header(t["designer"])
    with st.form(f"project_designer_{lang}"):
        a,b=st.columns(2)
        with a:
            name=st.text_input(t["name"],"Secure S3 Architecture Lab"); objective=st.text_input(t["objective"],"Proteggere artefatti aziendali in S3" if lang=="it" else "Protect business artifacts in S3")
            description=st.text_area(t["description"],"Bucket privato per artefatti riservati." if lang=="it" else "Private bucket for confidential artifacts.")
            services=st.multiselect(t["services"],["S3","IAM","CloudTrail","KMS","CloudWatch","AWS Config"],["S3","IAM","CloudTrail"]); accounts=st.text_input(t["accounts"],"demo-account")
            environments=st.multiselect(t["environments"],["development","staging","production"],["development"]); regions=st.multiselect(t["regions"],["eu-west-1","eu-central-1","eu-south-1","us-east-1"],["eu-west-1"]); identities=st.text_area(t["identities"],"Ruolo applicativo e ruolo audit read-only" if lang=="it" else "Application role and read-only audit role")
        with b:
            sensitivity=st.selectbox(t["sensitivity"],["Pubblici","Interni","Confidenziali","Riservati"] if lang=="it" else ["Public","Internal","Confidential","Restricted"],index=2)
            network=st.text_input(t["network"],"Solo TLS; nessun accesso pubblico" if lang=="it" else "TLS only; no public access"); security=st.text_input(t["security"],"Privato, cifrato, versionato e registrato" if lang=="it" else "Private, encrypted, versioned and logged")
            compliance=st.text_input(t["compliance"],"Evidenze di accesso conservate" if lang=="it" else "Retain access evidence"); availability=st.text_input(t["availability"],"Recupero da sovrascrittura accidentale" if lang=="it" else "Recovery from accidental overwrite"); backup=st.text_input(t["backup"],"Versioning e retention 90 giorni" if lang=="it" else "Versioning and 90-day retention"); budget=st.text_input(t["budget"],"EUR 50")
            x,y=st.columns(2); rto=x.number_input(t["rto"],min_value=0,value=4); rpo=y.number_input(t["rpo"],min_value=0,value=1); constraints=st.text_input(t["constraints"],"Nessuna credenziale; approvazione manuale" if lang=="it" else "No credentials; manual approval")
        st.form_submit_button(t["analyze"])
    config={"block_public_access":False,"encryption":False,"versioning":False,"logging":False,"enforce_tls":False,"least_privilege":True,"monitoring":False,"lifecycle":False}
    if mode==OperatingMode.SIMULATION:
        st.subheader(t["current"]); cols=st.columns(4)
        labels={"block_public_access":"Public Access Block","encryption":"Encryption","versioning":"Versioning","logging":"Logging","enforce_tls":"TLS","least_privilege":"Least privilege","monitoring":"Monitoring","lifecycle":"Lifecycle"}
        for i,(key,label) in enumerate(labels.items()): config[key]=cols[i%4].checkbox(label,value=config[key],key=f"current_{lang}_{key}")
    else: st.info(t["provenance"])
    return ProjectDefinition(name,objective,description,tuple(services),tuple(v.strip() for v in accounts.split(",") if v.strip()),tuple(environments),tuple(regions),identities,sensitivity,network,security,compliance,availability,backup,budget,int(rto),int(rpo),constraints,mode,config)


def _render_analysis(project, analysis, scores, t, lang):
    st.header(t["analysis_title"]); cols=st.columns(4)
    for col,title,values in zip(cols,(t["missing"],t["contradictions"],t["risks"],t["dependencies"]),(analysis.missing_information,analysis.contradictions,analysis.risks,analysis.dependencies)):
        with col.container(border=True): st.metric(title,len(values)); [st.caption(f"• {v}") for v in values[:3]]
    metrics=st.columns(3); metrics[0].metric(t["technical"],f"{overall_score(scores)}/100"); metrics[1].metric(t["maturity"],f"{maturity_score(project.configuration)}/100"); metrics[2].metric(t["quality"],f"{input_quality(project)}/100")
    st.info(t["score_note"]); _score_cards(scores,t,lang)


def _score_cards(scores,t,lang):
    cols=st.columns(4)
    for i,(category,score) in enumerate(scores.items()):
        color="#64748b" if score is None else "#22c55e" if score>=80 else "#eab308" if score>=60 else "#f97316" if score>=40 else "#ef4444"; label=CATEGORY_IT.get(category,category) if lang=="it" else category; value=t["insufficient"] if score is None else f"{score}/100"
        cols[i%4].markdown(f'<div style="border:1px solid #334155;border-left:6px solid {color};padding:1rem;border-radius:.6rem;margin-bottom:1rem"><small>{label}</small><h3>{value}</h3></div>',unsafe_allow_html=True)


def _render_controls(results,t,lang):
    st.header(t["control_table"]); status_map={"Correct":"Corretto","Improvable":"Migliorabile","Medium risk":"Rischio medio","High risk":"Rischio elevato","Insufficient data":"Dati insufficienti"}
    rows=[]
    for item in results:
        rows.append({t["select_change"]:item.score==15,t["control"]:item.definition.control_id,t["category"]:CATEGORY_IT.get(item.definition.category,item.definition.category) if lang=="it" else item.definition.category,t["configuration"]:item.current_value,t["status"]:status_map.get(item.status.value,item.status.value) if lang=="it" else item.status.value,t["risk"]:item.definition.description,t["severity"]:item.severity,t["reason"]:item.rationale,t["remediation"]:item.definition.remediation,t["cost"]:item.definition.estimated_monthly_cost,t["weight"]:item.definition.weight,t["probability"]:item.definition.likelihood,t["impact"]:item.definition.impact,t["input_key"]:item.definition.input_key})
    edited=st.data_editor(rows,hide_index=True,width="stretch",disabled=[k for k in rows[0] if k!=t["select_change"]],column_config={t["select_change"]:st.column_config.CheckboxColumn(t["select_change"])},key=f"lab_controls_{lang}")
    return [row[t["input_key"]] for row in edited if row[t["select_change"]]]


def _render_simulation(project,selected,scores,results,t,lang):
    st.header(t["simulation_title"]); st.warning(t["simulation_warning"])
    if st.button(t["run_sim"],type="primary",disabled=not selected,key=f"simulate_{lang}"):
        st.session_state["lab_simulation"]=simulate_s3_changes(project.configuration,tuple(selected),project,lang); st.session_state.pop("lab_package",None)
    sim=st.session_state.get("lab_simulation")
    if sim is None: st.info(t["choose"]); return
    cols=st.columns(4); cols[0].metric(t["before"],f"{sim.technical_before}/100"); cols[1].metric(t["after"],f"{sim.technical_after}/100"); cols[2].metric(t["absolute"],f"+{sim.absolute_delta}"); cols[3].metric(t["relative"],f"+{sim.percentage_delta}%")
    st.caption(t["formula"]); st.write(f"**{t['maturity']}:** {sim.maturity_before} → {sim.maturity_after} · **{t['quality']}:** {sim.input_quality}/100 · **{t['confidence']}:** {sim.confidence}%")
    st.subheader(t["category_chart"]); _before_after_chart(sim,lang)
    st.subheader(t["risk_matrix"]); _risk_matrix(results,lang); st.caption(t["matrix_note"])
    st.subheader(t["contributions"]); st.dataframe(list(sim.contributions),hide_index=True,width="stretch")
    a,b,c=st.columns(3); a.success(t["eliminated"]+"\n\n"+"\n\n".join(f"• {v}" for v in sim.eliminated_risks)); b.warning(t["residual"]+"\n\n"+"\n\n".join(f"• {v}" for v in sim.residual_risks)); c.info(t["new"]+"\n\n"+("\n\n".join(f"• {v}" for v in sim.new_risks) or f"• {t['none']}")); st.write(f"**{t['operational']}:** {sim.operational_impact}"); st.write(f"**{t['estimate']}:** {sim.estimated_cost}")


def _before_after_chart(sim,lang):
    values=[]
    for category in sim.before_scores:
        label=CATEGORY_IT.get(category,category) if lang=="it" else category
        values.extend([{"category":label,"phase":"Prima" if lang=="it" else "Before","score":sim.before_scores[category] or 0},{"category":label,"phase":"Dopo" if lang=="it" else "After","score":sim.after_scores[category] or 0}])
    st.vega_lite_chart({"values":values},{"mark":"bar","encoding":{"x":{"field":"category","type":"nominal","axis":{"labelAngle":-35}},"y":{"field":"score","type":"quantitative","scale":{"domain":[0,100]}},"color":{"field":"phase","type":"nominal","scale":{"range":["#f97316","#22c55e"]}},"xOffset":{"field":"phase"},"tooltip":[{"field":"category"},{"field":"phase"},{"field":"score"}]}},width="stretch")


def _risk_matrix(results,lang):
    values=[{"control":r.definition.control_id,"description":r.definition.description,"likelihood":r.definition.likelihood,"impact":r.definition.impact,"severity":r.severity,"size":r.definition.weight*12} for r in results]
    st.vega_lite_chart({"values":values},{"mark":{"type":"circle","opacity":0.85},"encoding":{"x":{"field":"likelihood","type":"quantitative","scale":{"domain":[0.5,5.5]},"title":"Probabilità" if lang=="it" else "Likelihood"},"y":{"field":"impact","type":"quantitative","scale":{"domain":[0.5,5.5]},"title":"Impatto" if lang=="it" else "Impact"},"size":{"field":"size","type":"quantitative","legend":None},"color":{"field":"impact","type":"quantitative","scale":{"range":["#22c55e","#eab308","#f97316","#ef4444"]}},"tooltip":[{"field":"control"},{"field":"description"},{"field":"likelihood"},{"field":"impact"}]}},width="stretch")


def _render_terraform(project,sim,t,lang):
    st.header(t["decision"])
    if sim is None: st.info(t["locked"]); return
    st.warning(t["local_only"])
    if st.button(t["generate"],type="primary",key=f"generate_tf_{lang}"): st.session_state["lab_package"]=generate_s3_package(project,sim,lang)
    package=st.session_state.get("lab_package")
    if package is None:return
    st.download_button(t["download"],package_zip_bytes(package),"secure-s3-terraform.zip","application/zip")
    st.subheader(t["files"]); selected=st.selectbox(t["generated_file"],list(package.files),key=f"tf_file_{lang}"); st.code(package.files[selected],language="hcl" if selected.endswith((".tf",".hcl",".tfvars")) else "markdown")
    st.subheader(t["diff"]); st.code(package.diff,language="diff")
    st.subheader(t["resources"]); st.dataframe([{t["resource"]:v["resource"],t["explanation"]:v["explanation"]} for v in package.resource_explanations],hide_index=True,width="stretch")
    st.subheader(t["mapping"]); st.dataframe([{t["control"]:v["control"],t["resource"]:v["terraform"],t["test"]:v["test"]} for v in package.mappings],hide_index=True,width="stretch")


def _render_validation(package,t,lang):
    st.header(t["validation_title"]); st.info(t["validation_truth"])
    if package is None: st.info(t["locked"]); return
    status_it={"Passed":t["passed"],"Warning":t["warning"],"Failed":t["failed"],"Not executed":t["not_executed"]}
    rows=[{t["check"]:v.check,t["command"]:v.command,t["status"]:status_it.get(v.status,v.status),t["result"]:v.result,t["rationale"]:v.rationale} for v in validate_s3_package(package,lang)]
    st.dataframe(rows,hide_index=True,width="stretch")


def _render_pipeline(t):
    st.header(t["pipeline_title"]); st.warning(t["pipeline_note"]); st.code(github_actions_example(),language="yaml")
