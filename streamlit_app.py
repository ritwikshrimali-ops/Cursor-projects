import streamlit as st
import requests
import json
from datetime import datetime
import time
import pandas as pd

# Hardcoded API Auth Token
API_AUTH_TOKEN = "vREkxoDNUEyrAtkhgtRN"

# API URLs
DEVICE_INSPECT_URL = "https://api.adjust.com/device_service/api/v2/inspect_device"

# Page configuration
st.set_page_config(
    page_title="Testing console - Adjust",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Force light theme
st.markdown("""
    <style>
    /* Force light theme */
    .stApp {
        background-color: #ffffff;
    }
    /* Hide GitHub menu and other Streamlit menu items */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Share button styling */
    .share-button-container {
        position: fixed;
        top: 1rem;
        right: 1rem;
        z-index: 999;
    }
    .share-button {
        background-color: #1f77b4;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        cursor: pointer;
        font-size: 0.9rem;
        font-weight: 500;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: background-color 0.3s;
    }
    .share-button:hover {
        background-color: #1565a0;
    }
    
    /* Modal styling */
    .share-modal {
        display: none;
        position: fixed;
        z-index: 1000;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        overflow: auto;
        background-color: rgba(0,0,0,0.4);
    }
    .share-modal-content {
        background-color: #fefefe;
        margin: 10% auto;
        padding: 2rem;
        border: 1px solid #888;
        border-radius: 0.5rem;
        width: 90%;
        max-width: 500px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .share-modal-header {
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: #1a1a1a;
    }
    .share-modal-close {
        color: #aaa;
        float: right;
        font-size: 28px;
        font-weight: bold;
        cursor: pointer;
    }
    .share-modal-close:hover,
    .share-modal-close:focus {
        color: #000;
    }
    .email-input-container {
        margin-bottom: 1rem;
    }
    .email-input {
        width: 100%;
        padding: 0.75rem;
        border: 1px solid #ddd;
        border-radius: 0.25rem;
        font-size: 0.95rem;
        margin-bottom: 0.5rem;
    }
    .email-tag {
        display: inline-block;
        background-color: #e3f2fd;
        color: #1976d2;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        margin: 0.25rem;
        font-size: 0.875rem;
    }
    .email-tag-remove {
        margin-left: 0.5rem;
        cursor: pointer;
        font-weight: bold;
    }
    .share-modal-buttons {
        display: flex;
        gap: 0.5rem;
        margin-top: 1rem;
    }
    .share-modal-button {
        padding: 0.5rem 1.5rem;
        border: none;
        border-radius: 0.25rem;
        cursor: pointer;
        font-size: 0.9rem;
        font-weight: 500;
    }
    .share-modal-button-primary {
        background-color: #1f77b4;
        color: white;
    }
    .share-modal-button-primary:hover {
        background-color: #1565a0;
    }
    .share-modal-button-secondary {
        background-color: #e0e0e0;
        color: #333;
    }
    .share-modal-button-secondary:hover {
        background-color: #d0d0d0;
    }
    </style>
""", unsafe_allow_html=True)

# Custom CSS to match Adjust console styling
st.markdown("""
    <style>
    .main-header {
        font-size: 1.75rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
    }
    .description-text {
        color: #666;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
        line-height: 1.5;
    }
    .section-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #e0e0e0;
    }
    .info-label {
        font-weight: 500;
        color: #333;
        margin-bottom: 0.25rem;
    }
    .info-value {
        color: #1a1a1a;
        margin-bottom: 0.75rem;
    }
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.875rem;
        font-weight: 500;
    }
    .badge-green {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .badge-blue {
        background-color: #d1ecf1;
        color: #0c5460;
        border: 1px solid #bee5eb;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# App name to token mapping
APP_NAME_TO_TOKEN = {
    "Word Search": "df8zj1g2e4n4",
    "Word Trip": "brmx7fdxeakg",
    "Daily themed crossword": "5m1ixiozuxs0",
    "Tilescapes": "d9j2i31ih5hc",
    "Crossword Go": "lh3djeuvx8u8",
    "Word Bingo": "axyjxakbq4u8",
    "Cryptogram": "mmdpjw08385c",
    "Word Tour": "10m9pfaqr7og",
    "Word Connect Association": "r35fo7shcq20",
    "Crossword Explorer": "kl9obuzolf5s",
    "Wordsearch Explorer Amazon": "imv73i9w1kw0",
    "DTC Amazon": "m5wkkketzbwg",
    "Word Jam": "yi754iuv045c",
    "Word Search Solitaire": "f31mdtfxsj5s",
    "Word Jam Amazon": "lq4zr6bosmbk",
    "Word Trip Amazon": "o7zbc1ugkcg0",
    "Wordsearch-wordtrip": "peaqr4bgdb7k",
    "2248 Tiles Game": "wh6mlumfs2rk",
    "WordPal": "ftrpnn2xascg",
    "Word Planet": "0695581rbqww"
}

# Sidebar for app selection
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # App selection dropdown
    app_names = list(APP_NAME_TO_TOKEN.keys())
    current_selection = st.session_state.get("selected_app_name", "")
    
    # Find index safely
    try:
        if current_selection and current_selection in app_names:
            selected_index = app_names.index(current_selection)
        else:
            selected_index = 0
    except (ValueError, IndexError):
        selected_index = 0
    
    selected_app_name = st.selectbox(
        "Select App",
        options=app_names,
        index=selected_index,
        help="Select an app to test"
    )
    
    # Automatically set app token based on selected app name
    app_token = APP_NAME_TO_TOKEN.get(selected_app_name, "")
    st.session_state["selected_app_name"] = selected_app_name
    st.session_state["app_token"] = app_token
    
    # Show selected app token (read-only)
    if app_token:
        st.caption(f"App Token: `{app_token}`")

# Initialize session state for share functionality
if "share_modal_open" not in st.session_state:
    st.session_state["share_modal_open"] = False
if "share_email" not in st.session_state:
    st.session_state["share_email"] = ""

# Share button styling - ensure text stays on one line
st.markdown("""
    <style>
    /* Fix Share button text to stay on one line */
    button[data-testid*="share_button_top"] {
        white-space: nowrap !important;
        word-break: keep-all !important;
    }
    button[data-testid*="share_button_top"] p {
        white-space: nowrap !important;
        margin: 0 !important;
    }
    /* Share popover styling */
    #sharePopover {
        position: fixed;
        top: 3.5rem;
        right: 1rem;
        z-index: 1000;
        background: white;
        border: 1px solid #ddd;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        min-width: 280px;
        max-width: 320px;
    }
    </style>
""", unsafe_allow_html=True)

# Create columns to position Share button in top right
col_left, col_right = st.columns([0.95, 0.05])
with col_right:
    if st.button("Share", key="share_button_top", help="Share access with other users", use_container_width=False):
        st.session_state["share_modal_open"] = not st.session_state["share_modal_open"]
        st.rerun()

# Handle closing share modal
if st.query_params.get("close_share") == "true":
    st.session_state["share_modal_open"] = False
    st.rerun()

# Handle share email submission
if st.query_params.get("share_email"):
    email = st.query_params.get("share_email")
    if email and "@" in email and "." in email.split("@")[1]:
        st.success(f"✅ Access shared with {email}")
        st.session_state["share_modal_open"] = False
        st.rerun()

# Compact share popover - only show when modal is open (using pure HTML/JS overlay)
if st.session_state["share_modal_open"]:
    st.markdown("""
        <div id="sharePopover">
            <form id="shareForm" onsubmit="event.preventDefault(); handleShareSubmit();">
                <label for="shareEmailInput" style="display: block; margin-bottom: 0.5rem; font-weight: 500; color: #333;">Email address</label>
                <input type="email" id="shareEmailInput" placeholder="user@example.com" 
                       style="width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 0.25rem; margin-bottom: 0.75rem; font-size: 0.9rem; box-sizing: border-box;" />
                <div style="display: flex; gap: 0.5rem;">
                    <button type="submit" id="shareSubmitBtn" 
                            style="flex: 1; padding: 0.5rem; background-color: #ff4444; color: white; border: none; border-radius: 0.25rem; cursor: pointer; font-size: 0.9rem; font-weight: 500;">Share</button>
                    <button type="button" 
                            style="flex: 1; padding: 0.5rem; background-color: white; color: #333; border: 1px solid #ddd; border-radius: 0.25rem; cursor: pointer; font-size: 0.9rem; font-weight: 500;"
                            onclick="closeSharePopover()">Cancel</button>
                </div>
            </form>
        </div>
        <script>
        function handleShareSubmit() {
            const email = document.getElementById('shareEmailInput').value.trim();
            if (email && email.includes('@') && email.includes('.')) {
                // Navigate with email as query param
                const url = new URL(window.location.href);
                url.searchParams.set('share_email', email);
                window.location.href = url.toString();
            } else {
                alert('Please enter a valid email address.');
            }
        }
        
        function closeSharePopover() {
            // Navigate without share modal state
            const url = new URL(window.location.href);
            url.searchParams.set('close_share', 'true');
            window.location.href = url.toString();
        }
        
        // Close on outside click
        setTimeout(function() {
            document.addEventListener('click', function(event) {
                const popover = document.getElementById('sharePopover');
                const shareButton = event.target.closest('button[data-testid*="share_button_top"]');
                const shareForm = document.getElementById('shareForm');
                if (popover && !popover.contains(event.target) && !shareButton && event.target !== shareForm) {
                    closeSharePopover();
                }
            });
        }, 100);
        </script>
    """, unsafe_allow_html=True)

# Main content - Header section
st.markdown('<p class="main-header">Testing console</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="description-text">Enter your advertising ID below to immediately verify raw device activity, review attribution data, confirm event activity, or clear your device between tests.</p>',
    unsafe_allow_html=True
)

# Advertising ID input and buttons
col1, col2, col3 = st.columns([3, 1, 1])

with col1:
    advertising_id = st.text_input(
        "Advertising ID",
        value=st.session_state.get("advertising_id", ""),
        help="Enter the advertising ID to inspect",
        label_visibility="visible",
        key="advertising_id_input"
    )
    st.session_state["advertising_id"] = advertising_id

with col2:
    fetch_button = st.button("View or refresh device data", type="primary", use_container_width=True)

with col3:
    forget_button = st.button("Forget device", use_container_width=True)

# Function to fetch device info with retry logic
def fetch_device_info(app_token, advertising_id, api_auth_token, api_url, max_retries=3):
    """Fetch device information from Adjust API with retry logic"""
    if not all([app_token, advertising_id]):
        return None, "Please fill in App Token and Advertising ID"
    
    params = {
        "app_token": app_token,
        "advertising_id": advertising_id
    }
    
    headers = {
        "Authorization": f"Bearer {api_auth_token}",
        "Accept": "application/json"
    }
    
    # Try with increasing timeout values
    timeout_values = [15, 30, 45]
    
    for attempt in range(max_retries):
        try:
            timeout = timeout_values[min(attempt, len(timeout_values) - 1)]
            response = requests.get(api_url, params=params, headers=headers, timeout=timeout)
            
            if response.status_code == 200:
                return response.json(), None
            elif response.status_code == 502:
                # 502 Bad Gateway - might be temporary, retry
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                    continue
                else:
                    error_data = response.text
                    try:
                        error_json = response.json()
                        if "errors" in error_json:
                            error_msg = ", ".join(error_json["errors"])
                            return None, f"API Error {response.status_code}: {error_msg}. The API request timed out. Please try again in a moment."
                    except:
                        pass
                    return None, f"API Error {response.status_code}: {error_data}. The API request timed out. Please try again."
            else:
                error_data = response.text
                try:
                    error_json = response.json()
                    if "errors" in error_json:
                        error_msg = ", ".join(error_json["errors"])
                        return None, f"API Error {response.status_code}: {error_msg}"
                except:
                    pass
                return None, f"API Error {response.status_code}: {error_data}"
        
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            else:
                return None, f"Request timed out after {max_retries} attempts. The API may be slow or overloaded. Please try again in a moment."
        
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            else:
                return None, f"Request failed after {max_retries} attempts: {str(e)}"
    
    return None, "Failed to fetch device information after multiple attempts."

# Function to create badge
def create_badge(text, badge_type="green"):
    """Create a pill-shaped badge"""
    badge_class = "badge-green" if badge_type == "green" else "badge-blue"
    return f'<span class="badge {badge_class}">{text}</span>'

# Function to format datetime
def format_datetime(dt_str, format_type="utc"):
    """Format datetime string"""
    if not dt_str or dt_str == "0001-01-01T00:00:00Z":
        return "—"
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        if format_type == "utc":
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        else:  # local
            return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return dt_str

# Auto-fetch logic (removed - no auto-refresh)
auto_fetch_triggered = False

# Handle forget device button
if forget_button:
    if "last_device_info" in st.session_state:
        del st.session_state["last_device_info"]
    st.session_state["advertising_id"] = ""
    st.rerun()

# Fetch data when button is clicked
should_fetch = fetch_button

if should_fetch:
    with st.spinner("Fetching device information..."):
        device_info, error = fetch_device_info(
            st.session_state.get("app_token", ""),
            st.session_state.get("advertising_id", ""),
            API_AUTH_TOKEN,
            DEVICE_INSPECT_URL
        )
        
        if error:
            st.markdown(f'<div class="error-box">❌ <strong>Error:</strong> {error}</div>', unsafe_allow_html=True)
            st.session_state["last_fetch_success"] = False
        else:
            st.session_state["last_device_info"] = device_info
            st.session_state["last_fetch_time"] = time.time()
            st.session_state["last_fetch_success"] = True

# Display results in Adjust console format
if "last_device_info" in st.session_state:
    device_info = st.session_state["last_device_info"]
    
    # Helper function to safely get nested values
    def get_nested_value(data, *keys, default="—"):
        """Safely get nested dictionary values"""
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current if current not in [None, "", "0001-01-01T00:00:00Z"] else default
    
    # 1. Identification information
    st.markdown('<p class="section-header">Identification information</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f'<p class="info-label">Advertising ID</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="info-value">{st.session_state.get("advertising_id", "—")}</p>', unsafe_allow_html=True)
    
    with col2:
        # ADID should be fetched from raw JSON Adid field (capital A)
        # Try multiple possible field names
        adid_value = "—"
        if isinstance(device_info, dict):
            adid_value = (device_info.get("Adid") or 
                         device_info.get("adid") or 
                         device_info.get("ADID") or 
                         get_nested_value(device_info, "Adid") or 
                         "—")
            # Filter out empty/null values
            if adid_value in [None, "", "0001-01-01T00:00:00Z"]:
                adid_value = "—"
        
        st.markdown(f'<p class="info-label">ADID</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="info-value">{adid_value}</p>', unsafe_allow_html=True)
    
    # 2. App information
    st.markdown('<p class="section-header">App information</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f'<p class="info-label">Last app version</p>', unsafe_allow_html=True)
        last_app_version = get_nested_value(device_info, "LastAppVersion", default=get_nested_value(device_info, "last_app_version", default="—"))
        st.markdown(f'<p class="info-value">{last_app_version}</p>', unsafe_allow_html=True)
        
        st.markdown(f'<p class="info-label">Last SDK version</p>', unsafe_allow_html=True)
        last_sdk_version = get_nested_value(device_info, "LastSdkVersion", default=get_nested_value(device_info, "last_sdk_version", default="—"))
        st.markdown(f'<p class="info-value">{last_sdk_version}</p>', unsafe_allow_html=True)
        
        st.markdown(f'<p class="info-label">Last app version short</p>', unsafe_allow_html=True)
        last_app_version_short = get_nested_value(device_info, "LastAppVersionShort", default=get_nested_value(device_info, "last_app_version_short", default="unknown"))
        st.markdown(f'<p class="info-value">{last_app_version_short}</p>', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'<p class="info-label">Last session time</p>', unsafe_allow_html=True)
        last_session = get_nested_value(device_info, "LastSessionTime", default=get_nested_value(device_info, "last_session_time", default="—"))
        st.markdown(f'<p class="info-value">{format_datetime(last_session) if last_session != "—" else "—"}</p>', unsafe_allow_html=True)
        
        st.markdown(f'<p class="info-label">Environment</p>', unsafe_allow_html=True)
        environment = get_nested_value(device_info, "Environment", default=get_nested_value(device_info, "environment", default="production"))
        st.markdown(f'<p class="info-value">{create_badge(environment, "blue")}</p>', unsafe_allow_html=True)
        
        st.markdown(f'<p class="info-label">Install state</p>', unsafe_allow_html=True)
        install_state = get_nested_value(device_info, "InstallState", default=get_nested_value(device_info, "install_state", default="Installed"))
        # Capitalize first letter for display
        install_state_display = install_state.capitalize() if install_state != "—" else "Installed"
        st.markdown(f'<p class="info-value">{create_badge(install_state_display, "green")}</p>', unsafe_allow_html=True)
    
    # 3. Attribution information
    st.markdown('<p class="section-header">Attribution information</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f'<p class="info-label">State</p>', unsafe_allow_html=True)
        state = get_nested_value(device_info, "State", default=get_nested_value(device_info, "attribution", "state", default="Installed"))
        state_display = state.capitalize() if state != "—" else "Installed"
        st.markdown(f'<p class="info-value">{create_badge(state_display, "green")}</p>', unsafe_allow_html=True)
        
        st.markdown(f'<p class="info-label">Link</p>', unsafe_allow_html=True)
        link = get_nested_value(device_info, "Tracker", default=get_nested_value(device_info, "attribution", "link", default="—"))
        st.markdown(f'<p class="info-value">{link}</p>', unsafe_allow_html=True)
        
        st.markdown(f'<p class="info-label">Link name</p>', unsafe_allow_html=True)
        link_name = get_nested_value(device_info, "TrackerName", default=get_nested_value(device_info, "attribution", "link_name", default="—"))
        st.markdown(f'<p class="info-value">{link_name}</p>', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'<p class="info-label">First link</p>', unsafe_allow_html=True)
        first_link = get_nested_value(device_info, "FirstTracker", default=get_nested_value(device_info, "attribution", "first_link", default="—"))
        st.markdown(f'<p class="info-value">{first_link}</p>', unsafe_allow_html=True)
        
        st.markdown(f'<p class="info-label">First link name</p>', unsafe_allow_html=True)
        first_link_name = get_nested_value(device_info, "FirstTrackerName", default=get_nested_value(device_info, "attribution", "first_link_name", default="—"))
        st.markdown(f'<p class="info-value">{first_link_name}</p>', unsafe_allow_html=True)
        
        st.markdown(f'<p class="info-label">Click time</p>', unsafe_allow_html=True)
        click_time = get_nested_value(device_info, "ClickTime", default=get_nested_value(device_info, "attribution", "click_time", default="—"))
        st.markdown(f'<p class="info-value">{format_datetime(click_time) if click_time != "—" else "—"}</p>', unsafe_allow_html=True)
        
        st.markdown(f'<p class="info-label">Install time</p>', unsafe_allow_html=True)
        install_time = get_nested_value(device_info, "InstallTime", default=get_nested_value(device_info, "attribution", "install_time", default="—"))
        st.markdown(f'<p class="info-value">{format_datetime(install_time) if install_time != "—" else "—"}</p>', unsafe_allow_html=True)
    
    # 4. Last event times - Matching the image format exactly
    st.markdown('<p class="section-header">Last event times</p>', unsafe_allow_html=True)
    
    # Recursive function to search for events in JSON
    def find_events_recursive(obj, path=""):
        """Recursively search for event data in JSON structure"""
        events = []
        
        if isinstance(obj, dict):
            # Check if this dict itself contains event-like data
            if "event_name" in obj or "event_token" in obj or "token" in obj:
                events.append(obj)
            
            # Check for common event keys
            for key in ["last_event_times", "events", "device_events", "event_times", "event_data"]:
                if key in obj:
                    value = obj[key]
                    if isinstance(value, list):
                        events.extend(value)
                    elif isinstance(value, dict):
                        # If it's a dict, it might be event_name -> event_data
                        for event_name, event_info in value.items():
                            if isinstance(event_info, dict):
                                event_info["event_name"] = event_info.get("event_name", event_name)
                                events.append(event_info)
                            else:
                                events.append({
                                    "event_name": event_name,
                                    "last_event_time": event_info if isinstance(event_info, str) else None
                                })
            
            # Recursively search nested dicts
            for key, value in obj.items():
                if isinstance(value, (dict, list)):
                    events.extend(find_events_recursive(value, f"{path}.{key}"))
        
        elif isinstance(obj, list):
            # Check if list contains event objects
            for item in obj:
                if isinstance(item, dict) and ("event_name" in item or "event_token" in item or "token" in item):
                    events.append(item)
                elif isinstance(item, (dict, list)):
                    events.extend(find_events_recursive(item, path))
        
        return events
    
    # Try to extract events from various possible locations
    events_data = None
    if isinstance(device_info, dict):
        # First, try direct keys (including LastEventsInfo which is the actual key in Adjust API)
        for key in ["LastEventsInfo", "last_event_times", "lastEventsInfo", "events", "device_events", "event_times", "event_data"]:
            if key in device_info:
                events_data = device_info[key]
                break
        
        # If not found, do recursive search
        if events_data is None:
            found_events = find_events_recursive(device_info)
            if found_events:
                events_data = found_events
        
        # Handle LastEventsInfo structure: {event_token: {name: "...", time: "..."}}
        if isinstance(events_data, dict):
            events_list = []
            for event_token, event_info in events_data.items():
                if isinstance(event_info, dict):
                    # Extract name and time from the event_info dict
                    event_name = event_info.get("name") or event_info.get("event_name") or event_info.get("eventName")
                    event_time = event_info.get("time") or event_info.get("last_event_time") or event_info.get("timestamp")
                    
                    events_list.append({
                        "event_name": event_name or "—",
                        "event_token": event_token,
                        "last_event_time": event_time
                    })
                else:
                    # Simple case: event_token -> timestamp string
                    events_list.append({
                        "event_name": "—",
                        "event_token": event_token,
                        "last_event_time": event_info if isinstance(event_info, str) else None
                    })
            events_data = events_list if events_list else None
    
    if events_data and isinstance(events_data, list) and len(events_data) > 0:
        # Build event table matching the image format
        event_rows = []
        for event in events_data:
            # Try multiple possible field names for event name
            event_name = (event.get("event_name") or event.get("name") or 
                         event.get("eventName") or event.get("event") or "—")
            
            # Try multiple possible field names for event token
            event_token = (event.get("event_token") or event.get("token") or 
                          event.get("eventToken") or event.get("token_id") or "—")
            
            # Try multiple possible field names for timestamp
            last_event_time_utc = (event.get("last_event_time") or event.get("last_time") or 
                                  event.get("lastEventTime") or event.get("timestamp") or 
                                  event.get("time") or "—")
            
            last_event_time_local = format_datetime(last_event_time_utc, "local") if last_event_time_utc != "—" else "—"
            
            event_rows.append({
                "Event name": event_name,
                "Event token": event_token,
                "Last event time (UTC)": format_datetime(last_event_time_utc) if last_event_time_utc != "—" else "—",
                "Last event time (local)": last_event_time_local
            })
        
        if event_rows:
            events_df = pd.DataFrame(event_rows)
            
            # Configure column display - Event tokens should be copyable
            column_config = {
                "Event name": st.column_config.TextColumn(
                    "Event name",
                    width="medium"
                ),
                "Event token": st.column_config.TextColumn(
                    "Event token",
                    width="small",
                    help="Click to copy token"
                ),
                "Last event time (UTC)": st.column_config.TextColumn(
                    "Last event time (UTC)",
                    width="medium"
                ),
                "Last event time (local)": st.column_config.TextColumn(
                    "Last event time (local)",
                    width="medium"
                )
            }
            
            # Display table matching the image format
            st.dataframe(
                events_df,
                use_container_width=True,
                hide_index=True,
                column_config=column_config
            )
        else:
            st.info("No event data available")
    else:
        st.info("No event data available")
        
        # Debug: Show JSON structure to help identify where events are
        with st.expander("🔍 Debug: View JSON structure to find events", expanded=False):
            st.json(device_info)
            st.caption("💡 Look for keys like 'last_event_times', 'events', 'device_events', or any array/list containing event data")
    
    # 5. SDK Signature information
    st.markdown('<p class="section-header">SDK Signature information</p>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'<p class="info-label">Signature verification result</p>', unsafe_allow_html=True)
        sig_verification = get_nested_value(device_info, "SignatureVerificationResult", default=get_nested_value(device_info, "signature_verification_result", default=get_nested_value(device_info, "sdk_signature", "verification_result", default="—")))
        # Format the verification result
        if sig_verification != "—":
            sig_verification_display = sig_verification.replace("_", " ").title() if isinstance(sig_verification, str) else str(sig_verification)
            # Check if it's a valid signature
            if "valid" in sig_verification_display.lower():
                st.markdown(f'<p class="info-value">{create_badge(sig_verification_display, "green")}</p>', unsafe_allow_html=True)
            else:
                st.markdown(f'<p class="info-value">{sig_verification_display}</p>', unsafe_allow_html=True)
        else:
            st.markdown(f'<p class="info-value">{sig_verification}</p>', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'<p class="info-label">Signature acceptance status</p>', unsafe_allow_html=True)
        sig_status = get_nested_value(device_info, "SignatureAcceptanceStatus", default=get_nested_value(device_info, "sdk_signature", "status", default="Accepted"))
        st.markdown(f'<p class="info-value">{create_badge(sig_status, "green")}</p>', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'<p class="info-label">Signature version</p>', unsafe_allow_html=True)
        sig_version = get_nested_value(device_info, "SignatureVersion", default=get_nested_value(device_info, "sdk_signature", "version", default="—"))
        st.markdown(f'<p class="info-value">{sig_version}</p>', unsafe_allow_html=True)
    
    with col4:
        st.markdown(f'<p class="info-label">Secret ID</p>', unsafe_allow_html=True)
        secret_id = get_nested_value(device_info, "SecretId", default=get_nested_value(device_info, "sdk_signature", "secret_id", default="—"))
        st.markdown(f'<p class="info-value">{secret_id}</p>', unsafe_allow_html=True)
