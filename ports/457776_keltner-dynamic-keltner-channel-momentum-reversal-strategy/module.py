"""Pullbacks to the middle of a wide Keltner channel (SMA 20 +- 6 ATR 35), daily bars: after the upper line was touched within the last 120 bars, a bar whose wick touches the middle line with the close over the EMA 280 goes long with a stop 5.5 ATR (previous bar) under the close; the mirror goes short; touching the opposite outer line closes; reversing.
Port of FMZ strategy #457776 "动态Keltner通道动量反转策略-Dynamic-Keltner-Channel-Momentum-Reversal-Strategy" (Keltner Channel Pullback and Entry Strategy).

FMZ source id: 457776

Source
    https://www.fmz.com/strategy/457776 (PineScript v5, FMZ last modified 2024-07-26 15:02:39).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 274-344), SMA 20; ATR 35; channel 6 ATR; EMA 280; touch lookback 120 bars (1 .. 120 back); stop 5.5 x ATR[1] from the signal close
    upper touched in bars 1-120 and low <= basis <= high and close > ema280 -> entry Long, exit(stop = close - 5.5 atr[1]);  the mirror -> entry Short
    long and high >= upper -> close Long;  short and low <= lower -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is fixed on the signal bar from its close and the previous bar's ATR: ported as the
      fraction 5.5 x ATR[1] / close of the signal bar, applied to the fill. A repeat signal inside a
      trade re-issues it, which stops() cannot express: the opening level is kept and the module is
      marked trailing_stop_pending (as #434428). The outer-line closes are bar-close tests filled at
      the next open (barstate.isnew is true on historical bars); a close on a bar that also reverses
      finds the trade reversed. REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops
      on 1-day bars: mark coarse_bar_stop. No sizing code. FREQ = "1D" from the backtest header
      (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the ATR stop as a fraction of the signal close; re-issued stops pending (mark).
    2 generic: PASS, Keltner middle-line pullbacks after an outer touch.
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

NAME = "fmz_457776_keltner_touch_then_middle_pullback_reversal"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "kc_mult": [6.0, 3.0],
    "ema_len": [280, 100],
    "lookback": [120, 50],
}
DEFAULT_PARAMS = {"kc_mult": 6.0, "ema_len": 280, "lookback": 120, "atr_len": 35, "kc_len": 20, "sl_atr": 5.5}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    atr = _atr(bars_df, p["atr_len"])
    basis = c.rolling(int(p["kc_len"])).mean()
    rng = float(p["kc_mult"]) * atr
    up, dn = basis + rng, basis - rng
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    k = int(p["lookback"])
    up_t = (h >= up).astype(float).shift(1).rolling(k, min_periods=1).max() > 0
    dn_t = (lo <= dn).astype(float).shift(1).rolling(k, min_periods=1).max() > 0
    mid = (h >= basis) & (lo <= basis)
    le = up_t & mid & (c > ema)
    se = dn_t & mid & (c < ema)
    lx = (h >= up) & ~le & ~se
    sx = (lo <= dn) & ~se & ~le
    return le, lx, se, sx


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    a = float(p["sl_atr"]) * _atr(bars_df, p["atr_len"]).shift(1) / bars_df["close"]
    return {"sl_stop": a.shift(1)}


def portfolio_kwargs(**params):
    return {}
