"""Simple PySpark data processing example.

This script reads a CSV file, applies basic transformations, and writes results as Parquet.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as spark_sum, count as spark_count


def run(input_path: str = "data/sample.csv", output_path: str = "output") -> None:
    spark = SparkSession.builder.appName("pyspark-data-processing").getOrCreate()

    # Read input data (CSV with header)
    df = (
        spark.read
        .option("header", "true")
        .option("inferSchema", "true")
        .csv(input_path)
    )

    # Basic schema expectations (transactions):
    #  - transaction_id: integer
    #  - date: string
    #  - category: string
    #  - amount: double

    # 1) Filter to transactions with amount > 20
    filtered = df.filter(col("amount") > 20)

    # 2) Compute per-category aggregates
    summary = (
        filtered.groupBy("category")
        .agg(
            spark_count("transaction_id").alias("transaction_count"),
            spark_sum("amount").alias("total_amount"),
        )
        .orderBy(col("total_amount").desc())
    )

    # Show results on console
    print("=== Transaction summary (amount > 20) ===")
    summary.show(truncate=False)

    # Write output as Parquet files (default: overwrite existing)
    summary.write.mode("overwrite").parquet(output_path)

    print(f"Wrote results to: {output_path}")

    spark.stop()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run PySpark data processing")
    parser.add_argument("--input", default="data/sample.csv", help="Input CSV path")
    parser.add_argument("--output", default="output", help="Output directory")
    args = parser.parse_args()

    run(input_path=args.input, output_path=args.output)
