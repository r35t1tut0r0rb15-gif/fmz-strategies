"""Williams Alligator (SMMA 8 / 5 / 3 of hl2) aligned with the EMA 200, 5-minute bars: lips over teeth over jaw with the close over the EMA buys from flat, the full bearish alignment closes the long and, from flat on a later bar, goes short; the bullish alignment closes the short; never reversing in one bar.
Port of FMZ strategy #451704 "William Alligator Moving Average Trend Catcher Strategy" (Alligator + MA Trend Catcher [TradeDots]).

FMZ source id: 451704

Source
    https://www.fmz.com/strategy/451704 (PineScript v5, FMZ last modified 2024-05-17 10:52:19).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 85-136), SMMA 8 / 5 / 3 of hl2 (offsets plot only); EMA 200; 80 % of equity, commission 0.01 %
    close > ema200 and lips > teeth > jaw and opentrades == 0 -> entry Long;  close < ema200 and lips < teeth < jaw -> close Long
    close < ema200 and lips < teeth < jaw and opentrades == 0 -> entry Short;  close > ema200 and lips > teeth > jaw -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The SMMA starts from the SMA of its first values, then Wilder's recursion (Pine's rma). The
      entries test opentrades at call time, so on the bar a long is closed the short entry still sees
      the open trade and is not sent: the position goes flat, and the short needs the next bar still
      aligned bearish (the same for the short-to-long turn). The alignment offsets only shift the
      plots. Opposite entries cannot occur (entries only from flat). The 80 % of equity and the
      commission are stored. FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, alligator alignment with an EMA trend.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity sizing and commission stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_451704_alligator_ema200_alignment_from_flat"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "jaw": [8, 13],
    "trend_len": [200, 100],
}
DEFAULT_PARAMS = {"jaw": 8, "teeth": 5, "lips": 3, "trend_len": 200}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    hl2 = (h + lo) / 2
    jaw, teeth, lips = _rma(hl2, int(p["jaw"])), _rma(hl2, int(p["teeth"])), _rma(hl2, int(p["lips"]))
    trend = c.ewm(span=int(p["trend_len"]), adjust=False).mean()
    bull = ((c > trend) & (lips > teeth) & (teeth > jaw)).to_numpy()
    bear = ((c < trend) & (lips < teeth) & (teeth < jaw)).to_numpy()
    m = len(bull)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        if pos == 0:
            if bull[i]:
                le[i], pos = True, 1
            elif bear[i]:
                se[i], pos = True, -1
        elif pos == 1 and bear[i]:
            lx[i], pos = True, 0             # the short entry still sees the open trade
        elif pos == -1 and bull[i]:
            sx[i], pos = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
