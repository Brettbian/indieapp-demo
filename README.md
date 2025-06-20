# IndieApp Demo

A Streamlit web application for file processing, AI chat, and business plan generation using Azure OpenAI.

## Features

- **📁 File Upload & Preview**: Upload files and convert them to markdown using markitdown
- **💬 AI Chat**: Chat with AI using uploaded files as context
- **🎯 AI Generation**: Generate beautiful HTML business plans
- **⚙️ Settings**: Configure Azure OpenAI API settings

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
streamlit run app.py
```

## Configuration

1. Go to the Settings page
2. Configure your Azure OpenAI settings:
   - Azure OpenAI Endpoint
   - API Key
   - Deployment Name
   - API Version

## Supported File Types

The application supports file types compatible with markitdown:
- PDF
- DOCX
- TXT
- MD
- XLSX
- PPTX
- HTML
- CSV

## File Size Limit

Maximum file size: 10MB per file

## Usage

1. **Upload Files**: Go to File Upload page and upload your documents
2. **Chat**: Use the AI Chat page to ask questions about your uploaded files
3. **Generate**: Create stunning business plans on the AI Generation page
4. **Configure**: Set up your Azure OpenAI credentials in Settings