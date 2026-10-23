"""CMF velocity (SMA 7 of the change of an 11-bar Chaikin money flow) crossing zero with the close on the EMA 200's side, 45-minute bars: crossing up above the EMA goes long, crossing down below it goes short, each with a stop 2 ATR 10 and a target 4 ATR 10 from the signal close; reversing.
Port of FMZ strategy #426394 "CMF Momentum Breakthrough Moving Average Strategy" (CMF Velocity with 200EMA Strategy).

FMZ source id: 426394

Source
    https://www.fmz.com/strategy/426394 (PineScript v4, FMZ last modified 2023-09-11 17:40:54).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 81-193), CMF 11, velocity 7; EMA 200; ATR 10 x 2; profit / loss 2; direction 0 (both); backtest window inputs not used by the orders
    crossover(sma(change(cmf(11)), 7), 0) and ema(close, 200) < close -> entry Long Entry, exit("Exit", stop = close - 2 atr, limit = close + 4 atr)
    crossunder(...) and ema(close, 200) > close -> entry Short Entry, exit("Exit", stop = close + 2 atr, limit = close - 4 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exit levels are prices fixed at the signal close; the port gives them as fractions of the fill
      (a level the fill has already passed gives no stop). A repeat signal while in the position re-sends
      the exit at new levels (the house bracket keeps the first: mark trailing_stop_pending). Both exits
      share the id "Exit", but each is sent only on its own side's signal bar, so it brackets the current
      side. A zero-range bar gives the CMF multiplier 0, as written. ATR is Pine's atr (Wilder, the first
      bar's high - low). REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). No sizing code.
      FREQ = "45min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket from the signal close.
    2 generic: PASS, money-flow velocity zero crossings with an EMA 200 side filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the Chaikin money flow (multiplier x volume over sma(volume, 11)); exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used (timeBacktesting is always true).
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_426394_cmf_velocity_zero_cross_ema200_atr2_4_bracket_reversal"
FAMILY = "money_flow"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "cmf_period": [11, 20],
    "atr_mult": [2.0, 3.0],
}
DEFAULT_PARAMS = {"cmf_period": 11, "atr_mult": 2.0, "vel_period": 7, "ema_period": 200, "atr_period": 10,
                  "pl_ratio": 2.0}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


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


def _signals(bars_df, p):
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    n = int(p["cmf_period"])
    mfm = (((c - lo) - (h - c)) / (h - lo).replace(0.0, np.nan) * v).fillna(0.0)
    cmf = mfm.rolling(n).mean() / v.rolling(n).mean()
    vel = cmf.diff().rolling(int(p["vel_period"])).mean()
    ema = c.ewm(span=int(p["ema_period"]), adjust=False).mean()
    le = (vel > 0) & (vel.shift(1) <= 0) & (ema < c)
    se = (vel < 0) & (vel.shift(1) >= 0) & (ema > c)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)   # first bar: high - low
    atr = _rma(tr, int(p["atr_period"]))
    return le, se & ~le, atr


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _ = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, atr = _signals(bars_df, p)
    o, c = bars_df["open"], bars_df["close"]
    off = (float(p["atr_mult"]) * atr).shift(1)          # the signal bar's stop offset
    c1 = c.shift(1)
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    sl_l, tp_l = 1 - (c1 - off) / o, (c1 + off * float(p["pl_ratio"])) / o - 1
    sl_s, tp_s = (c1 + off) / o - 1, 1 - (c1 - off * float(p["pl_ratio"])) / o
    sl_f = sl_l.where(lf, sl_s.where(sf))
    tp_f = tp_l.where(lf, tp_s.where(sf))
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
