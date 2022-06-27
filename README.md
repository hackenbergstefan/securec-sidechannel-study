# Study of side-channel analysis frameworks - Branch Demo

Single example to show how

- Side-channel analysis using **Lascar** works together with
- Capturing traces with **Chipwhisperer** or
- Capturing traces with **ELMO** and
- Visualizing the results in a **Juypter Notebook**.

## Structure

The repository is structured into the following main folders:

- [./capture](./capture)
  Code and tools for capturing side-channel traces.
- [./analyze](./analyze)
  Code and tools for analysis of captured side-channel traces.

  The methods for analysis are implemented and described in Jupyter notebooks.
  Some functionalities are put into separate python files to abstract the heavy lifting which is not relevant for the actual respective analysis.
- [./examples](./examples)
  The C-code under investigation.
  Each folder is understood as Python module and may implement different capture functionalities within it's `__init__.py`.
