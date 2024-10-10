
###Container Based Testing
1. Ensure Docker Container is up and running 
2. **Use `sipyco_rpctool`** to call functions on the motor controller and test your changes:

    ```
    sipyco_rpctool localhost 3256 call <method_name>
    ```

   - Replace `<method_name>` with the desired method to invoke.


### Example Usage

- **List Available Methods**:
  
    ```
    sipyco_rpctool localhost 3256 list-methods
    ```

- **Invoke a Method** (e.g., identify the module):

    ```
    sipyco_rpctool localhost 3256 call module_identify
    ```

### Additional Information

- **Port Details**:
  - The server runs on **port 3255** for communication with the motor controller.
  - The Docker container maps **port 3255** to **port 3256** on the host for testing.

### References

- Docker commands are used for building and deploying the controller system.
- `sipyco_rpctool` is the primary tool for interacting with the motor controller once the server is active.

---

This concludes the guide for using Sipyco with Thorlabs motor controllers. Follow these steps to make local changes, build with Docker, and test hardware interactions effectively.