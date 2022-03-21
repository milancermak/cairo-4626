# this file only exposes private (non-@external or non-@view) functions
# from the main contract (ERC4626.cairo) and exists purely as a helper
# for testing; you can ignore / remove it in your own implementation

%lang starknet

from starkware.cairo.common.uint256 import Uint256

from library import uint256_is_zero, uint256_max, uint256_mul_checked, uint256_unsigned_div_rem_up

@view
func test_uint256_is_zero{range_check_ptr}(v : Uint256) -> (yesno : felt):
    let (yesno) = uint256_is_zero(v)
    return (yesno)
end

@view
func test_uint256_max{range_check_ptr}() -> (res : Uint256):
    let (res) = uint256_max()
    return (res)
end

@view
func test_uint256_mul_checked{range_check_ptr}(a : Uint256, b : Uint256) -> (product : Uint256):
    let (product) = uint256_mul_checked(a, b)
    return (product)
end

@view
func test_uint256_unsigned_div_rem_up{range_check_ptr}(a : Uint256, b : Uint256) -> (res : Uint256):
    let (res) = uint256_unsigned_div_rem_up(a, b)
    return (res)
end
