import os
import json
import platform
from flask import Blueprint, jsonify, request
from core.extensions import require_api_key
from services.ai_advisor import ai_chat_completion, AI_INTERVIEWER_PREAMBLE

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/api/ai/chat', methods=['POST'])
@require_api_key
def ai_chat():
    data = request.get_json() or {}
    message = data.get('message', '')
    chat_history = data.get('history', [])
    result = ai_chat_completion(message, chat_history)
    return jsonify(result)

@ai_bp.route('/api/ai/chat/image', methods=['POST'])
@require_api_key
def ai_chat_image():
    try:
        import pytesseract
        from PIL import Image
        
        if platform.system() == 'Windows':
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
            
        file = request.files['image']
        img = Image.open(file.stream)
        
        try:
            extracted_text = pytesseract.image_to_string(img)
        except Exception as ocr_err:
            extracted_text = f"OCR Error: {ocr_err}"
            
        cohere_key = os.getenv("COHERE_API_KEY", "").strip()
        if cohere_key:
            try:
                import cohere
                co = cohere.Client(cohere_key)
                chat_history = json.loads(request.form.get('history', '[]'))
                cohere_history = [
                    {"role": "USER" if msg['role'] == 'user' else "CHATBOT", "message": msg['content']}
                    for msg in chat_history
                ]
                prompt = (
                    f"The user uploaded an image. Here is the raw text extracted from it via OCR:\n\n"
                    f"---\n{extracted_text}\n---\n\n"
                    f"Please analyze this text and answer the user's implicit question or provide a helpful summary of the financial data shown."
                )
                response = co.chat(
                    message=prompt,
                    chat_history=cohere_history,
                    preamble=AI_INTERVIEWER_PREAMBLE,
                    model='command-r-plus-08-2024',
                    temperature=0.5,
                    max_tokens=800
                )
                return jsonify({
                    'success': True,
                    'response': response.text,
                    'extracted_text': extracted_text,
                    'tokens_used': response.meta.tokens.input_tokens if response.meta else None
                })
            except Exception as e:
                print(f"[Aria OCR] Cohere error: {e}")

        clean_text = extracted_text.strip() if extracted_text else "No readable text detected in this image."
        fallback_msg = f"📄 **Extracted text from image:**\n\n```\n{clean_text}\n```\n\n💡 *Tip: Configure `COHERE_API_KEY` in `.env` for AI image insights.*"
        return jsonify({
            'success': True,
            'response': fallback_msg,
            'extracted_text': extracted_text
        })
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500
