# Study of side-channel analysis frameworks

This repository contains a small study of existing recent side-channel analysis frameworks.

## Resources

The following resources are basis of this work:

- https://github.com/phonchi/awesome-side-channel-attack
- https://github.com/Ledger-Donjon/lascar
- https://github.com/hackenbergstefan/introduction-sidechannel-chipwhisperer

## Scope

### Victim firmware

The author uses for all analysis the same implementation with different security levels.

### Victim hardware

The author used different hardware victims to compare the different analysis methods and their leakage behaviors:

- ChipWhisperer Lite XMEGA
- ChipWhisperer Lite ARM
- ELMO side-channel simulator with different leakage models

### Framework

While there are a few more frameworks performing side-channel analysis the author focuses on `lascar`.

## Topics for further study

- Include more promising frameworks:
  - [Riscure Jlsca](https://github.com/Riscure/Jlsca) (Julia)
  - [Scared](https://gitlab.com/eshard/scared) (Python)
- Include more analysis methods:
  - χ²-Test
  - MIA
  - ...

## Structure

The repository is structured into the following main folders:

- [./capture](./capture)
  Code and tools for capturing side-channel traces used in this study.
- [./analyze](./analyze)
  Code and tools for analysis of captured side-channel traces.

  The methods for analysis are implemented and described in Jupyter notebooks.
  Some functionalities are put into separate python files to abstract the heavy lifting which is not relevant for the actual respective analysis.
- [./examples](./examples)
  The C-code under investigation.
  Each folder is understood as Python module and may implement different capture functionalities within it's `__init__.py`.
