"""TradingView-accurate technical indicators for vectorbt.

Plain functions (pandas/numpy in, same type out)::

    import tv_indicators as ti
    bb = ti.bbands(df.close)            # namedtuple: basis, upper, lower, ...
    st = ti.supertrend(df.high, df.low, df.close)

vectorbt indicator classes (parameter grids, crossover helpers)::

    from tv_indicators.vbt import BBANDS
    bb = BBANDS.run(df.close, length=[20, 30], mult=2.0)

See README.md for the full list and the TradingView reference for each.
"""

from ._core import REGISTRY, ma_kind  # noqa: F401
from .bollinger import (  # noqa: F401
    bb_percent_b, bbands, bbtrend, bbw, bbwp, double_bbands, squeeze_momentum,
    ttm_squeeze,
)
from .moving_averages import (  # noqa: F401
    alma, dema, ema, hl2, hlc3, hlcc4, hma, kama, lsma, ma, mcginley, ohlc4,
    rma, sma, tema, vwma, wma,
)
from .oscillators import (  # noqa: F401
    awesome_oscillator, cci, cmo, connors_rsi, coppock, dpo, fisher, macd, mfi,
    mom, roc, rsi, stoch, stoch_rsi, trix, tsi, ultimate_oscillator, wavetrend,
    willr,
)
from .trend import adx, aroon, dmi, ichimoku  # noqa: F401
from .volatility import (  # noqa: F401
    atr, chandelier_exit, choppiness, donchian, envelope, heikin_ashi,
    historical_volatility, keltner, natr, psar, supertrend, true_range, ut_bot,
    vortex,
)
from .volume import (  # noqa: F401
    accdist, chaikin_osc, cmf, efi, obv, pvt, session_ids, vwap, vwap_session,
)

__version__ = "0.1.0"
