### Procedure for Local Builds and Hardware Testing

1. **Make changes** in your local repository or branch as needed.

2. **Build the latest image** to reflect your repository's current state:

    ```
    sudo docker build -t tsc001:latest .
    ```

3. **Spin up the container**:

    ```
    sudo docker compose up
    ```