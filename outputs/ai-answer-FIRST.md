To operate an IBC relayer, you need to follow these steps:

1. **Install Hermes**

Hermes is an IBC relayer developed by Informal Systems. You can install it from binaries or build it from source. The instructions are provided in the [Hermes documentation](https://hermes.informal.systems/documentation/installation.html).

For example, to install from binaries:

```bash
export TAG="v1.7.4-namada-beta7"
export ARCH="x86_64-unknown-linux-gnu" # or "aarch64-apple-darwin"
curl -Lo /tmp/hermes.tar.gz https://github.com/heliaxdev/hermes/releases/download/${TAG}/hermes-${TAG}-${ARCH}.tar.gz
tar -xvzf /tmp/hermes.tar.gz -C /usr/local/bin
```

2. **Configure Hermes**

You need to create a `config.toml` file that describes the connections Hermes will be responsible for. An example configuration is provided in the [supplemental materials](supplemental-materials/hermes-config.toml).

3. **Set up the relayer account**

On each chain, you need to create a `relayer` account. For Namada, you can run:

```bash
namadaw gen --alias relayer
```

This will generate a key for the relayer account, stored in the `wallet.toml` file in the node's base directory.

4. **Add the relayer key to Hermes**

You need to add the relayer's key to Hermes using the `keys add` command:

```bash
hermes --config $HERMES_CONFIG keys add --chain $CHAIN_ID --key-file $WALLET_PATH
```

5. **Create IBC channel**

To create an IBC channel between the two chains, run:

```bash
hermes --config $HERMES_CONFIG \
  create channel \
  --a-chain $CHAIN_A_ID \
  --b-chain $CHAIN_B_ID \
  --a-port transfer \
  --b-port transfer \
  --new-client-connection --yes
```

This will create the necessary IBC client connection and channel.

6. **Start the relayer**

Finally, you can start the relayer:

```bash
hermes --config $HERMES_CONFIG start
```

The relayer will now monitor the chains and relay IBC packets according to the events it observes.

For more details on operating a relayer, you can refer to the [Hermes documentation](https://hermes.informal.systems/) and the [Namada docs on relaying](https://docs.namada.net/operators/ibc.html).
