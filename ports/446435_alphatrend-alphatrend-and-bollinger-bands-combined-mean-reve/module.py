"""Broker days: the close crossing over the upper Bollinger band (20, 2) on the bar the AlphaTrend line (MFI 14, ATR = SMA 20 of the true range) turns up goes long; the close crossing under the lower band as AlphaTrend turns down goes short; reversing.
Port of FMZ strategy #446435 "AlphaTrend和布林带相结合的均值回归趋势跟踪策略AlphaTrend-and-Bollinger-Bands-Combined-Mean-Reversion-Trend-Following-Strategy" (AT_BB120324 (AlphaTrend and Bollinger Bands, brlu99)).

FMZ source id: 446435

Source
    https://www.fmz.com/strategy/446435 (PineScript v5, FMZ last modified 2024-03-28 16:32:35).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 177-216), AlphaTrend multiplier 1, period 14 (MFI on hlc3); BB 20 x 2
    AlphaTrend := mfi(hlc3, 14) >= 50 ? (upT < nz(AT[1]) ? nz(AT[1]) : upT) : (downT > nz(AT[1]) ? nz(AT[1]) : downT)
    longCondition = crossover(close, upper) and crossover(AT, AT[1]) -> entry Buy;  shortCondition mirror -> entry Sell;  exit("Buy", "longExit_AT_6", ...) / exit("Sell", "shortExit_AT_6", ...)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exits name entries that do not exist ("longExit_AT_6" / "shortExit_AT_6"), so they never act
      (weird case): positions end only by the reversal. AlphaTrend starts from 0 (nz) and ratchets with
      upT = low - ATR, downT = high + ATR. Pine's stdev is the population deviation. REVERSAL INTENDED. No
      sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger breakouts on AlphaTrend turns.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the MFI 14 that switches AlphaTrend; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_446435_alphatrend_turn_bollinger_breakout_reversal"
FAMILY = "bollinger_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ap": [14, 21],
    "bb_mult": [2.0, 1.5],
}
DEFAULT_PARAMS = {"coeff": 1.0, "ap": 14, "atr_len": 20, "bb_len": 20, "bb_mult": 2.0}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    atr = tr.rolling(int(p["atr_len"])).mean()
    up_t = (lo - atr * float(p["coeff"])).to_numpy()
    dn_t = (h + atr * float(p["coeff"])).to_numpy()
    bull = (_mfi((h + lo + c) / 3, v, int(p["ap"])) >= 50).to_numpy()
    m = len(up_t)
    at = np.full(m, np.nan)
    prev = 0.0
    for i in range(m):
        if bull[i]:
            val = prev if up_t[i] < prev else up_t[i]
        else:
            val = prev if dn_t[i] > prev else dn_t[i]
        at[i] = val
        prev = 0.0 if np.isnan(val) else val
    a = pd.Series(at, index=c.index)
    turn_up = (a > a.shift(1)) & (a.shift(1) <= a.shift(2))
    turn_dn = (a < a.shift(1)) & (a.shift(1) >= a.shift(2))
    n = int(p["bb_len"])
    basis = c.rolling(n).mean()
    dev = c.rolling(n).std(ddof=0) * float(p["bb_mult"])
    upper, lower = basis + dev, basis - dev
    lg = (c > upper) & (c.shift(1) <= upper.shift(1)) & turn_up
    sh = (c < lower) & (c.shift(1) >= lower.shift(1)) & turn_dn
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return lg.astype(bool), false, sh.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
