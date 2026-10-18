"""Fisher stochastic of the relative vigor index, broker days: with the "opposite trade" input on, the signal crossing under its previous value beyond 0.76 goes long and crossing over goes
short (reversing); a position with a negative open profit more than eight bars after its entry is closed.
Port of FMZ strategy #436218 "Ehlers Fisher Stochastic Relative Vigor Index Strategy" (Ehlers Fisher Stochastic Relative Vigor Index Strategy).

FMZ source id: 436218

Source
    https://www.fmz.com/strategy/436218 (PineScript v3, FMZ last modified 2023-12-22 12:04:23).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 122-154), length 10; opposite trade on
    RVI = sum((CO + 2 CO[1] + 2 CO[2] + CO[3]) / 6, 10) / sum((HL + 2 HL[1] + 2 HL[2] + HL[3]) / 6, 10);  signal = FisherStoch(RVI, 10);  trigger = signal[1]
    oppositeTrade: crossunder(signal, trigger) and |signal| > 2 / 2.64 -> entry long;  crossover -> entry short;  openprofit < 0 and barsSinceEntry > 8 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * FisherStoch(src, len) = 0.5 log((1 + 1.98 (v - 0.5)) / (1 - 1.98 (v - 0.5))) / 2.64 with v the 1-2-3-4
      weighted average of stoch(src, len) / 100. The open profit is the close against the entry fill (the next
      open); barsSinceEntry counts bars since the last entry signal or since the position went flat.
      The three orders of one bar are filled in the script's call order at the next open (long entry, short
      entry, close_all). REVERSAL INTENDED. The full-equity size is sizing. Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; exit on closes.
    2 generic: PASS, Fisher stochastic of a vigor index.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and pyramiding stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436218_fisher_stochastic_rvi"
FAMILY = "momentum_oscillator"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "p": [10, 14],
    "opposite_trade": [True, False],
}
DEFAULT_PARAMS = {"p": 10, "opposite_trade": True, "bars_limit": 8}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["p"])
    co, hl = c - o, h - lo
    v1 = (co + 2 * co.shift(1) + 2 * co.shift(2) + co.shift(3)) / 6
    v2 = (hl + 2 * hl.shift(1) + 2 * hl.shift(2) + hl.shift(3)) / 6
    num, den = v1.rolling(n).sum(), v2.rolling(n).sum()
    with np.errstate(invalid="ignore", divide="ignore"):
        rvi = (num / den).where(den != 0, 0.0)
        s = (rvi - rvi.rolling(n).min()) / (rvi.rolling(n).max() - rvi.rolling(n).min())
        val1 = s
        val2 = (4 * val1 + 3 * val1.shift(1) + 2 * val1.shift(2) + val1.shift(3)) / 10
        x = 1.98 * (val2 - 0.5)
        signal = 0.5 * np.log((1 + x) / (1 - x)) / 2.64
    trigger = signal.shift(1)
    big = signal.abs() > 2 / 2.64
    opp = bool(p["opposite_trade"])
    up_x = (signal > trigger) & (signal.shift(1) <= trigger.shift(1))
    dn_x = (signal < trigger) & (signal.shift(1) >= trigger.shift(1))
    long_sig = (((up_x & (not opp)) | (dn_x & opp)) & big).fillna(False).to_numpy()
    short_sig = (((dn_x & (not opp)) | (up_x & opp)) & big).fillna(False).to_numpy()
    cv, ov = c.to_numpy(dtype=float), o.to_numpy(dtype=float)
    m = len(cv)
    held = np.zeros(m, dtype=np.int8)
    pos, avg, bse = 0, np.nan, 0
    ops = []
    for i in range(m):
        if i > 0:                            # fills at this bar's open, in the script's call order
            for op in ops:
                if op == "eL" and pos <= 0:
                    pos, avg = 1, ov[i]
                elif op == "eS" and pos >= 0:
                    pos, avg = -1, ov[i]
                elif op == "X" and pos != 0:
                    pos, avg = 0, np.nan
        held[i] = pos
        ops = []
        bse = bse + 1
        if pos == 0:
            bse = 0
        if long_sig[i]:
            ops.append("eL")
            bse = 0
        if short_sig[i]:
            ops.append("eS")
            bse = 0
        open_profit_neg = (pos == 1 and cv[i] < avg) or (pos == -1 and cv[i] > avg)
        if open_profit_neg and bse > int(p["bars_limit"]):
            ops.append("X")
            bse = 0
    nxt = np.concatenate((held[1:], held[-1:]))
    ix = bars_df.index
    return (pd.Series((nxt == 1) & (held != 1), index=ix), pd.Series((nxt == 0) & (held == 1), index=ix),
            pd.Series((nxt == -1) & (held != -1), index=ix), pd.Series((nxt == 0) & (held == -1), index=ix))


def portfolio_kwargs(**params):
    return {}
