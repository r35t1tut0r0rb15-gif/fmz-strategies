"""Three falling closes in a row above the SMA 200 buy from flat, daily bars, long only, with a 1.5 % target and a 1 % stop from the fill; the close crossing the SMA 10 in either direction closes.
Port of FMZ strategy #450868 "Dynamic Take Profit and Stop Loss Trading Strategy Based on Three Consecutive Bearish Candles and Moving Averages" (Estrategia de Trading (three falling closes above the SMA 200)).

FMZ source id: 450868

Source
    https://www.fmz.com/strategy/450868 (PineScript v5, FMZ last modified 2024-05-09 16:42:35).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 118-178), 3 falling closes; SMA 200 filter; target 1.5 %, stop 1 % of the average price; SMA 10 cross exit
    falling count >= 3 and close > sma200 and no open trade -> entry Long;  long and the close crosses the SMA 10 (either way) -> close Long
    exit(Long, limit = avg x 1.015, stop = avg x 0.99)  (every bar)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket comes from the average price (na while flat), so it is a fixed 1.5 % / 1 % of the
      fill: tp_stop 0.015, sl_stop 0.01 (as #440797). Entries only from flat; the port follows the
      bracket on its own bars (stop first when both are reachable, as the engine does) so that the
      entries and the SMA close line up with the position. A near-duplicate of #451412 in the corpus,
      ported under rule 7. Daily stop module: mark coarse_bar_stop. Long only. Stop module:
      portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1D" from the backtest header (broker
      days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed from the fill.
    2 generic: PASS, falling-close dips in an uptrend with a percent bracket and an SMA exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the percent bracket quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG450868 (2 members, best partner #451412, Jaccard 1.000); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_450868_three_falling_closes_sma200_pct_bracket_sma10_exit_long"
FAMILY = "mean_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "n_falls": [3, 4],
    "tp": [0.015, 0.03],
}
DEFAULT_PARAMS = {"n_falls": 3, "tp": 0.015, "sl": 0.01, "ma_exit": 10, "ma_trend": 200}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    falls = (c.diff() < 0).to_numpy()
    above = (c > c.rolling(int(p["ma_trend"])).mean()).to_numpy()
    me = c.rolling(int(p["ma_exit"])).mean()
    up = c > me
    cross = (up.shift(1, fill_value=False) != up).to_numpy() & me.notna().to_numpy() & me.shift(1).notna().to_numpy()
    ov, hv, lv = o.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    tp, sl = float(p["tp"]), float(p["sl"])
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held, fill_i, fp = False, -1, np.nan
    cnt = 0
    for i in range(m):
        cnt = cnt + 1 if falls[i] else 0
        if held and i >= fill_i and (lv[i] <= fp * (1 - sl) or hv[i] >= fp * (1 + tp)):
            held = False                     # the bracket closed it inside this bar
        if not held and cnt >= int(p["n_falls"]) and above[i] and i + 1 < m:
            le[i], held, fill_i, fp = True, True, i + 1, ov[i + 1]
        elif held and i >= fill_i and cross[i]:
            lx[i], held = True, False
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"]), "tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
