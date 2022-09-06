from typing import Tuple

from starkware.starknet.public.abi import get_selector_from_name


def str_to_felt(text: str) -> int:
    b_text = bytes(text, "ascii")
    return int.from_bytes(b_text, "big")


def felt_to_str(felt: int) -> str:
    b_felt = felt.to_bytes(31, "big")
    return b_felt.decode()


def to_uint(a) -> Tuple[int, int]:
    """Takes in value, returns uint256-ish tuple."""
    return (a & ((1 << 128) - 1), a >> 128)


def from_uint(uint: Tuple[int, int]) -> int:
    """Takes in uint256-ish tuple, returns value."""
    return uint[0] + (uint[1] << 128)


def assert_event_emitted(tx_exec_info, event_name):
    key = get_selector_from_name(event_name)
    for event in tx_exec_info.raw_events:
        if key in event.keys:
            return

    assert False
