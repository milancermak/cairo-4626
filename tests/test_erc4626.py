import pytest
from starkware.cairo.lang.vm.vm_exceptions import VmException
from starkware.starkware_utils.error_handling import StarkException


@pytest.mark.asyncio
@pytest.mark.parametrize("uint256, expected", [((0, 0), 1), ((1, 0), 0), ((0, 1), 0)])
async def test_uint256_is_zero(terc4626, uint256, expected):
    tx = await terc4626.test_uint256_is_zero(uint256).invoke()
    assert tx.result.yesno == expected


@pytest.mark.asyncio
async def test_uint256_max(terc4626):
    tx = await terc4626.test_uint256_max().invoke()
    uint256_max = (2**128-1, 2**128-1)
    assert tx.result.res == uint256_max


@pytest.mark.asyncio
async def test_uint256_mul_checked(terc4626):
    a = (2, 0)
    b = (3, 0)
    tx = await terc4626.test_uint256_mul_checked(a, b).invoke()
    assert tx.result.product == (6, 0)

    with pytest.raises(StarkException):
        a = (2**120, 2**120)
        b = (2**121, 2**121)
        _ = await terc4626.test_uint256_mul_checked(a, b).invoke()

@pytest.mark.asyncio
async def test_uint256_unsigned_div_rem_up(terc4626):
    # division without reminder
    a = (12, 0)
    b = (4, 0)
    tx = await terc4626.test_uint256_unsigned_div_rem_up(a, b).invoke()
    assert tx.result.res == (3, 0)

    # division rounded up
    a = (11, 0)
    b = (4, 0)
    tx = await terc4626.test_uint256_unsigned_div_rem_up(a, b).invoke()
    assert tx.result.res == (3, 0)
