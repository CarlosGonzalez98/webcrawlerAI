import gradio as gr
from gradio import themes

from src.webui.webui_manager import WebuiManager
from src.webui.components.agent_settings_tab import create_agent_settings_tab
from src.webui.components.browser_settings_tab import create_browser_settings_tab
from src.webui.components.browser_use_agent_tab import create_browser_use_agent_tab
from src.webui.components.deep_research_agent_tab import create_deep_research_agent_tab
from src.webui.components.load_save_config_tab import create_load_save_config_tab
from src.webui.components.documentation_tab import create_documentation_tab
from src.webui.components.vayner_client_research_tab import create_vayner_client_research_tab

theme_map = {
    "Default": themes.Default(),
    "Soft": themes.Soft(),
    "Monochrome": themes.Monochrome(),
    "Glass": themes.Glass(),
    "Origin": themes.Origin(),
    "Citrus": themes.Citrus(),
    "Ocean": themes.Ocean(),
    "Base": themes.Base()
}


def create_ui(theme_name="Ocean"):
    css = """
    .gradio-container {
        width: 100vw !important; 
        max-width: 100% !important; 
        margin-left: auto !important;
        margin-right: auto !important;
        padding-top: 10px !important;
    }
    .header-text {
        text-align: center;
        margin-bottom: 20px;
    }
    .tab-header-text {
        text-align: center;
    }
    .theme-section {
        margin-bottom: 10px;
        padding: 15px;
        border-radius: 10px;
    }
    """

    # dark mode in default
    js_func = """
    function refresh() {
        const url = new URL(window.location);

        if (url.searchParams.get('__theme') !== 'dark') {
            url.searchParams.set('__theme', 'dark');
            window.location.href = url.href;
        }
    }
    """

    ui_manager = WebuiManager()

    with gr.Blocks(
            title="Browser Use WebUI", theme=theme_map[theme_name], css=css, js=js_func,
    ) as demo:
        with gr.Row():
            gr.Markdown(
                """
                # 🌐 Browser Use WebUI
                ### Control your browser with AI assistance
                """,
                elem_classes=["header-text"],
            )

        with gr.Tabs() as tabs:
            with gr.TabItem("Vayner Client Research"):
                create_vayner_client_research_tab(ui_manager)

            with gr.TabItem("📚 Documentation"):
                create_documentation_tab(ui_manager)

    return demo
