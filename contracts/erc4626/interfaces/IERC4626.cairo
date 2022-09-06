%lang starknet

from starkware.cairo.common.uint256 import Uint256

@contract_interface
namespace IERC4626 {
    func asset() -> (assetTokenAddress: felt) {
    }

    func totalAssets() -> (totalManagedAssets: Uint256) {
    }

    func convertToShares(assets: Uint256) -> (shares: Uint256) {
    }

    func convertToAssets(shares: Uint256) -> (assets: Uint256) {
    }

    func maxDeposit(receiver: felt) -> (maxAssets: Uint256) {
    }

    func previewDeposit(assets: Uint256) -> (shares: Uint256) {
    }

    func deposit(assets: Uint256, receiver: felt) -> (shares: Uint256) {
    }

    func maxMint(receiver: felt) -> (maxShares: Uint256) {
    }

    func previewMint(shares: Uint256) -> (assets: Uint256) {
    }

    func mint(shares: Uint256, receiver: felt) -> (assets: Uint256) {
    }

    func maxWithdraw(owner: felt) -> (maxAssets: Uint256) {
    }

    func previewWithdraw(assets: Uint256) -> (shares: Uint256) {
    }

    func withdraw(assets: Uint256, receiver: felt, owner: felt) -> (shares: Uint256) {
    }

    func maxRedeem(owner: felt) -> (maxShares: Uint256) {
    }

    func previewRedeem(shares: Uint256) -> (assets: Uint256) {
    }

    func redeem(shares: Uint256, receiver: felt, owner: felt) -> (assets: Uint256) {
    }
}
