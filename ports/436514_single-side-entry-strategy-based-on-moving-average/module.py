"""Average side flips, 1-hour bars: a trend value flips to up when the whole bar is over a chosen moving average (low over the average) and to down when the whole bar is under it (high under); a flip to up goes long, a flip
to down goes short (reversing). Six average types are ported (not the volume-weighted one).
Port of FMZ strategy #436514 "Single Side Entry Strategy Based on Moving Average" (Noro's MAs Tests v1.1).

FMZ source id: 436514

Source
    https://www.fmz.com/strategy/436514 (PineScript v2, FMZ last modified 2023-12-25 14:09:49).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 144-191), MA length 30, type 1 (SMA), source close, Antipila on
    ma = type 1 sma / 2 ema / 3 vwma / 4 dema / 5 tema / 6 kama / 7 price-channel centre of src, len;  trend = (anti off: close > ma ? 1 : close < ma ? -1 :) low > ma ? 1 : high < ma ? -1 : trend[1]
    longCondition = trend == 1 and trend[1] == -1 -> entry Long;  shortCondition = trend == -1 and trend[1] == 1 -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Type 3 (volume-weighted average) reads volume and is not ported. The KAMA starts from 0 as written
      (nz of nothing), so it needs a long run to converge on the price. The DEMA uses ema(ema(close, len),
      len) for its second term (the source is close by default). Antipila is on by default (the bar
      must be fully over / under the average). The input switches for long / short are on. REVERSAL
      INTENDED. The percent-of-equity size is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average side flips.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size stored.
    5 ranges declared: GRID below (12 trials), before any backtest.
    6 near-duplicates: ND427090 (2 members, best partner #427090, Jaccard 0.789); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436514_noro_ma_side_flips"
FAMILY = "trend_filter"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma_type": [1, 2, 4, 5, 6, 7],
    "len": [30, 50],
}
DEFAULT_PARAMS = {"ma_type": 1, "len": 30, "anti": True}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["len"])
    t = int(p["ma_type"])
    ema = lambda s: s.ewm(span=n, adjust=False).mean()      # noqa: E731
    if t == 1:
        ma = c.rolling(n).mean()
    elif t == 2:
        ma = ema(c)
    elif t == 4:
        ma = 2 * ema(c) - ema(ema(c))
    elif t == 5:
        e1 = ema(c)
        e2 = ema(e1)
        ma = 3 * e1 - 3 * e2 + ema(e2)
    elif t == 6:
        noise = c.diff().abs().rolling(n).sum()
        sig = c.diff(n).abs()
        with np.errstate(divide="ignore", invalid="ignore"):
            er = (sig / noise).where(noise.notna() & (noise != 0), 0.0)
        sm = (er * (0.20 - 0.05) + 0.05) ** 2
        x, s = c.to_numpy(dtype=float), sm.to_numpy()
        k = np.empty(len(x))
        prev = 0.0
        for i in range(len(x)):
            prev = prev + s[i] * (x[i] - prev)
            k[i] = prev
        ma = pd.Series(k, index=c.index)
    elif t == 7:
        ma = (c.rolling(n).max() + c.rolling(n).min()) / 2
    else:
        raise ValueError("ma_type 3 (volume-weighted) reads volume and is not ported")
    mv = ma.to_numpy()
    cc, hh, ll = c.to_numpy(), h.to_numpy(), lo.to_numpy()
    m = len(cc)
    trend = np.full(m, np.nan)
    with np.errstate(invalid="ignore"):
        for i in range(m):
            if not p["anti"] and cc[i] > mv[i]:
                v = 1.0
            elif not p["anti"] and cc[i] < mv[i]:
                v = -1.0
            elif ll[i] > mv[i]:
                v = 1.0
            elif hh[i] < mv[i]:
                v = -1.0
            else:
                v = trend[i - 1] if i > 0 else np.nan
            trend[i] = v
    prev = np.concatenate(([np.nan], trend[:-1]))
    with np.errstate(invalid="ignore"):
        long_c = (trend == 1) & (prev == -1)
        short_c = (trend == -1) & (prev == 1)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(long_c, index=ix), false, pd.Series(short_c, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
