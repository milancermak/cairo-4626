%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.cairo.common.bool import TRUE
from starkware.cairo.common.uint256 import Uint256

from contracts.lib.openzeppelin.token.erc20.library import ERC20
from contracts.erc4626.library import ERC4626

@constructor
func constructor{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    name: felt, symbol: felt, asset_addr: felt
) {
    ERC4626.initializer(name, symbol, asset_addr);
    return ();
}

//
// ERC 20
//

//
// Getters
//

@view
func name{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() -> (name: felt) {
    let (name) = ERC20.name();
    return (name,);
}

@view
func symbol{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() -> (symbol: felt) {
    let (symbol) = ERC20.symbol();
    return (symbol,);
}

@view
func totalSupply{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() -> (
    totalSupply: Uint256
) {
    let (totalSupply: Uint256) = ERC20.total_supply();
    return (totalSupply,);
}

@view
func decimals{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() -> (
    decimals: felt
) {
    let (decimals) = ERC20.decimals();
    return (decimals,);
}

@view
func balanceOf{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(account: felt) -> (
    balance: Uint256
) {
    let (balance: Uint256) = ERC20.balance_of(account);
    return (balance,);
}

@view
func allowance{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    owner: felt, spender: felt
) -> (remaining: Uint256) {
    let (remaining: Uint256) = ERC20.allowance(owner, spender);
    return (remaining,);
}

//
// Externals
//

@external
func transfer{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    recipient: felt, amount: Uint256
) -> (success: felt) {
    ERC20.transfer(recipient, amount);
    return (TRUE,);
}

@external
func transferFrom{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    sender: felt, recipient: felt, amount: Uint256
) -> (success: felt) {
    ERC20.transfer_from(sender, recipient, amount);
    return (TRUE,);
}

@external
func approve{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    spender: felt, amount: Uint256
) -> (success: felt) {
    ERC20.approve(spender, amount);
    return (TRUE,);
}

//
// ERC 4626
//

@view
func asset{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() -> (
    assetTokenAddress: felt
) {
    let (asset: felt) = ERC4626.asset();
    return (asset,);
}

@view
func totalAssets{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() -> (
    totalManagedAssets: Uint256
) {
    let (total: Uint256) = ERC4626.total_assets();
    return (total,);
}

@view
func convertToShares{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    assets: Uint256
) -> (shares: Uint256) {
    let (shares: Uint256) = ERC4626.convert_to_shares(assets);
    return (shares,);
}

@view
func convertToAssets{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    shares: Uint256
) -> (assets: Uint256) {
    let (assets: Uint256) = ERC4626.convert_to_assets(shares);
    return (assets,);
}

@view
func maxDeposit{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    receiver: felt
) -> (maxAssets: Uint256) {
    let (maxAssets: Uint256) = ERC4626.max_deposit(receiver);
    return (maxAssets,);
}

@view
func previewDeposit{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    assets: Uint256
) -> (shares: Uint256) {
    let (shares: Uint256) = ERC4626.preview_deposit(assets);
    return (shares,);
}

@external
func deposit{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    assets: Uint256, receiver: felt
) -> (shares: Uint256) {
    let (shares: Uint256) = ERC4626.deposit(assets, receiver);
    return (shares,);
}

@view
func maxMint{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(receiver: felt) -> (
    maxShares: Uint256
) {
    let (maxShares: Uint256) = ERC4626.max_mint(receiver);
    return (maxShares,);
}

@view
func previewMint{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    shares: Uint256
) -> (assets: Uint256) {
    let (assets: Uint256) = ERC4626.preview_mint(shares);
    return (assets,);
}

@external
func mint{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    shares: Uint256, receiver: felt
) -> (assets: Uint256) {
    let (assets: Uint256) = ERC4626.mint(shares, receiver);
    return (assets,);
}

@view
func maxWithdraw{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(owner: felt) -> (
    maxAssets: Uint256
) {
    let (maxWithdraw: Uint256) = ERC4626.max_withdraw(owner);
    return (maxWithdraw,);
}

@view
func previewWithdraw{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    assets: Uint256
) -> (shares: Uint256) {
    let (shares: Uint256) = ERC4626.preview_withdraw(assets);
    return (shares,);
}

@external
func withdraw{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    assets: Uint256, receiver: felt, owner: felt
) -> (shares: Uint256) {
    let (shares: Uint256) = ERC4626.withdraw(assets, receiver, owner);
    return (shares,);
}

@view
func maxRedeem{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(owner: felt) -> (
    maxShares: Uint256
) {
    let (maxShares: Uint256) = ERC4626.max_redeem(owner);
    return (maxShares,);
}

@view
func previewRedeem{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    shares: Uint256
) -> (assets: Uint256) {
    let (assets: Uint256) = ERC4626.preview_redeem(shares);
    return (assets,);
}

@external
func redeem{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    shares: Uint256, receiver: felt, owner: felt
) -> (assets: Uint256) {
    let (assets: Uint256) = ERC4626.redeem(shares, receiver, owner);
    return (assets,);
}
