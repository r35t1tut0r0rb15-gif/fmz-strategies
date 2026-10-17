"""Closes crossing above the EMA 20 while EMAs 20, 50 and 100 all rise go long; closed when RSI 14 is above 70 or the
close crosses back under the EMA 20, long only, four-hour bars.
Port of FMZ strategy #482502 "多周期均线趋势判断与RSI超买策略-Multi-Period-EMA-Trend-Detection-with-RSI-Overbought-Strategy" (EMA Crossover + RSI Strategy).

FMZ source id: 482502

Source
    https://www.fmz.com/strategy/482502 (PineScript v5, FMZ last modified 2025-02-18 17:50:40).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 100-129), EMA 20 / 50 / 100, RSI 14 (70)
    crossover(close, ema20) and ema20, ema50, ema100 all above their previous values -> entry long
    rsi > 70 or crossunder(close, ema20) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The close is written after the entry: it acts on the position held at the bar's start and never undoes an
      entry on that bar (#430850). State machine; exits emitted only on going flat.
    * Long only. Signal module, no stops. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMAs and an RSI level.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 200 % of equity, quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (long only).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482502_ema20_cross_rising_emas_rsi70_exit_long"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [20, 10],
    "rsi_exit": [70.0, 80.0],
}
DEFAULT_PARAMS = {"fast": 20, "mid": 50, "slow": 100, "rsi_len": 14, "rsi_exit": 70.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


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
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    e1, e2, e3 = (c.ewm(span=int(p[k]), adjust=False).mean() for k in ("fast", "mid", "slow"))
    rising = (e1 > e1.shift(1)) & (e2 > e2.shift(1)) & (e3 > e3.shift(1))
    buy = ((c > e1) & (c.shift(1) <= e1.shift(1)) & rising).to_numpy()
    sell = ((_rsi(c, int(p["rsi_len"])) > p["rsi_exit"]) | ((c < e1) & (c.shift(1) >= e1.shift(1)))).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        start = pos
        if buy[i] and pos != 1:
            le[i], pos = True, 1
        if sell[i] and start == 1 and pos == 1:
            lx[i], pos = True, 0
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false, false.copy()


def portfolio_kwargs(**params):
    return {}
