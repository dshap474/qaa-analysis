Of course. We have our "venues" (`master_contract_list.json`) and our "behaviors" (`action_dictionary.json`). Now it's time to put them together to interpret what's happening on the blockchain.

Here are the step-by-step instructions for **Step 3: Monitor and Decode On-Chain Activity**.

The goal of this step is to build a script that can take any transaction on Ethereum, check if it's relevant to our analysis, and if so, tell us exactly who did what. This is the core engine of your analysis system.

---

### **Prerequisites**

1.  **Your Files:** Make sure `master_contract_list.json` and `action_dictionary.json` are in the same directory as your new script.
2.  **Your Toolkit:** You'll need the same Python environment with the `web3.py` library installed.

---

### **Part A: Setting Up the Script and Loading Your Data**

First, we need to load the data from our JSON files into memory. For efficient lookups, we'll transform them into Python dictionaries where the keys are the addresses and selectors we want to search for.

#### **Step A.1: Create the Script and Load Data**

Create a new Python file (e.g., `decode_transactions.py`).

```python
import json
from web3 import Web3

# --- CONFIGURATION ---
RPC_URL = "https://mainnet.infura.io/v3/YOUR_API_KEY"
w3 = Web3(Web3.HTTPProvider(RPC_URL))

if not w3.is_connected():
    print("Error: Could not connect to the Ethereum node.")
    exit()

# --- LOAD DATA FROM STEPS 1 & 2 ---

# Load the master list of contracts (the "venues")
with open('master_contract_list.json', 'r') as f:
    master_contract_list = json.load(f)

# Load the dictionary of actions (the "behaviors")
with open('action_dictionary.json', 'r') as f:
    action_dictionary = json.load(f)

print("✅ Successfully loaded data from Steps 1 and 2.")
```

#### **Step A.2: Create Fast Lookup Dictionaries**

Searching through lists and nested dictionaries for every transaction is slow. We'll re-structure the data for instant lookups.

```python
# Create a dictionary for fast lookups: {contract_address: {"protocol": "...", "category": "..."}}
# This lets us instantly know if a contract is one we care about.
CONTRACT_LOOKUP = {
    w3.to_checksum_address(contract['contract_address']): {
        "protocol": contract['protocol'],
        "category": contract['category']
    } for contract in master_contract_list
}

# Create dictionaries for fast lookups of function and event selectors
# This lets us instantly map a selector back to its human-readable action.
FUNCTION_SELECTOR_LOOKUP = {}
EVENT_SELECTOR_LOOKUP = {}

for protocol, actions in action_dictionary.items():
    for action_name, details in actions.items():
        # Map function selector -> action details
        if 'function_selector' in details:
            FUNCTION_SELECTOR_LOOKUP[details['function_selector']] = {
                "protocol": protocol,
                "action": action_name,
                "signature": details.get('function_signature')
            }
        # Map event selector -> action details
        if 'event_selector' in details:
            EVENT_SELECTOR_LOOKUP[details['event_selector']] = {
                "protocol": protocol,
                "action": action_name,
                "signature": details.get('event_signature')
            }

print("✅ Created fast lookup dictionaries for contracts and selectors.")
```

---

### **Part B: The Core Decoding Logic**

Now we'll build the functions that process a block, filter its transactions, and decode the actions within them.

#### **Step B.1: The Main Processing Function**

This function will orchestrate the process: get a block, loop through its transactions, and pass each one to our decoding functions.

```python
def process_block(block_number):
    """Fetches a block and analyzes each transaction within it."""
    print(f"\n--- Processing Block: {block_number} ---")
    try:
        block = w3.eth.get_block(block_number, full_transactions=True)
    except Exception as e:
        print(f"Could not fetch block {block_number}: {e}")
        return

    for tx in block.transactions:
        # The 'to' address can be None for contract creation transactions
        if not tx['to']:
            continue

        # --- FILTERING (The Magic of Step 1) ---
        # Is this transaction interacting with a contract we know about?
        contract_address = w3.to_checksum_address(tx['to'])
        if contract_address in CONTRACT_LOOKUP:
            # It's a relevant transaction! Let's decode it.
            decode_transaction(tx, contract_address)

```

#### **Step B.2: The Transaction and Event Decoding Functions**

These functions use our lookup tables to find out what happened.

```python
def decode_transaction(tx, contract_address):
    """Decodes a single transaction to identify the user's action."""
    user_address = w3.to_checksum_address(tx['from'])
    tx_hash = tx['hash'].hex()
    
    # The function selector is the first 10 characters of the input data ('0x' + 8 hex chars)
    function_selector = tx['input'][:10]

    # --- DECODING INTENT (Using Function Selectors) ---
    if function_selector in FUNCTION_SELECTOR_LOOKUP:
        action_details = FUNCTION_SELECTOR_LOOKUP[function_selector]
        print(f"\n[INTENT] User {user_address} initiated '{action_details['action']}' on {action_details['protocol']}")
        print(f"  -> Tx Hash: {tx_hash}")
    
    # --- DECODING OUTCOME (Using Event Logs) ---
    # We need the transaction receipt to see the logs
    try:
        receipt = w3.eth.get_transaction_receipt(tx_hash)
    except Exception as e:
        print(f"    -> Could not get receipt for {tx_hash}: {e}")
        return

    if receipt.status == 0:
        print("    -> Transaction FAILED.")
        return

    for log in receipt.logs:
        # The event selector is the first topic (topic0)
        if not log['topics']:
            continue
            
        event_selector = log['topics'][0].hex()
        if event_selector in EVENT_SELECTOR_LOOKUP:
            event_details = EVENT_SELECTOR_LOOKUP[event_selector]
            print(f"  [OUTCOME] Emitted '{event_details['action']}' event from {event_details['protocol']}")

```

---

### **Part C: Running the Engine**

Finally, let's put it all together and run our analysis on the latest block.

#### **Step C.1: The Main Execution Block**

Add this to the end of your `decode_transactions.py` script.

```python
# --- RUN THE ENGINE ---
if __name__ == "__main__":
    try:
        # Get the latest block number
        latest_block = w3.eth.block_number
        process_block(latest_block)
    except Exception as e:
        print(f"An error occurred: {e}")

```

### **Summary of Step 3**

When you run this script (`python decode_transactions.py`), you will see a live feed of decoded DeFi activity from the latest block.

**Example Output:**

```
✅ Successfully loaded data from Steps 1 and 2.
✅ Created fast lookup dictionaries for contracts and selectors.

--- Processing Block: 19980560 ---

[INTENT] User 0x1234... initiated 'swap' on Uniswap V2
  -> Tx Hash: 0xabcd...
  [OUTCOME] Emitted 'swap' event from Uniswap V2

[INTENT] User 0x5678... initiated 'supply' on Aave V3
  -> Tx Hash: 0xefgh...
  [OUTCOME] Emitted 'supply' event from Aave V3
```

You have now successfully built a powerful engine that:

1.  **Filters** the noise of the blockchain to focus only on contracts you care about.
2.  **Decodes** both the user's *intent* (the function they called) and the *outcome* (the events that were emitted).
3.  **Translates** complex hexadecimal data into human-readable actions.

The output of this script is the raw, structured data you need for the final step. You now have a stream of `(user_address, action_type, protocol)` tuples, which is the perfect input for **Step 4: Apply Rules to Assign Categories**.