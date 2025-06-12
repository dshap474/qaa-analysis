*   **Step 1: Build a Master List of Contracts (The "Venues")**
    *   Use factory registries to automatically discover all DEX pools and markets.
    *   Manually add the main application contracts (e.g., Aave Pool, Uniswap Router, Lido Staking).

*   **Step 2: Create a Dictionary of Actions (The "Behaviors")**
    *   Map key user actions like "swap," "add liquidity," "borrow," and "supply" to their specific function and event selectors.

*   **Step 3: Monitor and Decode On-Chain Activity**
    *   Track all transactions that interact with your master list of contracts.
    *   For each transaction, use your dictionary to identify the specific action performed by the user.

*   **Step 4: Apply Rules to Assign Categories**
    *   Define simple rules (heuristics) to classify addresses based on their activity patterns.
    *   **Example:** An address frequently performing `swap` actions is a **"Trader."** An address performing `addLiquidity` actions is a **"Liquidity Provider."** An address performing `borrow` actions is a **"Borrower."**