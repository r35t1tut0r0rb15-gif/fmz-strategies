"""Upper-band breakouts in an uptrend with rising volatility, 3-hour bars, long only: a close over the upper Bollinger 20 / 2 band, over the parabolic SAR and over the EMA 100, with the ATR 14 over its 100-bar mean, buys (at most 5 signals between exits); a close crossing under the middle band or the SAR sells everything; each trade has a 2 % stop from the fill.
Port of FMZ strategy #458200 "Multi Order Breakout Trend Following Strategy" (Multi-Order Breakout Strategy).

FMZ source id: 458200

Source
    https://www.fmz.com/strategy/458200 (PineScript v5, FMZ last modified 2024-07-30 17:18:11).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 206-258), BB 20, 2; SAR 0.02 / 0.02 / 0.2; EMA 100; ATR 14 vs SMA 100 of it; stop 2 % of the average price; max 5 positions; risk 1 % of equity per trade
    close > upper and close > sar and close > ema100 and open_positions < 5 and atr > sma(atr, 100) -> entry "Long n", open_positions += 1
    every bar: exit("SL n", "Long n", stop = avg x 0.98) for n = 1..5;  crossunder(close, middle) or crossunder(close, sar), open_positions > 0 -> close_all, open_positions = 0

Interpretation choices (Pine rules in SURVEY_README.md)
    * The default pyramiding of 1 lets an entry fill only from flat, so the "multi-order" entries never
      stack: open_positions counts signals, not positions, and after 5 signals without an exit no entry
      is sent until the next close_all resets it. The stop comes from the average (fill) price and is
      sent every bar: ported active from the fill bar (#440797) as the fixed fraction 0.02, and followed
      in the loop (a stop-out leaves the count as it is, as written). close_all acts only on a position
      held into the bar. Pine's ta.sar as documented. The equity-risk quantity is not ported (sizing is
      the optimisation layer's). Long only. Stop module: portfolio_kwargs {} (driver D4). Stops on
      3-hour bars: mark coarse_bar_stop. FREQ = "3h" from the backtest header (UTC-aligned 3-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the fill-price stop as a fixed fraction.
    2 generic: PASS, band breakouts with trend and volatility filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: equity-risk quantity stored, not ported.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_458200_bb_breakout_sar_ema100_atr_rising_signal_count_long"
FAMILY = "bollinger_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "lookback": [20, 50],
    "breakout_mult": [2.0, 1.5],
    "sl_pct": [0.02, 0.04],
}
DEFAULT_PARAMS = {"lookback": 20, "breakout_mult": 2.0, "sl_pct": 0.02, "max_positions": 5,
                  "atr_period": 14, "ma_len": 100}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def _sar(hv, lv, cv, start, inc, mx):
    """Pine's ta.sar as documented (pine_sar)."""
    m = len(cv)
    out = np.full(m, np.nan)
    res = mm = acc = np.nan
    below = None
    for i in range(1, m):
        first = False
        if i == 1:
            if cv[1] > cv[0]:
                below, mm, res = True, hv[1], lv[0]
            else:
                below, mm, res = False, lv[1], hv[0]
            first, acc = True, start
        res = res + acc * (mm - res)
        if below:
            if res > lv[i]:
                first, below = True, False
                res, mm, acc = max(hv[i], mm), lv[i], start
        else:
            if res < hv[i]:
                first, below = True, True
                res, mm, acc = min(lv[i], mm), hv[i], start
        if not first:
            if below:
                if hv[i] > mm:
                    mm, acc = hv[i], min(acc + inc, mx)
            else:
                if lv[i] < mm:
                    mm, acc = lv[i], min(acc + inc, mx)
        if below:
            res = min(res, lv[i - 1])
            if i > 1:
                res = min(res, lv[i - 2])
        else:
            res = max(res, hv[i - 1])
            if i > 1:
                res = max(res, hv[i - 2])
        out[i] = res
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["lookback"])
    middle = c.rolling(n).mean()
    upper = middle + float(p["breakout_mult"]) * c.rolling(n).std(ddof=0)
    sar = pd.Series(_sar(h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float),
                         0.02, 0.02, 0.2), index=c.index)
    ma = c.ewm(span=int(p["ma_len"]), adjust=False).mean()
    atr = _atr(bars_df, p["atr_period"])
    go = ((c > upper) & (c > sar) & (c > ma) & (atr > atr.rolling(100).mean())).to_numpy()
    out = (((c < middle) & (c.shift(1) >= middle.shift(1))) | ((c < sar) & (c.shift(1) >= sar.shift(1)))).to_numpy()
    ov, lv = o.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    sl, mx = float(p["sl_pct"]), int(p["max_positions"])
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend, level, cnt = 0, 0, np.nan, 0
    for i in range(m):
        if pend == 1:
            pos, level = 1, ov[i] * (1 - sl)
        elif pend == 2:
            pos, level = 0, np.nan
        pend = 0
        if pos == 1 and lv[i] <= level:
            pos, level = 0, np.nan               # the stop fills inside this bar
        if go[i] and cnt < mx:
            cnt += 1
            if pos == 0:
                le[i], pend = True, 1            # pyramiding 1: fills only from flat
        if out[i] and cnt > 0:
            cnt = 0
            if pos == 1:
                le[i], lx[i], pend = False, True, 2
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"])}


def portfolio_kwargs(**params):
    return {}
