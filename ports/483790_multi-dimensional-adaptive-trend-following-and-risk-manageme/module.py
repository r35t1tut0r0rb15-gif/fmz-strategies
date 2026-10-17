"""Closes crossing an ATR-widened 10-bar SMA of highs (lows) in an EMA 50 / 200 trend, 02:00-14:00 UTC, with a 15-bar
cooldown, a tick bracket as ATR multiples and a break-even close-out, 1-hour bars: the close crossing above
SMA(high, 10) + 1.2 ATR with close > EMA 50 > EMA 200 goes long; the mirror goes short.
Port of FMZ strategy #483790 "多维度自适应趋势追踪与风险管理策略-Multi-Dimensional-Adaptive-Trend-Following-and-Risk-Management-Strategy" (Optimized Target Trend Strategy v2).

FMZ source id: 483790

Source
    https://www.fmz.com/strategy/483790 (PineScript v5, FMZ last modified 2025-02-26 09:54:35).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 164-218), length 10, ATR 14 x 1.2, EMA 50 / 200, cooldown 15 bars
    long = crossover(close, sma(high, 10) + 1.2 ATR) and close > ema50 > ema200 and 2 <= hour < 14 and canTrade
    exit(limit = close + 100 ticks, stop = close - 50 ticks - 1.2 ATR) (short mirrored)
    break-even: while long and high >= close + 50 ticks, exit(stop = close + 2 ticks)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Tick distances -> ATR multiples (criterion 2), judged on the author's market (Binance ETH_USDT, 1h, Jan-Feb
      2025: mintick 0.01, ATR(14) about 30 USD): the 100-tick target (1.00 USD) is tp_k = 0.033 ATR, the 50-tick
      extra stop distance (0.50 USD) is 0.017 ATR, the 50-tick break-even trigger 0.017 ATR; the 2-tick buffer is
      negligible and dropped.
    * The bracket is fixed at the signal bar: sl_stop = (atr_mult + 0.017) x ATR / close, tp_stop = tp_k x ATR /
      close, shifted one bar inside stops() and re-based on the fill (house rule).
    * The break-even exit is a stop placed ABOVE the current close for a long (below for a short) whenever the bar's
      high reached close + the trigger, so it fills at the next open: a bar-range-checked exit signal at the next open
      (rule 3; as #489638). It is never emitted on an entry-signal bar (the position is not yet held there in Pine).
    * Clock rule (check 9 / C6): `hour` is the bar's open hour in the chart's time zone, UTC on the author's Binance
      chart; the window is 02:00 <= open < 14:00 UTC, as written (no DST: UTC).
    * The cooldown counts bars since the last signal bar (lastTradeBar is set on every entry); entries need more than
      15 bars since it.
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the break-even stop acts as a next-open exit.
    2 generic: PASS, moving averages, ATR and tick distances as ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (an entry window 02:00-14:00 UTC by bar open time, declared above).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483790_sma_band_cross_trend_window_cooldown"
FAMILY = "breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_k": [0.033, 0.066],
    "atr_mult": [1.2, 1.5],
}
DEFAULT_PARAMS = {"session_tz": "UTC", "length": 10, "cooldown": 15, "atr_len": 14, "atr_mult": 1.2,
                  "tp_k": 0.033, "sl_extra_k": 0.017, "be_k": 0.017}


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
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    atr = _atr(bars_df, int(p["atr_len"]))
    atr_v = atr * p["atr_mult"]
    e50, e200 = c.ewm(span=50, adjust=False).mean(), c.ewm(span=200, adjust=False).mean()
    up_l = h.rolling(n).mean() + atr_v
    dn_l = lo.rolling(n).mean() - atr_v
    x_up = (c > up_l) & (c.shift(1) <= up_l.shift(1))
    x_dn = (c < dn_l) & (c.shift(1) >= dn_l.shift(1))
    loc = bars_df.index.tz_convert(p["session_tz"])
    t_ok = np.asarray((loc.hour >= 2) & (loc.hour < 14))
    raw_l = (x_up & (c > e50) & (e50 > e200)).to_numpy() & t_ok
    raw_s = (x_dn & (c < e50) & (e50 < e200)).to_numpy() & t_ok
    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    last = None
    cd = int(p["cooldown"])
    for i in range(m):
        if last is not None and i - last <= cd:
            continue
        if raw_l[i]:
            le[i], last = True, i
        elif raw_s[i]:
            se[i], last = True, i
    be = p["be_k"] * atr
    sig = le | se
    lx = ((h >= c + be).to_numpy() & ~sig)
    sx = ((lo <= c - be).to_numpy() & ~sig)
    idx = bars_df.index
    return tuple(pd.Series(a, index=idx) for a in (le, lx, se, sx))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = (_atr(bars_df, int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": (p["atr_mult"] + p["sl_extra_k"]) * a, "tp_stop": p["tp_k"] * a}


def portfolio_kwargs(**params):
    return {}
