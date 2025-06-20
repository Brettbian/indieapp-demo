import streamlit as st
import os
from markitdown import MarkItDown
from openai import AzureOpenAI
import tempfile
import html

st.set_page_config(
    page_title="IndieApp Demo",
    page_icon="🚀",
    layout="wide"
)

def init_session_state():
    if 'uploaded_files_content' not in st.session_state:
        st.session_state.uploaded_files_content = {}
    if 'deleted_files' not in st.session_state:
        st.session_state.deleted_files = set()
    if 'azure_client' not in st.session_state:
        st.session_state.azure_client = None

def get_azure_client():
    if st.session_state.azure_client is None:
        endpoint = st.session_state.get('azure_endpoint', '')
        api_key = st.session_state.get('azure_api_key', '')
        api_version = st.session_state.get('azure_api_version', '2024-02-01')
        
        if endpoint and api_key:
            st.session_state.azure_client = AzureOpenAI(
                azure_endpoint=endpoint,
                api_key=api_key,
                api_version=api_version
            )
    return st.session_state.azure_client

def file_upload_page():
    st.title("📁 File Upload & Preview")
    
    # Hide the default file uploader file list
    st.markdown("""
    <style>
    .uploadedFile {
        display: none !important;
    }
    div[data-testid="stFileUploader"] > div > div > div > div > section > div {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Upload files (max 10MB each)",
        accept_multiple_files=True,
        type=['pdf', 'docx', 'txt', 'md', 'xlsx', 'pptx', 'html', 'csv'],
        key="file_uploader"
    )
    
    # Process new files
    if uploaded_files:
        md = MarkItDown()
        
        for uploaded_file in uploaded_files:
            if uploaded_file.size > 10 * 1024 * 1024:  # 10MB limit
                st.error(f"File {uploaded_file.name} exceeds 10MB limit")
                continue
            
            # Only process if not already processed AND not explicitly deleted
            if (uploaded_file.name not in st.session_state.uploaded_files_content and 
                uploaded_file.name not in st.session_state.deleted_files):
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_file_path = tmp_file.name
                    
                    result = md.convert(tmp_file_path)
                    markdown_content = result.text_content
                    
                    st.session_state.uploaded_files_content[uploaded_file.name] = markdown_content
                    
                    os.unlink(tmp_file_path)
                    
                except Exception as e:
                    st.error(f"Error processing {uploaded_file.name}: {str(e)}")
    
    # Display all processed files (persisted across page switches)
    if st.session_state.uploaded_files_content:
        st.success(f"📚 {len(st.session_state.uploaded_files_content)} files processed and ready for AI chat")
        
        # Add option to clear all files
        if st.button("🗑️ Clear All Files", type="secondary"):
            st.session_state.deleted_files.update(st.session_state.uploaded_files_content.keys())
            st.session_state.uploaded_files_content = {}
            st.rerun()
        
        st.subheader("📄 Processed Files Preview:")
        
        # Create a list of filenames to iterate over (to avoid dictionary changing during iteration)
        filenames = list(st.session_state.uploaded_files_content.keys())
        
        for filename in filenames:
            if filename not in st.session_state.uploaded_files_content:
                continue  # Skip if file was deleted
                
            content = st.session_state.uploaded_files_content[filename]
            
            # Create row with filename and delete button
            col1, col2 = st.columns([5, 1])
            
            with col1:
                # Use expander with filename
                with st.expander(f"📄 {filename}"):
                    st.markdown("**Markdown Preview:**")
                    
                    # Create scrollable container for markdown content
                    st.markdown(
                        f"""
                        <div style="
                            max-height: 400px; 
                            overflow-y: auto; 
                            padding: 10px; 
                            border: 1px solid #e0e0e0; 
                            border-radius: 5px; 
                            background-color: #f9f9f9;
                            font-family: monospace;
                            white-space: pre-wrap;
                        ">
                        {html.escape(content)}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    # Show file stats
                    st.caption(f"File size: {len(content):,} characters")
            
            with col2:
                # Delete button aligned with expander header
                st.write("")  # Add some spacing to align with expander
                if st.button("🗑️", key=f"delete_preview_{filename}", help=f"Delete {filename}"):
                    st.session_state.deleted_files.add(filename)
                    del st.session_state.uploaded_files_content[filename]
                    st.rerun()
    else:
        st.info("👆 Upload files above to get started")

def ai_chat_page():
    st.title("💬 AI Chat")
    
    if not st.session_state.uploaded_files_content:
        st.warning("Please upload some files first in the File Upload page.")
        return
    
    client = get_azure_client()
    if not client:
        st.warning("Please configure Azure OpenAI settings in the Settings page.")
        return
    
    deployment_name = st.session_state.get('deployment_name', '')
    if not deployment_name:
        st.warning("Please set deployment name in Settings page.")
        return
    
    context = "\n\n".join([f"File: {filename}\n{content}" for filename, content in st.session_state.uploaded_files_content.items()])
    
    # Show compact context files summary
    with st.expander(f"📚 Context Files ({len(st.session_state.uploaded_files_content)} files) - Click to manage"):
        filenames = list(st.session_state.uploaded_files_content.keys())
        for filename in filenames:
            if filename not in st.session_state.uploaded_files_content:
                continue
                
            col1, col2 = st.columns([5, 1])
            with col1:
                st.write(f"📄 {filename}")
            with col2:
                if st.button("🗑️", key=f"delete_chat_{filename}", help=f"Remove {filename} from context"):
                    st.session_state.deleted_files.add(filename)
                    del st.session_state.uploaded_files_content[filename]
                    st.rerun()
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Ask about your uploaded files..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            try:
                response = client.chat.completions.create(
                    model=deployment_name,
                    messages=[
                        {"role": "system", "content": f"You are a helpful assistant. Use the following context from uploaded files to answer questions. Format your responses using markdown for better readability (use headers, bullet points, code blocks, etc. when appropriate):\n\n{context}"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )
                
                assistant_response = response.choices[0].message.content
                # Render markdown with better formatting
                st.markdown(assistant_response, unsafe_allow_html=False)
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                
            except Exception as e:
                st.error(f"Error calling Azure OpenAI: {str(e)}")

def ai_generation_page():
    st.title("🎯 AI Business Plan Generator")
    
    client = get_azure_client()
    if not client:
        st.warning("Please configure Azure OpenAI settings in the Settings page.")
        return
    
    deployment_name = st.session_state.get('deployment_name', '')
    if not deployment_name:
        st.warning("Please set deployment name in Settings page.")
        return
    
    # Show compact context files summary if any
    if st.session_state.uploaded_files_content:
        with st.expander(f"📚 Available Context Files ({len(st.session_state.uploaded_files_content)} files) - Click to manage"):
            filenames = list(st.session_state.uploaded_files_content.keys())
            for filename in filenames:
                if filename not in st.session_state.uploaded_files_content:
                    continue
                    
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.write(f"📄 {filename}")
                with col2:
                    if st.button("🗑️", key=f"delete_gen_{filename}", help=f"Remove {filename}"):
                        st.session_state.deleted_files.add(filename)
                        del st.session_state.uploaded_files_content[filename]
                        st.rerun()
    
    if st.button("🚀 Generate Business Plan", type="primary"):
        with st.spinner("Generating your stunning business plan... DO NOT GO AWAY!"):
            try:
                # Build context from uploaded files
                context = ""
                if st.session_state.uploaded_files_content:
                    context = "\n\nCONTEXT FROM UPLOADED FILES:\n" + "\n\n".join([f"File: {filename}\n{content}" for filename, content in st.session_state.uploaded_files_content.items()])
                
                business_plan_prompt = f"""
                Create a comprehensive, visually appealing HTML business plan that will dazzle investors. 
                
                {context}
                
                Use the uploaded files as context to inform the business plan. If no files are uploaded, create a fictional innovative tech startup.
                
                The HTML should include:
                
                1. Modern CSS styling with gradients, shadows, and professional typography
                2. Executive Summary with compelling value proposition
                3. Market Analysis with growth projections
                4. Business Model and Revenue Streams  
                5. Marketing Strategy
                6. Financial Projections (3-year outlook)
                7. Team section
                8. Investment Requirements and Use of Funds
                
                Make it visually stunning with:
                - Modern color scheme (blues, greens, professional colors)
                - Clean layout with proper spacing
                - Icons and visual elements using Unicode symbols
                - Responsive design
                - Charts represented as styled progress bars or visual elements
                - Professional fonts and typography
                
                Make the numbers realistic but impressive. Base the business plan on the uploaded documents if available.
                Return ONLY the complete HTML code, no markdown formatting.
                """
                # Assuming 'context' is already defined as in your original code

                slide_prompt = f"""
                Act as an expert full-stack developer and UI/UX designer. Your specialty is creating stunning, data-driven web presentations that captivate audiences. Your task is to build a single, self-contained, and visually spectacular HTML presentation slide for a high-stakes investor pitch.

                **CONTEXT FROM UPLOADED FILES:**
                {context if context else "No context files were provided."}

                **INSTRUCTIONS:**

                **1. Core Content Strategy (for a SINGLE SLIDE):**
                - **Headline:** A powerful, concise headline that grabs attention.
                - **The Hook:** A 1-2 sentence summary of the core value proposition.
                - **Key Metrics (3-4 max):** Showcase the most impressive data points using dynamic charts.
                - **The Ask:** Clearly state the investment amount being sought and its primary purpose.

                **2. Design & Technical Specifications:**

                **A. Frameworks & Libraries (MUST USE):**
                You must include the following via their CDNs within the HTML `<head>` or before `</body>` as appropriate:
                - **Tailwind CSS:** For all styling.
                - **Google Fonts:** For the 'Inter' font family.
                - **Google Material Symbols:** For all iconography.
                - **AOS (Animate On Scroll):** For subtle on-load animations.
                - **Chart.js:** For creating beautiful, animated data visualizations.

                **B. Layout & Styling:**
                - **Layout:** Use a sophisticated, asymmetrical grid layout. Ensure a strong visual hierarchy that guides the viewer's eye.
                - **Color Palette:** Implement a professional dark theme. Use a subtle, dark gradient background (e.g., `bg-gradient-to-br from-gray-900 via-black to-blue-900`). Use a single, vibrant accent color (e.g., `#00FFA3` for a neon mint) for CTAs, highlights, and chart elements.
                - **Animation:** Use the **AOS library** to add elegant fade-in or slide-in animations to elements as they load. For example: `data-aos="fade-up"` and `data-aos-delay="200"`. Initialize AOS in the script tag.

                **C. Typography:**
                - Use the 'Inter' font from Google Fonts.
                - Use a range of font weights (e.g., 300 for paragraphs, 700 for headlines) to create clear contrast and hierarchy.

                **D. Iconography:**
                - **Primary Method:** Use **Google Material Symbols**. Link the stylesheet in the `<head>`. Implement icons using `<span class="material-symbols-outlined">rocket_launch</span>`. The icons should be sharp, clear, and complement the content.
                - **Fallback Method:** Only use inline SVGs if a highly custom visual (like a unique logo) is absolutely necessary.

                **E. Data Visualization:**
                - **DO NOT use static text or tables for key metrics.**
                - Use **Chart.js** to create 3-4 small, clean, and animated charts (e.g., doughnut or pie charts for percentages, small bar charts for growth).
                - Each chart should be placed within its own "card" element with a title.
                - The charts must be animated on load (default for Chart.js) and use the chosen accent color.

                **3. Fallback Scenario:**
                - If no context is provided, invent a compelling fictional tech startup. Be specific and modern. Examples: "Aether," a decentralized cloud storage solution, or "Oasis," an AI-powered platform for urban vertical farming.

                **4. Final Output:**
                - Return ONLY the complete, self-contained HTML file.
                - The response must start with `<!DOCTYPE html>` and end with `</html>`.
                - All CSS (via Tailwind) and JavaScript (for AOS and Chart.js initialization) must be correctly included to make the file work perfectly when opened in a browser.
                - The JavaScript for initializing the libraries and charts should be in a single `<script>` tag before the closing `</body>` tag.
                """
                
                response = client.chat.completions.create(
                    model=deployment_name,
                    messages=[{"role": "user", "content": slide_prompt}],
                    temperature=0.8,
                    max_tokens=3000
                )
                
                html_content = response.choices[0].message.content
                
                # Clean up any markdown formatting
                if html_content.startswith('```html'):
                    html_content = html_content.replace('```html', '').replace('```', '')
                
                st.subheader("📊 Your Generated Business Plan")
                
                # Display the HTML
                st.components.v1.html(html_content, height=800, scrolling=True)
                
                # Also provide download option
                st.download_button(
                    label="💾 Download Business Plan HTML",
                    data=html_content,
                    file_name="business_plan.html",
                    mime="text/html"
                )
                
            except Exception as e:
                st.error(f"Error generating business plan: {str(e)}")

def settings_page():
    st.title("⚙️ Settings")
    
    st.subheader("Azure OpenAI Configuration")
    
    azure_endpoint = st.text_input(
        "Azure OpenAI Endpoint",
        value=st.session_state.get('azure_endpoint', ''),
        placeholder="https://your-resource-name.openai.azure.com/",
        help="Your Azure OpenAI resource endpoint"
    )
    
    azure_api_key = st.text_input(
        "Azure OpenAI API Key",
        value=st.session_state.get('azure_api_key', ''),
        type="password",
        help="Your Azure OpenAI API key"
    )
    
    deployment_name = st.text_input(
        "Deployment Name",
        value=st.session_state.get('deployment_name', ''),
        placeholder="gpt-4",
        help="Name of your deployed model"
    )
    
    azure_api_version = st.text_input(
        "API Version",
        value=st.session_state.get('azure_api_version', '2024-02-01'),
        help="Azure OpenAI API version"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Save Settings"):
            st.session_state.azure_endpoint = azure_endpoint
            st.session_state.azure_api_key = azure_api_key
            st.session_state.deployment_name = deployment_name
            st.session_state.azure_api_version = azure_api_version
            st.session_state.azure_client = None  # Reset client to use new settings
            st.success("Settings saved successfully!")
    
    with col2:
        if st.button("🔍 Test Connection"):
            if not all([azure_endpoint, azure_api_key, deployment_name]):
                st.error("Please fill in all settings before testing connection")
            else:
                with st.spinner("Testing connection..."):
                    try:
                        test_client = AzureOpenAI(
                            azure_endpoint=azure_endpoint,
                            api_key=azure_api_key,
                            api_version=azure_api_version
                        )
                        
                        # Test with a simple completion
                        response = test_client.chat.completions.create(
                            model=deployment_name,
                            messages=[{"role": "user", "content": "Hello, this is a connection test."}],
                            max_tokens=10,
                            temperature=0.1
                        )
                        
                        if response.choices[0].message.content:
                            st.success("✅ Connection successful! Azure OpenAI is working correctly.")
                        else:
                            st.error("❌ Connection failed: No response received")
                            
                    except Exception as e:
                        st.error(f"❌ Connection failed: {str(e)}")
    
    st.subheader("Current Settings Status")
    if azure_endpoint and azure_api_key and deployment_name:
        st.success("✅ Azure OpenAI configured")
    else:
        st.warning("⚠️ Please configure all Azure OpenAI settings")

def main():
    init_session_state()
    
    st.sidebar.title("🚀 IndieApp Demo")
    
    # Create tabs in sidebar
    if st.sidebar.button("📁 File Upload", use_container_width=True):
        st.session_state.current_page = "file_upload"
    if st.sidebar.button("💬 AI Chat", use_container_width=True):
        st.session_state.current_page = "ai_chat"
    if st.sidebar.button("🎯 AI Generation", use_container_width=True):
        st.session_state.current_page = "ai_generation"
    if st.sidebar.button("⚙️ Settings", use_container_width=True):
        st.session_state.current_page = "settings"
    
    # Initialize current page if not set
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "file_upload"
    
    # Display the selected page
    if st.session_state.current_page == "file_upload":
        file_upload_page()
    elif st.session_state.current_page == "ai_chat":
        ai_chat_page()
    elif st.session_state.current_page == "ai_generation":
        ai_generation_page()
    elif st.session_state.current_page == "settings":
        settings_page()

if __name__ == "__main__":
    main()