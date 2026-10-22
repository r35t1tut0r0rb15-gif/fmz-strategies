"""34-bar high breakouts with a daily EMA exit, 1-hour bars, long only: from flat, a close above the previous bar's 34-bar high goes long; a close under the last completed day's EMA 34 closes.
Port of FMZ strategy #446537 "突破最高价EMA交叉策略-BreakHigh-EMA-Crossover-Strategy" (BreakHigh Strategy).

FMZ source id: 446537

Source
    https://www.fmz.com/strategy/446537 (PineScript v5, FMZ last modified 2024-03-29 14:39:27).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 167-285), 34-bar high; daily EMA 34 (request.security, D); stop on the 9-bar low (off); risk 2.5 % per trade; dates 2012-9999
    buyLine = highest(high, 34)[1];  show = security(D, ema(close, 34));  close > buyLine and no open trade -> entry LONG (qty from risk);  close < show -> close LONG  (stop on the 9-bar low off)

Interpretation choices (Pine rules in SURVEY_README.md)
    * A version-5 request.security() of the daily EMA without lookahead is read as the last completed
      broker day's value (as #440503), built from the module's own hourly bars grouped by broker day.
      The entry is taken only when no trade is open; a same-bar close only acts on a held long. The
      Buy / Sell markers only plot; the 9-bar-low stop is switched off. Long only. The risk quantity is
      sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the daily EMA from completed broker days.
    2 generic: PASS, channel-high breakouts with a daily EMA exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the risk-per-trade quantity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_446537_34bar_high_break_daily_ema34_exit_long"
FAMILY = "donchian_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period": [34, 52],
    "daily_ema": [34, 20],
}
DEFAULT_PARAMS = {"period": 34, "daily_ema": 34}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


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
    h, c = bars_df["high"], bars_df["close"]
    day = broker_day(bars_df.index)
    dc = c.groupby(day).last()
    dema = dc.ewm(span=int(p["daily_ema"]), adjust=False).mean().shift(1)   # last completed broker day
    show = pd.Series(dema.reindex(day).to_numpy(), index=c.index)
    line = h.rolling(int(p["period"])).max().shift(1)
    with np.errstate(invalid="ignore"):
        go = (c > line).to_numpy()
        out = (c < show).to_numpy()
    m = len(go)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held = False
    for i in range(m):
        if go[i] and not held:
            le[i] = True                     # a same-bar close acts only on a held long
        elif out[i] and held:
            lx[i] = True
        held = (held and not lx[i]) or le[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
