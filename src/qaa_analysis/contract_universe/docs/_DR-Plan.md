A Comprehensive Technical Plan for Automated Discovery of Ethereum Application Markets and User Action Mapping for Behavioral AnalysisI. IntroductionPurpose and ScopeThis report outlines a comprehensive, step-by-step technical plan for automatically discovering Decentralized Exchange (DEX) pools, lending markets, and NFT marketplace contracts on the Ethereum blockchain. The core methodology relies on identifying and interacting with "factory" or registry-like smart contracts of top Ethereum applications. The ultimate objective is to enable the mapping of key user on-chain actions (e.g., swaps, liquidity provision, borrowing, lending, staking, NFT purchases/sales) to these discovered entities. This foundational data layer is essential for conducting in-depth behavioral analysis of Ethereum addresses. The scope of this plan is primarily the Ethereum mainnet, focusing on prominent Decentralized Finance (DeFi) protocols—including DEXs, lending platforms, and liquid staking solutions—and major NFT marketplaces.Significance for Behavioral AnalysisUnderstanding user interactions within the complex and multifaceted Ethereum ecosystem requires precise identification of the smart contracts with which users engage. Automating the discovery of these interaction points, such as liquidity pools and lending markets, is crucial for scalable and accurate analysis. By mapping specific actions to these identified pools and markets, analysts can uncover a wealth of patterns. These may include preferred trading venues, characteristic liquidity provision strategies, borrowing habits, preferences for particular NFT collections, and overall engagement levels of addresses within the DeFi and NFT sectors. Such a granular view of on-chain economic activity provides invaluable data for behavioral studies, risk assessment, and market trend identification.Overview of the ApproachThe strategy detailed herein involves a multi-stage process:
Identifying Top Ethereum Applications and Their Core Infrastructure: This involves selecting leading applications based on objective metrics and locating their central factory or registry contracts.
Automated Discovery of Pools and Markets: This step leverages factory contract events (e.g., PairCreated, PoolCreated) and/or read functions callable on the factory contracts to discover the addresses of individual pool or market contracts.
Mapping Key User Actions: This requires identifying key user action function signatures (e.g., swapExactTokensForTokens, supply, fulfillBasicOrder) and their corresponding event signatures (e.g., Swap, Supply, OrderFulfilled) that signify these actions.
Data Extraction and Association: The final phase involves extracting relevant data from transaction inputs and event logs to link user addresses to specific actions performed on the discovered pools and markets. This data forms the basis for subsequent behavioral analysis.
II. Identifying Target Ethereum Applications and Their Factory InfrastructureA. Selecting Top Ethereum Applications (DeFi & NFT)The selection of "top" Ethereum applications is foundational to ensure that the subsequent analysis is focused on platforms with significant user activity and data richness. This selection is guided by established metrics within the DeFi and NFT sectors.Methodology:For DeFi protocols, Total Value Locked (TVL) serves as a primary metric. TVL quantifies the dollar value of digital assets secured within a DeFi protocol's smart contracts. A higher TVL generally indicates greater user trust, engagement, and a larger volume of assets, which often translates to a higher number of transactions and interactions. This makes high-TVL protocols rich sources for behavioral analysis. Data sources such as DefiLlama 1 and DappRadar  provide reliable TVL rankings. Based on these sources, prominent DeFi protocols include Decentralized Exchanges (DEXs) like Uniswap and Curve, lending protocols such as Aave and Compound, and liquid staking solutions like Lido and Rocket Pool.1For NFT marketplaces, metrics such as trading volume and the number of unique traders are more indicative of user activity. DappRadar 4 is a valuable resource for this data. Leading NFT marketplaces on Ethereum include OpenSea and Blur, which command significant market share and transaction volume.4The rationale for using TVL as a primary selection criterion for DeFi protocols is that it reflects user participation and the liquidity depth underpinning on-chain operations. Protocols with substantial TVL have demonstrated an ability to attract and retain capital, suggesting a robust user base and a significant number of on-chain interactions suitable for behavioral analysis.Table 1: Illustrative List of Top Ethereum Applications for Analysis
Protocol NameCategoryKey Metric (Example Source)Link to Example Data SourceAaveLendingTVL: $24.4 billionhttps://tangem.com/en/blog/post/total-value-locked-tvl/LidoLiquid StakingTVL: $22.6 billionhttps://tangem.com/en/blog/post/total-value-locked-tvl/UniswapDEXTVL: $3.817 billionhttps://tangem.com/en/blog/post/total-value-locked-tvl/Curve FinanceDEXTVL: $1.48B (Curve +1)https://dappradar.com/rankings/defi/chain/ethereumCompoundLendingTVL: $2.07Bhttps://dappradar.com/rankings/defi/chain/ethereumRocket PoolLiquid StakingTVL: $3.67Bhttps://dappradar.com/rankings/defi/chain/ethereumOpenSeaNFT MarketplaceVolume (30d): $153.88M 4https://smithii.io/en/ethereum-nft-marketplace/BlurNFT MarketplaceVolume (30d): $453.55M 4https://smithii.io/en/ethereum-nft-marketplace/
Note: TVL and volume figures are dynamic and should be checked from sources like DefiLlama and DappRadar for the most current data at the time of implementation. The table provides a snapshot based on available research material.This curated list provides a solid starting point for the discovery process, focusing efforts on applications with the highest potential yield of behavioral data. Users of this plan can expand this list based on their specific analytical interests.B. The Role of Factory Contracts in Decentralized ProtocolsFactory contracts are a common design pattern in decentralized protocols, particularly in DEXs. These are smart contracts specifically designed to deploy other smart contracts, typically instances of a standard pool or market template.8 For example, the Uniswap V2 Factory contract is responsible for creating new instances of Uniswap V2 exchange contracts for different ERC20 token pairs.9 Similarly, the Uniswap V3 Factory deploys Uniswap V3 pools and acts as a centralized registry for them.8 Curve Finance also utilizes factory contracts, such as the CryptoSwap Factory, for the permissionless deployment of two-coin volatile asset pools.11These factory contracts often maintain a record or registry of the contracts they have deployed. This registry feature is key to discovering all associated pools or markets. For instance, the Uniswap V2 Factory maps token pairs to their corresponding exchange addresses, allowing for easy discovery and interaction.9It is important to recognize that while the term "factory" is explicit in protocols like Uniswap, other major applications achieve similar market registration and central interaction point functionalities through different architectural designs. For lending protocols like Aave, a single main contract, such as Aave's Pool contract 12, manages all lending markets for various assets. Users interact with this central Pool contract to supply, borrow, or withdraw assets. Similarly, for NFT marketplaces like OpenSea, the Seaport protocol contract 13 acts as the core marketplace engine where orders are created and fulfilled. While these central contracts may not "deploy" new, distinct market contracts for every asset or pair in the same way a Uniswap factory does, they serve an analogous role as the primary point for logging key interactions and can be considered "registries" of market activity. Therefore, to achieve the goal of discovering "all dex pools and markets," the approach must be flexible enough to encompass these variations in protocol architecture, identifying the central contracts that log or enable discovery of distinct market interactions.C. Locating Factory (or Equivalent Central Registry) Contract AddressesIdentifying the correct factory or central registry contract addresses is a critical first step. Several strategies can be employed:
Official Protocol Documentation: This is generally the most reliable source. Protocol developers usually provide lists of their deployed mainnet contract addresses. For example, Uniswap's documentation explicitly lists its V2 and V3 factory addresses.15 Aave's documentation provides addresses for its core contracts, including the V3 Pool.12 Curve's documentation also details its factory contract addresses.11
Blockchain Explorers (e.g., Etherscan): Verified smart contracts on Etherscan often have public name tags, labels (e.g., "Uniswap V2: Factory"), and links to the project's official website or documentation.18 Examining the transaction history of known protocol components, such as router contracts, can also lead to the identification of associated factory contracts, as routers frequently interact with factories to get pool information.
Third-Party Analytics Platforms: Platforms like DefiLlama  and DappRadar 3 aggregate data about DeFi protocols and dApps. They often list key contract addresses or provide links to Etherscan pages where these addresses can be found.
Project GitHub Repositories: Developers may include deployment addresses in configuration files, deployment scripts, or README files within their public GitHub repositories.20
Verification: It is crucial to cross-reference addresses obtained from multiple sources whenever possible. Always verify that the contract on Etherscan is indeed verified, has relevant tags, and, if possible, matches the address provided in official documentation. This diligence minimizes the risk of interacting with incorrect or malicious contracts.Table 2: Key Factory/Registry Contract Addresses for Selected Top Protocols (Ethereum Mainnet)Protocol NameContract Type (Role)Mainnet AddressLink to Etherscan ExampleLink to Official Documentation (Example)Uniswap V2Factory0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f1515Uniswap V3Factory0x1F98431c8aD98523631AE4a59f267346ea31F9841616Curve FinanceCryptoSwap Factory0xf18056bbd320e96a48e3fbf8bc061322531aac992211Aave V3Pool (Central Lending Market Registry)0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e22312OpenSeaSeaport Protocol (Marketplace Core)0x0000000000000068F116a894984e2DB1123eB3951313LidostETH Token (Staking Entry & Registry of stETH)0xae7ab96520DE3A18E5e111B5EaAb095312D7fE842425Compound V2Comptroller (Market Risk & Listing Registry)0x3d9819210A31b4961b30EF54bE2aeD79B9c9Cd3B2627Rocket PoolDeposit Pool0xDD3f50F8A6CafbE9b31a427582963f465E745AF82828BlurMarketplace Contract (Example: Blur.io: Marketplace 3)0x867cDd985c84cb8c9079397b1e04b89d95c1910329(Refer to Blur's official developer resources for definitive marketplace contract addresses)This table serves as a quick reference to the critical contract addresses. These addresses are the starting points for programmatic interaction and data extraction in the subsequent steps of this plan.III. Step-by-Step: Automated Discovery of Pools and Markets via Factory/Registry ContractsOnce the primary factory or registry contracts for the target applications are identified, the next phase is to discover the individual DEX pools or market instances they manage or have deployed. This can be achieved primarily by monitoring event logs, and complementarily by calling read functions on the factory contracts.A. Discovering Pools/Markets via Factory Event LogsThis method is highly effective for discovering newly created pools or markets in real-time and can also be used for historical discovery by querying past logs. The process involves identifying specific event signatures, calculating their Topic0 hashes, querying an Ethereum node for logs matching these criteria, and then decoding the event data.1. Identifying Pool/Market Creation Event Signatures:Factory contracts that deploy new pool/market instances typically emit an event upon each successful creation. The signature of this event (its name and the types of its parameters) is crucial for filtering and decoding.
Uniswap V2: The V2 factory emits a PairCreated event.

Signature: PairCreated(address indexed token0, address indexed token1, address pair, uint).15
This event provides the addresses of the two tokens forming the pair (token0, token1) and the address of the newly created pair contract (pair). The uint parameter indicates the index of this pair in the factory's list of all pairs.


Uniswap V3: The V3 factory emits a PoolCreated event.

Signature 30: PoolCreated(address indexed token0, address indexed token1, uint24 indexed fee, int24 tickSpacing, address pool).30 Note that 39 presents a slightly different signature from the Solidity code (PoolCreated(address tokenA, address tokenB, uint24 fee, address pool)), where tickSpacing is derived from the fee. For log filtering, the signature that matches the Topic0 hash used by indexers is key.
This event provides the token addresses, the fee tier for the pool, the tick spacing (which governs price granularity), and the address of the new pool contract.


Curve Finance (CryptoSwap Factory): The CryptoSwap factory emits a CryptoPoolDeployed event.

Signature (from Etherscan ABI for 0xf18056bbd320e96a48e3fbf8bc061322531aac99): CryptoPoolDeployed(address token, address coins, uint256 A, uint256 gamma, uint256 mid_fee, uint256 out_fee, uint256 allowed_extra_profit, uint256 fee_gamma, uint256 adjustment_step, uint256 admin_fee, uint256 ma_half_time, uint256 initial_price, address deployer).22
This event provides the address of the LP token (token), the addresses of the two underlying coins (coins), and various pool-specific parameters like the amplification coefficient (A) and fees.


Other Protocols: For protocols that do not follow this exact "factory deploys new contract instance" pattern (e.g., Aave, where markets are configured within a central Pool contract), this step involves identifying events related to market listing, activation, or significant configuration changes. For NFT marketplaces like OpenSea (using Seaport), the "market" is often the main marketplace contract itself, and individual "pools" can be thought of as listings or orders. Events like OrderFulfilled signal activity within these markets rather than the creation of new, distinct market contracts.32
2. Calculating Event Topic0 Hashes (Keccak-256):The Event Topic0 is the Keccak-256 hash of the canonical event signature string (e.g., "PairCreated(address,address,address,uint256)"). This hash is the primary filter used when querying Ethereum logs.
Uniswap V2 PairCreated(address,address,address,uint256):

Topic0: 0x0d3648bd0f6ba80134a33ba9275ac585d9d315f0ad8355cddefde31afa28d0e9.30


Uniswap V3 PoolCreated(address,address,uint24,int24,address):

Topic0: 0x783cca1c0412dd0d695e784568c96da2e9c22ff989357a2e8b1d9b2b4e6b7118.30


Curve CryptoSwap Factory CryptoPoolDeployed(address,address,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,uint256,address):

Topic0: 0x062384933E4AA575767D87DAd5f6F3529C070D3A4579C8D9AA80916852577E09 (calculated using address for address).
Online Keccak-256 calculators 33 or cryptographic libraries within programming languages (e.g., ethers.id() in ethers.js, Web3.keccak() in web3.py) can be used for this calculation. The input string must be the precise canonical event signature, without parameter names or the indexed keyword.


3. Querying Ethereum Node for Logs:An Ethereum node's JSON-RPC API, specifically the eth_getLogs method, is used to fetch event logs.
Parameters for eth_getLogs:

address: The address of the factory contract emitting the events.
topics: An array where the first element (topics) is the Topic0 hash of the creation event. Subsequent elements can be used to filter by indexed event parameters (e.g., specific token addresses).
fromBlock, toBlock: Define the block range for the query. For historical discovery, this can span from the factory's deployment block to the current block. For ongoing monitoring, toBlock can be set to "latest".


Node Requirements: Access to an Ethereum archive node is necessary for querying the full history of events, especially for protocols that have been active for a long time.35 Full nodes typically prune historical states beyond a certain window, making them unsuitable for complete historical backfills.
4. Decoding Event Data:The eth_getLogs method returns an array of log objects. Each log object contains:
address: The address of the contract that emitted the event (the factory).
topics: An array of up to four 32-byte topic hashes. topics is the event signature hash. topics through topics are the values of indexed event parameters.
data: A hex string containing the ABI-encoded values of the non-indexed event parameters.
To decode this data, the ABI (Application Binary Interface) of the factory contract is required. Libraries like ethers.js (using Interface.parseLog()) or web3.py provide utilities to parse these log objects into human-readable event data, extracting the values of all parameters. From this decoded data, the address of the newly created pool/market, the constituent tokens/assets, and other relevant metadata can be obtained.It is important to note that discrepancies can exist between documented event signatures and the actual signatures defined in a contract's ABI on-chain.30 The contract's verified ABI, as found on Etherscan 22 or obtained from official project artifacts 21, should always be considered the definitive source for constructing Topic0 hashes and for decoding event data. This ensures accuracy in identifying and interpreting the discovered pools and markets.Specific Example (Uniswap V2 PairCreated):
Factory Address: 0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f.15
Event Signature: PairCreated(address indexed token0, address indexed token1, address pair, uint).15
Topic0: 0x0d3648bd0f6ba80134a33ba9275ac585d9d315f0ad8355cddefde31afa28d0e9.30
Data Extraction from Log:

token0: log.topics (decode as address).
token1: log.topics (decode as address).
pair and uint (pair index): Decoded from log.data using the factory ABI. pair is the first non-indexed argument, uint is the second.


Illustrative Code Snippet (ethers.js conceptual):
JavaScript// const factoryAddress = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f";
// const pairCreatedTopic = "0x0d3648bd0f6ba80134a33ba9275ac585d9d315f0ad8355cddefde31afa28d0e9";
// const factoryABI =; 
// const provider = new ethers.JsonRpcProvider(YOUR_ETHEREUM_NODE_URL);
// const factoryInterface = new ethers.Interface(factoryABI);
//
// async function discoverV2Pairs(fromBlock, toBlock) {
//   const logs = await provider.getLogs({
//     address: factoryAddress,
//     fromBlock: fromBlock,
//     toBlock: toBlock,
//     topics:
//   });
//   logs.forEach(log => {
//     try {
//       const parsedLog = factoryInterface.parseLog({ topics: log.topics, data: log.data });
//       if (parsedLog && parsedLog.name === "PairCreated") {
//         console.log("Uniswap V2 Pair Discovered:");
//         console.log("  Token0 (from topic):", ethers.getAddress('0x' + log.topics.slice(26)));
//         console.log("  Token1 (from topic):", ethers.getAddress('0x' + log.topics.slice(26)));
//         console.log("  Pair Address (from data):", parsedLog.args.pair);
//         console.log("  AllPairs Index (from data):", parsedLog.args.toString()); // Accessing the unnamed uint
//       }
//     } catch (e) {
//       console.error("Error parsing log:", e, log);
//     }
//   });
// }
// discoverV2Pairs(0, 'latest'); // Example: Discover all pairs


Specific Example (Uniswap V3 PoolCreated):
Factory Address: 0x1F98431c8aD98523631AE4a59f267346ea31F984.16
Event Signature 30: PoolCreated(address indexed token0, address indexed token1, uint24 indexed fee, int24 tickSpacing, address pool).
Topic0: 0x783cca1c0412dd0d695e784568c96da2e9c22ff989357a2e8b1d9b2b4e6b7118.30
Data Extraction from Log:

token0: log.topics (decode as address).
token1: log.topics (decode as address).
fee: log.topics (decode as uint24).
tickSpacing and pool: Decoded from log.data using the factory ABI.


Illustrative Code Snippet (ethers.js conceptual):
JavaScript// const factoryV3Address = "0x1F98431c8aD98523631AE4a59f267346ea31F984";
// const poolCreatedTopicV3 = "0x783cca1c0412dd0d695e784568c96da2e9c22ff989357a2e8b1d9b2b4e6b7118";
// const factoryV3ABI =;
// const provider = new ethers.JsonRpcProvider(YOUR_ETHEREUM_NODE_URL);
// const factoryV3Interface = new ethers.Interface(factoryV3ABI);
//
// async function discoverV3Pools(fromBlock, toBlock) {
//   const logs = await provider.getLogs({
//     address: factoryV3Address,
//     fromBlock: fromBlock,
//     toBlock: toBlock,
//     topics:
//   });
//   logs.forEach(log => {
//     try {
//       const parsedLog = factoryV3Interface.parseLog({ topics: log.topics, data: log.data });
//       if (parsedLog && parsedLog.name === "PoolCreated") {
//         console.log("Uniswap V3 Pool Discovered:");
//         console.log("  Token0 (from topic):", ethers.getAddress('0x' + log.topics.slice(26)));
//         console.log("  Token1 (from topic):", ethers.getAddress('0x' + log.topics.slice(26)));
//         console.log("  Fee (from topic):", parseInt(log.topics, 16)); // uint24
//         console.log("  TickSpacing (from data):", parsedLog.args.tickSpacing.toString());
//         console.log("  Pool Address (from data):", parsedLog.args.pool);
//       }
//     } catch (e) {
//       console.error("Error parsing log:", e, log);
//     }
//   });
// }
// discoverV3Pools(0, 'latest'); // Example: Discover all V3 pools


B. Discovering Pools/Markets via Factory Read Functions (Alternative/Complementary)Some factory contracts provide read-only functions that allow for the enumeration or direct lookup of deployed pool/market addresses. This method can be an alternative or a complement to event log scanning, particularly for historical data retrieval.

Uniswap V2:

getPair(address tokenA, address tokenB) external view returns (address pair); Returns the address of the pair for tokenA and tokenB if it has been created, otherwise returns the zero address.15 This is useful for checking if a specific pair exists.
allPairs(uint index) external view returns (address pair); Returns the address of the nth pair (0-indexed) created through the factory.15
allPairsLength() external view returns (uint); Returns the total number of pairs created by the factory.15
Usage for Discovery: One can call allPairsLength() to get the total count and then iterate from index 0 up to count - 1, calling allPairs(index) in each iteration to retrieve all deployed pair addresses. This is highly effective for a complete historical backfill of all Uniswap V2 pairs.



Uniswap V3:

getPool(address tokenA, address tokenB, uint24 fee) external view returns (address pool); Creates (if not already created by an external call to createPool) and returns the pool address for a given token pair and fee tier.17
Usage for Discovery: This function is more suited for looking up a specific pool if the tokens and fee tier are known. It's less straightforward for discovering all pools without prior knowledge of existing pairs and active fee tiers. However, one could iterate through known tokens and common fee tiers (e.g., 100, 500, 3000, 10000 bps) to discover pools.



Curve Finance:

Curve factory contracts often act as registries.20 The specific functions to list all deployed pools vary depending on the factory type (e.g., Stableswap, CryptoSwap, StableswapNG). For example, some Curve factory ABIs include functions like pool_list(uint256 index) and pool_count() (e.g., the Curve StableSwap Factory NG at 0x6A8cbed756804B16E05E741eDaBd5cB544AE21bf 40 likely has such functions based on common Curve factory patterns). The exact functions must be identified from the specific factory's ABI.


Considerations for Using Read Functions:
Scalability and RPC Load: Iterating through a large number of indices or potential token pair combinations via read functions can result in a high volume of RPC calls to the Ethereum node. This can be slow and may lead to rate-limiting by RPC providers.
Completeness: While iteration can be complete for factories like Uniswap V2's allPairs, for others like Uniswap V3's getPool, it relies on knowing the input parameters (token pairs, fees), which might not be exhaustive.
Efficiency for Historical Data: For a one-time historical sync, especially for protocols like Uniswap V2, iterating via read functions can be more straightforward than processing potentially millions of event logs, provided the number of pools is manageable.
A hybrid discovery approach often offers the most robust solution. For instance, an initial bulk discovery of older pools can be performed using factory read functions (like Uniswap V2's allPairs). Subsequently, real-time monitoring and updates for new pool creations can be handled by listening to factory events. This balances the need for historical completeness with the efficiency of event-based tracking for ongoing discovery.IV. Mapping Key User Actions to Discovered Pools/MarketsAfter discovering the addresses of DEX pools and other relevant market contracts, the next crucial step is to identify and map key user actions to these entities. This involves analyzing transaction data and event logs associated with these contracts.A. Defining Key User Actions for Behavioral AnalysisThe specific user actions to track will depend on the goals of the behavioral analysis. However, a common set of interactions across DeFi and NFT protocols includes:1. DEX Interactions:
Swap: The fundamental action of exchanging one token for another within a liquidity pool.41 Examples of swap transactions can be found on Etherscan, often involving router contracts.43
Add Liquidity (Liquidity Provision): Users supply tokens (typically a pair) to a liquidity pool to earn trading fees and/or liquidity mining rewards.
Remove Liquidity: Users withdraw their supplied tokens and accrued fees from a liquidity pool.
2. Lending Protocol Interactions (e.g., Aave, Compound):
Supply: Users lend their assets to the protocol to earn interest. This is a primary interaction point.45 Etherscan examples can illustrate these transactions.47
Borrow: Users take out loans against their supplied collateral.
Repay: Users pay back their borrowed amounts, plus accrued interest.
Withdraw: Users retrieve their supplied assets from the protocol.
Flash Loans: A unique DeFi primitive allowing users to borrow assets without collateral, provided the loan is repaid within the same transaction block.49 These are often used for arbitrage or liquidations.
3. Liquid Staking Interactions (e.g., Lido, Rocket Pool):
Stake ETH: Users deposit ETH into the protocol and receive a liquid staking derivative token (e.g., stETH from Lido, rETH from Rocket Pool) in return.51
Withdraw/Unstake ETH: Users redeem their liquid staking tokens to get back their original ETH plus accrued staking rewards. This process might involve a withdrawal queue or swapping the liquid token on a DEX.
4. NFT Marketplace Interactions (e.g., OpenSea, Blur):
Buy NFT (Order Fulfillment): A user accepts and fulfills an existing sell order for an NFT.
Sell NFT (Order Fulfillment): A user's listed NFT is purchased by another user, fulfilling the sell order.
These actions typically involve interactions with the marketplace's core contract, like OpenSea's Seaport.32 Etherscan can be used to trace these sales.57
B. Identifying Interaction Points: Router, Pool/Market, and Other Key ContractsUsers rarely interact directly with the underlying pool/market contracts, especially in DEXs. Instead, they typically go through intermediary contracts like routers or proxies, which abstract away some of the complexities and optimize execution.
Uniswap:

Uniswap V2 Router 2: 0x7a250d5630b4cf539739df2c5dacb4c659f2488d.37 Note: Etherscan also shows 0xf164fc0ec4e93095b804a4795bbe1e041497b92a as a V2 Router.59
Uniswap V3 SwapRouter: 0xE592427A0AEce92De3Edee1F18E0157C05861564.16
Uniswap Universal Router: 0xef1c6e67703c7bd7107eed8303fbe6ec2554bf6b (also seen as 0x66a9893cc07d91d95644aedd05d03f95e1dba8af in documentation 16). This is the preferred entry point for ERC20 and NFT swaps, replacing SwapRouter02.17
These routers handle token pathing and interact with the specific pair/pool contracts discovered earlier.


Curve Finance: Interactions can occur directly with pool contracts or through "zap" contracts that simplify liquidity provision across multiple pools or with different input tokens. The specific router/zap addresses vary.
Aave: User interactions (supply, borrow, repay, withdraw) are primarily with the main Pool contract. For Aave V3 on Ethereum Mainnet, this is 0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2.12
Lido: Staking ETH (submitting ETH to receive stETH) involves interacting with the stETH token contract itself: 0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84.25 The submit function is typically called.
Compound Finance (V2): Users interact with individual cToken contracts (representing supplied/borrowed assets, e.g., cETH, cDAI 27) for minting (supplying) and borrowing. These interactions are governed by the Comptroller contract: 0x3d9819210A31b4961b30EF54bE2aeD79B9c9Cd3B 26, which manages risk and market listings.
OpenSea: Transactions are facilitated through the Seaport protocol contract. A commonly referenced address is 0x0000000000000068F116a894984e2DB1123eB395 (Seaport 1.6).13
Blur: Blur utilizes its own set of marketplace contracts, such as "Blur.io: Marketplace 3" at 0x867cDd985c84cb8c9079397b1e04b89d95c19103.29 It may also interact with or aggregate listings from other protocols like Seaport.66 The BLUR token contract is 0x5283d291dbcf85356a21ba090e6db59121208b44.67 Loan functionalities are handled via the Blend protocol.66
Table 3: Common Interaction Contract Addresses for Selected Protocols (Ethereum Mainnet)Protocol NameContract RoleMainnet AddressLink to Etherscan ExampleUniswap V2Router (UniswapV2Router02)0x7a250d5630b4cf539739df2c5dacb4c659f2488d37Uniswap V3SwapRouter0xE592427A0AEce92De3Edee1F18E0157C0586156416UniswapUniversalRouter (Preferred for V3/NFT Swaps)0xef1c6e67703c7bd7107eed8303fbe6ec2554bf6b70Aave V3Pool (Main Lending/Borrowing Contract)0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e223Compound V2Comptroller (Risk Management & Market Listing)0x3d9819210A31b4961b30EF54bE2aeD79B9c9Cd3B26LidostETH Token Contract (Staking Entry Point)0xae7ab96520DE3A18E5e111B5EaAb095312D7fE8424OpenSeaSeaport Protocol (Marketplace Core)0x0000000000000068F116a894984e2DB1123eB39513BlurMarketplace Contract (Blur.io: Marketplace 3)0x867cDd985c84cb8c9079397b1e04b89d95c1910329This table provides direct links to the primary contracts users will interact with, simplifying the process of finding ABIs and monitoring transactions for these contracts.C. Decoding Transactions and Event Logs for Action MappingTo map user actions, one must analyze both the input data of transactions sent to these interaction contracts and the event logs emitted by them or the underlying pool/market contracts.1. Identifying Target Function Signatures and Selectors:For each key user action, the specific function signature on the interaction contract (router, pool, etc.) must be identified. The function selector, which is the first four bytes of the Keccak-256 hash of this canonical signature, is present in the input data of transactions calling this function.71
Uniswap V2 Router swapExactTokensForTokens:

Signature: swapExactTokensForTokens(uint256,uint256,address,address,uint256).37
Selector: 0x38ed1739.


Aave V3 Pool supply:

Signature (typical): supply(address asset, uint256 amount, address onBehalfOf, uint16 referralCode).21
Selector: 0x617ba037 (calculated from supply(address,uint256,address,uint16)).


Lido stETH submit:

Signature: submit(address _referral).62
Selector: 0xa1903eab (calculated from submit(address)).


OpenSea Seaport fulfillBasicOrder:

The exact signature depends on the BasicOrderParameters struct. A common canonical signature for fulfillBasicOrder taking a complex tuple is fulfillBasicOrder((address,address,address,(uint8,address,uint256,uint256,uint256),(uint8,address,uint256,uint256,uint256,address),uint8,uint256,uint256,bytes32,uint256,bytes32,uint256)).65
Selector: 0xfb0f3ee1.
OpenSea also uses an optimized version fulfillBasicOrder_efficient_6GL6yc which may have a different selector, potentially 0x00000000 if it's designed to be the default payable function or if it has a selector with leading zero bytes, or 0xb3a34c4c as seen in some Seaport versions.


2. Identifying Relevant Event Signatures and Topic0 Hashes:Key user actions usually result in the emission of events from the pool/market contract or the interaction contract itself. These events provide a structured and often more reliable record of the action's outcome.
Uniswap Pair/Pool Swap Event:

V2 Signature: Swap(address indexed sender, uint amount0In, uint amount1In, uint amount0Out, uint amount1Out, address indexed to).41
V2 Topic0: 0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822.42
V3 Signature: Swap(address indexed sender, address indexed recipient, int256 amount0, int256 amount1, uint160 sqrtPriceX96, uint128 liquidity, int24 tick) (from Uniswap V3 Pool ABI).
V3 Topic0: 0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67.42


Aave V3 Pool Supply Event:

Signature: Supply(address indexed reserve, address user, address indexed onBehalfOf, uint256 amount, uint16 indexed referralCode).21
Topic0: 0x2f3c22a3a06777a51711741c21b87f5013030c68606631270100000000000000 (calculated from Supply(address,address,address,uint256,uint16)).


Lido stETH Staking (Minting Event):

When ETH is staked via submit(), stETH is minted. This results in an ERC20 Transfer event.
Signature: Transfer(address indexed from, address indexed to, uint256 value).
Topic0: 0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef (standard ERC20 Transfer).
The from address will be 0x0000000000000000000000000000000000000000 for a mint.
The stETH proxy contract might also emit a ProxyDeposit(address sender, uint256 value) event with Topic0 0x15eeaa57c7bd188c1388020bcadc2c436ec60d647d36ef5b9eb3c742217ddee1.63


OpenSea Seaport OrderFulfilled Event:

Signature: OrderFulfilled(bytes32 orderHash, address indexed offerer, address indexed zone, address recipient, SpentItem offer, ReceivedItem consideration).3256,(uint8,address,uint256,uint256,address))). The one from 65 derived from Seaport 1.6 source isOrderFulfilled(bytes32 orderHash, address indexed offerer, address indexed zone, address recipient, (uint8 itemType, address token, uint256 identifier, uint256 amount) offer, (uint8 itemType, address token, uint256 identifier, uint256 amount, address recipient) consideration)`.
Topic0 65: 0x9d9af8e38d66c62e2c12f0225249fd9d721c54b83f48d9352c97c6cacdcb6f31.


3. Extracting Data:
From Transaction Input (tx.input): The input data of a transaction contains the function selector followed by ABI-encoded arguments. Using the contract's ABI, these arguments can be decoded to understand the user's intended action and parameters (e.g., amounts, token paths, recipient addresses). The msg.sender of the transaction is typically the user initiating the action.
From Event Logs: Event logs provide a structured way to capture the results of an action. After fetching logs using eth_getLogs (filtered by contract address and Topic0), the log.data (for non-indexed parameters) and log.topics (for indexed parameters) can be decoded using the ABI. This yields details like actual amounts transferred, tokens involved, and parties to the transaction.
The combination of analyzing transaction input data and emitted event logs provides a comprehensive view of user actions. Input data reveals the user's intent and initial parameters, while event logs confirm the execution and provide the actual outcomes. For instance, a swapExactTokensForTokens call to a Uniswap router specifies the amountIn and a minimum amountOutMin 37; the corresponding Swap event from the pair contract will show the actual amountIn processed and amountOut received 42, reflecting any slippage. Relying on both sources offers a more robust mapping of the user's action and its results.Table 4: Key User Actions - Signatures, Selectors, and Event Topics
ProtocolActionInteraction Contract TypeFunction Signature (Example)Function SelectorEvent Emitting Contract TypeEvent Signature (Example)Event Topic0Uniswap V2SwapRouterswapExactTokensForTokens(uint256,uint256,address,address,uint256) 370x38ed1739PairSwap(address indexed sender, uint256 amount0In, uint256 amount1In, uint256 amount0Out, uint256 amount1Out, address indexed to) 410xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822 42Uniswap V3SwapRouter (SwapRouter)exactInputSingle((address,address,uint24,address,uint256,uint256,uint256,uint160))0xc04b8602PoolSwap(address indexed sender, address indexed recipient, int256 amount0, int256 amount1, uint160 sqrtPriceX96, uint128 liquidity, int24 tick)0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67 42Aave V3SupplyPoolsupply(address asset, uint256 amount, address onBehalfOf, uint16 referralCode)0x617ba037PoolSupply(address indexed reserve, address user, address indexed onBehalfOf, uint256 amount, uint16 indexed referralCode)0x2f3c22a3a06777a51711741c21b87f5013030c68606631270100000000000000LidoStake ETHstETH Tokensubmit(address _referral) 62 (payable)0xa1903eabstETH TokenTransfer(address indexed from, address indexed to, uint256 value) (for stETH minting) OR ProxyDeposit(address sender, uint256 value) 630xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef (Transfer) 0x15eeaa57c7bd188c1388020bcadc2c436ec60d647d36ef5b9eb3c742217ddee1 (ProxyDeposit)OpenSea SeaportFulfill OrderSeaportfulfillBasicOrder((address,address,address,(uint8,address,uint256,uint256,uint256),(uint8,address,uint256,uint256,uint256,address),uint8,uint256,uint256,bytes32,uint256,bytes32,uint256)) 650xfb0f3ee1SeaportOrderFulfilled(bytes32 orderHash, address indexed offerer, address indexed zone, address recipient, (uint8 itemType, address token, uint256 identifier, uint256 amount), (uint8 itemType, address token, uint256 identifier, uint256 amount, address recipient)) 650x9d9af8e38d66c62e2c12f0225249fd9d721c54b83f48d9352c97c6cacdcb6f31 65Compound V2Supply (Mint)cTokenmint(uint256 mintAmount) (payable if cETH)0xa0712d68cTokenMint(address minter, uint256 mintAmount, uint256 mintTokens) 260x4c209b5fc8ad50758f13e2e1088ba56a560dff690a1c6fef26394f4c03821c4fCompound V2BorrowcTokenborrow(uint256 borrowAmount)0x4b8a3529cTokenBorrow(address borrower, uint256 borrowAmount, uint256 accountBorrows, uint256 totalBorrows) 260xae61be3d95f3c6094005496c6e4e07913508005f377075f3c734638598eba40f
Note: Function selectors and Topic0 hashes are calculated based on the canonical signatures. Structs in signatures are represented by tuple. For payable functions, the ETH value is available in tx.value.D. Step-by-Step Examples for Mapping Specific Actions1. DEX Swap (e.g., Uniswap V2):
Interaction Flow: A user initiates a swap by calling a function like swapExactTokensForTokens on a Uniswap V2 Router contract (e.g., 0x7a250d5630b4cf539739df2c5dacb4c659f2488d 37). The router then interacts with the specific token pair contract (discovered via the Factory). The pair contract executes the swap logic and emits a Swap event.
Identifying the Transaction:

Look for transactions where tx.to is the Router address and tx.input starts with the selector for a swap function (e.g., 0x38ed1739 for swapExactTokensForTokens).
The user address is tx.from.


Extracting Data from tx.input (for swapExactTokensForTokens):

Decode tx.input using the Router ABI.
Parameters: amountIn (uint256), amountOutMin (uint256), path (address - sequence of token addresses, first is input, last is output), to (address - recipient of output tokens), deadline (uint256).


Extracting Data from Swap Event:

The Swap event is emitted by the Pair contract.
Event Signature: Swap(address indexed sender, uint amount0In, uint amount1In, uint amount0Out, uint amount1Out, address indexed to).41
Topic0: 0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822.42
log.address is the Pair contract address.
log.topics is the sender (often the Router).
log.topics is the to (final recipient, same as to in router call).
log.data contains amount0In, amount1In, amount0Out, amount1Out. These need to be mapped to the actual input/output tokens based on the path from the router call and the token0/token1 order in the pair.


Mapping: The user_address is tx.from. The pool_or_market_address is log.address (the Pair contract). token_in_address is path. token_out_address is path[path.length - 1]. token_in_amount and token_out_amount are derived from the Swap event's amount0In/Out and amount1In/Out fields, considering the token order.
2. Lending - Supply (e.g., Aave V3):
Interaction Flow: User calls supply(address asset, uint256 amount, address onBehalfOf, uint16 referralCode) on the Aave V3 Pool contract (0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2).12
Identifying the Transaction:

tx.to is the Aave V3 Pool address.
tx.input starts with selector 0x617ba037.
User address is tx.from (or onBehalfOf if specified).


Extracting Data from tx.input:

Decode tx.input using Pool ABI.
Parameters: asset (address of token supplied), amount (uint256 amount supplied), onBehalfOf (address for whom supply is made), referralCode (uint16).


Extracting Data from Supply Event:

Event Signature: Supply(address indexed reserve, address user, address indexed onBehalfOf, uint256 amount, uint16 indexed referralCode).
Topic0: 0x2f3c22a3a06777a51711741c21b87f5013030c68606631270100000000000000.
log.address is the Pool contract address.
log.topics is reserve (asset address).
log.topics is onBehalfOf.
log.topics is referralCode.
log.data contains user (actual supplier if onBehalfOf is different from tx.from) and amount.


Mapping: user_address is parsedEvent.args.user. pool_or_market_address is log.address. token_in_address is parsedEvent.args.reserve. token_in_amount is parsedEvent.args.amount. action_type is SUPPLY.
3. Liquid Staking - Stake ETH (e.g., Lido):
Interaction Flow: User calls the payable function submit(address _referral) on the Lido stETH contract (0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84), sending ETH with the transaction.51 The contract mints stETH to the user.
Identifying the Transaction:

tx.to is the Lido stETH contract address.
tx.input starts with selector 0xa1903eab.
tx.value is greater than 0 (amount of ETH staked).
User address is tx.from.


Extracting Data from Transfer Event (for stETH minting):

Event Signature: Transfer(address indexed from, address indexed to, uint256 value).
Topic0: 0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef.
log.address is the stETH contract address.
log.topics (from) is 0x0000000000000000000000000000000000000000.
log.topics (to) is the user's address (tx.from).
log.data contains value (amount of stETH minted).


Mapping: user_address is tx.from. pool_or_market_address is the stETH contract address. token_in_address is WETH address (representing ETH). token_in_amount is tx.value. token_out_address is stETH address. token_out_amount is the value from the Transfer event. action_type is STAKE.
4. NFT Sale (e.g., OpenSea Seaport):
Interaction Flow: A buyer (fulfiller) calls a function like fulfillBasicOrder(...) or fulfillOrder(...) on the Seaport contract (e.g., 0x0000000000000068F116a894984e2DB1123eB395) to accept a listed NFT offer.13
Identifying the Transaction:

tx.to is the Seaport contract address.
tx.input starts with a selector for one of Seaport's fulfillment functions (e.g., 0xfb0f3ee1 for a common fulfillBasicOrder variant).
The buyer is typically tx.from.


Extracting Data from OrderFulfilled Event:

Event Signature: OrderFulfilled(bytes32 orderHash, address indexed offerer, address indexed zone, address recipient, SpentItem offer, ReceivedItem consideration).32
Topic0: 0x9d9af8e38d66c62e2c12f0225249fd9d721c54b83f48d9352c97c6cacdcb6f31.65
log.address is the Seaport contract address.
log.topics is offerer (seller's address).
log.topics is zone.
log.data contains orderHash, recipient (buyer's address), offer array, and consideration array.
The offer array usually contains the NFT details (itemType, token address, identifier/tokenId, amount).
The consideration array usually contains payment details (itemType, token address (e.g., WETH or ETH_PLACEHOLDER), amount, recipient).


Mapping: user_address (buyer) is parsedEvent.args.recipient (or tx.from if recipient is address(0) in event). Seller is parsedEvent.args.offerer. pool_or_market_address is the Seaport contract. nft_address and token_id from parsedEvent.args.offer. Payment token and amount from parsedEvent.args.consideration. action_type is NFT_BUY (for buyer) or NFT_SELL (for seller).
V. Technical Implementation: Tools and ConsiderationsImplementing the described discovery and mapping plan requires careful selection of tools for node access, programming, data storage, and ABI management.A. Ethereum Node AccessAccess to an Ethereum node is fundamental for querying blockchain data. The type of node—full or archive—has significant implications for historical data retrieval capabilities.
Full Node: A full node downloads and verifies all blocks and maintains the current state of the blockchain. It typically stores recent block data (e.g., the last 128 blocks) and can derive older states, but it may prune historical states beyond a certain window to save disk space.35 For ongoing monitoring of new pools/markets and analysis of recent user activity, a full node can be sufficient. Hardware requirements include a fast multi-core CPU, 16GB+ RAM, and a fast SSD with at least 1-2TB of space, which will grow over time.36
Archive Node: An archive node stores the complete history of states for every block since genesis. This makes it indispensable for deep historical analysis, querying past contract states (e.g., balances at a specific block), or fetching very old event logs.35 The storage requirements for an archive node are substantially larger, potentially exceeding 12-15TB for a Geth archive node, although clients like Erigon offer more space-efficient archival.36
Recommendation: For a comprehensive historical discovery of all pools and markets from the inception of various protocols, access to an archive node is highly preferable. If the analysis is focused on recent activity or if a complete historical backfill is not critical, a full node might suffice, potentially supplemented by data from indexing services for older data.
RPC Providers: Running and maintaining a personal Ethereum node, especially an archive node, can be resource-intensive and complex. Third-party RPC providers such as QuickNode, Alchemy, Infura, and GetBlock 35 offer API access to Ethereum nodes, including archive nodes. These services abstract away the operational overhead and are often a more practical solution for most data collection needs.
B. Programming Libraries for On-Chain InteractionSoftware libraries are essential for programmatic interaction with an Ethereum node and smart contracts.
Ethers.js (JavaScript/TypeScript): A widely used, comprehensive library for Ethereum development. It provides functionalities for connecting to Ethereum nodes (via JSON-RPC), managing wallets, encoding and decoding ABI data, interacting with smart contracts (calling functions, listening to events), and various utility functions.43 Its Interface class is particularly useful for parsing transaction input and event logs.
Web3.py (Python): A popular Python library offering a similar range of functionalities as ethers.js, making it suitable for developers working within the Python ecosystem.
Usage: These libraries will be instrumental in:

Establishing a connection to the chosen Ethereum node (self-hosted or provider).
Instantiating contract objects using their ABIs and addresses.
Calling read-only functions on factory contracts (e.g., allPairsLength, getPair).
Fetching event logs (eth_getLogs) and decoding them.
Decoding transaction input data.


C. Data Storage and IndexingThe volume of data generated from discovering pools/markets and mapping user actions across numerous protocols can be immense. An efficient data storage and indexing strategy is crucial.
Challenges: Storing raw transaction and log data, along with derived information about pools, markets, and user actions, requires a scalable and queryable system.
Storage Options:

Relational Databases (e.g., PostgreSQL, MySQL): Suitable for storing structured data with well-defined schemas. Tables can be designed for pools/markets, tokens, and user actions, with relationships between them.
NoSQL Databases (e.g., MongoDB, Cassandra): Offer more flexibility for semi-structured data, which can be advantageous when dealing with diverse event log structures from various protocols.


Specialized Blockchain Indexing Solutions:

The Graph: A decentralized protocol for indexing and querying blockchain data. Developers create "subgraphs" that define which smart contracts to monitor, which events to process, and how to transform this data into entities that can be queried via GraphQL.38 This can significantly simplify the data ingestion pipeline.
SubQuery: Similar to The Graph, SubQuery provides tools and infrastructure for building custom data indexers for various blockchains, including Ethereum. It allows developers to transform and store blockchain data efficiently.38
Dune Analytics: While primarily an analytics platform where users write SQL queries, Dune's backend performs extensive indexing of blockchain data. It might be possible to leverage its datasets or build custom queries if direct data pipeline construction is too complex.
Custom Indexers: Building a custom indexing pipeline involves listening to new blocks, fetching relevant transactions and logs, decoding them, and storing them in a chosen database. This offers maximum flexibility but requires significant development effort.


Recommendation: For robust, scalable, and maintainable data collection and querying, leveraging specialized blockchain indexing services like The Graph or SubQuery is highly recommended. These platforms handle much of the low-level complexity of data extraction, decoding, and storage, allowing developers to focus on defining the data models and business logic. If a custom solution is preferred, careful planning of the database schema and data processing pipeline is essential. Building a custom data pipeline to ingest, decode, and store all relevant on-chain data is a significant engineering effort. Indexing services provide frameworks and infrastructure that can greatly accelerate this process by handling much of the low-level data extraction and providing queryable APIs.38
D. Obtaining Contract ABIsThe Application Binary Interface (ABI) is crucial for decoding transaction data and event logs. It defines the contract's functions, events, and data structures in a machine-readable format (typically JSON).
Etherscan (and similar block explorers): If a smart contract's source code has been verified on Etherscan, its ABI is usually available on the "Contract" tab. Etherscan also provides an API endpoint to fetch the ABI of a verified contract.43 Many of the browsed Etherscan links in the research material point to pages where ABIs can be found.22
Official Protocol Documentation: Protocol developers often include ABIs or links to them in their official documentation.12
Project GitHub Repositories: ABIs are commonly found as JSON files within the build/contracts/ or artifacts/ directories of a smart contract project's GitHub repository after compilation.21
NPM Packages: Some protocols distribute their contract ABIs as part of NPM packages, which can be easily integrated into JavaScript/TypeScript projects (e.g., @aave/core-v3 21, Uniswap's @uniswap/v2-core or @uniswap/v3-core packages 15).
It is essential to use the correct ABI for the specific version of the contract being interacted with, as ABIs can change between contract upgrades.VI. Laying the Foundation for Behavioral AnalysisThe data collected through the discovery and mapping process forms the bedrock for subsequent behavioral analysis. Structuring this data effectively is key.A. Structuring the Collected DataConsider organizing the data into relational tables or equivalent structures in a NoSQL database:
Pools_Markets Table:

pool_market_id (Primary Key)
pool_address (TEXT, UNIQUE, Indexed)
protocol_name (TEXT, e.g., "Uniswap V2", "Aave V3")
protocol_version (TEXT, e.g., "2.0", "3.0.1")
market_type (TEXT, e.g., "DEX_POOL", "LENDING_MARKET", "LIQUID_STAKING_POOL")
token0_address (TEXT, Indexed, for pairs)
token1_address (TEXT, Indexed, for pairs)
asset_address (TEXT, Indexed, for single-asset markets like lending)
other_pool_parameters (JSONB or TEXT, e.g., fee for Uniswap V3, amplification for Curve)
creation_block_number (BIGINT)
creation_timestamp (TIMESTAMP)


User_Actions Table:

action_id (Primary Key)
transaction_hash (TEXT, UNIQUE, Indexed)
log_index (INTEGER, part of composite key with tx_hash if multiple actions in one tx)
block_number (BIGINT, Indexed)
timestamp (TIMESTAMP, Indexed)
user_address (TEXT, Indexed - initiator of the action)
action_type (TEXT, Indexed, e.g., "SWAP", "SUPPLY", "BORROW", "STAKE_ETH", "NFT_BUY", "ADD_LIQUIDITY")
protocol_name (TEXT)
pool_market_address (TEXT, Indexed, Foreign Key to Pools_Markets.pool_address)
token_in_address (TEXT)
token_in_amount_raw (NUMERIC)
token_in_decimals (INTEGER)
token_out_address (TEXT)
token_out_amount_raw (NUMERIC)
token_out_decimals (INTEGER)
nft_address (TEXT, for NFT actions)
nft_token_id (NUMERIC, for NFT actions)
price_raw (NUMERIC, for NFT actions)
price_currency_address (TEXT, for NFT actions)
price_currency_decimals (INTEGER, for NFT actions)
gas_used (BIGINT)
effective_gas_price (BIGINT)
details (JSONB, for other action-specific parameters)


A critical aspect of data structuring is handling token amounts correctly. ERC20 tokens can have varying numbers of decimal places (e.g., USDC typically has 6, while WETH and many others have 18 64). Smart contracts store token amounts as large integers (e.g., uint256) without inherent decimal points. Therefore, when storing these amounts, it is essential to either store the raw integer value alongside the token's decimal count (obtained by calling the decimals() function on the token contract) or to normalize all amounts to a human-readable representation (e.g., as a floating-point number or a fixed-point decimal type). Failure to account for these differing decimal precisions will lead to severe inaccuracies in any quantitative behavioral analysis, such as comparing swap sizes or loan amounts.B. Initial Thoughts on Metrics and Patterns for Behavioral AnalysisWith the data structured as described, various avenues for behavioral analysis open up:
User Profiling:

Activity Frequency: How often does a user perform specific actions (e.g., daily swaps, weekly liquidity additions, monthly borrowing)?
Protocol Preferences: Does a user primarily interact with DEXs, lending protocols, or NFT marketplaces? Which specific protocols do they favor?
Transaction Sizes: What are the typical sizes of their swaps, loans, or NFT purchases?
Token Portfolio: Based on the tokens they interact with (swap, supply, hold), what does their implicit portfolio look like?
Sophistication: Are they using advanced features like flash loans 49 or complex multi-step DeFi strategies?


Protocol/Pool Level Analysis:

Activity Hotspots: Which pools or markets see the most transaction volume or unique user interactions?
Fund Flows: How does capital move between different protocols or within a protocol's ecosystem?
Arbitrage Identification: Detect patterns indicative of arbitrage, such as rapid buy-and-sell sequences across different DEX pools for the same asset, often involving flash loans.72
Liquidation Analysis: In lending protocols, identify accounts undergoing liquidation, the liquidators, and the assets involved.


Temporal Patterns:

Market Event Correlation: Do user activity patterns (e.g., trading volume, borrowing rates) change significantly around major market news or events?
Evolution of Behavior: How does an individual address's or a cohort's behavior change over time? Do they adopt new protocols or strategies?


This structured on-chain data, when combined, can paint a detailed picture of user engagement with the Ethereum ecosystem.VII. ConclusionSummary of the PlanThis report has detailed a systematic technical plan for the automated discovery of DEX pools and other market-related smart contracts within top Ethereum applications. The core of this plan revolves around:
Strategic Application Selection: Identifying key DeFi and NFT applications based on metrics like TVL and trading volume, ensuring a rich dataset for analysis.
Factory/Registry Identification: Locating the central factory or registry contracts for these applications through documentation, blockchain explorers, and community resources.
Automated Pool/Market Discovery: Utilizing factory-emitted events (such as PairCreated or PoolCreated) and, where applicable, factory read functions to systematically find the addresses of individual liquidity pools and market contracts. This involves understanding event signatures, calculating Topic0 hashes, and proficiently querying Ethereum nodes.
User Action Mapping: Defining key on-chain user actions (swaps, supplies, borrows, NFT trades, etc.) and identifying their corresponding function signatures, selectors, and emitted events. This allows for the decoding of transaction inputs and event logs to link specific user addresses to actions on specific pools/markets.
Reinforcement of UtilityThe successful execution of this plan provides a robust and structured foundational data layer. This dataset, which accurately maps user addresses to their interactions with specific on-chain markets, is invaluable for conducting sophisticated behavioral analysis. It enables deep insights into user strategies, protocol adoption trends, market dynamics, risk concentrations, and the overall economic health of the Ethereum ecosystem. By moving beyond aggregated statistics to individual user-level interactions, analysts can uncover nuanced patterns that are otherwise invisible.Future Considerations and Potential ExpansionsThe framework established by this plan can be extended and enhanced in several ways:
Cross-Chain Analysis: Many of the targeted protocols are deployed on multiple EVM-compatible chains (e.g., Polygon, Arbitrum, Base 5). The core methodology for discovery and action mapping can be adapted to these other chains, allowing for a broader understanding of user behavior across the multi-chain landscape.
Advanced Behavioral Modeling: The collected dataset is well-suited for the application of machine learning techniques. This could involve clustering users based on their behavioral profiles, predicting future actions, detecting anomalous or potentially malicious activities, or building more sophisticated risk models.
Real-time Alerting Systems: Based on the continuous monitoring of on-chain actions, systems can be developed to trigger real-time alerts for specific events of interest. This could include large liquidity movements, significant flash loan activities, detection of potential arbitrage bots, or unusual trading volumes in specific pools.
Integration with Off-Chain Data: Correlating the on-chain behavioral data with off-chain information—such as social media sentiment, news events, tokenomic changes, or governance proposals—can provide a richer context for understanding why certain behaviors emerge and how external factors influence on-chain activity.
Enhanced User Interface and Visualization: Developing tools to visualize user interaction flows, capital movements, and behavioral patterns can make the insights derived from the data more accessible and actionable.
Ethical ConsiderationsAnalyzing address-level blockchain data, while powerful, also raises ethical considerations regarding user privacy. Although Ethereum addresses are pseudonymous, patterns of activity can sometimes be linked to real-world identities or reveal sensitive financial strategies. It is important that any analysis conducted using this data is done responsibly, with an awareness of potential privacy implications, and in compliance with any relevant legal or regulatory frameworks. The focus should be on understanding aggregate behaviors and market dynamics rather than de-anonymizing individual users without consent.By following the detailed steps and leveraging the technical insights provided in this report, entities can build a powerful analytical capability to understand the intricate behaviors of participants in the Ethereum ecosystem.