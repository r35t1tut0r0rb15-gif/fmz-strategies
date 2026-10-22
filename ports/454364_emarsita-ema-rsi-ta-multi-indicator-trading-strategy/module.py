"""EMA 4 / 12 crossings on the side of the EMA 48 with an RSI 14 filter, daily bars: the cross up over the EMA 48 with the RSI under 70 goes long, the cross down under it with the RSI over 30 goes short; reversing.
Port of FMZ strategy #454364 "EMARSITA多重指标交易策略-EMA-RSI-TA-Multi-Indicator-Trading-Strategy" (EMA & RSI Strategy with 200 EMA (EMARSI200)).

FMZ source id: 454364

Source
    https://www.fmz.com/strategy/454364 (PineScript v4, FMZ last modified 2024-06-17 16:38:23).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 103-146), EMA 4 / 12; trend EMA 48 (labelled 200); RSI 14, levels 70 / 30
    crossover(ema4, ema12) and rsi < 70 and close > ema48 -> entry Buy;  crossunder and rsi > 30 and close < ema48 -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * There is no exit: positions end at the opposite entry. REVERSAL INTENDED. No sizing code. FREQ =
      "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings with trend and RSI filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_454364_ema4_12_cross_ema48_rsi_filter_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "short_len": [4, 9],
    "long_len": [12, 21],
    "trend_len": [48, 200],
}
DEFAULT_PARAMS = {"short_len": 4, "long_len": 12, "trend_len": 48, "rsi_len": 14, "ob": 70.0, "os": 30.0}


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
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    a = c.ewm(span=int(p["short_len"]), adjust=False).mean()
    b = c.ewm(span=int(p["long_len"]), adjust=False).mean()
    t = c.ewm(span=int(p["trend_len"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_len"]))
    le = (a > b) & (a.shift(1) <= b.shift(1)) & (r < float(p["ob"])) & (c > t)
    se = (a < b) & (a.shift(1) >= b.shift(1)) & (r > float(p["os"])) & (c < t)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
