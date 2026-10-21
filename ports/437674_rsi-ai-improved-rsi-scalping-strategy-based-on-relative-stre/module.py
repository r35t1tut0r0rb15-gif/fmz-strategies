"""RSI cross follow-ups, broker days: on the bar after an RSI 14 crossing over 50 or 30 (and not again on this bar) go long; after a crossing under 50 or 70 go short; reversing; the author's tick bracket
(re-sent every bar from the latest close, 10 / 5 ticks) is described, not emitted.
Port of FMZ strategy #437674 "基于RSI和AI自定义条件进行交易的高级策略Improved-RSI-Scalping-Strategy-based-on-Relative-Strength-Index" (Improved RSI Scalping Strategy).

FMZ source id: 437674

Source
    https://www.fmz.com/strategy/437674 (PineScript v5, FMZ last modified 2024-01-04 17:20:57).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 154-191), RSI 14, levels 70 / 30 (and 50); take profit 10 / stop loss 5 (ticks); risk 1 %
    longCondition = crossover(rsi, 50) or aiCondition2Long (a var: computed on the first bar only) or crossover(rsi, 30);  shortCondition mirrors with 50 / 70
    entry Long when longCondition[1] and not longCondition (qty 1), exit(limit = close + 10 ticks, stop = close - 5 ticks) every bar;  short mirror (with the same long-side levels)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The var conditions are evaluated on the first bar only (false: the RSI is undefined there), as
      written. The exit is re-sent every bar from that bar's close, so its levels move after entry, and
      the short side reuses the long levels (a limit above the price); stops() cannot express it, so it is
      kept pending (rule 2, mark trailing_stop_pending; 5 / 10 ticks of 0.1 on BTC against a daily ATR near
      1000 are about 0.0005 / 0.001 ATR). Positions end at the opposite entry until then. The risk-based
      size is computed but not used (qty 1). REVERSAL INTENDED. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: REVIEW, RSI crossings; the every-bar tick bracket is pending.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the risk size formula, fixed quantity and the tick inputs stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_437674_rsi_cross_follow_up"
FAMILY = "rsi_oscillator"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_length": [14, 7],
    "oversold": [30.0, 20.0],
}
DEFAULT_PARAMS = {"rsi_length": 14, "oversold": 30.0}


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


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _rsi(c, n):
    d = c.diff()
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    r = _rsi(bars_df["close"], int(p["rsi_length"]))
    r1 = r.shift(1)
    os_ = float(p["oversold"])
    ob = 100.0 - os_
    lc = ((r > 50) & (r1 <= 50)) | ((r > os_) & (r1 <= os_))
    sc = ((r < 50) & (r1 >= 50)) | ((r < ob) & (r1 >= ob))
    le = lc.shift(1, fill_value=False) & ~lc
    se = sc.shift(1, fill_value=False) & ~sc
    false = pd.Series(False, index=bars_df.index)
    return le & ~se, false, se & ~le, false.copy()


def portfolio_kwargs(**params):
    return {}
