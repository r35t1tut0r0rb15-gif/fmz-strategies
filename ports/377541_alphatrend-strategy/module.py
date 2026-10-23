"""AlphaTrend (MFI 14 of hlc3 at 50 choosing a ratcheting low - 1 ATR or high + 1 ATR line, ATR = SMA 14 of the true range), broker days: the line crossing over its value two bars back goes long, crossing under goes short; reversing.
Port of FMZ strategy #377541 "AlphaTrend Strategy" (AlphaTrend Strategy).

FMZ source id: 377541

Source
    https://www.fmz.com/strategy/377541 (PineScript v5, FMZ last modified 2022-08-12 16:51:26).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 61-99), coeff 1; period 14; ATR = sma(tr, 14); MFI(hlc3, 14) (the no-volume RSI switch off)
    AlphaTrend := mfi(hlc3, 14) >= 50 ? (low - atr < AT[1] ? AT[1] : low - atr) : (high + atr > AT[1] ? AT[1] : high + atr)   (AT[1] via nz)
    crossover(AlphaTrend, AlphaTrend[2]) -> entry Long;  crossunder(AlphaTrend, AlphaTrend[2]) -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The line starts from nz(AT[1]) = 0 and ratchets as written; ta.tr is na on the first bar. ta.mfi(hlc3,
      14) as Pine defines it (100 when the falling flow is 0, 0 when the rising flow is 0). The signal
      compares the line with itself two bars back (the KivancOzbilgic original; #360014 is the FMZ variant
      that crosses the low / high over the line, with coeff 5). The BUY / SELL label filter (O1 > K2) only
      feeds plots. REVERSAL INTENDED. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MFI-switched ATR trailing line against its own lag.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: margin 100 % long / short stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG377541 (3 members, best partner #426357, Jaccard 0.942); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in ta.mfi(hlc3, 14); exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_377541_alphatrend_mfi14_atr1_line_lag2_cross_reversal"
FAMILY = "atr_trailing_line"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "coeff": [1.0, 2.0],
    "ap": [14, 8],
}
DEFAULT_PARAMS = {"coeff": 1.0, "ap": 14}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    at = alpha_trend(bars_df, float(p["coeff"]), int(p["ap"]))
    a2 = at.shift(2)
    le = (at > a2) & (at.shift(1) <= a2.shift(1))
    se = (at < a2) & (at.shift(1) >= a2.shift(1)) & ~le
    false = pd.Series(False, index=at.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
