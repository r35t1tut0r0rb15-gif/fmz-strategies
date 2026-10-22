"""Gap-down shorts, 1-hour bars, short only: an hourly open more than 150 points under the daily reference close sells short when the same bar already reaches a 50-point target from its open or is at or after 11:00 UTC; the trade's target is the 50-point level sent on the signal bar when that bar reached it.
Port of FMZ strategy #458137 "Comprehensive Price Gap Short Term Trend Capture Strategy" (Gap Down Short Strategy).

FMZ source id: 458137

Source
    https://www.fmz.com/strategy/458137 (PineScript v5, FMZ last modified 2024-07-30 11:08:23).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 304-350), daily close[1] by request.security("D") (no lookahead); gap threshold 150, target 50 points (price units); 11:00 cut-off (exchange time, UTC)
    gap = open - prevClose;  gapDown and not inPosition -> entryPrice = open, target = open - 50, inPosition, targetHit = false
    inPosition: low <= target -> targetHit, inPosition = false;  time >= 11:00 -> inPosition = false
    entry Short when gapDown and not inPosition;  targetHit -> exit(limit = target);  time >= 11:00 and inPosition -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The version-5 request.security("D", close[1]) without lookahead is read on the last broker day
      completed by the chart bar's close (#440503): close[1] of that day, i.e. the close two days back
      on every bar but the day's last, where it is the previous day's close. The 150 / 50 points are
      price amounts, ported as fractions of 42000 (0.00357 / 0.00119 of the price). The flags are
      followed as written: the entry call comes after the flag updates, so a gap bar enters only when
      the same bar hits the target or is at or after 11:00; the 11:00 close never fires (the flag is
      cleared at 11:00 before it is tested). The target is sent while targetHit holds: the level in
      force on the signal bar is the trade's target (a fraction of the fill), a level at or over the
      fill open is marketable and is sent as a bar-close exit on the fill bar (one bar late); a target
      armed or moved by a later gap bar is not followed (pending, mark trailing_stop_pending). A short
      opened without a target has no exit, as written. Short only. Stop module: portfolio_kwargs {}
      (driver D4). No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the point target as a fraction of the fill.
    2 generic: PASS, opening-gap shorts with a point target.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: 11:00 UTC cut-off on the bar open (exchange time of the Binance header).
Short only: Opposite entries cannot occur.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_458137_gap_down_short_point_target_flags"
FAMILY = "breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "gap_frac": [0.00357, 0.01],
    "target_frac": [0.00119, 0.005],
}
DEFAULT_PARAMS = {"gap_frac": 0.00357, "target_frac": 0.00119, "cutoff_min": 660}


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


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _run(bars_df, p):
    o, lo, c = bars_df["open"], bars_df["low"], bars_df["close"]
    ix = bars_df.index
    day = broker_day(ix)
    ends = np.asarray(broker_day(ix + pd.Timedelta(FREQ)) != day)   # this bar's close ends its day
    dc = c.groupby(day).last()
    k = dc.index.get_indexer(day) - (~ends).astype(int)              # last day completed by the close
    ref = dc.shift(1).to_numpy()                                      # close[1] on that day
    prev_c = np.where(k >= 0, ref[np.clip(k, 0, None)], np.nan)
    ov, lv = o.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    with np.errstate(invalid="ignore"):
        gd = (ov - prev_c) < -float(p["gap_frac"]) * prev_c
    late = np.asarray(ix.hour * 60 + ix.minute >= int(p["cutoff_min"]))
    tf = float(p["target_frac"])
    m = len(ov)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sent = np.full(m, np.nan)                    # target in force on each entry's signal bar
    in_flag, hit, target = False, False, np.nan
    pos, pend, active, lvl = 0, 0, np.nan, np.nan
    for i in range(m):
        if pend == 1:
            pos, pend, active = -1, 0, lvl
            if not np.isnan(active) and active >= ov[i]:
                sx[i], pend, active = True, 2, np.nan    # target through the fill: closed at the next open
        elif pend == 2:
            pos, pend, active = 0, 0, np.nan
        if pos == -1 and not np.isnan(active) and lv[i] <= active:
            pos, active = 0, np.nan              # the target fills inside this bar
        if gd[i] and not in_flag:
            target, in_flag, hit = ov[i] * (1 - tf), True, False
        if in_flag:
            if lv[i] <= target:
                hit, in_flag = True, False
            if late[i]:
                in_flag = False
        if gd[i] and not in_flag and pos == 0 and pend == 0:
            lvl = target if hit else np.nan
            se[i], pend, sent[i] = True, 1, lvl
    return pd.Series(se, index=ix), pd.Series(sx, index=ix), pd.Series(sent, index=ix)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    se, sx, _ = _run(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return false, false.copy(), se, sx


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    f = 1 - _run(bars_df, p)[2].shift(1) / bars_df["open"]     # the signal bar's target, as a fraction of the fill open
    return {"tp_stop": f.where(f > 0)}                          # at or through the fill: closed by a bar-close exit


def portfolio_kwargs(**params):
    return {}
