"""
Object models for portfolios related endpoints args and response.
"""

from typing import List
from enum import Enum
from uuid import UUID

import pycurl
import io
import json

from coinbaseadvanced.models.common import BaseModel, ValueCurrency
from coinbaseadvanced.models.error import CoinbaseAdvancedTradeAPIError
from coinbaseadvanced.models.futures import FuturesPosition, FuturesPositionSide, MarginType


class UserRawCurrency(BaseModel):
    """
    Represents a user's raw currency.

    Attributes:
        user_native_currency (ValueCurrency): The user's native currency.
        raw_currency (ValueCurrency): The raw currency.
    """

    user_native_currency: ValueCurrency
    raw_currency: ValueCurrency

    def __init__(self, userNativeCurrency: dict, rawCurrency: dict):
        self.user_native_currency = ValueCurrency(**userNativeCurrency)
        self.raw_currency = ValueCurrency(**rawCurrency)


class PortfolioType(Enum):
    """
    Enum representing whether "BUY" or "SELL" order.
    """

    UNDEFINED = "UNDEFINED"
    DEFAULT = "DEFAULT"
    CONSUMER = "CONSUMER"
    INTX = "INTX"


class Portfolio(BaseModel):
    """
    Object representing a portfolio.
    """

    uuid: UUID
    name: str
    type: PortfolioType
    deleted: bool

    def __init__(
            self, uuid: UUID, name: str, type: str, deleted: bool, **kwargs) -> None:
        self.uuid = uuid
        self.name = name
        self.type = PortfolioType[type]
        self.deleted = deleted

        self.kwargs = kwargs

    @classmethod
    def from_response(cls, response: bytes, response_code: int) -> 'Portfolio':
        """
        Factory Method.
        """

        if response_code < 200 or response_code >= 300:
            raise CoinbaseAdvancedTradeAPIError.not_ok_response(response_code, response)

        result = json.loads(response.decode('utf-8'))
        return cls(**result['portfolio'])


class PortfolioBalances(BaseModel):
    """
    Object representing a portfolio balances.
    """

    total_balance: ValueCurrency
    total_futures_balance: ValueCurrency
    total_cash_equivalent_balance: ValueCurrency
    total_crypto_balance: ValueCurrency
    futures_unrealized_pnl: ValueCurrency
    perp_unrealized_pnl: ValueCurrency

    def __init__(
        self, total_balance: dict,
            total_futures_balance: dict,
            total_cash_equivalent_balance: dict,
            total_crypto_balance: dict,
            futures_unrealized_pnl: dict,
            perp_unrealized_pnl: dict, **kwargs) -> None:
        self.total_balance = ValueCurrency(**total_balance)
        self.total_futures_balance = ValueCurrency(**total_futures_balance)
        self.total_cash_equivalent_balance = ValueCurrency(
            **total_cash_equivalent_balance)
        self.total_crypto_balance = ValueCurrency(**total_crypto_balance)
        self.futures_unrealized_pnl = ValueCurrency(
            **futures_unrealized_pnl)
        self.perp_unrealized_pnl = ValueCurrency(**perp_unrealized_pnl)

        self.kwargs = kwargs


class PortfolioBreakdown(BaseModel):
    """
    Object representing a portfolio breakdown.
    """

    portfolio: Portfolio
    portfolio_balances: PortfolioBalances
    spot_positions: List[SpotPosition]
    perp_positions: List[PerpPosition]
    futures_positions: List[FuturesPosition]

    def __init__(self, portfolio: dict,
                 portfolio_balances: dict,
                 spot_positions: list,
                 perp_positions: list,
                 futures_positions: list,  **kwargs):
        self.portfolio = Portfolio(**portfolio)
        self.portfolio_balances = PortfolioBalances(**portfolio_balances)
        self.spot_positions = [SpotPosition(**x) for x in spot_positions]
        self.perp_positions = [PerpPosition(**x) for x in perp_positions]
        self.futures_positions = [
            FuturesPosition(**x) for x in futures_positions]

        self.kwargs = kwargs

    @classmethod
    def from_response(cls, response: bytes, response_code: int) -> 'PortfolioBreakdown':
        """
        Factory Method.
        """

        if response_code < 200 or response_code >= 300:
            raise CoinbaseAdvancedTradeAPIError.not_ok_response(response_code, response)

        result = json.loads(response.decode('utf-8'))
        return cls(**result['breakdown'])


class PortfoliosPage(BaseModel):
    """
    Portfolio Page.
    """

    portfolios: List[Portfolio]

    def __init__(self, portfolios: list, **kwargs) -> None:
        self.portfolios = list(map(lambda x: Portfolio(**x), portfolios)) \
            if portfolios is not None else []

        self.kwargs = kwargs

    @classmethod
    def from_response(cls, response: bytes, response_code: int) -> 'PortfoliosPage':
        """
        Factory Method.
        """

        if response_code < 200 or response_code >= 300:
            raise CoinbaseAdvancedTradeAPIError.not_ok_response(response_code, response)

        result = json.loads(response.decode('utf-8'))
        return cls(**result)

    def __iter__(self):
        return self.portfolios.__iter__()


class PortfolioFundsTransfer(BaseModel):
    """
    Represents a funds transfer between two portfolios.
    """

    source_portfolio_uuid: str
    target_portfolio_uuid: str

    def __init__(self, source_portfolio_uuid: str, target_portfolio_uuid: str, **kwargs):
        """
        Initializes a new instance of the PortfolioFundsTransfer class.

        Args:
            source_portfolio_uuid (str): The UUID of the source portfolio.
            target_portfolio_uuid (str): The UUID of the target portfolio.
            **kwargs: Additional keyword arguments.

        """
        self.source_portfolio_uuid = source_portfolio_uuid
        self.target_portfolio_uuid = target_portfolio_uuid
        self.kwargs = kwargs

    @classmethod
    def from_response(cls, response: bytes, response_code: int) -> 'PortfolioFundsTransfer':
        """
        Factory method that creates a PortfolioFundsTransfer object from a response.

        Args:
            response (bytes): The response body as bytes.
            response_code (int): The HTTP status code.

        Returns:
            PortfolioFundsTransfer: The created PortfolioFundsTransfer object.

        Raises:
            CoinbaseAdvancedTradeAPIError: If the response is not OK.

        """
        if response_code < 200 or response_code >= 300:
            raise CoinbaseAdvancedTradeAPIError.not_ok_response(response_code, response)

        result = json.loads(response.decode('utf-8'))
        return cls(**result)
