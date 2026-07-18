# AI Architect Advisor (AIA)

## Architecture


![Architecture](docs/architecture.png)

<p align="center">
  <img src="docs/aia-architecture.png" alt="AI Architect Advisor Architecture" width="850">
</p>

<p align="center">
<b>Figure 1.</b> High-level architecture of AI Architect Advisor.
</p>
> An open-source AI-powered Decision Intelligence Platform for AWS Landing Zones.

AI Architect Advisor (AIA) is an intelligent assistant designed to help Cloud Architects understand what is happening inside complex AWS environments.

Instead of simply collecting AWS findings, AIA analyzes cloud telemetry, correlates information from multiple AWS services, explains architectural risks, prioritizes remediation actions, and generates executive-level recommendations using Artificial Intelligence.

The objective is to transform raw cloud data into actionable architectural intelligence.

---

## Vision

Modern AWS Landing Zones generate thousands of events every day.

Cloud Architects often need to analyze information coming from multiple AWS services before making a decision.

This process is time-consuming, repetitive and requires deep knowledge of cloud architecture.

AI Architect Advisor was created to become an intelligent architectural advisor capable of understanding the overall state of an AWS environment, identifying risks, explaining infrastructure behavior and supporting technical decision making.

Rather than replacing Cloud Architects, AIA is designed to augment their capabilities.
---

# Why this project?

Most existing dashboards simply display information.

AI Architect Advisor goes one step further.

Instead of asking engineers to manually interpret dozens of dashboards, AIA explains what is happening, why it matters, what the business impact is and what actions should be taken.

The project demonstrates how Artificial Intelligence can support cloud architecture, governance, operational excellence, security and FinOps.

---

# Current Version (V1)

Version 1 introduces the core Decision Intelligence Engine.

Current capabilities include:

- AWS Organizations analysis
- IAM analysis
- CloudTrail analysis
- GuardDuty analysis
- Security Hub analysis
- Risk Scoring Engine
- Priority Engine
- Recommendation Engine
- Executive Report Generator
- AI Narrative Generation
- Historical Snapshot Engine
- Infrastructure Fingerprinting
- Streamlit Dashboard
- Amazon Bedrock integration

This version demonstrates the overall architecture and the first implementation of the AI decision workflow.

---

# Architecture Overview

The project is composed of multiple independent AI engines.

Each engine performs a specific responsibility inside the decision pipeline.

```text
Collectors
↓
Analyzers
↓
Risk Engine
↓
Priority Engine
↓
Recommendation Engine
↓
Executive Report Engine
↓
Bedrock AI Narrator
↓
Dashboard
```

---

# AWS Services

Current integrations include:

- AWS Organizations
- IAM
- CloudTrail
- GuardDuty
- Security Hub
- Amazon Bedrock

Future versions will include additional AWS services.

---

# Project Structure

```text
dashboard/
docs/
history/
src/
├── analyzers/
├── collectors/
├── config/
├── engines/
├── history/
├── models/
├── services/
├── utils/
README.md
LICENSE
```

---

# Installation

```bash
git clone https://github.com/michele-cloud-cyber/architect-intelligence-advisor.git

cd architect-intelligence-advisor

pip install -r requirements.txt
```

---

# Run

### CLI

```bash
python main.py
```

### Dashboard

```bash
streamlit run dashboard/app.py
```

---

# Current Status

Project under active development.

This repository currently represents Version 1 (MVP).

New AI engines and AWS integrations will be continuously added.

---

# Roadmap

## Version 2

- Forecast Engine improvements
- Drift Detection
- FinOps Advisor
- Explainability Engine
- Better Bedrock prompts

## Version 3

- Natural Language Chat
- Multi-account analysis
- Cost Optimization Advisor
- Compliance Advisor
- Architecture Pattern Recognition

---

# Future Vision

The long-term goal of AI Architect Advisor is to become an intelligent architectural companion capable of understanding the complete health of an AWS Landing Zone, explaining infrastructure behavior, predicting future risks and supporting Cloud Architects during strategic decision making.

---

# License

MIT License

---

# Contributing

Pull Requests are welcome.

Suggestions, ideas and architectural discussions are always appreciated.
