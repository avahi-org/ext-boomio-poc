import streamlit as st
import os
import io
import boto3
import re
from PIL import Image
from src.code.workflow import Workflow
from src.code.config import Config
# --- Configuration ---
# You need to replace this with your ComfyUI server address
# The address should not include http:// or ws://

# --- App Configuration and Title ---
st.set_page_config(
    page_title="Boomio game assets generator",
    page_icon="🎨",
    layout="wide"
)
spc_1, spc_2, spc_3 = st.columns([2, 2, 2]) # Adjust ratios for desired spacing
with spc_2:
    st.image("src/boomio_logo.svg", width=800)

st.title("🎨 Boomio game assets generator")
st.sidebar.header("Assest generator (ComfyUI only)")
st.markdown("##### This platform allows you to: \n" \
"- Generate individual game assets (characters, obstacles, backgrounds) based on prompts and pre-processing.")
st.markdown("##### Guidelines:")
st.markdown("1. Write a prompt with the specifications for the game asset you want to generate.")
st.markdown("2. Click the **Generate Image** button to create the asset.")
st.markdown("3. Repeat the process for each game asset, or create new ones by following the same steps.")

col1, col2 = st.columns([1, 1])
col3, col4 = st.columns([1, 1])
col5, col6 = st.columns([1, 1])
col_bkg_1, col_bkg_2, col_bkg_3, col_bkg_4, col_bkg_5= st.columns([2, 2, 2, 2, 2])
col_bkg_shift_1, col_bkg_shift_2, col_bkg_shift_3, col_bkg_shift_4, col_bkg_shift_5= st.columns([2, 2, 2, 2, 2])

if 'generated_image_character' not in st.session_state:
    st.session_state.generated_image_character = []

if 'generated_image_obstacle' not in st.session_state:
    st.session_state.generated_image_obstacle = []

if 'generated_image_background' not in st.session_state:
    st.session_state.generated_image_background = []

if 'bkg_img_1' not in st.session_state:
    st.session_state.bkg_img_1 = []
if 'bkg_img_2' not in st.session_state:
    st.session_state.bkg_img_2 = []
if 'bkg_img_3' not in st.session_state:
    st.session_state.bkg_img_3 = []
if 'bkg_img_4' not in st.session_state:
    st.session_state.bkg_img_4 = []



def save_img_s3_buffer(prefix, buffer):
    # Initialize S3 client
    s3 = boto3.client("s3",)
    # Regex to extract sequence numbers (e.g. image_001.png → 1)
    pattern = re.compile(rf"{prefix}_(\d+)\.\w+$")
    # 1. Get existing objects in the bucket
    existing_objects = s3.list_objects_v2(Bucket="avahi-boomio", Prefix=f"avahi-boomio-genai-img/{prefix}")
    last_number = 0
    if "Contents" in existing_objects:
        for obj in existing_objects["Contents"]:
            match = pattern.search(obj["Key"])
            if match:
                num = int(match.group(1))
                last_number = max(last_number, num)
    s3_key = f"avahi-boomio-genai-img/{prefix}/{prefix}_{last_number}.png"  # e.g. image_004.png

    print(f"Uploading {s3_key} -> s3://avahi-boomio/avahi-boomio-genai-img/{prefix}/{s3_key}")
    # Upload the BytesIO object to S3
    s3.upload_fileobj(
        buffer,
        "avahi-boomio",
        s3_key
    )


def save_img_s3_file(prefix, path):
    # Initialize S3 client
    s3 = boto3.client("s3",)
    # Regex to extract sequence numbers (e.g. image_001.png → 1)
    pattern = re.compile(rf"{prefix}_(\d+)\.\w+$")
    # 1. Get existing objects in the bucket
    existing_objects = s3.list_objects_v2(Bucket="avahi-boomio", Prefix=f"avahi-boomio-genai-img/{prefix}")
    last_number = 0
    if "Contents" in existing_objects:
        for obj in existing_objects["Contents"]:
            match = pattern.search(obj["Key"])
            if match:
                num = int(match.group(1))
                last_number = max(last_number, num)
    s3_key = f"avahi-boomio-genai-img/{prefix}/{prefix}_{last_number}.png"  # e.g. image_004.png

    print(f"Uploading {s3_key} -> s3://avahi-boomio/avahi-boomio-genai-img/{prefix}/{s3_key}")
    # Upload the BytesIO object to S3
    s3.upload_file(
        path,
        "avahi-boomio",
        s3_key
    )


def split_image_into_tiles(image_path, output_dir, rows, cols):
    img = Image.open(image_path)
    img_width, img_height = img.size
    tile_width = img_width // cols
    tile_height = img_height // rows

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for r in range(rows):
        for c in range(cols):
            left = c * tile_width
            upper = r * tile_height
            right = left + tile_width
            lower = upper + tile_height

            # Crop the tile
            tile = img.crop((left, upper, right, lower))

            # Save the tile
            tile_name = f"tile_r{r}_c{c}.jpg"
            tile.save(os.path.join(output_dir, tile_name))


with st.container():
    # --- User Input Section (on the left) ---
    with col1:
        # --- Main Columns for Layout ---
        st.header("1. Input prompt character")
        # A text area for the user to enter the image generation prompt.
        prompt_character = st.text_area(
            "Enter your prompt for image generation here:",
            height=150,
            value="Pixel art a detailed, full-body, character of a cute and cheerful brown cat name Katty. Katty is wearing a vibrant blue retro witch dress and hat. Cute and smiling face. The art style is crisp and clean, with a simple color palette that highlights the character's features. Add running cycle pose on mid air.",
            placeholder="Pixel art a detailed, full-body, character of a cute and cheerful brown sloth name sloth. The sloth is wearing a vibrant blue superhero cape and a white headband with red and blue stripes. The art style is crisp and clean, with a simple color palette that highlights the character's features. Add flapping cycle pose on mid air. "
            , key="area 1"
        )


    # --- Generated Image Output Section (on the right) ---
    with col2:
        st.header("2. Character generated image")
        # --- Button to Trigger Generation ---
        # This is a placeholder for where you would add your generation logic.
        with st.spinner("Generating..."):
            st.success("Image generation process would start now!")
        if st.button("Generate Image", key="button 1"):
                # Load the workflow
                wrk = Workflow()
                workflow = wrk.load_workflow(Config.WORKFLOW_CHARACTER)
                
                if workflow:
                    with st.spinner("Processing..."):
                        # Update the workflow with a random seed
                        workflow = wrk.update_workflow_with_rdn_seed(workflow, "7")

                        # Update the workflow with a new prompt
                        workflow = wrk.update_workflow_with_prompt(workflow, prompt_character, "5")

                        if workflow:
                            # Queue the prompt
                            response = wrk.queue_prompt(workflow)

                            if response:
                                prompt_id = response.get('prompt_id')
                                if prompt_id:
                                    st.info("Prompt queued. Waiting for image generation...")
                                    
                                    # Get the generated image
                                    generated_image = wrk.get_image(prompt_id)
                                    buffer = io.BytesIO()
                                    generated_image.save(buffer, format='PNG') # Save the image to the buffer
                                    buffer.seek(0) 
                                    save_img_s3_buffer("character", buffer)
                                    st.session_state.generated_image_character=generated_image
                                else:
                                    st.error("Failed to get prompt ID from the server response.")
                        else:
                            st.error("Failed to update the workflow. Please check your workflow file.")
        #st.subheader("Character Generated Images:")
        if st.session_state.generated_image_character:
            st.image(st.session_state.generated_image_character, caption="Generated character")

with st.container():
    # --- User Input Section (on the left) ---
    with col3:
        # --- Main Columns for Layout ---
        st.header("3. Input prompt obstacles")
        # A text area for the user to enter the image generation prompt.
        prompt_obstacles = st.text_area(
            "Enter your prompt for image generation here:",
            height=150,
            value="A single pixel art jungle tree obstacle for a side-scrolling endless runner, isolated sprite, tall and narrow. transparent background",
            placeholder="A single pixel art jungle tree obstacle for a side-scrolling endless runner, isolated sprite, tall and narrow. transparent background"
            , key="area 2"
        )


    # --- Generated Image Output Section (on the right) ---
    with col4:
        st.header("4. Obstacles generated image ")
        # --- Button to Trigger Generation ---
        # This is a placeholder for where you would add your generation logic.
        with st.spinner("Generating..."):
            st.success("Image generation process would start now!")
        if st.button("Generate Image", key="button 2"):
                # Load the workflow
                wrk = Workflow()
                workflow_obstacle = wrk.load_workflow(Config.WORKFLOW_OBSTACLE)
                
                if workflow_obstacle:
                    with st.spinner("Processing..."):
                        # Update the workflow with a random seed
                        workflow_obstacle = wrk.update_workflow_with_rdn_seed(workflow_obstacle, "2")

                        # Update the workflow with a new prompt
                        workflow_obstacle = wrk.update_workflow_with_prompt(workflow_obstacle, prompt_obstacles, "3")

                        if workflow_obstacle:
                            # Queue the prompt
                            obstacle_response = wrk.queue_prompt(workflow_obstacle)

                            if obstacle_response:
                                prompt_id_obstacles = obstacle_response.get('prompt_id')
                                if prompt_id_obstacles:
                                    st.info("Prompt queued. Waiting for image generation...")
                                    
                                    # Get the generated image
                                    generated_image_obstacles = wrk.get_image(prompt_id_obstacles)
                                    buffer = io.BytesIO()
                                    generated_image_obstacles.save(buffer, format='PNG') # Save the image to the buffer
                                    buffer.seek(0) 
                                    save_img_s3_buffer("obstacle", buffer)
                                    st.session_state.generated_image_obstacle=generated_image_obstacles
                                else:
                                    st.error("Failed to get prompt ID from the server response.")
                        else:
                            st.error("Failed to update the workflow. Please check your workflow file.")
        if st.session_state.generated_image_obstacle:
            st.image(st.session_state.generated_image_obstacle, caption="Generated obstacle")

with st.container():
    # --- User Input Section (on the left) ---
    with col3:
        # --- Main Columns for Layout ---
        st.header("5. Input prompt background")
        # A text area for the user to enter the image generation prompt.
        prompt_background = st.text_area(
            "Enter your prompt for image generation here:",
            height=150,
            value="A 2D rendered game scene, 16-bit retro pixel art, retro video game, flappy bird-like style. Bright colorful sky with a magical gradient (purple, pink, and turquoise). Floating glowing clouds and sparkles in the air. Mystical floating islands and crystal mountains in the distance. Flatten, runnable ground area made of enchanted grass with glowing flowers and mushrooms. Playful, vibrant, whimsical style with smooth vector-like shading, clean and iconic, suitable for 2D mobile game assets. ",
            placeholder="A 2D rendered game scene, 16-bit retro pixel art, retro video game, flappy bird-like style. Bright colorful sky with a magical gradient (purple, pink, and turquoise). Floating glowing clouds and sparkles in the air. Mystical floating islands and crystal mountains in the distance. Flatten, runnable ground area made of enchanted grass with glowing flowers and mushrooms. Playful, vibrant, whimsical style with smooth vector-like shading, clean and iconic, suitable for 2D mobile game assets. ",
            key="area 3"
        )


    # --- Generated Image Output Section (on the right) ---
    with col4:
        st.header("6. Background generated image ")
        # --- Button to Trigger Generation ---
        # This is a placeholder for where you would add your generation logic.
        with st.spinner("Generating..."):
            st.success("Image generation process would start now!")
        if st.button("Generate Image", key="button 3"):
                # Load the workflow
                wrk = Workflow()
                workflow_background = wrk.load_workflow(Config.WORKFLOW_BACKGROUND)
                
                if workflow_background:
                    with st.spinner("Processing..."):
                        # Update the workflow with a random seed
                        workflow_background = wrk.update_workflow_with_rdn_seed(workflow_background, "5")

                        # Update the workflow with a new prompt
                        workflow_background = wrk.update_workflow_with_prompt(workflow_background, prompt_background, "3")

                        if workflow_background:
                            # Queue the prompt
                            background_response = wrk.queue_prompt(workflow_background)

                            if background_response:
                                prompt_id_background = background_response.get('prompt_id')
                                if prompt_id_background:
                                    st.info("Prompt queued. Waiting for image generation...")
                                    
                                    # Get the generated image
                                    generated_image_background = wrk.get_image(prompt_id_background)
                                    st.session_state.generated_image_background=generated_image_background
                                else:
                                    st.error("Failed to get prompt ID from the server response.")
                        else:
                            st.error("Failed to update the workflow. Please check your workflow file.")
        if st.session_state.generated_image_background:
            st.image(st.session_state.generated_image_background, caption="Generated background")

with st.container():

    with col_bkg_1:
        st.header("Split background image")
        if st.button("Splitting background", key="button 4"):
            # Assuming 'image_path.png' is your image file
            # Create a BytesIO object from the image bytes
            img = st.session_state.generated_image_background
            # Example of saving to BytesIO and then passing
            buffer = io.BytesIO()
            img.save(buffer, format='PNG') # Save the image to the buffer
            buffer.seek(0) # Rewind the buffer to the beginning
            split_image_into_tiles(buffer, "output_tiles", 1, 4)
            save_img_s3_file("background", "output_tiles/tile_r0_c0.jpg")
            save_img_s3_file("background", "output_tiles/tile_r0_c1.jpg")
            save_img_s3_file("background", "output_tiles/tile_r0_c2.jpg")
            save_img_s3_file("background", "output_tiles/tile_r0_c3.jpg")
            st.session_state.bkg_img_1="output_tiles/tile_r0_c0.jpg"
            st.session_state.bkg_img_2="output_tiles/tile_r0_c1.jpg"
            st.session_state.bkg_img_3="output_tiles/tile_r0_c2.jpg"
            st.session_state.bkg_img_4="output_tiles/tile_r0_c3.jpg"
    with col_bkg_2:
        if st.session_state.bkg_img_1:
            st.image(st.session_state.bkg_img_1, caption="Bkg 1")
    with col_bkg_3:
        if st.session_state.bkg_img_2:
            st.image(st.session_state.bkg_img_2, caption="Bkg 2")
    with col_bkg_4:
        if st.session_state.bkg_img_3:
            st.image(st.session_state.bkg_img_3, caption="Bkg 3")
    with col_bkg_5:
        if st.session_state.bkg_img_4:
            st.image(st.session_state.bkg_img_4, caption="Bkg 4")

with st.container():

    with col_bkg_shift_1:
        st.header("Moving background image")

    with col_bkg_shift_2:
        if st.session_state.bkg_img_3:
            st.image(st.session_state.bkg_img_3, caption="Shift Bkg 3")
    with col_bkg_shift_3:
        if st.session_state.bkg_img_4:
            st.image(st.session_state.bkg_img_4, caption="Shift Bkg 4")
    with col_bkg_shift_4:
        if st.session_state.bkg_img_1:
            st.image(st.session_state.bkg_img_1, caption="Shift Bkg 1")
    with col_bkg_shift_5:
        if st.session_state.bkg_img_2:
            st.image(st.session_state.bkg_img_2, caption="Shift Bkg 2")


