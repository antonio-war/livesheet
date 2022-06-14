import functions_framework
import base64
import os
import time
from google.cloud import workflows_v1beta
from google.cloud.workflows import executions_v1beta
from google.cloud.workflows.executions_v1beta.types import executions
from google.cloud.workflows.executions_v1beta.types import CreateExecutionRequest, Execution
import json
from flask import send_file


@functions_framework.http
def execute_workflow(request):
    project = 'livesheet-351108'
    location = 'europe-west6'
    workflow = 'transform-workflow'
    request_body = request.json
    arguments = {"bpm": request_body["bpm"], "image": request_body["image"]}

    execution_client = executions_v1beta.ExecutionsClient()
    workflows_client = workflows_v1beta.WorkflowsClient()

    parent = workflows_client.workflow_path(project, location, workflow)
    execution = Execution(argument = json.dumps(arguments))
    response = execution_client.create_execution(parent=parent, execution=execution)
    print(f"Created execution: {response.name}")

    execution_finished = False
    backoff_delay = 1  # Start wait with delay of 1 second
    print('Poll every second for result...')
    while (not execution_finished):
        execution = execution_client.get_execution(request={"name": response.name})
        execution_finished = execution.state != executions.Execution.State.ACTIVE

        # If we haven't seen the result yet, wait a second.
        if not execution_finished:
            print('- Waiting for results...')
            time.sleep(backoff_delay)
            backoff_delay *= 2  # Double the delay to provide exponential backoff.
        else:
            print(f'Execution finished with state: {execution.state.name}')

    response = json.loads(execution.result)
    if "body" in response:
        if "sound" in response["body"]:
            sound_encoded = response["body"]["sound"]
            if sound_encoded[0] == 'b' and sound_encoded[1] == "'" and sound_encoded[-1] == "'":
                sound_encoded = sound_encoded[2:-1]
            decode_string = base64.b64decode(sound_encoded)
            wav_file = open("/tmp/sound.wav", "wb")
            wav_file.write(decode_string)
            if os.path.isfile("/tmp/sound.wav"):
                return send_file("/tmp/sound.wav", mimetype="audio/wav")
    return "", 500