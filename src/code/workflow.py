import streamlit as st
import json
import urllib.request
import urllib.parse
import base64
import websocket
import io
import random
from PIL import Image
from src.code.config import Config

class Workflow:

    def __init__(self):
        # Instance attributes (unique to each instance)
        pass

    # --- Functions from your code ---
    def load_workflow(self, filename=Config.WORKFLOW_FILENAME):
        try:
            with open(filename, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            st.error(f"Error: Workflow file '{filename}' not found.")
            return None
        except json.JSONDecodeError:
            st.error(f"Error: Failed to decode JSON from '{filename}'.")
            return None

    def encode_image_to_base64(self, image_bytes):
        return base64.b64encode(image_bytes).decode('utf-8')

    def update_workflow_with_image(self, workflow, image_bytes):
        if workflow is None:
            return None
        base64_image = self.encode_image_to_base64(image_bytes)
        # The node ID '10' is hardcoded from your example.
        # It might be different in a user's workflow.
        if "14" in workflow and "inputs" in workflow["14"]:
            workflow["14"]["inputs"]["image"] = base64_image
            return workflow
        else:
            st.error("Error: Workflow structure is missing node '20' or 'input'.")
            return None
    
    def update_workflow_with_prompt(self, workflow, prompt):
        if workflow is None:
            return None
        # The node ID '10' is hardcoded from your example.
        # It might be different in a user's workflow.
        if "6" in workflow and "inputs" in workflow["6"]:
            workflow["6"]["inputs"]["text"] = prompt
            return workflow
        else:
            st.error("Error: Workflow structure is missing node '6' or 'inputs'.")
            return None

    def queue_prompt(self, prompt):
        data = json.dumps({"prompt": prompt}).encode('utf-8')
        req = urllib.request.Request(f"http://{Config.SERVER_ADDRESS}/prompt", data=data, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read())
        except urllib.error.HTTPError as e:
            st.error(f"HTTP Error: {e.code}: {e.reason}")
            st.error(f"Response body: {e.read().decode('utf-8')}")
            return None
        except Exception as e:
            st.error(f"An error occurred while queuing the prompt: {e}")
            return None

    def get_image(self, prompt_id):
        try:
            ws = websocket.WebSocket()
            ws.connect(f"ws://{Config.SERVER_ADDRESS}/ws")
            st.info(f"Waiting for image data for prompt ID: {prompt_id}")

            while True:
                message = ws.recv()
                if isinstance(message, str):
                    data = json.loads(message)
                    if data["type"] == "executing" and data["data"]["node"] is None and data["data"]["prompt_id"] == prompt_id:
                        st.success("Execution completed.")
                        break
                elif isinstance(message, bytes):
                    # We expect the first binary message to be the image.
                    ws.close()
                    return Image.open(io.BytesIO(message[8:]))
            ws.close()
            return None
        except Exception as e:
            st.error(f"An error occurred while retrieving the image: {e}")
            return None
            
    def update_workflow_with_rdn_seed(self, workflow):
        if workflow is None:
            return None
        random_seed = random.randint(4294967294, 742213406368043)
        # The node ID '3' is hardcoded from your example.
        if "3" in workflow and "inputs" in workflow["3"]:
            workflow["3"]["inputs"]["seed"] = random_seed
            return workflow
        else:
            st.error("Error: Workflow structure is missing node '3' or 'inputs'.")
            return None