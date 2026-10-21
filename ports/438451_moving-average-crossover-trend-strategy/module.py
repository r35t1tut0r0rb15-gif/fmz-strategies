"""SMA 60 / 275 crossings of the previous day's open, 10-minute bars, long only: from flat, the fast average crossing over the slow one with the day open above the slow one buys; the day open crossing over the
slow average closes; each trade has a 13 % stop and a 42 % target from the fill.
Port of FMZ strategy #438451 "Moving Average Crossover Trend Strategy" (x-over 150d_200d_sma - Free).

FMZ source id: 438451

Source
    https://www.fmz.com/strategy/438451 (PineScript v5, FMZ last modified 2024-01-12 10:56:57).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 159-203), repaint off; daily open; fast 60, slow 275 (10-minute bars of the daily value); target 42 %, stop 13 %
    srcmc = security(tickerid, "D", open, lookahead_off);  fast / slow = sma(srcmc, 60 / 275);  srcmc > slow and crossover(fast, slow) -> entry long;  crossover(srcmc, slow) -> close long
    in position: exit(limit = avg x 1.42, stop = avg x 0.87)

Interpretation choices (Pine rules in SURVEY_README.md)
    * A version-5 security() without lookahead is read as the last completed higher bar: the previous
      broker day's open, built from the module's own bars; both averages run over the 10-minute bars of
      that value, as written. The close acts on the position held at the bar close (a bar with both the
      entry and the close opens from flat and closes an open long). The bracket is sent from the first
      bar close inside the trade; the port fixes it at the fill (sl_stop 0.13, tp_stop 0.42). "Flat"
      follows the house bracket. Long only. Stop module: portfolio_kwargs {} (driver D4). No sizing code.
      FREQ = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry; daily value from completed days.
    2 generic: PASS, moving-average crossings of the day open; percent bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone) for the daily open.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438451_day_open_sma60_275_bracket_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [60, 30],
    "slow": [275, 150],
}
DEFAULT_PARAMS = {"fast": 60, "slow": 275, "stop": 0.13, "take": 0.42}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    day = broker_day(bars_df.index)
    d_open = o.groupby(day).first()
    src = pd.Series(d_open.shift(1).reindex(day).to_numpy(), index=c.index)   # last completed day's open
    fast = src.rolling(int(p["fast"])).mean()
    slow = src.rolling(int(p["slow"])).mean()
    lc = ((src > slow) & (fast > slow) & (fast.shift(1) <= slow.shift(1))).to_numpy()
    cc = ((src > slow) & (src.shift(1) <= slow.shift(1))).to_numpy()
    ov, hv, lv = o.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    sl, tp = float(p["stop"]), float(p["take"])
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, pend_x = 0, -1, False
    for i in range(m):
        if pend_x:                                       # the close fills at this bar's open
            pos, pend_x = 0, False
        if pos == 1 and i >= entry_i and (lv[i] <= ov[entry_i] * (1 - sl) or hv[i] >= ov[entry_i] * (1 + tp)):
            pos = 0
        if pos == 1 and i >= entry_i and cc[i]:
            lx[i], pend_x = True, True
        elif pos == 0 and lc[i] and i + 1 < m:
            le[i], pos, entry_i = True, 1, i + 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["stop"]), "tp_stop": float(p["take"])}


def portfolio_kwargs(**params):
    return {}
