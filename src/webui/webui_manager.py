import json
from collections.abc import Generator
from typing import TYPE_CHECKING
import os
import gradio as gr
from datetime import datetime
from typing import Optional, Dict, List, Any
import uuid
import asyncio

from gradio.components import Component
from browser_use.browser.browser import Browser
from browser_use.browser.context import BrowserContext
from browser_use.agent.service import Agent
from src.browser.custom_browser import CustomBrowser
from src.browser.custom_context import CustomBrowserContext
from src.controller.custom_controller import CustomController
from src.agent.deep_research.deep_research_agent import DeepResearchAgent


class WebuiManager:
    def __init__(self, settings_save_dir: str = "./tmp/webui_settings"):
        self.id_to_component: dict[str, Component] = {}
        self.component_to_id: dict[Component, str] = {}

        self.settings_save_dir = settings_save_dir
        os.makedirs(self.settings_save_dir, exist_ok=True)

        # Add type annotation for vayner_pdf_report
        self.vayner_pdf_report: Optional[str] = None

    def init_browser_use_agent(self) -> None:
        """
        init browser use agent
        """
        self.bu_agent: Optional[Agent] = None
        self.bu_browser: Optional[CustomBrowser] = None
        self.bu_browser_context: Optional[CustomBrowserContext] = None
        self.bu_controller: Optional[CustomController] = None
        self.bu_chat_history: List[Dict[str, Optional[str]]] = []
        self.bu_response_event: Optional[asyncio.Event] = None
        self.bu_user_help_response: Optional[str] = None
        self.bu_current_task: Optional[asyncio.Task] = None
        self.bu_agent_task_id: Optional[str] = None
        self.bu_task_metrics: Optional[Dict[str, Any]] = None
        
    def init_vayner_client_research(self) -> None:
        """
        Initialize Vayner Client Research components and state
        """
        if not hasattr(self, "vayner_chat_history"):
            self.vayner_chat_history = []
        
        if not hasattr(self, "vayner_pdf_report"):
            self.vayner_pdf_report = None
            
        if not hasattr(self, "vayner_controller"):
            self.vayner_controller = None
            
        if not hasattr(self, "vayner_browser"):
            self.vayner_browser = None
            
        if not hasattr(self, "vayner_browser_context"):
            self.vayner_browser_context = None
            
        if not hasattr(self, "vayner_agent"):
            self.vayner_agent = None
            
        if not hasattr(self, "vayner_current_task"):
            self.vayner_current_task = None
            
        # Initialize data collections for PDF report
        if not hasattr(self, "vayner_screenshots"):
            self.vayner_screenshots = []
            
        if not hasattr(self, "vayner_business_info"):
            self.vayner_business_info = []
            
        if not hasattr(self, "vayner_keyword_data"):
            self.vayner_keyword_data = []
            
        if not hasattr(self, "vayner_ranking_data"):
            self.vayner_ranking_data = []
            
        if not hasattr(self, "vayner_current_business"):
            self.vayner_current_business = "Unknown Business"
            
        # New: keyword table rows for third page
        if not hasattr(self, "vayner_keyword_table_rows"):
            self.vayner_keyword_table_rows = []
            
        # Queue for updates during task execution
        if not hasattr(self, "update_queue"):
            self.update_queue = []

    def init_deep_research_agent(self) -> None:
        """
        init deep research agent
        """
        self.dr_agent: Optional[DeepResearchAgent] = None
        self.dr_current_task = None
        self.dr_agent_task_id: Optional[str] = None
        self.dr_save_dir: Optional[str] = None

    def add_components(self, tab_name: str, components_dict: dict[str, "Component"]) -> None:
        """
        Add tab components
        """
        for comp_name, component in components_dict.items():
            comp_id = f"{tab_name}.{comp_name}"
            self.id_to_component[comp_id] = component
            self.component_to_id[component] = comp_id

    def get_components(self) -> list["Component"]:
        """
        Get all components
        """
        return list(self.id_to_component.values())

    def get_component_by_id(self, comp_id: str) -> Optional["Component"]:
        """
        Get component by id. Returns None if not found.
        """
        return self.id_to_component.get(comp_id, None)

    def get_id_by_component(self, comp: "Component") -> str:
        """
        Get id by component. Raises KeyError if not found.
        """
        return self.component_to_id[comp]

    def save_config(self, components: Dict["Component", str]) -> str:
        """
        Save config
        """
        cur_settings = {}
        for comp in components:
            if not isinstance(comp, gr.Button) and not isinstance(comp, gr.File) and str(
                    getattr(comp, "interactive", True)).lower() != "false":
                comp_id = self.get_id_by_component(comp)
                cur_settings[comp_id] = components[comp]

        config_name = datetime.now().strftime("%Y%m%d-%H%M%S")
        with open(os.path.join(self.settings_save_dir, f"{config_name}.json"), "w") as fw:
            json.dump(cur_settings, fw, indent=4)

        return os.path.join(self.settings_save_dir, f"{config_name}.json")

    def load_config(self, config_path: str):
        """
        Load config
        """
        with open(config_path, "r") as fr:
            ui_settings = json.load(fr)

        update_components = {}
        for comp_id, comp_val in ui_settings.items():
            if comp_id in self.id_to_component:
                comp = self.id_to_component[comp_id]
                update_components[comp] = gr.update(value=comp_val)

        config_status = self.id_to_component["load_save_config.config_status"]
        update_components.update(
            {
                config_status: gr.update(value=f"Successfully loaded config: {config_path}")
            }
        )
        yield update_components
