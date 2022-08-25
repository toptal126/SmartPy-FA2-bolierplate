import smartpy as sp
FA2 = sp.io.import_script_from_url("https://smartpy.io/templates/fa2_lib.py")


class PublicMintNft:
    """(Mixin) Non-standard `mint` entrypoint for FA2Nft with incrementing id.

    Requires the `Admin` mixin.
    """

    @sp.entry_point
    def mint(self, batch):
        """Admin can mint new or existing tokens."""
        sp.set_type(
            batch,
            sp.TList(
                sp.TRecord(
                    to_=sp.TAddress,
                    metadata=sp.TMap(sp.TString, sp.TBytes),
                ).layout(("to_", "metadata"))
            ),
        )
        # sp.verify(self.is_administr/ator(sp.sender), "FA2_NOT_ADMIN")
        with sp.for_("action", batch) as action:
            token_id = sp.compute(self.data.last_token_id)
            metadata = sp.record(token_id=token_id, token_info=action.metadata)
            self.data.token_metadata[token_id] = metadata
            self.data.ledger[token_id] = action.to_
            self.data.last_token_id += 1


class NftWithAdmin(FA2.Admin, FA2.WithdrawMutez, PublicMintNft, FA2.Fa2Nft):
    def __init__(self, admin, **kwargs):
        FA2.Fa2Nft.__init__(self, **kwargs)
        FA2.Admin.__init__(self, admin)


tok0_md = sp.map(l={
    "": sp.utils.bytes_of_string(
        "ipfs://QmTq1FXht8jFc9CaW2j2hJ3bMjLqgAJhr3bxjcJ723TaHT"
    ),
})
tok1_md = FA2.make_metadata(name="Token One", decimals=1, symbol="Tok1")
tok2_md = FA2.make_metadata(name="Token Two", decimals=1, symbol="Tok2")
TOKEN_METADATA = [tok0_md, tok1_md, tok2_md]
METADATA = sp.utils.metadata_of_url(
    "ipfs://bafkreiels7nywfxi6tcmj7j6cbmtqh7uoeneun6hqc4i5ngd3w74p2thn4")


alice = sp.test_account("Alice")


@ sp.add_test(name="NFT with admin and mint")
def test():
    sc = sp.test_scenario()

    c1 = NftWithAdmin(
        admin=sp.test_account("admin").address,
        metadata=METADATA,
        token_metadata=TOKEN_METADATA
    )

    sc += c1


# A a compilation target (produces compiled code)
sp.add_compilation_target("NftWithAdmin_Compiled", NftWithAdmin(
    admin=sp.test_account("admin").address,
    metadata=sp.utils.metadata_of_url(
        "ipfs://bafkreigb6nsuvwc7vzx6oqzoaeaxno6liyr5rigbheg2ol7ndac75kawoe"
    ),
    ledger={0: alice.address, 1: alice.address, 2: alice.address},
    token_metadata=TOKEN_METADATA,
))
