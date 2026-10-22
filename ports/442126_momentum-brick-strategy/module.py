"""ATR renko emulation, broker days: the renko line (moving one ATR(14) brick per bar from zero, as written) turning up past its previous brick goes long, turning down goes short; reversing.
Port of FMZ strategy #442126 "Momentum Brick Strategy" (Flex Renko Emulator).

FMZ source id: 442126

Source
    https://www.fmz.com/strategy/442126 (PineScript v4, FMZ last modified 2024-02-19 15:32:17).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 118-236), ATR 14 on resolution "D" (the chart's own daily bars); margin on; dates 2017-2025 (testPeriod true)
    Brick1 = close > nz(Brick1[1]) + ATR ? nz(Brick1[1]) + ATR : close < nz(Brick1[1]) - ATR ? nz(Brick1[1]) - ATR : nz(Brick1[1]);  Brick2 = the previous brick when Brick1 changes
    mylong = crossover(Brick1, Brick2) -> last_long;  myshort = crossunder -> last_short;  in_long = last_long > last_short ? 2 : 0;  crossover(in_long, 1.9) and not long -> entry Long;  crossover(in_short, 1.9) and not short -> entry Short (Margin on)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "D" security on a daily chart is the chart's own ATR(14). The brick line starts at 0 (nz) and
      moves at most one brick per bar, as written. The second in_long / in_short terms are always 0. With
      Margin on, the short signal enters short (the close of the long is skipped) and reverses it.
      REVERSAL INTENDED. No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with
      their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, renko brick direction changes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442126_flex_renko_brick_turn_reversal"
FAMILY = "renko_bricks"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_len": [14, 7],
}
DEFAULT_PARAMS = {"atr_len": 14}


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


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    bs = _rma(tr, int(p["atr_len"])).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    b1 = np.zeros(m)
    b2 = np.zeros(m)
    s1 = s2 = 0.0
    for i in range(m):
        prev1 = s1
        if cv[i] > s1 + bs[i]:
            s1 = s1 + bs[i]
        elif cv[i] < s1 - bs[i]:
            s1 = s1 - bs[i]
        if s1 != prev1:
            s2 = prev1
        b1[i], b2[i] = s1, s2
    b1s, b2s = pd.Series(b1, index=c.index), pd.Series(b2, index=c.index)
    ml = ((b1s > b2s) & (b1s.shift(1) <= b2s.shift(1))).to_numpy()
    ms = ((b1s < b2s) & (b1s.shift(1) >= b2s.shift(1))).to_numpy()
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    last_l = last_s = 0
    in_l_prev = in_s_prev = 0
    for i in range(m):
        if ml[i]:
            last_l = i + 1
        if ms[i]:
            last_s = i + 1
        in_l = 2 if last_l > last_s else 0
        in_s = 2 if last_s > last_l else 0
        le[i] = in_l > 1.9 and in_l_prev <= 1.9
        se[i] = in_s > 1.9 and in_s_prev <= 1.9
        in_l_prev, in_s_prev = in_l, in_s
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
