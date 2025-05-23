# DATA DICTIONARY: DeFi Protocol Contract Inventory

## Overview & Methodology

This data dictionary provides a curated inventory of Ethereum mainnet contract addresses and metadata for leading DeFi protocols. The inventory is designed to support on-chain data analysis, particularly for clustering addresses based on user behavior and protocol interaction.

**Construction Methodology:**

1.  **Aggregation:** Contract addresses and metadata were gathered from:
    *   Official protocol documentation
    *   Verified smart contract code on Etherscan
    *   Reputable sources like DeFiLlama and CoinGecko

2.  **Verification:** Each address was cross-checked against primary sources (official documentation, GitHub repositories) to ensure it is canonical and currently active on Ethereum mainnet.

3.  **Scope:** The inventory focuses on top DeFi protocols (TVL ≥ $250M) across key sectors:
    *   DEXs (Decentralized Exchanges)
    *   Lending Markets
    *   Stablecoins
    *   Liquid Staking Derivatives (LSDs)
    *   Bridges
    *   Derivatives Platforms

**Key Steps:**

*   **Protocol Selection:** Started with the top ~20 DeFi protocols by TVL (per DeFiLlama, May 2025), then extended to other major protocols ≥ $250M TVL. Examples include Aave, Lido, Uniswap, Maker/Spark, Curve, Compound, Rocket Pool, and Frax. NFT-specific platforms were excluded. Major cross-chain bridge contracts on Ethereum (e.g., Optimism, Arbitrum bridges) were included due to their high TVL.

*   **Address Collection:** For each protocol, the primary Ethereum mainnet contracts were identified:
    *   Core logic contracts (often proxied), such as Aave's Pool proxy, Compound's Comptroller, and Uniswap factories/routers.
    *   Token contracts for stablecoins and LSDs (e.g., DAI, USDC, stETH).
    *   Factory/registry contracts that spawn new pools or vaults (e.g., Uniswap/Curve factories, Lido's new V2 router).

*   **Proxy vs. Implementation:** Where proxies are used, the proxy address is listed as canonical (with `label_type: Proxy`), and the implementation address is noted if relevant (e.g., Curve's VotingEscrow proxy and implementation pair). All listed proxies have verified source code via Etherscan's proxy info.

*   **Verification:** Each address is verified as source-code verified on Etherscan (`etherscan_verified: Yes`). Etherscan and block explorers were used to fetch deployment blocks and confirm contract roles (via name tags or code). Official documentation was crucial for verification.

## Metadata Fields

The data dictionary includes the following metadata fields for each contract:

*   **`contract_role`:** Describes the contract's purpose within the protocol (e.g., "Pool (LendingPool proxy)" for Aave's main pool proxy, "UniswapV3 Factory").

*   **`label_type`:** Differentiates between proxies and regular contracts. "Proxy" indicates an upgradeable proxy; "Contract" indicates a direct implementation or non-proxy contract.

*   **`first_block`:** The Ethereum block height at which the contract was created. This helps confirm the contract's generation chronology.

*   **`abi_url`:** A reference to the ABI (Application Binary Interface) or source code. Often, the official documentation URL is used as the ABI reference, as Etherscan ABI JSON links are not static without an API.

*   **`notes`:** Captures any relevant nuances (e.g., "deprecated by V3," "example pool").

*   **`event_topic`:** (For Factories) The Keccak-256 hash of the event signature emitted when a child contract is spawned.

*   **`child_slot_index`:** (For Factories) The index of the event parameter containing the child contract's address.

## Factories & Events

Key factory contracts and the log event signatures they emit when spawning child contracts are included. The `event_topic` is determined by computing the Keccak-256 hash of the event signature. The `child_slot_index` is deduced from event definitions and validated by checking actual log data where possible.

## Function Selectors

Common function selectors for user-facing actions (swaps, deposits, borrows) in selected protocols are collated. The 4-byte directory and official ABIs are used to map function signatures to their 4-byte selectors. This aids in decoding transaction data for behavioral analysis. Focus is on high-level actions (e.g., Uniswap's `swapExactTokensForTokens`, Aave's `deposit`/`borrow`, Compound's `mint`/`redeem`, Curve's `exchange`) to capture typical DeFi interactions.

## Token Metadata

A list of major tokens relevant to these protocols is included, classifying them as stablecoins or LSDs. `decimals` are standardized to 18, except for USDC/USDT (6 decimals). CoinGecko IDs are provided for programmatic price and market cap lookups. `is_stable` is set to `true` for fiat-pegged assets, and `is_lsd` is set to `true` for staking derivatives. This classification supports clustering by distinguishing stablecoin usage from LSD usage in address activity.

## Data Provenance and Quality

Every contract address is sourced from:

*   Official project documentation or repository (e.g., Aave's address book, Uniswap docs, Lido dev docs).
*   Well-known blockchain data aggregators (DeFiLlama, CoinGecko) for secondary verification.

Unverified forum posts or user-generated lists are avoided unless cross-verified. The exact location in documentation or code commits confirming an address is cited where possible. All Etherscan verification statuses are "Yes," as unverified contracts are intentionally omitted.

## Changelog

*   **2025-05-22: Initial Release**
    *   Compiled ~40 contract addresses across 15+ protocols.
    *   Added factories for Uniswap, Curve, Lido, with event topics for pool creation.
    *   Included 13 function selectors for Uniswap, Aave, Compound, Curve core actions.
    *   Listed 10 major tokens (5 stablecoins, 5 LSDs) with classifications.
    *   Verified all entries with primary sources and provided detailed citations.

## Future Updates

This dataset will be updated for protocol upgrades, newly verified contracts, and TVL/top-ranking changes. Community feedback and corrections will be integrated. All changes will be logged with dates and descriptions to maintain transparency.