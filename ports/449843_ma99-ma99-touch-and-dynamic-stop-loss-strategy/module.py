"""SMA 99 touches, daily bars, with a two-close stop at the touch level: a bar touching the SMA 99 and closing above it goes long, closing below goes short; two closes in a row beyond the SMA value saved
at the entry close the position; reversing.
Port of FMZ strategy #449843 "MA99接触与动态止损策略-MA99-Touch-and-Dynamic-Stop-Loss-Strategy" (MA99 Temas ve Dinamik Stop-Loss Stratejisi).

FMZ source id: 449843

Source
    https://www.fmz.com/strategy/449843 (PineScript v5, FMZ last modified 2024-04-29 16:59:41).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 96-149), SMA 99; stop = the SMA 99 at the signal bar, two-close rule; 10 % of equity
    low <= ma99 <= high and close > ma99 -> entry Long Entry, longStop = ma99, trig = 0;  close < ma99 -> entry Short Entry, shortStop = ma99
    longStop set: trig = close < longStop;  trig[1] and close < longStop -> close Long Entry, longStop = na  (short mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is a close test, not an order: the saved level is the SMA 99 on the signal bar, and
      the position closes at the next open after the second close in a row beyond it; both saved
      levels live on independently, as written (a long's level can survive a reversal to short). A
      close acts only on a held position not reversed by that bar's entry. REVERSAL INTENDED. The 10 %
      of equity size is sizing. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the stop is a two-close test.
    2 generic: PASS, SMA touches with a two-close stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 10 % of equity size stored.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_449843_sma99_touch_two_close_stop_reversal"
FAMILY = "ma_pullback"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma_len": [99, 50],
}
DEFAULT_PARAMS = {"ma_len": 99}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ma = c.rolling(int(p["ma_len"])).mean()
    touch = (lo <= ma) & (h >= ma)
    lc = (touch & (c > ma)).to_numpy()
    sc = (touch & (c < ma)).to_numpy()
    mv, cv = ma.to_numpy(), c.to_numpy(dtype=float)
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    lstop = sstop = np.nan
    ltrig = strig = 0
    for i in range(m):
        new = pos
        lt_prev, st_prev = ltrig, strig
        if lc[i]:
            if new != 1:
                le[i], new = True, 1
            lstop, ltrig = mv[i], 0
        if sc[i]:
            if new != -1:
                se[i], le[i], new = True, False, -1
            sstop, strig = mv[i], 0
        if not np.isnan(lstop):
            ltrig = 1 if cv[i] < lstop else 0
            if lt_prev == 1 and cv[i] < lstop:
                if pos == 1 and new == 1:            # strategy.close acts only on a held, non-reversed long
                    lx[i], new = True, 0
                lstop, ltrig = np.nan, 0
        if not np.isnan(sstop):
            strig = 1 if cv[i] > sstop else 0
            if st_prev == 1 and cv[i] > sstop:
                if pos == -1 and new == -1:
                    sx[i], new = True, 0
                sstop, strig = np.nan, 0
        pos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
