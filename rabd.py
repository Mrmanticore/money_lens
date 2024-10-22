from inference_sdk import InferenceHTTPClient

client = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="TCCK6CI1iPvBwCoJmIjO"
)

result = client.run_workflow(
    workspace_name="projectshub-f6lna",
    workflow_id="custom-workflow-9xu",
    images={
        "image": "new.png"
    }
)