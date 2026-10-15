"""Dual Thrust on 10-minute bars: Range = max(HH - LC, HC - LL) over the last 20 completed 4-hour
bars; the close crossing above the reference open + 0.67 Range goes long, crossing under the
reference open - 0.62 Range goes short (always in the market after the first signal).
Port of FMZ strategy #427267 "Dual Thrust Strategy".

FMZ source id: 427267

Source
    https://www.fmz.com/strategy/427267 (PineScript v3, FMZ last modified
    2023-09-19 16:27:12). Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 192-211), k1 0.67, k2 0.62, TimeFrame '240', len 20
    HH / LC / HC / LL = security(ticker, '240', highest(high, 20) / lowest(close, 20) / highest(close, 20)
                        / lowest(low, 20), lookahead_off)
    Range = max(HH - LC, HC - LL)
    BuyLine = security(ticker, 'D', open, lookahead_off) + k1 Range; SellLine = ... - k2 Range
    crossover(close, BuyLine) -> entry long; crossunder(close, SellLine) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md, skill section 4)
    * lookahead_off on history: a higher bar's values are seen from the chart bar whose close is
      the higher bar's close. The 4-hour blocks (UTC, fixed clock grid) and the broker day (ends
      17:00 America/New_York, DST by the zone) end at known clock times, so a 10-minute bar sees
      every block / day that has ended by its own close.
    * So the daily "open" is the open of the last COMPLETED broker day (yesterday's open), not
      today's; this is how the script behaves on history (lookahead_off on 'open'), and it is
      ported as written. A version on today's open (the textbook Dual Thrust, known at the day's
      start) is a decision owed, not ported here.
    * The 4-hour bars are built from the minute data (left-labelled, gaps kept); highest / lowest
      over the last 20 of them, current block excluded until it has ended.
    * strategy.entry reverses: REVERSAL INTENDED (qty 1 is sizing).
    * FREQ = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; higher bars only once ended.
    2 generic: PASS, the range is a price difference scaled by k (no levels).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty 1 and initial capital stored in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: the reference open is the broker day's (17:00 America/New_York, DST by the zone), not a venue open.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427267_dual_thrust"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None
HTF = "4h"      # TimeFrame '240'

GRID = {
    "k1": [0.67, 0.4],
    "k2": [0.62, 0.4],
    "length": [20, 10],
}
DEFAULT_PARAMS = {"k1": 0.67, "k2": 0.62, "length": 20}


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


def _htf_from_bars(bars):
    """4-hour OHLC built from the 10-minute bars (10 minutes divide 4 hours: the same values as from minutes)."""
    return bars.resample(HTF, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n = int(p["length"])
    htf = _htf_from_bars(bars_df)
    hh = htf["high"].rolling(n).max()
    lc = htf["close"].rolling(n).min()
    hc = htf["close"].rolling(n).max()
    ll = htf["low"].rolling(n).min()
    rng = pd.concat([hh - lc, hc - ll], axis=1).max(axis=1, skipna=False)
    bar_end = bars_df.index + pd.Timedelta(FREQ)
    # last 4-hour block that has ended by this bar's close: its start is <= bar_end - 4h
    blk = pd.Series(rng.to_numpy(), index=htf.index)
    pos_b = np.searchsorted(htf.index.values, (bar_end - pd.Timedelta(HTF)).values, side="right") - 1
    r = np.where(pos_b >= 0, blk.to_numpy()[np.clip(pos_b, 0, None)], np.nan)
    # last broker day that has ended by this bar's close: label < broker_day(bar_end)
    lab = broker_day(bars_df.index)
    day_open = bars_df["open"].groupby(lab).first()
    end_lab = broker_day(bar_end)
    pos_d = np.searchsorted(day_open.index.values, end_lab.values, side="left") - 1
    dopen = np.where(pos_d >= 0, day_open.to_numpy()[np.clip(pos_d, 0, None)], np.nan)
    buy = dopen + p["k1"] * r
    sell = dopen - p["k2"] * r
    c = bars_df["close"].to_numpy(dtype=float)
    c1 = np.concatenate(([np.nan], c[:-1]))
    b1 = np.concatenate(([np.nan], buy[:-1]))
    s1 = np.concatenate(([np.nan], sell[:-1]))
    long_c = (c > buy) & (c1 <= b1)
    short_c = (c < sell) & (c1 >= s1)
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if long_c[i] and pos != 1:
            pos = 1
        elif short_c[i] and pos != -1:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    idx = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=idx), pd.Series((prev == 1) & (tgt == 0), index=idx),
            pd.Series((tgt == -1) & (prev != -1), index=idx), pd.Series((prev == -1) & (tgt == 0), index=idx))


def portfolio_kwargs(**params):
    return {}
