"""Central provider-neutral registry for navigation, search and module health."""

from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class ModuleDefinition:
    module_id: str; name_it: str; name_en: str; description_it: str; description_en: str
    destination: str; area: str; keywords: tuple[str, ...]; badge: str
    probe_module: str; probe_attribute: str; optional: bool = False

    def name(self, language: str) -> str: return self.name_it if language=="it" else self.name_en
    def description(self, language: str) -> str: return self.description_it if language=="it" else self.description_en


MODULE_REGISTRY=(
    ModuleDefinition("overview","Panoramica","Overview","Inventario e maturità multi-cloud","Multi-cloud inventory and maturity","Panoramica","overview",("aws","azure","gcp","inventario","inventory","maturità","maturity"),"Demo","dashboard_v2.components.multicloud_foundation","render_multicloud_overview"),
    ModuleDefinition("stable_lab","Design e simulazione","Design & simulation","Project Designer, controlli e simulazione","Project Designer, controls and simulation","Design e simulazione","design",("progetto","project","simulazione","simulation","sicurezza","security","controlli","controls","network","rete"),"Simulation","dashboard_v2.components.platform_lab","render_platform_lab"),
    ModuleDefinition("code_architecture","Code → Architecture & Risk","Code → Architecture & Risk","Parsing statico, grafo, rischi e remediation","Static parsing, graph, risks and remediation","Code & Test Lab","code",("terraform","codice","code","grafico","graph","architettura","architecture","metadata","ec2","imds","imdsv2"),"Demo","dashboard_v2.components.code_architecture","render_code_architecture"),
    ModuleDefinition("vulnerability","Vulnerability Intelligence","Vulnerability Intelligence","CVE, CVSS ed evidenze sintetiche","Synthetic CVE, CVSS and evidence","Code & Test Lab","code",("cve","cvss","vulnerabilità","vulnerability","finding","security findings"),"Demo","dashboard_v2.components.security_findings","render_vulnerability_intelligence"),
    ModuleDefinition("ai_bedrock","AI & Bedrock Advisory","AI & Bedrock Advisory","Storytelling consultivo su modello redatto read-only","Advisory storytelling over a redacted read-only model","Code & Test Lab","code",("bedrock","ai","llm","storytelling","token","narrativa","narrative"),"Demo","dashboard_v2.components.ai_bedrock_advisory","render_ai_bedrock_advisory"),
    ModuleDefinition("history","Landing Zone Intelligence","Landing Zone Intelligence","Storico, drift ed evoluzione","History, drift and evolution","Code & Test Lab","code",("storico","history","drift","evoluzione","evolution","intelligence"),"Demo","dashboard_v2.components.multicloud_foundation","render_scenario_history"),
    ModuleDefinition("finops","FinOps","FinOps","Costi, budget e impatti a cascata","Costs, budgets and cascading impacts","Trasversale","cross",("costi","cost","budget","token","finops","spesa","spend"),"Demo","v2.modules.finops_dashboard","render_finops"),
    ModuleDefinition("governance","Governance","Governance","Policy, audit, orchestratore e fallback","Policy, audit, orchestrator and fallback","Governance","governance",("governance","policy","scp","iam","accessi","audit","compliance","orchestratore","orchestrator","fallback"),"Read-only","dashboard_v2.components.multicloud_foundation","render_governance_plane"),
)


def search_modules(query: str, language: str="it") -> tuple[ModuleDefinition,...]:
    needle=query.strip().casefold()
    if not needle:return ()
    ranked=[]
    for module in MODULE_REGISTRY:
        haystack=" ".join((module.name_it,module.name_en,module.description_it,module.description_en,module.destination,*module.keywords)).casefold()
        if needle in haystack:
            score=3 if needle in module.name(language).casefold() else 2 if any(needle in word.casefold() for word in module.keywords) else 1
            ranked.append((score,module))
    return tuple(module for _,module in sorted(ranked,key=lambda item:(-item[0],item[1].name(language))))


def get_module(module_id: str) -> ModuleDefinition|None:
    return next((item for item in MODULE_REGISTRY if item.module_id==module_id),None)
