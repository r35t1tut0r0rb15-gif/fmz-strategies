"""Bollinger 20 / 2 and RSI 14 extremes, 2-day bars: a close under the lower band with the RSI under 30 goes long, the mirror goes short, each with a 1 ATR stop and 0.75 ATR target from the signal close; reversing.
Port of FMZ strategy #471689 "High Win Rate Trend Mean Reversion Trading Strategy" (High Win Rate Mean Reversion Strategy for Gold).

FMZ source id: 471689

Source
    https://www.fmz.com/strategy/471689 (PineScript v5, FMZ last modified 2024-11-12 14:45:46).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 123-185), BB 20, 2 sd; RSI 14, levels 30 / 70; ATR 14: stop 1 x, target 0.75 x; risk 2 % of equity per trade
    close < lower and rsi < 30 -> entry Long (qty = risk / stop distance) + exit(limit = close + 0.75 atr, stop = close - atr);  the mirror -> entry Short + exit (mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entry tests are states, so the signal and its exit are re-sent on every bar while they hold:
      the opening levels are kept, as ATR multiples of the signal bar shifted into the fill (as #434428,
      mark trailing_stop_pending). The risk-based quantity is not ported (sizing is the optimisation
      layer's). The title names gold; the rules are generic. REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). Stops on 2-day bars: mark coarse_bar_stop. FREQ = "2D" from the
      backtest header (blocks of two broker days, as _multiday).

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket at entry.
    2 generic: PASS, band and RSI extremes with a tight ATR bracket.
    3 crypto-exchange-only: no (exchange pair in the header only (gold named in the title)).
    4 signals only: equity-risk quantity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_471689_bb20_rsi_extreme_atr_bracket_reversal_2d"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (two broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "bb_length": [20, 50],
    "rr": [0.75, 1.5],
}
DEFAULT_PARAMS = {"bb_length": 20, "rr": 0.75, "atr_len": 14, "rsi_len": 14, "days": 2}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _multiday(raw_1m_df, days):
    """Blocks of `days` broker days counted from 1970-01-01, each stamped with its first minute."""
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    key = np.asarray((broker_day(df.index) - pd.Timestamp("1970-01-01")).days // days)
    bars = df.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(key).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    return _multiday(raw_1m_df, int(p["days"]))


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
    n = int(p["bb_length"])
    basis = c.rolling(n).mean()
    dev = 2.0 * c.rolling(n).std(ddof=0)
    r = _rsi(c, int(p["rsi_len"]))
    le = (c < basis - dev) & (r < 30)
    se = (c > basis + dev) & (r > 70)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = _atr(bars_df, p["atr_len"]) / bars_df["close"]
    return {"sl_stop": a.shift(1), "tp_stop": (float(p["rr"]) * a).shift(1)}


def portfolio_kwargs(**params):
    return {}
