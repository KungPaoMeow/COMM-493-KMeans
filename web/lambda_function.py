import json
import boto3
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# ************************************************************
# INSTRUCTION: Update the endpoint name below to match your SageMaker endpoint.
# If you are switching to another service or endpoint type, adjust this variable accordingly.
# ************************************************************
ENDPOINT_NAME = "credit-kmeans-one-a-HPT"  # Replace with your actual SageMaker endpoint name

def lambda_handler(event, context):
    logger.info("Received event: %s", event)

    # ************************************************************
    # INSTRUCTION: This block handles different input formats.
    # If your API passes inputs differently (for example, not via "body"), modify this section.
    # ************************************************************
    try:
        # If this is called through API Gateway, event has a "body" field
        if "body" in event:
            body = event["body"]
            # If the body is a string, parse it into JSON.
            if isinstance(body, str):
                body = json.loads(body)
        else:
            body = event

        # Expecting a JSON object with "instances" key which is a list of text strings
        instances = body.get("instances")

    except Exception as e:
        logger.error("Failed to parse input or extract instances: %s", e)
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid input format."})
        }

    # ************************************************************
    # INSTRUCTION: Ensure that the expected input (instances) is provided.
    # Modify the condition below if your API input structure changes.
    # ************************************************************
    if not instances:
        error_message = "No instances provided in the event."
        logger.error(error_message)
        return {
            "statusCode": 400,
            "body": json.dumps({"error": error_message})
        }

    # # Prepare the JSON payload
    # payload = {
    #     "instances": instances
    # }
    # ************************************************************
    # INSTRUCTION: The following converts the input instances to CSV format.
    # If your new endpoint does not expect CSV (or expects a different format),
    # update this conversion logic accordingly.
    # ************************************************************
    try:
        csv_payload = "\n".join([",".join(map(str, row)) for row in instances])
    except Exception as e:
        error_message = f"Error converting instances to CSV: {str(e)}"
        logger.error(error_message)
        return {
            "statusCode": 400,
            "body": json.dumps({"error": error_message})
        }
    logger.info("Payload prepared: %s", csv_payload)

    # Call the SageMaker endpoint
    try:
        runtime = boto3.client("sagemaker-runtime")
        response = runtime.invoke_endpoint(
            EndpointName=ENDPOINT_NAME,
            ContentType="application/json",  # INSTRUCTION: Change ContentType if your endpoint expects a different format.
            Body=csv_payload
        )
        logger.info("SageMaker response received")

        # Decode the response from bytes to a JSON object.
        result = json.loads(response["Body"].read().decode("utf-8"))
        logger.info("Decoded response: %s", result)

        # ************************************************************
        # INSTRUCTION: This section assumes the response has a "predictions" key.
        # Modify this part if your API returns a different response structure.
        # ************************************************************
        return {
            "statusCode": 200,
            "body": json.dumps({"predictions": result})
        }

    except Exception as e:
        error_message = f"Exception during SageMaker invocation: {str(e)}"
        logger.error(error_message)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": error_message})
        }
