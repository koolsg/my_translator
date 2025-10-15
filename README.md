# My Local AI Translator

A simple, locally-hosted web application that allows you to translate text using different Large Language Models (LLMs) like Google's Gemini and OpenAI's ChatGPT.

## ✨ Features

- **Runs Locally**: No need to deploy to a cloud server. Everything runs on your local machine.
- **Web Interface**: A clean and simple user interface that runs in any modern web browser.
- **Side-by-Side View**: Displays the original text and the translated text in a convenient two-column layout (perfectly balanced 50/50 split).
- **Multi-Provider Support**: Choose between different AI providers and their models.
  - **Google Gemini**: Multiple models available based on your API key permissions
  - **OpenAI**: Dynamic model list based on your API key permissions
- **API Provider Selection**: Dedicated dropdown to select between Gemini and OpenAI
- **Dynamic Model Loading**: Model list updates automatically based on selected provider
- **Model Presets**: Successfully used models are saved as presets and appear first in the list
- **Real-time Character Count**: Shows character count of input text in the top-right corner
- **Multiple Languages**: Support for Korean, English, Japanese, and Chinese translations
- **External API Key Management**: Securely manage your API keys in an external `config.json` file, separated from the source code.

## 📂 Project Structure

```
my_translator/
├── app.py              # The Python Flask backend server
├── config.json         # Configuration file for API keys
├── index.html          # The HTML/CSS/JS frontend
└── requirements.txt    # Python dependencies
```

## 🚀 Setup and Installation

Follow these steps to get the translator running on your local machine.

### Option A: Manual Setup

#### 1. Configure API Keys

First, you need to provide your API keys.

1. **Copy the example configuration**:
   ```bash
   cp config.json.example config.json
   ```

2. **Edit `config.json`** with your actual API keys:
   ```json
   {
     "gemini": {
       "api_keys": [
         "YOUR_ACTUAL_GEMINI_API_KEY"
       ]
     },
     "openai": {
       "api_key": "YOUR_ACTUAL_OPENAI_API_KEY"
     }
   }
   ```

   > **Note**: You only need to provide the key for the model(s) you intend to use.
   > **Security**: Never commit `config.json` to Git - it's in `.gitignore` for security.

#### 2. Install Dependencies

You need Python 3 installed. Open your terminal and navigate to the project directory, then install the required Python libraries.

```bash
# Navigate to the project folder
cd path/to/my_translator

# Create virtual environment (recommended)
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 3. Run the Backend Server

Once the dependencies are installed, start the Flask backend server.

```bash
python app.py
```

You should see a message indicating that the server is running on `http://127.0.0.1:5000`. Keep this terminal window open.

#### 4. Open the Translator

Open the `index.html` file in your favorite web browser (e.g., by double-clicking the file).

### Option B: Automated Setup with PowerShell Scripts

For a more convenient setup and management, use the provided PowerShell scripts. These scripts handle virtual environment setup, process management, and background execution automatically.

#### 📊 Scripts Overview

| Script | Purpose | Usage |
|--------|---------|-------|
| `start_server.ps1` | Starts the Flask server in background mode | `./start_server.ps1` |
| `stop_server.ps1` | Stops the background server and cleans up processes | `./stop_server.ps1` |

#### ⚙️ Prerequisites for PowerShell Scripts

- **PowerShell Version**: Compatible with PowerShell 5.1+ (included in Windows 7 and newer)
- **Windows OS**: Required for full functionality (uses Windows-specific APIs)
- **Execution Policy**: May need to be adjusted for script execution

#### 🚀 Using PowerShell Scripts

1. **Initial Setup**:
    ```powershell
    # Navigate to project directory
    cd path/to/my_translator

    # Start the server (auto-setup mode)
    # Note: First run may take longer as it sets up virtual environment
    .\start_server.ps1
    ```

2. **Check Server Status**:
    ```powershell
    # If PID file exists, server is running
    Get-Content app.pid  # Shows current process ID
    ```

3. **Stop the Server**:
    ```powershell
    # Gracefully stops server and all child processes
    .\stop_server.ps1
    ```

#### 🔧 PowerShell Script Features

**start_server.ps1 Features**:
- Automatic virtual environment detection and setup
- Background execution (no console window)
- Process ID tracking via `app.pid` file
- Comprehensive error handling
- Silent operation suitable for scheduled tasks

**stop_server.ps1 Features**:
- Safe shutdown of main process and all child processes
- Recursive child process termination
- PID file validation and cleanup
- Process existence verification
- Clean termination even if processes are unresponsive

#### 🛡️ Error Handling

The scripts include robust error handling for common scenarios:
- Missing virtual environment
- Invalid PID files
- Process not found
- Permission issues
- Child process cleanup failures

#### 📁 Files Generated

- `app.pid`: Contains the main process ID for server management
- `.venv/`: Virtual environment (created automatically in auto-setup mode)

## 💡 How to Use

1.  Start the backend server: `python app.py`
2.  Open `index.html` in your browser.
3.  Select the desired AI model from the dropdown menu at the top (successfully used models appear first as presets).
4.  Choose the target language for translation.
5.  Type or paste the text you want to translate into the left-hand text box (character count shown in real-time).
6.  Click the "번역하기" (Translate) button.
7.  The translated text will appear in the right-hand box.
8.  Successfully used models are automatically saved as presets for future sessions.

## 🛠️ Technologies Used

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python, Flask
- **APIs**: Google Gemini API, OpenAI API
