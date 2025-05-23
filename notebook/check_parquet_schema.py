# save as inspect_parquet_schema.py in your project root or notebooks
import pyarrow.parquet as pq
import os
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_project_root() -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.basename(current_dir) in ["notebooks", "scripts", "notebook"]:
        return os.path.dirname(current_dir)
    return current_dir


if __name__ == "__main__":
    project_root = get_project_root()
    logging.info(f"Project root: {project_root}")

    data_name = "basic_rev_daily_data_20250521_to_20250521_sample100.parquet"  # From successful ETL
    data_path = os.path.join(project_root, "data", "processed", data_name)
    logging.info(f"Inspecting Parquet file: {data_path}")

    try:
        parquet_file = pq.ParquetFile(data_path)
        print(f"\n--- Parquet File Schema for {data_name} ---")
        print(parquet_file.schema)
        print("---------------------------------------------------\n")

        # You can also iterate through fields if needed:
        # logging.info("Fields:")
        # for field in parquet_file.schema:
        #     logging.info(f"  - Name: {field.name}, Type: {field.type}, Nullable: {field.nullable}")

    except FileNotFoundError:
        logging.error(f"Data file not found at {data_path}")
    except Exception as e:
        logging.exception(f"An error occurred: {e}")
