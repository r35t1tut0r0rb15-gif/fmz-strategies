"""2-day bars: a positive triple-EMA (3) smoothed ROC 7 with MFI 14 (of hlc3) above 50 goes long, a negative one with MFI under 50 goes short; a long closes when the momentum is negative and MFI under 20, a short when it is positive and MFI over 80; reversing.
Port of FMZ strategy #483094 "三重EMA平滑动量与资金流量综合交易策略-Triple-EMA-Smoothed-Momentum-and-Money-Flow-Integrated-Trading-Strategy" (Momentum & Money Flow Strategy with Triple EMA Smoothing).

FMZ source id: 483094

Source
    https://www.fmz.com/strategy/483094 (PineScript v5, FMZ last modified 2025-02-21 13:25:57).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 94-138), ROC 7, triple EMA 3; MFI 14 (hlc3), 50 / 80 / 20; 10 % of equity
    longCondition = smoothedMomentum > 0 and mfi > 50 and position_size <= 0 -> entry Long;  shortCondition = smoothedMomentum < 0 and mfi < 50 and position_size >= 0 -> entry Short
    position_size > 0 and smoothedMomentum < 0 and mfi < 20 -> close Long;  position_size < 0 and smoothedMomentum > 0 and mfi > 80 -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entries are states, taken when flat or against the held side (a reversal). A long's close
      condition also meets the short entry, so it reverses; the closes act only on a position the bar's
      entries leave unchanged. ta.mfi(hlc3, 14) sums volume x hlc3 over up / down hlc3 changes; its
      division by zero is na. 2-day bars are blocks of two broker days counted from 1970-01-01, each
      stamped with its first minute. REVERSAL INTENDED. 10 % of equity is sizing. FREQ = "2D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, smoothed momentum side confirmed by money flow.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per 2-day bar) in the MFI 14; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker days in 2-day blocks (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483094_triple_ema_roc_mfi_state_2d_reversal"
FAMILY = "momentum"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (two broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "roc_len": [7, 14],
    "smooth": [3, 5],
}
DEFAULT_PARAMS = {"days": 2, "roc_len": 7, "smooth": 3, "mfi_len": 14}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _multiday(raw_1m_df, days):
    """Blocks of `days` broker days counted from 1970-01-01, each stamped with its first minute."""
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    key = np.asarray((broker_day(df.index) - pd.Timestamp("1970-01-01")).days // days)
    bars = df.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    first = pd.Series(df.index, index=df.index).groupby(key).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    return _multiday(raw_1m_df, int(p["days"]))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    k, sm = int(p["roc_len"]), int(p["smooth"])
    roc = 100 * (c / c.shift(k) - 1)
    mom = roc.ewm(span=sm, adjust=False).mean().ewm(span=sm, adjust=False).mean().ewm(span=sm, adjust=False).mean()
    src = (h + lo + c) / 3
    chg = src.diff()
    n = int(p["mfi_len"])
    pos_f = (v * src.where(~(chg <= 0), 0.0)).rolling(n).sum()
    neg_f = (v * src.where(~(chg >= 0), 0.0)).rolling(n).sum()
    mfi = 100.0 - 100.0 / (1.0 + pos_f / neg_f.where(neg_f != 0))
    buy, sell = ((mom > 0) & (mfi > 50)).to_numpy(), ((mom < 0) & (mfi < 50)).to_numpy()
    ex_l, ex_s = ((mom < 0) & (mfi < 20)).to_numpy(), ((mom > 0) & (mfi > 80)).to_numpy()
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        new = pos
        if buy[i] and new != 1:
            new = 1
        if sell[i] and new != -1:
            new = -1
        if new == pos:
            if pos == 1 and ex_l[i]:
                new = 0
            elif pos == -1 and ex_s[i]:
                new = 0
        if new != pos:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif pos == 1:
                lx[i] = True
            else:
                sx[i] = True
            pos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
