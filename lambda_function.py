import json
import math
import os
from datetime import datetime, timezone

import boto3

TABLE_NAME = os.environ.get("DYNAMODB_TABLE", "PowerOfMathDB")
table = boto3.resource("dynamodb").Table(TABLE_NAME)

CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "OPTIONS,POST",
}

def lambda_handler(event, context):
    try:
        # Supports API Gateway proxy events and direct Lambda test events.
        body = event.get("body") if isinstance(event, dict) else None
        if isinstance(body, str):
            payload = json.loads(body)
        elif isinstance(body, dict):
            payload = body
        else:
            payload = event if isinstance(event, dict) else {}

        base = float(payload["base"])
        exponent = int(payload["exponent"])
        result = math.pow(base, exponent)
        timestamp = datetime.now(timezone.utc).isoformat()

        table.put_item(Item={
            "ID": f"{timestamp}#{base}^{exponent}",
            "Base": str(base),
            "Exponent": exponent,
            "Result": result,
            "Timestamp": timestamp,
        })

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps({"base": base, "exponent": exponent, "result": result}),
        }
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        return {
            "statusCode": 400,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": f"Invalid input: {exc}"}),
        }
    except Exception:
        # See CloudWatch Logs for the detailed error.
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": "Server-side error. Check Lambda logs and DynamoDB permissions."}),
        }
