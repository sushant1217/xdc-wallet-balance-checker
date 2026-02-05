# Wallet Balance Checker - XDC Network Dashboard

A real-time wallet balance scanner for XDC Network. Check multiple wallet addresses simultaneously and retrieve live balance updates for XDC, VVFIT, USDT, or any custom ERC-20 token.

## Features

- **Real-time Streaming Results** - Live updates as each wallet is scanned via Server-Sent Events (SSE)
- **Multi-Token Support** - Preset buttons for XDC, VVFIT, and USDT; custom token contract address input
- **Batch Wallet Scanning** - Efficiently check 100+ wallet addresses in a single operation
- **Referral Calculator** - Automatic referral calculation for VVFIT (formula: `(Balance - 750) / 300`)
- **Auto-scroll Results Panel** - Latest entries automatically scroll into view
- **Aggregate Totals** - View cumulative XDC balance, token balance, and referral counts
- **Address Tracking** - Sequential numbering for easy address identification

## Tech Stack

- **Backend**: Python Flask with SSE for real-time updates
- **Frontend**: Vanilla JavaScript with HTML5 & CSS3
- **API**: XDC Network (via Apicoin/Etherscan-compatible API)
- **Smart Contracts**: ERC-20 token standard

## Prerequisites

- Python 3.7+
- pip (Python package manager)
- Modern web browser (Chrome, Firefox, Safari, Edge)
- XDC Network API Key

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/sushant1217/xdc-wallet-balance-checker.git
cd "Wallet Dashboard"
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Key

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Then edit `.env` and add your XDC Network API key:

```
XDC_API_KEY=your_actual_api_key_here
```

### 4. Run the Application

```bash
python app.py
```

The dashboard will be available at `http://127.0.0.1:5000/`

## Usage

1. Enter wallet addresses (XDC format: `xdc...` or Ethereum format: `0x...`) - one per line
2. Select a token: Use preset buttons (XDC, VVFIT, USDT) or enter a custom contract address
3. Click "Start" to begin scanning
4. Monitor real-time balance updates in the results panel
5. Click "Stop" to halt the scan at any time

## Project Structure

```
Wallet Dashboard/
│
├── app.py                # Main application file
├── requirements.txt       # Python dependencies
├── static/                # Static files (CSS, JavaScript, images)
│   ├── css/
│   ├── js/
│   └── img/
└── templates/             # HTML templates
    ├── layout.html
    ├── index.html
    └── results.html
```

## Troubleshooting

- If you encounter any issues, ensure that you have installed all the prerequisites and dependencies.

## Acknowledgments

- Inspired by the need for transparent and accessible crypto wallet management tools.
- Thanks to the open-source community for their invaluable contributions.

## Contact

i.g - sushant.1217

---