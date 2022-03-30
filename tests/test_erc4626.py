import pytest
from utils import str_to_felt, to_uint, assert_event_emitted
from starkware.starkware_utils.error_handling import StarkException


UINT_MAX = (2 ** 128 - 1, 2 ** 128 - 1)


@pytest.mark.asyncio
@pytest.mark.order(1)
async def test_init(erc4626, asset):
    # contract is already compiled and deployed as a fixture
    # in conftest.py, checking the basics here
    assert (await erc4626.name().invoke()).result.name == str_to_felt("Vault of Winning")
    assert (await erc4626.symbol().invoke()).result.symbol == str_to_felt("vWIN")
    assert (await erc4626.decimals().invoke()).result.decimals == 18
    assert (await erc4626.asset().invoke()).result.assetTokenAddress == asset.contract_address
    assert (await erc4626.totalAssets().invoke()).result.totalManagedAssets == to_uint(0)


@pytest.mark.asyncio
async def test_conversions(erc4626):
    shares = to_uint(1000)
    assets = to_uint(1000)

    # convertToAssets(convertToShares(assets)) == assets
    converted_shares = (await erc4626.convertToShares(assets).invoke()).result.shares
    converted_assets = (await erc4626.convertToAssets(converted_shares).invoke()).result.assets
    assert assets == converted_assets

    # convertToShares(convertToAssets(shares)) == shares
    converted_assets = (await erc4626.convertToAssets(shares).invoke()).result.assets
    converted_shares = (await erc4626.convertToShares(converted_assets).invoke()).result.shares
    assert shares == converted_shares


@pytest.mark.asyncio
async def test_deposit_redeem_flow(erc4626, users, asset):
    asset_owner_signer, asset_owner_account = await users("asset_owner")
    depositooor_signer, depositooor_account = await users("depositooor")

    # mint asset tokens to depositooor
    await asset_owner_signer.send_transaction(
        asset_owner_account,
        asset.contract_address,
        "mint",
        [depositooor_account.contract_address, *to_uint(100_000)],
    )
    assert (
        await asset.balanceOf(depositooor_account.contract_address).invoke()
    ).result.balance == to_uint(100_000)

    assert (
        await erc4626.maxDeposit(depositooor_account.contract_address).invoke()
    ).result.maxAssets == UINT_MAX

    # max approve
    await depositooor_signer.send_transaction(
        depositooor_account,
        asset.contract_address,
        "approve",
        [erc4626.contract_address, *UINT_MAX],
    )

    amount = to_uint(10_000)

    # deposit asset tokens to the vault, get shares
    tx = await depositooor_signer.send_transaction(
        depositooor_account,
        erc4626.contract_address,
        "deposit",
        [*amount, depositooor_account.contract_address],
    )

    assert (
        await erc4626.balanceOf(depositooor_account.contract_address).invoke()
    ).result.balance == amount
    assert_event_emitted(tx, "Deposit")
    assert (
        await asset.balanceOf(depositooor_account.contract_address).invoke()
    ).result.balance == to_uint(90_000)

    # redeem vault shares, get back assets
    tx = await depositooor_signer.send_transaction(
        depositooor_account,
        erc4626.contract_address,
        "redeem",
        [*amount, depositooor_account.contract_address, depositooor_account.contract_address],
    )

    assert (
        await erc4626.balanceOf(depositooor_account.contract_address).invoke()
    ).result.balance == to_uint(0)
    assert_event_emitted(tx, "Withdraw")
    assert (
        await asset.balanceOf(depositooor_account.contract_address).invoke()
    ).result.balance == to_uint(100_000)


@pytest.mark.asyncio
async def test_mint_withdraw_flow(erc4626, users, asset):
    asset_owner_signer, asset_owner_account = await users("asset_owner")
    mintooor_signer, mintooor_account = await users("mintooor")

    # mint asset tokens to the mintooor first
    await asset_owner_signer.send_transaction(
        asset_owner_account,
        asset.contract_address,
        "mint",
        [mintooor_account.contract_address, *to_uint(100_000)],
    )
    assert (
        await asset.balanceOf(mintooor_account.contract_address).invoke()
    ).result.balance == to_uint(100_000)

    assert (
        await erc4626.maxMint(mintooor_account.contract_address).invoke()
    ).result.maxShares == UINT_MAX
    assert (
        await erc4626.balanceOf(mintooor_account.contract_address).invoke()
    ).result.balance == to_uint(0)

    # max approve
    await mintooor_signer.send_transaction(
        mintooor_account, asset.contract_address, "approve", [erc4626.contract_address, *UINT_MAX]
    )

    amount = to_uint(10_000)

    # mint shares for assets
    tx = await mintooor_signer.send_transaction(
        mintooor_account,
        erc4626.contract_address,
        "mint",
        [*amount, mintooor_account.contract_address],
    )

    assert (
        await erc4626.balanceOf(mintooor_account.contract_address).invoke()
    ).result.balance == amount
    assert_event_emitted(tx, "Deposit")
    assert (
        await asset.balanceOf(mintooor_account.contract_address).invoke()
    ).result.balance == to_uint(90_000)

    # withdraw shares, get back assets
    tx = await mintooor_signer.send_transaction(
        mintooor_account,
        erc4626.contract_address,
        "withdraw",
        [*amount, mintooor_account.contract_address, mintooor_account.contract_address],
    )

    assert (
        await erc4626.balanceOf(mintooor_account.contract_address).invoke()
    ).result.balance == to_uint(0)
    assert_event_emitted(tx, "Withdraw")
    assert (
        await asset.balanceOf(mintooor_account.contract_address).invoke()
    ).result.balance == to_uint(100_000)


@pytest.mark.asyncio
async def test_allowances(erc4626, users, asset):
    asset_owner_signer, asset_owner_account = await users("asset_owner")
    capo_signer, capo_account = await users("capo")
    maxi_signer, maxi_account = await users("maxi")
    mini_signer, mini_account = await users("mini")

    amount = to_uint(100_000)

    # mint assets to capo
    await asset_owner_signer.send_transaction(
        asset_owner_account,
        asset.contract_address,
        "mint",
        [capo_account.contract_address, *amount],
    )
    assert (await asset.balanceOf(capo_account.contract_address).invoke()).result.balance == amount

    # have capo get shares in valut
    await capo_signer.send_transaction(
        capo_account, asset.contract_address, "approve", [erc4626.contract_address, *UINT_MAX]
    )
    await capo_signer.send_transaction(
        capo_account, erc4626.contract_address, "mint", [*amount, capo_account.contract_address]
    )

    # max approve maxi
    await capo_signer.send_transaction(
        capo_account,
        erc4626.contract_address,
        "approve",
        [maxi_account.contract_address, *UINT_MAX],
    )

    # approve mini only for 10K
    await capo_signer.send_transaction(
        capo_account,
        erc4626.contract_address,
        "approve",
        [mini_account.contract_address, *to_uint(10_000)],
    )

    #
    # have maxi withdraw 50K assets from capo's vault position
    #
    assert (
        await erc4626.balanceOf(capo_account.contract_address).invoke()
    ).result.balance == to_uint(100_000)
    assert (
        await erc4626.balanceOf(maxi_account.contract_address).invoke()
    ).result.balance == to_uint(0)
    assert (
        await asset.balanceOf(maxi_account.contract_address).invoke()
    ).result.balance == to_uint(0)

    await maxi_signer.send_transaction(
        maxi_account,
        erc4626.contract_address,
        "withdraw",
        [*to_uint(50_000), maxi_account.contract_address, capo_account.contract_address],
    )

    assert (
        await erc4626.balanceOf(capo_account.contract_address).invoke()
    ).result.balance == to_uint(50_000)
    assert (
        await erc4626.balanceOf(maxi_account.contract_address).invoke()
    ).result.balance == to_uint(0)
    assert (
        await asset.balanceOf(maxi_account.contract_address).invoke()
    ).result.balance == to_uint(50_000)
    assert (
        await erc4626.allowance(
            capo_account.contract_address, maxi_account.contract_address
        ).invoke()
    ).result.remaining == UINT_MAX

    #
    # have mini withdraw 10K assets from capo's vaule position
    #
    assert (
        await erc4626.balanceOf(mini_account.contract_address).invoke()
    ).result.balance == to_uint(0)
    assert (
        await asset.balanceOf(mini_account.contract_address).invoke()
    ).result.balance == to_uint(0)

    await mini_signer.send_transaction(
        mini_account,
        erc4626.contract_address,
        "withdraw",
        [*to_uint(10_000), mini_account.contract_address, capo_account.contract_address],
    )

    assert (
        await erc4626.balanceOf(capo_account.contract_address).invoke()
    ).result.balance == to_uint(40_000)
    assert (
        await erc4626.balanceOf(mini_account.contract_address).invoke()
    ).result.balance == to_uint(0)
    assert (
        await asset.balanceOf(mini_account.contract_address).invoke()
    ).result.balance == to_uint(10_000)
    assert (
        await erc4626.allowance(
            capo_account.contract_address, mini_account.contract_address
        ).invoke()
    ).result.remaining == to_uint(0)

    # mini tries withdrawing again, has insufficient allowance, :burn:
    with pytest.raises(StarkException):
        await mini_signer.send_transaction(
            mini_account,
            erc4626.contract_address,
            "withdraw",
            [*to_uint(1), mini_account.contract_address, capo_account.contract_address],
        )


@pytest.mark.asyncio
@pytest.mark.parametrize("uint256, expected", [((0, 0), 1), ((1, 0), 0), ((0, 1), 0)])
async def test_uint256_is_zero(terc4626, uint256, expected):
    tx = await terc4626.test_uint256_is_zero(uint256).invoke()
    assert tx.result.yesno == expected


@pytest.mark.asyncio
async def test_uint256_max(terc4626):
    tx = await terc4626.test_uint256_max().invoke()
    assert tx.result.res == UINT_MAX


@pytest.mark.asyncio
async def test_uint256_mul_checked(terc4626):
    a = (2, 0)
    b = (3, 0)
    tx = await terc4626.test_uint256_mul_checked(a, b).invoke()
    assert tx.result.product == (6, 0)

    with pytest.raises(StarkException):
        a = (2 ** 120, 2 ** 120)
        b = (2 ** 121, 2 ** 121)
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
