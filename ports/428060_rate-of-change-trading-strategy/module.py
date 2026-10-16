"""Rate-of-change dip buyer, broker days, long only: buy when the low is under SMA 30, the 12-bar
rate of change exceeds 2.3 %, SMA 14 is rising and SMA 100 falling. The only exit is a 3.62 % trailing
stop on closes, armed (and re-armed) on bars where the trade is in profit and a sell setup appears.
Port of FMZ strategy #428060 "Rate of Change Trading Strategy" (ROC+Strategy).

FMZ source id: 428060

Source
    https://www.fmz.com/strategy/428060 (PineScript v4, FMZ last modified 2023-09-28 11:26:44).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 206-282), SMAs 14 / 100 / 30, ROC 12 bars (2.3 % / 4.7 %), trail 3.62 %
    ROC = (max(close[12], close) - min(close[12], close)) / max(close[12], close)
    enterLong = low < sma30 and ROC > 0.023 and rising(sma14, 1) and falling(sma100, 1) -> entry long (if not long)
    trail = max(close x (1 - 3.62 %), trail[1]) while long
    enterShort = close > sma30 and ROC > 0.047 and rising(close, 3) and openprofit > 0 and sma14 > sma100
                 -> strategy.exit(stop = trail) (a resting stop at the current trail level)

Interpretation choices (Pine rules in SURVEY_README.md; skill section 7)
    * The exit is a resting stop at a close-ratchet level armed by a condition: the house spec cannot
      express it (mark trailing_stop_pending). Stated approximation, so the port has an exit: once
      armed, a bar whose low reaches the armed level is an exit signal filled at the next open
      (Pine fills at the level, intrabar); the level is refreshed on every later setup bar.
    * The entry price is the fill (next open); openprofit > 0 is the close above it. A touch and a
      new entry on one bar keep the position (Pine would exit and re-enter; stated).
    * The order stake (96 % of equity) is sizing. Long only.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
    * FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the trailing exit is approximated (mark).
    2 generic: PASS, MA lengths and percentages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the order stake stored; the trailing exit quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND428060 (2 members, best partner #435831, Jaccard 0.785); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_428060_roc_dip_buyer_armed_trail"
FAMILY = "momentum_breakout"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "trail_pct": [3.62, 2.0],
    "lookback": [12, 6],
}
DEFAULT_PARAMS = {"ss": 14, "ff": 100, "ref": 30, "low_offset": 0.023, "high_offset": 0.047,
                  "lookback": 12, "trail_pct": 3.62}


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


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, lo, c = bars_df["open"], bars_df["low"], bars_df["close"]
    fast, slow, ref = (c.rolling(int(p[k])).mean() for k in ("ss", "ff", "ref"))
    lb = int(p["lookback"])
    cl = c.shift(lb)
    hi_, lo_ = np.maximum(cl, c), np.minimum(cl, c)
    roc = (hi_ - lo_) / hi_
    enter_long = ((lo < ref) & (roc > p["low_offset"]) & (fast > fast.shift(1)) & (slow < slow.shift(1))).to_numpy()
    setup = ((c > ref) & (roc > p["high_offset"]) & (c > c.shift(3)) & (fast > slow)).to_numpy()
    ov, lv, cv = o.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    tp = p["trail_pct"] / 100
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos, entry_i, trail, armed = 0, -1, 0.0, np.nan
    for i in range(m):
        held = pos == 1 and i >= entry_i
        if held and not np.isnan(armed) and lv[i] <= armed:
            pos, armed, trail = 0, np.nan, 0.0          # touched the resting stop
            held = False
        if held:
            trail = max(cv[i] * (1 - tp), trail)
            if setup[i] and cv[i] > ov[entry_i]:
                armed = trail                           # strategy.exit(stop = trail) re-issued
        if pos != 1 and enter_long[i]:
            pos, entry_i, trail, armed = 1, i + 1, 0.0, np.nan
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
