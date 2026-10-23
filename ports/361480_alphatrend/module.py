"""AlphaTrend (MFI 8 of hlc3 at 50 choosing a ratcheting low - 1 ATR or high + 1 ATR line, ATR = SMA 8 of the true range), broker days: the line crossing over its value two bars back goes long when the last such down-cross is more recent than the previous up-cross, the mirror goes short; reversing.
Port of FMZ strategy #361480 "AlphaTrend" (AlphaTrend).

FMZ source id: 361480

Source
    https://www.fmz.com/strategy/361480 (PineScript v5, FMZ last modified 2022-05-06 15:49:16).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 80-115), coeff 1; period 8; MFI(hlc3, 8) (the no-volume RSI switch off); signals shown
    AlphaTrend as #360014 with coeff 1, period 8;  buy = crossover(AT, AT[2]);  sell = crossunder(AT, AT[2])
    buy and barssince(buy[1]) > barssince(sell) -> entry long;  else sell and barssince(sell[1]) > barssince(buy) -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The same line as #360014 with the author's defaults (coeff 1, period 8; MFI, the "no volume data"
      switch is off). The barssince tests keep the signals alternating: a buy counts only when a sell came
      after the previous buy (na before the first of each, which fails the test). REVERSAL INTENDED. No
      sizing code. The source carries the Mozilla Public License 2.0 notice. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MFI-switched ATR trailing line turns, alternating.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in ta.mfi(hlc3, 8); exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_361480_alphatrend_mfi8_atr1_two_bar_turn_alternating_reversal"
FAMILY = "atr_trailing_line"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "coeff": [1.0, 2.0],
    "ap": [8, 14],
}
DEFAULT_PARAMS = {"coeff": 1.0, "ap": 8}


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


def _mfi(src, vol, n):
    """Pine ta.mfi: money-flow ratio over n bars; 100 when the falling flow is 0, 0 when the rising is 0."""
    ch = src.diff()
    upper = (vol * src.where(~(ch <= 0), 0.0)).rolling(n).sum()
    lower = (vol * src.where(~(ch >= 0), 0.0)).rolling(n).sum()
    out = 100.0 - 100.0 / (1.0 + upper / lower.where(lower != 0))
    return out.where(upper != 0, 0.0).where(lower != 0, 100.0).where(upper.notna() & lower.notna())


def alpha_trend(bars_df, coeff, ap):
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    atr = tr.rolling(ap).mean()
    up_t = (lo - atr * coeff).to_numpy(dtype=float)
    dn_t = (h + atr * coeff).to_numpy(dtype=float)
    bull = (_mfi((h + lo + c) / 3, v, ap) >= 50).to_numpy()
    m = len(up_t)
    at = np.zeros(m)
    prev = 0.0
    for i in range(m):
        if bull[i]:
            at[i] = prev if up_t[i] < prev else up_t[i]
        else:
            at[i] = prev if dn_t[i] > prev else dn_t[i]
        prev = 0.0 if np.isnan(at[i]) else at[i]      # nz(AlphaTrend[1])
    return pd.Series(at, index=c.index)


def _barssince(cond):
    """Pine ta.barssince: bars since cond was last true (NaN before the first true)."""
    a = np.asarray(cond, dtype=bool)
    idx = np.maximum.accumulate(np.where(a, np.arange(len(a)), -1))
    return np.where(idx >= 0, np.arange(len(a)) - idx, np.nan)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    at = alpha_trend(bars_df, float(p["coeff"]), int(p["ap"]))
    a2 = at.shift(2)
    buy = ((at > a2) & (at.shift(1) <= a2.shift(1))).to_numpy()
    sell = ((at < a2) & (at.shift(1) >= a2.shift(1))).to_numpy()
    k1, k2 = _barssince(buy), _barssince(sell)
    o1 = _barssince(np.r_[False, buy[:-1]])
    o2 = _barssince(np.r_[False, sell[:-1]])
    le = buy & (o1 > k2)
    se = sell & (o2 > k1) & ~le
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
