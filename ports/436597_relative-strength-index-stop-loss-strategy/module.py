"""RSI 7 extremes with a percent stop, no bar size of its own: an RSI under 37 goes long; an RSI over 75 goes short (reversing); each trade carries a stop of 1 % of the entry price (the input's reading). The daily loss
limit can never trigger.
Port of FMZ strategy #436597 "Relative Strength Index Stop Loss Strategy" (RSI Strategy with Daily Loss Limit).

FMZ source id: 436597

Source
    https://www.fmz.com/strategy/436597 (PineScript v5, FMZ last modified 2023-12-26 10:22:44).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 127-178), RSI 7 (the RSI Length input is unused), limits 75 / 37, stop 1 %
    rsi = rsi(close, 7);  rsi < 37 -> entry Buy, exit("Buy", loss = close x 1 %);  rsi > 75 -> entry Sell (short), exit("Sell", loss = close x 1 %);  (the block is written twice);  strategy.equity < strategy.equity x 0.97 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the exit's `loss` is written as close x 1 % in TICKS and is only sent on the bar of the
      opposite signal; it is read here as its stated intent, a stop of the Stop Loss Percentage (1 %) of the
      entry fill price on both sides, so the stop is `stop_pct`. The duplicated block adds nothing. The
      daily loss limit compares the equity with itself times 0.97 and can never be true. The source
      has no backtest header and names no bar size: FREQ = "bar_size_pending" (skill section 5a).
      REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). The default quantity is sizing.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, tick stop on a signal bar -> percent stop on every trade.
    3 crypto-exchange-only: no (no exchange header at all).
    4 signals only: the stop input stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: bar_size_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_436597_rsi7_extremes_percent_stop"
FAMILY = "rsi_oscillator"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "bar_size_pending"
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rsi_len": [7, 14],
    "stop_pct": [0.01, 0.02],
}
DEFAULT_PARAMS = {"rsi_len": 7, "stop_pct": 0.01, "oversold": 37, "overbought": 75}


def precompute(raw_1m_df, symbol_key, **params):
    import bar_sizes                      # the house builder (mining\bar_sizes.py), on the desktop's path
    return bar_sizes.build_bars(raw_1m_df, params["bar_size"])


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["rsi_len"])
    ch = c.diff()
    up_ = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn_ = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = (100 - 100 / (1 + up_ / dn_)).where(dn_ != 0, 100.0).where(up_.notna())
    le = (rsi < float(p["oversold"])).fillna(False).astype(bool)
    se = (rsi > float(p["overbought"])).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["stop_pct"])}


def portfolio_kwargs(**params):
    return {}
