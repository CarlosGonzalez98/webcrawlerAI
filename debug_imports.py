import sys
import os

print("Python executable path:", sys.executable)
print("Python version:", sys.version)
print("Sys.path:", sys.path)

try:
    import gradio
    print("Gradio version:", gradio.__version__)
except ImportError as e:
    print("Error importing gradio:", e)

try:
    from src.webui.interface import theme_map, create_ui
    print("Successfully imported src.webui.interface")
except ImportError as e:
    print("Error importing src.webui.interface:", e)
    
    try:
        import src
        print("src module exists")
        try:
            import src.webui
            print("src.webui module exists")
            print(dir(src.webui))
        except ImportError as e:
            print("Error importing src.webui:", e)
    except ImportError as e:
        print("Error importing src:", e)

print("Current working directory:", os.getcwd()) 