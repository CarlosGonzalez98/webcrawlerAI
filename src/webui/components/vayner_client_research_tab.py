import asyncio
import json
import logging
import os
from typing import Any, AsyncGenerator, Dict, List, Optional
from datetime import datetime

import gradio as gr
from gradio.components import Component

from src.agent.browser_use.browser_use_agent import BrowserUseAgent
from src.browser.custom_browser import CustomBrowser
from src.controller.custom_controller import CustomController
from src.utils import llm_provider
from src.webui.webui_manager import WebuiManager
from browser_use.browser.browser import BrowserConfig
from browser_use.browser.context import BrowserContext, BrowserContextConfig

logger = logging.getLogger(__name__)

# Import environment variables
from dotenv import load_dotenv
load_dotenv()  # This ensures environment variables are loaded

# Get Vayner credentials from environment
VAYNER_USERNAME = os.getenv("VAYNER_USERNAME", "")
VAYNER_PASSWORD = os.getenv("VAYNER_PASSWORD", "")

VAYNER_CLIENT_TEMPLATE = """
Task: Research Vayner Commerce data for business: "{business_name}"

1. Log in to https://local.vaynercommerce.com/myclients  
   - Username: admin@vaynercommerce.com  
   - Password: oKLl4li-HY  
   - Use these credentials on the login form

2. After successful login, search for the business named "{business_name}" in the search box  
3. Click on the business in the search results  

**Part 1: Keyword Performance Table**
4. Extract the keyword performance table (columns: Keyword, Performance, Status)  
   - Return this as a formatted table

**Part 2: Keyword Ranking History Analysis Table**
5. For the first keyword in the list:  
   a. Click on the keyword to open its detail view  
   b. Look for the **History** section 

   c. Click the **last row (earliest date)** in the History section:  
       -extract:  
         - Top 3 Rank → This is the **Initial Top 3 Rank (SOV)**  
         - Coverage → This is the **Initial Coverage**  
       - Then look for the **Your Rankings** section (while this row is selected), extract:  
         - ARP → This is the **Initial ARP**

   d. Then again the table under the **History** section, click the **first row (most recent date)** in the History section:  
       - From the **History section**, extract:  
         - Top 3 Rank → This is the **Current Rank (SOV) in our table**  
         - Coverage → This is the **Current Coverage**  
       - Then look for the **Your Rankings** section  (while this row is selected), extract:  
         - ARP → This is the **Current Scan ARP**

6. Go back to the Keywords list and repeat Step 5 for the second keyword in the list.


Please provide:

- The complete keyword performance data as a 1 table.
- Another new table that Return all of information from **Part 2: Keyword Ranking History Analysis Table** as a second table with the following columns:  
   - Keyword  
   - Initial ARP  
   - Initial Top 3 Rank (SOV)  
   - Initial Coverage  
   - Current Scan ARP  
   - Current Rank (SOV)  
   - Current Coverage
   At the bottom of the table, compute and include a final row labeled "Average" showing the average of all numeric columns (excluding the "Keyword" column).

   """


# Function to generate PDF-like report from task results
def generate_pdf_report(business_name, history):
    """
    Generate HTML for a PDF-like report based on the agent's history data
    """
    # Extract relevant information from history
    final_result = history.final_result() or {}
    screenshots = []
    keyword_data = []
    ranking_data = []
    performance_data = []
    
    # Process agent history to extract information
    try:
        # The history object is itself iterable
        for item in history:
            try:
                # Extract screenshot if available
                if hasattr(item, "state") and hasattr(item.state, "screenshot"):
                    if item.state.screenshot and isinstance(item.state.screenshot, str) and len(item.state.screenshot) > 100:
                        screenshots.append(item.state.screenshot)
                
                # Extract data from actions
                if hasattr(item, "output") and item.output:
                    for action in item.output.action:
                        if hasattr(action, "thought"):
                            thought = action.thought.lower() if action.thought else ""
                            
                            # Look for keyword data in thoughts
                            if "keyword" in thought and ("performance" in thought or "score" in thought):
                                keyword_data.append(action.thought)
                            # Check if action contains ranking data
                            elif "ranking" in thought or "rank" in thought:
                                ranking_data.append(action.thought)
                            # Check if action contains performance data
                            elif "performance" in thought and "score" in thought:
                                performance_data.append(action.thought)
                        
                        # Check for extracted data in observe action results
                        if hasattr(action, "result") and action.result:
                            if isinstance(action.result, str):
                                result = action.result.lower()
                                if "keyword" in result or "performance" in result:
                                    if action.result not in keyword_data and len(action.result.strip()) > 5:
                                        keyword_data.append(action.result)
                                if "ranking" in result or "rank" in result:
                                    if action.result not in ranking_data and len(action.result.strip()) > 5:
                                        ranking_data.append(action.result)
            except Exception as e:
                logger.error(f"Error processing history item: {e}")
                continue
    except Exception as e:
        logger.error(f"Error iterating through history: {e}")
    
    # Generate HTML for PDF-like report
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 90%; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
        <div style="text-align: center; border-bottom: 2px solid #2c3e50; padding-bottom: 10px; margin-bottom: 20px;">
            <h1 style="color: #2c3e50;">Vayner Client Research Report</h1>
            <h2 style="color: #3498db;">{business_name}</h2>
            <p style="color: #7f8c8d;">Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div style="margin-bottom: 30px;">
            <h3 style="color: #2c3e50; border-bottom: 1px solid #e0e0e0; padding-bottom: 5px;">Executive Summary</h3>
            <p>This report contains research data for {business_name} extracted from Vayner Commerce platform. 
            We analyzed keyword performance data and geographic rankings.</p>
        </div>
    """
    
    # If no specific data is found, try to extract from all output
    if not keyword_data and not ranking_data and not performance_data:
        try:
            all_text = []
            for item in history:
                if hasattr(item, "output") and item.output:
                    for action in item.output.action:
                        if hasattr(action, "thought") and action.thought:
                            all_text.append(action.thought)
                        if hasattr(action, "result") and action.result:
                            all_text.append(action.result)
            
            # Look for sections in the text
            for text in all_text:
                if "keyword" in text.lower() or "score" in text.lower() or "performance" in text.lower():
                    keyword_data.append(text)
                if "ranking" in text.lower() or "rank" in text.lower():
                    ranking_data.append(text)
        except Exception as e:
            logger.error(f"Error extracting all text: {e}")
    
    # Add performance data section
    if performance_data or keyword_data:
        html += """
        <div style="margin-bottom: 30px;">
            <h3 style="color: #2c3e50; border-bottom: 1px solid #e0e0e0; padding-bottom: 5px;">Keyword Performance Data</h3>
        """
        
        # Try to parse data into a table format
        table_data = []
        try:
            combined_data = performance_data + keyword_data
            for data in combined_data:
                lines = data.split("\n")
                for line in lines:
                    if ":" in line:
                        parts = line.split(":", 1)
                        if len(parts) == 2:
                            keyword, value = parts
                            table_data.append((keyword.strip(), value.strip()))
                    elif "-" in line and not line.strip().startswith("-"):
                        parts = line.split("-", 1)
                        if len(parts) == 2:
                            keyword, value = parts
                            table_data.append((keyword.strip(), value.strip()))
            
            if table_data:
                html += """
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background-color: #f2f2f2;">
                            <th style="padding: 10px; border: 1px solid #e0e0e0; text-align: left;">Keyword</th>
                            <th style="padding: 10px; border: 1px solid #e0e0e0; text-align: left;">Performance/Score</th>
                        </tr>
                    </thead>
                    <tbody>
                """
                
                for keyword, value in table_data:
                    html += f"""
                    <tr>
                        <td style="padding: 10px; border: 1px solid #e0e0e0;">{keyword}</td>
                        <td style="padding: 10px; border: 1px solid #e0e0e0;">{value}</td>
                    </tr>
                    """
                
                html += """
                    </tbody>
                </table>
                """
            else:
                # Display raw data if table parsing failed
                for data in combined_data:
                    html += f"""
                    <div style="margin-bottom: 15px; padding: 10px; background-color: #f9f9f9; border: 1px solid #e0e0e0;">
                        <pre style="margin: 0; white-space: pre-wrap;">{data}</pre>
                    </div>
                    """
        except Exception as e:
            logger.error(f"Error formatting table data: {e}")
            # Fallback to raw display
            for data in performance_data + keyword_data:
                html += f"""
                <div style="margin-bottom: 15px; padding: 10px; background-color: #f9f9f9; border: 1px solid #e0e0e0;">
                    <pre style="margin: 0; white-space: pre-wrap;">{data}</pre>
                </div>
                """
        
        html += """
        </div>
        """
    
    # Add rankings data section
    if ranking_data:
        html += """
        <div style="margin-bottom: 30px;">
            <h3 style="color: #2c3e50; border-bottom: 1px solid #e0e0e0; padding-bottom: 5px;">Geographic Rankings</h3>
        """
        
        for data in ranking_data:
            html += f"""
            <div style="margin-bottom: 15px; padding: 10px; background-color: #f9f9f9; border: 1px solid #e0e0e0;">
                <pre style="margin: 0; white-space: pre-wrap;">{data}</pre>
            </div>
            """
        
        html += """
        </div>
        """
    
    # Add screenshots section
    if screenshots:
        html += """
        <div style="margin-bottom: 30px;">
            <h3 style="color: #2c3e50; border-bottom: 1px solid #e0e0e0; padding-bottom: 5px;">Map Visualizations</h3>
            <div style="display: flex; flex-wrap: wrap; gap: 15px; justify-content: center;">
        """
        
        for idx, screenshot in enumerate(screenshots):
            if isinstance(screenshot, str) and len(screenshot) > 100:
                html += f"""
                <div style="margin-bottom: 15px; text-align: center;">
                    <img src="data:image/jpeg;base64,{screenshot}" alt="Map {idx+1}" style="max-width: 100%; border: 1px solid #e0e0e0; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                    <p style="margin-top: 5px; font-style: italic; color: #7f8c8d;">Map Visualization {idx+1}</p>
                </div>
                """
        
        html += """
            </div>
        </div>
        """
    
    # If no data was found, show a message
    if not keyword_data and not performance_data and not ranking_data and not screenshots:
        html += """
        <div style="margin-bottom: 30px; text-align: center; padding: 20px; background-color: #f8f9fa; border-radius: 5px;">
            <h3 style="color: #e74c3c;">No data extracted</h3>
            <p>The agent was unable to extract specific data for this report. Please check the chat logs for more details on what was found.</p>
        </div>
        """
    
    # Add footer
    html += """
        <div style="border-top: 1px solid #e0e0e0; padding-top: 15px; text-align: center; font-size: 12px; color: #7f8c8d;">
            <p>Generated by Vayner Client Research Agent | Browser-Use WebUI</p>
        </div>
    </div>
    """
    
    return html

# Function to generate live PDF-like report updated during the task
def generate_live_report(business_name, business_info, keyword_data, ranking_data, screenshots, keyword_table_rows=None, final_result=None):
    """
    Generate HTML for a live-updating PDF-like report based on data collected so far
    Only show the first three pages: cover, second page, and keyword table with final result.
    """
    if keyword_table_rows is None:
        keyword_table_rows = []
    # Cover page (black background, business name, VaynerCommerce logo)
    html = f'''
    <div style="width:100%; min-height:400px; background:#000; color:#fff; display:flex; flex-direction:column; align-items:center; justify-content:center; padding:60px 0 40px 0;">
        <div style="width:70%; max-width:500px; margin-bottom:30px;">
            <div style="text-align:center; margin-bottom:20px;">
                <svg width="120" height="80" viewBox="0 0 120 80" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M60 15C70 15 80 25 90 30C100 35 110 30 115 25C110 40 100 50 80 50C60 50 40 40 30 30C40 35 50 15 60 15Z" fill="white"/>
                    <path d="M70 15C65 20 60 18 55 15" stroke="white" stroke-width="2"/>
                    <path d="M75 12C70 17 65 15 60 12" stroke="white" stroke-width="2"/>
                </svg>
            </div>
            <div style="font-size:2.7rem; font-weight:600; letter-spacing:2px; text-align:center; line-height:1.1; text-transform:uppercase; font-family: 'Montserrat', Arial, sans-serif;">
                {business_name}
            </div>
            <div style="font-size:1.2rem; text-align:center; letter-spacing:1px; margin-top:5px; text-transform:uppercase; font-family: 'Montserrat', Arial, sans-serif;">
               
            </div>
        </div>
        
        <div style="font-size:2.5rem; font-weight:600; margin: 30px 0; text-align:center;">X</div>
        
        <div style="width:70%; max-width:500px;">
            <div style="font-size:2.1rem; font-weight:700; letter-spacing:2px; text-align:center; text-transform:uppercase; font-family: 'Montserrat', Arial, sans-serif;">
                <div style="display:inline-block; margin-right:10px; vertical-align:middle;">◆</div> VAYNERCOMMERCE
            </div>
        </div>
    </div>
    '''
    # Second page (logo, business name, service, date, image)
    html += f'''
    <div style="width:100%; min-height:400px; background:#fff; color:#222; display:flex; flex-direction:row; align-items:stretch; padding:0;">
        <div style="flex:1; display:flex; flex-direction:column; align-items:center; justify-content:center; padding:40px 20px; border-right:1px solid #eee;">
            <div style="width:240px; margin-bottom:20px;">
                <svg viewBox="0 0 240 140" width="240" height="140" xmlns="http://www.w3.org/2000/svg">
                    <path d="M120 30C140 30 160 50 180 60C200 70 220 60 230 50C220 80 200 100 160 100C120 100 80 80 60 60C80 70 100 30 120 30Z" fill="#4A8FBA"/>
                    <path d="M140 30C130 40 120 36 110 30" stroke="#4A8FBA" stroke-width="2"/>
                    <path d="M150 24C140 34 130 30 120 24" stroke="#4A8FBA" stroke-width="2"/>
                    <ellipse cx="140" cy="70" rx="100" ry="15" fill="#E3B151" opacity="0.3"/>
                </svg>
            </div>
            <div style="font-size:2.2rem; font-weight:600; color:#4A8FBA; margin-bottom:10px; font-family: 'Montserrat', Arial, sans-serif; text-transform:uppercase; letter-spacing:1px; text-align:center; line-height:1.1;">
                {business_name}<br>
                <span style="font-size:1.1rem; color:#666; text-transform:uppercase; letter-spacing:1px;">BEHAVIORAL HEALTH</span>
            </div>
            <div style="font-size:1.1rem; color:#666; margin:20px 0; text-align:center;">SEO Services</div>
            <div style="font-size:1rem; color:#444; text-align:center;">Weeks of <span style="font-weight:600;">04/07/25 - 04/21/25</span></div>
            <div style="margin-top:60px; font-size:0.9rem; color:#bbb; font-family: 'Montserrat', Arial, sans-serif;">
                <span style="display:inline-block; margin-right:5px; vertical-align:middle;">◆</span> VAYNERCOMMERCE
            </div>
        </div>
        <div style="flex:1; min-height:400px; background-image:url('https://images.unsplash.com/photo-1577563908411-5077b6dc7624?auto=format&fit=crop&w=700&q=80'); background-size:cover; background-position:center;">
        </div>
    </div>
    '''
    # Third page: Final Result and Keyword Table
    html += f'''
    <div style="width:100%; min-height:600px; background:#000; color:#fff; display:flex; flex-direction:column; align-items:center; justify-content:flex-start; padding:40px 0 40px 0; border-bottom:2px solid #222;">
        <div style="font-size:1.8rem; font-weight:600; color:#fff; margin-bottom:10px; font-family: 'Montserrat', Arial, sans-serif;">Final Research Results</div>
        <div style="width:90%; max-width:900px; margin-bottom:40px;">
    '''
    
    # Display Final Result if available
    if final_result:
        # Determine if final_result is likely a table
        is_table = False
        if isinstance(final_result, str):
            lines = final_result.strip().split('\n')
            if any('|' in line for line in lines) or any('keyword' in line.lower() and 'performance' in line.lower() for line in lines):
                is_table = True
        
        if is_table:
            # Format as a table
            try:
                html += '<div style="width:100%; overflow-x:auto; margin:20px 0; border-radius:4px; box-shadow:0 2px 10px rgba(0,0,0,0.1);">'
                
                # Split the table data
                lines = [line.strip() for line in final_result.split('\n') if line.strip()]
                
                # Find the header row
                header_row_index = -1
                for i, line in enumerate(lines):
                    if ('keyword' in line.lower() and 'performance' in line.lower()) or ('keyword' in line.lower() and 'sov' in line.lower()):
                        header_row_index = i
                        break
                
                if header_row_index != -1:
                    # Create an HTML table
                    html += '<table style="width:100%; border-collapse:collapse; font-family:Arial, sans-serif; background:#000; color:#fff;">'
                    
                    # Format the header row
                    header = lines[header_row_index]
                    header_cells = [cell.strip() for cell in header.strip('|').split('|')]
                    html += '<thead><tr style="background-color:#222; color:#fff;">'
                    for cell in header_cells:
                        html += f'<th style="padding:12px 15px; text-align:left; border-bottom:2px solid #444;">{cell}</th>'
                    html += '</tr></thead><tbody>'
                    
                    # Skip the separator row if it exists
                    data_start = header_row_index + 2 if header_row_index + 1 < len(lines) and '---' in lines[header_row_index + 1] else header_row_index + 1
                    
                    # Format the data rows
                    for i in range(data_start, len(lines)):
                        row = lines[i]
                        if '|' in row:
                            cells = [cell.strip() for cell in row.strip('|').split('|')]
                            bg_color = '#111' if i % 2 == 0 else '#181818'
                            html += f'<tr style="background-color:{bg_color}; color:#fff;">'
                            for cell in cells:
                                html += f'<td style="padding:10px 15px; border-bottom:1px solid #333;">{cell}</td>'
                            html += '</tr>'
                    
                    html += '</tbody></table>'
                else:
                    # If no proper header found, just display the text in a pre tag
                    html += f'<pre style="width:100%; background-color:#111; color:#fff; padding:15px; border-radius:4px; white-space:pre-wrap; overflow-x:auto;">{final_result}</pre>'
                
                html += '</div>'
            except Exception:
                # If parsing fails, just display the raw text
                html += f'<pre style="width:100%; background-color:#111; color:#fff; padding:15px; border-radius:4px; white-space:pre-wrap; overflow-x:auto;">{final_result}</pre>'
        else:
            # Format as regular text
            html += f'<div style="width:100%; background-color:#111; color:#fff; padding:20px; border-radius:4px; border-left:4px solid #4A8FBA; margin:20px 0;">'
            
            if isinstance(final_result, str):
                # Format the text with proper paragraphs
                paragraphs = final_result.split('\n\n')
                for paragraph in paragraphs:
                    if paragraph.strip():
                        paragraph_html = paragraph.replace("\n", "<br>")
                        html += f'<p style="margin-bottom:15px; line-height:1.5;">{paragraph_html}</p>'
            elif isinstance(final_result, list):
                # Handle list of items
                html += '<ul style="margin-left:20px; line-height:1.5;">'
                for item in final_result:
                    html += f'<li style="margin-bottom:8px;">{item}</li>'
                html += '</ul>'
            elif isinstance(final_result, dict):
                # Handle dictionary
                html += '<div style="line-height:1.5;">'
                for key, value in final_result.items():
                    html += f'<div style="margin-bottom:10px;"><strong>{key}:</strong> {value}</div>'
                html += '</div>'
            else:
                # Generic string representation
                html += f'<p style="line-height:1.5;">{str(final_result)}</p>'
            
            html += '</div>'
    else:
        html += '''
        <div style="width:90%; background-color:#111; color:#fff; padding:20px; border-radius:4px; text-align:center; margin:20px 0;">
            <p style="color:#bbb; font-style:italic;">Results will appear here when the task is completed.</p>
        </div>
        '''
    
    # Additional keyword table display
    if keyword_table_rows:
        html += '''
        <div style="width:90%; max-width:800px; margin-top:30px;">
            <div style="font-size:1.4rem; font-weight:600; color:#fff; margin-bottom:15px; font-family: 'Montserrat', Arial, sans-serif;">Keyword Performance Summary</div>
            <table style="width:100%; border-collapse:collapse; background:#000; color:#fff;">
                <thead>
                    <tr style="background-color:#222; color:#fff;">
                        <th style="padding:10px; border:1px solid #333; text-align:left;">Keyword</th>
                        <th style="padding:10px; border:1px solid #333; text-align:left;">Performance</th>
                        <th style="padding:10px; border:1px solid #333; text-align:left;">SOV</th>
                    </tr>
                </thead>
                <tbody>
        '''
        
        for row in keyword_table_rows:
            html += f'''<tr style="background-color:#111; color:#fff;">
                <td style="padding:10px; border:1px solid #333;">{row['keyword']}</td>
                <td style="padding:10px; border:1px solid #333;">{row['performance']}</td>
                <td style="padding:10px; border:1px solid #333;">{row['sov']}</td>
            </tr>'''
        
        html += '''
                </tbody>
            </table>
        </div>
        '''
    
    html += '</div></div>'
    return html

async def run_vayner_research(
    webui_manager: WebuiManager, 
    components: Dict[gr.components.Component, Any],
    business_name: str
) -> AsyncGenerator[Dict[gr.components.Component, Any], None]:
    """
    Runs a Vayner client research task and yields UI updates.
    """
    # Get all required UI components
    run_button_comp = webui_manager.get_component_by_id("vayner_client_research.run_button")
    stop_button_comp = webui_manager.get_component_by_id("vayner_client_research.stop_button")
    chatbot_comp = webui_manager.get_component_by_id("vayner_client_research.chatbot")
    browser_view_comp = webui_manager.get_component_by_id("vayner_client_research.browser_view")
    pdf_report_comp = webui_manager.get_component_by_id("vayner_client_research.pdf_report")
    
    # Create the task using the template with credentials
    task = VAYNER_CLIENT_TEMPLATE.format(
        business_name=business_name,
        vayner_username=VAYNER_USERNAME,
        vayner_password=VAYNER_PASSWORD
    )
    
    # Initialize chat history if needed
    if not hasattr(webui_manager, "vayner_chat_history"):
        webui_manager.vayner_chat_history = []
    
    # Show the business being researched
    webui_manager.vayner_chat_history.append(
        {"role": "user", "content": f"Research business: {business_name}"}
    )
    webui_manager.vayner_chat_history.append(
        {"role": "assistant", "content": f"Starting research for {business_name}..."}
    )
    
    yield {
        k: v for k, v in {
            chatbot_comp: gr.update(value=webui_manager.vayner_chat_history),
            run_button_comp: gr.update(value="⏳ Researching...", interactive=False),
            stop_button_comp: gr.update(interactive=True),
            pdf_report_comp: gr.update(visible=False)
        }.items() if k is not None
    }
    
    # Get settings from agent settings
    def get_setting(name, default=None):
        comp = webui_manager.get_component_by_id(f"agent_settings.{name}")
        return components.get(comp, default) if comp else default

    # LLM Settings
    llm_provider_name = get_setting("llm_provider", "openai")
    llm_model_name = get_setting("llm_model_name", "gpt-4o")
    llm_temperature = get_setting("llm_temperature", 0.6)
    use_vision = True  # Always need vision for this task
    llm_base_url = get_setting("llm_base_url", "")
    llm_api_key = get_setting("llm_api_key", "")
    if not llm_api_key:
        llm_api_key = os.getenv("OPENAI_API_KEY", "")
    
    # Browser Settings
    def get_browser_setting(key, default=None):
        comp = webui_manager.get_component_by_id(f"browser_settings.{key}")
        return components.get(comp, default) if comp else default

    headless = True  # Force headless mode for this agent
    disable_security = get_browser_setting("disable_security", False)
    window_w = int(get_browser_setting("window_w", 1920))
    window_h = int(get_browser_setting("window_h", 1080))
    save_recording_path = get_browser_setting("save_recording_path") or "./tmp/vayner_recordings"
    save_download_path = get_browser_setting("save_download_path", "./tmp/downloads")
    
    # Make sure paths exist
    os.makedirs(save_recording_path, exist_ok=True)
    if save_download_path:
        os.makedirs(save_download_path, exist_ok=True)
    
    # Stream settings for view
    stream_vw = 80
    stream_vh = int(80 * window_h // window_w)
    
    # Get LLM for agent
    main_llm = llm_provider.get_llm_model(
        provider="openai",  # Force OpenAI for vision capabilities
        model_name=str(llm_model_name) if llm_model_name else "gpt-4o",
        temperature=float(llm_temperature),
        base_url=str(llm_base_url) if llm_base_url else None,
        api_key=str(llm_api_key) if llm_api_key else None,
    )
    if main_llm is None:
        raise ValueError("Failed to initialize LLM. Please check your OpenAI API key and model settings in Agent Settings.")
    
    # Step and done callbacks
    async def step_callback(state, output, step_num):
        step_num -= 1
        logger.info(f"Step {step_num} completed.")
        
        # Process screenshot if available (for PDF only, not chat)
        screenshot_data = getattr(state, "screenshot", None)
        if screenshot_data:
            try:
                if isinstance(screenshot_data, str) and len(screenshot_data) > 100:
                    # Store screenshot for report
                    if not hasattr(webui_manager, "vayner_screenshots"):
                        webui_manager.vayner_screenshots = []
                    webui_manager.vayner_screenshots.append(screenshot_data)
            except Exception as e:
                logger.error(f"Error processing screenshot: {e}")
        
        # Extract information for real-time PDF report
        try:
            if not hasattr(webui_manager, "vayner_business_info"):
                webui_manager.vayner_business_info = []
            if not hasattr(webui_manager, "vayner_keyword_data"):
                webui_manager.vayner_keyword_data = []
            if not hasattr(webui_manager, "vayner_ranking_data"):
                webui_manager.vayner_ranking_data = []
            
            # Extract business info, keywords, and rankings from this step
            for action in output.action:
                if hasattr(action, "thought") and action.thought:
                    thought = action.thought.lower()
                    
                    # Extract business info
                    if "business" in thought and any(x in thought for x in ["name", "address", "info", "details", "about"]):
                        if action.thought not in webui_manager.vayner_business_info:
                            webui_manager.vayner_business_info.append(action.thought)
                    
                    # Extract keyword data
                    if "keyword" in thought and any(x in thought for x in ["performance", "score", "data"]):
                        if action.thought not in webui_manager.vayner_keyword_data:
                            webui_manager.vayner_keyword_data.append(action.thought)
                    
                    # Extract ranking data
                    if any(x in thought for x in ["ranking", "rank", "geography", "location"]):
                        if action.thought not in webui_manager.vayner_ranking_data:
                            webui_manager.vayner_ranking_data.append(action.thought)
                
                # Also check action results for structured data
                if hasattr(action, "result") and action.result and isinstance(action.result, str):
                    result = action.result.lower()
                    
                    # Extract structured data from results
                    if "business" in result and len(action.result) > 10:
                        if action.result not in webui_manager.vayner_business_info:
                            webui_manager.vayner_business_info.append(action.result)
                    
                    if "keyword" in result and len(action.result) > 10:
                        if action.result not in webui_manager.vayner_keyword_data:
                            webui_manager.vayner_keyword_data.append(action.result)
                            
                    if "rank" in result and len(action.result) > 10:
                        if action.result not in webui_manager.vayner_ranking_data:
                            webui_manager.vayner_ranking_data.append(action.result)
                            
            # Extract current URL for page context
            if hasattr(state, "url") and state.url:
                page_url = state.url
                if "business" in page_url.lower() and not any(page_url in info for info in webui_manager.vayner_business_info):
                    webui_manager.vayner_business_info.append(f"Page URL: {page_url}")
                    
            # Extract visible text from the page if available
            if hasattr(state, "text_content") and state.text_content:
                # Extract table-like data or lists that might contain keywords or rankings
                if "keyword" in state.text_content.lower() and len(state.text_content) > 20:
                    if state.text_content not in webui_manager.vayner_keyword_data:
                        webui_manager.vayner_keyword_data.append(state.text_content)
            
            # Extract keyword table data
            if not hasattr(webui_manager, "vayner_keyword_table_rows"):
                webui_manager.vayner_keyword_table_rows = []
            for action in output.action:
                # Try to extract keyword, performance, SOV from action.thought or action.result
                for field in [getattr(action, "thought", None), getattr(action, "result", None)]:
                    if field and isinstance(field, str):
                        # Simple regex/parse for lines like: "keyword: X, performance: Y, sov: Z"
                        import re
                        match = re.search(r"keyword[:\s]+([\w\- ]+)[,;\s]+performance[:\s]+([\w\-\.]+)[,;\s]+sov[:\s]+([\w\-\.]+)", field, re.IGNORECASE)
                        if match:
                            keyword = match.group(1).strip()
                            performance = match.group(2).strip()
                            sov = match.group(3).strip()
                            # Only add if not already present
                            if not any(row["keyword"].lower() == keyword.lower() for row in webui_manager.vayner_keyword_table_rows):
                                webui_manager.vayner_keyword_table_rows.append({
                                    "keyword": keyword,
                                    "performance": performance,
                                    "sov": sov
                                })
            
            # Update the PDF report with the latest data
            business_name = getattr(webui_manager, "vayner_current_business", "Unknown Business")
            webui_manager.vayner_pdf_report = generate_live_report(
                business_name,
                webui_manager.vayner_business_info,
                webui_manager.vayner_keyword_data,
                webui_manager.vayner_ranking_data,
                webui_manager.vayner_screenshots,
                webui_manager.vayner_keyword_table_rows,
                history.final_result()
            )
            
            # Get the PDF report component and update it in real-time
            pdf_report_comp = webui_manager.get_component_by_id("vayner_client_research.pdf_report")
            if pdf_report_comp and hasattr(webui_manager, "update_queue"):
                webui_manager.update_queue.append({
                    pdf_report_comp: gr.update(
                        value=webui_manager.vayner_pdf_report,
                        visible=True
                    )
                })
                
        except Exception as e:
            logger.error(f"Error updating PDF report: {e}")
        
        # Format logs similar to the screenshot (NO screenshots in chat)
        try:
            log_html = f'''
            <div style="margin: 5px 0; padding: 10px; background-color: #f8f9fa; border-radius: 4px; border-left: 4px solid #3498db; font-family: 'Courier New', monospace;">
                <div style="display: flex; align-items: center; margin-bottom: 5px;">
                    <span style="background-color: #e0f0ff; color: #3498db; font-weight: bold; padding: 2px 8px; border-radius: 12px; font-size: 12px; margin-right: 10px;">agent</span>
                    <span style="color: #555; font-size: 12px;">{datetime.now().strftime('%H:%M:%S')}</span>
                </div>
            '''
            
            # Extract actions
            actions_text = []
            has_content = False
            
            # Get full json output
            action_dump = [action.model_dump(exclude_none=True) for action in output.action]
            state_dump = output.current_state.model_dump(exclude_none=True)
            
            # Step info
            log_html += f'<div style="font-weight: bold; margin-bottom: 5px; color: #333;">🔶 Step {step_num}</div>'
            
            # Add current URL if available
            if hasattr(state, "url") and state.url:
                log_html += f'<div style="margin-bottom: 5px;"><span style="color: #888;">URL:</span> {state.url}</div>'
            
            # Add actions
            for action in action_dump:
                has_content = True
                
                if 'action_type' in action:
                    action_type = action['action_type'].upper()
                    
                    # Icon based on action type
                    if action_type == "CLICK":
                        icon = "🖱️"
                    elif action_type == "TYPE":
                        icon = "⌨️"
                    elif action_type == "NAVIGATE":
                        icon = "🔗"
                    elif action_type == "EXTRACT":
                        icon = "📋"
                    elif action_type == "WAIT_FOR_ELEMENT":
                        icon = "⏳"
                    else:
                        icon = "⚙️"
                    
                    # Format based on action type
                    if action_type == "CLICK" and 'selector' in action:
                        log_html += f'<div style="margin-bottom: 5px;"><span style="color: #e67e22;">{icon} CLICK:</span> <code>{action["selector"]}</code></div>'
                    elif action_type == "TYPE" and 'text' in action:
                        text = action['text']
                        if len(text) > 50:
                            text = text[:47] + "..."
                        log_html += f'<div style="margin-bottom: 5px;"><span style="color: #2ecc71;">{icon} TYPE:</span> <code>"{text}"</code></div>'
                    elif action_type == "NAVIGATE" and 'url' in action:
                        log_html += f'<div style="margin-bottom: 5px;"><span style="color: #3498db;">{icon} NAVIGATE:</span> <code>{action["url"]}</code></div>'
                    elif action_type == "EXTRACT":
                        log_html += f'<div style="margin-bottom: 5px;"><span style="color: #9b59b6;">{icon} EXTRACT DATA</span></div>'
                    elif action_type == "WAIT_FOR_ELEMENT" and 'selector' in action:
                        log_html += f'<div style="margin-bottom: 5px;"><span style="color: #f39c12;">{icon} WAIT FOR:</span> <code>{action["selector"]}</code></div>'
                    else:
                        details = ", ".join([f"{k}={v}" for k, v in action.items() if k != 'action_type' and k != 'thought'])
                        log_html += f'<div style="margin-bottom: 5px;"><span style="color: #34495e;">{icon} {action_type}:</span> <code>{details}</code></div>'
                
                # Include thoughts with thinking emoji
                if 'thought' in action and action['thought']:
                    thought = action['thought'].strip()
                    if len(thought) > 150:
                        thought = thought[:147] + "..."
                    log_html += f'<div style="margin: 5px 0 10px 15px; color: #7f8c8d; font-style: italic;">💭 {thought}</div>'

            # Close log div
            log_html += '</div>'
            
            # If no actions found
            if not has_content:
                log_html = f'''
                <div style="margin: 5px 0; padding: 10px; background-color: #f8f9fa; border-radius: 4px; border-left: 4px solid #e74c3c; font-family: 'Courier New', monospace;">
                    <div style="display: flex; align-items: center; margin-bottom: 5px;">
                        <span style="background-color: #ffe0e0; color: #e74c3c; font-weight: bold; padding: 2px 8px; border-radius: 12px; font-size: 12px; margin-right: 10px;">agent</span>
                        <span style="color: #555; font-size: 12px;">{datetime.now().strftime('%H:%M:%S')}</span>
                    </div>
                    <div style="font-weight: bold; margin-bottom: 5px; color: #333;">⚠️ Step {step_num} - No actions recorded</div>
                </div>
                '''
            
        except Exception as e:
            logger.error(f"Error formatting step output: {e}")
            log_html = f'''
            <div style="margin: 5px 0; padding: 10px; background-color: #f8f9fa; border-radius: 4px; border-left: 4px solid #e74c3c; font-family: 'Courier New', monospace;">
                <div style="display: flex; align-items: center; margin-bottom: 5px;">
                    <span style="background-color: #ffe0e0; color: #e74c3c; font-weight: bold; padding: 2px 8px; border-radius: 12px; font-size: 12px; margin-right: 10px;">error</span>
                </div>
                <div style="font-weight: bold; margin-bottom: 5px; color: #333;">⚠️ Error formatting Step {step_num}</div>
                <div style="color: #e74c3c;">{str(e)}</div>
            </div>
            '''
        
        # Add to chat history
        webui_manager.vayner_chat_history.append(
            {"role": "assistant", "content": log_html}
        )
    
    def done_callback(history):
        logger.info(f"Vayner research task finished. Duration: {history.total_duration_seconds():.2f}s")
        
        final_summary = "**Task Completed**\n"
        final_summary += f"- Duration: {history.total_duration_seconds():.2f} seconds\n"
        
        final_result = history.final_result()
        if final_result:
            final_summary += f"- Final Result: {final_result}\n"
            # --- FIX: Parse final_result for keywords and update table ---
            import re
            if not hasattr(webui_manager, "vayner_keyword_table_rows"):
                webui_manager.vayner_keyword_table_rows = []
            # Accept both string and dict/list results
            if isinstance(final_result, str):
                # 1. Parse markdown/pipe table
                lines = [line.strip() for line in final_result.splitlines() if line.strip()]
                table_start = -1
                for i, line in enumerate(lines):
                    if re.match(r"\|?\s*keyword\s*\|\s*performance\s*\|\s*sov\s*\|?", line, re.IGNORECASE):
                        table_start = i
                        break
                if table_start != -1 and table_start + 2 < len(lines):
                    # Table header, separator, then data rows
                    for row in lines[table_start+2:]:
                        if not row.startswith("|"):
                            continue
                        cells = [c.strip() for c in row.strip("|").split("|")]
                        if len(cells) >= 3:
                            keyword, performance, sov = cells[:3]
                            if keyword and performance and sov:
                                if not any(row_item["keyword"].lower() == keyword.lower() for row_item in webui_manager.vayner_keyword_table_rows):
                                    webui_manager.vayner_keyword_table_rows.append({
                                        "keyword": keyword,
                                        "performance": performance,
                                        "sov": sov
                                    })
                # 2. Also parse lines like: "keyword: X, performance: Y, sov: Z"
                for line in lines:
                    match = re.search(r"keyword[:\s]+([\w\- ]+)[,;\s]+performance[:\s]+([\w\-\.]+)[,;\s]+sov[:\s]+([\w\-\.]+)", line, re.IGNORECASE)
                    if match:
                        keyword = match.group(1).strip()
                        performance = match.group(2).strip()
                        sov = match.group(3).strip()
                        if not any(row_item["keyword"].lower() == keyword.lower() for row_item in webui_manager.vayner_keyword_table_rows):
                            webui_manager.vayner_keyword_table_rows.append({
                                "keyword": keyword,
                                "performance": performance,
                                "sov": sov
                            })
            elif isinstance(final_result, list):
                for item in final_result:
                    if isinstance(item, dict):
                        keyword = item.get("keyword")
                        performance = item.get("performance")
                        sov = item.get("sov")
                        if keyword and performance and sov:
                            if not any(row_item["keyword"].lower() == keyword.lower() for row_item in webui_manager.vayner_keyword_table_rows):
                                webui_manager.vayner_keyword_table_rows.append({
                                    "keyword": keyword,
                                    "performance": performance,
                                    "sov": sov
                                })
        
        errors = history.errors()
        if errors and any(errors):
            final_summary += f"- **Errors:**\n```\n{errors}\n```\n"
        else:
            final_summary += "- Status: Success\n"
        
        webui_manager.vayner_chat_history.append(
            {"role": "assistant", "content": final_summary}
        )
        
        # Generate PDF report using the current live data collections
        try:
            business_name = getattr(webui_manager, "vayner_current_business", "Unknown Business")
            webui_manager.vayner_pdf_report = generate_live_report(
                business_name,
                webui_manager.vayner_business_info,
                webui_manager.vayner_keyword_data,
                webui_manager.vayner_ranking_data,
                webui_manager.vayner_screenshots,
                webui_manager.vayner_keyword_table_rows,
                final_result
            )
        except Exception as e:
            logger.error(f"Error generating PDF report: {e}", exc_info=True)
            webui_manager.vayner_pdf_report = f"<div class='error'>Error generating report: {str(e)}</div>"
    
    # Initialize controller and browser
    try:
        if not webui_manager.vayner_controller:
            webui_manager.vayner_controller = CustomController()
            
        if not webui_manager.vayner_browser:
            webui_manager.vayner_browser = CustomBrowser(
                config=BrowserConfig(
                    headless=headless,
                    disable_security=disable_security,
                    browser_binary_path=None,
                    new_context_config=BrowserContextConfig(
                        window_width=window_w,
                        window_height=window_h,
                    )
                )
            )
            
        if not webui_manager.vayner_browser_context:
            context_config = BrowserContextConfig(
                save_recording_path=save_recording_path,
                save_downloads_path=save_download_path,
                window_height=window_h,
                window_width=window_w,
            )
            webui_manager.vayner_browser_context = (
                await webui_manager.vayner_browser.new_context(config=context_config)
            )
        
        # Initialize agent
        if not webui_manager.vayner_agent:
            webui_manager.vayner_agent = BrowserUseAgent(
                task=task,
                llm=main_llm,
                browser=webui_manager.vayner_browser,
                browser_context=webui_manager.vayner_browser_context,
                controller=webui_manager.vayner_controller,
                register_new_step_callback=step_callback,
                register_done_callback=done_callback,
                use_vision=use_vision,
                max_input_tokens=128000,
                max_actions_per_step=10,
                source="vayner_research",
            )
        else:
            webui_manager.vayner_agent.add_new_task(task)
        
        # Run the agent
        agent_run_coro = webui_manager.vayner_agent.run(max_steps=50)
        agent_task = asyncio.create_task(agent_run_coro)
        webui_manager.vayner_current_task = agent_task
        
        # Monitor the task and update UI
        last_chat_len = len(webui_manager.vayner_chat_history)
        while not agent_task.done():
            # Update Chatbot if new messages arrived
            if len(webui_manager.vayner_chat_history) > last_chat_len:
                yield {
                    chatbot_comp: gr.update(value=webui_manager.vayner_chat_history)
                }
                last_chat_len = len(webui_manager.vayner_chat_history)
            
            # Update Browser View
            if webui_manager.vayner_browser_context:
                try:
                    screenshot_b64 = await webui_manager.vayner_browser_context.take_screenshot()
                    if screenshot_b64:
                        html_content = f'<img src="data:image/jpeg;base64,{screenshot_b64}" style="width:{stream_vw}vw; height:{stream_vh}vh; border:1px solid #ccc;">'
                        yield {
                            browser_view_comp: gr.update(value=html_content, visible=True)
                        }
                except Exception as e:
                    logger.debug(f"Failed to capture screenshot: {e}")
            
            await asyncio.sleep(0.5)  # Polling interval
        
        # Wait for the task to complete
        await agent_task
        
        # Show PDF Report if generated
        if hasattr(webui_manager, "vayner_pdf_report") and webui_manager.vayner_pdf_report:
            yield {
                run_button_comp: gr.update(value="▶️ Research Client", interactive=True),
                stop_button_comp: gr.update(interactive=False),
                chatbot_comp: gr.update(value=webui_manager.vayner_chat_history),
                pdf_report_comp: gr.update(value=webui_manager.vayner_pdf_report, visible=True)
            }
        else:
            # Update UI when complete without PDF report
            yield {
                run_button_comp: gr.update(value="▶️ Research Client", interactive=True),
                stop_button_comp: gr.update(interactive=False),
                chatbot_comp: gr.update(value=webui_manager.vayner_chat_history)
            }
        
    except Exception as e:
        logger.error(f"Error during Vayner research: {e}", exc_info=True)
        error_message = f"**Error during research:**\n```\n{str(e)}\n```"
        webui_manager.vayner_chat_history.append(
            {"role": "assistant", "content": error_message}
        )
        
        yield {
            chatbot_comp: gr.update(value=webui_manager.vayner_chat_history),
            run_button_comp: gr.update(value="▶️ Research Client", interactive=True),
            stop_button_comp: gr.update(interactive=False),
            pdf_report_comp: gr.update(visible=False)
        }
        
        gr.Error(f"Research task failed: {e}")

async def handle_submit(webui_manager: WebuiManager, business_name: str):
    """Handles click on the Research Client button."""
    if not business_name.strip():
        gr.Warning("Please enter a business name")
        yield {}
    else:
        # Store the current business name
        webui_manager.vayner_current_business = business_name.strip()
        
        # Reset report data collections
        webui_manager.vayner_screenshots = []
        webui_manager.vayner_business_info = []
        webui_manager.vayner_keyword_data = []
        webui_manager.vayner_ranking_data = []
        webui_manager.vayner_keyword_table_rows = []  # Reset keyword table rows
        
        # Initialize empty report (cover and second page only)
        webui_manager.vayner_pdf_report = generate_live_report(
            business_name.strip(),
            [], [], [], [], []
        )
        
        # Get PDF report component
        pdf_report_comp = webui_manager.get_component_by_id("vayner_client_research.pdf_report")
        
        # Show the cover/second page immediately
        yield {
            pdf_report_comp: gr.update(
                value=webui_manager.vayner_pdf_report,
                visible=True
            )
        }
        
        # Initialize update queue
        webui_manager.update_queue = []
        
        # Use async generator to stream updates
        components = {}  # Will be populated by components in run_vayner_research
        async for update in run_vayner_research(webui_manager, components, business_name.strip()):
            # Include any queued PDF report updates
            while webui_manager.update_queue:
                pdf_updates = webui_manager.update_queue.pop(0)
                update.update(pdf_updates)
            
            yield update

async def handle_stop(webui_manager: WebuiManager):
    """Handles clicks on the 'Stop' button."""
    logger.info("Stop button clicked.")
    
    agent = webui_manager.vayner_agent
    task = webui_manager.vayner_current_task
    
    if agent and task and not task.done():
        # Safely try to stop the agent
        try:
            if hasattr(agent, 'stop'):
                agent.stop()
            else:
                # Alternative method
                agent.state.stopped = True
                agent.state.paused = False
        except Exception as e:
            logger.warning(f"Error stopping agent: {e}")
        
        task.cancel()
        try:
            await asyncio.wait_for(task, timeout=2.0)
        except (asyncio.CancelledError, asyncio.TimeoutError, Exception):
            pass
        
        run_button_comp = webui_manager.get_component_by_id("vayner_client_research.run_button")
        stop_button_comp = webui_manager.get_component_by_id("vayner_client_research.stop_button")
        
        yield {
            run_button_comp: gr.update(value="▶️ Research Client", interactive=True),
            stop_button_comp: gr.update(interactive=False)
        }
    else:
        yield {}

async def handle_clear(webui_manager: WebuiManager):
    """Handles clicks on the 'Clear' button."""
    logger.info("Clear button clicked.")
    
    # Stop any running task
    task = webui_manager.vayner_current_task
    if task and not task.done():
        # Stop the agent instead of using handle_stop
        try:
            agent = webui_manager.vayner_agent
            if agent and hasattr(agent, 'stop'):
                agent.stop()
            elif agent:
                agent.state.stopped = True
                agent.state.paused = False
            
            # Cancel the task
            task.cancel()
            try:
                await asyncio.wait_for(task, timeout=1.0)
            except (asyncio.CancelledError, asyncio.TimeoutError, Exception):
                pass
        except Exception as e:
            logger.warning(f"Error stopping agent: {e}")
    
    # Reset the chat history and PDF report
    webui_manager.vayner_chat_history = []
    webui_manager.vayner_pdf_report = generate_live_report(
        "Business Name",
        [], [], [], [], []
    )
    
    # Reset data collections for PDF report
    webui_manager.vayner_screenshots = []
    webui_manager.vayner_business_info = []
    webui_manager.vayner_keyword_data = []
    webui_manager.vayner_ranking_data = []
    webui_manager.vayner_keyword_table_rows = []
    webui_manager.vayner_current_business = "Business Name"
    webui_manager.update_queue = []
    
    # Get components
    chatbot_comp = webui_manager.get_component_by_id("vayner_client_research.chatbot")
    run_button_comp = webui_manager.get_component_by_id("vayner_client_research.run_button")
    stop_button_comp = webui_manager.get_component_by_id("vayner_client_research.stop_button")
    browser_view_comp = webui_manager.get_component_by_id("vayner_client_research.browser_view")
    business_name_comp = webui_manager.get_component_by_id("vayner_client_research.business_name")
    pdf_report_comp = webui_manager.get_component_by_id("vayner_client_research.pdf_report")
    
    yield {
        chatbot_comp: gr.update(value=[]),
        run_button_comp: gr.update(value="▶️ Research Client", interactive=True),
        stop_button_comp: gr.update(interactive=False),
        browser_view_comp: gr.update(value="<div style='text-align:center;'>Browser View</div>"),
        business_name_comp: gr.update(value=""),
        pdf_report_comp: gr.update(value=webui_manager.vayner_pdf_report, visible=True)
    }

def create_vayner_client_research_tab(webui_manager: WebuiManager):
    """
    Create the Vayner Client Research tab with specialized agent functionality.
    """
    # Initialize manager for Vayner client research
    webui_manager.init_vayner_client_research()

    # Create UI layout with left panel for agent interaction and right panel for browser view
    with gr.Row(elem_id="vayner_client_research_container"):
        # Left Panel - Agent Interaction (30% width)
        with gr.Column(scale=3):
            gr.Markdown("### Vayner Client Research Agent")
            
            chatbot = gr.Chatbot(
                value=webui_manager.vayner_chat_history,
                label="Agent Interaction",
                height=700,
                show_copy_button=True,
                type="messages"
            )
            
            with gr.Row():
                business_name = gr.Textbox(
                    label="Business Name",
                    placeholder="Enter the business name to research",
                    lines=1
                )
            
            with gr.Row():
                run_button = gr.Button("▶️ Research Client", variant="primary", scale=3)
                stop_button = gr.Button("⏹️ Stop", interactive=False, variant="stop", scale=2)
                clear_button = gr.Button("🗑️ Clear", variant="secondary", scale=2)
        
        # Right Panel - Browser View (70% width)
        with gr.Column(scale=7):
            with gr.Tabs():
                with gr.TabItem("Browser View"):
                    browser_view = gr.HTML(
                        value="<div style='width:100%; height:700px; display:flex; justify-content:center; align-items:center; border:1px solid #ccc; background-color:#f0f0f0;'><p>Browser view will appear here during research</p></div>",
                        label="Browser Live View",
                    )
                
                with gr.TabItem("PDF Report"):
                    pdf_report = gr.HTML(
                        value="<div style='width:100%; height:700px; display:flex; justify-content:center; align-items:center; border:1px solid #ccc; background-color:#f0f0f0;'><p>PDF Report will appear here after task completion</p></div>",
                        label="Research Report",
                        visible=False
                    )
    
    # Store components in manager
    tab_components = {
        "chatbot": chatbot,
        "business_name": business_name,
        "run_button": run_button,
        "stop_button": stop_button,
        "clear_button": clear_button,
        "browser_view": browser_view,
        "pdf_report": pdf_report
    }
    webui_manager.add_components("vayner_client_research", tab_components)
    
    # Wrapper functions for button handlers
    async def submit_wrapper(business_name_value):
        async for update in handle_submit(webui_manager, business_name_value):
            yield update
    
    async def stop_wrapper():
        async for update in handle_stop(webui_manager):
            yield update
    
    async def clear_wrapper():
        async for update in handle_clear(webui_manager):
            yield update
    
    # Connect event handlers
    run_button.click(
        fn=submit_wrapper,
        inputs=[business_name],
        outputs=list(tab_components.values())
    )
    
    business_name.submit(
        fn=submit_wrapper,
        inputs=[business_name],
        outputs=list(tab_components.values())
    )
    
    stop_button.click(
        fn=stop_wrapper,
        inputs=None,
        outputs=list(tab_components.values())
    )
    
    clear_button.click(
        fn=clear_wrapper,
        inputs=None,
        outputs=list(tab_components.values())
    )

