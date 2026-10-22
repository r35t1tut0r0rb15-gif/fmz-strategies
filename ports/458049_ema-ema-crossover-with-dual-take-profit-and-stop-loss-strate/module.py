"""EMA 20 / 50 crossings, 4-hour bars: the cross up goes long with a stop 100 ticks under the EMA 50 and a 200-tick target over the close; the cross down goes short (mirror); reversing. The ticks are read as ATR multiples at the 4-hour reading (0.025 / 0.05 ATR).
Port of FMZ strategy #458049 "EMA交叉指示双重止盈止损策略-EMA-Crossover-with-Dual-Take-Profit-and-Stop-Loss-Strategy" (Estratégia com Médias Móveis (EMA 20 / 50 with EMA-based stop)).

FMZ source id: 458049

Source
    https://www.fmz.com/strategy/458049 (PineScript v5, FMZ last modified 2024-07-29 14:46:31).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 172-232), EMA 20 / 50; stop EMA 50 -+ 100 pips (x mintick); target close +- 200 pips; levels set on the signal bar
    crossover(ema20, ema50) -> stop = ema50 - 100 ticks, target = close + 200 ticks, entry Compra;  crossunder -> stop = ema50 + 100 ticks, target = close - 200 ticks, entry Venda
    in a position: exit(limit = target, stop = stop)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The levels are fixed on the signal bar (var) and sent while in the position: ported active from
      the fill bar (#440797) as fractions of the signal close, the stop (close - ema50) / close plus
      0.025 ATR and the target 0.05 ATR (100 / 200 ticks are 10 / 20 at the 0.1 tick, read at the
      4-hour ATR ~400), ATR 14 from the signal bar. A cross whose stop already sits beyond the close
      would fill at once: that signal is sent as the opposite trade's close (no new trade). REVERSAL
      INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on 4-hour bars: mark
      coarse_bar_stop. No sizing code. FREQ = "4h" from the backtest header (UTC-aligned 4-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the EMA-based stop and tick target as fractions of the signal close.
    2 generic: PASS, EMA crossings with an EMA-anchored stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_458049_ema20_50_cross_ema50_anchored_stop_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "short_len": [20, 9],
    "long_len": [50, 100],
    "tp_atr": [0.05, 2.0],
}
DEFAULT_PARAMS = {"short_len": 20, "long_len": 50, "tp_atr": 0.05, "sl_atr": 0.025, "atr_len": 14}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def _levels(bars_df, p):
    c = bars_df["close"]
    a = c.ewm(span=int(p["short_len"]), adjust=False).mean()
    b = c.ewm(span=int(p["long_len"]), adjust=False).mean()
    up = (a > b) & (a.shift(1) <= b.shift(1))
    dn = (a < b) & (a.shift(1) >= b.shift(1))
    atr = _atr(bars_df, p["atr_len"])
    sl_l = (c - b + float(p["sl_atr"]) * atr) / c
    sl_s = (b + float(p["sl_atr"]) * atr - c) / c
    tp = float(p["tp_atr"]) * atr / c
    return up, dn, sl_l, sl_s, tp


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    up, dn, sl_l, sl_s, _ = _levels(bars_df, p)
    ok_l, ok_s = up & (sl_l > 0), dn & (sl_s > 0)
    return ok_l, dn & ~ok_s, ok_s, up & ~ok_l


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    up, dn, sl_l, sl_s, tp = _levels(bars_df, p)
    sl = pd.Series(np.nan, index=bars_df.index).mask(up, sl_l).mask(dn, sl_s)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.where(up | dn).shift(1)}


def portfolio_kwargs(**params):
    return {}
