# Starting a Local Server for Thorlabs Application

To start a local server to run the Thorlabs application using the `aqctl_thorlabs_cube` entrypoint script, you need the following components:

1. **Port**: Specify a port for the server to listen on.
2. **Product Identifier**: Provide a valid product identifier (e.g., `ksc101`).
3. **Device Address**: Indicate the address where the hardware is connected (e.g., `/dev/ttyUSB0`).

---

## Command Syntax

The command follows this structure:

```bash
$ aqctl_thorlabs_cube -p [port] -P [product_identifier] -d [device_address]
```

---

## Example Command

Here is an example of starting the server:

```bash
$ aqctl_thorlabs_cube -p 3257 -P ksc101 -d /dev/ttyUSB0
```

- **`aqctl_thorlabs_cube`**: The entrypoint script for the Thorlabs controller.
- **`-p 3257`**: The server listens on port `3257`.
- **`-P ksc101`**: The product identifier for the Thorlabs device (e.g., `ksc101` for a stepper motor controller).
- **`-d /dev/ttyUSB0`**: The system address where the hardware is connected (e.g., `/dev/ttyUSB0` for Linux).

---

## Key Points

1. **Virtual Environment**: Ensure you activate your Python virtual environment if required before running the command.
   ```bash
   $ source venv/bin/activate
   ```
2. **Port Availability**: Make sure the specified port (e.g., `3257`) is available and not used by another application.
3. **Device Connection**: Verify the hardware is connected and accessible via the specified address (e.g., `/dev/ttyUSB0`).

---

## Supported Device Drivers

The following are the currently supported device drivers. These are the strings to use with the `-P` flag:

- `tdc001` (T-Cube DC Servo Driver)
- `kdc101` (K-Cube DC Servo Motor Driver)
- `tpa101` (T-Cube Piezo Actuator Driver)
- `kpa101` (K-Cube Piezo Actuator Driver)
- `tpz001` (T-Cube Piezo Controller)
- `kpz101` (K-Cube Piezo Controller)
- `tsc001` (T-Cube Stepper Controller)
- `ksc101` (K-Cube Stepper Controller)

---

With this setup, the local server should start successfully, allowing you to communicate with the Thorlabs device using SiPyCo's RPC or ARTIQ.
