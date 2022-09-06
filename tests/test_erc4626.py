import pytest
from conftest import ASSET_OWNER
from utils import str_to_felt, to_uint, assert_event_emitted
from starkware.starkware_utils.error_handling import StarkException


UINT_MAX = (2**128 - 1, 2**128 - 1)


@pytest.mark.asyncio
@pytest.mark.order(1)
async def test_init(erc4626, asset):
    # contract is already compiled and deployed as a fixture
    # in conftest.py, checking the basics here
    assert (await erc4626.name().execute()).result.name == str_to_felt("Vault of Winning")
    assert (await erc4626.symbol().execute()).result.symbol == str_to_felt("vWIN")
    assert (await erc4626.decimals().execute()).result.decimals == 18
    assert (await erc4626.asset().execute()).result.assetTokenAddress == asset.contract_address
    assert (await erc4626.totalAssets().execute()).result.totalManagedAssets == to_uint(0)


@pytest.mark.asyncio
async def test_conversions(erc4626):
    shares = to_uint(1000)
    assets = to_uint(1000)

    # convertToAssets(convertToShares(assets)) == assets
    converted_shares = (await erc4626.convertToShares(assets).execute()).result.shares
    converted_assets = (await erc4626.convertToAssets(converted_shares).execute()).result.assets
    assert assets == converted_assets

    # convertToShares(convertToAssets(shares)) == shares
    converted_assets = (await erc4626.convertToAssets(shares).execute()).result.assets
    converted_shares = (await erc4626.convertToShares(converted_assets).execute()).result.shares
    assert shares == converted_shares


@pytest.mark.asyncio
async def test_deposit_redeem_flow(erc4626, asset):
    DEPOSITOR = str_to_felt("depostior")

    # mint asset tokens to DEPOSITOR
    await asset.mint(DEPOSITOR, to_uint(100_000)).execute(caller_address=ASSET_OWNER)
    assert (await asset.balanceOf(DEPOSITOR).execute()).result.balance == to_uint(100_000)
    assert (await erc4626.maxDeposit(DEPOSITOR).execute()).result.maxAssets == UINT_MAX

    # max approve
    await asset.approve(erc4626.contract_address, UINT_MAX).execute(caller_address=DEPOSITOR)

    amount = to_uint(10_000)

    # deposit asset tokens to the vault, get shares
    tx = await erc4626.deposit(amount, DEPOSITOR).execute(caller_address=DEPOSITOR)
    assert_event_emitted(tx, "Deposit")
    assert (await erc4626.balanceOf(DEPOSITOR).execute()).result.balance == amount
    assert (await asset.balanceOf(DEPOSITOR).execute()).result.balance == to_uint(90_000)

    # redeem vault shares, get back assets
    tx = await erc4626.redeem(amount, DEPOSITOR, DEPOSITOR).execute(caller_address=DEPOSITOR)
    assert_event_emitted(tx, "Withdraw")
    assert (await erc4626.balanceOf(DEPOSITOR).execute()).result.balance == to_uint(0)
    assert (await asset.balanceOf(DEPOSITOR).execute()).result.balance == to_uint(100_000)


@pytest.mark.asyncio
async def test_mint_withdraw_flow(erc4626, asset):
    MINTER = str_to_felt("minter")

    # mint asset tokens to MINTER
    await asset.mint(MINTER, to_uint(100_000)).execute(caller_address=ASSET_OWNER)
    assert (await asset.balanceOf(MINTER).execute()).result.balance == to_uint(100_000)
    assert (await erc4626.maxMint(MINTER).execute()).result.maxShares == UINT_MAX
    assert (await erc4626.balanceOf(MINTER).execute()).result.balance == to_uint(0)

    # max approve
    await asset.approve(erc4626.contract_address, UINT_MAX).execute(caller_address=MINTER)

    amount = to_uint(10_000)

    # mint shares for assets
    tx = await erc4626.mint(amount, MINTER).execute(caller_address=MINTER)
    assert_event_emitted(tx, "Deposit")
    assert (await erc4626.balanceOf(MINTER).execute()).result.balance == amount
    assert (await asset.balanceOf(MINTER).execute()).result.balance == to_uint(90_000)

    # withdraw shares, get back assets
    tx = await erc4626.withdraw(amount, MINTER, MINTER).execute(caller_address=MINTER)
    assert_event_emitted(tx, "Withdraw")
    assert (await erc4626.balanceOf(MINTER).execute()).result.balance == to_uint(0)
    assert (await asset.balanceOf(MINTER).execute()).result.balance == to_uint(100_000)


@pytest.mark.asyncio
async def test_allowances(erc4626, asset):
    CAPO = str_to_felt("capo")
    MAXI = str_to_felt("maxi")
    MINI = str_to_felt("mini")

    amount = to_uint(100_000)

    # mint assets to capo
    await asset.mint(CAPO, amount).execute(caller_address=ASSET_OWNER)
    assert (await asset.balanceOf(CAPO).execute()).result.balance == amount

    # have capo get shares in valut
    await asset.approve(erc4626.contract_address, UINT_MAX).execute(caller_address=CAPO)
    await erc4626.mint(amount, CAPO).execute(caller_address=CAPO)

    # max approve maxi
    await erc4626.approve(MAXI, UINT_MAX).execute(caller_address=CAPO)

    # approve mini only for 10K
    await erc4626.approve(MINI, to_uint(10_000)).execute(caller_address=CAPO)

    #
    # have maxi withdraw 50K assets from capo's vault position
    #
    assert (await erc4626.balanceOf(CAPO).execute()).result.balance == to_uint(100_000)
    assert (await erc4626.balanceOf(MAXI).execute()).result.balance == to_uint(0)
    assert (await asset.balanceOf(MAXI).execute()).result.balance == to_uint(0)

    await erc4626.withdraw(to_uint(50_000), MAXI, CAPO).execute(caller_address=MAXI)

    assert (await erc4626.balanceOf(CAPO).execute()).result.balance == to_uint(50_000)
    assert (await erc4626.balanceOf(MAXI).execute()).result.balance == to_uint(0)
    assert (await asset.balanceOf(MAXI).execute()).result.balance == to_uint(50_000)
    assert (await erc4626.allowance(CAPO, MAXI).execute()).result.remaining == UINT_MAX

    #
    # have mini withdraw 10K assets from capo's vaule position
    #
    assert (await erc4626.balanceOf(MINI).execute()).result.balance == to_uint(0)
    assert (await asset.balanceOf(MINI).execute()).result.balance == to_uint(0)

    await erc4626.withdraw(to_uint(10_000), MINI, CAPO).execute(caller_address=MINI)

    assert (await erc4626.balanceOf(CAPO).execute()).result.balance == to_uint(40_000)
    assert (await erc4626.balanceOf(MINI).execute()).result.balance == to_uint(0)
    assert (await asset.balanceOf(MINI).execute()).result.balance == to_uint(10_000)
    assert (await erc4626.allowance(CAPO, MINI).execute()).result.remaining == to_uint(0)

    # mini tries withdrawing again, has insufficient allowance, :burn:
    with pytest.raises(StarkException):
        await erc4626.withdraw(to_uint(1), MINI, CAPO).execute(caller_address=MINI)


@pytest.mark.asyncio
@pytest.mark.parametrize("uint256, expected", [((0, 0), 1), ((1, 0), 0), ((0, 1), 0)])
async def test_uint256_is_zero(terc4626, uint256, expected):
    tx = await terc4626.test_uint256_is_zero(uint256).execute()
    assert tx.result.yesno == expected


@pytest.mark.asyncio
async def test_uint256_max(terc4626):
    tx = await terc4626.test_uint256_max().execute()
    assert tx.result.res == UINT_MAX


@pytest.mark.asyncio
async def test_uint256_mul_checked(terc4626):
    a = (2, 0)
    b = (3, 0)
    tx = await terc4626.test_uint256_mul_checked(a, b).execute()
    assert tx.result.product == (6, 0)

    with pytest.raises(StarkException):
        a = (2**120, 2**120)
        b = (2**121, 2**121)
        _ = await terc4626.test_uint256_mul_checked(a, b).execute()


@pytest.mark.asyncio
async def test_uint256_unsigned_div_rem_up(terc4626):
    # division without reminder
    a = (12, 0)
    b = (4, 0)
    tx = await terc4626.test_uint256_unsigned_div_rem_up(a, b).execute()
    assert tx.result.res == (3, 0)

    # division rounded up
    a = (11, 0)
    b = (4, 0)
    tx = await terc4626.test_uint256_unsigned_div_rem_up(a, b).execute()
    assert tx.result.res == (3, 0)
