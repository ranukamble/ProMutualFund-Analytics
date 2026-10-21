from flask import Blueprint, jsonify, request
from core.extensions import TASKS
from services.portfolio import calculate_portfolio_metrics
from services.portfolio_builder import (
    build_generated_portfolio, 
    save_portfolio_entry, 
    list_saved_portfolios, 
    delete_saved_portfolio, 
    auto_build_portfolio_by_risk
)
from services.ai_advisor import start_ai_generation_task

portfolio_bp = Blueprint('portfolio', __name__)

@portfolio_bp.route('/api/portfolio/generate', methods=['POST'])
def generate_portfolio():
    try:
        data = request.get_json() or {}
        portfolio_items = data.get('portfolio', [])
        investment_amount = data.get('investment_amount', 100000)
        investment_type = data.get('investment_type', 'lumpsum')
        duration_years = int(data.get('duration_years', 5))
        
        result, status_code = build_generated_portfolio(
            portfolio_items=portfolio_items,
            investment_amount=investment_amount,
            investment_type=investment_type,
            duration_years=duration_years
        )
        return jsonify(result), status_code
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500

@portfolio_bp.route('/api/portfolio/save', methods=['POST'])
def save_portfolio():
    try:
        data = request.get_json() or {}
        new_id = save_portfolio_entry(data)
        return jsonify({
            'success': True,
            'portfolio_id': new_id,
            'message': 'Portfolio saved successfully!'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@portfolio_bp.route('/api/portfolio/list', methods=['GET'])
def list_portfolios():
    try:
        portfolios = list_saved_portfolios()
        return jsonify({'portfolios': portfolios})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@portfolio_bp.route('/api/portfolio/delete/<int:pid>', methods=['DELETE'])
def delete_portfolio(pid):
    try:
        success = delete_saved_portfolio(pid)
        if not success:
            return jsonify({'success': False, 'error': 'Portfolio not found'}), 404
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@portfolio_bp.route('/api/portfolio/analyze', methods=['POST'])
def analyze_portfolio():
    data = request.json or {}
    funds = data.get('funds', [])
    allocation = data.get('allocation', {})
    investment_details = data.get('investment_details', {})
    result = calculate_portfolio_metrics(funds, allocation, investment_details)
    return jsonify(result)

@portfolio_bp.route('/api/portfolio/auto-build', methods=['POST'])
def auto_build():
    data = request.get_json() or {}
    risk = data.get('risk', 'moderate').lower()
    inv_type = data.get('type', 'sip').lower()
    amount = data.get('amount', 10000)
    duration = data.get('duration', 5)
    result = auto_build_portfolio_by_risk(risk, inv_type, amount, duration)
    return jsonify(result)

@portfolio_bp.route('/api/portfolio/ai-generate', methods=['POST'])
def ai_generate_portfolio():
    try:
        data = request.get_json() or {}
        api_key = data.get('api_key', '')
        if not api_key:
            return jsonify({'success': False, 'error': 'Cohere API Key is required.'}), 400
            
        task_id = start_ai_generation_task(
            api_key=api_key,
            inv_type=data.get('type', 'lumpsum'),
            inv_amt=data.get('amount', 100000),
            duration_years=data.get('years', 5),
            risk_level=data.get('risk', 'medium')
        )
        return jsonify({'success': True, 'task_id': task_id}), 202
    except Exception as e:
        return jsonify({'success': False, 'error': f"AI generation enqueue failed: {str(e)}"}), 500

@portfolio_bp.route('/api/portfolio/status/<task_id>', methods=['GET'])
def task_status(task_id):
    task = TASKS.get(task_id)
    if not task:
        return jsonify({'state': 'FAILURE', 'success': False, 'error': 'Task not found'}), 404
        
    if task['state'] == 'PENDING':
        return jsonify({'state': 'PENDING', 'status': 'Pending...'})
    elif task['state'] == 'SUCCESS':
        return jsonify({'state': 'SUCCESS', 'success': True, 'funds': task['funds'], 'name': 'AI Optimal Growth Portfolio'})
    else:
        return jsonify({'state': 'FAILURE', 'success': False, 'error': task.get('error', 'Unknown error')})
