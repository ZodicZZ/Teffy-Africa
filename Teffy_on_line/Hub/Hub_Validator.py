
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from pycardano import *
from blockfrost import BlockFrostApi, ApiUrls
from pycardano import crypto
load_dotenv()
network = os.getenv("network")
wallet_mnemonic = os.getenv("wallet_mnemonic")
blockfrost_api_key = os.getenv("blockfrost_api_key")
if network == "testnet":
    base_url = ApiUrls.preprod.value
    cardano_network = Network.TESTNET
else:
    base_url = ApiUrls.mainnet.value
    cardano_network = Network.MAINNET
def derive_wallet_address():
    new_wallet = crypto.bip32.HDWallet.from_mnemonic(wallet_mnemonic)
    payment_key = new_wallet.derive_from_path(f"m/1852'/1815'/0'/0/0")
    staking_key = new_wallet.derive_from_path(f"m/1852'/1815'/0'/2/0")
    payment_skey = ExtendedSigningKey.from_hdwallet(payment_key)
    staking_skey = ExtendedSigningKey.from_hdwallet(staking_key)
    main_address = Address(
        payment_part=payment_skey.to_verification_key().hash(),
        staking_part=staking_skey.to_verification_key().hash(),
        network=cardano_network,
    )
    return main_address, payment_skey
def submit_crop_validation_transaction(project: str, purpose: str, timestamp: str, extra_data: dict = {}):
    main_address, payment_skey = derive_wallet_address()
    print(f"Using address: {main_address}\n")

    api = BlockFrostApi(project_id=blockfrost_api_key, base_url=base_url)
    try:
        utxos = api.address_utxos(main_address)
    except Exception as e:
        if hasattr(e, "status_code") and e.status_code == 404:
            print("No UTXOs. Fund the wallet first.")
        else:
            print(f"API Error: {str(e)}")
        sys.exit(1)
    cardano = BlockFrostChainContext(project_id=blockfrost_api_key, base_url=base_url)
    builder = TransactionBuilder(cardano)
    for _ in range(20):
        output = TransactionOutput(main_address, Value(4000000))
        builder.add_output(output)
    builder.add_input_address(main_address)
    metadata = Metadata()
    metadata_content = {
        "project": project,
        "purpose": purpose,
        "timestamp": timestamp,
        "network": network
    }
    metadata_content.update(extra_data)
    metadata[674] = metadata_content

    aux_data = AuxiliaryData(metadata)
    builder.auxiliary_data = aux_data

    signed_tx = builder.build_and_sign([payment_skey], change_address=main_address)
    result = cardano.submit_tx(signed_tx.to_cbor())

    print(f"Submitted Tx:\n\tInputs: {len(signed_tx.transaction_body.inputs)}\n\tOutputs: {len(signed_tx.transaction_body.outputs)}")
    print(f"\tFee: {signed_tx.transaction_body.fee/1000000} ADA\n\tTx ID: {result}")
    return result
