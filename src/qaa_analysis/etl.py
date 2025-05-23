from __future__ import annotations
from google.cloud import bigquery, bigquery_storage
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

from qaa_analysis.config import PROJECT_ID

DATE_STR = "2025-05-21"  # <-- change to any UTC date

SQL = f"""
WITH day_tx AS (
  SELECT
    from_address                         AS address,
    receipt_gas_used                     AS gas_used,
    (receipt_gas_used * gas_price)/1e18  AS rev_eth
  FROM `bigquery-public-data.crypto_ethereum.transactions`
  WHERE DATE(block_timestamp) = '{DATE_STR}'
)
SELECT
  address,
  COUNT(*)                AS tx_cnt,
  SUM(gas_used)           AS gas_used,
  SUM(rev_eth)            AS rev_eth
FROM day_tx
GROUP BY address
"""


def main() -> None:
    bq = bigquery.Client(project=PROJECT_ID)
    bqstor = bigquery_storage.BigQueryReadClient()

    df = (
        bq.query(SQL)
        .result()
        .to_dataframe(bqstorage_client=bqstor, create_bqstorage_client=True)
    )

    features = df[["tx_cnt", "gas_used", "rev_eth"]]
    X = StandardScaler().fit_transform(features)

    km = KMeans(n_clusters=8, n_init="auto", random_state=42)
    df["cluster"] = km.fit_predict(X)

    summary = (
        df.groupby("cluster")["rev_eth"]
        .agg(count="size", total_rev_eth="sum", avg_rev_eth="mean")
        .reset_index()
        .sort_values("total_rev_eth", ascending=False)
    )

    print(summary.to_string(index=False, float_format=lambda x: f"{x:,.4f}"))


if __name__ == "__main__":
    main()
