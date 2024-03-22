from hashlib import sha256

from user_agents import parse

from utils import logger


logs = logger.get_logger(__name__)


def generate_unique_id(device: str, os: str, ip: str):
    data_to_hash = f"{device}{os}{ip}"
    logs.info(f"Generating unique ID for: {data_to_hash}")
    hashed_data = sha256(data_to_hash.encode()).hexdigest()
    
    return hashed_data[:12]

def collect_parameters(user_data, request):
    logs.info("Received user data. Parsing user parameters.")
    if user_data.initiator:
        initiator = user_data.initiator
    else:
        logs.info("No initiator provided. Using X-Real-IP.")
        initiator = request.headers.get('X-Real-IP') or request.headers.get('X-Forwarded-For') or request.client.host
    
    user_agent = parse(user_data.user_agent)
    user_parameters = {
        "initiator": initiator,
        "panel_clid": user_data.panel_clid,
        "service_tag": user_data.service_tag,
        "ip": user_data.user_ip,
        "user_agent_full": user_data.user_agent,
        "user_agent_short": str(user_agent),
        "os": user_agent.os.family,
        "os_version": user_agent.os.version_string,
        "browser": user_agent.browser.family,
        "browser_version": user_agent.browser.version_string,
        "device": user_agent.device.family,
        "device_brand": user_agent.device.brand,
        "device_model": user_agent.device.model,
        "is_mobile": user_agent.is_mobile,
        "unique_id": generate_unique_id(
            user_agent.device.family, user_agent.os.family, user_data.user_ip
        ),
    }
    
    return user_parameters

def generate_search_key(user_data):
    try:
        user_agent = parse(user_data.user_agent)
        search_key = generate_unique_id(
            user_agent.device.family,
            user_agent.os.family,
            user_data.user_ip
        )
    except Exception as e:
        logs.error(f"Error generating search key: {e}")
        search_key = None
    logs.info(f"Generated search key: {search_key}")
    
    return search_key
