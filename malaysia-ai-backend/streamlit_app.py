"""
Streamlit Frontend for AI Chat Application
A modern, responsive chat interface that connects to the FastAPI backend
"""

import streamlit as st
import requests
import json
import re
import uuid
from typing import List, Dict, Any
import time

# Load environment variables
from dotenv import load_dotenv
load_dotenv(override=True)

# Configure Streamlit page
st.set_page_config(
    page_title="🇲🇾 Aiman - Malaysia Travel Concierge",
    page_icon="🇲🇾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Backend configuration - works both locally and on Render
import os
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
BACKEND_URL = API_BASE_URL

# Enhanced CSS for modern UI with integrated upload
st.markdown("""
<style>
    /* Main container */
    .main {
        padding-block-start: 1rem;
        max-inline-size: 1200px;
        margin: 0 auto;
    }
    
    /* Chat messages styling */
    .stChatMessage {
        padding: 1.2rem;
        border-radius: 16px;
        margin: 1rem 0;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* User message */
    .stChatMessage[data-testid="user-message"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        margin-inline-start: 20%;
    }
    
    /* Assistant message */
    .stChatMessage[data-testid="assistant-message"] {
        background: #f8f9fa;
        border-inline-start: 4px solid #28a745;
        margin-inline-end: 20%;
    }
    
    /* Header styling */
    .header-container {
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        margin-block-end: 2rem;
        color: white;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .header-container h1 {
        font-size: 2.5rem;
        margin-block-end: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .header-container p {
        font-size: 1.2rem;
        opacity: 0.9;
        margin-block-end: 0;
    }
    
    /* Enhanced Chat Input Area */
    .chat-input-container {
        position: fixed !important;
        inset-block-end: 0 !important;
        inset-inline-start: 0 !important;
        inset-inline-end: 0 !important;
        background: white !important;
        border-block-start: 2px solid #e0e0e0 !important;
        padding: 1.5rem !important;
        box-shadow: 0 -4px 20px rgba(0,0,0,0.1) !important;
        z-index: 999999 !important;
        backdrop-filter: blur(10px) !important;
    }
    
    /* Chat input wrapper with integrated upload */
    .input-wrapper {
        max-inline-size: 1200px;
        margin: 0 auto;
        display: flex;
        align-items: flex-end;
        gap: 1rem;
        background: #f8f9fa;
        border: 2px solid #e0e0e0;
        border-radius: 20px;
        padding: 0.8rem 1.2rem;
        transition: all 0.3s ease;
        position: relative;
    }
    
    .input-wrapper:focus-within {
        border-color: #667eea;
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.2);
    }
    
    /* Image preview in chat input */
    .image-preview-compact {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 0.5rem;
        margin-inline-end: 0.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        animation: slideIn 0.3s ease;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .image-preview-compact img {
        inline-size: 40px;
        block-size: 40px;
        object-fit: cover;
        border-radius: 8px;
    }
    
    .image-preview-compact .remove-btn {
        background: #ff4757;
        color: white;
        border: none;
        border-radius: 50%;
        inline-size: 20px;
        block-size: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        font-size: 12px;
        transition: all 0.2s ease;
    }
    
    .image-preview-compact .remove-btn:hover {
        background: #ff3838;
        transform: scale(1.1);
    }
    
    /* Upload button integrated in input */
    .upload-btn-integrated {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        border: none;
        border-radius: 12px;
        inline-size: 44px;
        block-size: 44px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.3s ease;
        margin-inline-start: 0.5rem;
        box-shadow: 0 2px 8px rgba(40, 167, 69, 0.3);
    }
    
    .upload-btn-integrated:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(40, 167, 69, 0.4);
    }
    
    .upload-btn-integrated svg {
        inline-size: 20px;
        block-size: 20px;
        fill: white;
    }
    
    /* Send button styling */
    .send-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 12px;
        inline-size: 44px;
        block-size: 44px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }
    
    .send-btn:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    .send-btn svg {
        inline-size: 20px;
        block-size: 20px;
        fill: white;
    }
    
    /* Main content area with bottom padding */
    .main-content {
        padding-block-end: 150px !important;
        min-block-size: calc(100vh - 150px) !important;
    }
    
    /* Chat history container */
    .chat-history {
        margin-block-end: 120px !important;
        max-block-size: calc(100vh - 200px) !important;
        overflow-y: auto !important;
    }
    
    /* Hide default Streamlit file uploader */
    .stFileUploader {
        display: none !important;
    }
    
    /* Enhanced image preview in chat */
    .chat-image-preview {
        background: #f8f9fa;
        border: 2px dashed #28a745;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        text-align: center;
        animation: fadeIn 0.5s ease;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: scale(0.95); }
        to { opacity: 1; transform: scale(1); }
    }
    
    .chat-image-preview img {
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        max-block-size: 200px;
    }
    
    /* Status indicators */
    .status-success {
        color: #28a745;
        font-weight: 600;
    }
    
    .status-error {
        color: #dc3545;
        font-weight: 600;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: #f8f9fa;
    }
    
    /* Action cards */
    .action-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: start;
        inline-size: 100%;
    }
    
    .action-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    /* Welcome card */
    .welcome-card {
        background: linear-gradient(135deg, #e8f5e8 0%, #f0f8f0 100%);
        border: 2px solid #28a745;
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
        text-align: center;
        animation: slideUp 0.6s ease;
    }
    
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin-block-start: 1.5rem;
    }
    
    .feature-item {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .feature-item:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.15);
    }
    
    /* Responsive design */
    @media (max-inline-size: 768px) {
        .stChatMessage[data-testid="user-message"] {
            margin-inline-start: 5%;
        }
        
        .stChatMessage[data-testid="assistant-message"] {
            margin-inline-end: 5%;
        }
        
        .header-container {
            padding: 2rem 1rem;
        }
        
        .header-container h1 {
            font-size: 2rem;
        }
        
        .input-wrapper {
            margin: 0 1rem;
        }
        
        .feature-grid {
            grid-template-columns: 1fr;
        }
    }
    
    /* Typing indicator */
    .typing-indicator {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: #666;
        font-style: italic;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 12px;
        margin: 0.5rem 0;
    }
    
    .typing-dots {
        display: flex;
        gap: 2px;
    }
    
    .typing-dots span {
        inline-size: 6px;
        block-size: 6px;
        background: #28a745;
        border-radius: 50%;
        animation: bounce 1.4s infinite ease-in-out both;
    }
    
    .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
    .typing-dots span:nth-child(2) { animation-delay: -0.16s; }
    
    @keyframes bounce {
        0%, 80%, 100% { transform: scale(0); }
        40% { transform: scale(1); }
    }
</style>

<script>
// More aggressive approach to keep chat input fixed
function forceFixedChatInput() {
    // Find all possible chat input elements
    const selectors = [
        '[data-testid="stChatInput"]',
        '.stChatInput',
        '.stChatInputContainer', 
        '[data-testid="chatInput"]',
        'div[data-testid="stChatInput"]',
        'div.stChatInput',
        'section[data-testid="stChatInput"]'
    ];
    
    selectors.forEach(selector => {
        const elements = document.querySelectorAll(selector);
        elements.forEach(element => {
            if (element) {
                // Force fixed position with highest priority
                element.style.setProperty('position', 'fixed', 'important');
                element.style.setProperty('bottom', '0', 'important');
                element.style.setProperty('left', '0', 'important');
                element.style.setProperty('right', '0', 'important');
                element.style.setProperty('z-index', '999999', 'important');
                element.style.setProperty('background-color', 'white', 'important');
                element.style.setProperty('border-top', '1px solid #e0e0e0', 'important');
                element.style.setProperty('padding', '1rem', 'important');
                element.style.setProperty('box-shadow', '0 -2px 10px rgba(0,0,0,0.1)', 'important');
                
                // Find parent containers and fix them too
                let parent = element.parentElement;
                while (parent && parent !== document.body) {
                    if (parent.tagName === 'DIV' || parent.tagName === 'SECTION') {
                        parent.style.setProperty('position', 'fixed', 'important');
                        parent.style.setProperty('bottom', '0', 'important');
                        parent.style.setProperty('left', '0', 'important');
                        parent.style.setProperty('right', '0', 'important');
                        parent.style.setProperty('z-index', '999999', 'important');
                        parent.style.setProperty('background-color', 'white', 'important');
                        break;
                    }
                    parent = parent.parentElement;
                }
            }
        });
    });
}

// Disable Streamlit's auto-scroll behavior
function disableAutoScroll() {
    // Override scroll-related functions
    const originalScrollTo = window.scrollTo;
    const originalScrollIntoView = Element.prototype.scrollIntoView;
    
    window.scrollTo = function(x, y) {
        // Allow scrolling but prevent scrolling to bottom during AI responses
        if (y > document.body.scrollHeight - window.innerHeight - 100) {
            return; // Don't scroll to bottom
        }
        return originalScrollTo.call(this, x, y);
    };
    
    Element.prototype.scrollIntoView = function(options) {
        // Disable scrollIntoView for chat elements
        if (this.closest('[data-testid="stChatMessage"]') || 
            this.closest('.stChatMessage') ||
            this.closest('[data-testid="stChatInput"]')) {
            return;
        }
        return originalScrollIntoView.call(this, options);
    };
}

// Use MutationObserver to watch for DOM changes
function setupMutationObserver() {
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                // Re-apply fixed positioning after DOM changes
                setTimeout(forceFixedChatInput, 10);
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
}

// Initialize everything
function initializeFixedChat() {
    disableAutoScroll();
    forceFixedChatInput();
    setupMutationObserver();
}

// Run immediately and on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeFixedChat);
} else {
    initializeFixedChat();
}

// Aggressive checking every 50ms
setInterval(forceFixedChatInput, 50);

// Prevent any scrolling that might interfere
document.addEventListener('scroll', function(e) {
    forceFixedChatInput();
});

// Additional check when window resizes
window.addEventListener('resize', function() {
    forceFixedChatInput();
});
</script>
""", unsafe_allow_html=True)

def check_backend_health() -> bool:
    """Check if the backend is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def clean_display_text(text: str) -> str:
    """Optimized text cleaning for better display"""
    if not text:
        return text
    
    # Faster regex processing (import moved to top)
    cleaned = re.sub(r' +', ' ', text)
    cleaned = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned)
    
    return cleaned.strip()

def process_aiman_directives(response_text: str) -> tuple:
    """Process Aiman's directives for UI enhancement (V7.0 compatible)"""
    
    # Extract new SEARCH_IMAGE directives (V7.0 format)
    search_image_pattern = r'\[SEARCH_IMAGE:\s*["\']([^"\']+)["\']\s*\]'
    search_image_queries = re.findall(search_image_pattern, response_text)
    
    # Extract legacy IMAGE RETRIEVE directives for backward compatibility
    image_retrieve_pattern = r'\[IMAGE:\s*RETRIEVE:\s*["\']([^"\']+)["\']\s*\]'
    image_queries = re.findall(image_retrieve_pattern, response_text)
    
    # Combine both formats into a single list
    all_image_queries = search_image_queries + image_queries
    
    # Extract regular IMAGE directives (fallback)
    image_pattern = r'\[IMAGE:\s*([^\]]+)\]'
    regular_images = re.findall(image_pattern, response_text)
    
    # Filter out RETRIEVE and SEARCH patterns from regular images
    regular_images = [img for img in regular_images if not img.startswith('RETRIEVE:') and not img.startswith('SEARCH_IMAGE:')]
    
    # Extract ACTION directives
    action_pattern = r'\[ACTION:\s*([^,]+),\s*([^\]]+)\]'
    actions = re.findall(action_pattern, response_text)
    
    # Clean response text (remove all directives for display)
    clean_text = re.sub(search_image_pattern, '', response_text)
    clean_text = re.sub(image_retrieve_pattern, '', clean_text)
    clean_text = re.sub(image_pattern, '', clean_text)
    clean_text = re.sub(action_pattern, '', clean_text)
    clean_text = clean_display_text(clean_text)
    
    return clean_text, regular_images, all_image_queries, actions

@st.cache_data(ttl=300)  # Cache for 5 minutes
def retrieve_images_for_queries(image_queries: List[str]) -> List[str]:
    """Retrieve images for the given search queries using the backend API - with caching"""
    retrieved_urls = []
    
    for query in image_queries:
        # Check cache first
        cache_key = f"image_query_{query}"
        if cache_key in st.session_state:
            cached_data = st.session_state[cache_key]
            retrieved_urls.append(cached_data["url"])
            continue
            
        try:
            response = requests.post(
                f"{BACKEND_URL}/image-search",
                json={"query": query, "max_results": 1},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                images = data.get("images", [])
                if images:
                    image_info = images[0]
                    retrieved_urls.append(image_info["url"])
                    # Store complete image metadata for attribution
                    st.session_state[cache_key] = {
                        "url": image_info["url"],
                        "source": image_info.get("source", ""),
                        "photographer_name": image_info.get("photographer_name", ""),
                        "photographer_url": image_info.get("photographer_url", ""),
                        "download_url": image_info.get("download_url", ""),
                        "title": image_info.get("title", ""),
                        "description": image_info.get("description", "")
                    }
            
        except Exception as e:
            st.error(f"Failed to retrieve image for: {query}")
            continue
    
    return retrieved_urls

def upload_and_analyze_image(uploaded_file, user_message: str = "What do you see in this image?") -> Dict[str, Any]:
    """Upload image to backend for analysis"""
    try:
        # Prepare files for upload
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        data = {"message": user_message}
        
        response = requests.post(
            f"{BACKEND_URL}/upload-image",
            files=files,
            data=data,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Image upload failed: {response.status_code}")
            return None
            
    except Exception as e:
        st.error(f"Error uploading image: {str(e)}")
        return None

def send_message_with_image(prompt: str, history: List[Dict[str, str]], image_data: str = None, session_id: str = None) -> Dict[str, Any]:
    """Send message with optional image to backend - with retry mechanism"""
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            # Get user-configured parameters or use defaults
            max_tokens = st.session_state.get("max_tokens", 8192)
            temperature = st.session_state.get("temperature", 0.7)
            
            # Enhanced payload with image support
            payload = {
                "message": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "conversation_history": history,
                "user_session_id": session_id or str(uuid.uuid4())
            }
            
            # Add image data if provided
            if image_data:
                payload["image_data"] = image_data
                endpoint = "/chat-with-image"
            else:
                endpoint = "/chat"
            
            response = requests.post(
                f"{BACKEND_URL}{endpoint}",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                response_data = response.json()
                raw_response = response_data.get("response", "❌ No response from AI model")
                model_used = response_data.get("model_used", "unknown")
                phase = response_data.get("phase", "unknown")
                contains_images = response_data.get("contains_images", False)
                contains_actions = response_data.get("contains_actions", False)
                search_image_queries = response_data.get("search_image_queries", [])
                action_items = response_data.get("action_items", [])
                
                # Store response info for debugging
                st.session_state["last_response_info"] = {
                    "length": len(raw_response),
                    "model": model_used,
                    "phase": phase,
                    "contains_images": contains_images,
                    "contains_actions": contains_actions,
                    "search_queries": len(search_image_queries),
                    "actions": len(action_items),
                    "temp": temperature,
                    "max_tokens": max_tokens,
                    "had_image": image_data is not None,
                    "attempts": attempt + 1
                }
                
                return {
                    "response": raw_response,
                    "phase": phase,
                    "contains_images": contains_images,
                    "contains_actions": contains_actions,
                    "search_image_queries": search_image_queries,
                    "action_items": action_items,
                    "model_used": model_used
                }
            else:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                    
                error_detail = response.text
                try:
                    error_json = response.json()
                    if "detail" in error_json:
                        error_detail = str(error_json["detail"])
                except:
                    pass
                return {"response": f"❌ Error: {response.status_code} - {error_detail}", "phase": "error"}
                
        except requests.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            return {"response": f"❌ Connection error after {max_retries} attempts: {str(e)}", "phase": "error"}

def fetch_search_images(queries: list) -> dict:
    """Fetch images for search queries from backend"""
    try:
        all_images = {}
        for query in queries:
            response = requests.post(
                f"{BACKEND_URL}/image-search",
                json={"query": query, "max_results": 1},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                all_images[query] = data.get("images", [])
            else:
                all_images[query] = []
        return all_images
    except Exception as e:
        st.error(f"Image search failed: {e}")
        return {}

def render_search_images(search_queries: list):
    """Render search images in modern layout"""
    if not search_queries:
        return
        
    st.markdown("### 🖼️ Related Images")
    
    # Fetch images
    images_data = fetch_search_images(search_queries)
    
    if not any(images_data.values()):
        st.info("No related images found")
        return
    
    # Display images in columns
    for query, images in images_data.items():
        if images:
            st.markdown(f"**{query}**")
            # Show only 1 image per query with smaller size
            if images:
                st.image(
                    images[0]["url"], 
                    caption=images[0].get("title", "Malaysia Tourism"),
                    width=300  # Set fixed width to make images smaller
                )

def render_action_card(action_type: str, action_name: str):
    """Render interactive action cards for bookable items (development preview)"""
    
    # Normalize action type
    action_type = action_type.strip().title()
    action_name = action_name.strip()
    
    # Show development preview cards with realistic expectations
    if action_type == "Hotel":
        st.info(f"🏨 **Hotel Option Identified**: {action_name}")
        if st.button(f"Research {action_name}", key=f"hotel_{hash(action_name)}"):
            st.success("💡 Great choice! Consider researching this hotel on booking platforms.")
            
    elif action_type == "Activity":
        st.info(f"🎯 **Activity Suggestion**: {action_name}")
        if st.button(f"Learn More About {action_name}", key=f"activity_{hash(action_name)}"):
            st.success("🎯 This looks like a fantastic experience to add to your itinerary!")
            
    elif action_type == "Flight":
        st.info(f"✈️ **Flight Destination**: {action_name}")
        if st.button(f"Research Flights to {action_name}", key=f"flight_{hash(action_name)}"):
            st.success("✈️ Check flight comparison sites for the best deals to this destination!")

def send_message(prompt: str, history: List[Dict[str, str]], session_id: str = None) -> Dict[str, Any]:
    """Send message to backend and get response with Aiman persona features"""
    try:
        # Get user-configured parameters or use defaults
        max_tokens = st.session_state.get("max_tokens", 8192)
        temperature = st.session_state.get("temperature", 0.7)
        
        # Enhanced payload with Aiman persona features
        payload = {
            "message": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "conversation_history": history,
            "user_session_id": session_id or str(uuid.uuid4())
        }
        
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json=payload,
            timeout=60  # Increased timeout for longer responses
        )
        
        if response.status_code == 200:
            response_data = response.json()
            raw_response = response_data.get("response", "❌ No response from AI model")
            model_used = response_data.get("model_used", "unknown")
            phase = response_data.get("phase", "unknown")
            contains_images = response_data.get("contains_images", False)
            contains_actions = response_data.get("contains_actions", False)
            
            # Store response info for debugging
            st.session_state["last_response_info"] = {
                "length": len(raw_response),
                "model": model_used,
                "phase": phase,
                "contains_images": contains_images,
                "contains_actions": contains_actions,
                "temp": temperature,
                "max_tokens": max_tokens
            }
            
            return {
                "response": raw_response,
                "phase": phase,
                "contains_images": contains_images,
                "contains_actions": contains_actions,
                "model_used": model_used
            }
        else:
            error_detail = response.text
            try:
                error_json = response.json()
                if "detail" in error_json:
                    error_detail = str(error_json["detail"])
            except:
                pass
            return {"response": f"❌ Error: {response.status_code} - {error_detail}", "phase": "error"}
            
    except requests.RequestException as e:
        return {"response": f"❌ Connection error: {str(e)}", "phase": "error"}

def main():
    # Modern Header
    st.markdown("""
    <div class="header-container">
        <h1>🇲🇾 Aiman</h1>
        <p>Your AI-Powered Malaysia Travel Concierge</p>
        <div style="margin-block-start: 1rem; font-size: 0.9rem; opacity: 0.8;">
            ✨ Discover Malaysia • 🏖️ Plan Your Journey • 📸 Get Recommendations
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📊 System Status")
        
        # Check backend status
        if check_backend_health():
            st.markdown('<p class="status-success">✅ Backend: Connected</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="status-error">❌ Backend: Disconnected</p>', unsafe_allow_html=True)
            st.error("Please ensure the backend server is running on http://localhost:8000")
            st.stop()
        
        st.markdown("### ⚙️ Settings")
        
        # Set optimal defaults for Aiman
        st.session_state["max_tokens"] = 8192
        st.session_state["temperature"] = 0.7
        
        # Clear chat button
        if st.button("🗑️ Clear Chat History", type="secondary"):
            st.session_state.messages = []
            st.rerun()
        
        # Model info with endpoint details
        st.markdown("### 🧠 Model Info")
        st.info("""
        **Model**: Fine-tuned Gemini (TourismMalaysia)  
        **Provider**: Google Vertex AI  
        **Endpoint**: 1393226367927058432  
        **Features**: Enhanced tourism knowledge, Multi-turn conversation, Aiman Persona
        """)
        
        # Performance monitoring
        st.markdown("### ⚡ Performance")
        if "last_response_info" in st.session_state:
            info = st.session_state["last_response_info"]
            perf_data = {
                "Response Length": f"{info.get('length', 0)} chars",
                "API Attempts": f"{info.get('attempts', 1)} tries",
                "Temperature": f"{info.get('temp', 0.7)}",
                "Max Tokens": f"{info.get('max_tokens', 8192)}"
            }
            st.json(perf_data)
        
        # Aiman conversation info
        if "last_response_info" in st.session_state:
            info = st.session_state["last_response_info"]
            st.markdown("### 🎭 Aiman Status")
            phase_emoji = {
                "greeting": "👋",
                "scoping": "🎯", 
                "ideation": "💡",
                "consolidation": "✨"
            }
            current_phase = info.get('phase', 'unknown')
            
            st.json({
                "Conversation Phase": f"{phase_emoji.get(current_phase, '❓')} {current_phase.title()}",
                "Images Available": "🖼️ Yes" if info.get('contains_images') else "❌ No",
                "Actions Available": "🎬 Yes" if info.get('contains_actions') else "❌ No",
                "Response Length": f"{info['length']} chars"
            })
        
        # Enhanced instructions
        st.markdown("### 💡 How to Use")
        st.markdown("""
        **💬 Chat Features:**
        • Type messages in the chat input below
        • Upload images using the 📸 button
        • Get instant AI-powered recommendations
        • Continue conversations naturally
        
        **🎯 Special Commands:**
        • Ask about destinations, food, culture
        • Upload travel photos for analysis
        • Request itinerary suggestions
        • Get local tips and recommendations
        """)

    # Initialize chat history and session
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    # Chat section with modern styling - wrapped in main content
    st.markdown("""
    <div class="main-content">
    <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 16px; margin: 1rem 0; border-inline-start: 4px solid #28a745;">
        <h3 style="margin: 0 0 0.5rem 0; color: #28a745; display: flex; align-items: center; gap: 0.5rem;">
            💬 Chat with Aiman
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced intro message with inline styles (fixed)
    if len(st.session_state.messages) == 0:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #e8f5e8 0%, #f0f8f0 100%);
            border: 2px solid #28a745;
            border-radius: 20px;
            padding: 2rem;
            margin: 2rem 0;
            text-align: center;
        ">
            <div style="font-size: 3rem; margin-block-end: 1rem;">👋</div>
            <h2 style="color: #28a745; margin-block-end: 1rem; font-weight: 600;">Selamat Datang! Welcome to Aiman</h2>
            <p style="color: #666; margin-block-end: 2rem; font-size: 1.1rem;">Your AI-powered Malaysia travel concierge is ready to help you discover the beauty of Malaysia</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature cards using Streamlit columns
        st.markdown("### ✨ What can Aiman do for you?")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style="
                background: white;
                padding: 1.5rem;
                border-radius: 16px;
                text-align: center;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                block-size: 200px;
                display: flex;
                flex-direction: column;
                justify-content: center;
            ">
                <div style="font-size: 2.5rem; color: #28a745; margin-block-end: 1rem;">💬</div>
                <h4 style="color: #333; margin-block-end: 0.5rem;">Ask Questions</h4>
                <p style="color: #666; font-size: 0.9rem;">Get personalized travel recommendations and local insights</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="
                background: white;
                padding: 1.5rem;
                border-radius: 16px;
                text-align: center;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                block-size: 200px;
                display: flex;
                flex-direction: column;
                justify-content: center;
            ">
                <div style="font-size: 2.5rem; color: #28a745; margin-block-end: 1rem;">📸</div>
                <h4 style="color: #333; margin-block-end: 0.5rem;">Upload Images</h4>
                <p style="color: #666; font-size: 0.9rem;">Share your travel photos for instant analysis and tips</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="
                background: white;
                padding: 1.5rem;
                border-radius: 16px;
                text-align: center;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                block-size: 200px;
                display: flex;
                flex-direction: column;
                justify-content: center;
            ">
                <div style="font-size: 2.5rem; color: #28a745; margin-block-end: 1rem;">🎯</div>
                <h4 style="color: #333; margin-block-end: 0.5rem;">Get Recommendations</h4>
                <p style="color: #666; font-size: 0.9rem;">Discover hidden gems and plan your perfect itinerary</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Pro tip
        st.info("💡 **Pro Tip**: Try uploading a photo and asking \"What can you tell me about this place?\"")
        st.markdown("---")
    
    # Chat container with chat history styling
    st.markdown('<div class="chat-history">', unsafe_allow_html=True)
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                if message["role"] == "assistant" and isinstance(message.get("content"), dict):
                    # Handle enhanced Aiman responses
                    response_data = message["content"]
                    clean_text, regular_images, image_queries, actions = process_aiman_directives(response_data.get("response", ""))
                    
                    # Display cleaned response text
                    st.markdown(clean_text)
                    
                    # Display regular images if available (fallback)
                    if regular_images:
                        for img_url in regular_images:
                            try:
                                st.image(img_url.strip(), caption="📸 Recommended by Aiman", width=300)
                            except:
                                # Gracefully handle broken images - don't show broken links
                                pass
                    
                    # Retrieve and display intelligent images
                    if image_queries:
                        st.markdown("**📸 Aiman's Visual Recommendations:**")
                        with st.spinner("🔍 Finding perfect images for you..."):
                            retrieved_urls = retrieve_images_for_queries(image_queries)
                            
                        for i, url in enumerate(retrieved_urls):
                            try:
                                query = image_queries[i] if i < len(image_queries) else "Malaysia Tourism"
                                
                                # Get image metadata for attribution
                                image_data = st.session_state.get(f"image_query_{query}", {})
                                
                                # Display image
                                st.image(url, caption=f"📸 {query}", width=300)
                                
                                # Add proper Unsplash attribution if available
                                if image_data.get("source") == "Unsplash":
                                    photographer_name = image_data.get("photographer_name", "Unknown Photographer")
                                    photographer_url = image_data.get("photographer_url", "https://unsplash.com")
                                    
                                    st.caption(f"Photo by [{photographer_name}]({photographer_url}) on [Unsplash](https://unsplash.com)")
                                    
                                    # Track download for Unsplash compliance
                                    download_url = image_data.get("download_url")
                                    if download_url:
                                        try:
                                            requests.post(f"{BACKEND_URL}/track-image-download", json={"download_url": download_url}, timeout=5)
                                        except:
                                            pass  # Silent failure for tracking
                                            
                            except:
                                # Gracefully handle broken retrieved images
                                pass
                    
                    # Display action cards if available
                    if actions:
                        st.markdown("---")
                        st.markdown("**🎯 Available Actions:**")
                        for action_type, action_name in actions:
                            render_action_card(action_type, action_name)
                else:
                    # Regular text content
                    content = message["content"] if isinstance(message["content"], str) else str(message["content"])
                    st.markdown(content)

    # Old image upload section removed - now integrated into chat flow above
    
    # Close chat history div
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Close main content div  
    st.markdown('</div>', unsafe_allow_html=True)

    # Modern chat interface (similar to ChatGPT/Claude)
    st.markdown("---")
    
    # Beautiful integrated chat input area (restored)
    st.markdown("""
    <div class="chat-input-container">
        <div class="input-wrapper">
            <div id="input-content-area" style="flex: 1; display: flex; flex-direction: column; gap: 0.5rem;">
                <!-- Image preview area -->
                <div id="image-preview-area"></div>
                <!-- Chat input will be placed here -->
                <div id="chat-input-area" style="min-block-size: 48px; display: flex; align-items: center;">
                    <div id="chat-placeholder" style="color: #999; font-size: 14px; flex: 1; padding: 12px;">
                        ✨ Ask Aiman about Malaysia travel, upload an image, or get recommendations...
                    </div>
                </div>
            </div>
            <div style="display: flex; gap: 0.5rem; align-items: flex-end;">
                <button class="upload-btn-integrated" id="upload-trigger" title="Upload Image">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2z"/>
                        <circle cx="9" cy="9" r="2"/>
                        <path d="M21 15l-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/>
                    </svg>
                </button>
                                 <button class="send-btn" id="send-trigger" title="Send Message">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M22 2L11 13"/>
                        <path d="M22 2L15 22L11 13L2 9L22 2Z"/>
                    </svg>
                </button>
            </div>
        </div>
    </div>
    
    """, unsafe_allow_html=True)
    
    # Hidden Streamlit components (positioned off-screen but functional)
    st.markdown("""
    <div style="position: absolute; inset-inline-start: -9999px; inset-block-start: -9999px; opacity: 0; pointer-events: none;">
    """, unsafe_allow_html=True)
    
    # Hidden but functional file uploader
    uploaded_file = st.file_uploader(
        "Upload Image",
        type=['png', 'jpg', 'jpeg', 'webp', 'gif'],
        key="hidden_uploader",
        label_visibility="collapsed"
    )
    
    # Hidden but functional chat input
    prompt = st.chat_input(
        "Type message...",
        key="hidden_chat"
    )
    
    st.markdown("</div>", unsafe_allow_html=True)
    
        # Enhanced styling for beautiful integrated interface
    st.markdown("""
    <style>
    /* Enhanced Chat Input Area */
    .chat-input-container {
        position: fixed !important;
        inset-block-end: 0 !important;
        inset-inline-start: 0 !important;
        inset-inline-end: 0 !important;
        background: white !important;
        border-block-start: 2px solid #e0e0e0 !important;
        padding: 1.5rem !important;
        box-shadow: 0 -4px 20px rgba(0,0,0,0.1) !important;
        z-index: 999999 !important;
        backdrop-filter: blur(10px) !important;
    }
    
    /* Chat input wrapper with integrated upload */
    .input-wrapper {
        max-inline-size: 1200px;
        margin: 0 auto;
        display: flex;
        align-items: flex-end;
        gap: 1rem;
        background: #f8f9fa;
        border: 2px solid #e0e0e0;
        border-radius: 20px;
        padding: 0.8rem 1.2rem;
        transition: all 0.3s ease;
        position: relative;
    }
    
    .input-wrapper:hover {
        border-color: #28a745;
        box-shadow: 0 0 25px rgba(40, 167, 69, 0.15);
    }
    
    .input-wrapper:focus-within {
        border-color: #667eea;
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.2);
    }
    
    /* Image preview in chat input */
    .image-preview-compact {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 0.5rem;
        margin-block-end: 0.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        animation: slideIn 0.3s ease;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .image-preview-compact img {
        inline-size: 40px;
        block-size: 40px;
        object-fit: cover;
        border-radius: 8px;
    }
    
    .image-preview-compact .remove-btn {
        background: #ff4757;
        color: white;
        border: none;
        border-radius: 50%;
        inline-size: 20px;
        block-size: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        font-size: 12px;
        transition: all 0.2s ease;
    }
    
    .image-preview-compact .remove-btn:hover {
        background: #ff3838;
        transform: scale(1.1);
    }
    
    /* Upload button integrated in input */
    .upload-btn-integrated {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        border: none;
        border-radius: 12px;
        inline-size: 44px;
        block-size: 44px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(40, 167, 69, 0.3);
    }
    
    .upload-btn-integrated:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(40, 167, 69, 0.4);
    }
    
    .upload-btn-integrated svg {
        inline-size: 20px;
        block-size: 20px;
        fill: white;
    }
    
    /* Send button styling */
    .send-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 12px;
        inline-size: 44px;
        block-size: 44px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }
    
    .send-btn:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    .send-btn svg {
        inline-size: 20px;
        block-size: 20px;
        fill: white;
    }
    
    /* Main content area with bottom padding */
    .main-content {
        padding-block-end: 150px !important;
        min-block-size: calc(100vh - 150px) !important;
    }
    
    /* Chat history container */
    .chat-history {
        margin-block-end: 120px !important;
        max-block-size: calc(100vh - 200px) !important;
        overflow-y: auto !important;
    }
    
    /* Interactive input area */
    #chat-input-area {
        cursor: text;
        border-radius: 8px;
        transition: all 0.2s ease;
    }
    
    #chat-input-area:hover {
        background: rgba(40, 167, 69, 0.05);
    }
    
    #chat-placeholder {
        transition: all 0.2s ease;
    }
    
    /* Input overlay styling */
    .input-overlay {
        inline-size: 100%;
        min-block-size: 40px;
        max-block-size: 120px;
        border: none;
        background: transparent;
        resize: none;
        outline: none;
        font-family: inherit;
        font-size: 14px;
        color: #333;
        padding: 12px;
        border-radius: 8px;
    }
    
    /* Enhanced focus states */
    .upload-btn-integrated:focus,
    .send-btn:focus {
        outline: 3px solid rgba(102, 126, 234, 0.3);
        outline-offset: 2px;
    }
    
    /* Responsive design */
    @media (max-inline-size: 768px) {
        .input-wrapper {
            margin: 0 1rem;
        }
        
        .chat-input-container {
            padding: 1rem !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Simple JavaScript for basic functionality
    st.markdown("""
    <script>
    // Basic functionality only
    console.log('Aiman chat interface loaded');
        
        // Debug function
        window.debug = function(msg) {
            if (window.debugMode) {
                console.log('[AIMAN-DEBUG]', msg);
                var debugArea = document.getElementById('debug-area');
                if (debugArea) {
                    var timeStr = new Date().toLocaleTimeString();
                    debugArea.innerHTML += '<div style="margin: 2px 0; font-size: 10px;">' + timeStr + ': ' + msg + '</div>';
                    debugArea.scrollTop = debugArea.scrollHeight;
                    
                    // Limit debug lines
                    var lines = debugArea.querySelectorAll('div');
                    if (lines.length > 20) {
                        lines[0].remove();
                    }
                }
            }
        };
    
        // Main initialization function
        window.initializeInterface = function() {
            debug('Starting interface initialization...');
            
            // Find components
            var fileInput = document.querySelector('input[type="file"]');
            var chatInputs = document.querySelectorAll('input, textarea');
            var chatInput = null;
            
            // Find chat input
            for (var i = 0; i < chatInputs.length; i++) {
                var input = chatInputs[i];
                if (input.placeholder && input.placeholder.includes('Type message')) {
                    chatInput = input;
                    break;
                }
            }
            
            debug('Found components: file=' + (fileInput ? 'YES' : 'NO') + ', chat=' + (chatInput ? 'YES' : 'NO'));
            
            // Setup upload button
            var uploadBtn = document.getElementById('upload-trigger');
            if (uploadBtn && fileInput) {
                uploadBtn.onclick = function(e) {
                    e.preventDefault();
                    debug('Upload button clicked!');
                    fileInput.click();
                };
                debug('Upload button configured');
            } else {
                debug('Upload button setup failed');
            }
            
            // Setup send button
            var sendBtn = document.getElementById('send-trigger');
            if (sendBtn && chatInput) {
                sendBtn.onclick = function(e) {
                    e.preventDefault();
                    debug('Send button clicked!');
                    
                    if (window.currentMessage.trim()) {
                        chatInput.value = window.currentMessage;
                        
                        // Trigger enter key
                        var event = new KeyboardEvent('keydown', {
                            key: 'Enter',
                            keyCode: 13,
                            which: 13,
                            bubbles: true
                        });
                        chatInput.dispatchEvent(event);
                        
                        debug('Message sent: ' + window.currentMessage);
                        clearInput();
                    } else {
                        debug('No message to send');
                    }
                };
                debug('Send button configured');
            } else {
                debug('Send button setup failed');
            }
            
            // Setup input area
            var inputArea = document.getElementById('chat-input-area');
            var placeholder = document.getElementById('chat-placeholder');
            
            if (inputArea && placeholder) {
                inputArea.onclick = function() {
                    debug('Input area clicked');
                    createInputOverlay();
                };
                debug('Input area configured');
            }
            
            // Setup file input change
            if (fileInput) {
                fileInput.onchange = function(e) {
                    debug('File input changed');
                    var file = e.target.files[0];
                    if (file) {
                        debug('File selected: ' + file.name);
                        showImagePreview(file);
                    }
                };
                debug('File input change listener added');
            }
            
            window.initialized = true;
            debug('Interface initialization complete!');
        };
    
        // Create input overlay
        window.createInputOverlay = function() {
            var inputArea = document.getElementById('chat-input-area');
            var placeholder = document.getElementById('chat-placeholder');
            
            if (inputArea && placeholder && !document.getElementById('input-overlay')) {
                placeholder.style.display = 'none';
                
                var textarea = document.createElement('textarea');
                textarea.id = 'input-overlay';
                textarea.className = 'input-overlay';
                textarea.placeholder = 'Type your message...';
                textarea.value = window.currentMessage;
                
                inputArea.appendChild(textarea);
                textarea.focus();
                
                textarea.oninput = function() {
                    window.currentMessage = this.value;
                    debug('Message updated: ' + window.currentMessage);
                };
                
                textarea.onkeydown = function(e) {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        debug('Enter pressed, sending...');
                        document.getElementById('send-trigger').click();
                    }
                };
                
                textarea.onblur = function() {
                    if (!window.currentMessage.trim()) {
                        removeInputOverlay();
                    }
                };
                
                debug('Input overlay created');
            }
        };
        
        // Remove input overlay
        window.removeInputOverlay = function() {
            var overlay = document.getElementById('input-overlay');
            var placeholder = document.getElementById('chat-placeholder');
            
            if (overlay) {
                overlay.remove();
                debug('Input overlay removed');
            }
            if (placeholder) {
                placeholder.style.display = 'block';
                debug('Placeholder restored');
            }
        };
        
        // Show image preview
        window.showImagePreview = function(file) {
            debug('Showing image preview: ' + file.name);
            var previewArea = document.getElementById('image-preview-area');
            if (previewArea && file) {
                var reader = new FileReader();
                reader.onload = function(e) {
                    window.currentImage = file;
                    previewArea.innerHTML = 
                        '<div class="image-preview-compact">' +
                            '<img src="' + e.target.result + '" alt="Uploaded image">' +
                            '<div style="flex: 1;">' +
                                '<div style="font-weight: 500; font-size: 12px; color: #333;">' + file.name + '</div>' +
                                '<div style="font-size: 10px; color: #666;">Ready for analysis</div>' +
                            '</div>' +
                            '<button class="remove-btn" onclick="removeImagePreview()" title="Remove image">×</button>' +
                        '</div>';
                    debug('Image preview displayed');
                };
                reader.readAsDataURL(file);
            }
        };
        
        // Remove image preview
        window.removeImagePreview = function() {
            var previewArea = document.getElementById('image-preview-area');
            if (previewArea) {
                previewArea.innerHTML = '';
            }
            window.currentImage = null;
            
            var fileInput = document.querySelector('input[type="file"]');
            if (fileInput) {
                fileInput.value = '';
            }
            debug('Image preview removed');
        };
        
        // Clear input
        window.clearInput = function() {
            window.currentMessage = '';
            removeInputOverlay();
            removeImagePreview();
            debug('Input cleared');
        };
        
        // Test functions
        window.testButtons = function() {
            debug('=== TESTING BUTTONS ===');
            var uploadBtn = document.getElementById('upload-trigger');
            var sendBtn = document.getElementById('send-trigger');
            
            if (uploadBtn) {
                uploadBtn.style.background = 'red';
                debug('Upload button turned red');
            }
            if (sendBtn) {
                sendBtn.style.background = 'blue';
                debug('Send button turned blue');
            }
            
            return 'Test completed - check debug console';
        };
        
        window.forceClick = function() {
            debug('=== FORCE CLICKING ===');
            var uploadBtn = document.getElementById('upload-trigger');
            var sendBtn = document.getElementById('send-trigger');
            
            if (uploadBtn) {
                uploadBtn.click();
                debug('Upload clicked');
            }
            if (sendBtn) {
                sendBtn.click();
                debug('Send clicked');
            }
            
            return 'Force clicks completed';
        };
        
        // Initialize when page loads
        debug('JavaScript loaded, starting initialization...');
        
        // Wait for DOM and Streamlit to be ready
        function waitAndInit() {
            var attempts = 0;
            var maxAttempts = 50;
            
            var checkReady = function() {
                attempts++;
                var fileInput = document.querySelector('input[type="file"]');
                var uploadBtn = document.getElementById('upload-trigger');
                var sendBtn = document.getElementById('send-trigger');
                
                debug('Attempt ' + attempts + ': file=' + (fileInput ? 'YES' : 'NO') + 
                      ', upload=' + (uploadBtn ? 'YES' : 'NO') + 
                      ', send=' + (sendBtn ? 'YES' : 'NO'));
                
                if ((fileInput && uploadBtn && sendBtn) || attempts >= maxAttempts) {
                    debug('Components ready, initializing interface...');
                    initializeInterface();
                } else {
                    setTimeout(checkReady, 200);
                }
            };
            
            checkReady();
        }
        
        // Start initialization
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', waitAndInit);
        } else {
            waitAndInit();
        }
        
        // Periodic re-initialization
        setInterval(function() {
            var uploadBtn = document.getElementById('upload-trigger');
            var sendBtn = document.getElementById('send-trigger');
            
            if (uploadBtn && sendBtn && !window.initialized) {
                debug('Re-initializing...');
                initializeInterface();
            }
        }, 3000);
        
        debug('JavaScript initialization setup complete');
        console.log('AIMAN-JS: JavaScript loaded successfully! Functions available:', typeof window.testButtons, typeof window.forceClick);
        
        // Add functions to global scope for immediate testing
        window.testButtons = window.testButtons;
        window.forceClick = window.forceClick;
        window.debug = window.debug;
        
        // Immediate test to verify functions work
        setTimeout(function() {
            console.log('AIMAN-TEST: testButtons type:', typeof window.testButtons);
            console.log('AIMAN-TEST: forceClick type:', typeof window.forceClick);
            console.log('AIMAN-TEST: debug type:', typeof window.debug);
        }, 1000);
        
    // Simple test functions that should work immediately
    window.testButtons = function() {
        console.log('testButtons called!');
        return 'testButtons function works!';
    };
    
    window.forceClick = function() {
        console.log('forceClick called!');
        return 'forceClick function works!';
    };
    
    console.log('AIMAN-FINAL: All JavaScript functions loaded');
    console.log('AIMAN-TEST: testButtons available:', typeof window.testButtons);
    console.log('AIMAN-TEST: forceClick available:', typeof window.forceClick);
    </script>
    """, unsafe_allow_html=True)
    
    # Handle image upload 
    if uploaded_file is not None and uploaded_file != st.session_state.get("last_uploaded_file"):
        st.session_state["pending_image"] = uploaded_file
        st.session_state["image_uploaded"] = True
        st.session_state["last_uploaded_file"] = uploaded_file
        st.rerun()
    
    # Handle text message (with or without image)
    if prompt or (st.session_state.get("image_uploaded", False) and prompt == ""):
        # Check if we have a pending image
        has_image = st.session_state.get("pending_image") is not None
        
        if has_image:
            # Process message with image
            uploaded_file = st.session_state["pending_image"]
            
            # Add user message to chat history
            user_message = prompt if prompt else "What do you see in this image? Please provide Malaysia travel recommendations."
            st.session_state.messages.append({
                "role": "user", 
                "content": f"[Image uploaded: {uploaded_file.name}] {user_message}"
            })
            
            # Display user message with image in a beautiful chat bubble
            with st.chat_message("user"):
                st.markdown(user_message)
                # Enhanced image display in chat
                st.markdown("""
                <div class="chat-image-preview">
                    <p style="margin-block-end: 1rem; color: #28a745; font-weight: 600;">📸 Uploaded Image</p>
                </div>
                """, unsafe_allow_html=True)
                st.image(uploaded_file, width=250, caption=f"📷 {uploaded_file.name}")
            
            # Show typing indicator while processing
            with st.chat_message("assistant"):
                st.markdown("""
                <div class="typing-indicator">
                    <div class="typing-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                    <span>Aiman is analyzing your image...</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Process with image analysis
                import base64
                image_bytes = uploaded_file.getvalue()
                image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                
                # Get conversation history
                history = []
                for msg in st.session_state.messages[:-1]:
                    content = msg["content"]
                    if isinstance(content, dict):
                        content = content.get("response", str(content))
                    elif not isinstance(content, str):
                        content = str(content)
                        
                    if msg["role"] == "user":
                        history.append({"role": "user", "content": content})
                    else:
                        history.append({"role": "assistant", "content": content})
                
                # Get AI response with image
                message_placeholder = st.empty()
                
                response_data = send_message_with_image(
                    user_message,
                    history,
                    image_base64,
                    st.session_state.session_id
                )
                
                # Process and display response
                if isinstance(response_data, dict) and "response" in response_data:
                    clean_text, regular_images, image_queries, actions = process_aiman_directives(response_data["response"])
                    
                    message_placeholder.markdown(clean_text)
                    
                    # Display search images using new system
                    search_queries = response_data.get("search_image_queries", [])
                    if search_queries:
                        render_search_images(search_queries)
                    
                    # Display action cards using new system
                    action_items = response_data.get("action_items", [])
                    if action_items:
                        st.markdown("---")
                        st.markdown("**🎯 Recommended Actions:**")
                        for action in action_items:
                            render_action_card(action.get("type", ""), action.get("name", ""))
                    
                    # Store response
                    st.session_state.messages.append({"role": "assistant", "content": response_data})
                else:
                    response_text = response_data.get("response", str(response_data)) if isinstance(response_data, dict) else str(response_data)
                    message_placeholder.markdown(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
            
            # Clear the pending image
            st.session_state["pending_image"] = None
            st.session_state["image_uploaded"] = False
            
            st.rerun()
            
        elif prompt:
            # Regular text message without image
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)

        # Prepare conversation history for backend
        history = []
        for msg in st.session_state.messages[:-1]:  # Exclude the current prompt
            content = msg["content"]
            
            # Ensure content is a string, not a dict
            if isinstance(content, dict):
                content = content.get("response", str(content))
            elif not isinstance(content, str):
                content = str(content)
                
            if msg["role"] == "user":
                history.append({"role": "user", "content": content})
            else:
                history.append({"role": "assistant", "content": content})

        # Get AI response with Aiman features
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            # Show thinking animation
            with st.spinner("🤔 Aiman is crafting your perfect response..."):
                response_data = send_message_with_image(prompt, history, None, st.session_state.session_id)
            
            if isinstance(response_data, dict) and "response" in response_data:
                # Process Aiman's enhanced response
                clean_text, regular_images, image_queries, actions = process_aiman_directives(response_data["response"])
                
                # Display response with directive processing
                message_placeholder.markdown(clean_text)
                
                # Display regular images if available (fallback)
                if regular_images:
                    st.markdown("**📸 Aiman's Visual Recommendations:**")
                    for img_url in regular_images:
                        try:
                            st.image(img_url.strip(), caption="📸 Recommended by Aiman", width=300)
                        except:
                            # Gracefully handle broken images - don't show broken links
                            pass
                
                # Retrieve and display intelligent images
                if image_queries:
                    st.markdown("**🔍 Finding Perfect Images for You...**")
                    with st.spinner("Searching Malaysia tourism images..."):
                        retrieved_urls = retrieve_images_for_queries(image_queries)
                        
                    if retrieved_urls:
                        st.markdown("**📸 Aiman's Visual Recommendations:**")
                        for i, url in enumerate(retrieved_urls):
                            try:
                                query = image_queries[i] if i < len(image_queries) else "Malaysia Tourism"
                                
                                # Get image metadata for attribution
                                image_data = st.session_state.get(f"image_query_{query}", {})
                                
                                # Display image
                                st.image(url, caption=f"📸 {query}", width=300)
                                
                                # Add proper Unsplash attribution if available
                                if image_data.get("source") == "Unsplash":
                                    photographer_name = image_data.get("photographer_name", "Unknown Photographer")
                                    photographer_url = image_data.get("photographer_url", "https://unsplash.com")
                                    
                                    st.caption(f"Photo by [{photographer_name}]({photographer_url}) on [Unsplash](https://unsplash.com)")
                                    
                                    # Track download for Unsplash compliance
                                    download_url = image_data.get("download_url")
                                    if download_url:
                                        try:
                                            requests.post(f"{BACKEND_URL}/track-image-download", json={"download_url": download_url}, timeout=5)
                                        except:
                                            pass  # Silent failure for tracking
                                            
                            except:
                                # Gracefully handle broken retrieved images
                                pass
                
                # Display action cards if available
                if actions:
                    st.markdown("---")
                    st.markdown("**🎯 Take Action:**")
                    for action_type, action_name in actions:
                        render_action_card(action_type, action_name)
                
                # Store the full response data for history
                st.session_state.messages.append({"role": "assistant", "content": response_data})
            else:
                # Fallback for simple text responses
                response_text = response_data.get("response", str(response_data)) if isinstance(response_data, dict) else str(response_data)
                message_placeholder.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
        
        # Auto-scroll to bottom
        st.rerun()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        🇲🇾 Aiman - Your Malaysia Travel Concierge | Powered by Fine-tuned Gemini AI
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 