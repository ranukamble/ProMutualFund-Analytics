import os
import re
import json
import uuid
import threading
import platform
import requests
from core.extensions import socketio, TASKS

AI_INTERVIEWER_PREAMBLE = """
You are Aria, a friendly and professional AI financial advisor 
for Pro Mutual Fund Analytics. Your ONLY job right now is to 
conduct a quick 4-question onboarding interview to understand 
the user's investment profile, then build them a personalized 
mutual fund portfolio.

## YOUR PERSONALITY:
- Warm, encouraging, and professional
- Use simple language — avoid jargon
- Celebrate when user provides information (e.g., "Great choice!")
- Keep responses SHORT (2-3 lines max per message)
- Add relevant emojis to make it feel friendly

## THE 4 DATA POINTS YOU MUST COLLECT:
1. Investment TYPE → SIP (monthly) or Lumpsum (one-time)
2. Investment AMOUNT → In Indian Rupees (₹)
3. Investment HORIZON → Number of years (1-40)
4. Risk APPETITE → Conservative / Moderate / Aggressive

## CONVERSATION FLOW — Follow this EXACTLY:

### Opening Message (when user first opens chat):
"Hi! I'm Aria, your personal portfolio advisor 👋

I'll help you build a customized mutual fund portfolio in just 
4 quick questions. Ready to get started? 🚀"

### Step 1 — Ask Investment Type:
"First question: Would you prefer to invest a 
**fixed amount every month** (SIP) or make a 
**one-time large investment** (Lumpsum)?

💡 SIP is great for salaried individuals — builds discipline!
Lumpsum works well if you have a windfall or bonus."

### Step 2 — Ask Amount:
Based on their choice, ask appropriately:
- If SIP: "How much can you invest monthly? 
  Common amounts: ₹1,000 / ₹5,000 / ₹10,000 / ₹25,000"
- If Lumpsum: "How much are you looking to invest as a 
  one-time amount? (e.g., ₹50,000 / ₹1 Lakh / ₹5 Lakhs)"

### Step 3 — Ask Horizon:
"For how many years do you want to stay invested?
  
  📅 Short term: 1-3 years
  📅 Medium term: 3-7 years  
  📅 Long term: 7+ years (Recommended for wealth creation)"

### Step 4 — Ask Risk:
"Last question! What's your risk appetite?

🟢 **Conservative** — Safety first, lower but stable returns
🟡 **Moderate** — Balanced approach, medium risk & returns  
🔴 **Aggressive** — Higher risk for potentially higher returns

Which best describes you?"

## AFTER COLLECTING ALL 4 DATA POINTS:

1. Give a brief, exciting summary message:
   "Perfect! 🎯 Building your [RISK] portfolio now...
   
   📊 **Your Profile:**
   - Type: [TYPE]
   - Amount: ₹[AMOUNT]
   - Duration: [YEARS] years
   - Risk: [RISK]
   
   Generating your personalized portfolio in seconds! ✨"

2. IMMEDIATELY after that message, output this EXACT JSON block:

```json
{
  "command": "BUILD_PORTFOLIO",
  "type": "[sip or lumpsum]",
  "amount": [number],
  "duration": [number],
  "risk": "[conservative or moderate or aggressive]"
}
```

## RULES:
- Ask ONE question at a time — never multiple questions together
- If user gives unclear answer, gently ask again with examples
- If user gives a range (e.g., "5-10 years"), pick the middle
- Accept natural language: "high risk" = aggressive, "safe" = conservative, "balanced" = moderate
- For amounts: accept "1 lakh" = 100000, "5k" = 5000, "10 thousand" = 10000
- NEVER discuss specific fund names — you only collect preferences
- Keep track of what's been answered — don't re-ask
"""

def fallback_ai_interview(message: str, chat_history: list) -> str:
    """
    Intelligent conversational fallback for Aria when COHERE_API_KEY is not supplied.
    """
    all_user_texts = [msg.get('content', '') for msg in chat_history if msg.get('role') == 'user']
    all_user_texts.append(message)
    last_msg = message.strip().lower()

    def extract_type(text):
        t = text.lower()
        if any(w in t for w in ['sip', 'monthly', 'every month', 'month']):
            return 'sip'
        if any(w in t for w in ['lumpsum', 'lump', 'one time', 'one-time', 'onetime']):
            return 'lumpsum'
        return None

    def extract_amount(text):
        text_clean = text.lower().replace(',', '')
        m_cr = re.search(r'(\d+(?:\.\d+)?)\s*(?:cr|crore)', text_clean)
        if m_cr: return int(float(m_cr.group(1)) * 10000000)
        m_lakh = re.search(r'(\d+(?:\.\d+)?)\s*(?:lakh|lac|l\b)', text_clean)
        if m_lakh: return int(float(m_lakh.group(1)) * 100000)
        m_k = re.search(r'(\d+(?:\.\d+)?)\s*k\b', text_clean)
        if m_k: return int(float(m_k.group(1)) * 1000)
        m_num = re.search(r'(?:₹|rs\.?|inr)?\s*(\d+)', text_clean)
        if m_num:
            val = int(m_num.group(1))
            if val >= 500: return val
        return None

    def extract_duration(text):
        text_clean = text.lower()
        m_yr = re.search(r'(\d+)\s*(?:years?|yrs?|y\b)', text_clean)
        if m_yr: return int(m_yr.group(1))
        words = text_clean.strip().split()
        if len(words) == 1 and words[0].isdigit():
            val = int(words[0])
            if 1 <= val <= 40: return val
        return None

    def extract_risk(text):
        t = text.lower()
        if any(w in t for w in ['conserv', 'safe', 'low risk', 'low', 'capital protection']): return 'conservative'
        if any(w in t for w in ['aggress', 'high risk', 'high', 'maximum', 'wealth creation']): return 'aggressive'
        if any(w in t for w in ['moderat', 'medium', 'balanced', 'normal']): return 'moderate'
        return None

    collected_type, collected_amount, collected_duration, collected_risk = None, None, None, None

    for txt in all_user_texts:
        if not collected_type: collected_type = extract_type(txt)
        if not collected_amount: collected_amount = extract_amount(txt)
        if not collected_duration: collected_duration = extract_duration(txt)
        if not collected_risk: collected_risk = extract_risk(txt)

    if 'tell me more' in last_msg or 'explain' in last_msg or 'how it works' in last_msg:
        return (
            "Mutual fund portfolio creation helps diversify your capital across top-performing equity, hybrid, and debt schemes according to your personal financial horizon and risk tolerance.\n\n"
            "I'll ask you 4 quick questions (Investment Type, Amount, Duration, Risk) to build your optimal portfolio. Would you prefer a monthly **SIP** or a one-time **Lumpsum**?"
        )

    if not collected_type:
        return (
            "First question: Would you prefer to invest a **fixed amount every month** (SIP) or make a **one-time large investment** (Lumpsum)?\n\n"
            "💡 *SIP is great for salaried investors to build long-term wealth, while Lumpsum works well for bonuses or windfalls.*"
        )

    if not collected_amount:
        if collected_type == 'sip':
            return "Great choice! 📅 **SIP** it is.\n\nHow much would you like to invest monthly? (e.g., **₹1,000**, **₹5,000**, **₹10,000**, or **₹25,000**)"
        else:
            return "Perfect! 💰 **Lumpsum** investment.\n\nHow much are you looking to invest as a one-time capital? (e.g., **₹25,000**, **₹50,000**, **₹1 Lakh**, or **₹5 Lakhs**)"

    if not collected_duration:
        return (
            f"Got it, **₹{collected_amount:,}** {'per month' if collected_type == 'sip' else 'lumpsum'}! 💼\n\n"
            "For how many years do you plan to stay invested?\n\n"
            "📅 **Short term:** 1 - 3 years\n"
            "📅 **Medium term:** 3 - 7 years\n"
            "📅 **Long term:** 7+ years *(Recommended for compounding)*"
        )

    if not collected_risk:
        return (
            f"Understood, a **{collected_duration}-year** investment horizon! ⏳\n\n"
            "Last question: What is your risk appetite?\n\n"
            "🟢 **Conservative** — Focus on capital safety with steady returns\n"
            "🟡 **Moderate** — Balanced growth with manageable risk\n"
            "🔴 **Aggressive** — High equity allocation for maximum growth\n\n"
            "Which profile suits you best?"
        )

    json_cmd = json.dumps({
        "command": "BUILD_PORTFOLIO",
        "type": collected_type,
        "amount": collected_amount,
        "duration": collected_duration,
        "risk": collected_risk
    })

    return (
        f"Perfect! 🎯 Building your **{collected_risk.upper()}** portfolio now...\n\n"
        f"📊 **Your Profile:**\n"
        f"- **Strategy:** {collected_type.upper()}\n"
        f"- **Amount:** ₹{collected_amount:,}{'/month' if collected_type == 'sip' else ' (Lumpsum)'}\n"
        f"- **Duration:** {collected_duration} years\n"
        f"- **Risk:** {collected_risk.capitalize()}\n\n"
        f"Generating your personalized portfolio in seconds! ✨\n\n"
        f"```json\n{json_cmd}\n```"
    )

def run_ai_task(task_id, api_key, inv_type, inv_amt, duration_years, risk_level):
    try:
        socketio.emit('task_update', {'task_id': task_id, 'state': 'PENDING', 'message': 'AI analysis started...'})
        prompt = f"""You are an expert financial advisor. The user wants an optimal, HIGHLY DIVERSIFIED mutual fund portfolio.
The user is planning a {inv_type.upper()} investment of ₹{inv_amt} for a duration of {duration_years} years.
Their risk tolerance is {risk_level.upper()}.
If risk tolerance is LOW, heavily favor Debt and Hybrid funds.
If risk tolerance is HIGH, heavily favor pure Equity funds (Small/Mid/Flexi Cap).
If risk tolerance is MEDIUM, balance between Large Cap/Flexi Cap Equity and Hybrid funds.

CRITICAL RULE on number of funds based on investment amount:
- If investment amount is less than ₹5000, select ONLY 3 to 4 funds.
- If investment amount is between ₹5000 and ₹15000, select 5 to 7 funds.
- If investment amount is above ₹15000, select 7 to 9 funds.

Based on this profile, suggest a portfolio of top-performing DIRECT PLAN mutual funds in India.
Assign percentage weights (must total exactly 100).
Respond ONLY with a valid JSON array. Format: [{{"name": "Parag Parikh Flexi Cap Fund Direct Growth", "category": "Flexi Cap", "weight": 40}}, ...]
"""
        socketio.emit('task_update', {'task_id': task_id, 'state': 'PENDING', 'message': 'Sending prompt to Cohere...'})
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        payload = {
            'model': 'command-r-plus-08-2024',
            'message': prompt,
            'temperature': 0.7
        }
        resp = requests.post('https://api.cohere.com/v1/chat', headers=headers, json=payload, timeout=60)
        if resp.status_code != 200:
            TASKS[task_id] = {'state': 'FAILURE', 'error': f"Cohere API Error: {resp.text}"}
            socketio.emit('task_update', {'task_id': task_id, 'state': 'FAILURE', 'error': f"Cohere API Error: {resp.text}"})
            return
            
        socketio.emit('task_update', {'task_id': task_id, 'state': 'PENDING', 'message': 'Processing AI response & searching fund codes...'})
        result_text = resp.json().get('text', '').strip()
        result_text = result_text.replace('```json', '').replace('```', '').strip()
        match = re.search(r'\[.*\]', result_text, re.DOTALL)
        if match:
            result_text = match.group(0)
            
        ai_funds = json.loads(result_text)
        funds = []
        for f in ai_funds:
            try:
                search_q = f['name'].replace(' ', '%20')
                search_resp = requests.get(f"https://api.mfapi.in/mf/search?q={search_q}", timeout=5)
                results = search_resp.json()
                if results:
                    best = results[0]
                    funds.append({
                        'code': str(best['schemeCode']),
                        'name': best['schemeName'],
                        'weight': f.get('weight', 0),
                        'category': f.get('category', 'Equity'),
                        'allocation_pct': f.get('weight', 0) / 100
                    })
            except Exception as e:
                print("Failed to search fund:", f['name'], e)
                
        if not funds:
            raise Exception("AI did not return any valid fund names that could be found in the API.")
                
        TASKS[task_id] = {'state': 'SUCCESS', 'funds': funds}
        socketio.emit('task_update', {'task_id': task_id, 'state': 'SUCCESS', 'funds': funds})
    except Exception as e:
        TASKS[task_id] = {'state': 'FAILURE', 'error': str(e)}
        socketio.emit('task_update', {'task_id': task_id, 'state': 'FAILURE', 'error': str(e)})

def start_ai_generation_task(api_key, inv_type, inv_amt, duration_years, risk_level):
    task_id = str(uuid.uuid4())
    TASKS[task_id] = {'state': 'PENDING'}
    t = threading.Thread(target=run_ai_task, args=(task_id, api_key, inv_type, inv_amt, duration_years, risk_level))
    t.start()
    return task_id

def ai_chat_completion(message, chat_history):
    cohere_key = os.getenv("COHERE_API_KEY", "").strip()
    if cohere_key:
        try:
            import cohere
            co = cohere.Client(cohere_key)
            cohere_history = [
                {"role": "USER" if msg.get('role') == 'user' else "CHATBOT", "message": msg.get('content', '')}
                for msg in chat_history
            ]
            response = co.chat(
                message=message,
                chat_history=cohere_history,
                preamble=AI_INTERVIEWER_PREAMBLE,
                model='command-r-plus-08-2024',
                temperature=0.7,
                max_tokens=500
            )
            return {
                'success': True,
                'response': response.text,
                'tokens_used': response.meta.tokens.input_tokens if response.meta else None
            }
        except Exception as e:
            print(f"[Aria] Cohere API error ({e}), switching to fallback interview.")
            
    fallback_text = fallback_ai_interview(message, chat_history)
    return {
        'success': True,
        'response': fallback_text,
        'tokens_used': None
    }
