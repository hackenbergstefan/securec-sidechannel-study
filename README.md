# Study of side-channel analysis frameworks

This repository contains a study of existing recent side-channel analysis frameworks.

## Resources

We used the following sources for study:

- https://github.com/phonchi/awesome-side-channel-attack
- https://github.com/Ledger-Donjon/lascar
- https://github.com/hackenbergstefan/introduction-sidechannel-chipwhisperer

## Structure

The repository is structured into four main folders:

- [./src](./src)
  The C-code under investigation.
- [./capture](./capture)
  Code and tools for capturing side-channel traces used in this study.
- [./analyse](./analyse)
  Code and tools for analysis of captured side-channel traces.
- [./data](./data)
  The actual side-channel traces.

## Capture

[./capture/README.md](./capture/README.md)

## Analyze

[./analyze/README.md](./analyze/README.md)
