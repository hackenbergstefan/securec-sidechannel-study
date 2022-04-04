# Capture side-channel traces for study purpose

## File format

All traces are recorded as `numpy` array.
Beside the actual trace it is beneficial to store `input`, `random`, and `key`.

`numpy` has the ability to name "columns" in an multi-dimensional array.
This is used to store all components in a single file.

Assume one has captured $n$ traces of $t$ samples each.
For each trace the following data is stored alongside:
An input array of length $m_i$, a key of length $m_k$, and random values of length $m_r$.
Length is always meant to be number of bytes.

Then, the multi-dimensional array is created like:

```python
data = np.zeros(n, dtype=[
    ('trace', 'f8', t),
    ('input', 'u1', mi),
    ('key', 'u1', mk),
    ('random', 'u1', mr),
])
```

In programming short mathematical notation leads to unreadable code.
So, we give more verbose names. In the code

- $n$ is named `num_traces`,
- $t$ is named `num_samples`.

Our subject of study is an AES SBOX lookup.
So, $m_i$, $m_k$, $m_r$ are fixed and won't be referred with variable names at all.

### Accessing data

Data can be accessed with usual numpy array syntax.
For example for `i` in `range(num_traces)` we have:

- `data['trace'].shape == (num_traces, num_samples)`
- `data['trace'][i, :].shape == (num_samples, )`
- `data['input', i][0]`: First byte of input of the `i`th trace

## Sources for traces

Traces can be captured by using the functions defined in this package and the subfolders.

### ChipWhisperer Lite

Our first two sources for traces are [ChipWhisperer Lite ARM](https://www.newae.com/products/NAE-CWLITE-ARM) and [ChipWhisperer Lite XMEGA](https://www.newae.com/products/NAE-CWLITE-XMEGA).
Traces are recorded using [ChipWhisperer python framework](https://github.com/newaetech/chipwhisperer).
As this repository mainly uses Jupyter-Notebooks which are not very handy when using with "real" python code a small abstraction framework was created in context of lectures hold at [HSA](https://www.hs-augsburg.de/): https://github.com/hackenbergstefan/securec

### ELMO side-channel simulator

The second source for traces is [ELMO](https://github.com/sca-research/ELMO).
It consists of two components: an emulator for the ARM M0 architecture and a set of leakage models.

#### How to build ELMO

The binaries [elmo](./elmo/elmo) and [elmohw](./elmo/elmohw) are built for Linux x86_64.
On a different platform use the following instructions to built you own version of Elmo:

1. Clone [ELMO](https://github.com/sca-research/ELMO).
2. Copy [./elmo/elmodefines.h](./elmo/elmodefines.h) to cloned ELMO folder.
3. Build ELMO `make clean elmo`.
4. Copy the generated executable `elmo` to the folder [./elmo](./elmo).
5. Edit the copy of `elmodefines.h` and change the power model to hamming weight model:

   ```diff
   --- a/elmodefines.h
   +++ b/elmodefines.h
   @@ -111,13 +111,13 @@ unsigned long systick_ints;
                           // bus
   //#define FIXEDVSRANDOM
   //#define MASKFLOW
   -#define ENERGYMODEL
   +//#define ENERGYMODEL

   //#define DIFFTRACELENGTH
   #define BINARYTRACES
   //#define MEANCENTRE
   #define POWERTRACES
   -//#define POWERMODEL_HW
   +#define POWERMODEL_HW
   ```

6. Call again `make clean elmo`.
7. Rename the generated executable `elmo` to `elmohw` and copy to folder [./elmo](./elmo).
