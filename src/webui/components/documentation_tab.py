import gradio as gr
from gradio.components import Component
from src.webui.webui_manager import WebuiManager


def create_documentation_tab(webui_manager: WebuiManager):
    """
    Creates a documentation tab with detailed project analysis.
    """
    tab_components = {}

    with gr.Group():
        gr.Markdown(
            """
            # Browser Use WebUI Documentation
            
            This documentation provides a comprehensive overview of the Browser Use WebUI project.
            """,
            elem_classes=["tab-header-text"],
        )

    with gr.Tabs() as doc_tabs:
        with gr.TabItem("Project Overview"):
            gr.Markdown(
                """
                ## Project Overview
                
                Browser Use WebUI is a Gradio-based interface for controlling and interacting with web browsers using AI assistance. 
                It provides a user-friendly way to automate browser tasks and research using large language models.
                
                ### Key Features
                
                - **AI-Controlled Browser**: Control Chrome or other browsers with AI assistance
                - **OpenAI LLM Support**: Compatible with OpenAI models including GPT-4 and GPT-3.5
                - **Custom Browser Support**: Use your own browser with persistent sessions
                - **Deep Research Agent**: Specialized agent for conducting in-depth web research
                
                ### Recent Updates
                
                As of the latest version, the system has been streamlined to support only OpenAI as the LLM provider. This change:
                
                - Simplifies the codebase and reduces dependencies
                - Focuses development efforts on optimizing the OpenAI integration
                - Ensures consistent behavior across all agent interactions
                - Improves reliability and reduces potential configuration issues
                
                If you were using other LLM providers with previous versions, please update your configurations to use OpenAI.
                """
            )
            
        with gr.TabItem("Submit Task Flow"):
            gr.Markdown(
                """
                ## BrowserUse Agent: Submit Task Flow Documentation

                This documentation provides a detailed overview of what happens when you click the "Submit Task" button in the BrowserUse agent tab.

                ### Files Involved

                - **browser_use_agent_tab.py**: Creates the UI for the BrowserUse agent tab and handles the submit task workflow.
                - **webui_manager.py**: Maintains the state of the web UI and stores components and agent instances.
                - **browser_use_agent.py**: Implements the core BrowserUse agent functionality for running tasks.
                - **custom_controller.py**: Handles the execution of browser actions requested by the agent.
                - **custom_browser.py**: Custom browser implementation for the BrowserUse agent.
                - **custom_context.py**: Manages browser contexts for the BrowserUse agent.

                ### Step-by-Step Process

                #### Step 1: User Submits a Task
                
                The process begins when a user enters a task in the text input field and clicks the "Submit Task" button, triggering the `handle_submit` function.

                #### Step 2: Task Initialization
                
                The `run_agent_task` function retrieves the user's task from UI components, updates the chat history, and initializes UI components for the task execution.

                #### Step 3: Browser and Context Setup
                
                The system initializes or reuses an existing browser instance and browser context, which provide the environment for the agent to interact with web pages.

                #### Step 4: Agent Initialization
                
                The system creates a new BrowserUseAgent instance or updates an existing one with the new task. It also registers callbacks for step updates and task completion.

                #### Step 5: Task Execution
                
                The system executes the agent's `run` method in a new task and waits for its completion, updating the UI with progress.

                #### Step 6: BrowserUseAgent Run Method
                
                The agent's `run` method is the core execution logic that performs the task through a series of steps, each interacting with the browser to accomplish the given task.

                #### Step 7: Step Processing Callback
                
                The `_handle_new_step` callback is called after each agent step, updating the UI with the latest screenshot and agent output.

                #### Step 8: Task Completion Callback
                
                The `_handle_done` callback is triggered when the agent completes the task (success or failure), updating the UI with the final results and metrics.

                ### System Flow Diagram

                ```
                User submits task → Task initialization → Browser setup → Agent initialization
                                                                                   ↓
                Task completion ← Agent run method ← Step processing callback ← Task execution
                ```
                """
            )

        with gr.TabItem("Architecture"):
            gr.Markdown(
                """
                ## System Architecture
                
                The project follows a modular architecture with clear separation of concerns:
                
                ### Core Components
                
                1. **WebUI Module (`src/webui/`)**: 
                   - Interface management using Gradio
                   - Tab components for different functionalities
                   - User input/output handling
                
                2. **Browser Module (`src/browser/`)**: 
                   - Custom browser implementation extending browser-use library
                   - Browser context management
                   - Screenshot and session handling
                
                3. **Agent Module (`src/agent/`)**: 
                   - Browser Use Agent: General-purpose browser automation
                   - Deep Research Agent: Specialized for research tasks
                   - Agent state and history management
                
                4. **Controller Module (`src/controller/`)**: 
                   - Action registry for browser control
                   - MCP client integration
                   - Custom action implementations
                
                5. **Utils Module (`src/utils/`)**: 
                   - OpenAI LLM integration
                   - Configuration helpers
                   - MCP client setup
                
                ### Data Flow
                
                1. User inputs task via WebUI
                2. WebUI Manager initializes components
                3. Agent receives task and configures OpenAI LLM
                4. Browser is launched or connected
                5. Agent iteratively performs actions via controller
                6. Results display in WebUI with screenshots
                """
            )
            
        with gr.TabItem("Browser Control"):
            gr.Markdown(
                """
                ## Browser Control System
                
                The browser control functionality is built on the browser-use library, with custom extensions:
                
                ### Browser Features
                
                - **Custom Browser Integration**: Connect to existing browser instances
                - **Browser Context Management**: Create and manage browser contexts
                - **Session Persistence**: Keep browser open between tasks
                - **Screenshot Capture**: Take and display screenshots of browser state
                - **DOM Interaction**: Interact with web page elements
                - **Action Registry**: Comprehensive set of browser actions
                
                ### Actions Supported
                
                - Navigate to URLs
                - Click elements
                - Input text
                - Extract content
                - Scroll pages
                - Search Google
                - Wait for page load
                - Handle alerts and dialogs
                - Upload files
                - And more through the registry system
                """
            )
            
        with gr.TabItem("Agent System"):
            gr.Markdown(
                """
                ## Agent System
                
                The application provides two main agent types:
                
                ### Browser Use Agent
                
                Extends the base Agent class from browser-use library to provide:
                
                - Task execution with dynamic tool selection
                - LLM integration with multiple providers
                - Browser control through registered actions
                - Error handling and recovery
                - Execution history tracking
                
                ### Deep Research Agent
                
                Specialized agent using LangGraph for:
                
                - Research planning through LLM
                - Web search and content extraction
                - Information synthesis
                - Structured research report generation
                - Multi-browser parallel processing
                
                ### Agent Components
                
                - **State Management**: Track agent state during execution
                - **History Recording**: Record steps and results
                - **Output Formatting**: Format results for display
                - **Tool Calling**: Different methods based on LLM capabilities
                """
            )
            
        with gr.TabItem("LLM Integration"):
            gr.Markdown(
                """
                ## LLM Integration
                
                The system supports OpenAI LLM:
                
                ### Supported Provider
                
                - **OpenAI**: GPT-4o, GPT-4, GPT-3.5
                
                ### Integration Features
                
                - **Vision Support**: Vision capabilities with compatible models
                - **Temperature Control**: Adjust randomness in model outputs
                - **Context Length Management**: Handle different model context limits
                - **API Key Management**: Secure handling of API credentials
                - **Tool Calling Methods**: Different methods based on model capabilities (function_calling, json_mode, raw)
                """
            )
            
        with gr.TabItem("Web UI Components"):
            gr.Markdown(
                """
                ## Web UI Components
                
                The interface is built with Gradio and organized into tabs:
                
                ### Main Tabs
                
                1. **Agent Settings**: Configure OpenAI models and parameters
                2. **Browser Settings**: Set up browser preferences and options
                3. **Run Agent**: Execute browser tasks and view results
                4. **Agent Marketplace**: Access specialized agents like Deep Research
                5. **Documentation**: Comprehensive project documentation (you are here)
                6. **Load & Save Config**: Save and load UI configurations
                
                ### Interface Features
                
                - **Chatbot Interface**: View agent interactions and results
                - **Task Input**: Submit tasks to the agent
                - **Control Buttons**: Start, stop, pause, and clear agent execution
                - **Configuration Forms**: Set up OpenAI and browser parameters
                - **Results Display**: View agent output including screenshots
                """
            )

        with gr.TabItem("API & Libraries"):
            gr.Markdown(
                """
                ## Core Libraries & Dependencies
                
                The project relies on several key libraries:
                
                ### Primary Dependencies
                
                - **browser-use**: Core browser automation library
                - **gradio**: Web UI framework
                - **langchain**: LLM integration framework
                - **langgraph**: Graph-based workflows for agents
                - **playwright**: Browser automation and control
                - **pyperclip**: Clipboard interaction
                - **dotenv**: Environment variable management
                
                ### API Integration
                
                - **LLM APIs**: OpenAI, Google, Azure, Anthropic, etc.
                - **MCP (Modular Coordination Protocol)**: Tool integration protocol
                - **MainContentExtractor**: Web content extraction
                
                ### Browser APIs
                
                - **CDP (Chrome DevTools Protocol)**: Browser communication
                - **WSS**: WebSocket connections for browser control
                """
            )
            
        with gr.TabItem("File Structure"):
            gr.Markdown(
                """
                ## Project File Structure
                
                ```
                web-ui/
                ├── src/
                │   ├── agent/
                │   │   ├── browser_use/
                │   │   │   └── browser_use_agent.py
                │   │   └── deep_research/
                │   │       └── deep_research_agent.py
                │   ├── browser/
                │   │   ├── custom_browser.py
                │   │   └── custom_context.py
                │   ├── controller/
                │   │   └── custom_controller.py
                │   ├── utils/
                │   │   ├── config.py
                │   │   ├── llm_provider.py
                │   │   └── mcp_client.py
                │   ├── webui/
                │   │   ├── components/
                │   │   │   ├── agent_settings_tab.py
                │   │   │   ├── browser_settings_tab.py
                │   │   │   ├── browser_use_agent_tab.py
                │   │   │   ├── deep_research_agent_tab.py
                │   │   │   ├── documentation_tab.py
                │   │   │   └── load_save_config_tab.py
                │   │   ├── interface.py
                │   │   └── webui_manager.py
                │   └── __init__.py
                ├── assets/
                ├── tmp/
                ├── tests/
                ├── .venv/
                ├── webui.py
                ├── Dockerfile
                ├── docker-compose.yml
                ├── requirements.txt
                ├── setup.py
                └── README.md
                ```
                """
            )
            
        with gr.TabItem("Setup & Usage"):
            gr.Markdown(
                """
                ## Setup & Usage Guide
                
                ### Installation
                
                #### Local Installation
                
                1. Clone the repository
                   ```bash
                   git clone https://github.com/browser-use/web-ui.git
                   cd web-ui
                   ```
                
                2. Set up Python environment
                   ```bash
                   uv venv --python 3.11
                   source .venv/bin/activate  # Linux/Mac
                   .venv\\Scripts\\activate    # Windows
                   ```
                
                3. Install dependencies
                   ```bash
                   uv pip install -r requirements.txt
                   playwright install --with-deps
                   ```
                
                4. Configure environment
                   ```bash
                   cp .env.example .env
                   # Edit .env to add your API keys
                   ```
                
                5. Run the application
                   ```bash
                   python webui.py --ip 127.0.0.1 --port 7788
                   ```
                
                #### Docker Installation
                
                ```bash
                docker compose up --build
                ```
                
                ### Usage Examples
                
                1. **Simple Web Search**
                   - Configure LLM in Agent Settings
                   - Configure browser in Browser Settings
                   - In Run Agent tab, enter: "Search for the latest news about AI"
                   - Click Submit Task
                
                2. **Deep Research**
                   - Configure LLM in Agent Settings
                   - Go to Agent Marketplace > Deep Research
                   - Enter research topic: "Advances in renewable energy in 2023"
                   - Click Run
                
                3. **Using Custom Browser**
                   - In Browser Settings, check "Use Own Browser"
                   - Configure paths to browser and user data
                   - Submit tasks as normal
                """
            )
            
        with gr.TabItem("Source Code Analysis"):
            gr.Markdown(
                """
                ## Detailed Source Code Analysis
                
                This section provides a deep dive into the code structure and implementation details of key components.
                
                ### WebUI Manager Class
                
                The `WebuiManager` class in `src/webui/webui_manager.py` serves as the central component managing UI elements and application state:
                
                ```python
                class WebuiManager:
                    def __init__(self, settings_save_dir: str = "./tmp/webui_settings"):
                        self.id_to_component: dict[str, Component] = {}
                        self.component_to_id: dict[Component, str] = {}
                        self.settings_save_dir = settings_save_dir
                        os.makedirs(self.settings_save_dir, exist_ok=True)
                ```
                
                Key functions:
                - `add_components()`: Registers UI components with unique IDs
                - `get_component_by_id()`: Retrieves components using their ID
                - `save_config()`: Serializes UI settings to JSON
                - `load_config()`: Loads settings from JSON
                - `init_browser_use_agent()`: Creates browser agent instances
                
                ### Custom Browser Implementation
                
                The `CustomBrowser` class in `src/browser/custom_browser.py` extends the base `Browser` class from the browser-use library:
                
                ```python
                class CustomBrowser(Browser):
                    async def new_context(self, config: BrowserContextConfig | None = None) -> CustomBrowserContext:
                        browser_config = self.config.model_dump() if self.config else {}
                        context_config = config.model_dump() if config else {}
                        merged_config = {**browser_config, **context_config}
                        return CustomBrowserContext(config=BrowserContextConfig(**merged_config), browser=self)
                ```
                
                Key features:
                - Extends the browser-use Browser class
                - Creates custom browser contexts
                - Configures Chrome arguments for different environments
                - Handles screen resolution and window dimensions
                
                ### Browser Use Agent
                
                The `BrowserUseAgent` class in `src/agent/browser_use/browser_use_agent.py` extends the Agent class:
                
                ```python
                class BrowserUseAgent(Agent):
                    def _set_tool_calling_method(self) -> ToolCallingMethod | None:
                        tool_calling_method = self.settings.tool_calling_method
                        if tool_calling_method == 'auto':
                            if is_model_without_tool_support(self.model_name):
                                return 'raw'
                            elif self.chat_model_library == 'ChatGoogleGenerativeAI':
                                return None
                            elif self.chat_model_library == 'ChatOpenAI':
                                return 'function_calling'
                            # Additional models...
                ```
                
                Key capabilities:
                - Automatically selects tool calling method based on LLM
                - Handles agent execution with configurable steps
                - Provides pause/resume functionality
                - Manages execution history and state
                - Implements error handling and recovery
                
                ### Deep Research Agent
                
                The `DeepResearchAgent` class in `src/agent/deep_research/deep_research_agent.py` implements a specialized research agent:
                
                ```python
                class DeepResearchAgent:
                    def __init__(
                        self,
                        llm: Any,
                        browser_config: Dict[str, Any],
                        mcp_server_config: Optional[Dict[str, Any]] = None,
                    ):
                        # Initialize agent with LLM and browser config
                ```
                
                Key components:
                - Uses LangGraph for structured research workflows
                - Implements planning, research, and synthesis nodes
                - Manages parallel browser instances for efficiency
                - Generates structured research reports
                - Handles task state persistence
                
                ### Custom Controller
                
                The `CustomController` class in `src/controller/custom_controller.py` extends the Controller class:
                
                ```python
                class CustomController(Controller):
                    def __init__(self, exclude_actions: list[str] = [],
                                output_model: Optional[Type[BaseModel]] = None,
                                ask_assistant_callback: Optional[...] = None):
                        super().__init__(exclude_actions=exclude_actions, output_model=output_model)
                        self._register_custom_actions()
                        self.ask_assistant_callback = ask_assistant_callback
                        self.mcp_client = None
                        self.mcp_server_config = None
                ```
                
                Key features:
                - Registers custom browser actions
                - Integrates with MCP (Modular Coordination Protocol)
                - Provides file upload capabilities
                - Implements human assistance features
                - Handles action execution with error management
                
                ### UI Components
                
                The UI is built using Gradio components:
                
                ```python
                def create_ui(theme_name="Ocean"):
                    with gr.Blocks(title="Browser Use WebUI", theme=theme_map[theme_name], css=css, js=js_func) as demo:
                        with gr.Tabs() as tabs:
                            with gr.TabItem("⚙️ Agent Settings"):
                                create_agent_settings_tab(ui_manager)
                            # Additional tabs...
                ```
                
                Key UI features:
                - Modular tab-based interface
                - Customizable themes
                - Responsive layout
                - Dark mode support
                - Configuration persistence
                """
            )
            
        with gr.TabItem("Technical Challenges"):
            gr.Markdown(
                """
                ## Technical Challenges & Solutions
                
                This section covers key technical challenges faced during development and the solutions implemented.
                
                ### Browser Integration Challenges
                
                **Challenge**: Connecting to existing browser instances with proper user profiles.
                
                **Solution**: Custom implementation using CDP (Chrome DevTools Protocol) and WebSocket connections:
                
                ```python
                # Implementation in custom_browser.py
                chrome_args = {
                    f'--remote-debugging-port={self.config.chrome_remote_debugging_port}',
                    *(CHROME_DOCKER_ARGS if IN_DOCKER else []),
                    *(CHROME_HEADLESS_ARGS if self.config.headless else []),
                    # Additional args...
                }
                
                # Check existing port conflicts
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    if s.connect_ex(('localhost', self.config.chrome_remote_debugging_port)) == 0:
                        chrome_args.remove(f'--remote-debugging-port={self.config.chrome_remote_debugging_port}')
                ```
                
                ### OpenAI LLM Integration
                
                **Challenge**: Configuring and optimizing OpenAI models for browser automation.
                
                **Solution**: Provider abstraction and method detection:
                
                ```python
                # In browser_use_agent.py
                def _set_tool_calling_method(self) -> ToolCallingMethod | None:
                    tool_calling_method = self.settings.tool_calling_method
                    if tool_calling_method == 'auto':
                        if is_model_without_tool_support(self.model_name):
                            return 'raw'
                        else:
                            return 'function_calling'
                ```
                
                ### Execution State Management
                
                **Challenge**: Maintaining agent state across steps and allowing pause/resume.
                
                **Solution**: Custom execution loop with state management:
                
                ```python
                # In browser_use_agent.py
                async def run(self, max_steps: int = 100, on_step_start: AgentHookFunc | None = None,
                        on_step_end: AgentHookFunc | None = None) -> AgentHistoryList:
                    
                    # Execution loop with state management
                    for step in range(max_steps):
                        # Check pause state
                        if self.state.paused:
                            signal_handler.wait_for_resume()
                            signal_handler.reset()
                            
                        # Check for stop
                        if self.state.stopped:
                            logger.info('Agent stopped')
                            break
                            
                        # Execute step with callbacks
                        if on_step_start is not None:
                            await on_step_start(self)
                            
                        step_info = AgentStepInfo(step_number=step, max_steps=max_steps)
                        await self.step(step_info)
                        
                        if on_step_end is not None:
                            await on_step_end(self)
                ```
                
                ### Multi-Browser Research Orchestration
                
                **Challenge**: Managing multiple parallel browser instances for research tasks.
                
                **Solution**: LangGraph-based workflow with parallel task execution:
                
                ```python
                # In deep_research_agent.py
                async def _run_browser_search_tool(
                    queries: List[str],
                    task_id: str,
                    llm: Any,
                    browser_config: Dict[str, Any],
                    stop_event: threading.Event,
                    max_parallel_browsers: int = 1,
                ) -> List[Dict[str, Any]]:
                    
                    # Execute tasks in parallel with limit
                    tasks = []
                    results = []
                    
                    semaphore = asyncio.Semaphore(max_parallel_browsers)
                    
                    async def task_wrapper(query):
                        async with semaphore:
                            return await run_single_browser_task(
                                query, task_id, llm, browser_config, stop_event
                            )
                            
                    # Create and gather tasks
                    for query in queries:
                        tasks.append(asyncio.create_task(task_wrapper(query)))
                    
                    results = await asyncio.gather(*tasks)
                    return results
                ```
                
                ### UI State Synchronization
                
                **Challenge**: Keeping UI state synchronized with backend operations.
                
                **Solution**: Component tracking and event-based updates:
                
                ```python
                # In webui_manager.py
                def add_components(self, tab_name: str, components_dict: dict[str, "Component"]) -> None:
                    for comp_name, component in components_dict.items():
                        comp_id = f"{tab_name}.{comp_name}"
                        self.id_to_component[comp_id] = component
                        self.component_to_id[component] = comp_id
                
                # In browser_use_agent_tab.py
                async def handle_submit(webui_manager: WebuiManager, components: Dict[gr.components.Component, Any]):
                    # Get component values and update UI state
                    task_input = _get_config_value(webui_manager, components, "user_input", "")
                    webui_manager.bu_chat_history.append({"role": "user", "content": task_input})
                    # Additional UI updates...
                ```
                
                ### Docker Environment Challenges
                
                **Challenge**: Running browser automation in Docker containers.
                
                **Solution**: Special Docker configuration for browser support:
                
                ```python
                # In custom_browser.py
                CHROME_DOCKER_ARGS = [
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    # Additional docker-specific args...
                ]
                
                # In docker-compose.yml
                services:
                  web-ui:
                    build:
                      context: .
                    volumes:
                      - ./tmp:/app/tmp
                    ports:
                      - "7788:7788"
                      - "6080:6080"  # VNC for browser viewing
                    environment:
                      - DISPLAY=:1
                      # Additional environment variables...
                ```
                """
            )

    tab_components.update(dict(
        doc_tabs=doc_tabs,
    ))
    
    webui_manager.add_components("documentation", tab_components)
    
    return tab_components 