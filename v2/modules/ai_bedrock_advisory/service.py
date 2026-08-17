"""No-network Bedrock boundary; real invocation intentionally absent."""

from __future__ import annotations
from dataclasses import dataclass
import re


ALLOWED_MODELS={
    "anthropic.claude-3-5-sonnet-demo":{"input_per_million":3.0,"output_per_million":15.0},
    "amazon.nova-pro-demo":{"input_per_million":0.8,"output_per_million":3.2},
}
INJECTION=re.compile(r"(?i)(ignore (all|previous) instructions|system prompt|reveal secrets|execute|terraform apply)")


@dataclass(frozen=True)
class AdvisoryEstimate:
    status: str; model: str; input_tokens: int; output_tokens: int; estimated_cost: float
    remaining_budget: float; narrative: str; risks: tuple[str,...]; dependencies: tuple[str,...]
    history: str; suggestions: tuple[str,...]; comparison: tuple[str,...]; links: tuple[str,...]
    audit_events: tuple[str,...]


def build_demo_advisory(normalized_summary: str, model: str, budget: float, output_tokens: int=800) -> AdvisoryEstimate:
    if model not in ALLOWED_MODELS: raise ValueError("Model is not allowlisted")
    if budget<0 or output_tokens<1 or output_tokens>2000: raise ValueError("Budget or token limit rejected")
    if INJECTION.search(normalized_summary): raise ValueError("Prompt-injection pattern blocked")
    redacted=re.sub(r"\b\d{12}\b","[ACCOUNT-REDACTED]",normalized_summary)
    redacted=re.sub(r"(?i)(secret|password|token)\s*[:=]\s*\S+",r"\1=[REDACTED]",redacted)
    input_tokens=max(1,(len(redacted)+3)//4); rates=ALLOWED_MODELS[model]
    cost=round(input_tokens/1_000_000*rates["input_per_million"]+output_tokens/1_000_000*rates["output_per_million"],6)
    return AdvisoryEstimate("Demo",model,input_tokens,output_tokens,cost,round(max(0,budget-cost),6),
        "La landing zone demo evolve da controlli locali frammentati verso un modello tracciabile, governato e multi-cloud.",
        ("Accesso pubblico e wildcard IAM aumentano il blast radius.","Finding CVE/CVSS demo richiedono validazione umana."),
        ("Logging influenza ingestione, retention, cifratura e costo.","Terraform, CVE/CVSS e FinOps sono collegati dal modello normalizzato."),
        "Lo storico demo conserva snapshot immutabili; nessuna evidenza passata viene riscritta.",
        ("Adottare un modello landing zone essenziale e progredire per approvazioni.","Prioritizzare least privilege, cifratura, logging e test IMDSv2."),
        ("Corrente: rischio elevato e input sintetici.","Proposta: rischio residuo esplicito, controlli testabili e costi demo tracciati."),
        ("Code → Architecture & Risk","Vulnerability Intelligence","FinOps","Multi-cloud controls","Landing Zone Intelligence"),
        ("normalized-read-only-model","redaction-applied","no-network","no-bedrock-call"))
