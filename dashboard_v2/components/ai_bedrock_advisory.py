"""Visible V3 AI & Bedrock advisory; deterministic and network-free by default."""

from __future__ import annotations
import streamlit as st
from v2.modules.ai_bedrock_advisory import ALLOWED_MODELS, build_demo_advisory


def render_ai_bedrock_advisory(language: str="it") -> None:
    it=language=="it"
    st.header("AI & Bedrock Advisory")
    st.warning("DEMO · Bedrock reale disabilitato. Nessuna chiamata AWS, cloud, Terraform o repository." if it else "DEMO · Real Bedrock is disabled. No AWS, cloud, Terraform or repository calls.")
    status=st.selectbox("Stato Bedrock" if it else "Bedrock status",["Disabilitato","Demo","Configurato"],index=1)
    model=st.selectbox("Modello allowlist" if it else "Allowlisted model",list(ALLOWED_MODELS))
    budget=st.number_input("Budget analisi" if it else "Analysis budget",min_value=0.0,value=1.0,step=.1)
    output_tokens=st.slider("Limite token output" if it else "Output token limit",100,2000,800,100)
    consent=st.checkbox("Consenso esplicito per una futura chiamata reale" if it else "Explicit consent for a future real call",value=False)
    st.caption("Configurato richiederebbe ruolo temporaneo least-privilege, redazione, timeout e limiti costo/token; l'invocazione reale non è implementata nella V3." if it else "Configured mode would require a temporary least-privilege role, redaction, timeout and cost/token limits; real invocation is not implemented in V3.")
    if status=="Configurato":
        st.error("Fail-closed: Bedrock reale resta disabilitato anche con consenso." if it else "Fail-closed: real Bedrock remains disabled even with consent.")
    bundle=st.session_state.get("v3_bundle")
    summary=f"provider={getattr(bundle,'provider','demo-multicloud')}; resources={len(getattr(bundle,'resources',()))}; findings={len(getattr(bundle,'findings',()))}; mode=read-only-redacted"
    estimate=build_demo_advisory(summary,model,budget,output_tokens)
    a,b,c,d=st.columns(4); a.metric("Input token",estimate.input_tokens); b.metric("Output token",estimate.output_tokens); c.metric("Costo demo" if it else "Demo cost",f"€ {estimate.estimated_cost:.6f}"); d.metric("Budget residuo" if it else "Remaining budget",f"€ {estimate.remaining_budget:.6f}")
    if status=="Disabilitato": st.info("Storytelling disponibile solo come esempio deterministico locale." if it else "Storytelling is available only as a deterministic local example.")
    st.subheader("Storytelling / Narrative"); st.write(estimate.narrative)
    c1,c2=st.columns(2)
    with c1:
        st.markdown("**Rischi / Risks**"); [st.write(f"• {item}") for item in estimate.risks]
        st.markdown("**Dipendenze / Dependencies**"); [st.write(f"• {item}") for item in estimate.dependencies]
        st.markdown("**Evoluzione storica / Historical evolution**"); st.write(estimate.history)
    with c2:
        st.markdown("**Suggerimenti architetturali / Architecture suggestions**"); [st.write(f"• {item}") for item in estimate.suggestions]
        st.markdown("**Corrente → proposta / Current → proposed**"); [st.write(f"• {item}") for item in estimate.comparison]
    st.markdown("**Collegamenti normalizzati / Normalized links**"); st.write(" · ".join(estimate.links))
    st.caption("Audit locale redatto: "+" · ".join(estimate.audit_events))
