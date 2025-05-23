#!/usr/bin/env python3
"""
Verification script for Basic REV Query & ETL Implementation.

This script validates that all components meet the SPEC PROMPT requirements
and provides a comprehensive verification log.
"""

import sys
import logging
from pathlib import Path
from typing import List, Dict, Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from qaa_analysis.queries.rev_queries import (
    get_blockworks_rev_query,
    validate_date_format,
    get_rev_query_metadata,
)
from qaa_analysis.config import PipelineConfig


def setup_verification_logging() -> logging.Logger:
    """Setup logging for verification process."""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    return logging.getLogger(__name__)


def verify_rev_queries_module() -> Dict[str, bool]:
    """
    Verify the rev_queries module meets all requirements.

    Returns:
        Dictionary mapping requirement to verification status.
    """
    logger = logging.getLogger(__name__)
    results = {}

    logger.info("=" * 60)
    logger.info("VERIFYING REV QUERIES MODULE")
    logger.info("=" * 60)

    # Test 1: Function exists with correct signature
    try:
        query = get_blockworks_rev_query("2024-01-01", "2024-01-07", 1.0)
        results["function_exists_correct_signature"] = True
        logger.info("✓ get_blockworks_rev_query function exists with correct signature")
    except Exception as e:
        results["function_exists_correct_signature"] = False
        logger.error(f"✗ Function signature error: {e}")

    # Test 2: Query contains required SQL components
    try:
        query = get_blockworks_rev_query("2024-01-01", "2024-01-07", 1.0)

        required_components = [
            "WITH filtered_transactions AS",
            "rev_components AS",
            "bigquery-public-data.crypto_ethereum.transactions",
            "DATE(block_timestamp) BETWEEN",
            "COALESCE(base_fee_per_gas, 0)",
            "GROUP BY address, tx_date",
            "ORDER BY tx_date DESC, total_rev_eth DESC",
        ]

        all_present = all(component in query for component in required_components)
        results["sql_components_present"] = all_present

        if all_present:
            logger.info("✓ All required SQL components present in query")
        else:
            missing = [comp for comp in required_components if comp not in query]
            logger.error(f"✗ Missing SQL components: {missing}")

    except Exception as e:
        results["sql_components_present"] = False
        logger.error(f"✗ SQL component verification failed: {e}")

    # Test 3: Required output columns
    try:
        query = get_blockworks_rev_query("2024-01-01", "2024-01-07", 1.0)

        required_columns = [
            "address",
            "tx_date",
            "tx_count",
            "sum_gas_used",
            "total_rev_eth",
            "tips_rev_eth",
            "burned_rev_eth",
            "avg_tx_fee_eth",
        ]

        all_columns_present = all(col in query for col in required_columns)
        results["output_columns_present"] = all_columns_present

        if all_columns_present:
            logger.info("✓ All required output columns present")
        else:
            missing = [col for col in required_columns if col not in query]
            logger.error(f"✗ Missing output columns: {missing}")

    except Exception as e:
        results["output_columns_present"] = False
        logger.error(f"✗ Output column verification failed: {e}")

    # Test 4: Sampling functionality
    try:
        query_with_sampling = get_blockworks_rev_query("2024-01-01", "2024-01-07", 0.1)
        query_without_sampling = get_blockworks_rev_query(
            "2024-01-01", "2024-01-07", 1.0
        )

        sampling_works = (
            "RAND() < 0.1" in query_with_sampling
            and "RAND()" not in query_without_sampling
        )

        results["sampling_functionality"] = sampling_works

        if sampling_works:
            logger.info("✓ Sampling functionality works correctly")
        else:
            logger.error("✗ Sampling functionality not working correctly")

    except Exception as e:
        results["sampling_functionality"] = False
        logger.error(f"✗ Sampling verification failed: {e}")

    # Test 5: Date validation function
    try:
        valid_tests = [
            validate_date_format("2024-01-01"),
            validate_date_format("2023-12-31"),
            not validate_date_format("invalid-date"),
            not validate_date_format("2024/01/01"),
        ]

        date_validation_works = all(valid_tests)
        results["date_validation"] = date_validation_works

        if date_validation_works:
            logger.info("✓ Date validation function works correctly")
        else:
            logger.error("✗ Date validation function not working correctly")

    except Exception as e:
        results["date_validation"] = False
        logger.error(f"✗ Date validation verification failed: {e}")

    # Test 6: Metadata function
    try:
        metadata = get_rev_query_metadata("2024-01-01", "2024-01-07", 0.5)

        required_metadata_fields = [
            "query_type",
            "start_date",
            "end_date",
            "days_span",
            "sample_rate",
            "is_sampled",
            "target_table",
            "estimated_complexity",
        ]

        metadata_complete = all(field in metadata for field in required_metadata_fields)
        results["metadata_function"] = metadata_complete

        if metadata_complete:
            logger.info("✓ Metadata function returns all required fields")
        else:
            missing = [
                field for field in required_metadata_fields if field not in metadata
            ]
            logger.error(f"✗ Missing metadata fields: {missing}")

    except Exception as e:
        results["metadata_function"] = False
        logger.error(f"✗ Metadata function verification failed: {e}")

    return results


def verify_etl_module() -> Dict[str, bool]:
    """
    Verify the basic_rev_etl module meets all requirements.

    Returns:
        Dictionary mapping requirement to verification status.
    """
    logger = logging.getLogger(__name__)
    results = {}

    logger.info("=" * 60)
    logger.info("VERIFYING ETL MODULE")
    logger.info("=" * 60)

    # Test 1: Module imports correctly
    try:
        from qaa_analysis.etl.basic_rev_etl import (
            setup_logging,
            validate_dataframe,
            save_dataframe_safely,
            main,
        )

        results["module_imports"] = True
        logger.info("✓ ETL module imports correctly")
    except Exception as e:
        results["module_imports"] = False
        logger.error(f"✗ ETL module import failed: {e}")
        return results

    # Test 2: Functions have correct signatures
    try:
        import inspect

        # Check main function signature
        main_sig = inspect.signature(main)
        main_correct = len(main_sig.parameters) == 0

        # Check other function signatures
        setup_logging_sig = inspect.signature(setup_logging)
        setup_logging_correct = len(setup_logging_sig.parameters) == 0

        validate_df_sig = inspect.signature(validate_dataframe)
        validate_df_correct = len(validate_df_sig.parameters) == 2

        save_df_sig = inspect.signature(save_dataframe_safely)
        save_df_correct = len(save_df_sig.parameters) == 3

        signatures_correct = all(
            [main_correct, setup_logging_correct, validate_df_correct, save_df_correct]
        )

        results["function_signatures"] = signatures_correct

        if signatures_correct:
            logger.info("✓ All function signatures are correct")
        else:
            logger.error("✗ Some function signatures are incorrect")

    except Exception as e:
        results["function_signatures"] = False
        logger.error(f"✗ Function signature verification failed: {e}")

    # Test 3: Core module integration
    try:
        # Check that the module imports all required core modules
        import qaa_analysis.etl.basic_rev_etl as etl_module
        import inspect

        source = inspect.getsource(etl_module)

        required_imports = [
            "PipelineConfig",
            "CostAwareBigQueryClient",
            "QueryCache",
            "get_blockworks_rev_query",
        ]

        imports_present = all(imp in source for imp in required_imports)
        results["core_module_integration"] = imports_present

        if imports_present:
            logger.info("✓ All required core modules are imported")
        else:
            missing = [imp for imp in required_imports if imp not in source]
            logger.error(f"✗ Missing imports: {missing}")

    except Exception as e:
        results["core_module_integration"] = False
        logger.error(f"✗ Core module integration verification failed: {e}")

    # Test 4: Logging configuration
    try:
        logger_instance = setup_logging()
        has_required_methods = all(
            hasattr(logger_instance, method)
            for method in ["info", "error", "warning", "debug"]
        )

        results["logging_setup"] = has_required_methods

        if has_required_methods:
            logger.info("✓ Logging setup works correctly")
        else:
            logger.error("✗ Logging setup missing required methods")

    except Exception as e:
        results["logging_setup"] = False
        logger.error(f"✗ Logging setup verification failed: {e}")

    return results


def verify_file_structure() -> Dict[str, bool]:
    """
    Verify that all required files exist in correct locations.

    Returns:
        Dictionary mapping requirement to verification status.
    """
    logger = logging.getLogger(__name__)
    results = {}

    logger.info("=" * 60)
    logger.info("VERIFYING FILE STRUCTURE")
    logger.info("=" * 60)

    # Define required files
    required_files = [
        "src/qaa_analysis/queries/__init__.py",
        "src/qaa_analysis/queries/rev_queries.py",
        "src/qaa_analysis/etl/basic_rev_etl.py",
        "tests/test_rev_queries.py",
        "tests/test_basic_rev_etl.py",
    ]

    project_root = Path(__file__).parent.parent

    for file_path in required_files:
        full_path = project_root / file_path
        exists = full_path.exists()
        results[f"file_exists_{file_path.replace('/', '_').replace('.', '_')}"] = exists

        if exists:
            logger.info(f"✓ {file_path} exists")
        else:
            logger.error(f"✗ {file_path} missing")

    # Check that files are not empty
    non_empty_results = {}
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            non_empty = size > 100  # At least 100 bytes
            non_empty_results[
                f"file_non_empty_{file_path.replace('/', '_').replace('.', '_')}"
            ] = non_empty

            if non_empty:
                logger.info(f"✓ {file_path} is non-empty ({size} bytes)")
            else:
                logger.error(f"✗ {file_path} is too small ({size} bytes)")

    results.update(non_empty_results)
    return results


def verify_configuration_integration() -> Dict[str, bool]:
    """
    Verify integration with existing configuration system.

    Returns:
        Dictionary mapping requirement to verification status.
    """
    logger = logging.getLogger(__name__)
    results = {}

    logger.info("=" * 60)
    logger.info("VERIFYING CONFIGURATION INTEGRATION")
    logger.info("=" * 60)

    # Test 1: PipelineConfig can be imported and instantiated
    try:
        config = PipelineConfig()
        results["config_instantiation"] = True
        logger.info("✓ PipelineConfig instantiates correctly")
    except Exception as e:
        results["config_instantiation"] = False
        logger.error(f"✗ PipelineConfig instantiation failed: {e}")
        return results

    # Test 2: Required configuration methods exist
    try:
        config = PipelineConfig()

        # Test get_date_filter method
        start_date, end_date = config.get_date_filter()
        date_filter_works = (
            isinstance(start_date, str)
            and isinstance(end_date, str)
            and len(start_date) == 10
            and len(end_date) == 10
        )

        results["date_filter_method"] = date_filter_works

        if date_filter_works:
            logger.info(f"✓ get_date_filter works: {start_date} to {end_date}")
        else:
            logger.error("✗ get_date_filter method not working correctly")

    except Exception as e:
        results["date_filter_method"] = False
        logger.error(f"✗ Date filter method verification failed: {e}")

    # Test 3: Required configuration attributes exist
    try:
        config = PipelineConfig()

        required_attributes = [
            "DEV_MODE",
            "MAX_DAYS_LOOKBACK",
            "SAMPLE_RATE",
            "PROCESSED_DATA_DIR",
            "LOCAL_CACHE_DIR",
        ]

        attributes_exist = all(hasattr(config, attr) for attr in required_attributes)
        results["config_attributes"] = attributes_exist

        if attributes_exist:
            logger.info("✓ All required configuration attributes exist")
            logger.info(f"  - DEV_MODE: {config.DEV_MODE}")
            logger.info(f"  - MAX_DAYS_LOOKBACK: {config.MAX_DAYS_LOOKBACK}")
            logger.info(f"  - SAMPLE_RATE: {config.SAMPLE_RATE}")
        else:
            missing = [
                attr for attr in required_attributes if not hasattr(config, attr)
            ]
            logger.error(f"✗ Missing configuration attributes: {missing}")

    except Exception as e:
        results["config_attributes"] = False
        logger.error(f"✗ Configuration attributes verification failed: {e}")

    return results


def generate_verification_report(all_results: Dict[str, Dict[str, bool]]) -> None:
    """
    Generate a comprehensive verification report.

    Args:
        all_results: Dictionary of verification results by category.
    """
    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info("VERIFICATION REPORT SUMMARY")
    logger.info("=" * 60)

    total_tests = 0
    passed_tests = 0

    for category, results in all_results.items():
        category_total = len(results)
        category_passed = sum(results.values())
        total_tests += category_total
        passed_tests += category_passed

        logger.info(
            f"{category.upper()}: {category_passed}/{category_total} tests passed"
        )

        # Show failed tests
        failed_tests = [test for test, passed in results.items() if not passed]
        if failed_tests:
            logger.warning(f"  Failed tests: {', '.join(failed_tests)}")

    logger.info("-" * 60)
    logger.info(
        f"OVERALL: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)"
    )

    if passed_tests == total_tests:
        logger.info("🎉 ALL VERIFICATION TESTS PASSED!")
        logger.info("The implementation meets all SPEC PROMPT requirements.")
    else:
        logger.warning("⚠️  Some verification tests failed.")
        logger.warning("Please review the failed tests and fix the issues.")

    logger.info("=" * 60)


def main() -> None:
    """Main verification function."""
    logger = setup_verification_logging()

    logger.info("Starting verification of Basic REV Query & ETL Implementation")
    logger.info("This script validates compliance with the SPEC PROMPT requirements")

    # Run all verification tests
    all_results = {
        "file_structure": verify_file_structure(),
        "rev_queries": verify_rev_queries_module(),
        "etl_module": verify_etl_module(),
        "configuration": verify_configuration_integration(),
    }

    # Generate comprehensive report
    generate_verification_report(all_results)


if __name__ == "__main__":
    main()
