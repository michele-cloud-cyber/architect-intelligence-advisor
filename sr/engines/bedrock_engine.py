import json
import boto3


class BedrockEngine:

    def __init__(self):
        self.client = boto3.client(
            "bedrock-runtime",
            region_name="eu-south-1"
        )
        print("Bedrock Engine initialized.")

    def generate_prompt(self, landing_zone):

        findings = "\n".join(str(f) for f in landing_zone.findings)

        recommendations = "\n".join(
            str(r) if not isinstance(r, dict)
            else f"- {r.get('title', '')}: {r.get('description', '')}"
            for r in landing_zone.recommendations
        )

        prompt = f"""
You are a Senior AWS Solutions Architect.

Analyze the following AWS Landing Zone.

Security Score: {landing_zone.security_score}
Network Score: {landing_zone.network_score}
IAM Score: {landing_zone.identity_score}
Operations Score: {landing_zone.operations_score}

Findings:
{findings}

Recommendations:
{recommendations}

Generate:

1. Executive Summary
2. Critical Risks
3. Priority Actions
4. Final Assessment
"""

        return prompt

    def invoke(self, prompt):

        body = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }

        response = self.client.invoke_model(
            modelId="eu.amazon.nova-2-lite-v1:0",
            body=json.dumps(body)
        )

        result = json.loads(
            response["body"].read()
        )

        return result["output"]["message"]["content"][0]["text"]