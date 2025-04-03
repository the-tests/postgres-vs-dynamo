# Database Performance Comparison: PostgreSQL vs DynamoDB

This repository contains a performance comparison between PostgreSQL and DynamoDB. The goal is to evaluate the strengths and weaknesses of each database under different workloads and use cases.

## Usage

1. Clone the repository:
    ```bash
    git clone git@github.com:the-tests/postgres-vs-dynamo.git
    cd postgres-vs-dynamo
    ```

2. Run docker
    ```bash
    cd docker
    docker compose up -d
    ```

3. Install dependencies:
    ```bash
    cd db_perf_check
    poetry install
    ```

4. Create config
    ```bash
    cp -p config_example.json config.json
    ```

5. Generate data:
    ```bash
    # dynamodb
    python src/db_perf_check/create_data.py dynamo
    # postgres
    python src/db_perf_check/create_data.py postgres
    ```

6. Run benchmarks
    ```bash
    # simply select a single element
    # postgres
    python src/db_perf_check/get_data.py postgres
    # dynamodb
    python src/db_perf_check/get_data.py dynamo
    # update a single record
    # postgres
    python src/db_perf_check/update_data.py postgres
    # dynamodb
    python src/db_perf_check/update_data.py dynamo
    ```

7. Run benchmarks endless in multiple processes
    ```bash
    # to get data
    ./run.sh get [postgres, dynamo] [N - num of procs]
    # to update data
    ./run.sh update [postgres, dynamo] [N - num of procs]
    ```
