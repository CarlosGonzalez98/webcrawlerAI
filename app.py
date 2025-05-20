from dotenv import load_dotenv
load_dotenv()
import os
from src.webui.interface import theme_map, create_ui

def get_default_theme():
    # Use "Ocean" or the first available theme
    return "Ocean" if "Ocean" in theme_map else list(theme_map.keys())[0]

def run_gradio():
    # Hugging Face Spaces: use default host/port, no CLI args
    theme = os.environ.get("GRADIO_THEME", get_default_theme())
    demo = create_ui(theme_name=theme)
    demo.queue().launch()  # Do NOT set server_name/server_port for Spaces

if __name__ == '__main__':
    # If running locally, allow CLI args as before
    import argparse
    parser = argparse.ArgumentParser(description="Gradio WebUI for Browser Agent")
    parser.add_argument("--ip", type=str, default="127.0.0.1", help="IP address to bind to")
    parser.add_argument("--port", type=int, default=8888, help="Port to listen on")
    parser.add_argument("--theme", type=str, default=get_default_theme(), choices=theme_map.keys(), help="Theme to use for the UI")
    args = parser.parse_args()

    demo = create_ui(theme_name=args.theme)
    print(f"Starting server on {args.ip}:{args.port}")
    demo.queue().launch(server_name=args.ip, server_port=args.port)
else:
    # If run by Hugging Face Spaces (no __main__), just launch with defaults
    run_gradio()