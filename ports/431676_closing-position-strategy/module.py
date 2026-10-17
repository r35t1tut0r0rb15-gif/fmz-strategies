"""End-of-day entries against a 200-bar average of the daily close, 1-hour bars: on the 20:00 UTC bar, a last completed daily
close above the SMA 200 (taken over the hourly bars of that series) goes long, below goes short.
Port of FMZ strategy #431676 "Closing Position Strategy" (End of Day Trading Strategy).

FMZ source id: 431676

Source
    https://www.fmz.com/strategy/431676 (PineScript v5, FMZ last modified 2023-11-10 14:25:30).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 195-222), 20:00 entries, 09:30 exits, SMA 200 of the daily close
    daily_close = security(tickerid, "D", close); sma200 = sma(daily_close, 200)
    hour == 20 and minute == 0 and daily_close > sma200 -> entry long (< -> entry short)
    long / short and hour == 9 and minute == 30 -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * hour / minute are the exchange time of the bar's open (UTC on Binance): the entry bar is the
      20:00 UTC bar (UTC, no DST; not a venue open). On the header's 1-hour bars minute is never 30,
      so the 09:30 exits never fire, as written: positions change only by the opposite entry.
    * security("D", close) without lookahead is read as the last completed broker day's close (as
      #429383), built inside simulate() from the port's own bars; the SMA 200 runs over the hourly
      bars of that series, as written.
    * strategy.entry reverses: REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; daily values from completed broker days.
    2 generic: PASS, a clock time and an SMA comparison.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: entries on the 20:00 UTC bar (exchange time on Binance; UTC, no DST); the 09:30 exit never fires on 1-hour bars.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_431676_end_of_day_sma200"
FAMILY = "calendar_seasonal"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_len": [200, 100],
    "entry_hour": [20, 16],
}
DEFAULT_PARAMS = {"sma_len": 200, "entry_hour": 20}


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
    c = bars_df["close"]
    lab = broker_day(bars_df.index)
    dc = pd.Series(c.groupby(lab).last().shift(1).reindex(lab).to_numpy(), index=c.index)
    sma = dc.rolling(int(p["sma_len"])).mean()
    idx = bars_df.index.tz_convert("UTC")
    eod = (idx.hour == int(p["entry_hour"])) & (idx.minute == 0)
    lg = pd.Series(eod & (dc > sma).to_numpy(), index=c.index)
    sh = pd.Series(eod & (dc < sma).to_numpy(), index=c.index)
    false = pd.Series(False, index=c.index)
    return lg, false, sh, false.copy()


def portfolio_kwargs(**params):
    return {}
