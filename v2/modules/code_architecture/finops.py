"""Transparent synthetic FinOps adapters; estimates are ranges, never prices."""

from __future__ import annotations
from .models import ArchitectureResource, FinOpsEstimate


DEMO_BASE = {
    "aws_instance": 42.0, "aws_s3_bucket": 8.0, "aws_cloudwatch_log_group": 6.0,
    "azurerm_linux_virtual_machine": 46.0, "azurerm_storage_account": 9.0,
    "google_compute_instance": 40.0, "google_storage_bucket": 8.0,
}


def estimate_portfolio(resources: tuple[ArchitectureResource, ...], budget: float | None = 250.0) -> tuple[FinOpsEstimate, ...]:
    estimates=[]
    for resource in resources:
        base=DEMO_BASE.get(resource.resource_type)
        if base is None:
            estimates.append(FinOpsEstimate(resource.resource_id,None,None,None,None,None,None,None,None,None,budget,None,None,None,("Non stimabile senza dati provider e utilizzo",),20,("Synthetic data only",)))
            continue
        operational=12.0 if "instance" in resource.resource_type or "virtual_machine" in resource.resource_type else 3.0
        likely=round(base*1.15,2); maximum=round(base*1.65,2); prudent=round(base*.9,2)
        new_total=likely; overrun=max(0.0,new_total-(budget or new_total)) if budget is not None else None
        alternatives=("Ridurre retention e frequenza query",) if "log" in resource.resource_type else ("Rightsizing e scheduling non-production",)
        estimates.append(FinOpsEstimate(resource.resource_id,base,likely,round(likely*12,2),operational,base,operational,prudent,likely,maximum,budget,new_total,overrun,overrun,alternatives,45,("Prezzo demo sintetico", "Esclusi sconti, tasse e data transfer")))
    return tuple(estimates)
