"""DEMA 40 band oscillator breakouts, alternating sides, with a band stop, a 1.5 R target and an ATR trail, hourly
bars: one bar after the DEMA sits in the top of its 2-sd band (normalised > 55) with the low above the upper band,
the strategy goes long (unless the last entry was long); the mirror goes short; the stop is the band, the target 1.5
times the risk, and an ATR trail takes over after 2 ATR of profit.
Port of FMZ strategy #491035 "双指数移动平均趋势震荡器策略基于标准差动态调整的量化交易模型-Dual-Exponential-Moving-Average-Trend-Oscillator-Strategy-A-Standard-Deviation-Based-Dynamic-Quantitative-Trading-Model" (DEMA Trend Oscillator Strategy).

FMZ source id: 491035

Source
    https://www.fmz.com/strategy/491035 (PineScript v6, FMZ last modified 2025-04-18 09:19:05).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 211-258), DEMA 40, base 20, thresholds 55 / 45, RR 1.5, trail 2 ATR(14)
    base = SMA 20 of DEMA; upperSD / lowerSD = base -+ 2 x stdev 20 of DEMA; norm = 100 (DEMA - lowerSD) / (upperSD - lowerSD)
    long_cond = norm > 55 and low > upperSD;  short_cond = norm < 45 and high < lowerSD
    long_cond[1] and lastDirection != "long" -> entry long + exit(stop = upperSD, limit = close + (close - upperSD) x 1.5,
    trail_points = trail_offset = 2 ATR in ticks); shorts mirrored with lowerSD

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.stdev is the population deviation (ddof 0). The trigger is the condition of the bar before, as written.
    * The bracket is placed once, on the signal bar: sl_stop = (close - upperSD) / close for a long, tp_stop = 1.5 x
      that, shifted one bar inside stops() and re-based on the fill. Since the trigger is the previous bar's, the
      signal bar's close can already be beyond its band (the source's stop then fires at once on the fill): the port
      emits no such entry (a zero-length trade), the direction memory still flips, as written.
    * The trail is in true ticks (ATR / mintick): from 2 ATR of profit a stop 2 ATR behind the best price. Ported
      natively (mark trailing_stop): {"type": "volatility", "atr_n": 14, "k": 2.0, "anchor": "high_low",
      "activate_after": 0.012}. Stated approximation: the 2-ATR activation becomes a 1.2 % gain (two hourly ATRs on
      the author's TRX_USD; judgement before any backtest), as #428795.
    * Entries alternate sides and reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "1h".

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at the signal bar; the trail a house trail (approximation stated).
    2 generic: PASS, normalised band position, band and ATR distances.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity quoted; the exits ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_491035_dema_band_oscillator_breakout"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "len_dema": [40, 20],
    "rr": [1.5, 3.0],
}
DEFAULT_PARAMS = {"len_dema": 40, "base_len": 20, "lu": 55, "su": 45, "rr": 1.5, "trail_mult": 2.0, "atr_len": 14,
                  "trail_activate": 0.012}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _bands(bars_df, p):
    c = bars_df["close"]
    n = int(p["len_dema"])
    e1 = c.ewm(span=n, adjust=False).mean()
    dema = 2 * e1 - e1.ewm(span=n, adjust=False).mean()
    b = int(p["base_len"])
    base = dema.rolling(b).mean()
    sd = dema.rolling(b).std(ddof=0) * 2
    upper, lower = base + sd, base - sd
    norm = 100 * (dema - lower) / (upper - lower)
    return upper, lower, norm


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    upper, lower, norm = _bands(bars_df, p)
    lt = ((norm > p["lu"]) & (lo > upper)).shift(1, fill_value=False).to_numpy(dtype=bool)
    st = ((norm < p["su"]) & (h < lower)).shift(1, fill_value=False).to_numpy(dtype=bool)
    d_long = ((c - upper) / c).to_numpy(dtype=float)
    d_short = ((lower - c) / c).to_numpy(dtype=float)
    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    dist = np.full(m, np.nan)
    last = 0
    for i in range(m):
        if lt[i] and last != 1:
            last = 1
            if d_long[i] > 0:
                le[i], dist[i] = True, d_long[i]
        if st[i] and last != -1:
            last = -1
            if d_short[i] > 0:
                le[i], se[i], dist[i] = False, True, d_short[i]
    return le, se, dist


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _ = _signals(bars_df, p)
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, pd.Series(se, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, dist = _signals(bars_df, p)
    d = pd.Series(dist, index=bars_df.index)
    return {"sl_stop": d.shift(1), "tp_stop": (p["rr"] * d).shift(1),
            "trail": {"type": "volatility", "atr_n": int(p["atr_len"]), "k": float(p["trail_mult"]),
                      "anchor": "high_low", "activate_after": float(p["trail_activate"])}}


def portfolio_kwargs(**params):
    return {}
