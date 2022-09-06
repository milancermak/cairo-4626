# amarna: disable=unused-function
%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.cairo.common.bool import TRUE, FALSE
from starkware.starknet.common.syscalls import get_caller_address, get_contract_address
from starkware.cairo.common.uint256 import (
    ALL_ONES,
    Uint256,
    uint256_eq,
    uint256_add,
    uint256_mul,
    uint256_sub,
    uint256_unsigned_div_rem,
    uint256_le,
)

from contracts.lib.openzeppelin.token.erc20.library import ERC20, ERC20_allowances
from contracts.lib.openzeppelin.token.erc20.IERC20 import IERC20

@event
func Deposit(caller : felt, owner : felt, assets : Uint256, shares : Uint256):
end

@event
func Withdraw(caller : felt, receiver : felt, owner : felt, assets : Uint256, shares : Uint256):
end

#
# Storage
#

@storage_var
func ERC4626_asset_addr() -> (addr : felt):
end

#
# Initializer
#

namespace ERC4626:
    func initializer{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        name : felt, symbol : felt, asset_addr : felt
    ):
        let (decimals) = IERC20.decimals(contract_address=asset_addr)
        ERC20.initializer(name, symbol, decimals)
        ERC4626_asset_addr.write(asset_addr)
        return ()
    end

    #
    # ERC4626
    #

    func asset{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}() -> (
        asset : felt
    ):
        let (asset : felt) = ERC4626_asset_addr.read()
        return (asset)
    end

    func total_assets{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}() -> (
        totalManagedAssets : Uint256
    ):
        let (asset : felt) = ERC4626.asset()
        let (vault : felt) = get_contract_address()
        let (total : Uint256) = IERC20.balanceOf(contract_address=asset, account=vault)
        return (total)
    end

    func convert_to_shares{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        assets : Uint256
    ) -> (shares : Uint256):
        alloc_locals

        let (total_supply : Uint256) = ERC20.total_supply()
        let (is_total_supply_zero : felt) = uint256_is_zero(total_supply)

        if is_total_supply_zero == TRUE:
            return (assets)
        else:
            let (product : Uint256) = uint256_mul_checked(assets, total_supply)
            let (total_assets : Uint256) = ERC4626.total_assets()
            let (shares, _) = uint256_unsigned_div_rem(product, total_assets)
            return (shares)
        end
    end

    func convert_to_assets{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        shares : Uint256
    ) -> (assets : Uint256):
        alloc_locals

        let (total_supply : Uint256) = ERC20.total_supply()
        let (is_total_supply_zero : felt) = uint256_is_zero(total_supply)

        if is_total_supply_zero == TRUE:
            return (shares)
        else:
            let (total_assets : Uint256) = ERC4626.total_assets()
            let (product : Uint256) = uint256_mul_checked(shares, total_assets)
            let (assets, _) = uint256_unsigned_div_rem(product, total_supply)
            return (assets)
        end
    end

    #
    # # Deposit
    #

    func max_deposit{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        receiver : felt
    ) -> (maxAssets : Uint256):
        let (maxAssets : Uint256) = uint256_max()
        return (maxAssets)
    end

    func preview_deposit{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        assets : Uint256
    ) -> (shares : Uint256):
        let (shares) = ERC4626.convert_to_shares(assets)
        return (shares)
    end

    func deposit{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        assets : Uint256, receiver : felt
    ) -> (shares : Uint256):
        alloc_locals

        let (shares : Uint256) = ERC4626.preview_deposit(assets)
        let (shares_is_zero : felt) = uint256_is_zero(shares)
        with_attr error_message("ERC4626: zero shares"):
            assert shares_is_zero = FALSE
        end

        let (asset : felt) = ERC4626.asset()
        let (caller : felt) = get_caller_address()
        let (vault : felt) = get_contract_address()

        let (success : felt) = IERC20.transferFrom(
            contract_address=asset, sender=caller, recipient=vault, amount=assets
        )
        with_attr error_message("ERC4626: transfer failed"):
            assert success = TRUE
        end

        ERC20._mint(receiver, shares)

        Deposit.emit(caller=caller, owner=receiver, assets=assets, shares=shares)

        return (shares)
    end

    #
    # # Mint
    #

    func max_mint{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        receiver : felt
    ) -> (maxShares : Uint256):
        let (maxShares) = uint256_max()
        return (maxShares)
    end

    func preview_mint{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        shares : Uint256
    ) -> (assets : Uint256):
        alloc_locals

        let (total_supply : Uint256) = ERC20.total_supply()
        let (is_total_supply_zero : felt) = uint256_is_zero(total_supply)

        if is_total_supply_zero == TRUE:
            return (shares)
        else:
            let (total_assets : Uint256) = ERC4626.total_assets()
            let (product : Uint256) = uint256_mul_checked(shares, total_assets)
            let (assets) = uint256_unsigned_div_rem_up(product, total_supply)
            return (assets)
        end
    end

    func mint{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        shares : Uint256, receiver : felt
    ) -> (assets : Uint256):
        alloc_locals

        let (assets : Uint256) = ERC4626.preview_mint(shares)

        let (asset : felt) = ERC4626.asset()
        let (caller : felt) = get_caller_address()
        let (vault : felt) = get_contract_address()

        let (success : felt) = IERC20.transferFrom(
            contract_address=asset, sender=caller, recipient=vault, amount=assets
        )
        with_attr error_message("ERC4626: transfer failed"):
            assert success = TRUE
        end

        ERC20._mint(receiver, shares)

        Deposit.emit(caller=caller, owner=receiver, assets=assets, shares=shares)

        return (assets)
    end

    #
    # # Withdraw
    #

    func max_withdraw{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        owner : felt
    ) -> (maxAssets : Uint256):
        let (owner_balance : Uint256) = ERC20.balance_of(owner)
        let (maxAssets : Uint256) = ERC4626.convert_to_assets(owner_balance)
        return (maxAssets)
    end

    func preview_withdraw{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        assets : Uint256
    ) -> (shares : Uint256):
        alloc_locals

        let (total_supply : Uint256) = ERC20.total_supply()
        let (is_total_supply_zero : felt) = uint256_is_zero(total_supply)

        if is_total_supply_zero == TRUE:
            return (assets)
        else:
            let (total_assets : Uint256) = ERC4626.total_assets()
            let (product : Uint256) = uint256_mul_checked(assets, total_supply)
            let (shares : Uint256) = uint256_unsigned_div_rem_up(product, total_assets)
            return (shares)
        end
    end

    func withdraw{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        assets : Uint256, receiver : felt, owner : felt
    ) -> (shares : Uint256):
        alloc_locals

        let (shares : Uint256) = ERC4626.preview_withdraw(assets)

        let (caller : felt) = get_caller_address()

        if caller != owner:
            decrease_allowance_by_amount(owner, caller, shares)
            tempvar syscall_ptr = syscall_ptr
            tempvar pedersen_ptr = pedersen_ptr
            tempvar range_check_ptr = range_check_ptr
        else:
            tempvar syscall_ptr = syscall_ptr
            tempvar pedersen_ptr = pedersen_ptr
            tempvar range_check_ptr = range_check_ptr
        end

        ERC20._burn(owner, shares)

        let (asset : felt) = ERC4626.asset()
        let (success : felt) = IERC20.transfer(
            contract_address=asset, recipient=receiver, amount=assets
        )
        with_attr error_message("ERC4626: transfer failed"):
            assert success = TRUE
        end

        Withdraw.emit(caller=caller, receiver=receiver, owner=owner, assets=assets, shares=shares)

        return (shares)
    end

    #
    # # REDEEM
    #

    func max_redeem{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        owner : felt
    ) -> (maxShares : Uint256):
        let (maxShares : Uint256) = ERC20.balance_of(owner)
        return (maxShares)
    end

    func preview_redeem{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        shares : Uint256
    ) -> (assets : Uint256):
        let (assets : Uint256) = ERC4626.convert_to_assets(shares)
        return (assets)
    end

    func redeem{syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr}(
        shares : Uint256, receiver : felt, owner : felt
    ) -> (assets : Uint256):
        alloc_locals

        let (caller : felt) = get_caller_address()

        if caller != owner:
            decrease_allowance_by_amount(owner, caller, shares)
            tempvar syscall_ptr = syscall_ptr
            tempvar pedersen_ptr = pedersen_ptr
            tempvar range_check_ptr = range_check_ptr
        else:
            tempvar syscall_ptr = syscall_ptr
            tempvar pedersen_ptr = pedersen_ptr
            tempvar range_check_ptr = range_check_ptr
        end

        let (assets : Uint256) = ERC4626.preview_redeem(shares)
        let (is_zero_assets : felt) = uint256_is_zero(assets)
        with_attr error_message("ERC4626: zero assets"):
            assert is_zero_assets = FALSE
        end

        ERC20._burn(owner, shares)

        let (asset : felt) = ERC4626.asset()
        let (success : felt) = IERC20.transfer(
            contract_address=asset, recipient=receiver, amount=assets
        )
        with_attr error_message("ERC4626: transfer failed"):
            assert success = TRUE
        end

        Withdraw.emit(caller=caller, receiver=receiver, owner=owner, assets=assets, shares=shares)

        return (assets)
    end
end

#
# allowance helper
#

func decrease_allowance_by_amount{
    syscall_ptr : felt*, pedersen_ptr : HashBuiltin*, range_check_ptr
}(owner : felt, spender : felt, amount : Uint256):
    alloc_locals

    let (spender_allowance : Uint256) = ERC20_allowances.read(owner, spender)

    let (max_allowance : Uint256) = uint256_max()
    let (is_max_allowance) = uint256_eq(spender_allowance, max_allowance)
    if is_max_allowance == 1:
        return ()
    end

    with_attr error_message("ERC4626: insufficient allowance"):
        # amount <= spender_allowance
        let (is_spender_allowance_sufficient) = uint256_le(amount, spender_allowance)
        assert is_spender_allowance_sufficient = 1
    end

    let (new_allowance : Uint256) = uint256_sub(spender_allowance, amount)
    ERC20_allowances.write(owner, spender, new_allowance)

    return ()
end

#
# Uint256 helper functions
#

func uint256_is_zero{range_check_ptr}(v : Uint256) -> (yesno : felt):
    let (yesno : felt) = uint256_eq(v, Uint256(0, 0))
    return (yesno)
end

func uint256_max() -> (res : Uint256):
    return (Uint256(low=ALL_ONES, high=ALL_ONES))
end

func uint256_mul_checked{range_check_ptr}(a : Uint256, b : Uint256) -> (product : Uint256):
    alloc_locals

    let (product, carry) = uint256_mul(a, b)
    let (in_range) = uint256_is_zero(carry)
    with_attr error_message("ERC4626: number too big"):
        assert in_range = TRUE
    end
    return (product)
end

func uint256_unsigned_div_rem_up{range_check_ptr}(a : Uint256, b : Uint256) -> (res : Uint256):
    alloc_locals

    let (q, r) = uint256_unsigned_div_rem(a, b)
    let (reminder_is_zero : felt) = uint256_is_zero(r)

    if reminder_is_zero == TRUE:
        return (q)
    else:
        let (rounded_up, oof) = uint256_add(q, Uint256(low=1, high=0))
        with_attr error_message("ERC4626: rounding overflow"):
            assert oof = 0
        end
        return (rounded_up)
    end
end
