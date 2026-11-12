from dotenv import load_dotenv
load_dotenv()

from langfuse import get_client

langfuse = get_client()