"""EMA 50 / 200 trend with RSI and MACD states, daily bars: in an up-trend with RSI over 55 and MACD over its signal it goes long, in a down-trend with RSI under 45 and MACD under its signal it goes short; a long closes when the up-trend or the MACD lead ends, a short on the mirror; reversing.
Port of FMZ strategy #474847 "趋势波段交易EMA-MACD复合策略-EMA-MACD-Composite-Strategy-for-Trend-Scalping" (TrendScalp Bot).

FMZ source id: 474847

Source
    https://www.fmz.com/strategy/474847 (PineScript v6, FMZ last modified 2024-12-12 15:05:37).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 97-143), EMA 50 / 200; RSI 14, 55 / 45; MACD 12 / 26 / 9; 100 % of equity
    up-trend and rsi > 55 and macd > signal -> entry Buy;  down-trend and rsi < 45 and macd < signal -> entry Sell;  not up-trend or not (macd > signal) -> close Buy;  not down-trend or not (macd < signal) -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * A close coinciding with the opposite entry only repeats the reversal (#437773), so it is masked on
      entry bars; a side's entry and its own close cannot hold on one bar. REVERSAL INTENDED. The equity
      share is not ported. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, trend / momentum states with state-end closes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: percent-of-equity size stored, not ported.
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

NAME = "fmz_474847_ema50_200_trend_rsi_macd_state_reversal"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [50, 20],
    "slow": [200, 100],
}
DEFAULT_PARAMS = {"fast": 50, "slow": 200}


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
    f, s = c.ewm(span=int(p["fast"]), adjust=False).mean(), c.ewm(span=int(p["slow"]), adjust=False).mean()
    r = _rsi(c, 14)
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    up, dn = f > s, f < s
    le = up & (r > 55) & (macd > sig)
    se = dn & (r < 45) & (macd < sig)
    lx = (~up | ~(macd > sig)) & ~se
    sx = (~dn | ~(macd < sig)) & ~le
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
