"""Broker days: the WMA 21 of the bar's close-location value (net up / down volume share, 0 on unchanged closes) above its EMA 9 holds a long, below it a short (always in the market after the first signal); each trade has a 1 % stop and a 2 % target from its fill; reversing.
Port of FMZ strategy #483519 "Multi Moving Average Net Volume Oscillator Trend Reversal Trading Strategy" (EMA-Based Net Volume Oscillator with Trend Change (NVO)).

FMZ source id: 483519

Source
    https://www.fmz.com/strategy/483519 (PineScript v5, FMZ last modified 2025-02-27 16:46:30).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 146-239), net volume oscillator (close location x volume / volume); WMA 21 (default type); EMA 9 overlay; SL 1 %, TP 2 % of position_avg_price; 100 % of equity
    dailyNetOscillator = volume > 0 ? (up - down volume) / volume x 100 : 0, with up = volume x (close - low) / range and down = volume x (1 - that) when the close changed, else 0
    oscillator = wma(dailyNetOscillator, 21);  oscillator > ema(oscillator, 9) and position_size <= 0 -> entry Long;  oscillator < ema and position_size >= 0 -> entry Short (each also closes the other side)
    position_size > 0 -> exit(stop = avg x 0.99, limit = avg x 1.02);  position_size < 0 mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * Volume cancels in the oscillator: it is (2 x (close - low) / range - 1) x 100 on bars where the
      close changed (a zero range counts 0.5), 0 on unchanged closes or zero volume, so only a zero
      volume changes a bar (weird case). The entries are states: after a stop or target the strategy
      re-enters on the next bar while the side still holds. The bracket is re-sent from
      position_avg_price every bar from the fill bar's close, so it is fixed at the fill: ported as
      sl_stop 0.01 / tp_stop 0.02 (stated approximation: the source acts from the bar after the fill, the
      house from the fill, as #429494). REVERSAL INTENDED. 100 % of equity is sizing. Stop module:
      portfolio_kwargs {} (driver D4). Stops on 1-day bars: coarse_bar_stop. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; 1 % / 2 % bracket from the fill.
    2 generic: PASS, smoothed close-location oscillator against its EMA.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) as a common factor of the oscillator, so only a zero volume changes it; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view

NAME = "fmz_483519_net_volume_oscillator_wma21_ema9_state_1_2pct_reversal"
FAMILY = "volume_oscillator"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ma_len": [21, 14],
    "sl": [0.01, 0.02],
}
DEFAULT_PARAMS = {"ma_len": 21, "ema_len": 9, "sl": 0.01, "tp": 0.02}


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


def _wma(x, n):
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        w = np.arange(1, n + 1, dtype=float)
        out[n - 1:] = sliding_window_view(v, n) @ w / w.sum()
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    rng = h - lo
    mult = ((c - lo) / rng.where(rng > 0)).where(rng > 0, 0.5)
    changed = (c != c.shift(1)) & c.shift(1).notna()
    net = (v * mult - v * (1 - mult)).where(changed, 0.0)
    daily = (net / v.where(v > 0) * 100).where(v > 0, 0.0)
    osc = _wma(daily, int(p["ma_len"]))
    ov = osc.ewm(span=int(p["ema_len"]), adjust=False).mean()
    buy = osc > ov
    sell = osc < ov
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"]), "tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
