from flask import Flask, render_template, request, jsonify, Response
import requests
import time
import os
import json
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()
API_KEY = os.getenv('XDC_API_KEY')
if not API_KEY:
    raise RuntimeError("XDC_API_KEY not set. Copy .env.example -> .env and set XDC_API_KEY=your_key")

BASE_URL = "https://api.etherscan.io/v2/api"
CHAIN_ID = "50"

OFFICIAL_CONTACTS = {
    "VVFIT": "0x23Db6050336B16Fc7d7030956b03214537E55f2e",
    "USDT": "0xd4b5f10d61916bd6e0860144a91ac658de8a1437",
}

def get_token_decimals(contract_addr):
    """Fetches decimal places for a given token contract address."""
    params = {
        "chainid": CHAIN_ID,
        "module": "token",
        "action": "tokeninfo",
        "contractaddress": contract_addr,
        "apikey": API_KEY
    }
    try:
        res = requests.get(BASE_URL, params=params, timeout=5).json()
        if res.get("status") == "1" and res.get("result"):
            return int(res["result"][0].get("divisor", 18))
    except Exception as e:
        print(f"Error fetching decimals: {e}")
    return 18

@app.route('/')
def index():
    """Renders the main dashboard page."""
    return render_template('index.html')

@app.route('/run-scan', methods=['GET', 'POST'])
def run_scan():
    """
    Handles wallet balance scanning with Server-Sent Events (SSE).
    Supports both XDC-only and XDC + Token balance checking.
    """
    if request.method == 'GET':
        user_input = request.args.get('token', '').strip().upper()
        addresses_input = request.args.get('addresses', '')
    else:
        data = request.json or {}
        user_input = data.get('token', '').strip().upper()
        addresses_input = data.get('addresses', '')
    
    def generate():
        try:
            if not user_input:
                yield f"data: {json.dumps({'error': 'Please enter a token name or contract address'})}\n\n"
                return
            
            if not addresses_input:
                yield f"data: {json.dumps({'error': 'Please provide wallet addresses'})}\n\n"
                return
            
            raw_addresses = [line.strip() for line in addresses_input.split('\n') if line.strip()]
            
            if not raw_addresses:
                yield f"data: {json.dumps({'error': 'No valid addresses found'})}\n\n"
                return
            
            clean_addresses = [a.replace('xdc', '0x').lower() for a in raw_addresses]
            token_contract = OFFICIAL_CONTACTS.get(user_input, user_input).lower()
            
            decimals = 18
            if token_contract and token_contract != '0x':
                decimals = get_token_decimals(token_contract)
            
            total_xdc = 0.0
            total_tokens = 0.0
            count = 0
            
            if not token_contract or token_contract == '0x':
                for i in range(0, len(clean_addresses), 20):
                    batch = clean_addresses[i:i+20]
                    params = {
                        "chainid": CHAIN_ID,
                        "module": "account",
                        "action": "balancemulti",
                        "address": ",".join(batch),
                        "tag": "latest",
                        "apikey": API_KEY
                    }
                    try:
                        response = requests.get(BASE_URL, params=params, timeout=10).json()
                        if response.get("status") == "1":
                            for item in response["result"]:
                                xdc_balance = int(item['balance']) / 10**18
                                total_xdc += xdc_balance
                                count += 1
                                yield f"data: {json.dumps({'index': count, 'address': item['account'], 'xdc_balance': round(xdc_balance, 4), 'token_balance': 0, 'token_name': 'XDC', 'progress': f'{count}/{len(clean_addresses)}'})}\n\n"
                        time.sleep(0.3)
                    except Exception as e:
                        print(f"Error in batch: {e}")
            else:
                for idx, addr in enumerate(clean_addresses, 1):
                    xdc_params = {
                        "chainid": CHAIN_ID,
                        "module": "account",
                        "action": "balance",
                        "address": addr,
                        "tag": "latest",
                        "apikey": API_KEY
                    }
                    token_params = {
                        "chainid": CHAIN_ID,
                        "module": "account",
                        "action": "tokenbalance",
                        "contractaddress": token_contract,
                        "address": addr,
                        "tag": "latest",
                        "apikey": API_KEY
                    }
                    
                    try:
                        xdc_res = requests.get(BASE_URL, params=xdc_params, timeout=5).json()
                        token_res = requests.get(BASE_URL, params=token_params, timeout=5).json()
                        
                        xdc_balance = int(xdc_res['result']) / 10**18 if xdc_res.get('status') == '1' else 0
                        token_balance = int(token_res['result']) / 10**decimals if token_res.get('status') == '1' else 0
                        
                        referrals = 0
                        if user_input == 'VVFIT' and token_balance > 750:
                            referrals = int((token_balance - 750) / 300)
                        
                        total_xdc += xdc_balance
                        total_tokens += token_balance
                        count += 1
                        
                        yield f"data: {json.dumps({'index': idx, 'address': addr, 'xdc_balance': round(xdc_balance, 4), 'token_balance': round(token_balance, 4), 'token_name': user_input, 'referrals': referrals, 'progress': f'{count}/{len(clean_addresses)}'})}\n\n"
                        time.sleep(0.2)
                    except Exception as e:
                        print(f"Error checking {addr}: {e}")
            
            yield f"data: {json.dumps({'done': True, 'totals': {'xdc': round(total_xdc, 4), 'tokens': round(total_tokens, 4)}, 'total_addresses': count})}\n\n"
        
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)