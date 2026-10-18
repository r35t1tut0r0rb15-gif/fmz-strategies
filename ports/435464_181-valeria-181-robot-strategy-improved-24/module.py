"""Close against its 4-bar average, broker days, with a bracket: the close crossing above its SMA 4 goes long, crossing below goes
short (reversing); each trade carries a 170-unit stop and a 150-unit target around the signal close, re-expressed as ATR multiples.
Port of FMZ strategy #435464 "跨趋势跟随套利181策略Valeria-181-Robot-Strategy-Improved-24" (Valeria 181 Bot Strategy Mejorado 2.21).

FMZ source id: 435464

Source
    https://www.fmz.com/strategy/435464 (PineScript v5, FMZ last modified 2023-12-15 10:13:38).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 119-143), SMA 1 (the close) against SMA 4; stop 170 / target 150 price units
    longCondition = crossover(sma(close, 1), sma(close, 4));  shortCondition = crossunder(sma(close, 1), sma(close, 4))
    entry long / short;  lastLongOrderPrice = close;  exit(stop = last - 170, limit = last + 150) (shorts mirror)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: 170 / 150 price units are no use across instruments; the port uses sl_stop = k_atr x
      ATR / close and tp_stop = (150 / 170) x k_atr x ATR / close of the signal bar, shifted one bar
      inside stops() (re-based on the fill); 0.17 is the reading on a daily BTC bar (the header
      instrument), 1.0 a volatility-sized stop. The author's exit levels follow the last order
      price; the port fixes them at the entry fill. The opposite cross reverses the position:
      REVERSAL INTENDED.
    * Stop module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, price-unit bracket -> ATR multiple.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the margin inputs stored; the price-unit bracket quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG435464 (3 members, best partner #442222, Jaccard 0.941); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_435464_close_sma4_cross_bracket"
FAMILY = "ma_cross"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "k_atr": [0.17, 1.0],
    "sma_len": [4, 10],
}
DEFAULT_PARAMS = {"k_atr": 0.17, "sma_len": 4, "tp_ratio": 0.8824, "atr_len": 14}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    ma = c.rolling(int(p["sma_len"])).mean()
    le = ((c > ma) & (c.shift(1) <= ma.shift(1))).fillna(False).astype(bool)
    se = ((c < ma) & (c.shift(1) >= ma.shift(1))).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    f = (tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / c * float(p["k_atr"])).shift(1)
    return {"sl_stop": f, "tp_stop": f * float(p["tp_ratio"])}


def portfolio_kwargs(**params):
    return {}
