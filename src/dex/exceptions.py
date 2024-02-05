class NotEnoughLiquidityError(Exception):
    code: str = "insufficient_pool_liquidity"
    pass
