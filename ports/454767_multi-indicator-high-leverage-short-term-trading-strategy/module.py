"""EMA 5 / 15 crossings confirmed by the RSI 7 and a fast MACD (6 / 13 / 5), daily bars: the cross up with the RSI under 80 and the MACD over its signal goes long, the mirror goes short; each with a stop and a target 1.5 ATR 5 from the signal close; reversing.
Port of FMZ strategy #454767 "Multi Indicator High Leverage Short Term Trading Strategy" (High Leverage Scalping Strategy).

FMZ source id: 454767

Source
    https://www.fmz.com/strategy/454767 (PineScript v5, FMZ last modified 2024-06-21 18:16:24).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 172-222), EMA 5 / 15; RSI 7 (80 / 20); MACD 6 / 13 / 5; ATR 5 x 1.5 stop and target
    crossover(ema5, ema15) and rsi < 80 and macd > signal -> entry Long, exit(limit = close + 1.5 atr, stop = close - 1.5 atr);  the mirror -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels are fixed on the signal bar: ported as the fraction 1.5 x ATR / close of the signal
      bar, applied to the fill. A repeat signal inside a trade re-issues them, which stops() cannot
      express: the opening levels are kept and the module is marked trailing_stop_pending (as
      #434428). REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on 1-day bars:
      mark coarse_bar_stop. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the ATR bracket as fractions of the signal close; re-issued levels pending (mark).
    2 generic: PASS, confirmed EMA crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_454767_ema5_15_cross_rsi_macd_atr_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "short_len": [5, 9],
    "long_len": [15, 21],
    "atr_mult": [1.5, 3.0],
}
DEFAULT_PARAMS = {"short_len": 5, "long_len": 15, "atr_mult": 1.5, "atr_len": 5, "rsi_len": 7}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    a = c.ewm(span=int(p["short_len"]), adjust=False).mean()
    b = c.ewm(span=int(p["long_len"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_len"]))
    macd = c.ewm(span=6, adjust=False).mean() - c.ewm(span=13, adjust=False).mean()
    sig = macd.ewm(span=5, adjust=False).mean()
    le = (a > b) & (a.shift(1) <= b.shift(1)) & (r < 80) & (macd > sig)
    se = (a < b) & (a.shift(1) >= b.shift(1)) & (r > 20) & (macd < sig)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = float(p["atr_mult"]) * _atr(bars_df, p["atr_len"]) / bars_df["close"]
    return {"sl_stop": a.shift(1), "tp_stop": a.shift(1)}


def portfolio_kwargs(**params):
    return {}
