"""Advisory-only change explanations for landing-zone evolution."""

from __future__ import annotations
from .models import AnalysisBundle


def detect_changes(previous: AnalysisBundle, current: AnalysisBundle) -> tuple[dict,...]:
    old={f.finding_id:f for f in previous.findings}; new={f.finding_id:f for f in current.findings}; events=[]
    for fid,finding in new.items():
        if fid not in old:
            events.append({"change":"New risk","evidence":finding.evidence,"impact":finding.severity,"resources":finding.resource_id,"remediation":finding.remediation,"confidence":finding.confidence})
    if sum(v.likely or 0 for v in current.finops)>sum(v.likely or 0 for v in previous.finops):events.append({"change":"Demo cost growth","evidence":"Synthetic likely estimate increased","impact":"Review budget","resources":"portfolio","remediation":"Review usage and cheaper alternatives","confidence":40})
    return tuple(events)
