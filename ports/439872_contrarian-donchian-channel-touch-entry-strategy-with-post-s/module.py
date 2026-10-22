"""Contrarian Donchian touches, broker days: a new 20-bar low goes long with a 0.22 % stop and a 0.44 % target, a new 20-bar high goes short; after a losing exit the same side pauses three bars; the
short's levels sit on the wrong side of the market, so each short closes at the next open; reversing.
Port of FMZ strategy #439872 "Contrarian Donchian Channel Touch Entry Strategy with Post Stop Loss Pause and Trailing Stop Loss" (Contrarian Donchian Channel Strategy - Touch Entry with Post-SL Pause and Trailing Stop).

FMZ source id: 439872

Source
    https://www.fmz.com/strategy/439872 (PineScript v4, FMZ last modified 2024-01-24 15:07:18).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 167-235), Donchian 20; risk / reward 2; stop 0.22 %; pause 3 candles; size 0.01 % of equity
    long = low <= lowest(low, 20) and (bar - longSLHitBar > 3 or lastTradeDirection != 1);  short = high >= highest(high, 20) and (pause rule);  entry Long / entry Short
    stopLoss = avg x (1 - 0.22 %), takeProfit = avg x (1 + 0.44 %), raised to (avg + centre) / 2 while close > centre (long);  exit(SL_TP_Long) and exit(SL_TP_Short) with the same two levels

Interpretation choices (Pine rules in SURVEY_README.md)
    * A loss is recorded on the bar the position goes flat when the previous close is beyond the
      average price; the state loop follows the bracket so that the pause sees those exits. The long
      bracket is a fixed 0.22 % / 0.44 % of the fill; its raise toward the channel centre is re-sent
      every bar: not ported, mark trailing_stop_pending. The short exit reuses the long's levels: a
      buy stop under and a buy limit over the price, both on the wrong side of the market, so the short
      closes at the first open after its fill bar (the port closes it on that bar's signal). When both
      touches fire, the later short wins (as #437773). strategy.entry reverses: REVERSAL INTENDED. Stop
      module: portfolio_kwargs {} (driver D4). Stops on 1-day bars: mark coarse_bar_stop. The 0.01 %
      size is sizing. Daily bars are broker days, stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; long bracket fixed from the fill; the short's wrong-side levels read as a close.
    2 generic: PASS, Donchian touches and a percent bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_439872_contrarian_donchian_touch_pause"
FAMILY = "donchian_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [20, 50],
    "sl": [0.0022, 0.01],
}
DEFAULT_PARAMS = {"length": 20, "sl": 0.0022, "rr": 2.0, "pause": 3}


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
    h, lo = bars_df["high"], bars_df["low"]
    n = int(p["length"])
    up = (h >= h.rolling(n).max()).to_numpy()
    dn = (lo <= lo.rolling(n).min()).to_numpy()
    ov, cv = bars_df["open"].to_numpy(dtype=float), bars_df["close"].to_numpy(dtype=float)
    hv, lv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    sl = float(p["sl"])
    tp = sl * float(p["rr"])
    pz = int(p["pause"])
    m = len(cv)
    le, se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, x, pend = 0, np.nan, 0
    lsl, ssl, last_dir = 0, 0, 0
    for i in range(m):
        before = pos
        if pend != 0:                                    # orders of the previous close fill at this open
            pos, x = pend, ov[i]
            pend = 0
        elif pos == -1:
            pos = 0                                      # the short's wrong-side exit fills at this open
        if pos == 1 and (lv[i] <= x * (1 - sl) or hv[i] >= x * (1 + tp)):
            pos = 0
        if i > 0 and before == 1 and pos == 0 and cv[i - 1] < x:
            lsl, last_dir = i, 1
        if i > 0 and before == -1 and pos == 0 and cv[i - 1] > x:
            ssl, last_dir = i, -1
        if i + 1 >= m:
            continue
        lc = dn[i] and (i - lsl > pz or last_dir != 1)
        sc = up[i] and (i - ssl > pz or last_dir != -1)
        if sc and pos != -1:
            pend = -1
        elif lc and pos != 1:
            pend = 1
        if pend == 1:
            le[i] = True
        elif pend == -1:
            se[i] = True
            sx[i + 1] = True                             # closed at the open after its fill bar
    return le, se, sx


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, sx = _run(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), pd.Series(sx & ~le, index=ix)


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, _, _ = _run(bars_df, p)
    ix = bars_df.index
    on = pd.Series(le, index=ix)
    sl = float(p["sl"])
    return {"sl_stop": pd.Series(sl, index=ix).where(on).shift(1),
            "tp_stop": pd.Series(sl * float(p["rr"]), index=ix).where(on).shift(1)}


def portfolio_kwargs(**params):
    return {}
