"""Conservative static Terraform parser and deterministic remediation simulator."""

from __future__ import annotations
from difflib import unified_diff
import re
from .finops import estimate_portfolio
from .models import AnalysisBundle, ArchitectureResource, Finding, RemediationSimulation


RESOURCE_RE=re.compile(r'(?ms)resource\s+"([\w-]+)"\s+"([\w-]+)"\s*\{')
REF_RE=re.compile(r'\b((?:aws|azurerm|google)_[\w]+\.[\w]+)\b')


def _block(text: str, start: int) -> tuple[str,int]:
    depth=0
    for i in range(start,len(text)):
        if text[i]=='{': depth+=1
        elif text[i]=='}':
            depth-=1
            if depth==0:return text[start:i+1],i+1
    return text[start:],len(text)


def _provider(resource_type: str, fallback: str) -> str:
    return "AWS" if resource_type.startswith("aws_") else "Azure" if resource_type.startswith("azurerm_") else "GCP" if resource_type.startswith("google_") else fallback


def analyze_terraform(files: dict[str,str], provider: str="Auto", environment: str="development", state_kind: str="current", budget: float|None=250.0) -> AnalysisBundle:
    resources=[]; findings=[]; warnings=[]
    for filename,text in files.items():
        if text.count("{") != text.count("}"): warnings.append(f"Malformed or incomplete block structure: {filename}")
        for match in RESOURCE_RE.finditer(text):
            rtype,name=match.groups(); code,end=_block(text,match.end()-1); rid=f"{rtype}.{name}"; prov=_provider(rtype,provider)
            deps=tuple(sorted(set(ref for ref in REF_RE.findall(code) if ref!=rid)))
            category="Identity" if any(v in rtype for v in ("iam","role","policy")) else "Network" if any(v in rtype for v in ("security_group","network","firewall")) else "Data" if any(v in rtype for v in ("bucket","storage")) else "Compute"
            blast="High" if any(v in code for v in ('0.0.0.0/0','"*"')) else "Medium" if deps else "Low"
            resources.append(ArchitectureResource(rid,prov,filename,rtype,name,category,code,deps,_flows(code),_trust(code),state_kind,"desired",blast,None,65))
            findings.extend(_findings(filename,rid,prov,rtype,code,deps))
    known={r.resource_id for r in resources}
    for resource in resources:
        for dependency in resource.dependencies:
            if dependency not in known:warnings.append(f"External or unresolved dependency: {dependency}")
    finops=estimate_portfolio(tuple(resources),budget)
    cost_map={item.resource_id:item.likely for item in finops}
    resources=[ArchitectureResource(**{**r.__dict__,"monthly_cost_demo":cost_map.get(r.resource_id)}) for r in resources]
    maturity=max(10, min(88, 82-len(findings)*4)) if resources else 0
    return AnalysisBundle(tuple(resources),tuple(findings),finops,maturity,tuple(files),provider,environment,state_kind,tuple(sorted(set(warnings))))


def _flows(code:str)->tuple[str,...]:
    flows=[]
    if re.search(r'(?i)ingress|cidr_blocks|source_ranges',code):flows.append("Network ingress")
    if re.search(r'(?i)logging|log_group|diagnostic',code):flows.append("Log data")
    if re.search(r'(?i)bucket|storage',code):flows.append("Stored data")
    return tuple(flows)


def _trust(code:str)->tuple[str,...]:
    return ("Wildcard principal",) if re.search(r'(?i)(principal|members)\s*=.*\*',code) else ()


def _finding(fid,prov,file,rid,cat,sev,l,i,conf,evidence,rule,dependencies,remediation,mapping,test,residual):
    return Finding(fid,prov,file,rid,cat,sev,l,i,conf,evidence,rule,dependencies,remediation,mapping,test,residual)


def _findings(file,rid,prov,rtype,code,deps):
    out=[]; key=rid.replace('.','-').upper()
    if re.search(r'0\.0\.0\.0/0|::/0',code):out.append(_finding(f"V3-{key}-PUBLIC",prov,file,rid,"Network","Critical",5,5,90,"Public CIDR in resource block","No unrestricted administrative ingress",deps,"Restrict CIDR and ports",f"{rid}.ingress","policy:test_no_public_ingress","Connectivity exceptions require review"))
    if re.search(r'(?i)(password|secret|access_key)\s*=\s*"(?!\[REDACTED\])',code):out.append(_finding(f"V3-{key}-SECRET",prov,file,rid,"Secrets","Critical",4,5,95,"Credential-like literal","No secrets in Terraform",deps,"Use a secret reference outside source",rid,"scan:test_no_secrets","Rotation and history cleanup remain required"))
    if "aws_instance"==rtype or "aws_launch_template"==rtype:
        required=bool(re.search(r'http_tokens\s*=\s*"required"',code)); endpoint_disabled=bool(re.search(r'http_endpoint\s*=\s*"disabled"',code))
        if not required and not endpoint_disabled:out.append(_finding(f"V3-{key}-IMDSV2",prov,file,rid,"Compute Security","High",4,4,85,"http_tokens is not required","Require IMDSv2 when metadata endpoint is enabled",deps,'Set http_tokens = "required"',f"{rid}.metadata_options.http_tokens","terraform:test_imdsv2","Container compatibility must be tested; hop limit 2 may be justified"))
    if any(v in rtype for v in ("bucket","storage_account")) and not re.search(r'(?i)encrypt|server_side_encryption|customer_managed_key',code):out.append(_finding(f"V3-{key}-ENC",prov,file,rid,"Encryption","High",3,5,75,"No encryption property found in static block","Encrypt data at rest",deps,"Add provider-supported encryption",f"{rid}.encryption","policy:test_encryption","Key governance remains required"))
    if not re.search(r'(?i)tags\s*=|labels\s*=|tags\s*\{',code):out.append(_finding(f"V3-{key}-TAGS",prov,file,rid,"Governance","Low",2,2,70,"No tags or labels found","Resources require ownership and environment metadata",deps,"Add owner, environment and cost-center tags",f"{rid}.tags","policy:test_required_tags","Tag accuracy requires ownership review"))
    if re.search(r'(?i)principal\s*=\s*"\*"|actions?\s*=\s*\[?"\*"',code):out.append(_finding(f"V3-{key}-IAM",prov,file,rid,"IAM","Critical",4,5,90,"Wildcard IAM element","Enforce least privilege",deps,"Replace wildcard with explicit principals/actions",rid,"policy:test_least_privilege","Permissions must be validated against workload behavior"))
    return out


def simulate_remediation(code:str, findings:tuple[Finding,...], selected_ids:tuple[str,...])->RemediationSimulation:
    selected=[f for f in findings if f.finding_id in selected_ids]; proposed=code
    for f in selected:
        if f.finding_id.endswith("-IMDSV2") and 'http_tokens = "required"' not in proposed: proposed=re.sub(r'(metadata_options\s*\{)',r'\1\n    http_tokens = "required"',proposed,count=1) if "metadata_options" in proposed else proposed
        elif f.finding_id.endswith("-PUBLIC"): proposed=proposed.replace('0.0.0.0/0','10.0.0.0/8').replace('::/0','fd00::/8')
        elif f.finding_id.endswith("-TAGS"):
            proposed += '\n# Proposed after human review: add owner, environment and cost-center tags.\n'
        else: proposed += f'\n# Proposed remediation for {f.finding_id}: {f.remediation}\n'
    diff=''.join(unified_diff(code.splitlines(True),proposed.splitlines(True),fromfile='original/main.tf',tofile='proposed/main.tf'))
    before=sum(f.likelihood*f.impact for f in findings); after=max(0,before-sum(f.likelihood*f.impact for f in selected)//2)
    return RemediationSimulation(code,proposed,diff,tuple(selected_ids),before,after,None,None,tuple(f.finding_id for f in selected),tuple(f.residual_risk for f in selected),(),("Application compatibility and policy regressions require testing",) if selected else (),tuple(f.test for f in selected),"Restore the reviewed original code; no change was applied automatically")
