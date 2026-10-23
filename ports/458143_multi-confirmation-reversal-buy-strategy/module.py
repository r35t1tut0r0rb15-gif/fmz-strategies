"""Long only, bar size searched: an up bar closing at its 3-bar closing high with RSI 14 above 50, the close above the SMA 10 above the SMA 20 and volume above its 5-bar average goes long; the position closes after 10 bars.
Port of FMZ strategy #458143 "Multi Confirmation Reversal Buy Strategy" (Buy After Dip Strategy (Arbitrary Exit) [nn1]).

FMZ source id: 458143

Source
    https://www.fmz.com/strategy/458143 (PineScript v5, FMZ last modified 2024-07-30 12:06:29).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 169-204), lookback 3; SMA 10 / 20; RSI 14; volume SMA 5; exit 10 bars after the last flat bar
    entryCondition = close > open and close == highest(close, 3) and rsi > 50 and close > sma10 and sma10 > sma20 and volume > sma(volume, 5) -> entry Long
    barssince(position_size == 0) >= 10 -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The source has no backtest header and names no bar size: FREQ = "bar_size_pending"; the bars come
      from the house bar_sizes.build_bars. barssince(position_size == 0) counts from the last flat bar, so
      the close is sent on the 10th bar of the position and fills at the next open. An entry while long adds
      nothing. Long only. No sizing code.

Admission criteria
    1 fits the interface: PASS, bar-close orders; 10-bar time exit.
    2 generic: PASS, breakout bars in an SMA uptrend with RSI and volume confirmation.
    3 crypto-exchange-only: no (no exchange header; no symbol named).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar by the house bar builder) against its SMA 5; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
Long only.

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_458143_dip_buy_breakout_bar_10bar_exit_long_only"
FAMILY = "pullback_time_exit"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "bar_size_pending"  # the source names no bar size (rule 1)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "hold": [10, 20],
    "lookback": [3, 5],
}
DEFAULT_PARAMS = {"lookback": 3, "fast": 10, "slow": 20, "hold": 10}


def precompute(raw_1m_df, symbol_key, **params):
    import bar_sizes                      # the house builder (mining\bar_sizes.py), on the desktop's path
    return bar_sizes.build_bars(raw_1m_df, params["bar_size"])


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
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c, v = bars_df["open"], bars_df["close"], bars_df["volume"]
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    entry = ((c > o) & (c == c.rolling(int(p["lookback"])).max()) & (_rsi(c, 14) > 50) & (c > f) & (f > s)
             & (v > v.rolling(5).mean())).to_numpy()
    k = int(p["hold"])
    m = len(entry)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend, fill = 0, False, -1
    for i in range(m):
        if pend:
            pos, pend, fill = 1, False, i
        if pos == 1 and i - fill + 1 >= k:
            lx[i], pos = True, 0
        elif pos == 0 and not pend and entry[i] and i + 1 < m:
            le[i], pend = True, True
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
