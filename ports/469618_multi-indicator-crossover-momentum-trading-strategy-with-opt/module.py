"""EMA 9 / 21 crossings confirmed by the RSI 14 and the MACD, daily bars: the cross up with the RSI under 70 and the MACD over its signal goes long, the mirror goes short, each with a 3 % target and 1 % stop from the fill; reversing.
Port of FMZ strategy #469618 "Multi Indicator Crossover Momentum Trading Strategy with Optimized Take Profit and Stop Loss System" (Crypto Futures Day Trading with Profit/Limit/Loss).

FMZ source id: 469618

Source
    https://www.fmz.com/strategy/469618 (PineScript v5, FMZ last modified 2024-10-14 11:45:11).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 122-186), EMA 9 / 21; RSI 14, levels 70 / 30; MACD 12 / 26 / 9; target 3 %, stop 1 % of the average price; the risk / reward input unused
    crossover(ema9, ema21) and rsi < 70 and macd > signal -> entry Long;  crossunder and rsi > 30 and macd < signal -> entry Short
    every bar: exit(Long, limit = avg x 1.03, stop = avg x 0.99);  exit(Short, limit = avg x 0.97, stop = avg x 1.01)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket comes from the average (fill) price and is sent every bar: ported active from the
      fill bar (#440797) as the fixed fractions 0.03 / 0.01 of the fill. The risk / reward input is never
      used. REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark
      coarse_bar_stop. The margin settings are not ported. FREQ = "1D" from the backtest header (broker
      days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the fill-price bracket as fixed fractions.
    2 generic: PASS, EMA crossings with RSI and MACD confirmation.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: margin settings stored, not ported.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_469618_ema9_21_cross_rsi_macd_confirm_pct_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [9, 5],
    "slow": [21, 50],
    "tp_pct": [0.03, 0.06],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21, "tp_pct": 0.03, "sl_pct": 0.01, "rsi_len": 14}


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
    a, b = c.ewm(span=int(p["fast"]), adjust=False).mean(), c.ewm(span=int(p["slow"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_len"]))
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    le = (a > b) & (a.shift(1) <= b.shift(1)) & (r < 70) & (macd > sig)
    se = (a < b) & (a.shift(1) >= b.shift(1)) & (r > 30) & (macd < sig)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
