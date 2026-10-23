"""Broker days: a close above the close 6 bars ago and above the SMA 50, closing in the upper half of its range, goes long; the mirror goes short; every bar re-sends a 3 % stop and a 29 % target from the latest close, followed in the signals; reversing.
Port of FMZ strategy #477958 "High Frequency Price Volume Trend Following with Volume Analysis Adaptive Strategy" (Autonomous 5-Minute Robot).

FMZ source id: 477958

Source
    https://www.fmz.com/strategy/477958 (PineScript v6, FMZ last modified 2025-01-10 15:42:31).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 93-141), SMA 50; lookback 6 closes; buy / sell volume split by the close's place in the range; SL 3 %, TP 29 % from each bar's close
    longCondition = close > close[6] and close > sma50 and volume x (close - low) / (high - low) > volume x (high - close) / (high - low) -> entry Long;  short mirrored
    every bar: exit("Exit Long", "Long", stop = close x 0.97, limit = close x 1.29);  exit("Exit Short", "Short", stop = close x 1.03, limit = close x 0.71)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both sides of the volume comparison carry the same volume, so it reduces to the close being in the
      upper (lower) half of the bar's range: volume is not really used (held for volume; weird case).
      The exits are re-sent every bar from that bar's close (the levels move both ways, including from
      the signal bar for the pending entry); the house engine cannot move a stop that way, so the
      signals follow it: a bar whose low / high reaches the previous bar's levels closes the trade at the
      next open (mark trailing_stop_pending). The entries are states, so after such a close the strategy
      re-enters on the next qualifying bar. Titled 5-minute; the header is 1 day. REVERSAL INTENDED. No
      sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; per-bar re-sent stop and target followed in the signals.
    2 generic: PASS, short-term momentum in the SMA 50 trend with close-location filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) as a common factor of both sides, so only a zero volume changes a signal; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_477958_momentum6_sma50_close_location_rolling_stop_reversal"
FAMILY = "momentum"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sl": [0.03, 0.05],
    "tp": [0.29, 0.1],
}
DEFAULT_PARAMS = {"ma_len": 50, "lookback": 6, "sl": 0.03, "tp": 0.29}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    ma = c.rolling(int(p["ma_len"])).mean()
    k = int(p["lookback"])
    rng = (h - lo).where(h != lo)
    bv = (v * (c - lo) / rng).fillna(0.0)
    sv = (v * (h - c) / rng).fillna(0.0)
    buy = ((c > c.shift(k)) & (c > ma) & (bv > sv)).to_numpy()
    sell = ((c < c.shift(k)) & (c < ma) & (sv > bv)).to_numpy()
    cn, hn, ln = c.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    sl, tp = float(p["sl"]), float(p["tp"])
    m = len(cn)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    vpos, pine = 0, 0
    for i in range(m):
        held = pine
        if i > 0 and held != 0:            # the exits sent at the previous close, from that close
            pc = cn[i - 1]
            if (held == 1 and (ln[i] <= pc * (1 - sl) or hn[i] >= pc * (1 + tp))) or \
               (held == -1 and (hn[i] >= pc * (1 + sl) or ln[i] <= pc * (1 - tp))):
                held = 0
        new = held
        if buy[i]:
            new = 1
        if sell[i]:
            new = -1
        pine = new
        if new != vpos and i + 1 < m:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif vpos == 1:
                lx[i] = True
            else:
                sx[i] = True
            vpos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
