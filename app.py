"""
Translation API Server

A Flask-based API server for text translation using OpenAI GPT and Google Gemini models.
"""

import json
import logging
import random
import sys
from typing import Dict, List, Optional, Any, cast

from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import google.generativeai as genai

# Constants
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 5000
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
DEFAULT_PROVIDER = 'gemini'
MAX_PRESETS = 5

# Logging configuration
def setup_logging(debug: bool = False) -> None:
    """Configure logging for the application."""
    log_level = logging.DEBUG if debug else logging.INFO
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('translation_server.log', encoding='utf-8')
        ]
    )

    # Set specific log levels for noisy libraries
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('flask').setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)
    logger.info("Logging configured successfully")


class ConfigManager:
    """Configuration file manager with JSON parsing and validation."""

    def __init__(self, config_path: str = 'config.json') -> None:
        self.config_path = config_path
        self._config: Optional[Dict[str, Any]] = None
        self.logger = logging.getLogger(__name__)

    def load(self) -> Dict[str, Any]:
        """Load and parse configuration file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_text = f.read()

            # Remove comments (# and after)
            lines = []
            for line in config_text.split('\n'):
                if '#' in line:
                    line = line[:line.find('#')].rstrip()
                if line.strip():
                    lines.append(line)

            config_text_cleaned = '\n'.join(lines)
            config = json.loads(config_text_cleaned)

            # Ensure config is a dictionary
            if not isinstance(config, dict):
                raise ValueError("Configuration must be a JSON object (dictionary)")

            self._config = cast(Dict[str, Any], config)
            self.logger.info("Configuration loaded successfully.")
            return self._config

        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to load configuration: {e}")

    def get_config(self) -> Dict[str, Any]:
        """Get cached configuration."""
        if self._config is None:
            self._config = self.load()
        return self._config

    def save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file."""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)


class GeminiTranslator:
    """Translation service using Google Gemini API."""

    def __init__(self, config_manager: ConfigManager) -> None:
        self.config_manager = config_manager

    def validate_api_keys(self) -> List[str]:
        """Validate and return Gemini API keys."""
        config = self.config_manager.get_config()
        api_keys = config.get('gemini', {}).get('api_keys', [])

        if not api_keys or not all(api_keys):
            raise ValueError("Gemini API keys not configured properly")

        return api_keys

    def translate(self, text: str, model_name: str, target_language: str) -> str:
        """Translate text using specified Gemini model."""
        api_keys = self.validate_api_keys()
        selected_key = random.choice(api_keys)

        genai.configure(api_key=selected_key)
        model = genai.GenerativeModel(model_name)
        prompt = f"Translate the following text to {target_language}: \n\n{text}"

        response = model.generate_content(prompt)
        return response.text


class OpenAITranslator:
    """Translation service using OpenAI GPT API."""

    def __init__(self, config_manager: ConfigManager) -> None:
        self.config_manager = config_manager

    def validate_api_key(self) -> str:
        """Validate and return OpenAI API key."""
        config = self.config_manager.get_config()
        api_key = config.get('openai', {}).get('api_key')

        if not api_key:
            raise ValueError("OpenAI API key not configured")

        return api_key

    def translate(self, text: str, model_name: str, target_language: str) -> str:
        """Translate text using specified OpenAI model."""
        api_key = self.validate_api_key()
        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": f"You are a translator. Translate the given text to {target_language}."},
                {"role": "user", "content": text}
            ]
        )
        content = response.choices[0].message.content
        return content if content is not None else ""


class TranslationService:
    """Main translation service coordinating different providers."""

    def __init__(self, config_manager: ConfigManager) -> None:
        self.config_manager = config_manager
        self.gemini_translator = GeminiTranslator(config_manager)
        self.openai_translator = OpenAITranslator(config_manager)
        self.logger = logging.getLogger(__name__)

    def translate(self, text: str, model_name: str, target_language: str) -> str:
        """Translate text using appropriate provider based on model name."""
        if 'gemini' in model_name:
            return self.gemini_translator.translate(text, model_name, target_language)
        elif 'gpt' in model_name:
            return self.openai_translator.translate(text, model_name, target_language)
        else:
            raise ValueError(f"Unsupported model: {model_name}")

    def get_available_models(self, provider: str) -> List[str]:
        """Get available models for specified provider, with presets first."""
        config = self.config_manager.get_config()
        available_models = []

        # Add preset models for the provider
        presets = config.get('presets', {}).get('models', [])
        provider_filter = 'gemini' if provider == 'gemini' else 'gpt'
        provider_presets = [
            model for model in presets
            if provider_filter in model
        ]
        available_models.extend(provider_presets)

        # Fetch dynamic models
        if provider == 'gemini':
            available_models.extend(self._get_gemini_models())
        elif provider == 'openai':
            available_models.extend(self._get_openai_models())

        # Remove duplicates while preserving order
        seen = set()
        unique_models = []
        for model in available_models:
            if model not in seen:
                seen.add(model)
                unique_models.append(model)

        return unique_models

    def _get_gemini_models(self) -> List[str]:
        """Fetch available Gemini models with fallback to saved models."""
        try:
            api_keys = self.gemini_translator.validate_api_keys()
            genai.configure(api_key=random.choice(api_keys))

            models = []
            for model_info in genai.list_models():
                if 'generateContent' in model_info.supported_generation_methods:
                    models.append(model_info.name)

            return models

        except Exception as e:
            self.logger.error(f"Failed to fetch Gemini models: {e}")
            # Fallback to saved models
            config = self.config_manager.get_config()
            return config.get('gemini', {}).get('available_models', [])

    def _get_openai_models(self) -> List[str]:
        """Fetch available OpenAI models with fallback to saved models."""
        try:
            
            api_key = self.openai_translator.validate_api_key()

            if api_key == 'YOUR_OPENAI_API_KEY_HERE':
                raise ValueError("OpenAI API key not configured")

            import openai as openai_module
            openai_module.api_key = api_key
            account_info = openai_module.models.list()
            return [model.id for model in account_info.data]

        except Exception as e:
            self.logger.error(f"Failed to fetch OpenAI models: {e}")
            # Fallback to saved models
            config = self.config_manager.get_config()
            return config.get('openai', {}).get('available_models', [])

    def save_preset_model(self, model_name: str) -> None:
        """Save model to presets, maintaining max limit."""
        config = self.config_manager.get_config()

        if 'presets' not in config:
            config['presets'] = {'models': [], 'targets': []}

        presets = config['presets']['models']
        if model_name not in presets:
            presets.insert(0, model_name)  # Add to beginning
            # Trim to max presets
            if len(presets) > MAX_PRESETS:
                presets[:] = presets[:MAX_PRESETS]

            self.config_manager.save_config(config)
            self.logger.info(f"Model '{model_name}' saved to presets.")


def create_app(config_path: str = 'config.json') -> Flask:
    """Application factory for Flask app."""
    app = Flask(__name__)
    CORS(app)

    # Configure Flask settings
    app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

    # Initialize services
    config_manager = ConfigManager(config_path)
    translation_service = TranslationService(config_manager)

    # Logger is available through Flask's app.logger

    @app.route('/models', methods=['GET'])
    def get_models() -> Any:
        """Get available models for specified provider."""
        provider = request.args.get('provider', DEFAULT_PROVIDER)

        if provider not in ['gemini', 'openai']:
            return jsonify({"error": "Invalid provider. Must be 'gemini' or 'openai'"}), 400

        try:
            models = translation_service.get_available_models(provider)
            return jsonify(models)
        except Exception as e:
            logging.getLogger(__name__).error(f"Error fetching models: {e}")
            return jsonify({"error": "Failed to fetch models"}), 500

    @app.route('/translate', methods=['POST'])
    def translate_text() -> Any:
        """Translate text using specified model and target language."""
        data = request.get_json()

        required_fields = ['text', 'model', 'target_language']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Missing required field: {field}"}), 400

        text = data['text']
        model_choice = data['model']
        target_language = data['target_language']

        try:
            logging.getLogger(__name__).info(f"Translating with {model_choice} to {target_language}")
            translated_text = translation_service.translate(text, model_choice, target_language)

            # Save successful model to presets
            try:
                translation_service.save_preset_model(model_choice)
            except Exception as e:
                logging.getLogger(__name__).warning(f"Failed to save preset (ignoring): {e}")

            return jsonify({'translated_text': translated_text})

        except ValueError as e:
            error_msg = str(e)
            logging.getLogger(__name__).warning(f"Validation error: {error_msg}")
            return jsonify({"error": error_msg}), 400
        except Exception as e:
            error_msg = str(e)
            logging.getLogger(__name__).error(f"Translation error: {error_msg}")
            return jsonify({"error": error_msg}), 500

    return app


if __name__ == '__main__':
    # Setup logging first
    setup_logging(debug=True)

    # Load configuration first
    try:
        app = create_app()
        logger = logging.getLogger(__name__)
        logger.info("Starting translation server...")
        logger.info(f"Server running on http://{DEFAULT_HOST}:{DEFAULT_PORT}")
        app.run(host=DEFAULT_HOST, port=DEFAULT_PORT, debug=True)
    except Exception as e:
        logging.getLogger(__name__).critical(f"Fatal error: {e}")
        exit(1)
