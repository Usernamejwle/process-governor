<a id="document-top"></a>

# Rule Behavior and Tips

[![README](icons/readme.png) README](README.md#documentation)

> [!TIP]  
> Before proceeding, it is recommended to familiarize yourself with [Process Governor UI](ui_process_governor.md).

## Table of Contents

1. [Rule Priority](#rule-priority)
2. Common Rule Usage Tips
    - [Ignoring a Process](#ignoring-a-process)
    - [Rule for All Processes](#rule-for-all-processes)
    - [Disabling Hyperthreading](#disabling-hyperthreading)
    - [Using Delay to Avoid Side Effects](#using-delay-to-avoid-side-effects)
    - [Optimizing for Older or Single-Threaded Games](#optimizing-for-older-or-single-threaded-games)
    - [Fixing Audio Crackling Issues](#fixing-audio-crackling-issues)

## Rule Priority

When applying rules, the program first checks **service rules** and then moves to **process rules**. This means that if
a service matches a rule, it will take precedence. If no matching service rule is found, the program then applies the
first matching process rule.

> [!IMPORTANT]  
> Only the first matching rule is applied, so the order of the rules in the configuration is important.

<p align="right">(<a href="#document-top">back to top</a>)</p>

## Ignoring a Process

To ignore a process without applying any specific settings:

1. Go to the **Process Rules** tab.
2. Add a new rule.
3. Set **Process Selector** to the name of the process you want to ignore (e.g., `someprocess.exe`).
4. Leave all other fields unchanged.

This will ensure that the process is excluded from any modifications by the governor.

<p align="right">(<a href="#document-top">back to top</a>)</p>

## Rule for All Processes

To apply a rule to all processes:

1. Go to the **Process Rules** tab.
2. Add a new rule.
3. Set **Process Selector** to `*` to match all processes.
4. Configure the desired settings (e.g., affinity, priority).
5. Place this rule at the bottom of the list to allow more specific rules to take precedence.

<p align="right">(<a href="#document-top">back to top</a>)</p>

## Disabling Hyperthreading

To limit a process to physical CPU cores and disable the use of hyperthreaded (logical) cores:

1. Go to the **Process Rules** tab.
2. Add a new rule.
3. Set **Process Selector** to the target process.
4. Set **Affinity** to even-numbered cores only (e.g., `0;2;4;6;8;10;12;14`).

This will prevent the process from using hyperthreaded cores, which can be beneficial for certain workloads.

<p align="right">(<a href="#document-top">back to top</a>)</p>

## Using Delay to Avoid Side Effects

For some applications, especially games, applying settings like core affinity immediately upon startup can cause issues.
Adding a delay ensures the process has time to initialize before adjustments are applied.

1. Go to the **Process Rules** tab.
2. Add a new rule.
3. Set **Process Selector** to the game executable (e.g., `bg3.exe`).
4. Set **Affinity** as needed (e.g., `0-15`).
5. Set a **Delay** of around 10 seconds to prevent early changes during startup.

This helps avoid potential problems like sound not working.

<p align="right">(<a href="#document-top">back to top</a>)</p>

## Optimizing for Older or Single-Threaded Games

Older or poorly optimized games that don’t efficiently use multiple cores can stutter if run with the default core
affinity settings. To improve performance:

1. Go to the **Process Rules** tab.
2. Add a new rule.
3. Set **Process Selector** to the game process.
4. Set **Priority** to a higher level (e.g., `AboveNormal` or `High`).
5. Adjust the **Affinity** to exclude CPU core 0 (e.g., `1-15`).

This setup can help distribute the load more effectively and reduce stuttering.

<p align="right">(<a href="#document-top">back to top</a>)</p>

## Fixing Audio Crackling Issues

To address audio crackling or stuttering under high CPU load, it’s recommended to increase the priority of audio-related
processes and services to ensure they have sufficient CPU resources.

### Steps for Optimizing Audio Processes:

1. Go to the **Process Rules** tab.
2. Add a new rule for each audio-related process.
3. Set **Process Selector** to the name of the audio process (e.g., `audiodg.exe`, `voicemeeter8x64.exe`).
4. Set **Priority** to `Realtime` or `High` depending on the process's importance.

### Steps for Optimizing Audio Services:

1. Go to the **Service Rules** tab.
2. Add a new rule for each audio-related service.
3. Set **Service Selector** to the service name (e.g., `AudioSrv`, `AudioEndpointBuilder`).
4. Set **Priority** to `Realtime` or `High`.

This approach prioritizes audio processing over other tasks, preventing interruptions in sound quality during heavy CPU
usage.

### Advanced Setup: Load Distribution Across CPU Cores

For all previously added rules related to audio processes, it is recommended to configure **Affinity** to assign
specific CPU cores dedicated to audio processing tasks. This helps ensure that audio processes have sufficient CPU
resources, minimizing interference from other tasks.

For example, if you have a **16-thread processor with 8 cores**, you can allocate the last 2 cores (threads 12-15) for
audio tasks, while the first 6 cores (threads 0-11) can be reserved for other applications.

#### Steps:

1. For each previously configured audio process rule:
    - Set **Affinity** to the last 2 cores (e.g., threads 12-15) for handling audio processing tasks.

2. After configuring the audio processes, add a new rule for all other processes:
    - Set **Process Selector** to `*`.
    - Set **Affinity** to allocate the remaining CPU cores (e.g., threads 0-11) for non-audio tasks.
    - **Important:** This rule must be placed **last** in the rule list, as it serves as a fallback for any processes
      that are not explicitly defined in previous rules.

> [!WARNING]  
> Avoid modifying the **Affinity** for audio services like **AudioSrv** or **AudioEndpointBuilder**, as this
> may worsen performance. Adjusting the priority for these services is usually sufficient to resolve audio issues such
> as crackling and stuttering.

This configuration helps distribute the CPU load, isolating audio processes to specific cores, ensuring smoother and
more stable sound under high system load.

<p align="right">(<a href="#document-top">back to top</a>)</p>
