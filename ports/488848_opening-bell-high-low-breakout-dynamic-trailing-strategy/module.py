"""08:30 opening-candle breakout, one trade a day, with a close-checked tick trail and a bracket, 5-minute bars: the
08:30 bar's high and low are recorded; between 08:40 and 15:00 the first close above the high goes long (below the
low goes short); a close that falls a few ticks below its best close closes the trade; a wide stop and a small target
are placed with the entry.
Port of FMZ strategy #488848 "早盘高低点突破动态追踪策略-Opening-Bell-High-Low-Breakout-Dynamic-Trailing-Strategy" (Breakout of 8:30 AM High/Low).

FMZ source id: 488848

Source
    https://www.fmz.com/strategy/488848 (PineScript v5, FMZ last modified 2025-03-31 11:21:39).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 190-276), 08:30 candle, trading 08:40-14:59, trail 15 ticks, TP 30 ticks, SL 100 (price)
    the 08:30 bar sets high830 / low830; a new weekday (or 00:00) resets tradeTakenToday
    long = close > high830 and in time and not taken -> entry + exit(stop = close - 100, limit = close + 30 ticks);
    trail = max(trail, close - 15 ticks) from the entry close; close <= trail -> close long (shorts mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Session open (check 9 / C6): 08:30 / 08:40 / 15:00 are clock times in the chart's time zone: UTC on the author's
      Binance chart (session_tz "UTC", the default), or the evident US open, 08:30 America/Chicago (DST by the zone),
      the grid's second reading. The day reset is the chart time zone's weekday change.
    * Criterion 2: on the author's 5-minute ETH_USDT (tick 0.01, 5-minute ATR about 5) 15 / 30 ticks are about
      0.03 / 0.06 ATR(14) and the 100-price-unit stop about 20 ATR (judgement before any backtest): the trail and the
      target as ATR multiples of the current / signal bar.
    * The trail is close-checked: a close-based exit signal (rule 2 / 3), no mark; the bracket from the signal bar
      (sl_stop / tp_stop, shifted one bar inside stops(), re-based on the fill).
    * Every signal bar is an entry (one a day); entries reverse only across days (REVERSAL INTENDED).
    * Stop module: portfolio_kwargs {} (D4). FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders and close-checked trail; bracket fixed at the signal bar.
    2 generic: ADAPT, tick / price distances -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: 08:30 candle, entries 08:40-15:00 in session_tz (UTC as written; America/Chicago, DST by the zone, as the variant).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_488848_0830_candle_breakout_tick_trail"
FAMILY = "momentum_breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "session_tz": ["UTC", "America/Chicago"],
    "trail_atr": [0.03, 0.5],
}
DEFAULT_PARAMS = {"session_tz": "UTC", "trail_atr": 0.03, "tp_atr": 0.06, "sl_atr": 20.0, "atr_len": 14}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    loc = bars_df.index.tz_convert(p["session_tz"])
    hr, mn, wd = loc.hour.to_numpy(), loc.minute.to_numpy(), loc.dayofweek.to_numpy()
    h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    tr_d = (p["trail_atr"] * _atr(bars_df, int(p["atr_len"]))).to_numpy(dtype=float)
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    h830 = l830 = np.nan
    last_day, taken = None, False
    ltr = str_ = np.nan
    for i in range(m):
        if hr[i] == 8 and mn[i] == 30:
            h830, l830 = h[i], lo[i]
        if wd[i] != last_day or (hr[i] == 0 and mn[i] == 0):
            taken, last_day = False, wd[i]
        in_time = (hr[i] == 8 and mn[i] >= 40) or (8 < hr[i] < 15)
        long_e = c[i] > h830 and not taken and in_time
        short_e = c[i] < l830 and not taken and in_time
        if long_e:
            ltr = c[i] - tr_d[i]
        if short_e:
            str_ = c[i] + tr_d[i]
        if not np.isnan(ltr):
            ltr = max(ltr, c[i] - tr_d[i])
        if not np.isnan(str_):
            str_ = min(str_, c[i] + tr_d[i])
        end_l = not np.isnan(ltr) and c[i] <= ltr
        end_s = not np.isnan(str_) and c[i] >= str_
        if end_l:
            ltr = np.nan
        if end_s:
            str_ = np.nan
        if long_e:
            le[i], taken = True, True
        if short_e:
            se[i], taken = True, True
        lx[i] = end_l and not le[i]
        sx[i] = end_s and not se[i]
    idx = bars_df.index
    return tuple(pd.Series(x, index=idx) for x in (le, lx, se, sx))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    frac = _atr(bars_df, int(p["atr_len"])) / bars_df["close"]
    return {"sl_stop": (p["sl_atr"] * frac).shift(1), "tp_stop": (p["tp_atr"] * frac).shift(1)}


def portfolio_kwargs(**params):
    return {}
