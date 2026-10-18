"""20-bar breakouts with a bracket, broker days: a close above the previous bar's 20-bar high goes long, a close under the
previous bar's 20-bar low goes short (reversing); each trade carries a 500-unit target and a 200-unit stop, re-expressed as
ATR multiples.
Port of FMZ strategy #435260 "Gold Price Action Trading Algorithm" (XAUUSD Price Action Strategy).

FMZ source id: 435260

Source
    https://www.fmz.com/strategy/435260 (PineScript v5, FMZ last modified 2023-12-13 16:08:12).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 177-194), highest(high, 20) / lowest(low, 20); target 500, stop 200 (price units)
    breakoutLevel = highs[1];  longCondition = high > highs[1] and close > highs[1];  shortCondition = low < highs[1] and close < lows[1]
    longCondition -> entry long, exit(limit = close + 500, stop = close - 200);  shortCondition -> entry short, exit(limit = close - 500, stop = close + 200)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The window is the previous bar's: highs[1] and lows[1] end one bar before the signal bar, so
      the bar is not in its own comparison set (a breakout can fire). The short test's first part
      (low under highs[1]) is implied by its second, as written. The two conditions cannot hold
      together. strategy.entry reverses: REVERSAL INTENDED.
    * Criterion 2: 500 / 200 price units are no use across instruments; the port uses tp_stop =
      2.5 x k_atr x ATR / close and sl_stop = k_atr x ATR / close of the signal bar, shifted one bar
      inside stops() (re-based on the fill); 0.2 is the reading on a daily BTC bar (the header
      instrument), 1.0 a volatility-sized stop. The author re-sends the exit on each bar the breakout
      holds (the levels then follow the new close); the port fixes the bracket at the entry fill.
    * Stop module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, price-unit bracket -> ATR multiple.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the price-unit bracket quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_435260_breakout_20_bracket"
FAMILY = "breakout"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "lookback": [20, 40],
    "k_atr": [0.2, 1.0],
}
DEFAULT_PARAMS = {"lookback": 20, "k_atr": 0.2, "tp_ratio": 2.5, "atr_len": 14}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["lookback"])
    hh1 = h.rolling(n).max().shift(1)
    ll1 = lo.rolling(n).min().shift(1)
    le = ((h > hh1) & (c > hh1)).fillna(False).astype(bool)
    se = ((lo < hh1) & (c < ll1)).fillna(False).astype(bool)
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
