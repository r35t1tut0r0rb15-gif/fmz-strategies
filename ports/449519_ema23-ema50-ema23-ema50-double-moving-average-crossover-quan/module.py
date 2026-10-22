"""EMA 23 / 50 crossings with EMA 50 stop tests and re-entries, daily bars: a cross up goes long and a cross down goes short; a low under the EMA 50 with the close under its previous value (or a 60 % gain)
closes a long, the mirror (or a 25 % gain) closes a short; trend-side closes beyond the EMA 50 re-enter; reversing.
Port of FMZ strategy #449519 "EMA23-EMA50双均线交叉量化交易策略-EMA23-EMA50-Double-Moving-Average-Crossover-Quantitative-Trading-Strategy" (EMA Crossover Strategy (EMA 23 / 50 with re-entries)).

FMZ source id: 449519

Source
    https://www.fmz.com/strategy/449519 (PineScript v5, FMZ last modified 2024-04-26 15:29:21).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 102-161), EMA 23 / 50; long target avg x 1.6, short target avg x 0.75; start 2022-01-01
    crossover -> entry Buy;  crossunder -> entry Sell;  long and (low < ema50 and close < ema50[1] or close >= avg x 1.6) -> close Buy;  short mirrored (close <= avg x 0.75) -> close Sell
    position <= 0 and high > ema50 and close > ema50 and ema23 > ema50 -> entry Buy;  position >= 0 and the mirror -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The calls run in the script's order with the position held into the bar: a close acts only on
      a held position not reversed by that bar's entries; the re-entry tests read the held position.
      The targets are bar-close tests against the fill price (the next open after the signal). The
      2022 start date is dropped (the data window decides). REVERSAL INTENDED. No sizing code. FREQ =
      "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; close tests against the fill.
    2 generic: PASS, EMA crossings with EMA 50 stop tests and trend re-entries.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_449519_ema23_50_cross_stop_test_reentry_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [23, 12],
    "slow": [50, 100],
}
DEFAULT_PARAMS = {"fast": 23, "slow": 50, "long_tp": 1.6, "short_tp": 0.75}


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
    ef = c.ewm(span=int(p["fast"]), adjust=False).mean()
    es = c.ewm(span=int(p["slow"]), adjust=False).mean()
    buy = ((ef > es) & (ef.shift(1) <= es.shift(1))).to_numpy()
    sell = ((ef < es) & (ef.shift(1) >= es.shift(1))).to_numpy()
    lsl = ((lo < es) & (c < es.shift(1))).to_numpy()
    ssl = ((h > es) & (c > es.shift(1))).to_numpy()
    lre = ((h > es) & (c > es) & (ef > es)).to_numpy()
    sre = ((lo < es) & (c < es) & (ef < es)).to_numpy()
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    ltp, stp = float(p["long_tp"]), float(p["short_tp"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, fp = 0, np.nan
    with np.errstate(invalid="ignore"):
        for i in range(m):
            new = pos

            def entry(d):
                nonlocal new
                if new != d:
                    new = d

            if buy[i]:
                entry(1)
            if sell[i]:
                entry(-1)
            if pos == 1 and new == 1 and (lsl[i] or cv[i] >= fp * ltp):
                new = 0
            if pos == -1 and new == -1 and (ssl[i] or cv[i] <= fp * stp):
                new = 0
            if pos <= 0 and lre[i]:
                entry(1)
            if pos >= 0 and sre[i]:
                entry(-1)
            if new != pos:
                if new == 1:
                    le[i] = True
                elif new == -1:
                    se[i] = True
                elif pos == 1:
                    lx[i] = True
                else:
                    sx[i] = True
                if new != 0:
                    fp = ov[i + 1] if i + 1 < m else np.nan   # the fill: the next bar's open
            pos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
