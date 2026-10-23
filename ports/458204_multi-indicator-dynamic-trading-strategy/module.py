"""Hourly bars: the EMA 34 crossing over the EMA 89 with RSI 14 above 30 goes long, crossing under with RSI below 70 goes short; a position closes at the next open after a bar with volume over 3 x its 20-bar average, after its 15th bar, or after a bar that touches the previous bar's EMA 34 (the re-sent EMA 34 stop, followed in the signals); reversing.
Port of FMZ strategy #458204 "Multi Indicator Dynamic Trading Strategy" (EMA & RSI Strategy).

FMZ source id: 458204

Source
    https://www.fmz.com/strategy/458204 (PineScript v5, FMZ last modified 2024-07-30 17:29:59).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 170-316), EMA 34 / 89; RSI 14 > 30 / < 70; volume SMA 20 x 3; 15-bar exit; EMA 34 stop
    longCondition = crossover(ema34, ema89) and rsi > 30 -> entry Long;  shortCondition = crossunder(ema34, ema89) and rsi < 70 -> entry Short
    opentrades.entry_id(0) == "Long" and volume > 3 x sma(volume, 20): takeProfitPriceLong := stopLossPriceLong := close -> exit(limit = stop = that close)
    barsSinceEntryLong counts bars held from the signal; >= 15 and not closed -> close Long
    opentrades.entry_id(0) == "Long" -> exit("Stop Loss Long", stop = ema34) every bar (short mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The high-volume exit sends a limit and a stop at that bar's close: one of the two is always met at
      the next open, so it is a close at the next open (exact). The bar count starts at 0 on the signal
      bar and adds 1 on each bar the trade is open, so the close is sent on the 15th held bar. The EMA 34
      stop is re-sent every bar from the bar after the fill: it is followed in the signals, a bar whose
      low (high for shorts) reaches the previous bar's EMA 34 closing the trade at the next open, not at
      the level (trailing_stop_pending). Closes act only on a position the bar's entries leave unchanged;
      an opposite entry reverses. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; EMA 34 stop followed in the signals.
    2 generic: PASS, EMA 34 / 89 crossings with RSI filter, volume and time exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against 3 x its SMA 20 as an exit; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_458204_ema34_89_cross_rsi_volume_15bar_ema_stop_1h_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "hold": [15, 30],
    "vol_mult": [3.0, 2.0],
}
DEFAULT_PARAMS = {"fast": 34, "slow": 89, "hold": 15, "vol_mult": 3.0}


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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    r = _rsi(c, 14)
    buy = ((f > s) & (f.shift(1) <= s.shift(1)) & (r > 30)).to_numpy()
    sell = ((f < s) & (f.shift(1) >= s.shift(1)) & (r < 70)).to_numpy()
    hv = (v > float(p["vol_mult"]) * v.rolling(20).mean()).to_numpy()
    ema_prev = f.shift(1).to_numpy(dtype=float)
    hn, ln = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    k = int(p["hold"])
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    vpos, held_prev = 0, 0
    cnt_l = cnt_s = None
    done_l = done_s = False
    for i in range(m):
        held = vpos
        if held == 1 and held_prev == 1 and ln[i] <= ema_prev[i]:
            held = 0                       # the EMA 34 stop sent at the previous close is touched
        elif held == -1 and held_prev == -1 and hn[i] >= ema_prev[i]:
            held = 0
        new = held
        if buy[i] and new != 1:
            new = 1
        if sell[i] and new != -1:
            new = -1
        if buy[i]:
            cnt_l, done_l = 0, False
        if sell[i]:
            cnt_s, done_s = 0, False
        if held == 1 and cnt_l is not None:
            cnt_l += 1
        if held == -1 and cnt_s is not None:
            cnt_s += 1
        time_l = held == 1 and cnt_l is not None and cnt_l >= k and not done_l
        time_s = held == -1 and cnt_s is not None and cnt_s >= k and not done_s
        done_l, done_s = done_l or time_l, done_s or time_s
        if new == held:
            if held == 1 and (hv[i] or time_l):
                new = 0
            elif held == -1 and (hv[i] or time_s):
                new = 0
        if new != vpos and i + 1 < m:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif vpos == 1:
                lx[i] = True
            else:
                sx[i] = True
            vpos = new
        held_prev = held
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
