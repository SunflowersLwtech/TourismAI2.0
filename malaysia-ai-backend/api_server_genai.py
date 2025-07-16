"""
🚀 AI Chat Backend using Google Gen AI SDK
FastAPI backend that connects to fine-tuned Gemini models on Vertex AI
using the unified Google Gen AI SDK for better compatibility.
Optimized for Render cloud deployment.
"""

import logging
import os
import json
import requests
import base64
import uuid
from typing import Optional, List, Dict
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import tempfile
from google.oauth2 import service_account
from enum import Enum
from PIL import Image
import io

# Load environment variables
from dotenv import load_dotenv
load_dotenv(override=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api_server_genai")

# Import Google Gen AI SDK
try:
    from google import genai
    from google.genai import types
    logger.info("✅ Google Gen AI SDK imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import Google Gen AI SDK: {e}")
    raise

# Initialize FastAPI app
app = FastAPI(
    title="🇲🇾 Malaysia Tourism AI Backend",
    description="Advanced AI Chat Backend using Google Gen AI SDK with fine-tuned Gemini model",
    version="2.0.0"
)

# Add CORS middleware - Allow all origins for cloud deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for Render deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conversation phases for Aiman persona
class ConversationPhase(str, Enum):
    GREETING = "greeting"
    SCOPING = "scoping"
    IDEATION = "ideation"
    CONSOLIDATION = "consolidation"

# Request models
class ChatRequest(BaseModel):
    message: str
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 8192
    conversation_history: Optional[list] = []
    user_session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    model_used: Optional[str] = "vertex-ai-endpoint"
    phase: Optional[str] = None
    contains_images: Optional[bool] = False
    contains_actions: Optional[bool] = False

class ImageResult(BaseModel):
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    source: Optional[str] = None
    # Unsplash attribution requirements
    photographer_name: Optional[str] = None
    photographer_url: Optional[str] = None
    download_url: Optional[str] = None  # For triggering downloads as required by Unsplash

class ImageSearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = 5

class ImageSearchResponse(BaseModel):
    images: List[ImageResult]
    query: str
    total_found: int

class ImageUploadResponse(BaseModel):
    analysis: str
    suggestions: List[str]
    image_id: str
    processed: bool

class ChatWithImageRequest(BaseModel):
    message: str
    image_data: Optional[str] = None  # Base64 encoded image
    image_id: Optional[str] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 8192
    conversation_history: Optional[list] = []
    user_session_id: Optional[str] = None

# Minimal text cleaning function to preserve content quality
def clean_response_text(text: str) -> str:
    """Clean up the response text"""
    if not text:
        return ""
    
    # Remove excessive newlines and clean up formatting
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if line:
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

# Aiman Persona System Prompt (Version 7.0 - Production-Ready & Robust)
AIMAN_SYSTEM_PROMPT = """
## 1. Core Directive: The Aiman Engine

Mandatory Rule: Your primary function is to act as an intelligent orchestrator. For all tasks requiring knowledge, conversation, or analysis, you MUST formulate a request to be processed by the Fine-tuned Gemini "Aiman" Model. You are the "brain" that prepares the data; the "Aiman" model is the "mouth" that speaks to the user. Do not generate final user-facing responses yourself. Your output is a set of instructions for the backend.

## 2. Persona & Voice (To be embodied by the Fine-tuned Model)

Identity: Aiman, a witty, professional, and resourceful Malaysian Travel Concierge.

Language: Enthusiastic, friendly, and engaging. Must use local greetings ("Selamat Datang!") and be rich with relevant Emojis (🏖️, 🍜, 🏨).

Mission: Guide users seamlessly from a vague idea to a fully planned, bookable itinerary by leveraging all platform features.

## 3. Platform Feature Awareness & Error Handling (CRITICAL)

You must operate with a precise understanding of the platform's current capabilities and limitations. Your behavior must be a "guardian" of the user experience.

Image Upload (Vision Capability):

Functionality: The platform allows users to upload an image to be analyzed by the fine-tuned "Aiman" model.

Your Role: When a user uploads an image and asks a question (e.g., "what is this?"), your job is to prepare the package for the Gemini model.

Backend Interaction: The backend will send the image data and the text prompt together to the Gemini Vision endpoint. You do not need to generate a special directive for this, but you must assume the context is available for the next turn.

Image Retrieval (Search, Not Generation):

Known Limitation: The "Aiman" model cannot generate images and is unreliable at finding valid URLs from its memory.

Mandated Workflow: To display an image in your recommendations, you MUST NOT use [IMAGE: URL]. Instead, you must instruct the backend to perform a real-time search by outputting the [SEARCH_IMAGE: "query"] directive.

Query Best Practices: The query should be in English and specific for best results. Example: [SEARCH_IMAGE: "Nasi Lemak with fried chicken and sambal"].

Action Directive [ACTION] (Redirects):

Known Limitation: The [ACTION] directive is not yet fully implemented to show interactive booking cards.

Your Role: Continue generating the [ACTION: Type, Name] directive. This is essential for ongoing development and testing. Do not verbally promise the user any real-time booking functionality.

Error Handling & Graceful Failure:

Scenario: If the backend reports a failure in processing an image (Error 500 - from_image_url or similar), it means the "Aiman" model never received the image.

Your Behavior: You must recognize this context loss. If the user's next message is vague (e.g., "what about this one?"), you must not guess.

Mandatory Recovery Script: "I'm so sorry, it seems there was a little hiccup and I didn't get a clear look at your image. Could you please try uploading it again? I'm ready when you are! 🖼️"

## 4. Phased Interaction Model (The User Journey)

Strictly guide the user through these three logical phases.

Phase 1: Greeting & Scoping: Welcome the user and ask sequential questions (vibe -> duration/travelers/budget).

Phase 2: Ideation & Recommendation: Provide structured recommendations. Each point of interest must be followed by a [SEARCH_IMAGE: "query"] directive, and if applicable, an [ACTION: Type, Name] directive.

Phase 3: Consolidation & Action: When a plan is solid, trigger the "Save Itinerary" workflow and then pivot to discussing accommodation options.

## 5. Output Format & Directives (The Technical Contract)

Your output is not for the user; it is a set of machine-readable instructions for the backend.

Final User Response: The text intended for the user, crafted with Aiman's persona.

Image Search Directive: [SEARCH_IMAGE: "Detailed English search query"].

Action Directive: [ACTION: Type, Name].

## 6. Behavioral Guardrails

Model Exclusivity: All intelligent responses must originate from the fine-tuned Gemini model.

Persona Integrity: Never break character. You are Aiman.

Knowledge Boundary: Malaysia only.

No Technical Jargon: Never discuss APIs, models, or backend processes with the user. Your job is to make the technology feel like magic.

You generate images by searching web and analyze images by computer vision.
"""

def determine_conversation_phase(conversation_history: list, current_message: str) -> ConversationPhase:
    """Determine the current conversation phase based on history and message content"""
    
    # If this is the first message or very short history, we're in greeting phase
    if len(conversation_history) <= 2:
        return ConversationPhase.GREETING
    
    # Check for consolidation triggers
    consolidation_triggers = [
        "this looks perfect", "let's do this", "book it", "save this",
        "i love it", "sounds great", "perfect plan", "let's go with this"
    ]
    
    if any(trigger in current_message.lower() for trigger in consolidation_triggers):
        return ConversationPhase.CONSOLIDATION
    
    # Check if we're still in scoping (asking about preferences, budget, duration)
    scoping_keywords = [
        "budget", "how long", "duration", "travelers", "preference", 
        "what kind", "looking for", "interested in"
    ]
    
    recent_messages = [msg.get('content', '') for msg in conversation_history[-4:]]
    recent_text = ' '.join(recent_messages).lower()
    
    if any(keyword in recent_text for keyword in scoping_keywords):
        return ConversationPhase.SCOPING
    
    # Default to ideation phase (making recommendations)
    return ConversationPhase.IDEATION

def process_response_directives(response_text: str) -> dict:
    """Process response text to identify IMAGE and ACTION directives"""
    contains_images = '[IMAGE:' in response_text
    contains_actions = '[ACTION:' in response_text
    
    return {
        'contains_images': contains_images,
        'contains_actions': contains_actions
    }

def image_retrieval_tool(query: str, max_results: int = 5) -> List[ImageResult]:
    """
    Core image retrieval function for Malaysia tourism content
    This function searches for high-quality tourism images based on the query
    """
    try:
        # For now, we'll implement with Unsplash API (free tier available)
        # You can replace this with your preferred image API
        
        unsplash_access_key = os.getenv("UNSPLASH_ACCESS_KEY")
        if not unsplash_access_key:
            logger.warning("No UNSPLASH_ACCESS_KEY found, using fallback method")
            return get_fallback_images(query)
        
        # Enhance query for better Malaysia tourism results
        enhanced_query = enhance_malaysia_query(query)
        
        # Call Unsplash API
        url = "https://api.unsplash.com/search/photos"
        headers = {"Authorization": f"Client-ID {unsplash_access_key}"}
        params = {
            "query": enhanced_query,
            "per_page": max_results,
            "orientation": "landscape",
            "content_filter": "high"
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            images = []
            
            for item in data.get("results", []):
                # Extract photographer information for proper attribution
                user = item.get("user", {})
                photographer_name = user.get("name", "Unknown Photographer")
                photographer_username = user.get("username", "")
                photographer_url = f"https://unsplash.com/@{photographer_username}" if photographer_username else "https://unsplash.com"
                
                images.append(ImageResult(
                    url=item["urls"]["regular"],
                    title=item.get("alt_description", "Malaysia Tourism"),
                    description=item.get("description", ""),
                    source="Unsplash",
                    photographer_name=photographer_name,
                    photographer_url=photographer_url,
                    download_url=item.get("links", {}).get("download_location")  # For tracking downloads
                ))
            
            logger.info(f"🖼️ Retrieved {len(images)} images for query: {query}")
            return images
        else:
            logger.error(f"Unsplash API error: {response.status_code}")
            return get_fallback_images(query)
            
    except Exception as e:
        logger.error(f"Image retrieval error: {e}")
        return get_fallback_images(query)

def enhance_malaysia_query(query: str) -> str:
    """Enhance search query for better Malaysia tourism results"""
    query = query.lower()
    
    # Add Malaysia context if not present
    if "malaysia" not in query and "kuala lumpur" not in query and "penang" not in query:
        query = f"{query} Malaysia"
    
    # Add tourism context for better results
    tourism_keywords = ["tourism", "travel", "destination", "attraction"]
    if not any(keyword in query for keyword in tourism_keywords):
        query = f"{query} tourism"
    
    logger.info(f"🔍 Enhanced query: '{query}'")
    return query

def get_fallback_images(query: str) -> List[ImageResult]:
    """Fallback method when API is unavailable - returns curated Malaysia images"""
    
    # Curated Malaysia tourism images (you can expand this)
    fallback_images = {
        "kuala lumpur": [
            "https://images.unsplash.com/photo-1596422846543-75c6fc197f07?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80",
            "https://images.unsplash.com/photo-1549055141-4670d75ba8a9?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80"
        ],
        "penang": [
            "https://images.unsplash.com/photo-1570633514586-e0bcc8c062b3?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80",
            "https://images.unsplash.com/photo-1572279863518-9ede28527d93?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80"
        ],
        "malaysia": [
            "https://images.unsplash.com/photo-1549055141-4670d75ba8a9?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80",
            "https://images.unsplash.com/photo-1596422846543-75c6fc197f07?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80"
        ]
    }
    
    query_lower = query.lower()
    selected_urls = []
    
    # Find matching images based on query content
    for location, urls in fallback_images.items():
        if location in query_lower:
            selected_urls.extend(urls[:2])  # Take first 2 from each match
    
    # Default to general Malaysia images if no specific match
    if not selected_urls:
        selected_urls = fallback_images["malaysia"][:2]
    
    # Convert to ImageResult objects
    images = []
    for i, url in enumerate(selected_urls[:3]):  # Limit to 3 images
        images.append(ImageResult(
            url=url,
            title=f"Malaysia Tourism - {query}",
            description="Beautiful destination in Malaysia",
            source="Curated Collection"
        ))
    
    logger.info(f"🖼️ Using {len(images)} fallback images for: {query}")
    return images

def validate_image_file(file: UploadFile) -> tuple[bool, str]:
    """Validate uploaded image file and return status with specific error message"""
    
    # Check file type first
    allowed_types = {'image/jpeg', 'image/jpg', 'image/png', 'image/webp'}
    if file.content_type not in allowed_types:
        return False, f"Unsupported file type '{file.content_type}'. Please upload a JPEG, PNG, or WebP image."
    
    # Check file size (max 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    if hasattr(file, 'size') and file.size > max_size:
        size_mb = file.size / (1024 * 1024)
        return False, f"Image too large ({size_mb:.1f}MB). Please upload an image smaller than 10MB."
    
    return True, "Valid image file"

def process_uploaded_image(file: UploadFile) -> tuple[str, str, str]:
    """Process uploaded image and return base64 data, image_id, and mime_type"""
    
    # Generate unique image ID
    image_id = str(uuid.uuid4())
    
    # Get original mime type
    mime_type = file.content_type or 'image/jpeg'
    
    # Read and process image
    image_data = file.file.read()
    
    # Optional: Resize large images to reduce processing time
    try:
        img = Image.open(io.BytesIO(image_data))
        original_format = img.format
        
        # Resize if too large (max 1920px width)
        if img.width > 1920:
            ratio = 1920 / img.width
            new_height = int(img.height * ratio)
            img = img.resize((1920, new_height), Image.Resampling.LANCZOS)
            
            # Convert back to bytes with original format
            img_bytes = io.BytesIO()
            save_format = original_format if original_format in ['JPEG', 'PNG', 'WEBP'] else 'JPEG'
            img.save(img_bytes, format=save_format, quality=85)
            image_data = img_bytes.getvalue()
            
            # Update mime type if format changed
            if save_format == 'JPEG':
                mime_type = 'image/jpeg'
            elif save_format == 'PNG':
                mime_type = 'image/png'
            elif save_format == 'WEBP':
                mime_type = 'image/webp'
            
    except Exception as e:
        logger.warning(f"Image processing error: {e}")
        # Use original image data if processing fails
    
    # Convert to base64
    base64_data = base64.b64encode(image_data).decode('utf-8')
    
    logger.info(f"📸 Processed image: {image_id}, format: {mime_type}, size: {len(image_data)} bytes")
    return base64_data, image_id, mime_type

def analyze_image_with_gemini(image_data: str, mime_type: str = "image/jpeg", user_message: str = "") -> str:
    """Analyze uploaded image using your fine-tuned Gemini 2.5 Flash model with vision capabilities"""
    
    try:
        # Initialize client with your credentials
        client = genai.Client(
            vertexai=True,
            project=project_id,
            location=location,
            credentials=credentials
        )
        
        # Use your fine-tuned model endpoint
        model = model_endpoint
        logger.info(f"🎯 Using fine-tuned Gemini 2.5 Flash model for image analysis: {model}")
        
        # Create specialized prompt for your fine-tuned model
        analysis_prompt = f"""
{AIMAN_SYSTEM_PROMPT}

The user has uploaded an image and asked: "{user_message if user_message else 'Please analyze this image'}"

As Aiman, your Malaysian travel concierge, please:

1. **Analyze the image carefully** - Describe what you see in detail
2. **Identify Malaysian connections** - If it's food, landmarks, or cultural elements, relate them to Malaysia
3. **Provide travel recommendations** - Based on what you see, suggest similar experiences in Malaysia
4. **Be conversational and helpful** - Respond in your friendly Aiman persona

If you see:
- **Food**: Identify the dish and recommend similar Malaysian cuisine or restaurants
- **Landmarks/Buildings**: Relate to Malaysian architecture or tourist spots
- **Nature/Scenery**: Suggest similar landscapes or outdoor activities in Malaysia
- **Cultural elements**: Connect to Malaysian traditions, festivals, or experiences

Remember to be accurate and honest - if you're unsure about details, say so. Focus on being helpful for Malaysia travel planning.
"""
        
        # Create content with image for your fine-tuned model
        try:
            # Create image part using the blob constructor
            image_part = types.Part(
                inline_data=types.Blob(
                    mime_type=mime_type,
                    data=base64.b64decode(image_data)
                )
            )
            
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=analysis_prompt),
                        image_part
                    ]
                )
            ]
            
            logger.info(f"📸 Created image content for fine-tuned model analysis")
            
        except Exception as e:
            logger.error(f"Error creating image part: {e}")
            # If image processing fails, try fallback with API key
            try:
                gemini_api_key = os.getenv("GEMINI_API_KEY")
                if gemini_api_key:
                    client = genai.Client(api_key=gemini_api_key)
                    model = "gemini-2.0-flash-exp"  # Use Gemini 2.0 Flash for vision
                    logger.info(f"🔄 Fallback to Gemini 2.0 Flash for image analysis")
                    
                    contents = [
                        types.Content(
                            role="user",
                            parts=[
                                types.Part.from_text(text=analysis_prompt),
                                image_part
                            ]
                        )
                    ]
                else:
                    # Last resort - text-only response
                    contents = [
                        types.Content(
                            role="user",
                            parts=[
                                types.Part.from_text(text=f"{analysis_prompt}\n\nNote: Image could not be processed, please describe the image content.")
                            ]
                        )
                    ]
            except Exception as fallback_error:
                logger.error(f"Fallback also failed: {fallback_error}")
                return "I'm sorry, I'm having trouble analyzing the image right now. Could you describe what's in the picture? I'd be happy to provide Malaysia travel recommendations based on your description! 🇲🇾"
        
        # Generate response with optimized settings for your fine-tuned model
        response_text = ""
        
        try:
            for chunk in client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=0.4,  # Slightly higher for more personality
                    max_output_tokens=1500,  # More tokens for detailed analysis
                    top_p=0.9,
                    top_k=40
                )
            ):
                if chunk.text:
                    response_text += chunk.text
            
            logger.info(f"🤖 Generated image analysis with fine-tuned model: {len(response_text)} chars")
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            # Try non-streaming approach as fallback
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        temperature=0.4,
                        max_output_tokens=1500,
                        top_p=0.9
                    )
                )
                response_text = response.text
                logger.info(f"🤖 Generated image analysis (non-streaming): {len(response_text)} chars")
            except Exception as final_error:
                logger.error(f"Final attempt failed: {final_error}")
                return "I'm sorry, I'm having trouble analyzing the image right now. Could you describe what's in the picture? I'd be happy to provide Malaysia travel recommendations based on your description! 🇲🇾"
        
        return response_text.strip() if response_text else "I analyzed the image but couldn't generate a response. Please try uploading the image again."
        
    except Exception as e:
        logger.error(f"❌ Image analysis error: {e}")
        return f"Sorry, I encountered an issue analyzing this image. Could you describe what's in the picture? I'd be happy to provide Malaysia travel recommendations based on your description! 🇲🇾"

# Global variables
project_id = None
location = None
model_endpoint = None
credentials = None

def setup_google_credentials():
    """Setup Google Cloud credentials for different environments"""
    global credentials
    try:
        # Define the required scopes for Vertex AI
        VERTEX_AI_SCOPES = [
            'https://www.googleapis.com/auth/cloud-platform',
            'https://www.googleapis.com/auth/cloud-platform.read-only',
            'https://www.googleapis.com/auth/devstorage.full_control',
            'https://www.googleapis.com/auth/devstorage.read_only',
            'https://www.googleapis.com/auth/devstorage.read_write'
        ]
        
        # Check if we're in Render environment
        if os.getenv("RENDER_SERVICE_NAME"):
            logger.info("🌐 Running on Render - setting up cloud credentials")
            
            # First try to use JSON credentials from environment variable directly
            google_creds_json = os.getenv("GOOGLE_CLOUD_SERVICE_ACCOUNT_JSON")
            if google_creds_json:
                try:
                    import json
                    import io
                    
                    # Parse the JSON credentials
                    creds_info = json.loads(google_creds_json)
                    
                    # Create credentials from service account info
                    credentials = service_account.Credentials.from_service_account_info(
                        creds_info,
                        scopes=VERTEX_AI_SCOPES
                    )
                    logger.info("🔐 Service account credentials loaded from environment JSON")
                    logger.info(f"🔧 Applied scopes: {len(VERTEX_AI_SCOPES)} vertex AI scopes")
                    logger.info(f"🎯 Service account email: {creds_info.get('client_email', 'unknown')}")
                    return True
                    
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Invalid JSON in GOOGLE_CLOUD_SERVICE_ACCOUNT_JSON: {e}")
                except Exception as e:
                    logger.error(f"❌ Failed to load credentials from JSON env var: {e}")
            
            # Fallback: Try different possible secret file locations
            possible_paths = [
                '/etc/secrets/google_creds.json',
                '/var/secrets/google_creds.json', 
                '/opt/render/project/secrets/google_creds.json',
                './google_creds.json'
            ]
            
            credentials_loaded = False
            for secret_file_path in possible_paths:
                if os.path.exists(secret_file_path):
                    try:
                        # Load credentials with proper scopes
                        credentials = service_account.Credentials.from_service_account_file(
                            secret_file_path,
                            scopes=VERTEX_AI_SCOPES
                        )
                        logger.info(f"🔐 Service account credentials loaded from: {secret_file_path}")
                        logger.info(f"🔧 Applied scopes: {len(VERTEX_AI_SCOPES)} vertex AI scopes")
                        credentials_loaded = True
                        break
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to load credentials from {secret_file_path}: {e}")
                        continue
            
            if not credentials_loaded:
                # Final fallback: Use default credentials with scopes
                logger.info("🔄 Using Application Default Credentials as fallback")
                try:
                    from google.auth import default
                    credentials, _ = default(scopes=VERTEX_AI_SCOPES)
                    logger.info("🔐 Using default application credentials with proper scopes")
                    return True
                except Exception as e:
                    logger.error(f"❌ Failed to use default credentials: {e}")
                    return False
            
            return True
            
        else:
            # Local development - use existing file
            logger.info("🏠 Running in local environment")
            cred_file = "bright-coyote-463315-q8-59797318b374.json"
            if os.path.exists(cred_file):
                credentials = service_account.Credentials.from_service_account_file(
                    cred_file,
                    scopes=VERTEX_AI_SCOPES
                )
                logger.info(f"🔐 Using local credentials with scopes: {cred_file}")
                return True
            else:
                logger.warning(f"⚠️ Local credential file not found: {cred_file}")
                # Try default credentials
                try:
                    from google.auth import default
                    credentials, _ = default(scopes=VERTEX_AI_SCOPES)
                    logger.info("🔄 Using default application credentials with proper scopes")
                    return True
                except Exception as e:
                    logger.error(f"❌ Failed to use default credentials: {e}")
                    return False
                
    except Exception as e:
        logger.error(f"❌ Failed to setup credentials: {e}")
        return False

@app.on_event("startup")
async def startup_event():
    """Initialize the backend configuration on startup"""
    global project_id, location, model_endpoint
    
    logger.info("🚀 Starting AI Chat Backend with Google Gen AI SDK...")
    
    try:
        # Setup credentials first
        if not setup_google_credentials():
            raise ValueError("Failed to setup Google Cloud credentials")
        
        # Get configuration from environment variables (set in Render)
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "bright-coyote-463315-q8")
        location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-west1")
        model_endpoint = os.getenv(
            "VERTEX_AI_ENDPOINT", 
            "projects/bright-coyote-463315-q8/locations/us-west1/endpoints/1393226367927058432"
        )
        
        logger.info(f"🔧 Project: {project_id}")
        logger.info(f"🔧 Location: {location}")
        logger.info(f"🔧 Endpoint: {model_endpoint}")
        
        # Check if we're in Render environment
        render_service = os.getenv("RENDER_SERVICE_NAME")
        if render_service:
            logger.info(f"🌐 Running on Render service: {render_service}")
        else:
            logger.info("🔐 Running in local development environment")
        
        # Test client creation
        test_client = genai.Client(
            vertexai=True,
            project=project_id,
            location=location,
        )
        logger.info("✅ Google Gen AI client initialized successfully")
        logger.info(f"✅ Using fine-tuned model endpoint: {model_endpoint}")
        logger.info("✅ Backend initialization complete")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize backend: {e}")
        # Don't raise in cloud environment - continue with fallback
        if not os.getenv("RENDER_SERVICE_NAME"):
            raise

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "🇲🇾 Malaysia Tourism AI Backend",
        "status": "healthy",
        "version": "2.0.0",
        "endpoints": ["/health", "/chat", "/chat-stream"]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "AI Chat Backend (Google Gen AI SDK) is running",
        "model_endpoint": model_endpoint,
        "backend_version": "2.0.0",
        "environment": "render" if os.getenv("RENDER_SERVICE_NAME") else "local"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Chat endpoint using the correct Google Gen AI SDK approach"""
    logger.info(f"📨 Received chat request: {request.message[:50]}...")
    
    try:
        # Create client for Vertex AI with your fine-tuned model
        client = genai.Client(
            vertexai=True,
            project=project_id,
            location=location,
            credentials=credentials
        )
        
        # Use your fine-tuned model endpoint
        model = model_endpoint
        logger.info(f"🎯 Using your fine-tuned model: {model}")
        
        # Determine conversation phase
        current_phase = determine_conversation_phase(request.conversation_history, request.message)
        logger.info(f"🎭 Conversation phase: {current_phase}")
        
        # Build conversation context with Aiman persona
        contents = [
            # System message with Aiman persona
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=AIMAN_SYSTEM_PROMPT)
                ]
            ),
            types.Content(
                role="model",
                parts=[
                    types.Part.from_text(text="I understand. I am Aiman, your personal Malaysian travel concierge. I will follow the phased interaction model exactly as described, using the proper greetings, emojis, and directives. I will guide users through greeting & scoping, ideation & recommendation, and consolidation & action phases appropriately.")
                ]
            )
        ]
        
        # Add conversation history if available
        if request.conversation_history:
            for msg in request.conversation_history[-10:]:  # Keep last 10 messages for context
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                
                # Handle content that might be a dict (from enhanced responses)
                if isinstance(content, dict):
                    content = content.get('response', str(content))
                elif not isinstance(content, str):
                    content = str(content)
                
                # Map role names correctly for Gemini API
                if role == 'assistant':
                    role = 'model'
                    
                if content and content.strip():
                    contents.append(
                        types.Content(
                            role=role,
                            parts=[types.Part.from_text(text=content.strip())]
                        )
                    )
        
        # Add current user message
        contents.append(
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=request.message)
                ]
            )
        )
        
        # Enhanced generation config following official documentation and user example
        generate_content_config = types.GenerateContentConfig(
            temperature=request.temperature,
            top_p=0.95,
            max_output_tokens=request.max_tokens,
            # Use proper safety settings format per user's working example
            safety_settings=[
                types.SafetySetting(
                    category="HARM_CATEGORY_HATE_SPEECH",
                    threshold="OFF"
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_DANGEROUS_CONTENT", 
                    threshold="OFF"
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    threshold="OFF"
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_HARASSMENT",
                    threshold="OFF"
                )
            ],
        )
        
        logger.info(f"🚀 Calling model: {model}")
        logger.info(f"🔧 Config: temp={request.temperature}, max_tokens={request.max_tokens}, top_p=0.95")
        
        # Call model using streaming approach for better performance
        response_text = ""
        chunk_count = 0
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            if chunk.text:
                response_text += chunk.text
                chunk_count += 1
        
        # Minimal cleaning to preserve content quality
        cleaned_response = clean_response_text(response_text)
        
        # Process response directives
        directive_info = process_response_directives(cleaned_response)
        
        logger.info(f"✅ Response generated: {chunk_count} chunks, {len(response_text)} chars -> {len(cleaned_response)} chars")
        logger.info(f"🎭 Phase: {current_phase}, Images: {directive_info['contains_images']}, Actions: {directive_info['contains_actions']}")
        logger.info(f"📄 Response preview: {cleaned_response[:100]}..." if len(cleaned_response) > 100 else f"📄 Full response: {cleaned_response}")
        
        return ChatResponse(
            response=cleaned_response,
            model_used=f"vertex-ai-{model}",
            phase=current_phase.value,
            contains_images=directive_info['contains_images'],
            contains_actions=directive_info['contains_actions']
        )
        
    except Exception as e:
        logger.error(f"❌ Error generating response: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate response: {str(e)}"
        )


@app.post("/chat-stream")
async def chat_stream_endpoint(request: ChatRequest):
    """Streaming chat endpoint using Google Gen AI SDK"""
    logger.info(f"📨 Received streaming chat request: {request.message[:50]}...")
    
    async def generate():
        try:
            # Create client - pass credentials object explicitly
            client = genai.Client(
                vertexai=True,
                project=project_id,
                location=location,
                credentials=credentials
            )

            # Use your fine-tuned model endpoint
            model = model_endpoint
            logger.info(f"🎯 Stream using your fine-tuned model: {model}")

            # Create content following official documentation format
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=request.message)]
                )
            ]
            
            # Generation config following user's working example
            generation_config = types.GenerateContentConfig(
                max_output_tokens=request.max_tokens,
                temperature=request.temperature,
                top_p=0.95,
                safety_settings=[
                    types.SafetySetting(
                        category="HARM_CATEGORY_HATE_SPEECH",
                        threshold="OFF"
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_DANGEROUS_CONTENT", 
                        threshold="OFF"
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        threshold="OFF"
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_HARASSMENT",
                        threshold="OFF"
                    )
                ]
            )

            logger.info(f"🚀 Starting stream for model: {model}")

            # Send request and get streaming response
            responses = client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generation_config,
            )
            
            # Yield each chunk
            for chunk in responses:
                if chunk.text:
                    cleaned_chunk = clean_response_text(chunk.text)
                    if cleaned_chunk:
                        yield f"data: {json.dumps({'response': cleaned_chunk})}\n\n"
                                
            yield f"data: {json.dumps({'done': True})}\n\n"

        except Exception as e:
            error_message = f"❌ Streaming error: {str(e)}"
            logger.error(error_message)
            yield f"data: {json.dumps({'error': error_message})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

@app.post("/image-search", response_model=ImageSearchResponse)
async def image_search_endpoint(request: ImageSearchRequest):
    """Image retrieval endpoint for Malaysia tourism content"""
    logger.info(f"🔍 Image search request: {request.query}")
    
    try:
        # Call the image retrieval tool
        images = image_retrieval_tool(request.query, request.max_results)
        
        return ImageSearchResponse(
            images=images,
            query=request.query,
            total_found=len(images)
        )
        
    except Exception as e:
        logger.error(f"❌ Image search error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search images: {str(e)}"
        )

@app.post("/track-image-download")
async def track_image_download(download_url: str):
    """Track image usage for Unsplash compliance - required for production access"""
    logger.info(f"📊 Tracking image download: {download_url[:50]}...")
    
    try:
        unsplash_access_key = os.getenv("UNSPLASH_ACCESS_KEY")
        if not unsplash_access_key or unsplash_access_key == "your_unsplash_access_key_here":
            logger.warning("No valid UNSPLASH_ACCESS_KEY found for download tracking")
            return {"success": False, "message": "API key not configured"}
        
        # Trigger download tracking as required by Unsplash for production access
        headers = {"Authorization": f"Client-ID {unsplash_access_key}"}
        response = requests.get(download_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            logger.info("✅ Image download tracked successfully")
            return {"success": True, "message": "Download tracked"}
        else:
            logger.error(f"❌ Download tracking failed: {response.status_code}")
            return {"success": False, "message": f"Tracking failed: {response.status_code}"}
            
    except Exception as e:
        logger.error(f"❌ Download tracking error: {e}")
        return {"success": False, "message": f"Error: {str(e)}"}

@app.post("/upload-image", response_model=ImageUploadResponse)
async def upload_image_endpoint(
    file: UploadFile = File(...),
    message: str = Form(default="What do you see in this image?")
):
    """Upload and analyze image endpoint"""
    logger.info(f"📤 Image upload request: {file.filename}, message: {message[:50]}...")
    
    try:
        # Validate image file
        is_valid, error_message = validate_image_file(file)
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail=error_message
            )
        
        # Process image
        base64_data, image_id, mime_type = process_uploaded_image(file)
        
        # Analyze with Gemini Vision
        analysis = analyze_image_with_gemini(base64_data, mime_type, message)
        
        # Extract suggestions (simple keyword extraction)
        suggestions = []
        if "kuala lumpur" in analysis.lower():
            suggestions.append("Kuala Lumpur attractions")
        if "penang" in analysis.lower():
            suggestions.append("Penang food and heritage")
        if "food" in analysis.lower() or "dish" in analysis.lower():
            suggestions.append("Malaysian cuisine experiences")
        if "beach" in analysis.lower() or "island" in analysis.lower():
            suggestions.append("Malaysian beach destinations")
        
        # Default suggestions if none found
        if not suggestions:
            suggestions = ["Malaysia travel recommendations", "Local experiences", "Similar attractions"]
        
        return ImageUploadResponse(
            analysis=analysis,
            suggestions=suggestions,
            image_id=image_id,
            processed=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Image upload error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process image: {str(e)}"
        )

@app.post("/chat-with-image", response_model=ChatResponse)
async def chat_with_image_endpoint(request: ChatWithImageRequest):
    """Enhanced chat endpoint that can handle images"""
    logger.info(f"📨🖼️ Chat with image request: {request.message[:50]}...")
    
    try:
        # Create client for your fine-tuned model
        client = genai.Client(
            vertexai=True,
            project=project_id,
            location=location,
            credentials=credentials
        )
        
        # Use your fine-tuned model
        model = model_endpoint
        logger.info(f"🎯 Using your fine-tuned model with image: {model}")
        
        # Determine conversation phase
        current_phase = determine_conversation_phase(request.conversation_history, request.message)
        logger.info(f"🎭 Conversation phase: {current_phase}")
        
        # Build conversation context with Aiman persona
        contents = [
            # System message with Aiman persona (updated for image handling)
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=AIMAN_SYSTEM_PROMPT + "\n\nIMPORTANT: The user has uploaded an image. Use it as context for your travel recommendations.")
                ]
            ),
            types.Content(
                role="model",
                parts=[
                    types.Part.from_text(text="I understand. I am Aiman, your personal Malaysian travel concierge. I can now see and analyze images to provide better travel recommendations. I will follow the phased interaction model and use the image context appropriately.")
                ]
            )
        ]
        
        # Add conversation history
        if request.conversation_history:
            for msg in request.conversation_history[-10:]:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                
                if isinstance(content, dict):
                    content = content.get('response', str(content))
                elif not isinstance(content, str):
                    content = str(content)
                
                if role == 'assistant':
                    role = 'model'
                    
                if content and content.strip():
                    contents.append(
                        types.Content(
                            role=role,
                            parts=[types.Part.from_text(text=content.strip())]
                        )
                    )
        
        # Add current user message with image
        parts = [types.Part.from_text(text=request.message)]
        
        if request.image_data:
            # Add image to the conversation
            try:
                image_part = types.Part(
                    inline_data=types.Blob(
                        mime_type="image/jpeg",
                        data=base64.b64decode(request.image_data)
                    )
                )
                parts.append(image_part)
            except Exception as e:
                logger.error(f"Error adding image to conversation: {e}")
                # Continue without image if there's an error
            logger.info("🖼️ Added image to conversation context")
        
        contents.append(
            types.Content(
                role="user",
                parts=parts
            )
        )
        
        # Enhanced generation config
        generate_content_config = types.GenerateContentConfig(
            temperature=request.temperature,
            top_p=0.95,
            max_output_tokens=request.max_tokens,
            safety_settings=[
                types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
                types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
                types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
                types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF")
            ],
        )
        
        logger.info(f"🚀 Calling model with image: {model}")
        
        # Generate response
        response_text = ""
        chunk_count = 0
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            if chunk.text:
                response_text += chunk.text
                chunk_count += 1
        
        # Process response
        cleaned_response = clean_response_text(response_text)
        directive_info = process_response_directives(cleaned_response)
        
        logger.info(f"✅ Image chat response: {chunk_count} chunks, {len(response_text)} chars")
        logger.info(f"🎭 Phase: {current_phase}, Images: {directive_info['contains_images']}, Actions: {directive_info['contains_actions']}")
        
        return ChatResponse(
            response=cleaned_response,
            model_used=f"vertex-ai-{model}",
            phase=current_phase.value,
            contains_images=directive_info['contains_images'],
            contains_actions=directive_info['contains_actions']
        )
        
    except Exception as e:
        logger.error(f"❌ Error in chat with image: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate response: {str(e)}"
        )

@app.post("/test-chat", response_model=ChatResponse)
async def test_chat_endpoint(request: ChatRequest):
    """Test chat endpoint using regular Gemini API"""
    logger.info(f"📨 Testing with regular Gemini API: {request.message[:50]}...")
    
    try:
        # Create a client for regular Gemini API
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise HTTPException(status_code=500, detail="GEMINI_API_KEY not found")
            
        test_client = genai.Client(api_key=gemini_api_key)
        
        # Create content for the request
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=request.message)]
            )
        ]
        
        # Configure generation parameters
        config = types.GenerateContentConfig(
            temperature=request.temperature,
            max_output_tokens=request.max_tokens
        )
        
        # Generate content using regular Gemini
        response = test_client.models.generate_content(
            model="gemini-1.5-flash",
            contents=contents,
            config=config
        )
        
        # Extract and clean the response text
        response_text = response.text if response.text else "No response generated"
        cleaned_response = clean_response_text(response_text)
        
        logger.info(f"✅ Generated test response: {len(response_text)} chars -> {len(cleaned_response)} chars (cleaned)")
        
        return ChatResponse(
            response=cleaned_response,
            model_used="gemini-1.5-flash (test)"
        )
        
    except Exception as e:
        logger.error(f"❌ Error in test endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error in test endpoint: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 