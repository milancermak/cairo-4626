import asyncio
import os

import pytest
from starkware.starknet.services.api.contract_definition import ContractDefinition
from starkware.starknet.compiler.compile import compile_starknet_files
from starkware.starknet.testing.starknet import Starknet, StarknetContract


def here() -> str:
    return os.path.abspath(os.path.dirname(__file__))


def contract_path(contract_name: str) -> str:
    return os.path.join(here(), "..", "contracts", "erc4626", contract_name)


def compile_contract(contract_name: str) -> ContractDefinition:
    contract_src = contract_path(contract_name)
    contracts_dir = os.path.join(here(), "..", "contracts")
    return compile_starknet_files(
        [contract_src],
        debug_info=True,
        disable_hint_validation=True,
        cairo_path=[
            os.path.join(contracts_dir, "erc4626"),
            os.path.join(contracts_dir, "lib")
        ]
    )


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.new_event_loop()


@pytest.fixture(scope="session")
async def starknet() -> Starknet:
    starknet = await Starknet.empty()
    return starknet


@pytest.fixture(scope="session")
async def account_factory(starknet):
    account_path = os.path.join(here(), "mocks", "account", "Account.cairo")
    cairo_path = os.path.join(here(), "mocks", "account")
    account_contract = compile_starknet_files([account_path], debug_info=True, cairo_path=[cairo_path])

    async def account_for_signer(signer):
        return await starknet.deploy(contract_def=account_contract, constructor_calldata=[signer.public_key])

    yield account_for_signer


@pytest.fixture(scope="module")
async def erc4626(starknet):
    # contract = compile_starknet_files(["../contracts/erc4626/ERC4626.cairo"], debug_info=True, cairo_path=["../contracts/lib"])
    contract = compile_contract("ERC4626.cairo")
    return await starknet.deploy(contract_def=contract, constructor_calldata=["TODO"])


@pytest.fixture(scope="module")
async def terc4626(starknet):
    contract = compile_contract("test_ERC4626.cairo")
    # contract = compile_starknet_files(["../contracts/erc4626/test_ERC4626.cairo"], debug_info=True, cairo_path=["../contracts/lib"])
    return await starknet.deploy(contract_def=contract)



# @pytest.fixture
# async def token(starknet):
