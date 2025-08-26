import streamlit as st
from PIL import Image
from src.code.workflow import Workflow
# --- Configuration ---
# You need to replace this with your ComfyUI server address
# The address should not include http:// or ws://


# --- App Configuration and Title ---
st.set_page_config(
    page_title="Image Generation App Template",
    page_icon="🎨",
    layout="wide"
)

st.title("🎨 ComfyUI Image Generator Web App")

# --- Main Columns for Layout ---
st.header("1. Input Prompt")
# A text area for the user to enter the image generation prompt.
prompt = st.text_area(
    "Enter your prompt for image generation here:",
    height=150,
    placeholder="e.g., A futuristic city with flying cars, highly detailed, sci-fi"
)
col1, col2 = st.columns([1, 1])

# --- User Input Section (on the left) ---
with col1:

    st.header("2. Input Image")
    # An image uploader for the first image (the "input image").
    uploaded_image = st.file_uploader(
        "Upload an image here as reference:",
        type=["png", "jpg", "jpeg"]
    )

    # Display the uploaded image if it exists.
    if uploaded_image:
        try:
            # Open the image using PIL
            st.image(uploaded_image, caption="Uploaded Input Image", use_container_width=True)
        except Exception as e:
            st.error(f"Error loading image: {e}")


# --- Generated Image Output Section (on the right) ---
with col2:
    st.header("3. Generated Image")
    # --- Button to Trigger Generation ---
    # This is a placeholder for where you would add your generation logic.
    if st.button("Generate Image"):
        if uploaded_image is None:
            st.warning("Please upload an image first.")
        else:
            # Load the workflow
            wrk = Workflow()
            workflow = wrk.load_workflow()
            
            if workflow:
                with st.spinner("Processing..."):
                    # Read the uploaded file as bytes
                    image_bytes = uploaded_image.read()

                    # Update the workflow with the input image
                    workflow = wrk.update_workflow_with_image(workflow, image_bytes)
                    
                    # Update the workflow with a random seed
                    workflow = wrk.update_workflow_with_rdn_seed(workflow)

                    # Update the workflow with a new prompt
                    workflow = wrk.update_workflow_with_prompt(workflow, prompt)

                    if workflow:
                        # Queue the prompt
                        response = wrk.queue_prompt(workflow)

                        if response:
                            prompt_id = response.get('prompt_id')
                            if prompt_id:
                                st.info("Prompt queued. Waiting for image generation...")
                                
                                # Get the generated image
                                generated_image = wrk.get_image(prompt_id)

                                if generated_image:
                                    st.success("Image generated successfully!")
                                    st.image(generated_image, caption="Generated Image")
                                else:
                                    st.error("Failed to retrieve the generated image.")
                            else:
                                st.error("Failed to get prompt ID from the server response.")
                    else:
                        st.error("Failed to update the workflow. Please check your workflow file.")
            with st.spinner("Generating..."):
                st.success("Image generation process would start now!")
