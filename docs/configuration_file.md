# Configuration File

[![README](icons/readme.png) README](README.md)

---

The `config.json` configuration file manages the behavior of the **Process Governor** application. This file allows
users to define rules for regulating process priorities, I/O priorities, and CPU core affinity, as well as manage
services with similar settings.

The application regularly checks the configuration file for changes and applies the updates accordingly.

---
## Configuration File Example

Below is an example of the configuration file with several rules defined for processes and services:

<details>
    <summary>See an example</summary>

```json
{
  "ruleApplyIntervalSeconds": 1,
  "processRules": [
    {
      "selectorBy": "Name",
      "selector": "aida_bench64.dll",
      "force": "N"
    },
    {
      "selectorBy": "Name",
      "selector": "bg3*.exe",
      "affinity": "0-15",
      "force": "N",
      "delay": "30"
    },
    {
      "selectorBy": "Name",
      "selector": "logioptionsplus_*.exe",
      "priority": "Idle",
      "ioPriority": "Low",
      "affinity": "0-15",
      "force": "N"
    },
    {
      "selectorBy": "Name",
      "selector": "discord.exe",
      "priority": "Normal",
      "affinity": "0-15",
      "force": "Y"
    },
    {
      "selectorBy": "Name",
      "selector": "audiodg.exe",
      "priority": "Realtime",
      "affinity": "16-23",
      "force": "N"
    },
    {
      "selectorBy": "Name",
      "selector": "*",
      "affinity": "0-15",
      "force": "N"
    }
  ],
  "serviceRules": [
    {
      "priority": "Realtime",
      "selector": "*audio*",
      "force": "N"
    }
  ],
  "version": 3
}
```
</details>

---

## Structure of the `config.json`

The configuration file contains several sections, each serving a specific purpose.

### `ruleApplyIntervalSeconds`

This parameter defines the interval, in seconds, at which the application applies the rules to processes and services.
The default value is `1`, meaning rules are applied every second.

### `processRules`

This section lists the rules applied to processes. Each rule object specifies how the application should manage a
process based on several key parameters:

#### Possible parameters:

- **`selectorBy`** (string): Determines how the `selector` value is interpreted for process matching.  
  **Valid values:**
    - `"Name"`: Match by process name (e.g., `"notepad.exe"`).
    - `"Path"`: Match by full executable path (e.g., `"C:/Windows/System32/notepad.exe"`).
    - `"Command line"`: Match by command line (e.g., `"App.exe Document.txt"`).


- **`selector`** (string): Specifies the name, pattern, or path to the process. 
  **Supported wildcards:**
    - `*`: Matches any number of characters.
    - `?`: Matches a single character.
    - `**`: Matches any sequence of directories.

  **Examples:**
    - `"selector": "name.exe"`
    - `"selector": "logioptionsplus_*.exe"`
    - `"selector": "C:/Program Files/**/app.exe --file Document.txt"`


- **`priority`** (string, optional): Sets the priority level of the process.  
  **Valid values:**
    - `"Idle"`
    - `"BelowNormal"`
    - `"Normal"`
    - `"AboveNormal"`
    - `"High"`
    - `"Realtime"`

  **Example:** `"priority": "High"`


- **`ioPriority`** (string, optional): Sets the I/O priority of the process.  
  **Valid values:**
    - `"VeryLow"`
    - `"Low"`
    - `"Normal"`

  **Example:** `"ioPriority": "Low"`


- **`affinity`** (string, optional): Sets the CPU core affinity for the process.  
  **Formats:**
    - Range (inclusive): `"affinity": "0-3"`
    - Specific cores: `"affinity": "0;2;4"`
    - Combination: `"affinity": "1;3-5"`


- **`force`** (string, optional): Forces the application of the settings.  
  **Valid values:**
    - `"Y"` for continuous enforcement.
    - `"N"` for one-time application.


- **`delay`** (integer, optional): Delay in seconds before applying the settings.  
  **Examples:**
    - If not specified, the settings are applied immediately.
    - Positive values set a delay in seconds before applying the settings.

### `serviceRules`

This section contains a list of rules applied to services. Unlike `processRules`, the **Service Rule** does not include
the `selectorBy` field because service rules only match by service name using the `selector` field.

#### Possible parameters:

- **`selector`** (string): Specifies the name or pattern of the service to match.  
  **Supported wildcards:**
    - `*`: Matches any number of characters.
    - `?`: Matches a single character.

  **Examples:**
    - `"selector": "ServiceName"`
    - `"selector": "*audio*"`

Other parameters such as `priority`, `ioPriority`, `affinity`, `force`, and `delay` are similar to those
in `processRules`.

### `version`

This field specifies the version of the configuration. It is required for ensuring proper migration and updates when the
program configuration changes over time.

---

## Validation

The configuration file undergoes validation to ensure consistency and correctness. If there are any issues, such as
invalid parameter combinations or missing required fields, the application will notify the user and prevent the
configuration from being applied until the errors are resolved.