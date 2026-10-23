"""Hourly bars: the low crossing over the SMA 50 minus 1 ATR 20 on volume above 1.5 x its 50-bar average goes long, the high crossing under it on such volume goes short; a long closes when the close falls under the previous low, a short when the close rises over the previous high; reversing.
Port of FMZ strategy #458177 "ATR和交易量结合的动态信号线趋势跟踪策略-Dynamic-Signal-Line-Trend-Following-Strategy-Combining-ATR-and-Volume" (Buy and Sell Strategy with ATR and Volume).

FMZ source id: 458177

Source
    https://www.fmz.com/strategy/458177 (PineScript v5, FMZ last modified 2024-07-30 16:01:40).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 176-216), SMA 50; ATR 20; signal line = SMA - 1 x ATR; volume SMA 50 x 1.5
    buy_condition = crossover(low, signal_line) and volume > avg_volume * 1.5 -> entry Buy;  sell_condition = crossunder(high, signal_line) and volume > avg_volume * 1.5 -> entry Sell
    position_size > 0 and close < low[1] -> close Buy;  position_size < 0 and close > high[1] -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The closes test the position held at the bar's close, so they act from the bar after the fill and
      only on a position the bar's entries leave unchanged; an opposite entry reverses (later call wins
      on a two-sided bar). ta.atr is Wilder's RMA of the true range (high - low on the first bar).
      REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, signal-line crossings of the low / high on high volume.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against 1.5 x its SMA 50; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_458177_atr_signal_line_cross_volume_prev_bar_exit_1h_reversal"
FAMILY = "channel_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [50, 100],
    "offset": [1, 2],
}
DEFAULT_PARAMS = {"length": 50, "atr_len": 20, "offset": 1, "vol_mult": 1.5}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    n = int(p["length"])
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    sig = c.rolling(n).mean() - _rma(tr, int(p["atr_len"])) * int(p["offset"])
    vol_ok = v > v.rolling(n).mean() * float(p["vol_mult"])
    buy = ((lo > sig) & (lo.shift(1) <= sig.shift(1)) & vol_ok).to_numpy()
    sell = ((h < sig) & (h.shift(1) >= sig.shift(1)) & vol_ok).to_numpy()
    ex_l = (c < lo.shift(1)).to_numpy()
    ex_s = (c > h.shift(1)).to_numpy()
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        new = pos
        if buy[i] and new != 1:
            new = 1
        if sell[i] and new != -1:
            new = -1
        if new == pos:
            if pos == 1 and ex_l[i]:
                new = 0
            elif pos == -1 and ex_s[i]:
                new = 0
        if new != pos:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif pos == 1:
                lx[i] = True
            else:
                sx[i] = True
            pos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
