"""Hourly bars: the EMA 17 crossing over the EMA 31 with the close above the session VWAP of hlc3 and the SMA 69 goes long (closing a short first), the mirror goes short (closing a long first); the EMA 8 crossing under the EMA 9 closes a long and crossing over it closes a short, unless an opposite entry fires.
Port of FMZ strategy #489736 "Multi Moving Average Trend Filter Crossover Quantitative Trading Strategy" (EMA+SMA+VWAP Trading Strategy).

FMZ source id: 489736

Source
    https://www.fmz.com/strategy/489736 (PineScript v5, FMZ last modified 2025-04-08 10:18:57).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 188-252), EMA 17 / 31 entries; SMA 69 and session VWAP of hlc3 filters; EMA 8 / 9 exits; long_active / short_active flags
    long_condition = crossover(ema17, ema31) and close > vwap and close > sma69: short_active -> close Short; not long_active -> entry Long
    short_condition mirrored;  long_active and crossunder(ema8, ema9) and not short_condition -> close Long (short mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The orders are followed in the order the script sends them, with the script's own flags beside the
      real position: a close acts only on a position open when it is sent, and an entry fills after the
      closes sent before it. On the rare bar where an entry and its own side's exit both fire, the flag
      is cleared while the entry still fills, so the next exit crossing does not close that trade, as
      written (weird case). ta.vwap(hlc3) restarts each session: the house session is the broker day
      (17:00 America/New_York). REVERSAL INTENDED (close then enter). No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings above / below the VWAP and SMA 69 with faster EMA exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as the session-VWAP weights; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone) for the VWAP reset; no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_489736_ema17_31_cross_vwap_sma69_ema8_9_exit_1h_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "entry_fast": [17, 12],
    "entry_slow": [31, 26],
}
DEFAULT_PARAMS = {"entry_fast": 17, "entry_slow": 31, "sma_len": 69, "exit_fast": 8, "exit_slow": 9}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _cross(a, b):
    return ((a > b) & (a.shift(1) <= b.shift(1))).to_numpy(), ((a < b) & (a.shift(1) >= b.shift(1))).to_numpy()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    ef = c.ewm(span=int(p["entry_fast"]), adjust=False).mean()
    es = c.ewm(span=int(p["entry_slow"]), adjust=False).mean()
    xf = c.ewm(span=int(p["exit_fast"]), adjust=False).mean()
    xs = c.ewm(span=int(p["exit_slow"]), adjust=False).mean()
    sma = c.rolling(int(p["sma_len"])).mean()
    day = broker_day(bars_df.index)
    hlc3 = (h + lo + c) / 3
    vw = (hlc3 * v).groupby(day).cumsum() / v.groupby(day).cumsum()
    up_e, dn_e = _cross(ef, es)
    up_x, dn_x = _cross(xf, xs)
    lc = up_e & ((c > vw) & (c > sma)).to_numpy()
    sc = dn_e & ((c < vw) & (c < sma)).to_numpy()
    m = len(lc)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    tgt, la, sa = 0, False, False
    for i in range(m):
        held = tgt                          # the position after this bar's open
        fin = held                          # the orders fill at the next open, in the order sent
        if lc[i]:
            if sa:
                if held == -1 and fin == -1:
                    fin = 0
                sa = False
            if not la:
                fin, la = 1, True
        if sc[i]:
            if la:
                if held == 1 and fin == 1:
                    fin = 0
                la = False
            if not sa:
                fin, sa = -1, True
        if la and dn_x[i] and not sc[i]:
            if held == 1 and fin == 1:
                fin = 0
            la = False
        if sa and up_x[i] and not lc[i]:
            if held == -1 and fin == -1:
                fin = 0
            sa = False
        if fin != held and i + 1 < m:
            if fin == 1:
                le[i] = True
            elif fin == -1:
                se[i] = True
            elif held == 1:
                lx[i] = True
            else:
                sx[i] = True
            tgt = fin
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
