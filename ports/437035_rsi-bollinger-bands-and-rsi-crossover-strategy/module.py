"""RSI band re-entries outside the Bollinger bands, 10-minute bars: the RSI 14 crossing back over 30 with the close under the lower band (SMA 20 - 2 sigma) goes long, crossing back under 70 with the close over
the upper band goes short; reversing.
Port of FMZ strategy #437035 "博林带RSI交叉策略Bollinger-Bands-and-RSI-Crossover-Strategy" (Bollinger Bands and RSI Strategy).

FMZ source id: 437035

Source
    https://www.fmz.com/strategy/437035 (PineScript v5, FMZ last modified 2023-12-29 16:40:19).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 128-160), BB 20 x 2, RSI 14, levels 70 / 30
    longCondition = crossover(rsi, 30) and close < lower -> entry Long;  shortCondition = crossunder(rsi, 70) and close > upper -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * stdev is the population deviation. Positions end only at the opposite entry. REVERSAL INTENDED. No
      sizing code. FREQ = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger bands and RSI levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437035_bollinger_rsi_reentry"
FAMILY = "bollinger_breakout"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 30],
    "rsi_len": [14, 21],
}
DEFAULT_PARAMS = {"length": 20, "rsi_len": 14, "mult": 2.0, "ob": 70.0, "os": 30.0}


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


def _rsi(c, n):
    d = c.diff()
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    r = _rsi(c, int(p["rsi_len"]))
    r1 = r.shift(1)
    os_, ob = float(p["os"]), float(p["ob"])
    lc = (r > os_) & (r1 <= os_) & (c < basis - dev)
    sc = (r < ob) & (r1 >= ob) & (c > basis + dev)
    false = pd.Series(False, index=bars_df.index)
    return lc, false, sc, false.copy()


def portfolio_kwargs(**params):
    return {}
