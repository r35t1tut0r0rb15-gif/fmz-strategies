"""EMA 12 / 26, MACD and RSI agreement, daily bars: the EMA 12 over the EMA 26 with the MACD over its signal and the RSI under 70 goes long, the mirror with the RSI over 30 goes short, each with a 1.5 ATR target and stop from the signal close; reversing.
Port of FMZ strategy #458255 "Multi Indicator Comprehensive Momentum Trading Strategy" (Bank Nifty Comprehensive Strategy).

FMZ source id: 458255

Source
    https://www.fmz.com/strategy/458255 (PineScript v5, FMZ last modified 2024-07-31 12:01:10).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 168-219), EMA 12 / 26; MACD 12 / 26 / 9; RSI 14, levels 70 / 30; ATR 14 x 1.5
    ema12 > ema26 and macd > signal and rsi < 70 -> entry Long + exit(limit = close + 1.5 atr, stop = close - 1.5 atr);  the mirror with rsi > 30 -> entry Short + exit (mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entry tests are states, so the signal and its exit are re-sent on every bar while they hold:
      the opening levels are kept, as ATR multiples of the signal bar shifted into the fill (as #434428,
      mark trailing_stop_pending). The title names Bank Nifty; the rules are generic. REVERSAL INTENDED.
      Stop module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. No
      sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket at entry.
    2 generic: PASS, EMA, MACD and RSI agreement with an ATR bracket.
    3 crypto-exchange-only: no (exchange pair in the header only (Bank Nifty named in the title)).
    4 signals only: no sizing code.
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

NAME = "fmz_458255_ema_macd_rsi_agreement_atr_bracket_reversal"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atr_mult": [1.5, 3.0],
    "rsi_len": [14, 7],
}
DEFAULT_PARAMS = {"atr_mult": 1.5, "rsi_len": 14, "atr_len": 14}


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
    e12, e26 = c.ewm(span=12, adjust=False).mean(), c.ewm(span=26, adjust=False).mean()
    macd = e12 - e26
    sig = macd.ewm(span=9, adjust=False).mean()
    r = _rsi(c, int(p["rsi_len"]))
    le = (e12 > e26) & (macd > sig) & (r < 70)
    se = (e12 < e26) & (macd < sig) & (r > 30)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    f = float(p["atr_mult"]) * _atr(bars_df, p["atr_len"]) / bars_df["close"]
    return {"sl_stop": f.shift(1), "tp_stop": f.shift(1)}


def portfolio_kwargs(**params):
    return {}
