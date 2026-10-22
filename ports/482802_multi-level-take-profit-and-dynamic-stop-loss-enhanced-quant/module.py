"""A strategy-tester template run with its default sources, 4-hour bars: every bar that ends flat sends a long and then a short entry (the short wins), and the short takes profit at the signal bar's low; no stop.
Port of FMZ strategy #482802 "Multi Level Take Profit and Dynamic Stop Loss Enhanced Quantitative Strategy" (Enhanced Strategy Tester with multi TP and SL Trigger).

FMZ source id: 482802

Source
    https://www.fmz.com/strategy/482802 (PineScript v6, FMZ last modified 2025-02-20 14:56:34).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 83-139), entry sources close / close; TP sources high (long) / low (short); exit and SL switches off; margin 100 / 100
    close > 0 and no open trade -> entry long + exits(limit = high x 3, stop = na);  close > 0 and no open trade -> entry short + exits(limit = low x 3, stop = na)

Interpretation choices (Pine rules in SURVEY_README.md)
    * With the default sources both entry conditions are close > 0, true on every bar: while flat, the
      long and the short are both sent and the later (short) wins (as #437773). The three short targets
      are all the signal bar's low and each closes the whole position, so the short exits at that low;
      the exit switches and the SL are off by default. Entries come only when no trade is open, so the
      loop follows the target on each bar's low to know when the position is flat again (as #449508; a
      target the fill opens through closes the trade one bar late in the engine, as #458256). Stop module:
      portfolio_kwargs {} (driver D4). Stops on bars longer than 1 hour: mark coarse_bar_stop. Opposite
      entries cannot occur (entries only from flat). The margin settings are not sizing signals.
      FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; previous-low target as a fraction of the fill.
    2 generic: PASS, template defaults: always-short with a prior-low target.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: margin 100 / 100 stored, not ported.
    5 ranges declared: GRID below (1 trial), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_482802_tester_defaults_flat_short_prev_low_target"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {}
DEFAULT_PARAMS = {}


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


def _signals(bars_df, p):
    o, lo, c = bars_df["open"], bars_df["low"], bars_df["close"]
    tgt = lo                                     # the short targets: the signal bar's low
    ov, lv, tv = o.to_numpy(dtype=float), lo.to_numpy(dtype=float), tgt.to_numpy(dtype=float)
    ok = (c > 0).to_numpy()
    m = len(ov)
    se = np.zeros(m, dtype=bool)
    pos, pend, tp = 0, 0, np.nan
    for i in range(m):
        if pend == -1:
            pos, tp = -1, tv[i - 1]
        pend = 0
        if pos == -1 and lv[i] <= tp:
            pos = 0                              # the target fills inside this bar (or at its open)
        if pos == 0 and ok[i]:
            se[i], pend = True, -1
    return pd.Series(se, index=c.index), tgt


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    se, tgt = _signals(bars_df, p)
    o = bars_df["open"]
    sf = se.shift(1, fill_value=False)
    s_thr = tgt.shift(1) >= o                                    # marketable at the fill
    false = pd.Series(False, index=o.index)
    return false, false.copy(), se, sf & s_thr & ~se


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    se, tgt = _signals(bars_df, p)
    tp_f = 1 - tgt.shift(1) / bars_df["open"]
    return {"tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
