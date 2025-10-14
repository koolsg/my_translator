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

### 1. Configure API Keys

First, you need to provide your API keys.

1. **Copy the example configuration**:
   ```bash
   cp config.json.example config.
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

### 2. Install Dependencies

You need Python 3 installed. Open your terminal and navigate to the project directory, then install the required Python libraries.

```bash
# Navigate to the project folder
cd path/to/my_translator

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the Backend Server

Once the dependencies are installed, start the Flask backend server.

```bash
python app.py
```

You should see a message indicating that the server is running on `http://127.0.0.1:5000`. Keep this terminal window open.

### 4. Open the Translator

Open the `index.html` file in your favorite web browser (e.g., by double-clicking the file).

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
