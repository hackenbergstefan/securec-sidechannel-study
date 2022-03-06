# Correlation Power Analysis

Introduction:

- [ChipWhisperer Course](https://chipwhisperer.readthedocs.io/en/latest/tutorials/courses_sca101_soln_lab%204_2%20-openadc-cwlitearm.html#tutorial-courses-sca101-soln-lab-4-2-openadc-cwlitearm)
- [Power Side-Channel Attack Analysis: A Review of 20 Years of Study for the Layman](https://www.mdpi.com/2410-387X/4/2/15)

## Key recovering

## Computations and Performance

### Lascar

[./lascar/cpa_key](./lascar/cpa_key.py).
Lascar's `CpaEngine` used by default a selection function which takes `value` and `guess`.
So, there is no difference between single guess and all guesses simultaneously.
Using `cw_loop5_fixedkey` with 100.000 traces each of 500 samples we get the following results (i7-1165G7@2.80GHz):

| thread_on_update | time |
|------------------|------|
| True             | 5.1s |
| False            | 5.3s |

### SecureC

[./chipwhisperer/cpa_key](./chipwhisperer/cpa_key.py).
Optimized implementation using `numpy.einsum` where all guesses are process in one step.
Using `cw_loop5_fixedkey` with 100.000 traces each of 500 samples we get the following results (i7-1165G7@2.80GHz):

2.4s
