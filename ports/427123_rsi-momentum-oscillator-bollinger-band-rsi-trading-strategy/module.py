"""Bollinger and RSI, long only: RSI(14) under 30 with the close under the lower Bollinger band
(20, 2) goes long; RSI above 70 closes it; a 10 % take-profit and a 25 % stop-loss on the entry
price stay in place.
Port of FMZ strategy #427123 "Momentum Oscillator Bollinger Band RSI Trading Strategy".

FMZ source id: 427123

Source
    https://www.fmz.com/strategy/427123 (PineScript v4, FMZ last modified 2023-09-18 14:07:51).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 146-187), RSI 14, BB 20 x 2, TP 10 %, SL 25 %
    entry_long = rsi < 30 and close < sma(close, 20) - 2 x stdev(close, 20) -> entry long
    exit(limit = avg x 1.10, stop = avg x 0.75); rsi > 70 -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The strategy() line is commented out in the source (with pyramiding 50 and
      calc_on_every_tick in it), so the script runs with Pine's defaults: pyramiding 0, bar-close
      evaluation. Entries only from flat: Opposite entries cannot occur (long only).
    * TP / SL are fixed fractions of the entry fill price: tp_stop 0.10, sl_stop 0.25 (stops()).
    * stdev is the population standard deviation (Pine). The BB offset input only shifts the plot.
    * An entry (RSI < 30) and the RSI exit (> 70) cannot fall on one bar.
    * FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the bracket is fixed at entry.
    2 generic: PASS, oscillator levels, a band in standard deviations, stops as fractions of price.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the TP / SL bracket is ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: DG427123 (2 members, with #444357, Jaccard 0.885); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427123_bb_rsi_long"
FAMILY = "bollinger_reversion"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "bb_mult": [2.0, 2.5],
    "tp_pct": [10.0, 3.0],
    "sl_pct": [25.0, 5.0],
}
DEFAULT_PARAMS = {"rsi_length": 14, "bb_length": 20, "bb_mult": 2.0, "tp_pct": 10.0, "sl_pct": 25.0,
                  "rsi_entry": 30, "rsi_exit": 70}


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


def _rsi(close, n):
    """Pine rsi as written in the source: down == 0 ? 100 : up == 0 ? 0 : 100 - 100 / (1 + up / down)."""
    ch = close.diff()
    up = _rma(ch.clip(lower=0), n).to_numpy()
    dn = _rma((-ch).clip(lower=0), n).to_numpy()
    with np.errstate(divide="ignore", invalid="ignore"):
        val = np.where(dn == 0, 100.0, np.where(up == 0, 0.0, 100 - 100 / (1 + up / dn)))
    val[np.isnan(up) | np.isnan(dn)] = np.nan
    return pd.Series(val, index=close.index)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["bb_length"])
    lower = c.rolling(n).mean() - p["bb_mult"] * c.rolling(n).std(ddof=0)
    r = _rsi(c, int(p["rsi_length"]))
    entry = (r < p["rsi_entry"]) & (c < lower)
    exit_ = r > p["rsi_exit"]
    false = pd.Series(False, index=bars_df.index)
    return entry.astype(bool), exit_.astype(bool), false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["tp_pct"] / 100}


def portfolio_kwargs(**params):
    return {}
