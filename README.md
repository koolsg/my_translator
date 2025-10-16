# My Local Translator

My Local Translator is a simple, self-hosted web application that allows you to translate text using different large language models from Google (Gemini) and OpenAI (GPT).

## Features

-   **Simple Interface**: A clean and straightforward interface for translating text.
-   **Multiple Providers**: Supports both Google Gemini and OpenAI models.
-   **Model Selection**: Choose from a list of available models from your selected provider.
-   **Remembers your last choice**: The application remembers the last provider and model you used, making it convenient for repeated use.
-   **Windows Notifications**: Get a desktop notification when a translation is complete.
-   **Local First**: Your API keys and configuration are stored locally on your machine.

## How to Use

### 1. Prerequisites

-   Python 3.x
-   [uv](https://github.com/astral-sh/uv) (for Python package management)
-   API keys for Google Gemini and/or OpenAI.

### 2. Installation

1.  **Clone the repository or download the files.**

2.  **Create a virtual environment and install dependencies:**
    ```shell
    # Create a virtual environment
    uv venv

    # Activate the environment
    # On Windows (PowerShell)
    .venv\Scripts\Activate.ps1

    # Install the required packages
    uv pip install -r requirements.txt
    ```

### 3. Configuration

1.  **Create the configuration file:**
    -   Make a copy of `config.json.example` and rename it to `config.json`.

2.  **Add your API keys:**
    -   Open `config.json` and paste your API keys in the appropriate fields.

    ```json
    {
      "gemini": {
        "api_keys": ["your_gemini_api_key_here"]
      },
      "openai": {
        "api_key": "your_openai_api_key_here"
      }
    }
    ```

### 4. Running the Application

1.  **Start the server:**
    -   Run the provided PowerShell script to start the backend server.
    ```powershell
    ./start_server.ps1
    ```

2.  **Open the translator:**
    -   Open the `index.html` file in your web browser.

You can now start translating!

### 5. Stopping the Server

-   To stop the background server, run the `stop_server.ps1` script.
    ```powershell
    ./stop_server.ps1
    ```