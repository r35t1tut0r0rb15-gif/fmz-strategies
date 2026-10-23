"""Broker days: a close below the lows of all 11 previous bars on above-average volume goes long, a close above the highs of the 11 previous bars on such volume goes short (contrarian); each trade gets a 1.5 ATR 14 stop and a 3 ATR target from the signal close; reversing.
Port of FMZ strategy #478716 "Multi Indicator Synergistic Trend Reversal Quantitative Trading Strategy" (Reversal Signals Strategy [AlgoAlpha]).

FMZ source id: 478716

Source
    https://www.fmz.com/strategy/478716 (PineScript v5, FMZ last modified 2025-01-17 15:44:01).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 91-155), lookback 12 (11 prior bars); volume SMA 20; ATR 14 x 1.5, RR 2; 100 % of equity
    bullCandleScore = count over i = 0 .. 11 of close < low[i];  bullSignal = bullCandleScore == 11 and volume > sma(volume, 20) -> entry Long, exit(stop = close - 1.5 atr, limit = close + 3 atr)
    bearSignal mirrored with close > high[i] -> entry Short, exit(stop = close + 1.5 atr, limit = close - 3 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The i = 0 term compares the close with its own bar's low, so it never counts: the signal needs the
      close under each of the 11 previous lows (over the 11 previous highs). The bracket is sent on signal
      bars, as levels from that close: ported as fractions of the fill, exact (1e-6 floor); a fresh
      signal while in the trade (a further new low) re-sends it from the new close (not followed:
      trailing_stop_pending). The trend MA only plots. REVERSAL INTENDED. 100 % of equity is sizing.
      Stop module: portfolio_kwargs {} (driver D4). Stops on 1-day bars: coarse_bar_stop. Daily bars
      are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket at the signal close as fractions of the fill.
    2 generic: PASS, contrarian extreme-close reversals on volume.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) against its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_478716_extreme_close_reversal_volume_atr_bracket_reversal"
FAMILY = "reversal_extreme"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "lookback": [12, 8],
    "rr": [2.0, 1.5],
}
DEFAULT_PARAMS = {"lookback": 12, "sl_atr": 1.5, "rr": 2.0}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
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
    return _rma(pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1), n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    k = int(p["lookback"])
    bull = pd.Series(0, index=c.index)
    bear = pd.Series(0, index=c.index)
    for i in range(k):
        bull += (c < lo.shift(i)).astype(int)
        bear += (c > h.shift(i)).astype(int)
    vol_ok = v > v.rolling(20).mean()
    buy = (bull == k - 1) & vol_ok
    sell = (bear == k - 1) & vol_ok
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, c = bars_df["open"], bars_df["close"]
    sl_d = float(p["sl_atr"]) * _atr(bars_df, 14)
    tp_d = sl_d * float(p["rr"])
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    sl_f = (pd.Series(np.nan, index=o.index).mask(lf, 1 - (c - sl_d).shift(1) / o)
            .mask(sf, (c + sl_d).shift(1) / o - 1))
    tp_f = (pd.Series(np.nan, index=o.index).mask(lf, (c + tp_d).shift(1) / o - 1)
            .mask(sf, 1 - (c - tp_d).shift(1) / o))
    return {"sl_stop": sl_f.clip(lower=1e-6), "tp_stop": tp_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
