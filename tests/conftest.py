import asyncio
import os

from utils import str_to_felt, to_uint

import pytest
from starkware.starknet.services.api.contract_class import ContractClass
from starkware.starknet.compiler.compile import compile_starknet_files
from starkware.starknet.testing.starknet import Starknet, StarknetContract


ASSET_OWNER = str_to_felt("assert owner")


def here() -> str:
    return os.path.abspath(os.path.dirname(__file__))


def contract_path(contract_name: str) -> str:
    return os.path.join(here(), "..", "contracts", "erc4626", contract_name)


def compile_contract(contract_name: str) -> ContractClass:
    contract_src = contract_path(contract_name)
    return compile_starknet_files(
        [contract_src],
        debug_info=True,
        disable_hint_validation=True,
        cairo_path=[
            os.path.join(here(), "..", "contracts", "lib"),
        ],
    )


def compile_mock_contract(contract_name: str) -> ContractClass:
    contract_src = os.path.join(here(), "mocks", contract_name)
    return compile_starknet_files([contract_src], debug_info=True, cairo_path=[os.path.join(here(), "mocks")])


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.new_event_loop()


@pytest.fixture(scope="session")
async def starknet() -> Starknet:
    starknet = await Starknet.empty()
    return starknet


@pytest.fixture(scope="session")
async def asset(
    starknet,
) -> StarknetContract:
    contract = compile_mock_contract("openzeppelin/token/erc20/ERC20_Mintable.cairo")

    return await starknet.deploy(
        contract_class=contract,
        constructor_calldata=[
            str_to_felt("Winning"),  # name
            str_to_felt("WIN"),  # symbol
            18,  # decimals
            *to_uint(10**18),  # initial supply
            ASSET_OWNER,  # recipient
            ASSET_OWNER,  # owner
        ],
    )


@pytest.fixture(scope="session")
async def erc4626(starknet, asset) -> StarknetContract:
    contract = compile_contract("ERC4626.cairo")

    return await starknet.deploy(
        contract_class=contract,
        constructor_calldata=[
            str_to_felt("Vault of Winning"),
            str_to_felt("vWIN"),
            asset.contract_address,
        ],
    )


@pytest.fixture(scope="session")
async def terc4626(starknet) -> StarknetContract:
    contract = compile_contract("test_ERC4626.cairo")
    return await starknet.deploy(contract_class=contract)
