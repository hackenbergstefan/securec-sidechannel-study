# Signal-to-Noise Ratio


> Signal-to-noise ratios are commonly used in electrical engineering and signal processing. An SNR is tbe ratio between tbe signal and tbe noise component of a measurement. The general definition of an SNR in a digital environment is given in (4.9).
> $$ SNR = \frac{Var(Signal)}{Var(Noise)} $$

(Mangard S., Oswald E., Popp T. Power Analysis Attacks.. Revealing the Secrets of Smart Cards (Advances in Information Security) (2007) 4.3.2)

For precise computation refer to [Advanced side-channel Measurement and Testing](https://hss-opus.ub.ruhr-uni-bochum.de/opus4/frontdoor/deliver/index/docId/8024/file/diss.pdf) (Formula 5.5).

$$ \mathrm{SNR} = \frac{
    \mathrm{Var}_{\forall k \in \mathcal S}(\mathbf{\bar x}_k)
}{
    \mathrm{E}_{\forall k \in \mathcal S}\big(\mathrm{Var}_{\forall i}(\mathbf{x}_{k,i})\big)
} $$

## Key recovering

Similar to T-Test we can partition the set of traces into multiple subsets.
But, in contrast we don't have to focus on a single bit.
The entire byte or it's Hamming Weight can be considered.

## Computations and Performance

### Lascar

[./lascar/snr_key](./lascar/snr_key.py).
Using `cw_loop5_fixedkey` with 100.000 traces each of 500 samples we get the following results (i7-1165G7@2.80GHz):

- Single engine:
  | thread_on_update | time |
  |------------------|------|
  | True             | 3.8s |
  | False            | 3.9s |

- Multiple engines:
  | thread_on_update | time  |
  |------------------|-------|
  | True             | 16.6s |
  | False            | 16.1s |
