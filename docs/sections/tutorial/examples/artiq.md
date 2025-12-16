# Adding Thorlabs T/K-Cube Devices to ARTIQ Device Database

This guide explains how to add Thorlabs T/K-Cube devices to the [ARTIQ device database](https://m-labs.hk/artiq/manual/developing_a_ndsp.html) and configure them for use with ARTIQ experiments.

---

## **Step 1: Set Up Your Device and Controller**

Before configuring the device database:

1. **Connect USB First, Then Power Up**: Always connect the USB cable before powering up the device to prevent it from entering a problematic state.
2. **Start the Controller**: Run the appropriate controller for your Thorlabs Cube device using the `aqctl_thorlabs_cube` command.
Example for different devices:

### **TPZ001 (T-Cube Piezo Controller)**

```bash
$ aqctl_thorlabs_cube -P tpz001 -d /dev/ttyUSBx
```

**Notes**:
- On Windows, the `-d` argument will be of the form `COMx`.
- You can specify the device using its Vendor/Product ID and USB Serial Number with the `hwgrep` URL format:
  ```bash
  -d "hwgrep://<VID>:<PID> SNR=<serial_number>"
  ```

---

## **Step 2: Add Device to the ARTIQ Device Database**

This is an example device setup/configuration.
Modify the `device_db.py` file to include an entry for the Thorlabs device.
For example:

```python
device_db = {
    # Core device configuration

    "core": {
        "type": "local",
        "module": "artiq.coredevice.core",
        "class": "Core",
        "arguments": {
            "host": "192.168.1.100",  # Replace with your core device's IP
        }
    },

    # Thorlabs TPZ001 Controller

    "thorlabs_tpz001": {
        "type": "controller",
        "host": "localhost",         # Replace with the IP of the computer connected to the Thorlabs controller
        "port": 3255,                # Port where the Thorlabs controller listens
        "target": "tpz001",          # Controller target name
        "command": "aqctl_thorlabs_cube -P tpz001 -d /dev/ttyUSB0",
    }
}
```

### Explanation:
- **`type`**: Set to `controller` for remote (non-real-time) devices.
- **`host`**: Set to `localhost` if the controller is running on the same machine, or the IP of the computer connected to the Thorlabs controller.
- **`port`**: TCP port the controller is listening on (`3255` in this example).
- **`target`**: The target name.
- **`command`**: Command to start the controller.

---

## **Notes**

1. **Persistent Device Database**:
   After modifying `device_db.py`, update the ARTIQ master:
   ```bash
   $ artiq_client scan-devices
   ```

2. **Controller State**:
   Ensure the controller is running and listening on the configured port (`aqctl_thorlabs_cube` should still be active).

3. **Troubleshooting**:
   - If the device is unresponsive, ensure USB is connected before power-up.
   - Use `--help` with `aqctl_thorlabs_cube` for detailed command-line options.

---
