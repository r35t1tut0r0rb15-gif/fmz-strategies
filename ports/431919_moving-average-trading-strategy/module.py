"""Negroni MA retests (strategy 3 defaults), 12-hour bars: in an EMA 32 > EMA 64 trend, a close crossing under the EMA 13
with RSI 14 over 55 and the close above the last completed broker day's EMA 100 goes long (mirror short); a 2 ATR 50 stop
and a 2.5 ATR 50 target from the entry. Adds are not ported.
Port of FMZ strategy #431919 "Moving Average Trading Strategy" (Negroni MA & RSI Strategy).

FMZ source id: 431919

Source
    https://www.fmz.com/strategy/431919 (PineScript v5, FMZ last modified 2023-11-13 11:17:51).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 199-438), retest entries, ATR SL / TP (50, x2 / x2.5), RSI 14 55 / 45, EMA 13 / 32 / 64, daily EMA 100, pyramiding 3
    Long_3 = crossunder(close, ema13) and ema32 > ema64 and rsi > 55 and close > security('D', ema(close, 100)) -> entry long
    Short_3 = crossover(close, ema13) and ema32 < ema64 and rsi < 45 and close < daily EMA 100 -> entry short
    exit(stop = avg - 2 ATR(50), limit = avg + 2.5 ATR(50)) re-issued every bar (mirror short)

Interpretation choices (Pine rules in SURVEY_README.md)
    * security('D', ema(close, 100)) without lookahead is read as the last completed broker day's EMA
      100 of daily closes (17:00 America/New_York), built inside simulate() from the port's own bars
      (as #429383). The other option sets (retest strategy 1 / 2, breakout entries) are off.
    * The bracket follows the current ATR on every bar (a moving level): rule 2, mark
      trailing_stop_pending; the port fixes it at the signal bar's ATR 50 (Wilder), as fractions of
      its close, shifted one bar. pyramiding 3: adds are not ported.
    * strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops
      on 12-hour bars: mark coarse_bar_stop. FREQ = "12h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving bracket fixed at entry (rule 2); adds not ported.
    2 generic: PASS, EMAs, RSI levels and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 3 % of equity and pyramiding 3 stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day for the daily EMA (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop_pending, coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_431919_negroni_ma_rsi_retest"
FAMILY = "ma_trend_oscillator_pullback"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "12h"  # backtest header period: 12h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_mult": [2.0, 3.0],
    "tp_mult": [2.5, 4.0],
}
DEFAULT_PARAMS = {"fast": 13, "trend": 32, "slow": 64, "rsi_len": 14, "rsi_buy": 55, "rsi_sell": 45,
                  "daily_ema": 100, "atr_len": 50, "sl_mult": 2.0, "tp_mult": 2.5}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    fast = c.ewm(span=int(p["fast"]), adjust=False).mean()
    trend = c.ewm(span=int(p["trend"]), adjust=False).mean()
    slow = c.ewm(span=int(p["slow"]), adjust=False).mean()
    ch = c.diff()
    n = int(p["rsi_len"])
    up, dn = _rma(ch.clip(lower=0), n), _rma((-ch).clip(lower=0), n)
    rsi = (100 - 100 / (1 + up / dn)).where(up != 0, 0.0).where(dn != 0, 100.0)
    lab = broker_day(bars_df.index)
    dclose = c.groupby(lab).last()
    dema = dclose.ewm(span=int(p["daily_ema"]), adjust=False).mean().shift(1)   # the last completed broker day
    fix = pd.Series(dema.reindex(lab).to_numpy(), index=c.index)
    xu = (c < fast) & (c.shift(1) >= fast.shift(1))
    xo = (c > fast) & (c.shift(1) <= fast.shift(1))
    lg = (xu & (trend > slow) & (rsi > p["rsi_buy"]) & (c > fix)).astype(bool)
    sh = (xo & (trend < slow) & (rsi < p["rsi_sell"]) & (c < fix)).astype(bool)
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1).where(c1.notna(), h - lo)
    af = _rma(tr, int(p["atr_len"])) / c
    return lg, sh, af


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lg, sh, _ = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return lg, false, sh, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, af = _signals(bars_df, p)
    return {"sl_stop": (af * float(p["sl_mult"])).shift(1), "tp_stop": (af * float(p["tp_mult"])).shift(1)}


def portfolio_kwargs(**params):
    return {}
