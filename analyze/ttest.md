# T-Test

## Key recovering

In classical DPA (e.g. [Power Side-Channel Attack Analysis: A Review of 20 Years of Study for the Layman](https://www.mdpi.com/2410-387X/4/2/15) 4.1) a _partition function_ is used to distinguish a set of traces into two distinct partitions.
Primarily the partition function focuses on a single bit of a computed value inside a cryptographic algorithm where a known part (mostly plaintext or ciphertext) collides with the secret key.
By partitioning with different key hypothesis one can "guess" the correct one: It is the partition where the two groups are most different from each other.

Kocher et al. proposed to use the "DoM (Difference of Means)" to compute a "difference" between two partitions.
The T-Test in contrast provides a better success rate [Empirical Comparison of Side Channel Analysis Distinguishers on DES in Hardware](https://www.esat.kuleuven.be/cosic/publications/article-1250.pdf).

## Example: AES SBOX Lookup

Recovering the key from an AES SBOX lookup the following partition function can be used:

```python
sbox(plaintext[i] ^ guess) & (1 << b)
```

Considering the `i`-th byte and the `b`-th bit the total amount of partitions is $16 \cdot 8 \cdot 256 = 32768$.

## Computations and Performance

### Lascar

Lascar uses `self._acc_x_by_partition` to compute T-Test (<https://github.com/Ledger-Donjon/lascar/blob/e27551c4e2f6d5675b582edf6612f52538b93308/lascar/engine/ttest_engine.py#47>).

#### Experiment

[./lascar/ttest_key](./lascar/ttest_key.py).
Using `cw_loop5_fixedkey` with 100.000 traces each of 500 samples we get the following results (i7-1165G7@2.80GHz):

- `main_single_engine`:
  | thread_on_update | time |
  |------------------|------|
  | True             | 4.3s |
  | False            | 4.1s |

- `main_multiple_engines` (20 engines):
  | thread_on_update | time  |
  |------------------|-------|
  | True             | 15.6s |
  | False            | 16.5s |

### Direct numpy implementation

[./numpy/ttest_key.py](./numpy/ttest_key.py).
It is not too hard to implement a T-Test directly in numpy.
But, the result is even worse: For 10 guesses in parallel (`multiprocessing.Pool`) we get 14.6s. What a pity!
