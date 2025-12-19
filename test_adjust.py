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
APPS_URL = "https://api.adjust.com/v1/apps"  # Common Adjust API endpoint for apps

# Page configuration
st.set_page_config(
    page_title="Testing console - Adjust",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    .info-icon {
        display: inline-block;
        width: 14px;
        height: 14px;
        margin-left: 4px;
        cursor: help;
    }
    </style>
""", unsafe_allow_html=True)

# Function to fetch apps from Adjust API
@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_apps(api_auth_token):
    """Fetch list of apps from Adjust API"""
    headers = {
        "Authorization": f"Bearer {api_auth_token}",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(APPS_URL, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            # Handle different possible response structures
            if isinstance(data, dict):
                apps = data.get("result", data.get("apps", data.get("data", [])))
            elif isinstance(data, list):
                apps = data
            else:
                apps = []
            
            # Extract app_token and app_name
            app_list = []
            for app in apps:
                if isinstance(app, dict):
                    app_token = app.get("app_token") or app.get("token") or app.get("id")
                    app_name = app.get("name") or app.get("app_name") or app.get("title") or app_token
                    if app_token:
                        app_list.append({
                            "app_token": app_token,
                            "app_name": app_name
                        })
            
            return app_list, None
        else:
            return [], f"Failed to fetch apps: {response.status_code} - {response.text}"
    
    except requests.exceptions.RequestException as e:
        return [], f"Error fetching apps: {str(e)}"

# Sidebar for app selection
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Fetch apps
    with st.spinner("Loading apps..."):
        apps_list, apps_error = fetch_apps(API_AUTH_TOKEN)
    
    if apps_error:
        st.error(f"Error loading apps: {apps_error}")
        st.info("You can manually enter the app token below")
        app_token = st.text_input(
            "App Token",
            value=st.session_state.get("app_token", ""),
            help="Enter your Adjust app token manually"
        )
    else:
        if apps_list:
            # Create dropdown options
            app_options = {f"{app['app_name']} ({app['app_token']})": app['app_token'] 
                          for app in apps_list}
            
            selected_app_display = st.selectbox(
                "Select App",
                options=[""] + list(app_options.keys()),
                index=0 if not st.session_state.get("selected_app") else 
                      list(app_options.keys()).index(st.session_state.get("selected_app", "")),
                help="Select an app from your Adjust account"
            )
            
            app_token = app_options.get(selected_app_display, "") if selected_app_display else ""
            st.session_state["selected_app"] = selected_app_display
            
            # Also allow manual entry
            if st.checkbox("Enter app token manually"):
                app_token = st.text_input(
                    "App Token (Manual)",
                    value=app_token,
                    help="Enter app token manually"
                )
        else:
            st.warning("No apps found. Please enter app token manually.")
            app_token = st.text_input(
                "App Token",
                value=st.session_state.get("app_token", ""),
                help="Enter your Adjust app token"
            )
    
    # Save to session state
    st.session_state["app_token"] = app_token
    
    st.divider()
    
    # Auto-refresh settings
    st.subheader("🔄 Auto-refresh")
    auto_refresh = st.checkbox("Enable Auto-refresh", value=False)
    refresh_interval = st.slider(
        "Interval (seconds)",
        min_value=5,
        max_value=60,
        value=10,
        step=5,
        disabled=not auto_refresh
    )

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

# Auto-fetch logic
auto_fetch_triggered = False
if auto_refresh:
    last_fetch = st.session_state.get("last_fetch_time", 0)
    current_time = time.time()
    if current_time - last_fetch >= refresh_interval:
        auto_fetch_triggered = True

# Handle forget device button
if forget_button:
    if "last_device_info" in st.session_state:
        del st.session_state["last_device_info"]
    st.session_state["advertising_id"] = ""
    st.rerun()

# Fetch data when button is clicked or auto-refresh triggers
should_fetch = fetch_button or auto_fetch_triggered

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
        
        st.markdown(f'<p class="info-label">ADID <span class="info-icon">ℹ️</span></p>', unsafe_allow_html=True)
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
        
        st.markdown(f'<p class="info-label">Install state <span class="info-icon">ℹ️</span></p>', unsafe_allow_html=True)
        install_state = get_nested_value(device_info, "InstallState", default=get_nested_value(device_info, "install_state", default="Installed"))
        # Capitalize first letter for display
        install_state_display = install_state.capitalize() if install_state != "—" else "Installed"
        st.markdown(f'<p class="info-value">{create_badge(install_state_display, "green")}</p>', unsafe_allow_html=True)
    
    # 3. Attribution information
    st.markdown('<p class="section-header">Attribution information</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f'<p class="info-label">State <span class="info-icon">ℹ️</span></p>', unsafe_allow_html=True)
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
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f'<p class="info-label">Signature acceptance status <span class="info-icon">ℹ️</span></p>', unsafe_allow_html=True)
        sig_status = get_nested_value(device_info, "SignatureAcceptanceStatus", default=get_nested_value(device_info, "sdk_signature", "status", default="Accepted"))
        st.markdown(f'<p class="info-value">{create_badge(sig_status, "green")}</p>', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'<p class="info-label">Signature version <span class="info-icon">ℹ️</span></p>', unsafe_allow_html=True)
        sig_version = get_nested_value(device_info, "SignatureVersion", default=get_nested_value(device_info, "sdk_signature", "version", default="—"))
        st.markdown(f'<p class="info-value">{sig_version}</p>', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'<p class="info-label">Secret ID <span class="info-icon">ℹ️</span></p>', unsafe_allow_html=True)
        secret_id = get_nested_value(device_info, "SecretId", default=get_nested_value(device_info, "sdk_signature", "secret_id", default="—"))
        st.markdown(f'<p class="info-value">{secret_id}</p>', unsafe_allow_html=True)

# Auto-refresh status
if auto_refresh and "last_fetch_time" in st.session_state:
    current_time = time.time()
    elapsed = current_time - st.session_state.get("last_fetch_time", current_time)
    remaining = max(0, refresh_interval - elapsed)
    
    if remaining > 0:
        progress = 1 - (remaining / refresh_interval)
        st.progress(progress)
        st.caption(f"🔄 Auto-refresh enabled | Next refresh in {int(remaining)} seconds")
