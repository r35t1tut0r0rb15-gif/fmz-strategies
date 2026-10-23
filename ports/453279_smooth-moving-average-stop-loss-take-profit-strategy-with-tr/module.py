"""Hourly bars, long only: a close under the SMA 200 on below-average volume (SMA 20) and below-average true range (SMA 20) goes long; exactly 3 bars after the latest such signal (if RSI 14 is not over 70 then) a stop 5 % under that signal's close is armed, and an RSI over 70 replaces the order by a +150 % target only; the trade ends at the stop.
Port of FMZ strategy #453279 "Smooth Moving Average Stop Loss Take Profit Strategy with Trend Filter and Exception Exit" (Smooth MA SL & TP with Exception).

FMZ source id: 453279

Source
    https://www.fmz.com/strategy/453279 (PineScript v5, FMZ last modified 2024-06-03 16:54:04).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 94-150), TP multiplier 1.5 (+150 %); SL 5 %; wait 3 bars; SMA 200; RSI 14; volume SMA 20; TR SMA 20
    warunek_wejscia = close < sma200 and volume < sma(volume, 20) and tr(true) < sma(tr(true), 20) -> stop_loss := close x 0.95, take_profit := close x 2.5, indeks := bar_index, entry Long
    opentrades != 0: rsi > 70 -> exit(limit = take_profit);  else bar_index - indeks == 3 -> exit(stop = stop_loss, limit = take_profit);  warunek_wyjscia (never true) -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * take_profit = close x (1 + 1.5) is 150 % above the entry (it practically never fills), and the exit
      condition needs close < SMA and close > SMA at once, so it never fires (weird case). The stop
      order exists only from 3 bars after the latest entry signal (if the RSI is not over 70 on that bar)
      and an RSI over 70 later re-sends the exit with the limit only, dropping the stop; the house engine
      cannot arm or drop a stop later, so the signals follow it: a bar whose low reaches the armed stop
      closes the trade at the next open (mark trailing_stop_pending). Entry signals repeat while long and
      re-anchor the levels, as written. Long only. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; late-armed stop followed in the signals.
    2 generic: PASS, quiet-market dips under the SMA 200.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) below its SMA 20 (the low-volume filter); exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_453279_quiet_dip_under_sma200_late_armed_stop_1h_long_only"
FAMILY = "pullback_time_exit"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sl_percent": [5.0, 2.0],
    "wait_bars": [3, 6],
}
DEFAULT_PARAMS = {"tp_multiplier": 1.5, "sl_percent": 5.0, "wait_bars": 3, "sma_period": 200, "rsi_period": 14}


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
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    sma = c.rolling(int(p["sma_period"])).mean()
    rsi = _rsi(c, int(p["rsi_period"])).to_numpy()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    entry = ((c < sma) & (v < v.rolling(20).mean()) & (tr < tr.rolling(20).mean())).to_numpy()
    cv, hv, lv = c.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    k_sl = 1 - float(p["sl_percent"]) / 100
    k_tp = 1 + float(p["tp_multiplier"])
    wait = int(p["wait_bars"])
    m = len(entry)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend_in, pend_out = 0, False, False
    sig_sl = sig_tp = np.nan
    last_sig = -10 ** 9
    o_sl = o_tp = np.nan                                 # the live exit order's stop / limit
    for i in range(m):
        if pend_in:
            pos, pend_in, o_sl, o_tp = 1, False, np.nan, np.nan
        if pend_out:
            pos, pend_out = 0, False
        if pos == 1 and ((not np.isnan(o_sl) and lv[i] <= o_sl) or (not np.isnan(o_tp) and hv[i] >= o_tp)):
            if i + 1 < m:
                lx[i], pend_out = True, True
            o_sl = o_tp = np.nan
            continue
        if entry[i]:
            sig_sl, sig_tp, last_sig = cv[i] * k_sl, cv[i] * k_tp, i
            if pos == 0 and not pend_in and i + 1 < m:
                le[i], pend_in = True, True
        if pos == 1:
            if rsi[i] > 70:
                o_sl, o_tp = np.nan, sig_tp
            elif i - last_sig == wait:
                o_sl, o_tp = sig_sl, sig_tp
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
