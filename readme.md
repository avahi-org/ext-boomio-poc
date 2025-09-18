🎨 Boomio Game Assets Generator

Boomio Game Assets Generator is a Streamlit-based web application that integrates ComfyUI, AWS Bedrock, S3, and DynamoDB to automatically generate game-ready assets (characters, obstacles, backgrounds).

It supports two workflows:

Prompt-based generation: manually define prompts to generate assets.

Brandbook-based generation: upload a brandbook (PDF), extract consistent style guidelines using AWS Bedrock, and automatically generate asset prompts.

🏗️ System Architecture

![Alt text](src/boomio_POC_architecture_diagram.png?raw=true "System Architecture")

✨ Key Features

Generate Assets for Games

Characters (sprites, poses)

Obstacles (2D side-scroller friendly)

Backgrounds (endless scrolling environments, auto-splitting into tiles)

Flexible Workflows

🎨 Prompt-based generation (ComfyUI only).

✨ Brandbook-based generation (Bedrock → ComfyUI).

Cloud Integration

Upload generated assets to Amazon S3.

Save prompts + metadata into DynamoDB.

UI Features

Multi-page Streamlit application.

Boomio-branded interface.

Image previews + download options.

Automatic tiling of backgrounds for endless runners.

🚀 Getting Started
1. Clone the repository
git clone https://github.com/avahi-org/ext-boomio-poc.git
cd boomio-game-assets-generator

2. Install dependencies

Requires Python 3.9+. Install required libraries:

pip install -r requirements.txt


Example requirements.txt:

streamlit>=1.32.0
boto3>=1.34.0
pillow>=10.0.0
websocket-client>=1.6.0

3. Configure AWS & ComfyUI

ComfyUI server
Set your server address in src/code/config.py (without http:// or ws://):

SERVER_ADDRESS = "localhost:8188"


AWS S3 bucket
Create an S3 bucket (default: avahi-boomio) with prefix avahi-boomio-genai-img/.

AWS DynamoDB
Create a table (default: avahi-boomio-img-prompt-registry) with a string primary key.

AWS Bedrock access
Ensure your IAM role has bedrock:InvokeModel permissions for model:
eu.anthropic.claude-sonnet-4-20250514-v1:0.

4. Run the app
streamlit run app.py


Open http://localhost:8501
 in your browser.

📂 Project Structure
### Project Structure

| File/Folder                  | Description                                                              |
| ---------------------------- | ------------------------------------------------------------------------ |
| `app.py`                     | The main Streamlit entry point for the application.                      |
| `pages/`                     | Contains the different pages of the Streamlit application.               |
| &nbsp;&nbsp;`1_🎨Assest generator (ComfyUI only).py`| Enables manual asset generation based on user prompts. |
| &nbsp;&nbsp;`2_✨Brandbook asset generator.py`   | A specialized tool for generating assets from a brandbook, leveraging Bedrock and ComfyUI. |
| `src/`                       | Stores source code and assets.                                           |
| &nbsp;&nbsp;`boomio_logo.svg`| The logo file used for UI branding.                                      |
| &nbsp;&nbsp;`code/`          | Contains core Python modules.                                            |
| &nbsp;&nbsp;&nbsp;&nbsp;`workflow.py`| Provides workflow utilities for ComfyUI.                               |
| &nbsp;&nbsp;&nbsp;&nbsp;`config.py`| Defines configuration constants, like server and workflow paths.         |
| &nbsp;&nbsp;&nbsp;&nbsp;`dynamo_adapter.py`| Manages metadata storage by connecting to DynamoDB.                      |
| `requirements.txt`           | Lists all the necessary Python dependencies for the project.             |
| `README.md`                  | This file, providing an overview of the project.                         |


🖥️ Streamlit Pages Overview
🔹 Main App (app.py)

Loads logo & title.

Sidebar for selecting generation mode.

Introduces available workflows.

🔹 1. Asset Generator (ComfyUI only)

Located at: pages/1_🎨Assest generator (ComfyUI only).py

Input prompts manually:

Character: Full-body sprites.

Obstacle: Vertical pipes, trees, or styled obstacles.

Background: Large scenic pixel-art backgrounds.

Features:

Randomized seeds for diversity.

Saves generated images to S3.

Saves prompts to DynamoDB.

Background splitting: auto-splits into tiles (1×4) for endless runners.

Shifting preview simulates side-scrolling effect.

🔹 2. Brandbook Asset Generator (Bedrock + ComfyUI)

Located at: pages/2_✨Brandbook asset generator.py

Upload a brandbook PDF.

Uses AWS Bedrock (Claude Sonnet) to extract consistent JSON prompts:

{
  "Character prompt": "...",
  "Obstacles prompt": "...",
  "Background prompt": "..."
}



Prompts are auto-inserted into ComfyUI workflows.

Assets are generated with brand-consistent styling.

⚙️ Core Modules
🔹 workflow.py

Handles communication with ComfyUI API.

load_workflow(file) → Load JSON workflow.

update_workflow_with_prompt(workflow, prompt, node_number) → Injects text.

update_workflow_with_image(workflow, image_bytes, node_number) → Injects base64 image.

update_workflow_with_rdn_seed(workflow, node_number) → Adds randomized seed.

queue_prompt(workflow) → Sends workflow to ComfyUI API.

get_image(prompt_id) → Retrieves image via WebSocket stream.

👉 This is the backbone connecting Streamlit UI to ComfyUI.

🔹 dynamo_adapter.py

Handles saving image metadata + prompts into DynamoDB.

Connects to AWS DynamoDB using boto3.

Saves records in table avahi-boomio-img-prompt-registry.

Ensures each asset has both S3 path + prompt context stored.

👉 Provides traceability between prompt → generated image → storage location.

🔹 config.py

Central configuration:

ComfyUI server address.

Workflow JSON paths:

WORKFLOW_CHARACTER

WORKFLOW_OBSTACLE

WORKFLOW_BACKGROUND

🖥️ Usage Flow

Launch app → choose Prompt or Brandbook mode.

Enter/upload input (prompt text or PDF).

Select asset type (character, obstacle, background).

App → sends workflow to ComfyUI.

ComfyUI generates image → returned to Streamlit.

Image saved to S3, metadata saved in DynamoDB.

User previews or downloads result.

🔧 Customization

Replace logo at: src/boomio_logo.svg.

Modify ComfyUI workflows → adjust config.py paths.

Change AWS resources:

Update S3 bucket name.

Update DynamoDB table.

Update Bedrock model ID.