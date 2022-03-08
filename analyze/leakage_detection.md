# Leakage detection

## Experiment 1 - Single leaky bit

Inject single leaky bit by using following capture function:

```python
("cw_sbox_fixedinput", 10_000, lambda: fixeddata, None, lambda: [random.randint(0, 255) & 0xfe, random.randint(0, 255), 0, 0]),
```

### Results

Difference to "cw_sbox_fixedinput":

- CPA: Difference: 0.03 vs 0.10
- SNR: Difference: 0.03 vs 0.10
- T-Test: Difference: 3 vs 25. Exact bit can be detected
