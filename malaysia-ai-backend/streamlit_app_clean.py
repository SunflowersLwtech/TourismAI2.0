import streamlit as st
import requests
import json
import base64
from typing import Dict, Any, Optional

# Page configuration
st.set_page_config(
    page_title="🇲🇾 Aiman - Malaysia Travel Concierge",
    page_icon="🇲🇾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
    }
    
    .chat-container {
        max-height: 500px;
        overflow-y: auto;
        padding: 1rem;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        background: #f8f9fa;
    }
    
    .status-success {
        color: #28a745;
        font-weight: bold;
    }
    
    .status-error {
        color: #dc3545;
        font-weight: bold;
    }
    
    .welcome-card {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin: 2rem 0;
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stChatMessage {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# Backend health check
def check_backend_health() -> bool:
    """Check if the backend is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

# Image search function
def search_images(query: str, max_results: int = 3) -> list:
    """Search for images using the backend image search endpoint"""
    try:
        url = "http://localhost:8000/image-search"
        payload = {"query": query, "max_results": max_results}
        
        response = requests.post(url, json=payload, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            images = result.get("images", [])
            
            # Validate image URLs
            valid_images = []
            for img in images:
                if img.get("url") and img["url"].startswith("http"):
                    valid_images.append(img)
                    
            return valid_images
        else:
            error_msg = f"Image search failed: {response.status_code}"
            if "debug_info" in st.session_state:
                st.session_state.debug_info += f"\n{error_msg}"
            return []
    except requests.exceptions.Timeout:
        error_msg = "Image search timeout - please try again"
        if "debug_info" in st.session_state:
            st.session_state.debug_info += f"\n{error_msg}"
        return []
    except Exception as e:
        error_msg = f"Image search error: {str(e)}"
        if "debug_info" in st.session_state:
            st.session_state.debug_info += f"\n{error_msg}"
        return []

# Function to get attraction booking links
def get_attraction_links(attraction_name: str) -> str:
    """Get booking links for attractions based on name"""
    # Common Malaysia attractions and their booking links
    attraction_links = {
        "petronas twin towers": "🔗 **Official Booking:** https://www.petronastwintowers.com.my/\n🎫 **Alternative:** https://www.klook.com/en-MY/activity/99-petronas-twin-towers-kuala-lumpur/",
        "petronas twin towers observation deck": "🔗 **Official Booking:** https://www.petronastwintowers.com.my/\n🎫 **Alternative:** https://www.klook.com/en-MY/activity/99-petronas-twin-towers-kuala-lumpur/",
        "batu caves": "🔗 **Free Entry** - No booking required\n🎫 **Guided Tours:** https://www.klook.com/en-MY/activity/1075-batu-caves-kuala-lumpur/",
        "genting highlands": "🔗 **Official:** https://www.rwgenting.com/\n🎫 **Cable Car:** https://www.awana.com.my/",
        "kl tower": "🔗 **Official:** https://www.menarakl.com.my/\n🎫 **Klook:** https://www.klook.com/en-MY/activity/142-kl-tower-kuala-lumpur/",
        "sunway lagoon": "🔗 **Official:** https://sunwaylagoon.com/\n🎫 **Tickets:** https://www.klook.com/en-MY/activity/1519-sunway-lagoon-kuala-lumpur/",
        "legoland malaysia": "🔗 **Official:** https://www.legoland.com.my/\n🎫 **Tickets:** https://www.klook.com/en-MY/activity/1356-legoland-malaysia-johor-bahru/",
        "aquaria klcc": "🔗 **Official:** https://www.aquariaklcc.com/\n🎫 **Tickets:** https://www.klook.com/en-MY/activity/1356-aquaria-klcc-kuala-lumpur/",
        "zoo negara": "🔗 **Official:** https://www.zoonegara.my/\n🎫 **Tickets:** https://www.klook.com/en-MY/activity/1356-zoo-negara-kuala-lumpur/",
        "universal studios singapore": "🔗 **Official:** https://www.rwsentosa.com/en/attractions/universal-studios-singapore\n🎫 **Tickets:** https://www.klook.com/en-MY/activity/22-universal-studios-singapore/",
        "singapore zoo": "🔗 **Official:** https://www.wrs.com.sg/en/singapore-zoo/\n🎫 **Tickets:** https://www.klook.com/en-MY/activity/108-singapore-zoo/",
        "sentosa island": "🔗 **Official:** https://www.sentosa.com.sg/\n🎫 **Tickets:** https://www.klook.com/en-MY/activity/108-sentosa-island-singapore/"
    }
    
    # Try to match attraction name (case insensitive)
    attraction_lower = attraction_name.lower()
    
    # Direct match
    if attraction_lower in attraction_links:
        return attraction_links[attraction_lower]
    
    # Partial match
    for key, value in attraction_links.items():
        if key in attraction_lower or attraction_lower in key:
            return value
    
    # Default response for unknown attractions
    return f"🔍 **Search for '{attraction_name}' tickets:**\n🎫 **Klook:** https://www.klook.com/en-MY/search/?query={attraction_name.replace(' ', '+')}\n🎫 **GetYourGuide:** https://www.getyourguide.com/malaysia-l188/?q={attraction_name.replace(' ', '+')}"

# Chat API call
def chat_with_aiman(message: str, image_data: Optional[str] = None) -> tuple[str, list]:
    """Send message to Aiman API and return response with image queries"""
    debug_info = []
    
    try:
        # Get conversation history from session state
        conversation_history = []
        if "messages" in st.session_state:
            # Convert messages to backend format and keep last 10 for context
            for msg in st.session_state.messages[-10:]:
                conversation_history.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Use different endpoint for image analysis
        if image_data:
            url = "http://localhost:8000/chat-with-image"
            payload = {
                "message": message,
                "image_data": image_data,  # Correct key name
                "conversation_history": conversation_history,
                "temperature": 0.7,
                "max_tokens": 8192
            }
            debug_info.append(f"Using image analysis endpoint")
            debug_info.append(f"Image data length: {len(image_data)}")
        else:
            url = "http://localhost:8000/chat"
            payload = {
                "message": message,
                "conversation_history": conversation_history
            }
            debug_info.append(f"Using regular chat endpoint")
        
        debug_info.append(f"Conversation history length: {len(conversation_history)}")
            
        debug_info.append(f"Sending request to {url}")
        debug_info.append(f"Payload keys: {list(payload.keys())}")
        
        response = requests.post(url, json=payload, timeout=30)
        
        debug_info.append(f"Response status: {response.status_code}")
        
        # Store debug info in session state
        st.session_state.debug_info = "\n".join(debug_info)
        
        if response.status_code == 200:
            result = response.json()
            debug_info.append(f"Response keys: {list(result.keys())}")
            debug_info.append(f"Contains images: {result.get('contains_images', False)}")
            debug_info.append(f"Search queries: {result.get('search_image_queries', [])}")
            st.session_state.debug_info = "\n".join(debug_info)
            
            # Clean response text by removing directives and extract action items
            response_text = result.get("response", "Sorry, I couldn't process your request.")
            import re
            
            # Remove SEARCH_IMAGE directives
            cleaned_response = re.sub(r'\[SEARCH_IMAGE:\s*"[^"]+"\]', '', response_text)
            
            # Remove ACTION directives and process them
            action_pattern = r'\[ACTION:\s*([^,\]]+)(?:,\s*([^\]]+))?\]'
            action_matches = re.findall(action_pattern, cleaned_response)
            cleaned_response = re.sub(action_pattern, '', cleaned_response)
            
            # Process action items
            action_items = []
            for match in action_matches:
                action_type = match[0].strip()
                action_target = match[1].strip() if match[1] else ""
                action_items.append({
                    "type": action_type,
                    "target": action_target
                })
            
            # Store action items in debug info
            if action_items:
                debug_info.append(f"Found actions: {action_items}")
                # Add action processing here
                for action in action_items:
                    if action["type"] == "Attraction":
                        attraction_links = get_attraction_links(action["target"])
                        if attraction_links:
                            cleaned_response += f"\n\n🔗 **Booking Links:**\n{attraction_links}"
            
            st.session_state.debug_info = "\n".join(debug_info)
            return cleaned_response.strip(), result.get("search_image_queries", [])
        else:
            error_msg = f"API Error: {response.status_code}"
            try:
                error_detail = response.json()
                error_msg += f" - {error_detail.get('detail', 'Unknown error')}"
                debug_info.append(f"Error detail: {error_detail}")
            except:
                pass
            st.session_state.debug_info = "\n".join(debug_info)
            return error_msg, []
    except Exception as e:
        debug_info.append(f"Exception: {str(e)}")
        st.session_state.debug_info = "\n".join(debug_info)
        return f"Connection error: {str(e)}", []

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Main app
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🇲🇾 Aiman - Malaysia Travel Concierge</h1>
        <p>Your AI-Powered Malaysia Travel Assistant</p>
        <p>✨ Discover Malaysia • 🏖️ Plan Your Journey • 📸 Get Recommendations</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 System Status")
        
        # Backend status
        if check_backend_health():
            st.success("✅ Backend: Connected")
        else:
            st.error("❌ Backend: Disconnected")
            st.error("Please ensure the backend server is running on http://localhost:8000")
            st.stop()
        
        st.markdown("---")
        
        # Clear chat button
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        st.markdown("---")
        
        # Debug info
        if "debug_info" in st.session_state:
            st.subheader("🔍 Debug Info")
            st.text(st.session_state.debug_info)
        
        # Info
        st.markdown("""
        ### 💡 How to use:
        1. **Ask questions** about Malaysia travel
        2. **Upload images** for analysis
        3. **Get recommendations** for your trip
        
        ### 🌟 Features:
        - Local insights and tips
        - Image analysis
        - Travel recommendations
        - Cultural information
        """)
    
    # Chat history
    st.subheader("💬 Chat History")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "image" in message and message["image"] is not None:
                try:
                    st.image(message["image"], width=300)
                    if "image_name" in message:
                        st.caption(f"📷 {message['image_name']}")
                except Exception as e:
                    st.error(f"❌ Failed to display image: {str(e)}")
            
            # Display search results for assistant messages
            if message["role"] == "assistant" and "search_queries" in message:
                st.markdown("### 📸 Related Images")
                for query in message["search_queries"]:
                    try:
                        with st.spinner(f"🔍 Loading images for: {query}"):
                            images = search_images(query, max_results=3)
                            if images:
                                st.markdown(f"**{query}**")
                                cols = st.columns(min(len(images), 3))
                                for i, img in enumerate(images[:3]):
                                    with cols[i]:
                                        try:
                                            st.image(
                                                img.get("url", ""),
                                                caption=img.get("title", "Image") if img.get("title") else "Image",
                                                use_container_width=True
                                            )
                                            if img.get("photographer_name"):
                                                st.caption(f"📷 {img['photographer_name']}")
                                        except Exception as img_error:
                                            st.error(f"❌ Failed to load image: {str(img_error)}")
                    except Exception as search_error:
                        st.error(f"❌ Search failed for '{query}': {str(search_error)}")
    
    # File uploader with improved handling
    uploaded_file = st.file_uploader(
        "📸 Upload an image (optional)",
        type=['png', 'jpg', 'jpeg', 'webp', 'gif'],
        help="Upload a travel photo for analysis",
        key="image_uploader"
    )
    
    # Initialize session state for image handling
    if "current_image" not in st.session_state:
        st.session_state.current_image = None
    if "current_image_data" not in st.session_state:
        st.session_state.current_image_data = None
    
    # Handle image upload
    if uploaded_file is not None:
        # Check if this is a new image
        if st.session_state.current_image != uploaded_file.name:
            try:
                # Process new image
                uploaded_file.seek(0)
                image_bytes = uploaded_file.read()
                st.session_state.current_image_data = base64.b64encode(image_bytes).decode()
                st.session_state.current_image = uploaded_file.name
                st.success(f"✅ Image uploaded: {uploaded_file.name}")
            except Exception as e:
                st.error(f"❌ Error processing image: {str(e)}")
                st.session_state.current_image_data = None
                st.session_state.current_image = None
        
        # Show uploaded image preview
        st.image(uploaded_file, width=300, caption=f"📷 {uploaded_file.name}")
        
    else:
        # Clear image data if no file uploaded
        st.session_state.current_image = None
        st.session_state.current_image_data = None
    
    # Show current image status before chat input
    if st.session_state.current_image:
        st.info(f"📸 Ready to analyze: {st.session_state.current_image}")
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about Malaysia travel..."):
        # Get current image data
        image_data = st.session_state.current_image_data
        current_image_name = st.session_state.current_image
        
        # Debug information
        debug_info = []
        debug_info.append(f"Prompt: {prompt}")
        debug_info.append(f"Image uploaded: {current_image_name is not None}")
        if current_image_name:
            debug_info.append(f"Image name: {current_image_name}")
            debug_info.append(f"Image data length: {len(image_data) if image_data else 0}")
            debug_info.append(f"Image data starts with: {image_data[:50] if image_data else 'None'}...")
        else:
            debug_info.append("No image data available")
        
        # Add user message
        user_message = {"role": "user", "content": prompt}
        if current_image_name and uploaded_file:
            user_message["image"] = uploaded_file
            user_message["image_name"] = current_image_name
        st.session_state.messages.append(user_message)
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
            if current_image_name and uploaded_file:
                st.image(uploaded_file, width=300)
                st.caption(f"📷 Analyzing: {current_image_name}")
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Analyzing your image..." if image_data else "🤔 Thinking..."):
                response, search_queries = chat_with_aiman(prompt, image_data)
                
                # Update debug info
                debug_info.append(f"Image sent to AI: {image_data is not None}")
                debug_info.append(f"Response length: {len(response)}")
                st.session_state.debug_info = "\n".join(debug_info)
            
            # Display the text response
            st.markdown(response)
            
            # If there are image search queries, fetch and display images
            if search_queries:
                st.markdown("### 📸 Related Images")
                for query in search_queries:
                    try:
                        with st.spinner(f"🔍 Searching for: {query}"):
                            images = search_images(query, max_results=3)
                            if images:
                                st.markdown(f"**{query}**")
                                cols = st.columns(min(len(images), 3))
                                for i, img in enumerate(images[:3]):
                                    with cols[i]:
                                        try:
                                            st.image(
                                                img.get("url", ""),
                                                caption=img.get("title", "Image") if img.get("title") else "Image",
                                                use_container_width=True
                                            )
                                            if img.get("photographer_name"):
                                                st.caption(f"📷 {img['photographer_name']}")
                                        except Exception as img_error:
                                            st.error(f"❌ Failed to load image: {str(img_error)}")
                            else:
                                st.info(f"💭 No images found for: {query}")
                    except Exception as search_error:
                        st.error(f"❌ Search failed for '{query}': {str(search_error)}")
                        # Update debug info
                        if "debug_info" in st.session_state:
                            st.session_state.debug_info += f"\nSearch exception for '{query}': {str(search_error)}"
        
        # Add assistant response (store both text and images)
        assistant_message = {"role": "assistant", "content": response}
        if search_queries:
            assistant_message["search_queries"] = search_queries
        st.session_state.messages.append(assistant_message)
        
        # Rerun to update chat
        st.rerun()
    
    # Welcome message
    if not st.session_state.messages:
        st.markdown("""
        <div class="welcome-card">
            <h2>👋 Welcome to Aiman!</h2>
            <p>I'm your AI-powered Malaysia travel concierge. I can help you:</p>
            <ul>
                <li>🏝️ Discover amazing places in Malaysia</li>
                <li>🗺️ Plan your perfect itinerary</li>
                <li>📸 Analyze travel photos</li>
                <li>💡 Get local insights and recommendations</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature examples
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="feature-card">
                <h4>🏛️ Ask Questions</h4>
                <p>Try: "What are the best places to visit in Kuala Lumpur?"</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="feature-card">
                <h4>🍜 Food Culture</h4>
                <p>Try: "Tell me about Malaysian food culture"</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="feature-card">
                <h4>📸 Image Analysis</h4>
                <p>Upload a photo and ask: "What can you tell me about this place?"</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()