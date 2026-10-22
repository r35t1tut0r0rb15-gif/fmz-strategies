"""RSI 14 re-entries from extremes, 1-hour bars: the RSI crossing back over 31 (after a dip under 30) goes long, back under 69 (after a rise over 70) goes short; a close 1000 ticks (100 price units, 0.00238 at BTC 42000) beyond the fill price in profit closes; reversing.
Port of FMZ strategy #458057 "RSI-反转交叉动量盈利目标量化交易策略-RSI-Reversal-Cross-Momentum-Profit-Target-Quantitative-Trading-Strategy" (1H RSI Reversal Scalping Bot with Profit Target).

FMZ source id: 458057

Source
    https://www.fmz.com/strategy/458057 (PineScript v5, FMZ last modified 2024-07-29 15:56:41).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 192-249), RSI 14; levels 30 / 70, entry 31 / 69; profit target 2000 USD at 2 lots (pointvalue 1) = 1000 ticks
    crossover(rsi, 31) and valuewhen(crossunder(rsi, 30), rsi, 0) < 31 -> entry Long (qty 2);  crossunder(rsi, 69) and valuewhen(crossover(rsi, 70), rsi, 0) > 69 -> entry Short
    long and close >= avg + 1000 ticks -> close Long;  short and close <= avg - 1000 ticks -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The valuewhen tests always hold once an extreme has occurred (the RSI is under 30 at its own
      crossunder). The profit target is 2000 / (pointvalue 1 x 2 lots) = 1000 ticks = 100 at the 0.1
      tick, a price amount read against BTC near 42000 (#440456) as 0.00238 of the fill; it is a
      bar-close test against the fill price, followed in a loop and filled at the next open; there is
      no stop. REVERSAL INTENDED. The 2 lots are sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the profit target is a close test against the fill.
    2 generic: PASS, RSI re-entries from extremes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the trade size stored.
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

NAME = "fmz_458057_rsi_extreme_reentry_close_profit_target_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [14, 7],
    "target_frac": [0.00238, 0.01],
}
DEFAULT_PARAMS = {"rsi_len": 14, "target_frac": 0.00238}


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
    return 100 - 100 / (1 + up / dn)


def _last_value(cond, src):
    out = np.full(len(src), np.nan)
    v = np.nan
    for i in range(len(src)):
        if cond[i]:
            v = src[i]
        out[i] = v
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    r = _rsi(c, int(p["rsi_len"]))
    rv = r.to_numpy()
    dn30 = ((r < 30) & (r.shift(1) >= 30)).to_numpy()
    up70 = ((r > 70) & (r.shift(1) <= 70)).to_numpy()
    with np.errstate(invalid="ignore"):
        buy = ((r > 31) & (r.shift(1) <= 31)).to_numpy() & (_last_value(dn30, rv) < 31)
        sell = ((r < 69) & (r.shift(1) >= 69)).to_numpy() & (_last_value(up70, rv) > 69)
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    f = float(p["target_frac"])
    m = len(cv)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, pend, avg = 0, 0, np.nan
    for i in range(m):
        if pend in (1, -1):
            pos, avg = pend, ov[i]
        elif pend == 2:
            pos = 0
        pend = 0
        cur = pos
        if buy[i] and cur != 1:
            cur = 1
        if sell[i] and cur != -1:
            cur = -1
        if pos == 1 and cur == 1 and cv[i] >= avg * (1 + f):
            cur = 0
        if pos == -1 and cur == -1 and cv[i] <= avg * (1 - f):
            cur = 0
        if cur == 1 and pos != 1:
            le[i] = True
        elif cur == -1 and pos != -1:
            se[i] = True
        elif cur == 0 and pos == 1:
            lx[i] = True
        elif cur == 0 and pos == -1:
            sx[i] = True
        if cur != pos:
            pend = 2 if cur == 0 else cur
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
