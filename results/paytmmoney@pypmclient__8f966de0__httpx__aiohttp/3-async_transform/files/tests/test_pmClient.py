import pytest
import sys

sys.path.append('../')


def test_set_access_token(pm_api):
    assert pm_api.set_access_token("access_token") == "access_token"


def test_set_public_access_token(pm_api):
    assert pm_api.set_public_access_token("public_access_token") == "public_access_token"


def test_set_read_access_token(pm_api):
    assert pm_api.set_read_access_token("read_access_token") == "read_access_token"


def test_login(pm_api):
    assert pm_api.login(
        state_key="<STATE_KEY>") == "https://login.paytmmoney.com/merchant-login?apiKey=<API_KEY>&state=<STATE_KEY>"


def test_login_type(pm_api):
    with pytest.raises(TypeError):
        pm_api.login(state_key=None)


@pytest.mark.asyncio
async def test_generate_session(pm_api):
    with pytest.raises(TypeError):
        await pm_api.generate_session(None)


@pytest.mark.asyncio
async def test_generate_session_connection(pm_api):
    with pytest.raises(Exception):
        await pm_api.generate_session("request_token")


@pytest.mark.asyncio
async def test_generate_session_access_token(pm_api, mocker):
    response = {
        "access_token": "access_token",
        "public_access_token": "public_access_token",
        "read_access_token": "read_access_token"
    }
    mocker.patch("pmClient.apiService.ApiService.api_call_helper", return_value=response)
    await pm_api.generate_session("request_token")


def test_logout(pm_api, mocker):
    response = {
        "access_token": "access_token",
        "public_access_token": "public_access_token",
        "read_access_token": "read_access_token"
    }
    mocker.patch("pmClient.apiService.ApiService.api_call_helper", return_value=response)
    pm_api.logout()


@pytest.mark.asyncio
async def test_place_order_attribute(pm_api):
    pm_api.access_token = "test_access_token"
    with pytest.raises(ConnectionError):
        await pm_api.place_order(
            source="W",
            txn_type="B",
            exchange="NSE",
            segment="E",
            product="",
            security_id="772",
            quantity=1,
            validity="DAY",
            order_type="SL",
            price=620.0,
            off_mkt_flag=False
        )


@pytest.mark.asyncio
async def test_place_order_connection(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(ConnectionError):
        await pm_api.place_order(
            source="W",
            txn_type="B",
            exchange="NSE",
            segment="E",
            product="I",
            security_id="772",
            quantity=1,
            validity="DAY",
            order_type="SL",
            price=620.0,
            off_mkt_flag=False
        )


@pytest.mark.asyncio
async def test_place_order_connection_edis(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(ConnectionError):
        await pm_api.place_order(
            source="W",
            txn_type="B",
            exchange="NSE",
            segment="E",
            product="I",
            security_id="772",
            quantity=1,
            validity="DAY",
            order_type="LMT",
            price=620.0,
            off_mkt_flag=False
        )


@pytest.mark.asyncio
async def test_place_order_connection_cover(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(ConnectionError):
        await pm_api.place_order(
            source="W",
            txn_type="B",
            exchange="NSE",
            segment="E",
            product="V",
            security_id="772",
            quantity=1,
            validity="DAY",
            order_type="LMT",
            price=620.0,
            trigger_price=90.0
        )


@pytest.mark.asyncio
async def test_place_order_connection_cover_type(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(TypeError):
        await pm_api.place_order(
            source="W",
            txn_type="B",
            exchange="NSE",
            segment="E",
            product="V",
            security_id="772",
            quantity=1,
            validity="DAY",
            order_type="LMT",
            price=620.0,
            trigger_price=None
        )


@pytest.mark.asyncio
async def test_place_order_connection_bracket(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(ConnectionError):
        await pm_api.place_order(
            source="W",
            txn_type="B",
            exchange="NSE",
            segment="E",
            product="B",
            security_id="772",
            quantity=1,
            validity="DAY",
            order_type="LMT",
            price=620.0,
            stoploss_value=4,
            profit_value=2
        )


@pytest.mark.asyncio
async def test_place_order_connection_bracket_type1(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(TypeError):
        await pm_api.place_order(
            source="W",
            txn_type="B",
            exchange="NSE",
            segment="E",
            product="B",
            security_id="772",
            quantity=1,
            validity="DAY",
            order_type="LMT",
            price=620.0,
            stoploss_value=None,
            profit_value=2
        )


@pytest.mark.asyncio
async def test_place_order_connection_bracket_type2(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(TypeError):
        await pm_api.place_order(
            source="W",
            txn_type="B",
            exchange="NSE",
            segment="E",
            product="B",
            security_id="772",
            quantity=1,
            validity="DAY",
            order_type="LMT",
            price=620.0,
            stoploss_value=2,
            profit_value=None
        )


@pytest.mark.asyncio
async def test_modify_order_attribute(pm_api):
    pm_api.access_token = "test_access_token"
    with pytest.raises(ConnectionError):
        await pm_api.modify_order(
            source="N",
            txn_type="B",
            exchange="NSE",
            segment="E",
            product="",
            security_id="772",
            quantity=2,
            validity="DAY",
            order_type="SL",
            price=620.0,
            off_mkt_flag=False,
            mkt_type="NL",
            order_no="order_no",
            serial_no=1,
            group_id=8
        )


@pytest.mark.asyncio
async def test_modify_order_connection(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(ConnectionError):
        await pm_api.modify_order(
            source="N",
            txn_type="B",
            exchange="NSE",
            segment="E",
            product="I",
            security_id="772",
            quantity=2,
            validity="DAY",
            order_type="LMT",
            price=620.0,
            off_mkt_flag=False,
            mkt_type="NL",
            order_no="order_no",
            serial_no=1,
            group_id=8
        )


@pytest.mark.asyncio
async def test_modify_order_connection_edis(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(ConnectionError):
        await pm_api.modify_order(
            source="N",
            txn_type="B",
            exchange="NSE",
            segment="E",
            product="I",
            security_id="772",
            quantity=2,
            validity="DAY",
            order_type="LMT",
            price=620.0,
            off_mkt_flag=False,
            mkt_type="NL",
            order_no="order_no",
            serial_no=1,
            group_id=8
        )


@pytest.mark.asyncio
async def test_modify_order_connection_cover(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(ConnectionError):
        await pm_api.modify_order(
            source="N",
            txn_type="B",
            exchange="NSE",
            segment="E",
            product="V",
            security_id="772",
            quantity=2,
            validity="DAY",
            order_type="SL",
            price=620.0,
            off_mkt_flag=False,
            mkt_type="NL",
            order_no="order_no",
            serial_no=1,
            group_id=8,
            leg_no="2"
        )


@pytest.mark.asyncio
async def test_modify_order_connection_cover_type(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(TypeError):
        await pm_api.modify_order(
            source="N",
            txn_type="B",
            exchange="NSE",
            segment="E",
            product="V",
            security_id="772",
            quantity=2,
            validity="DAY",
            order_type="LMT",
            price=620.0,
            off_mkt_flag=False,
            mkt_type="NL",
            order_no="order_no",
            serial_no=1,
            group_id=8,
            leg_no=None
        )


@pytest.mark.asyncio
async def test_modify_order_connection_bracket(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(ConnectionError):
        await pm_api.modify_order(
            source="N",
            txn_type="B",
            exchange="NSE",
            segment="E",
            product="B",
            security_id="772",
            quantity=2,
            validity="DAY",
            order_type="LMT",
            price=620.0,
            off_mkt_flag=False,
            mkt_type="NL",
            order_no="order_no",
            serial_no=1,
            group_id=8,
            leg_no="2",
            algo_order_no="1"
        )


@pytest.mark.asyncio
async def test_modify_order_connection_bracket_type1(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(TypeError):
        await pm_api.modify_order(
            source="N",
            txn_type="B",
            exchange="NSE",
            segment="E",
            product="B",
            security_id="772",
            quantity=2,
            validity="DAY",
            order_type="LMT",
            price=620.0,
            off_mkt_flag=False,
            mkt_type="NL",
            order_no="order_no",
            serial_no=1,
            group_id=8,
            leg_no=None,
            algo_order_no="1"
        )


@pytest.mark.asyncio
async def test_modify_order_connection_bracket_type2(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(TypeError):
        await pm_api.modify_order(
            source="N",
            txn_type="B",
            exchange="NSE",
            segment="E",
            product="B",
            security_id="772",
            quantity=2,
            validity="DAY",
            order_type="LMT",
            price=620.0,
            off_mkt_flag=False,
            mkt_type="NL",
            order_no="order_no",
            serial_no=1,
            group_id=8,
            leg_no="2",
            algo_order_no=None
        )


@pytest.mark.asyncio
async def test_cancel_order_attribute(pm_api):
    pm_api.access_token = "test_acess_token"
    with pytest.raises(ConnectionError):
        await pm_api.cancel_order(
            source="N",
            txn_type="B",
            exchange="NSE",
            segment="E",
            product="",
            security_id="",
            quantity=2,
            validity="DAY",
            order_type="SL",
            price=620.0,
            off_mkt_flag=False,
            mkt_type="NL",
            order_no="order_no",
            serial_no=2,
            group_id=8
        )


@pytest.mark.asyncio
async def test_cancel_order_connection(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(ConnectionError):
        await pm_api.cancel_order(
            source="N",
            txn_type="B",
            exchange="NSE",
            segment="E",
            product="I",
            security_id="772",
            quantity=2,
            validity="DAY",
            order_type="SL",
            price=620.0,
            off_mkt_flag=False,
            mkt_type="NL",
            order_no="order_no",
            serial_no=2,
            group_id=8
        )


@pytest.mark.asyncio
async def test_cancel_order_connection_cover(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(ConnectionError):
        await pm_api.cancel_order(
            source="N",
            txn_type="B",
            exchange="NSE",
            segment="E",
            product="V",
            security_id="772",
            quantity=2,
            validity="DAY",
            order_type="LMT",
            price=620.0,
            off_mkt_flag=False,
            mkt_type="NL",
            order_no="order_no",
            serial_no=2,
            group_id=8,
            leg_no="2"
        )


@pytest.mark.asyncio
async def test_cancel_order_connection_cover_type(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(ConnectionError):
        await pm_api.cancel_order(
            source="N",
            txn_type="B",
            exchange="NSE",
            segment="E",
            product="I",
            security_id="772",
            quantity=2,
            validity="DAY",
            order_type="LMT",
            price=620.0,
            off_mkt_flag=False,
            mkt_type="NL",
            order_no="order_no",
            serial_no=2,
            group_id=8,
            leg_no=None
        )


@pytest.mark.asyncio
async def test_cancel_order_connection_bracket(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(ConnectionError):
        await pm_api.cancel_order(
            source="N",
            txn_type="B",
            exchange="NSE",
            segment="E",
            product="B",
            security_id="772",
            quantity=2,
            validity="DAY",
            order_type="LMT",
            price=620.0,
            off_mkt_flag=False,
            mkt_type="NL",
            order_no="order_no",
            serial_no=2,
            group_id=8,
            leg_no="2",
            algo_order_no="5"
        )


@pytest.mark.asyncio
async def test_cancel_order_connection_bracket1(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(TypeError):
        await pm_api.cancel_order(
            source="N",
            txn_type="B",
            exchange="NSE",
            segment="E",
            product="B",
            security_id="772",
            quantity=2,
            validity="DAY",
            order_type="LMT",
            price=620.0,
            off_mkt_flag=False,
            mkt_type="NL",
            order_no="order_no",
            serial_no=2,
            group_id=8,
            leg_no="2",
            algo_order_no=None
        )


@pytest.mark.asyncio
async def test_cancel_order_connection_bracket2(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(TypeError):
        await pm_api.cancel_order(
            source="N",
            txn_type="B",
            exchange="NSE",
            segment="E",
            product="B",
            security_id="772",
            quantity=2,
            validity="DAY",
            order_type="LMT",
            price=620.0,
            off_mkt_flag=False,
            mkt_type="NL",
            order_no="order_no",
            serial_no=2,
            group_id=8,
            leg_no=None,
            algo_order_no="5"
        )


@pytest.mark.asyncio
async def test_cancel_order_attribute_cover(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(TypeError):
        await pm_api.cancel_order(
            source="N",
            txn_type="B",
            exchange="NSE",
            segment="E",
            product="V",
            security_id="772",
            quantity=2,
            validity="DAY",
            order_type="LMT",
            price=620.0,
            off_mkt_flag=False,
            mkt_type="NL",
            order_no="order_no",
            serial_no=2,
            group_id=8,
            leg_no=None,
            algo_order_no="5"
        )


@pytest.mark.asyncio
async def test_convert_order_connection(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(ConnectionError):
        await pm_api.convert_regular(
            source="M",
            txn_type="S",
            exchange="NSE",
            segment="E",
            product_from="C",
            product_to="I",
            security_id="2885",
            quantity=100,
            mkt_type="NL"
        )


@pytest.mark.asyncio
async def test_convert_order_attribute(pm_api):
    pm_api.access_token = "eyJhbGciOiJIUzI1NiJ9.eyJhcGlLZXkiOiIwNTY2ZTRhMGIyNzI0Y2NlYTA2ZjMwYTdhMTlkMTk4NyIsIm1lcmNoYW50SWQiOiJNRVJfMjI2IiwicGFzc2NvZGVWYWxpZCI6dHJ1ZSwiYXV0aG9yaXNhdGlvbiI6IltcIlAxXCIsXCJQMlwiLFwiUDNcIixcIlA0XCJdIiwicGFzc2NvZGVWYWxpZFRpbGxFUE9DU2Vjb25kcyI6IjE2NTk5ODMzNDAwMDAiLCJzc29Ub2tlbiI6IlVmNndtYURTZDNrT3NNdlJQeFptOGlpNDFsbHhIMXFUNTlRK2hOeXVCcTMzN0FFSTFXTmlNUXQwcjlrWS9MMXMiLCJ1c2VySWQiOiI3OTQ1NjkiLCJpc3MiOiJwYXl0bW1vbmV5IiwiYXVkIjoibWVyY2hhbnQifQ.V_A8GjygTEWtArfF4ZM-04nyIe053rWTmcbmyDo0iYM"
    with pytest.raises(Exception):
        await pm_api.convert_regular(
            source="",
            txn_type="",
            exchange="",
            segment="E",
            product_from="",
            product_to="",
            security_id="2885",
            quantity=100,
            mkt_type="NL",
        )


@pytest.mark.asyncio
async def test_order_book_connection(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(ConnectionError):
        await pm_api.order_book()

@pytest.mark.asyncio
async def test_orders_connection(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(ConnectionError):
        await pm_api.orders()


@pytest.mark.asyncio
async def test_trade_details_connection(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(ConnectionError):
        await pm_api.trade_details(order_no="order_no", leg_no="1", segment="E")


@pytest.mark.asyncio
async def test_position_connection(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(ConnectionError):
        await pm_api.position()


@pytest.mark.asyncio
async def test_position_details_connection(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(Exception):
        await pm_api.position_details(security_id="772", product="I", exchange="NSE")


@pytest.mark.asyncio
async def test_funds_summary_attribute(pm_api):
    # If no funds could be fetched, this exception will be raised.
    pm_api.access_token = "test_access_token"
    with pytest.raises(ConnectionError):
        await pm_api.funds_summary(config="r")


@pytest.mark.asyncio
async def test_funds_summary_connection(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(Exception):
        await pm_api.funds_summary(config=True)


@pytest.mark.asyncio
async def test_holdings_value_connection(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(ConnectionError):
        await pm_api.holdings_value()


@pytest.mark.asyncio
async def test_user_holdings_data_connection(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(ConnectionError):
        await pm_api.user_holdings_data()


@pytest.mark.asyncio
async def test_scrips_margin_attribute(pm_api):
    pm_api.access_token = "test_access_token"
    with pytest.raises(ConnectionError):
        await pm_api.scrips_margin(
            source="W",
            margin_list=None
        )


@pytest.mark.asyncio
async def test_scrips_margin_connection(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(ConnectionError):
        await pm_api.scrips_margin(
            source="W",
            margin_list=[
                {
                    "exchange": "NSE",
                    "segment": "D",
                    "security_id": "46840",
                    "txn_type": "B",
                    "quantity": "250",
                    "strike_price": "0",
                    "trigger_price": "0",
                    "instrument": "FUTSTK"
                },
                {
                    "exchange": "NSE",
                    "segment": "D",
                    "security_id": "46834",
                    "txn_type": "B",
                    "quantity": "250",
                    "strike_price": "0",
                    "trigger_price": "0",
                    "instrument": "FUTSTK"
                },
                {
                    "exchange": "NSE",
                    "segment": "E",
                    "security_id": "27466",
                    "txn_type": "B",
                    "quantity": "25",
                    "strike_price": "0",
                    "trigger_price": "0",
                    "instrument": "EQUITY"
                }
            ])


@pytest.mark.asyncio
async def test_order_margin_connection(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(ConnectionError):
        await pm_api.order_margin(
            source="W",
            exchange="NSE",
            segment="E",
            security_id="772",
            txn_type="B",
            quantity=100,
            price=0.0,
            product="1",
            trigger_price=0.0
        )


def test_security_master_connection(pm_api):
    with pytest.raises(Exception):
        pm_api.security_master(scrip_type="ef", exchange="NS")


def test_security_master_connection1(pm_api):
    with pytest.raises(Exception):
        pm_api.security_master(scrip_type=None, exchange="NS")


def test_security_master_connection2(pm_api):
    with pytest.raises(Exception):
        pm_api.security_master(scrip_type="None", exchange=None)


@pytest.mark.asyncio
async def test_generate_tpin_attribute(pm_api):
    # If user details could not be fetched, this exception will be thrown.
    pm_api.access_token = "eyJhbGciOiJIUzI1NiJ9.eyJhcGlLZXkiOiIwNTY2ZTRhMGIyNzI0Y2NlYTA2ZjMwYTdhMTlkMTk4NyIsIm1lcmNoYW50SWQiOiJNRVJfMjI2IiwicGFzc2NvZGVWYWxpZCI6dHJ1ZSwiYXV0aG9yaXNhdGlvbiI6IltcIlAxXCIsXCJQMlwiLFwiUDNcIixcIlA0XCJdIiwicGFzc2NvZGVWYWxpZFRpbGxFUE9DU2Vjb25kcyI6IjE2NTk5ODMzNDAwMDAiLCJzc29Ub2tlbiI6IlVmNndtYURTZDNrT3NNdlJQeFptOGlpNDFsbHhIMXFUNTlRK2hOeXVCcTMzN0FFSTFXTmlNUXQwcjlrWS9MMXMiLCJ1c2VySWQiOiI3OTQ1NjkiLCJpc3MiOiJwYXl0bW1vbmV5IiwiYXVkIjoibWVyY2hhbnQifQ.V_A8GjygTEWtArfF4ZM-04nyIe053rWTmcbmyDo0iYM"
    with pytest.raises(Exception):
        await pm_api.generate_tpin()


@pytest.mark.asyncio
async def test_generate_tpin_connection(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(ConnectionError):
        await pm_api.generate_tpin()


@pytest.mark.asyncio
async def test_validate_tpin_attribute(pm_api):
    pm_api.access_token = "test_access_token"
    with pytest.raises(ConnectionError):
        await pm_api.validate_tpin(
            trade_type="trade_type",
            isin_list=None
        )


@pytest.mark.asyncio
async def test_validate_tpin_connection(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(ConnectionError):
        await pm_api.validate_tpin(
            trade_type="trade_type",
            isin_list=[]
        )


@pytest.mark.asyncio
async def test_status_attribute(pm_api):
    # Invalid edis_request_id or null may cause this exception.
    pm_api.access_token = "test_access_token"
    with pytest.raises(Exception):
        await pm_api.status(edis_request_id="req_id")


@pytest.mark.asyncio
async def test_status_connection(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(ConnectionError):
        await pm_api.status(edis_request_id="req_id")


@pytest.mark.asyncio
async def test_get_user_details_connection(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(ConnectionError):
        await pm_api.get_user_details()


# def test_price_chart_sym_connection(pm_api):
#     pm_api.access_token = "invalid_token"
#     with pytest.raises(ConnectionError):
#         pm_api.price_chart_sym(
#             cont="false",
#             exchange="NSE",
#             expiry="2022-04-26",
#             from_date="2022-02-10",
#             inst_type="FUTIDX",
#             interval="MINUTE",
#             symbol="MIDCPNIFTY",
#             to_date="2022-02-05"
#         )


def test_price_chart_sym_attribute(pm_api):
    pm_api.access_token = "eyJhbGciOiJIUzI1NiJ9.eyJhcGlLZXkiOiIwNTY2ZTRhMGIyNzI0Y2NlYTA2ZjMwYTdhMTlkMTk4NyIsIm1lcmNoYW50SWQiOiJNRVJfMjI2IiwicGFzc2NvZGVWYWxpZCI6dHJ1ZSwiYXV0aG9yaXNhdGlvbiI6IltcIlAxXCIsXCJQMlwiLFwiUDNcIixcIlA0XCJdIiwicGFzc2NvZGVWYWxpZFRpbGxFUE9DU2Vjb25kcyI6IjE2NTk5ODMzNDAwMDAiLCJzc29Ub2tlbiI6IlVmNndtYURTZDNrT3NNdlJQeFptOGlpNDFsbHhIMXFUNTlRK2hOeXVCcTMzN0FFSTFXTmlNUXQwcjlrWS9MMXMiLCJ1c2VySWQiOiI3OTQ1NjkiLCJpc3MiOiJwYXl0bW1vbmV5IiwiYXVkIjoibWVyY2hhbnQifQ.V_A8GjygTEWtArfF4ZM-04nyIe053rWTmcbmyDo0iYM"
    with pytest.raises(Exception):
        pm_api.price_chart_sym(
            cont="false",
            exchange="NSE",
            expiry="2022-04-26",
            from_date="2022-02-10",
            inst_type="FUTIDX",
            interval="MINUTE",
            symbol="",
            to_date="2022-02-05"
        )


@pytest.mark.asyncio
async def test_create_gtt_connection(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(ConnectionError):
        await pm_api.create_gtt(
            segment="E",
            exchange="NSE",
            pml_id="1000001488",
            security_id="14366",
            product_type="C",
            set_price=12.80,
            transaction_type="S",
            quantity=1,
            trigger_price=12.7,
            limit_price=0,
            order_type="MKT",
            trigger_type="SINGLE"
        )


@pytest.mark.asyncio
async def test_create_gtt_attribute(pm_api):
    pm_api.access_token = "test_access_token"
    with pytest.raises(ConnectionError):
        await pm_api.create_gtt(
            segment="E",
            exchange=9.0,
            pml_id="1000001488",
            security_id="14366",
            product_type="C",
            set_price=12.80,
            transaction_type="S",
            quantity=1,
            trigger_price=12.7,
            limit_price=0,
            order_type="",
            trigger_type="SINGLE"
        )


@pytest.mark.asyncio
async def test_get_gtt_by_status_or_id_connection1(pm_api, mocker):
    response = "response"
    mocker.patch("pmClient.apiService.ApiService.api_call_helper", return_value=response)
    await pm_api.get_gtt_by_pml_id_and_status(
        status="ACTIVE",
        pml_id="1000001488"
    )


@pytest.mark.asyncio
async def test_get_gtt_by_status_or_id_connection2(pm_api, mocker):
    response = "response"
    mocker.patch("pmClient.apiService.ApiService.api_call_helper", return_value=response)
    await pm_api.get_gtt_by_pml_id_and_status(
        status="ACTIVE",
        pml_id=""
    )


@pytest.mark.asyncio
async def test_get_gtt_by_status_or_id_connection3(pm_api, mocker):
    response = "response"
    mocker.patch("pmClient.apiService.ApiService.api_call_helper", return_value=response)
    await pm_api.get_gtt_by_pml_id_and_status(
        status="",
        pml_id="123"
    )


@pytest.mark.asyncio
async def test_get_gtt_by_status_or_id_connection4(pm_api, mocker):
    response = "response"
    mocker.patch("pmClient.apiService.ApiService.api_call_helper", return_value=response)
    await pm_api.get_gtt_by_pml_id_and_status(
        status="",
        pml_id=""
    )


@pytest.mark.asyncio
async def test_get_gtt_by_status_or_id_attribute(pm_api):
    pm_api.access_token = "test_access_token"
    with pytest.raises(ConnectionError):
        await pm_api.get_gtt_by_pml_id_and_status(
            status="ACTIE",
            pml_id="1000001488"
        )


@pytest.mark.asyncio
async def test_update_gtt_connection(pm_api):
    pm_api.access_token = "Invalid_token"
    with pytest.raises(ConnectionError):
        await pm_api.update_gtt(
            id=987,
            set_price=12.80,
            transaction_type="S",
            quantity=3,
            trigger_price=12.7,
            limit_price=0,
            order_type="MKT",
            trigger_type="SINGLE"
        )


@pytest.mark.asyncio
async def test_update_gtt_attribute(pm_api):
    pm_api.access_token = "eyJhbGciOiJIUzI1NiJ9.eyJhcGlLZXkiOiIwNTY2ZTRhMGIyNzI0Y2NlYTA2ZjMwYTdhMTlkMTk4NyIsIm1lcmNoYW50SWQiOiJNRVJfMjI2IiwicGFzc2NvZGVWYWxpZCI6dHJ1ZSwiYXV0aG9yaXNhdGlvbiI6IltcIlAxXCIsXCJQMlwiLFwiUDNcIixcIlA0XCJdIiwicGFzc2NvZGVWYWxpZFRpbGxFUE9DU2Vjb25kcyI6IjE2NTk5ODMzNDAwMDAiLCJzc29Ub2tlbiI6IlVmNndtYURTZDNrT3NNdlJQeFptOGlpNDFsbHhIMXFUNTlRK2hOeXVCcTMzN0FFSTFXTmlNUXQwcjlrWS9MMXMiLCJ1c2VySWQiOiI3OTQ1NjkiLCJpc3MiOiJwYXl0bW1vbmV5IiwiYXVkIjoibWVyY2hhbnQifQ.V_A8GjygTEWtArfF4ZM-04nyIe053rWTmcbmyDo0iYM"
    with pytest.raises(Exception):
        await pm_api.update_gtt(
            id=987,
            set_price=12.80,
            transaction_type=5,
            quantity=3,
            trigger_price=12.7,
            limit_price=0,
            order_type="",
            trigger_type="SINGLE"
        )


@pytest.mark.asyncio
async def test_get_gtt_connection(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(ConnectionError):
        await pm_api.get_gtt(
            id=4563,
        )


@pytest.mark.asyncio
async def test_delete_gtt_connection(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(ConnectionError):
        await pm_api.delete_gtt(
            id=4563,
        )


@pytest.mark.asyncio
async def test_get_gtt__aggregate_connection(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(ConnectionError):
        await pm_api.get_gtt_aggregate()


@pytest.mark.asyncio
async def test_get_gtt_expiry_connection(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(ConnectionError):
        await pm_api.get_gtt_expiry_date(
            pml_id="1000001488",
        )


@pytest.mark.asyncio
async def test_get_gtt_by_instruction_id_connection(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(Exception):
        await pm_api.get_gtt_by_instruction_id(
            id="4563",
        )

@pytest.mark.asyncio
async def test_create_gtt_v2_connection(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(ConnectionError):
        await pm_api.create_gtt_v2(
            segment="E",
            exchange=9.0,
            security_id="14366",
            product_type="C",
            set_price=12.80,
            transaction_type="S",
            trigger_type="SINGLE",
            transaction_details=""
        )


@pytest.mark.asyncio
async def test_create_gtt_v2_attribute(pm_api):
    pm_api.access_token = "test_access_token"
    with pytest.raises(ConnectionError):
        await pm_api.create_gtt_v2(
            segment="E",
            exchange=9.0,
            security_id="14366",
            product_type="C",
            set_price=12.80,
            transaction_type="S",
            trigger_type="SINGLE",
            transaction_details=""
        )

@pytest.mark.asyncio
async def test_get_gtt_by_status_or_id_v2_connection1(pm_api, mocker):
    response = "response"
    mocker.patch("pmClient.apiService.ApiService.api_call_helper", return_value=response)
    await pm_api.get_gtt_by_pml_id_and_status_v2(
        status="ACTIVE",
        pml_id="1000001488"
    )


@pytest.mark.asyncio
async def test_get_gtt_by_status_or_id_v2_connection2(pm_api, mocker):
    response = "response"
    mocker.patch("pmClient.apiService.ApiService.api_call_helper", return_value=response)
    await pm_api.get_gtt_by_pml_id_and_status_v2(
        status="ACTIVE",
        pml_id=""
    )


@pytest.mark.asyncio
async def test_get_gtt_by_status_or_id_v2_connection3(pm_api, mocker):
    response = "response"
    mocker.patch("pmClient.apiService.ApiService.api_call_helper", return_value=response)
    await pm_api.get_gtt_by_pml_id_and_status_v2(
        status="",
        pml_id="123"
    )


@pytest.mark.asyncio
async def test_get_gtt_by_status_or_id_v2_connection4(pm_api, mocker):
    response = "response"
    mocker.patch("pmClient.apiService.ApiService.api_call_helper", return_value=response)
    await pm_api.get_gtt_by_pml_id_and_status_v2(
        status="",
        pml_id=""
    )


@pytest.mark.asyncio
async def test_get_gtt_by_status_or_id_v2_attribute(pm_api):
    pm_api.access_token = "test_access_token"
    with pytest.raises(ConnectionError):
        await pm_api.get_gtt_by_pml_id_and_status_v2(
            status="ACTIE",
            pml_id="1000001488"
        )

@pytest.mark.asyncio
async def test_update_gtt_v2_connection(pm_api):
    pm_api.access_token = "Invalid_token"
    with pytest.raises(ConnectionError):
        await pm_api.update_gtt_v2(
            id=987,
            set_price=12.80,
            transaction_type="S",
            trigger_type="SINGLE",
            transaction_details=""
        )


@pytest.mark.asyncio
async def test_update_gtt_v2_attribute(pm_api):
    pm_api.access_token = "access_token"
    with pytest.raises(Exception):
        await pm_api.update_gtt_v2(
            id=987,
            set_price=12.80,
            transaction_type=5,
            trigger_type="SINGLE",
            transaction_details=""
        )

@pytest.mark.asyncio
async def test_get_gtt_v2_connection(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(ConnectionError):
        await pm_api.get_gtt_v2(
            id=4563,
        )

@pytest.mark.asyncio
async def test_get_gtt_by_instruction_id_v2_connection(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(Exception):
        await pm_api.get_gtt_by_instruction_id_v2(
            id="4563",
        )

def test_live_market_data(pm_api, mocker):
    response = {
        "data": [
            {
                "last_trade_time": 1,
                "last_update_time": 1
            }
        ]
    }
    mocker.patch("pmClient.apiService.ApiService.api_call_helper", return_value=response)
    pm_api.get_live_market_data(
        mode_type="FULL",
        preferences="NSE:13:INDEX"
    )


@pytest.mark.asyncio
async def test_get_option_chain(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(ConnectionError):
        await pm_api.get_option_chain(
            type="CALL",
            symbol="NSE",
            expiry="expiry"
        )


@pytest.mark.asyncio
async def test_get_option_chain_config(pm_api):
    pm_api.access_token = "invalid_token"
    with pytest.raises(ConnectionError):
        await pm_api.get_option_chain_config(
            symbol="symbol"
        )
