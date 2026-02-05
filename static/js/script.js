const addressesInput = document.getElementById('addresses');
const customTokenInput = document.getElementById('customToken');
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const clearBtn = document.getElementById('clearBtn');
const resultsContainer = document.getElementById('resultsContainer');
const progressText = document.getElementById('progressText');
const totalXDCEl = document.getElementById('totalXDC');
const totalTokensEl = document.getElementById('totalTokens');
const totalReferralsEl = document.getElementById('totalReferrals');

let eventSource = null;
let selectedToken = null;
let isScanning = false;
let runningTotalXDC = 0.0;
let runningTotalTokens = 0.0;
let runningTotalReferrals = 0;

document.querySelectorAll('.token-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        document.querySelectorAll('.token-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        selectedToken = this.dataset.token;
        customTokenInput.value = '';
    });
});

customTokenInput.addEventListener('input', function() {
    if (this.value.trim()) {
        document.querySelectorAll('.token-btn').forEach(b => b.classList.remove('active'));
        selectedToken = this.value.trim();
    }
});

startBtn.addEventListener('click', startScan);
stopBtn.addEventListener('click', stopScan);
clearBtn.addEventListener('click', clearResults);

function startScan() {
    const addresses = addressesInput.value.trim();
    
    if (!addresses) {
        showError('Please enter at least one wallet address');
        return;
    }

    if (!selectedToken && !customTokenInput.value) {
        showError('Please select or enter a token');
        return;
    }

    const token = selectedToken || customTokenInput.value.trim();
    
    isScanning = true;
    startBtn.disabled = true;
    stopBtn.disabled = false;
    clearResults();

    eventSource = new EventSource(`/run-scan?token=${encodeURIComponent(token)}&addresses=${encodeURIComponent(addresses)}`);

    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);

        if (data.error) {
            showError(data.error);
            stopScan();
            return;
        }

        if (data.done) {
            progressText.textContent = `Completed: ${data.total_addresses} wallets scanned`;
            stopScan();
            return;
        }

        displayResult(data);
        progressText.textContent = data.progress;
    };

    eventSource.onerror = function() {
        showError('Connection lost');
        stopScan();
    };
}

function stopScan() {
    isScanning = false;
    if (eventSource) {
        eventSource.close();
    }
    startBtn.disabled = false;
    stopBtn.disabled = true;
}

function displayResult(data) {
    const resultItem = document.createElement('div');
    resultItem.className = 'result-item';

    runningTotalXDC += data.xdc_balance;
    runningTotalTokens += data.token_balance;

    let balanceHTML = `
        <div class="balance">
            <span class="balance-label">XDC:</span>
            <span class="balance-value">${data.xdc_balance.toFixed(4)}</span>
        </div>
    `;

    if (data.token_balance > 0 || data.token_name !== 'XDC') {
        balanceHTML += `
            <div class="balance">
                <span class="balance-label">${data.token_name}:</span>
                <span class="balance-value">${data.token_balance.toFixed(4)}</span>
            </div>
        `;
    }

    let referralsHTML = '';
    if (data.referrals > 0) {
        referralsHTML = `<div class="referrals">Referrals: <span class="referrals-count">${data.referrals}</span></div>`;
        runningTotalReferrals += data.referrals;
    }

    resultItem.innerHTML = `
        <div class="result-header">
            <span class="result-index">#${data.index}</span>
        </div>
        <div class="result-address">${data.address}</div>
        <div class="result-balances">
            ${balanceHTML}
        </div>
        ${referralsHTML}
    `;

    resultsContainer.appendChild(resultItem);
    resultsContainer.scrollTop = resultsContainer.scrollHeight;

    if (resultsContainer.querySelector('.placeholder')) {
        resultsContainer.innerHTML = '';
        resultsContainer.appendChild(resultItem);
    }

    updateTotalsDisplay();
}

function showError(message) {
    const errorItem = document.createElement('div');
    errorItem.className = 'result-item error';
    errorItem.innerHTML = `<strong>Error:</strong> ${message}`;
    resultsContainer.appendChild(errorItem);
}

function clearResults() {
    resultsContainer.innerHTML = '<p class="placeholder">Results will appear here...</p>';
    progressText.textContent = '';
    runningTotalXDC = 0.0;
    runningTotalTokens = 0.0;
    runningTotalReferrals = 0;
    updateTotalsDisplay();
}

function updateTotalsDisplay() {
    totalXDCEl.textContent = runningTotalXDC.toFixed(4);
    totalTokensEl.textContent = runningTotalTokens.toFixed(4);
    totalReferralsEl.textContent = runningTotalReferrals;
}
