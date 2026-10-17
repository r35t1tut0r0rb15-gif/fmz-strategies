"""Inside bars with an SMA 65 filter, 3-minute bars: a green inside bar (high under and low over the previous bar's) with the
close above the SMA 65 goes long, a red inside bar under it goes short (reversing); each trade carries a stop 5 ATR 14 from
the bar's ohlc4 and a target twice the stop distance.
Port of FMZ strategy #434998 "Look Up and Look Down Strategy Based on Internal Price Channels" (Inside Bar Strategy w/ SL).

FMZ source id: 434998

Source
    https://www.fmz.com/strategy/434998 (PineScript v4, FMZ last modified 2023-12-11 15:56:28).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 174-329), 1 inside bar; MA filter on, SMA 65; stop type ATR (5 x ATR 14 from ohlc4), TP 2 R; direct reverse on; trailing off
    BUY = bar_index > 40 and high < high[1] and low > low[1] and close > open and close > sma65;  SELL mirror with close < open and not above the SMA
    SL = valuewhen(position changed, ohlc4 - 5 atr(14));  TP = avg + (avg - SL) x 2;  shorts mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The script takes the ATR stop at the bar its position changes (the fill bar's close); the port
      takes it from the signal bar ((close - (ohlc4 - 5 ATR)) / close), shifted one bar inside
      stops() and re-based on the fill: approximation stated. A signal whose stop is not beyond the
      close places no entry; the target is twice the stop fraction. The first 40 bars give no signal.
    * strategy.entry reverses (direct reversal on): REVERSAL INTENDED. Stop module: portfolio_kwargs
      {} (driver D4). FREQ = "3min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (approximation stated).
    2 generic: PASS, inside bars, an average filter and ATR exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity, capital and commission stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND434998 (4 members, best partner #435256, Jaccard 0.652); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_434998_inside_bar_sma_atr_bracket"
FAMILY = "candle_pattern"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ma_len": [65, 200],
    "atr_mult": [5.0, 2.0],
}
DEFAULT_PARAMS = {"ma_len": 65, "atr_len": 14, "atr_mult": 5.0, "rr": 2.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _setup(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    atr = (tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() * float(p["atr_mult"])).to_numpy()
    ma = c.rolling(int(p["ma_len"])).mean()
    inside = (h < h.shift(1)) & (lo > lo.shift(1))
    above = c > ma
    warm = pd.Series(np.arange(len(c)) > 40, index=c.index)
    bull = (warm & inside & (c > o) & above).to_numpy()
    bear = (warm & inside & (c < o) & ~above).to_numpy()
    cv = c.to_numpy(dtype=float)
    o4 = ((o + h + lo + c) / 4).to_numpy(dtype=float)
    with np.errstate(invalid="ignore"):
        l_sl, s_sl = (cv - (o4 - atr)) / cv, ((o4 + atr) - cv) / cv
        le, se = bull & (l_sl > 0), bear & (s_sl > 0)
        sl = np.where(le, l_sl, np.where(se, s_sl, np.nan))
    return le, se, sl, sl * float(p["rr"])


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _, _ = _setup(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl, tp = _setup(bars_df, p)
    ix = bars_df.index
    return {"sl_stop": pd.Series(sl, index=ix).shift(1), "tp_stop": pd.Series(tp, index=ix).shift(1)}


def portfolio_kwargs(**params):
    return {}
