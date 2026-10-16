"""RSI zone entries with a fixed bracket, hourly bars: from flat, RSI 14 between 18 and 27 goes long, between 68 and 80
goes short; each trade has a target and a stop (in ticks, re-expressed as ATR multiples).
Port of FMZ strategy #429509 "Algorithm-RSI区间突破策略Algorithm-RSI-Range-Breakout-Strategy" (BTC/USD - RSI).

FMZ source id: 429509

Source
    https://www.fmz.com/strategy/429509 (PineScript v5, FMZ last modified 2023-10-17 17:14:09).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 187-226), RSI 14, buy 27 / 18, sell 68 / 80, target 2500 / stop 5000 ticks
    flat and 18 < rsi <= 27 -> entry long; flat and 68 <= rsi < 80 -> entry short
    (the nested level-2 entries need rsi <= 18 inside rsi > 18: they never fire)
    exit(profit = 2500, loss = 5000) per side

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: 2500 / 5000 ticks of 0.1 on hourly BTC (250 / 500 USD) are about 1.7 / 3.3 x Wilder
      ATR(14) of the signal bar (tp_atr / sl_atr, shifted one bar inside stops(), re-based on the fill).
    * Entries only from flat: "flat" follows the house bracket on bars. Opposite entries cannot occur.
      Stop module: portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick distances -> ATR multiples.
    3 crypto-exchange-only: no ("BTC/USD" in the title only; exchange pair in the header).
    4 signals only: the lot input stored; the bracket quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_429509_rsi_zone_bracket"
FAMILY = "rsi_oscillator"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_atr": [1.7, 3.0],
    "sl_atr": [3.3, 1.5],
}
DEFAULT_PARAMS = {"length": 14, "buy1": 27, "buy2": 18, "sell1": 68, "sell2": 80, "tp_atr": 1.7, "sl_atr": 3.3,
                  "atr_length": 14}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _frac(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    return _rma(tr, n) / c


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    r = _rsi(bars_df["close"], int(p["length"]))
    lc = ((r <= p["buy1"]) & (r > p["buy2"])).to_numpy()
    sc = ((r >= p["sell1"]) & (r < p["sell2"])).to_numpy()
    fr = _frac(bars_df, int(p["atr_length"])).to_numpy()
    ov, hv, lv = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, s_, t_ = 0, -1, np.nan, np.nan
    for i in range(m):
        if pos != 0 and i >= entry_i:                    # house bracket from the fill price
            e = ov[entry_i]
            if pos == 1 and (lv[i] <= e * (1 - s_) or hv[i] >= e * (1 + t_)):
                pos = 0
            elif pos == -1 and (hv[i] >= e * (1 + s_) or lv[i] <= e * (1 - t_)):
                pos = 0
        if pos == 0 and not np.isnan(fr[i]):
            if lc[i]:
                le[i], pos, entry_i = True, 1, i + 1
            elif sc[i]:
                se[i], pos, entry_i = True, -1, i + 1
            s_, t_ = p["sl_atr"] * fr[i], p["tp_atr"] * fr[i]
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    fr = _frac(bars_df, int(p["atr_length"]))
    return {"sl_stop": (p["sl_atr"] * fr).shift(1), "tp_stop": (p["tp_atr"] * fr).shift(1)}


def portfolio_kwargs(**params):
    return {}
