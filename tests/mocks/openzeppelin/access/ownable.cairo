// SPDX-License-Identifier: MIT
// OpenZeppelin Cairo Contracts v0.1.0 (access/ownable.cairo)

%lang starknet

from starkware.cairo.common.cairo_builtins import HashBuiltin
from starkware.starknet.common.syscalls import get_caller_address

@storage_var
func Ownable_owner() -> (owner: felt) {
}

func Ownable_initializer{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    owner: felt
) {
    Ownable_owner.write(owner);
    return ();
}

func Ownable_only_owner{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() {
    let (owner) = Ownable_owner.read();
    let (caller) = get_caller_address();
    assert owner = caller;
    return ();
}

func Ownable_get_owner{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}() -> (
    owner: felt
) {
    let (owner) = Ownable_owner.read();
    return (owner=owner);
}

func Ownable_transfer_ownership{syscall_ptr: felt*, pedersen_ptr: HashBuiltin*, range_check_ptr}(
    new_owner: felt
) -> (new_owner: felt) {
    Ownable_only_owner();
    Ownable_owner.write(new_owner);
    return (new_owner=new_owner);
}
