"""Cowabunga trend entries, 1-hour bars, 05:00-16:00 UTC: the close crossing over its EMA 5 with slow and fast stochastics, RSIs, MACD and EMA stacks all bullish goes long, the mirror short; a fixed
target from the entry (tick distance, re-expressed as an ATR multiple); reversing.
Port of FMZ strategy #440509 "Bull Market Tracking System" (Cowabunga System from babypips.com).

FMZ source id: 440509

Source
    https://www.fmz.com/strategy/440509 (PineScript v4, FMZ last modified 2024-01-31 11:01:45).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 118-194), stoch 162 / 48 / 48 and 10 / 3 / 3; RSI 240 and 9; MACD 12 / 26 / 9; EMA 80 / 162, 5 / 10; take profit 1000, stop 0, trail 400 with offset 0; hours 0500-1600
    long = crossover(close, ema5) and in hours and rsi240 <= 80 and k162 >= d and k162 <= 80 and ema80 >= ema162 and rsi9 <= 80 and k10 >= d and k10 <= 80 and macd >= 0 and ema5 >= ema10;  short mirrored (20 levels)
    strategy.exit(profit = 1000, loss = na, trail_points = 400, trail_offset = na) for each side

Interpretation choices (Pine rules in SURVEY_README.md)
    * The hours are read on the UTC bar open: bars opening 05:00-15:00. The 4-hour and 15-minute names
      are the author's; every indicator runs on the chart's bars, as written. The trail has points but
      no offset and places nothing; the stop input 0 is na. Criterion 2: the 1000-tick target is read as
      0.67 ATR(14) of the signal bar (100 USD on BTC with 0.1 ticks against a 1-hour ATR near 150),
      shifted one bar inside stops() and re-based on the fill. strategy.entry reverses: REVERSAL
      INTENDED. Stop module: portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; target fixed at entry.
    2 generic: ADAPT, tick target -> ATR multiple.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: entries on bars opening 05:00-15:00 UTC (bar open time).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440509_cowabunga_ema5_cross_atr_target"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "k_tp": [0.67, 2.0],
    "len4": [162, 81],
}
DEFAULT_PARAMS = {"k_tp": 0.67, "len4": 162, "sk4": 48, "sd4": 48, "len15": 10, "sk15": 3, "sd15": 3,
                  "rsi4": 240, "rsi15": 9, "atr_len": 14, "h_start": 5, "h_end": 16}


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
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def _stoch(bars_df, n, sk, sd):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    st = 100.0 * (c - ll) / (hh - ll).where(hh > ll)
    k = st.rolling(sk).mean()
    return k, k.rolling(sd).mean()


def _setup(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    k4, d4 = _stoch(bars_df, int(p["len4"]), int(p["sk4"]), int(p["sd4"]))
    k, d = _stoch(bars_df, int(p["len15"]), int(p["sk15"]), int(p["sd15"]))
    r4, r15 = _rsi(c, int(p["rsi4"])), _rsi(c, int(p["rsi15"]))
    ema = {n: c.ewm(span=n, adjust=False).mean() for n in (5, 10, 12, 26, 80, 162)}
    hour = bars_df.index.tz_convert("UTC").hour
    sess = pd.Series((hour >= int(p["h_start"])) & (hour < int(p["h_end"])), index=c.index)
    e5 = ema[5]
    longs = (sess & (r4 <= 80) & (k4 >= d4) & (k4 <= 80) & (ema[80] >= ema[162]) & (r15 <= 80)
             & (k >= d) & (k <= 80) & (ema[12] >= ema[26]) & (e5 >= ema[10]))
    shorts = (sess & (r4 >= 20) & (k4 <= d4) & (k4 >= 20) & (ema[80] <= ema[162]) & (r15 >= 20)
              & (k <= d) & (k >= 20) & (ema[12] <= ema[26]) & (e5 <= ema[10]))
    lsig = (c > e5) & (c.shift(1) <= e5.shift(1)) & longs
    ssig = (c < e5) & (c.shift(1) >= e5.shift(1)) & shorts
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    tp = float(p["k_tp"]) * _rma(tr, int(p["atr_len"])) / c
    return lsig.to_numpy(), ssig.to_numpy(), tp


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lsig, ssig, tp_s = _setup(bars_df, p)
    tp = tp_s.to_numpy()
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, t_ = 0, -1, np.nan
    for i in range(m):
        if pos != 0 and i >= entry_i:
            x = ov[entry_i]
            if pos == 1 and hv[i] >= x * (1 + t_):
                pos = 0
            elif pos == -1 and lv[i] <= x * (1 - t_):
                pos = 0
        if i + 1 < m and not np.isnan(tp[i]):
            if lsig[i] and pos != 1:
                le[i], pos, entry_i, t_ = True, 1, i + 1, tp[i]
            elif ssig[i] and pos != -1:
                se[i], pos, entry_i, t_ = True, -1, i + 1, tp[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"tp_stop": _setup(bars_df, p)[2].shift(1)}


def portfolio_kwargs(**params):
    return {}
