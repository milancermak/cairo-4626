# cairo-4626

Minimal [EIP 4626](https://eips.ethereum.org/EIPS/eip-4626) implementation in Cairo lang for [StarkNet](https://starknet.io/).

The contract is based on OpenZeppelin's ERC20 implementation and overal contract structure and heavily inspired by Solmate's ERC4626.sol.

A word of warning - the repo is still a work in progress, at minimum tests and proper documentation is still missing.

## Compiling

To compile the contract, you'll need to set the module import path (`CAIRO_PATH`) to point to the `contracts/lib` directory:

```shell
CAIRO_PATH=`pwd`/contracts/lib nile compile
```

## Customizing

Following OpenZeppelin's [StarkNet extensibility pattern](https://github.com/OpenZeppelin/cairo-contracts/blob/main/docs/Extensibility.md#the-pattern), all modifications regarding your EIP4626 business logic should go in the `contracts/erc4626/library.cairo` file.
