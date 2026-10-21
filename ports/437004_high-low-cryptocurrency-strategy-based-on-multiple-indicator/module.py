"""Three rising highs with a MACD, SAR, CCI and SMA-gap filter and a percent bracket, 45-minute bars: two higher highs after a close above the high of three bars ago, a positive MACD histogram (SMA oscillator), an
uptrending SAR, a non-negative CCI 20 and the SMA 5 under the SMA 35 go long; the mirror goes short; reversing; each trade has a 0.5 % stop and a 15 % target.
Port of FMZ strategy #437004 "High Low Cryptocurrency Strategy Based on Multiple Indicators" (Crypto strategy high/low).

FMZ source id: 437004

Source
    https://www.fmz.com/strategy/437004 (PineScript v4, FMZ last modified 2023-12-29 14:16:16).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 190-321), MACD 12 / 26 / 9 (SMA oscillator, EMA signal), SAR 0.02 / 0.02 / 0.2, CCI 20, SMA 5 / 35 gap in percent, original colouring on; sl 0.005, tp 0.15
    longC = high > high[1] and high[1] > high[2] and close[2] > high[3] and hist > 0 and uptrend and smadif < 0 and cci >= 0;  shortC = the mirrors with not uptrend, smadif > 0, cci < 0
    entry long / short;  exit(loss = close x sl / mintick, profit = close x tp / mintick) for both, every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is written in ticks of close x 0.5 % / 15 %, re-sent each bar from that bar's close; the
      port reads it as fixed 0.5 % / 15 % fractions of the entry fill (scalars in stops(); the moving close
      changes the distance only a little). The SAR is the script's own block (Pine's reference algorithm;
      na on the first bar, where neither side can enter). With original colouring on, the colour test is the
      CCI's sign; the CCI buffer line only paints. REVERSAL INTENDED. Stop module: portfolio_kwargs {}
      (driver D4). No sizing code. FREQ = "45min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the entry.
    2 generic: PASS, percent bracket, dimensionless filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437004_rising_highs_filters_pct_bracket"
FAMILY = "trend_confluence"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl": [0.005, 0.01],
    "tp": [0.15, 0.05],
}
DEFAULT_PARAMS = {"sl": 0.005, "tp": 0.15, "fast": 12, "slow": 26, "signal": 9, "psar_start": 0.02,
                  "psar_inc": 0.02, "psar_max": 0.2, "cci_len": 20, "sma1": 5, "sma2": 35}


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


def _sar_up(h, lo, c, start, inc, mx):
    """Trend side of Pine's sar reference block (True = uptrend); False on the first bar (na)."""
    n = len(c)
    up = np.zeros(n, dtype=bool)
    result = max_min = acc = np.nan
    below = False
    for i in range(1, n):
        first = False
        if i == 1:
            if c[1] > c[0]:
                below, max_min, result = True, h[1], lo[0]
            else:
                below, max_min, result = False, lo[1], h[0]
            first, acc = True, start
        result = result + acc * (max_min - result)
        if below:
            if result > lo[i]:
                first, below = True, False
                result, max_min, acc = max(h[i], max_min), lo[i], start
        else:
            if result < h[i]:
                first, below = True, True
                result, max_min, acc = min(lo[i], max_min), h[i], start
        if not first:
            if below:
                if h[i] > max_min:
                    max_min, acc = h[i], min(acc + inc, mx)
            else:
                if lo[i] < max_min:
                    max_min, acc = lo[i], min(acc + inc, mx)
        if below:
            result = min(result, lo[i - 1])
            if i > 1:
                result = min(result, lo[i - 2])
        else:
            result = max(result, h[i - 1])
            if i > 1:
                result = max(result, h[i - 2])
        up[i] = below
    return up


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    macd = c.rolling(int(p["fast"])).mean() - c.rolling(int(p["slow"])).mean()
    hist = macd - macd.ewm(span=int(p["signal"]), adjust=False).mean()
    n = int(p["cci_len"])
    sma = c.rolling(n).mean()
    mad = c.rolling(n).apply(lambda v: np.abs(v - v.mean()).mean(), raw=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        cci = (c - sma) / (0.015 * mad)
    smadif = (c.rolling(int(p["sma1"])).mean() - c.rolling(int(p["sma2"])).mean()) / c * 100
    upv = _sar_up(h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float),
                  float(p["psar_start"]), float(p["psar_inc"]), float(p["psar_max"]))
    first = np.zeros(len(c), dtype=bool)
    if len(c):
        first[0] = True
    up = pd.Series(upv, index=c.index)
    dn = pd.Series(~upv & ~first, index=c.index)
    h1, h2, h3 = h.shift(1), h.shift(2), h.shift(3)
    l1, l2, l3 = lo.shift(1), lo.shift(2), lo.shift(3)
    c2 = c.shift(2)
    lc = (h > h1) & (h1 > h2) & (c2 > h3) & (hist > 0) & up & (smadif < 0) & (cci >= 0)
    sc = (lo < l1) & (l1 < l2) & (c2 < l3) & (hist < 0) & dn & (smadif > 0) & ~(cci >= 0)
    false = pd.Series(False, index=bars_df.index)
    return lc, false, sc, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"]), "tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
