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
    st.title("🎯 AI Business Canvas Generator")
    
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
                
            
                # Assuming 'context' is already defined as in your original code

                canvas_prompt = f"""
                Act as an expert business strategist and senior frontend developer. Your task is to create a complete, visually clean, and well-structured HTML Business Model Canvas based on the provided context. The final output must be a single, self-contained HTML file.

                **CONTEXT FROM UPLOADED FILES:**
                {context if context else "No context files were provided."}

                **--- CORE TASK & INSTRUCTIONS ---**

                **1. Analyze and Populate:**
                - Carefully analyze the business information provided in the "CONTEXT" section.
                - Populate all nine sections of the Business Model Canvas with relevant, concise bullet points derived from the context. The content should be strategic and to the point.

                **2. Fallback Scenario:**
                - If no context is provided, invent a compelling and detailed fictional tech startup. Do not use a generic example. Be specific, e.g., "AstraFlow," a platform that uses AI to automate and optimize supply chain logistics for e-commerce businesses. Then, fill out the canvas for this fictional company.

                **--- DESIGN & TECHNICAL REQUIREMENTS ---**

                **1. Frameworks and Libraries (MUST USE):**
                - **Tailwind CSS:** For all styling, loaded from the CDN.
                - **Google Fonts:** For the 'Inter' font family.
                - **Google Material Symbols (Outlined):** For all icons, loaded from the Google Fonts CDN.

                **2. Layout (CRITICAL):**
                - You MUST use the exact HTML structure and CSS Grid layout provided in the template below.
                - The canvas must be responsive, collapsing gracefully into a single column on smaller screens (e.g., mobile). Use Tailwind's responsive prefixes (`sm:`, `md:`, `lg:`).

                **3. Styling:**
                - Adhere to a clean, professional, and minimalist design inspired by the Strategyzer canvas.
                - Each canvas section (grid-item) should be a card with a light background (`bg-gray-50` or `bg-white`), rounded corners (`rounded-lg`), and a subtle box shadow (`shadow-md`).
                - Use a professional color for the icon and title in each section (e.g., `text-gray-700`).
                - Ensure excellent padding and spacing throughout for readability.

                **4. Iconography:**
                - You MUST use the specific Google Material Symbols defined within the HTML template. Implement them using `<span class="material-symbols-outlined">icon_name</span>`.

                **5. Warning:**
                - ONLY OUTPUT THE HTML CODE, NO OTHER TEXT OR MARKDOWN.

                **--- HTML TEMPLATE (USE THIS EXACT STRUCTURE) ---**

                You must use this template as the foundation for your response. Populate the `<ul>` elements with the business content.

                ```html
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Business Model Canvas</title>
                    <script src="[https://cdn.tailwindcss.com](https://cdn.tailwindcss.com)"></script>
                    <link rel="preconnect" href="[https://fonts.googleapis.com](https://fonts.googleapis.com)">
                    <link rel="preconnect" href="[https://fonts.gstatic.com](https://fonts.gstatic.com)" crossorigin>
                    <link href="[https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap](https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap)" rel="stylesheet">
                    <link rel="stylesheet" href="[https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200](https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200)" />
                    <style>
                        body {{ font-family: 'Inter', sans-serif; }}
                        .material-symbols-outlined {{ font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24; font-size: 28px; }}
                        /* Responsive grid layout */
                        .canvas-grid {{
                            display: grid;
                            grid-template-columns: repeat(1, 1fr);
                            gap: 1rem;
                        }}
                        @media (min-width: 1024px) {{
                            .canvas-grid {{
                                grid-template-columns: repeat(5, 1fr);
                                grid-template-rows: auto auto auto;
                            }}
                            .grid-item-kp {{ grid-column: 1 / 2; grid-row: 1 / 3; }}
                            .grid-item-ka {{ grid-column: 2 / 3; grid-row: 1 / 2; }}
                            .grid-item-vp {{ grid-column: 3 / 4; grid-row: 1 / 3; }}
                            .grid-item-cr {{ grid-column: 4 / 5; grid-row: 1 / 2; }}
                            .grid-item-cs {{ grid-column: 5 / 6; grid-row: 1 / 3; }}
                            .grid-item-kr {{ grid-column: 2 / 3; grid-row: 2 / 3; }}
                            .grid-item-ch {{ grid-column: 4 / 5; grid-row: 2 / 3; }}
                            .grid-item-cst {{ grid-column: 1 / 4; grid-row: 3 / 4; }}
                            .grid-item-rs {{ grid-column: 4 / 6; grid-row: 3 / 4; }}
                        }}
                    </style>
                </head>
                <body class="bg-gray-100 p-4 sm:p-6 lg:p-8">

                    <div class="max-w-7xl mx-auto">
                        <header class="mb-8">
                            <h1 class="text-3xl font-bold text-gray-800">Business Model Canvas</h1>
                            <div class="flex flex-wrap gap-x-6 gap-y-2 text-sm text-gray-600 mt-2">
                                <p><span class="font-semibold">Designed for:</span> [Company Name]</p>
                                <p><span class="font-semibold">Date:</span> [Current Date]</p>
                                <p><span class="font-semibold">Version:</span> 1.0</p>
                            </div>
                        </header>

                        <main class="canvas-grid">
                            <section class="grid-item-kp bg-white p-4 rounded-lg shadow-md flex flex-col">
                                <div class="flex items-center gap-3 mb-3">
                                    <span class="material-symbols-outlined text-blue-600">handshake</span>
                                    <h2 class="text-lg font-semibold text-gray-800">Key Partners</h2>
                                </div>
                                <ul class="list-disc list-inside text-gray-700 text-sm space-y-1 flex-grow">
                                    </ul>
                            </section>

                            <section class="grid-item-ka bg-white p-4 rounded-lg shadow-md flex flex-col">
                                <div class="flex items-center gap-3 mb-3">
                                    <span class="material-symbols-outlined text-green-600">checklist</span>
                                    <h2 class="text-lg font-semibold text-gray-800">Key Activities</h2>
                                </div>
                                <ul class="list-disc list-inside text-gray-700 text-sm space-y-1 flex-grow">
                                    </ul>
                            </section>

                            <section class="grid-item-vp bg-white p-4 rounded-lg shadow-md flex flex-col">
                                <div class="flex items-center gap-3 mb-3">
                                    <span class="material-symbols-outlined text-purple-600">redeem</span>
                                    <h2 class="text-lg font-semibold text-gray-800">Value Propositions</h2>
                                </div>
                                <ul class="list-disc list-inside text-gray-700 text-sm space-y-1 flex-grow">
                                    </ul>
                            </section>

                            <section class="grid-item-cr bg-white p-4 rounded-lg shadow-md flex flex-col">
                                <div class="flex items-center gap-3 mb-3">
                                    <span class="material-symbols-outlined text-red-600">favorite</span>
                                    <h2 class="text-lg font-semibold text-gray-800">Customer Relationships</h2>
                                </div>
                                <ul class="list-disc list-inside text-gray-700 text-sm space-y-1 flex-grow">
                                    </ul>
                            </section>
                            
                            <section class="grid-item-cs bg-white p-4 rounded-lg shadow-md flex flex-col">
                                <div class="flex items-center gap-3 mb-3">
                                    <span class="material-symbols-outlined text-orange-600">groups</span>
                                    <h2 class="text-lg font-semibold text-gray-800">Customer Segments</h2>
                                </div>
                                <ul class="list-disc list-inside text-gray-700 text-sm space-y-1 flex-grow">
                                    </ul>
                            </section>

                            <section class="grid-item-kr bg-white p-4 rounded-lg shadow-md flex flex-col">
                                <div class="flex items-center gap-3 mb-3">
                                    <span class="material-symbols-outlined text-green-600">build_circle</span>
                                    <h2 class="text-lg font-semibold text-gray-800">Key Resources</h2>
                                </div>
                                <ul class="list-disc list-inside text-gray-700 text-sm space-y-1 flex-grow">
                                    </ul>
                            </section>

                            <section class="grid-item-ch bg-white p-4 rounded-lg shadow-md flex flex-col">
                                <div class="flex items-center gap-3 mb-3">
                                    <span class="material-symbols-outlined text-red-600">local_shipping</span>
                                    <h2 class="text-lg font-semibold text-gray-800">Channels</h2>
                                </div>
                                <ul class="list-disc list-inside text-gray-700 text-sm space-y-1 flex-grow">
                                    </ul>
                            </section>

                            <section class="grid-item-cst bg-white p-4 rounded-lg shadow-md flex flex-col">
                                <div class="flex items-center gap-3 mb-3">
                                    <span class="material-symbols-outlined text-cyan-600">payments</span>
                                    <h2 class="text-lg font-semibold text-gray-800">Cost Structure</h2>
                                </div>
                                <ul class="list-disc list-inside text-gray-700 text-sm space-y-1 flex-grow">
                                    </ul>
                            </section>
                            
                            <section class="grid-item-rs bg-white p-4 rounded-lg shadow-md flex flex-col">
                                <div class="flex items-center gap-3 mb-3">
                                    <span class="material-symbols-outlined text-teal-600">attach_money</span>
                                    <h2 class="text-lg font-semibold text-gray-800">Revenue Streams</h2>
                                </div>
                                <ul class="list-disc list-inside text-gray-700 text-sm space-y-1 flex-grow">
                                    </ul>
                            </section>
                        </main>
                    </div>
                </body>
                </html>
                """

    
                
                response = client.chat.completions.create(
                    model=deployment_name,
                    messages=[{"role": "user", "content": canvas_prompt}],
                    temperature=0.8,
                    max_tokens=6000
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
        placeholder="gpt-4o",
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