"""RSI 11 oversold buys, 1-hour bars, long only: an RSI under 20 buys; an RSI over 79 sells, as does a close more than 3.5 % over the close of the latest oversold bar.
Port of FMZ strategy #468322 "多周期RSI超卖反转策略-Multi-Timeframe-RSI-Oversold-Reversal-Strategy" (15min oversold gold).

FMZ source id: 468322

Source
    https://www.fmz.com/strategy/468322 (PineScript v5, FMZ last modified 2024-09-26 15:38:20).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 145-198), RSI 11, entry under 20, exit over 79; target 3.5 % over the latest signal close (close test); stop 1.4 % computed, never used; EMA 290 plotted only; 'add more' entry (qty 3) under 98 % of the signal close
    rsi < 20 -> entryPrice = close, entry Long;  rsi > 79 -> close Long;  close > entryPrice x 1.035 -> close Long;  close < entryPrice x 0.98 -> entry 'add more' (qty 3)

Interpretation choices (Pine rules in SURVEY_README.md)
    * entryPrice is re-set on every oversold bar, held or not, so the target follows the latest
      signal close; the stop test is computed but no order uses it. With the default pyramiding of 1 the
      'add more' entry never fills while long (#441137), and when flat it is a second long entry on a
      close under 98 % of the last signal close, as written. The closes act only on a long held into the
      bar. The title names gold and 15 minutes; the backtest header's 1-hour bars are followed. Long
      only. The 3-unit quantity is not ported. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the target is a close test.
    2 generic: PASS, RSI oversold entries with RSI and percent exits.
    3 crypto-exchange-only: no (exchange pair in the header only (gold named in the title)).
    4 signals only: the 3-unit add-on quantity stored, not ported.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_468322_rsi11_oversold_rsi79_or_signal_close_target_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [11, 14],
    "entry_th": [20, 30],
    "tp_pct": [0.035, 0.02],
}
DEFAULT_PARAMS = {"rsi_len": 11, "entry_th": 20, "exit_th": 79, "tp_pct": 0.035}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    r = _rsi(c, int(p["rsi_len"])).to_numpy()
    cv = c.to_numpy(dtype=float)
    th, xt, tp = float(p["entry_th"]), float(p["exit_th"]), float(p["tp_pct"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, ref = 0, np.nan
    for i in range(m):
        go = r[i] < th
        if go:
            ref = cv[i]
        add = cv[i] < ref * 0.98
        cur = pos
        if (go or add) and pos == 0:
            cur = 1
        if pos == 1 and (r[i] > xt or cv[i] > ref * (1 + tp)):
            cur = 0                              # the closes act only on a long held into the bar
        if cur == 1 and pos == 0:
            le[i] = True
        elif cur == 0 and pos == 1:
            lx[i] = True
        pos = cur
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
