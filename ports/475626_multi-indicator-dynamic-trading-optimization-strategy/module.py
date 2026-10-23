"""4-hour bars: the average of four inverse-Fisher oscillators (CCI 5, RSI 5, stochastic 5, MFI 5, each WMA 9) crossing over -0.5 goes long and crossing under 0.5 goes short; a 0.5 % stop and 1 % target from position_avg_price are armed only when a signal arrives while a trade is open, followed in the signals; reversing.
Port of FMZ strategy #475626 "Multi Indicator Dynamic Trading Optimization Strategy" (wombocombo (IFTCOMBO)).

FMZ source id: 475626

Source
    https://www.fmz.com/strategy/475626 (PineScript v5, FMZ last modified 2024-12-20 16:31:21).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 100-181), IFT of CCI / RSI / stoch / MFI (5, WMA 9); levels -0.5 / 0.5; SL 0.5 %, TP 1 % of position_avg_price; 100 % of equity
    longCondition = crossover(AVINV, -0.5) -> entry Long, exit('Long Exit', 'Long', stop = position_avg_price x 0.995, limit = position_avg_price x 1.01);  longCloseCondition = crossunder(AVINV, 0.5) -> close Long
    shortCondition = crossunder(AVINV, 0.5) -> entry Short, exit(stop = avg x 1.005, limit = avg x 0.99);  shortCloseCondition = crossover(AVINV, -0.5) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket takes position_avg_price at the signal bar: na when the signal opens a trade from flat
      (no exit exists), the old trade's fill on a reversal bar (the new trade gets levels from the old
      price, as written), the trade's own fill on a repeated signal while it is open. The house engine
      cannot arm a bracket from those prices, so the signals follow it: a bar whose low / high reaches an
      armed level closes the trade at the next open (mark trailing_stop_pending). The close conditions
      are the opposite entries, which reverse. The MFI counts a bar's money flow as up when the hlc3
      change is positive or na, as written; its division by zero is na. REVERSAL INTENDED. 100 % of
      equity is sizing. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; position-price bracket followed in the signals.
    2 generic: PASS, inverse-Fisher oscillator combo crossings of -0.5 / 0.5.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the MFI 5; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view

NAME = "fmz_475626_ift_combo_cci_rsi_stoch_mfi_cross_4h_reversal"
FAMILY = "inverse_fisher"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "level": [0.5, 0.3],
    "wma_len": [9, 5],
}
DEFAULT_PARAMS = {"len": 5, "wma_len": 9, "level": 0.5, "sl": 0.005, "tp": 0.01}


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


def _wma(x, n):
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        w = np.arange(1, n + 1, dtype=float)
        out[n - 1:] = sliding_window_view(v, n) @ w / w.sum()
    return pd.Series(out, index=x.index)


def _cci(x, n):
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        win = sliding_window_view(v, n)
        mean = win.mean(axis=1)
        mad = np.abs(win - mean[:, None]).mean(axis=1)
        with np.errstate(divide="ignore", invalid="ignore"):
            out[n - 1:] = np.where(mad != 0, (v[n - 1:] - mean) / (0.015 * mad), np.nan)
    return pd.Series(out, index=x.index)


def _ift(x):
    return (np.exp(2 * x) - 1) / (np.exp(2 * x) + 1)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    n, w = int(p["len"]), int(p["wma_len"])
    i1 = _ift(_wma(0.1 * (_cci(c, n) / 4), w))
    i2 = _ift(_wma(0.1 * (_rsi(c, n) - 50), w))
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    i3 = _ift(_wma(0.1 * (100 * (c - ll) / (hh - ll) - 50), w))
    src = (h + lo + c) / 3
    chg = src.diff()
    up = (v * src.where(~(chg <= 0), 0.0)).rolling(n).sum()
    dn = (v * src.where(~(chg >= 0), 0.0)).rolling(n).sum()
    mfi = 100.0 - 100.0 / (1.0 + up / dn.where(dn != 0))
    i4 = _ift(_wma(0.1 * (mfi - 50), w))
    av = (i1 + i2 + i3 + i4) / 4
    lv = float(p["level"])
    buy = ((av > -lv) & (av.shift(1) <= -lv)).to_numpy()
    sell = ((av < lv) & (av.shift(1) >= lv)).to_numpy()
    on, hn, ln = o.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    sl, tp = float(p["sl"]), float(p["tp"])
    m = len(on)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    vpos, pine, fp, pend, armed = 0, 0, np.nan, False, None
    for i in range(m):
        held = pine
        if pend:
            fp, pend = on[i], False
        if held != 0 and armed is not None:
            st, lm = armed
            if (held == 1 and (ln[i] <= st or hn[i] >= lm)) or (held == -1 and (hn[i] >= st or ln[i] <= lm)):
                held, armed, fp = 0, None, np.nan
        new, sent = held, None
        if buy[i]:
            new = 1
            sent = (fp * (1 - sl), fp * (1 + tp)) if held != 0 else None
        if sell[i]:
            new = -1
            sent = (fp * (1 + sl), fp * (1 - tp)) if held != 0 else None
        if new != held:
            armed, pend = sent, new != 0
        elif sent is not None:
            armed = sent
        pine = new
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
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
