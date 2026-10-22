"""Band re-entries after stochastic-RSI extremes, daily bars, with the script's sides swapped: a close falling back under the upper band (20, 2) after K and D over 90 goes LONG, a close rising back over the
lower band after K and D under 10 goes SHORT; reversing.
Port of FMZ strategy #448061 "布林带随机RSI极值信号策略-Bollinger-Bands-Stochastic-RSI-Extreme-Signal-Strategy" (BBSR Extreme (Bollinger Bands Stochastic RSI Extreme Signal)).

FMZ source id: 448061

Source
    https://www.fmz.com/strategy/448061 (PineScript v5, FMZ last modified 2024-04-12 16:36:42).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 99-156), BB 20 / 2; stochastic RSI: RSI 14, stoch 14, K / D 3; limits 90 / 10
    Bear = close[1] > upper[1] and close < upper and k[1] > 90 and d[1] > 90 -> entry "Enter Long" (long);  else Bull = mirrored at the lower band, k / d < 10 -> entry "Enter Short" (short)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The script sends a LONG on its "Bear" signal and a SHORT on its "Bull" signal, as written (the
      labels and the plotted triangles say the opposite); ported as the orders are sent. k = sma(
      stoch(rsi, rsi, rsi, 14), 3), d = sma(k, 3). Pine's stdev is the population deviation. No exit:
      positions end at the opposite entry. REVERSAL INTENDED. No sizing code. FREQ = "1D" from the
      backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band re-entries after stochastic-RSI extremes (sides as sent).
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

NAME = "fmz_448061_band_reentry_stochrsi_extreme_swapped_sides_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "upper_limit": [90.0, 80.0],
}
DEFAULT_PARAMS = {"length": 20, "upper_limit": 90.0, "lower_limit": 10.0, "mult": 2.0, "k": 3, "d": 3, "rsi_len": 14, "stoch_len": 14}


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
    n = int(p["length"])
    basis, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    upper = basis + float(p["mult"]) * sd
    lower = basis - float(p["mult"]) * sd
    r = _rsi(c, int(p["rsi_len"]))
    sn = int(p["stoch_len"])
    lo_r, hi_r = r.rolling(sn).min(), r.rolling(sn).max()
    st = 100 * (r - lo_r) / (hi_r - lo_r).where(hi_r > lo_r)
    k = st.rolling(int(p["k"])).mean()
    d = k.rolling(int(p["d"])).mean()
    ul, ll = float(p["upper_limit"]), float(p["lower_limit"])
    bear = (c.shift(1) > upper.shift(1)) & (c < upper) & (k.shift(1) > ul) & (d.shift(1) > ul)
    bull = (c.shift(1) < lower.shift(1)) & (c > lower) & (k.shift(1) < ll) & (d.shift(1) < ll)
    false = pd.Series(False, index=bars_df.index)
    return bear, false, bull & ~bear, false.copy()     # sides as sent: Bear -> long, Bull -> short


def portfolio_kwargs(**params):
    return {}
