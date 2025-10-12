import os
import json
import random
import google.generativeai as genai
import openai
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- config.json 파일에서 설정 불러오기 ---
try:
    with open('config.json', 'r') as f:
        config_text = f.read()
        # 주석(# 이후부터 떨어내기) 처리
        lines = []
        for line in config_text.split('\n'):
            if '#' in line:
                line = line[:line.find('#')].rstrip()
            if line.strip():  # 빈 줄 건너뛰기
                lines.append(line)
        config_text_cleaned = '\n'.join(lines)
        config = json.loads(config_text_cleaned)
    print("config.json 파일을 성공적으로 불러왔습니다.")
except Exception as e:
    print(f"치명적 오류: config.json 파일을 읽을 수 없거나 형식이 잘못되었습니다. 프로그램을 종료합니다.")
    print(f"오류 내용: {e}")
    exit()

app = Flask(__name__)
CORS(app)

# --- 번역 함수 분리 (모델 이름과 대상 언어를 파라미터로 받도록 수정) ---
def translate_with_gemini(text, model_name, target_language):
    api_keys = config.get('gemini', {}).get('api_keys', [])
    if not api_keys or not all(api_keys):
        raise ValueError("Gemini API 키가 config.json에 설정되지 않았습니다.")
    
    selected_key = random.choice(api_keys)
    genai.configure(api_key=selected_key)
    
    model = genai.GenerativeModel(model_name)
    prompt = f"Translate the following text to {target_language}: \n\n{text}"
    response = model.generate_content(prompt)
    return response.text

def translate_with_openai(text, model_name, target_language):
    openai_config = config.get('openai', {})
    api_key = openai_config.get('api_key')

    if not api_key:
        raise ValueError("OpenAI API 키가 config.json에 설정되지 않았습니다.")

    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": f"You are a translator. Translate the given text to {target_language}."},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content

# --- API 라우트 ---

@app.route('/models', methods=['GET'])
def get_models():
    """선택된 Provider의 사용 가능한 모델 목록을 반환하는 엔드포인트 - 프리셋 모델 우선 표시"""
    provider = request.args.get('provider', 'gemini')  # 기본값은 gemini
    available_models = []

    # 프리셋 모델들 중 해당 provider의 것만 먼저 추가
    presets = config.get('presets', {}).get('models', [])
    provider_presets = [model for model in presets if ('gemini' in model and provider == 'gemini') or ('gpt' in model and provider == 'openai')]
    available_models.extend(provider_presets)

    if provider == 'gemini':
        # Gemini 모델 목록 가져오기
        try:
            gemini_api_keys = config.get('gemini', {}).get('api_keys', [])
            if gemini_api_keys and all(gemini_api_keys):
                genai.configure(api_key=random.choice(gemini_api_keys))
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        model_name = m.name
                        if model_name not in available_models:  # 프리셋에 없는 경우만 추가
                            available_models.append(model_name)
            else:
                # API key가 없는 경우 저장된 모델 목록 사용
                saved_models = config.get('gemini', {}).get('available_models', [])
                available_models.extend([model for model in saved_models if model not in available_models])
        except Exception as e:
            print(f"Gemini 모델 목록을 가져오는 중 오류 발생: {e}")
            # 저장된 모델 목록으로 fallback
            saved_models = config.get('gemini', {}).get('available_models', [])
            available_models.extend([model for model in saved_models if model not in available_models])

    elif provider == 'openai':
        # OpenAI 모델 목록 가져오기
        try:
            openai_config = config.get('openai', {})
            if openai_config.get('api_key') and openai_config.get('api_key') != 'YOUR_OPENAI_API_KEY_HERE':
                import openai
                openai.api_key = openai_config.get('api_key')
                account_info = openai.models.list()
                for model in account_info.data:
                    model_name = model.id
                    if model_name not in available_models:  # 프리셋에 없는 경우만 추가
                        available_models.append(model_name)
            else:
                # API key가 없거나 기본값인 경우 저장된 모델 목록 사용
                saved_models = config.get('openai', {}).get('available_models', [])
                available_models.extend([model for model in saved_models if model not in available_models])
        except Exception as e:
            print(f"OpenAI 모델 목록을 가져오는 중 오류 발생: {e}")
            # 저장된 모델 목록으로 fallback
            saved_models = config.get('openai', {}).get('available_models', [])
            available_models.extend([model for model in saved_models if model not in available_models])

    return jsonify(available_models)

@app.route('/translate', methods=['POST'])
def translate_text_route():
    data = request.get_json()
    input_text = data.get('text')
    model_choice = data.get('model') # 프론트엔드에서 정확한 모델 이름을 전달
    target_language = data.get('target_language') # 프론트엔드에서 대상 언어를 전달

    if not input_text:
        return jsonify({"error": "No text provided"}), 400
    if not model_choice:
        return jsonify({"error": "No model selected"}), 400
    if not target_language:
        return jsonify({"error": "No target language selected"}), 400

    try:
        translated_text = ""
        print(f"{model_choice} 모델로 {target_language}로 번역을 요청합니다...")

        # 모델 이름에 따라 적절한 함수 호출
        if 'gemini' in model_choice:
            translated_text = translate_with_gemini(input_text, model_choice, target_language)
        elif 'gpt' in model_choice:
            translated_text = translate_with_openai(input_text, model_choice, target_language)
        else:
            return jsonify({"error": f"Unsupported model: {model_choice}"}), 400
        
        print("번역 완료.")

        # 번역 성공 시 프리셋에 모델 저장
        try:
            if 'presets' not in config:
                config['presets'] = {'models': [], 'targets': []}
            if model_choice not in config['presets']['models']:
                config['presets']['models'].insert(0, model_choice)  # 최상단에 추가
                # 최대 5개로 제한
                if len(config['presets']['models']) > 5:
                    config['presets']['models'] = config['presets']['models'][:5]
                # config.json 파일 업데이트
                with open('config.json', 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                print(f"모델 '{model_choice}'을 프리셋에 저장했습니다.")
        except Exception as e:
            print(f"프리셋 저장 중 오류 발생 (무시): {e}")

        return jsonify({'translated_text': translated_text})

    except Exception as e:
        error_message = str(e)
        print(f"번역 중 오류 발생: {error_message}")
        return jsonify({"error": error_message}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
