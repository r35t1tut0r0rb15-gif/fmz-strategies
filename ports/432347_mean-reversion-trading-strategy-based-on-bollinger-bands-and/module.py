"""With the EMA 50 above the EMA 200, a close or low at or under the lower 0.618 band (VWMA 50 of hlc3 minus 0.618 x 1.5 standard deviations) goes long; the close crossing over the upper 0.618 band closes, and a close under 95 % of the entry price closes; hourly bars, long only.
Port of FMZ strategy #432347 "Mean Reversion Trading Strategy Based on Bollinger Bands and Golden Ratio" (Bollinger Band with Fib Golden Ratio (0.618)).

FMZ source id: 432347

Source
    https://www.fmz.com/strategy/432347 (PineScript v4, FMZ last modified 2023-11-16 16:52:55).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 167-211), BB length 50, source hlc3, basis vwma, mult 1.5, band 0.618; EMA 50 / 200; stop loss 5 % (close-based)
    basis = vwma(hlc3, 50);  dev = 1.5 stdev(hlc3, 50);  lower_618 = basis - 0.618 dev, upper_618 = basis + 0.618 dev
    ema50 > ema200 and (close < lower_618 or low <= lower_618) -> entry BB_Fib618;  position_size >= 1 and crossover(close, upper_618) -> close;  position_size >= 1 and close < avg x 0.95 -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * position_size >= 1 is read as "in a position" (as #426617). The 5 % stop is a strategy.close on a bar
      CLOSE under 95 % of the average price, not a broker stop: ported in the signals, with the average
      price = the entry fill (the next bar's open). pyramiding 1, so no adds. Long only. 20 % of equity is
      sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-based stop in the signals.
    2 generic: PASS, Bollinger 0.618 band mean reversion in an EMA uptrend.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): 20 % of equity, capital 10000, pyramiding 1, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the band basis vwma(hlc3, 50); exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432347_vwma50_bb_fib618_dip_ema_uptrend_close_stop_long"
FAMILY = "bollinger_reversion"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [50, 20],
    "mult": [1.5, 2.0],
}
DEFAULT_PARAMS = {"length": 50, "mult": 1.5, "fib": 0.618, "stop_pct": 5.0}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    n = int(p["length"])
    src = (h + lo + c) / 3
    vs = v.rolling(n).sum()
    basis = (src * v).rolling(n).sum() / vs.where(vs != 0)
    dev = float(p["mult"]) * src.rolling(n).std(ddof=0)
    upper = basis + float(p["fib"]) * dev
    lower = basis - float(p["fib"]) * dev
    trend = c.ewm(span=50, adjust=False).mean() > c.ewm(span=200, adjust=False).mean()
    ent = (trend & ((c < lower) | (lo <= lower))).to_numpy()
    xup = ((c > upper) & (c.shift(1) <= upper.shift(1))).to_numpy()
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    k = 1 - float(p["stop_pct"]) / 100
    m = len(ent)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, avg, filled = 0, np.nan, False
    for i in range(m):
        if pos == 1:
            if not filled:
                avg, filled = ov[i], True                # the entry fills at this bar's open
            if xup[i] or cv[i] < avg * k:
                lx[i], pos = True, 0
        elif pos == 0 and ent[i] and i + 1 < m:
            le[i], pos, filled = True, 1, False
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
