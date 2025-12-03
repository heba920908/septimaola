import os
import uuid
from dotenv import load_dotenv

# ADK imports
from google.adk import Agent
from google.adk.agents import LlmAgent
from google.adk.agents import SequentialAgent, LoopAgent, ParallelAgent
from google.adk.tools.tool_context import ToolContext

from a2a.types import AgentCapabilities, AgentCard, AgentSkill

from google import genai
from google.genai.types import GenerateContentConfig, ImageConfig
from google.cloud import storage 

load_dotenv()

# --- SDK Initialization ---
project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
location = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
client = genai.Client(vertexai=True, project=project_id, location=location)


def generate_image(prompt: str) -> dict[str, str]:
    """Generate an illustration and upload it to GCS using Gemini.

    Args:
        prompt (str): The prompt to provide to the image generation model.

    Returns:
        dict[str, str]: {"image_url": "The public URL of the generated image in GCS."}
    """
    # 1. Call the model
    response = client.models.generate_content(
        model=os.getenv("IMAGE_MODEL"),
        contents=prompt,
        config=GenerateContentConfig(
            response_modalities=["IMAGE"],
            image_config=ImageConfig(
                aspect_ratio="16:9",
            ),
            candidate_count=1,
        ),
    )

    # 2. Extract the raw image data from the response
    image_bytes = response.candidates[0].content.parts[0].inline_data.data

    # 3. Upload the image bytes to Google Cloud Storage
    storage_client = storage.Client(project=project_id)
    bucket_name = f"{project_id}-bucket" # Your bucket name
    bucket = storage_client.bucket(bucket_name)
    
    # Generate a unique name for the image file
    blob_name = f"generated-images/{uuid.uuid4()}.png"
    blob = bucket.blob(blob_name)
    
    # Upload the data
    blob.upload_from_string(image_bytes, content_type="image/png")

    # 4. Construct and return the public URL
    url = f"https://storage.cloud.google.com/{bucket_name}/{blob_name}"
    
    return {"image_url": url}


# ==============================================================================
# Agent code
# ==============================================================================
image_agent = Agent(
    name="illustration_agent",
    model=os.getenv("MODEL"),
    description="Creates branded illustrations.",
    instruction="""
    You are a designer expert in press-kits for music bands.

    You will receive a block of text, it is your job to write
    a prompt that will express the ideas of this text.

    You always emphasize that there should be no text in the image.
    You prefer an informal, artistic, colorful non-photorealistic style of art.
    Your brand palette is purple (#BF40BF), green (#DAF7A6), and sunset colors.
    Consider a clever or charming approach with specific details.
    Incorporate music imagery like lights, instruments, notes, and stages.
    Incorporate nature imagery like plants, flowers, and landscapes.
    Incorporate mexico imagery like cacti, sombreros, and traditional patterns.

    Once you have written the prompt, use your 'generate_image' tool to generate an image.
    Always return both of the following:
        - the text of the prompt you used
        - the generated image URL returned by your tool
    """,
    tools=[generate_image]
)

septima_ola_background_agent = Agent(
    name="septima_ola_background_agent",
    model=os.getenv("MODEL"),
    description="Provides information about the 'septima ola' band.",
    instruction="""
        - Provide the user information about the "septima ola" band.
        "Septima Ola" it is a band that combines reggae, ska, and rocksteady to create a unique sound that resonates with audiences worldwide. Their music is characterized by catchy melodies, infectious rhythms, and socially conscious lyrics that address themes of love, unity, and social justice.
        "Septima Ola" borne out of the shared passion for music among its members, who bring diverse influences and experiences to the table. In Alfred's departmen in La Raza DF, Mexico, the band keeps growing and evolving, captivating audiences with their energetic live performances and heartfelt songs.
        "Septima Ola" objective is to spread positive messages through their music, inspiring listeners to embrace love, peace, and social change.
        Our vision is to be a leading force in the reggae and ska music scene, known for our authentic sound, meaningful lyrics, and commitment to artistic integrity, while our mission is to create music that resonates with people from all walks of life, fostering a sense of community and empowerment through our art.
        """,
    before_model_callback=log_query_to_model,
    after_model_callback=log_model_response,
    )

root_agent = LlmAgent(
    model=os.getenv("MODEL"),
    name='slide_content_agent',
    description='An agent that writes content for slide decks.',
    #after_tool_callback=self._handle_auth_required_task,
    instruction="""
        A user will ask you to create content for a slide to communicate an idea.
        Ask about the background of the bad using the 'septima_ola_background_agent'.
        Write a short headline about this idea.
        Write 1-2 sentences of body text about this idea.
        Share these with the user.
        Then transfer to the 'image_agent' to generate an illustration related to this idea.
        """,
	# Add the sub_agents parameter below
    sub_agents=[image_agent, septima_ola_background_agent]
)
