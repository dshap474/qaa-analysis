# ┌────────────────────────────────────────────────────────────────────────────────────┐
# │ Phase 2: Volume-Filtered Contract Discovery Strategy                              │
# └────────────────────────────────────────────────────────────────────────────────────┘

**Updated Phase 2 Strategy: 180-Day Volume Coverage for High-Impact Pool Discovery**

---
seven7s/qaa-analysis/src/qaa_analysis/contract_universe/docs/Phase2-Volume-Strategy.md
---
Detailed strategy document for Phase 2 implementation focusing on discovering 
high-impact DeFi pools using 180-day trailing volume coverage analysis.

## 🎯 **Strategy Overview**

### **Key Principle**
Instead of discovering ALL contracts (300k+), focus on pools that account for **90% of 180-day trailing volume**. This gives us the pools that actually matter for behavioral analysis.

### **Expected Results**
```python
VOLUME_STRATEGY_RESULTS = {
    "Target Coverage": "90% of total 180-day volume",
    "Expected Pool Count": "400-800 pools (vs 300k+ total)",
    "Processing Time": "~30 minutes (vs 8+ hours)",
    "API Calls": "~500 (vs 1,700+)",
    "Storage Size": "~200KB (vs 60MB)",
    "Update Frequency": "Weekly",
    "Quality": "High-impact pools only"
}
```

## 📊 **Volume Distribution Analysis**

### **Real DeFi Volume Distribution (Pareto Principle)**
```python
DEFI_VOLUME_REALITY = {
    "Top 1% of pools": "~60% of volume",
    "Top 5% of pools": "~80% of volume", 
    "Top 10% of pools": "~90% of volume",
    "Top 20% of pools": "~95% of volume",
    "Remaining 80%": "~5% of volume"
}

# This means for Uniswap V2 (150k pools):
UNISWAP_V2_EXAMPLE = {
    "Total pools": 150_000,
    "90% volume coverage": "~200 pools (0.13%)",
    "99% volume coverage": "~800 pools (0.5%)"
}
```

### **Why 180-Day Volume?**
- ✅ **Filters seasonal noise** (eliminates pump-and-dump pools)
- ✅ **Captures consistent performers** (established trading pairs)
- ✅ **Includes major pairs** across different market cycles
- ✅ **Excludes dead pools** (zero or minimal recent activity)
- ✅ **More stable for analysis** (reliable behavioral patterns)

## 🏗️ **Implementation Architecture**

### **Phase 2 Pipeline**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ 1. Factory      │───▶│ 2. Volume       │───▶│ 3. Coverage     │
│ Discovery       │    │ Enrichment      │    │ Filtering       │
│                 │    │                 │    │                 │
│ All Addresses   │    │ + 180d Volume   │    │ Top 90% Only    │
│ (Fast)          │    │ + Token Info    │    │ (Smart Filter)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
      ~30 min                ~15 min                ~5 min

Final Result: High-Impact Pool Universe (~400-800 pools)
```

## 🔧 **Technical Implementation Plan**

### **Core Components**

#### **1. Lightweight Factory Discovery**
```python
class FactoryDiscovery:
    """Fast address-only discovery from factory contracts"""
    
    def discover_pool_addresses(self) -> List[Dict]:
        """Get pool addresses efficiently (no metadata yet)"""
        
        all_pools = []
        for factory in self.factory_configs:
            
            # Use read functions for bulk discovery (fastest)
            if factory.protocol in ["Uniswap V2", "SushiSwap"]:
                pools = self._bulk_discover_via_read_functions(factory)
            
            # Use recent events for newer protocols
            else:
                pools = self._discover_recent_pools(factory)
            
            all_pools.extend(pools)
        
        return all_pools  # Just addresses + basic info
```

#### **2. Volume Data Source Integration**
```python
class VolumeDataProvider:
    """Multi-source volume data provider with fallbacks"""
    
    def get_180d_volume(self, pool_address: str, protocol: str) -> Dict:
        """Get 180-day trailing volume from multiple sources"""
        
        # Primary: The Graph Protocol (free, reliable)
        try:
            return self._get_from_graph(pool_address, protocol)
        except Exception as e:
            self.logger.debug(f"Graph failed: {e}")
        
        # Fallback: DeFiLlama (free, good coverage)
        try:
            return self._get_from_defillama(pool_address)
        except Exception as e:
            self.logger.debug(f"DeFiLlama failed: {e}")
        
        # Last resort: DEX Screener (free, basic)
        try:
            return self._get_from_dexscreener(pool_address)
        except Exception as e:
            self.logger.debug(f"DEX Screener failed: {e}")
        
        return None  # Skip pools without volume data
```

#### **3. Coverage Calculator**
```python
class VolumeCoverageCalculator:
    """Calculate pools needed for target volume coverage"""
    
    def calculate_90_percent_threshold(self, pools_with_volume: List) -> Dict:
        """Find pools that account for 90% of total volume"""
        
        # Sort by 180-day volume (descending)
        sorted_pools = sorted(pools_with_volume, 
                            key=lambda x: x['volume_180d'], 
                            reverse=True)
        
        total_volume = sum(p['volume_180d'] for p in sorted_pools)
        target_volume = total_volume * 0.90
        
        cumulative_volume = 0
        for i, pool in enumerate(sorted_pools):
            cumulative_volume += pool['volume_180d']
            
            if cumulative_volume >= target_volume:
                return {
                    'pools_needed': i + 1,
                    'volume_threshold': pool['volume_180d'],
                    'actual_coverage': cumulative_volume / total_volume,
                    'total_volume_180d': total_volume
                }
```

## 📋 **Data Sources & APIs**

### **Volume Data Sources (All Free Tier)**

#### **1. The Graph Protocol (Primary)**
```python
SUBGRAPH_ENDPOINTS = {
    "Uniswap V2": "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2",
    "Uniswap V3": "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3", 
    "SushiSwap": "https://api.thegraph.com/subgraphs/name/sushiswap/exchange",
    "Curve": "https://api.thegraph.com/subgraphs/name/messari/curve-finance-ethereum"
}

# Example query for 180-day volume
GRAPH_QUERY = """
{
  pair(id: "{pool_address}") {
    volumeUSD
    reserveUSD
    token0 { symbol }
    token1 { symbol }
    dayData(first: 180, orderBy: date, orderDirection: desc) {
      dailyVolumeUSD
    }
  }
}
"""
```

#### **2. DeFiLlama API (Backup)**
```python
DEFILLAMA_ENDPOINTS = {
    "pools": "https://api.llama.fi/pools",
    "protocol": "https://api.llama.fi/protocol/{protocol}",
    "historical": "https://api.llama.fi/protocol/{protocol}/historical"
}
```

#### **3. DEX Screener (Validation)**
```python
DEXSCREENER_ENDPOINTS = {
    "pair": "https://api.dexscreener.com/latest/dex/pairs/{chain}/{address}",
    "search": "https://api.dexscreener.com/latest/dex/search/?q={query}"
}
```

## 📊 **Expected Results by Protocol**

### **Volume Coverage Estimates**
```python
PROTOCOL_ESTIMATES = {
    "Uniswap V2": {
        "total_pools": 150_000,
        "90%_coverage_pools": 200,
        "example_top_pools": [
            "USDC/WETH", "WBTC/WETH", "DAI/USDC", "USDT/WETH",
            "LINK/WETH", "UNI/WETH", "SHIB/WETH"
        ]
    },
    "Uniswap V3": {
        "total_pools": 70_000,
        "90%_coverage_pools": 100,
        "example_top_pools": [
            "USDC/WETH 0.05%", "WBTC/WETH 0.3%", "DAI/USDC 0.01%",
            "USDC/WETH 0.3%", "ETH/USDT 0.05%"
        ]
    },
    "Curve": {
        "total_pools": 5_000,
        "90%_coverage_pools": 25,
        "example_top_pools": [
            "3pool (DAI+USDC+USDT)", "stETH/ETH", "FRAX/USDC",
            "crvUSD/USDT", "ETH/frxETH"
        ]
    },
    "Combined Total": {
        "estimated_pools": 400,
        "coverage": "90% of DeFi volume",
        "storage_size": "~200KB"
    }
}
```

## 🚀 **Implementation Steps**

### **Step 1: Quick Factory Discovery (10 min)**
- Get all pool addresses from major factories
- Use efficient read functions (allPairs, allPools)
- No volume data yet - just addresses

### **Step 2: Volume Data Enrichment (15 min)**
- Batch query volume APIs for discovered pools
- Focus on 180-day trailing volume
- Collect token symbols and basic metadata

### **Step 3: Coverage Filtering (5 min)**
- Sort pools by 180-day volume
- Calculate 90% coverage threshold
- Return filtered high-impact pool universe

### **Step 4: Quality Validation (5 min)**
- Cross-validate volume data across sources
- Add manual high-importance pools if needed
- Export final filtered universe

## 💰 **Resource Requirements**

### **API Usage (Free Tier Compatible)**
```python
API_USAGE_ESTIMATE = {
    "Factory Discovery": {
        "calls": 50,
        "time": "10 minutes"
    },
    "Volume Enrichment": {
        "calls": 400,  # Batch queries
        "time": "15 minutes",
        "rate_limit": "5/second (The Graph)"
    },
    "Total": {
        "calls": 450,
        "time": "30 minutes",
        "cost": "$0 (free tier)"
    }
}
```

### **Update Schedule**
- **Weekly**: Refresh volume rankings
- **Monthly**: Full rediscovery and recalculation
- **Quarterly**: Review coverage targets and add new protocols

## 🎯 **Success Metrics**

### **Quality Indicators**
- ✅ Captures major trading pairs (USDC/WETH, WBTC/WETH, etc.)
- ✅ Includes established DeFi blue-chips
- ✅ Filters out dead/inactive pools
- ✅ Maintains 90%+ volume coverage
- ✅ Reasonable pool count (400-800)

### **Performance Indicators**
- ✅ Completes in under 30 minutes
- ✅ Uses under 500 API calls
- ✅ Fits in free API tiers
- ✅ Produces manageable dataset (<1MB)

## 📋 **Next Steps**

After Phase 2 completion, we'll have:
- **High-Impact Pool Universe** (~400-800 pools)
- **Volume and TVL Metrics** for each pool
- **Token Metadata** (symbols, decimals, addresses)
- **Protocol Classifications** (Uniswap V2/V3, Curve, etc.)

This filtered universe will be the foundation for:
- **Phase 3**: Action Mapping (transaction decoding on relevant pools)
- **Phase 4**: Behavioral Analysis (user profiling on active venues)
- **Phase 5**: Data Storage & Analytics (efficient querying and insights)

---

**Ready to Implement**: This strategy provides maximum analytical value with minimal computational overhead, focusing on the pools that actually drive DeFi activity. 