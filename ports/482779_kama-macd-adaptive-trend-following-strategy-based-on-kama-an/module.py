"""Closes crossing a KAMA (50, fast 3, slow 30) with MACD 26 / 52 / 18 on the matching side of its signal, broker days, long only: the cross up goes long, the cross down closes; the 3 ATR stop and target re-sent every bar from the latest close are pending.
Port of FMZ strategy #482779 "基于KAMA与MACD的自适应趋势跟踪量化交易策略-Adaptive-Trend-Following-Strategy-Based-on-KAMA-and-MACD-Integration" (4-Hour KAMA Strategy).

FMZ source id: 482779

Source
    https://www.fmz.com/strategy/482779 (PineScript v5, FMZ last modified 2025-02-20 15:01:37).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 105-144), KAMA 50 / 3 / 30 (loop, seeded at the close); ATR 14 x 3.0; MACD 26 / 52 / 18; 10 % of equity
    er = |close - close[50]| / sum(|close[i] - close[i+1]|, i < 50);  sc = (er (2/4 - 2/31) + 2/31)^2;  kama := na(kama[1]) ? close : kama[1] + sc (close - kama[1])
    crossover(close, kama) and macd > signal -> entry Buy;  crossunder(close, kama) and macd < signal -> close Buy;  every bar: exit(stop = close - 3 atr, limit = close + 3 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The KAMA is kept as written: it is seeded with the close whenever its previous value is na, so it
      alternates close / na until the efficiency ratio exists, and a zero noise sum makes it na for a bar.
      The bracket is re-sent on every bar from that bar's close: stops() cannot express a level re-set
      every bar, so it is described here and kept pending (as #438034, mark trailing_stop_pending); longs
      end at the down-crossing until then. Long only. The 10 % of equity size is sizing. The source
      carries the Mozilla Public License 2.0 notice. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; re-sent ATR bracket described (pending).
    2 generic: PASS, KAMA crossings with a MACD side filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482779_kama50_cross_macd26_52_side_long"
FAMILY = "adaptive_average"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ama_length": [50, 20],
    "slow_length": [30, 60],
}
DEFAULT_PARAMS = {"ama_length": 50, "slow_length": 30, "fast_length": 3}


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
    c = bars_df["close"]
    n = int(p["ama_length"])
    pc = (c - c.shift(n)).abs()
    vs = c.diff().abs().rolling(n).sum()
    er = (pc / vs).where(vs > 0)
    fa, sl = 2 / (float(p["fast_length"]) + 1), 2 / (float(p["slow_length"]) + 1)
    sc = ((er * (fa - sl) + sl) ** 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    kama = np.full(m, np.nan)
    prev = np.nan
    for i in range(m):
        prev = cv[i] if np.isnan(prev) else prev + sc[i] * (cv[i] - prev)   # na sc gives na
        kama[i] = prev
    k = pd.Series(kama, index=c.index)

    def ema(x, nn):
        return x.ewm(span=nn, adjust=False).mean()

    macd = ema(c, 26) - ema(c, 52)
    sig = ema(macd, 18)
    le = (c > k) & (c.shift(1) <= k.shift(1)) & (macd > sig)
    lx = (c < k) & (c.shift(1) >= k.shift(1)) & (macd < sig)
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
