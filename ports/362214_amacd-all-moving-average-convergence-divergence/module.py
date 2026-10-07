"""AMACD (EMA12 - SMA26, SMA9 signal) histogram zero crosses with the script's deal-state
alternation: a cross opposite to the open deal only closes it, so the strategy keeps trading
the side its first signal chose (open, close, open, close ...).
Port of FMZ strategy #362214 "AMACD-All-Moving-Average-Convergence-Divergence".

Source
    https://www.fmz.com/strategy/362214 (PineScript v5, FMZ last modified 2022-05-10 16:13:20).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 202-405), defaults: fast EMA 12, slow SMA 26,
signal SMA 9, "Buy/Sell Moving Average Crossover" on, generate close signals on
    hist = macd - signal; long signal = crossover(hist, 0); short signal = crossunder(hist, 0)
    long signal:  dealstate[1] == -1 ? closeShort (dealstate 0) : openLong (dealstate 1)
    short signal: dealstate[1] ==  1 ? closeLong  (dealstate 0) : openShort (dealstate -1)
    openLong -> entry long; openShort -> entry short; closeLong/closeShort -> strategy.close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The deal state is reproduced exactly; since histogram crosses alternate, the strategy
      ends up long-flat-long-flat or short-flat-short-flat depending on the first cross (as written).
      Opposite entries cannot occur in that cycle; portfolio_kwargs returns
      upon_opposite_entry="ignore" (rule 6).
    * FREQ = "30min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_362214_amacd_deal_state"
FAMILY = "macd_momentum"  # proposed 2026-10-07, user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [8, 12],
    "slow": [26, 34],
    "signal": [9, 12],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "signal": 9}


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
    c = bars_df["close"]
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.rolling(int(p["slow"])).mean()
    hist = macd - macd.rolling(int(p["signal"])).mean()
    up = ((hist > 0) & (hist.shift(1) <= 0)).to_numpy()
    dn = ((hist < 0) & (hist.shift(1) >= 0)).to_numpy()
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    deal = 0
    for i in range(m):
        prev = deal
        if up[i]:
            if prev == -1:
                sx[i], deal = True, 0
            else:
                le[i], deal = True, 1
        if dn[i]:
            if prev == 1:
                lx[i], deal = True, 0
            else:
                se[i], deal = True, -1
    idx = bars_df.index
    return (pd.Series(le, index=idx), pd.Series(lx, index=idx),
            pd.Series(se, index=idx), pd.Series(sx, index=idx))


def portfolio_kwargs(**params):
    return {"upon_opposite_entry": "ignore"}
