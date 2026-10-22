"""SMA 50 / 200 crossings, daily bars: the SMA 50 crossing over goes long with a 1.5 % stop and 2 % target from the fill; crossing under closes the long and goes short; the short's levels sit on the wrong
side of the market, so each short closes at the open after its first bar; reversing.
Port of FMZ strategy #442657 "Trend Following Strategy Based on Moving Average Crossover" (Gleitend Strategie).

FMZ source id: 442657

Source
    https://www.fmz.com/strategy/442657 (PineScript v5, FMZ last modified 2024-02-23 15:14:31).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 109-149), SMA 50 / 200; stop avg x 0.985, limit avg x 1.02 for both ids
    crossover(sma50, sma200) -> entry Buy;  crossunder -> close Buy, entry Sell
    exit(Buy, stop = avg x 0.985, limit = avg x 1.02);  exit(Sell, stop = avg x 0.985, limit = avg x 1.02)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The long bracket is sent every bar from the average (fill) price, ported active from the fill bar
      (#440797) as fixed fractions 0.015 / 0.02 of the fill. The short exit reuses the long's levels: a
      buy stop under and a buy limit over the price, both on the wrong side of the market, so the short
      closes at the first open after its fill bar (as #439872: the port closes it on that bar's
      signal). strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4).
      Stops on 1-day bars: mark coarse_bar_stop. No sizing code. FREQ = "1D" from the backtest header
      (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; long bracket fixed from the fill; the short's wrong-side levels read as a close.
    2 generic: PASS, SMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_442657_sma50_200_cross_long_bracket_short_one_bar"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "short_len": [50, 20],
    "long_len": [200, 100],
}
DEFAULT_PARAMS = {"short_len": 50, "long_len": 200, "sl_pct": 0.015, "tp_pct": 0.02}


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


def _run(bars_df, p):
    c = bars_df["close"]
    s, l_ = c.rolling(int(p["short_len"])).mean(), c.rolling(int(p["long_len"])).mean()
    buy = ((s > l_) & (s.shift(1) <= l_.shift(1))).to_numpy()
    sell = ((s < l_) & (s.shift(1) >= l_.shift(1))).to_numpy()
    sl, tp = float(p["sl_pct"]), float(p["tp_pct"])
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le, se, sx = (np.zeros(m, dtype=bool) for _ in range(3))
    pos, entry_i = 0, -1
    for i in range(m):
        if pos == 1 and i >= entry_i and (lv[i] <= ov[entry_i] * (1 - sl) or hv[i] >= ov[entry_i] * (1 + tp)):
            pos = 0
        if i + 1 >= m:
            continue
        if buy[i] and pos != 1:
            le[i], pos, entry_i = True, 1, i + 1
        elif sell[i] and pos != -1:
            se[i], pos, entry_i = True, -1, i + 1
        elif pos == -1 and i == entry_i:
            sx[i], pos = True, 0          # the wrong-side short levels fill at the next open
    return le, se, sx


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, sx = _run(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), pd.Series(sx, index=ix)


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, _, _ = _run(bars_df, p)
    ix = bars_df.index
    on = pd.Series(le, index=ix)
    return {"sl_stop": pd.Series(float(p["sl_pct"]), index=ix).where(on).shift(1),
            "tp_stop": pd.Series(float(p["tp_pct"]), index=ix).where(on).shift(1)}


def portfolio_kwargs(**params):
    return {}
