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
    initial_sidebar_state="expanded"
)

# Backend configuration - works both locally and on Render
import os
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
BACKEND_URL = API_BASE_URL

# Custom CSS for beautiful UI
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    .chat-container {
        max-height: 600px;
        overflow-y: auto;
        padding: 1rem;
        border: 1px solid #ddd;
        border-radius: 10px;
        background-color: #fafafa;
    }
    .status-success {
        color: #4caf50;
        font-weight: bold;
    }
    .status-error {
        color: #f44336;
        font-weight: bold;
    }
    .header-container {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

def check_backend_health() -> bool:
    """Check if the backend is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def clean_display_text(text: str) -> str:
    """Clean text for better display"""
    if not text:
        return text
    
    # Remove excessive whitespace while preserving paragraph breaks
    import re
    
    # Replace multiple spaces with single space
    cleaned = re.sub(r' +', ' ', text)
    
    # Clean up line breaks - preserve intentional formatting
    cleaned = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned)
    
    # Remove trailing/leading whitespace
    cleaned = cleaned.strip()
    
    return cleaned

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

def retrieve_images_for_queries(image_queries: List[str]) -> List[str]:
    """Retrieve images for the given search queries using the backend API"""
    retrieved_urls = []
    
    for query in image_queries:
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
                    st.session_state[f"image_query_{query}"] = {
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
    """Send message with optional image to backend"""
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
            
            # Store response info for debugging
            st.session_state["last_response_info"] = {
                "length": len(raw_response),
                "model": model_used,
                "phase": phase,
                "contains_images": contains_images,
                "contains_actions": contains_actions,
                "temp": temperature,
                "max_tokens": max_tokens,
                "had_image": image_data is not None
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
    # Header
    st.markdown("""
    <div class="header-container">
        <h1>🇲🇾 Aiman - Your Malaysia Travel Concierge</h1>
        <p>Selamat Datang! Welcome to your personalized Malaysian travel experience</p>
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
        
        # Instructions
        st.markdown("### 💡 How to Use")
        st.markdown("""
        1. Type your message in the chat input
        2. Press Enter to send
        3. Watch the AI respond in real-time
        4. Continue the conversation naturally
        """)

    # Initialize chat history and session
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    # Display chat history
    st.markdown("### 💬 Chat with Aiman")
    
    # Show intro message if no conversation started
    if len(st.session_state.messages) == 0:
        st.info("👋 Selamat Datang! Start your conversation with Aiman by asking about Malaysia travel plans or upload an image for personalized recommendations!")
    
    # Chat container
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
                                st.image(img_url.strip(), caption="📸 Recommended by Aiman")
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
                                st.image(url, caption=f"📸 {query}")
                                
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

    # Chat input with integrated image upload (like Gemini interface)
    st.markdown("---")
    
    # Create input area with image upload button beside it
    col1, col2 = st.columns([6, 1])
    
    with col1:
        prompt = st.chat_input("Type your message here...")
    
    with col2:
        # Small upload button next to input
        uploaded_file = st.file_uploader(
            "📸",
            type=['png', 'jpg', 'jpeg', 'webp'],
            help="Upload image",
            key="quick_upload",
            label_visibility="collapsed"
        )
    
    # Handle quick image upload
    if uploaded_file is not None:
        # Store the uploaded file in session state for processing
        st.session_state["pending_image"] = uploaded_file
        st.session_state["image_uploaded"] = True
        
        # Show compact preview
        with st.container():
            col1, col2 = st.columns([1, 3])
            with col1:
                st.image(uploaded_file, width=80)
            with col2:
                st.success("📸 Image ready! Type your question and press Enter.")
    
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
            
            # Display user message with image
            with st.chat_message("user"):
                st.markdown(user_message)
                st.image(uploaded_file, width=200)
            
            # Process with image analysis
            with st.spinner("🤖 Aiman is analyzing your image..."):
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
                with st.chat_message("assistant"):
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
                        
                        # Display any retrieved images
                        if image_queries:
                            st.markdown("**🔍 Finding Related Images...**")
                            with st.spinner("Searching Malaysia tourism images..."):
                                retrieved_urls = retrieve_images_for_queries(image_queries)
                                
                            if retrieved_urls:
                                st.markdown("**📸 Related Recommendations:**")
                                for i, url in enumerate(retrieved_urls):
                                    try:
                                        query = image_queries[i] if i < len(image_queries) else "Malaysia Tourism"
                                        
                                        # Get image metadata for attribution
                                        image_data = st.session_state.get(f"image_query_{query}", {})
                                        
                                        # Display image
                                        st.image(url, caption=f"📸 {query}")
                                        
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
                                        pass
                        
                        # Display action cards
                        if actions:
                            st.markdown("---")
                            st.markdown("**🎯 Take Action:**")
                            for action_type, action_name in actions:
                                render_action_card(action_type, action_name)
                        
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
            
        else:
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
                            st.image(img_url.strip(), caption="📸 Recommended by Aiman")
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
                                st.image(url, caption=f"📸 {query}")
                                
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