"""Tale indicators, as written, broker days: EMA 3 crossing above EMA 15 of highs goes long, crossing
under EMA 15 of lows goes short; "re-enter" and "exit" tests on EMA 3 / candle positions drive the
script's own position flags, which gate the re-entries and the closes exactly as the source orders
them (including its flag slips).
Port of FMZ strategy #427526 "Momentum Moving Average Crossover Strategy".

FMZ source id: 427526

Source
    https://www.fmz.com/strategy/427526 (PineScript v4, FMZ last modified 2023-09-21 21:29:22).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 197-320), fast 3, slow 15, exit fast 3, tuner 0.005
    enter_long = crossover(ema3, ema15(high)); enter_short = crossunder(ema3, ema15(low))
    exit_long = crossunder(ema3, ema15(high)); exit_short = crossover(ema3, ema15(high))  (as written)
    bull_exit / bear_exit / bull_reenter / bear_reenter as lines 243-256
    flags long_position_open / short_position_open updated in lines 284-312, THEN the orders:
    LO on enter_long, or on bull_reenter while the flag is off; close LO on bull_exit while the flag is on;
    SO likewise (lines 315-320)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Ported AS WRITTEN, including the slips: the short-exit cross uses the HIGH EMA, bear_r tests
      bull_exit[2], and bear_reenter sets the LONG flag. The orders read the flags after this bar's
      updates (script order), so most closes are pre-empted; positions mostly change by reversal.
      A cleaned-up version is a decision owed.
    * qty 4 / 1 per entry is sizing; pyramiding 0 (same-direction entries are ignored).
    * The 0.005 exit tuner is a price ratio (kept). window() is the constant true.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
    * strategy.entry reverses: REVERSAL INTENDED; entries win over same-bar closes.
    * FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MA lengths and a price ratio.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty 4 / 1, capital and commission stored in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427526_tale_indicators_as_written"
FAMILY = "ma_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len_fast": [3, 5],
    "len_slow": [15, 30],
    "exit_tuner": [0.005, 0.01],
}
DEFAULT_PARAMS = {"len_fast": 3, "len_slow": 15, "len_fast_exit": 3, "exit_tuner": 0.005}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    nf, ns, nfe = int(p["len_fast"]), int(p["len_slow"]), int(p["len_fast_exit"])
    fast = c.ewm(span=nf, adjust=False).mean()
    slow_len = h.ewm(span=ns, adjust=False).mean()          # slowMALEn (and slowMALEx, as written)
    slow_sen = lo.ewm(span=ns, adjust=False).mean()         # slowMASEn
    fmae = c.ewm(span=nfe, adjust=False).mean()

    def xo(a, b):
        return (a > b) & (a.shift(1) <= b.shift(1))

    def xu(a, b):
        return (a < b) & (a.shift(1) >= b.shift(1))

    enter_long, enter_short = xo(fast, slow_len), xu(fast, slow_sen)
    exit_long, exit_short = xu(fmae, slow_len), xo(fmae, slow_len)
    bull, bear = fast > slow_len, fast < slow_sen
    t = float(p["exit_tuner"])
    bull_exit = (bull & (lo > fmae * (1 + t))) | exit_long | (~bear & (fmae > h))
    bear_exit = (bear & (fmae * (1 - t) > h)) | exit_short | (~bull & (lo > fmae))
    be1, be2 = bull_exit.shift(1, fill_value=False), bull_exit.shift(2, fill_value=False)
    se1 = bear_exit.shift(1, fill_value=False)
    bull_r = bull & (be1 | (be2 & be1)) & (lo <= fmae)
    bear_r = bear & (se1 | (be2 & be1)) & (fmae <= h)
    bull_re = (bull_r & ~enter_long).to_numpy()
    bear_re = (bear_r & ~enter_short).to_numpy()
    el, es = enter_long.to_numpy(), enter_short.to_numpy()
    bx, sxv = bull_exit.to_numpy(), bear_exit.to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    lpo = spo = False
    pos = 0
    for i in range(m):
        if el[i] and not bx[i] and not lpo:
            lpo = True
            if spo:
                spo = False
        if bull_re[i] and not lpo:
            lpo = True
        if bx[i] and lpo:
            lpo = False
        if es[i] and not sxv[i] and not spo:
            spo = True
            if lpo:
                lpo = False
        if bear_re[i] and not spo:
            lpo = True                                       # as written (the source sets the long flag)
        if sxv[i] and spo:
            spo = False
        long_e = el[i] or (bull_re[i] and not lpo)
        long_c = bx[i] and lpo
        short_e = es[i] or (bear_re[i] and not spo)
        short_c = sxv[i] and spo
        if long_e and pos != 1:
            pos = 1
        elif short_e and pos != -1:
            pos = -1
        elif pos == 1 and long_c:
            pos = 0
        elif pos == -1 and short_c:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
