"""Bilingual V3 Code → Architecture, Risk and FinOps experience."""

from __future__ import annotations
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile
import streamlit as st

from v2.modules.code_architecture import InputSecurityError, InputSecurityGateway, analyze_terraform, simulate_remediation


SAMPLE='''resource "aws_instance" "web" {
  ami           = "ami-demo"
  instance_type = "t3.micro"
  metadata_options {
    http_endpoint = "enabled"
    http_put_response_hop_limit = 2
  }
}

resource "aws_security_group" "web" {
  ingress {
    from_port = 22
    to_port = 22
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_s3_bucket" "data" { bucket = "demo-data" }
'''

T={
"it":{"title":"Code → Architecture & Risk","note":"Solo analisi statica locale: nessuna esecuzione, rete, init, plan, apply, destroy o download moduli.","paste":"Incolla Terraform","upload":"Carica .tf o ZIP controllato","provider":"Provider dichiarato","env":"Ambiente","state":"Stato","analyze":"Analizza staticamente","architecture":"Architettura visuale","findings":"Finding granulari","resource":"Dettaglio risorsa","simulate":"Simula remediation selezionate","download":"Scarica copia proposta ZIP","finops":"FinOps demo trasversale","legend":"Legenda: 🟢 conforme · 🟡 basso · 🟠 medio · 🔴 alto/critico · 🟣 dipendenza esterna · ⚪ non determinabile"},
"en":{"title":"Code → Architecture & Risk","note":"Local static analysis only: no execution, network, init, plan, apply, destroy or module downloads.","paste":"Paste Terraform","upload":"Upload controlled .tf or ZIP","provider":"Declared provider","env":"Environment","state":"State","analyze":"Run static analysis","architecture":"Visual architecture","findings":"Granular findings","resource":"Resource detail","simulate":"Simulate selected remediation","download":"Download proposed copy ZIP","finops":"Cross-cutting demo FinOps","legend":"Legend: 🟢 compliant · 🟡 low · 🟠 medium · 🔴 high/critical · 🟣 external dependency · ⚪ undetermined"}}


def render_code_architecture(language: str="it") -> None:
    t=T[language]; st.header(t["title"]); st.warning(t["note"]); st.caption(t["legend"])
    a,b,c=st.columns(3); provider=a.selectbox(t["provider"],["Auto","AWS","Azure","GCP"]); environment=b.selectbox(t["env"],["development","staging","production"]); state_kind=c.radio(t["state"],["current","desired"],horizontal=True)
    code=st.text_area(t["paste"],SAMPLE,height=300,key=f"v3_code_{language}")
    uploaded=st.file_uploader(t["upload"],type=["tf","zip"],key=f"v3_upload_{language}")
    budget=st.number_input("Budget demo mensile" if language=="it" else "Demo monthly budget",min_value=0.0,value=250.0)
    if st.button(t["analyze"],type="primary",key=f"v3_analyze_{language}"):
        gateway=InputSecurityGateway()
        try:
            if uploaded:
                payload=uploaded.getvalue(); secured=gateway.secure_zip(payload) if uploaded.name.lower().endswith(".zip") else gateway.secure_text(payload.decode("utf-8"),uploaded.name)
            else: secured=gateway.secure_text(code)
            st.session_state.v3_bundle=analyze_terraform(secured.files,provider,environment,state_kind,budget)
            st.session_state.v3_original="\n".join(secured.files.values())
            if secured.redacted_events:st.warning("Secret rilevato e redatto; non è stato conservato." if language=="it" else "Secret detected and redacted; it was not retained.")
        except (InputSecurityError,UnicodeDecodeError) as exc: st.error(("Input bloccato: " if language=="it" else "Input blocked: ")+str(exc))
    bundle=st.session_state.get("v3_bundle")
    if not bundle: st.info("Carica o incolla Terraform per iniziare." if language=="it" else "Upload or paste Terraform to begin."); return
    m1,m2,m3,m4=st.columns(4); m1.metric("Resources",len(bundle.resources)); m2.metric("Findings",len(bundle.findings)); m3.metric("Maturity",f"{bundle.maturity}/100"); m4.metric("Mode","Static / Demo")
    st.subheader(t["architecture"])
    graph=[]
    severity={f.resource_id:f.severity for f in bundle.findings}
    colors={"Critical":"#ef4444","High":"#f97316","Medium":"#eab308","Low":"#eab308"}
    for index,r in enumerate(bundle.resources): graph.append({"resource":r.resource_id,"provider":r.provider,"category":r.category,"x":index,"y":len(r.dependencies),"color":colors.get(severity.get(r.resource_id),"#22c55e"),"blast":r.blast_radius,"cost":r.monthly_cost_demo})
    st.vega_lite_chart({"values":graph},{"mark":{"type":"circle","size":900},"encoding":{"x":{"field":"x","type":"quantitative","axis":None},"y":{"field":"y","type":"quantitative","title":"Dependencies"},"color":{"field":"color","type":"nominal","scale":None},"tooltip":[{"field":"resource"},{"field":"provider"},{"field":"category"},{"field":"blast"},{"field":"cost"}]}},width="stretch")
    st.dataframe([{"Source":r.resource_id,"Dependencies":", ".join(r.dependencies) or "—","Flows":", ".join(r.flows) or "—","IAM/Trust":", ".join(r.iam_trust) or "—","Blast radius":r.blast_radius} for r in bundle.resources],hide_index=True,width="stretch")
    selected_resource=st.selectbox(t["resource"],[r.resource_id for r in bundle.resources]); resource=next(r for r in bundle.resources if r.resource_id==selected_resource)
    st.code(resource.code,language="hcl"); st.write({"dependencies":resource.dependencies,"risk":severity.get(resource.resource_id,"Compliant/undetermined"),"demo_monthly_cost":resource.monthly_cost_demo,"confidence":resource.confidence})
    st.subheader(t["findings"])
    rows=[{"Select":False,"ID":f.finding_id,"Provider":f.provider,"File / Resource":f"{f.file} · {f.resource_id}","Category":f.category,"Severity":f.severity,"Likelihood":f.likelihood,"Impact":f.impact,"Confidence":f.confidence,"Evidence":f.evidence,"Rule":f.rule,"Dependencies":", ".join(f.dependencies),"Remediation":f.remediation,"Terraform":f.terraform_mapping,"Test":f.test,"Residual risk":f.residual_risk} for f in bundle.findings]
    edited=st.data_editor(rows,hide_index=True,width="stretch",disabled=[key for key in rows[0] if key!="Select"] if rows else [],key=f"v3_findings_{language}") if rows else []
    explicit=st.multiselect("Finding da simulare" if language=="it" else "Findings to simulate",[f.finding_id for f in bundle.findings],key=f"v3_selected_{language}")
    selected=tuple(dict.fromkeys([row["ID"] for row in edited if row["Select"]]+explicit))
    requested=st.button(t["simulate"],disabled=not selected,key=f"v3_sim_{language}")
    if selected and (requested or st.session_state.get("v3_sim_selection")!=selected):
        st.session_state.v3_sim=simulate_remediation(st.session_state.v3_original,bundle.findings,selected)
        st.session_state.v3_sim_selection=selected
    simulation=st.session_state.get("v3_sim") if selected else None
    if simulation:
        x,y=st.columns(2); x.metric("Risk before",simulation.risk_before); y.metric("Risk after",simulation.risk_after,simulation.risk_after-simulation.risk_before)
        st.code(simulation.diff,language="diff"); st.write("**Residual:**",simulation.residual); st.write("**Regressions:**",simulation.regressions); st.write("**Tests:**",simulation.tests); st.write("**Rollback:**",simulation.rollback)
        output=BytesIO()
        with ZipFile(output,"w",ZIP_DEFLATED) as archive:
            archive.writestr("proposed/main.tf",simulation.proposed_code); archive.writestr("REVIEW_REQUIRED.txt","Human review required. No plan or apply was executed.\n")
        st.download_button(t["download"],output.getvalue(),"terraform-proposed-review.zip","application/zip")
    st.subheader(t["finops"]); _render_finops(bundle)


def _render_finops(bundle):
    def money(value): return "Non stimabile" if value is None else f"€ {value:,.2f} demo"
    rows=[]
    for item in bundle.finops:
        rows.append({"Resource":item.resource_id,"Current/month":money(item.current_monthly),"Projected/month":money(item.projected_monthly),"Annual":money(item.projected_annual),"One-time":money(item.one_time),"Direct":money(item.direct),"Indirect":money(item.indirect),"Prudent":money(item.prudent),"Likely":money(item.likely),"Maximum":money(item.maximum),"Budget":money(item.budget),"Overrun":money(item.overrun),"Confidence":item.confidence,"Assumptions":"; ".join(item.assumptions),"Alternatives":"; ".join(item.cheaper_alternatives)})
    st.dataframe(rows,hide_index=True,width="stretch")
    cascade=[{"step":name,"order":i,"impact":i+1} for i,name in enumerate(("logging","ingestion","storage","retention","query","encryption","data transfer"))]
    st.vega_lite_chart({"values":cascade},{"mark":{"type":"line","point":True},"encoding":{"x":{"field":"order","type":"ordinal","axis":{"labels":False},"title":"Cascade"},"y":{"field":"impact","type":"quantitative","title":"Synthetic impact"},"color":{"value":"#8b5cf6"},"tooltip":[{"field":"step"},{"field":"impact"}]}},width="stretch")
