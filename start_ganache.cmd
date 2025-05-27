@echo off

ganache ^
  --server.host 0.0.0.0 ^
  --server.port 8545 ^
  --miner.blockGasLimit 15000000 ^
  --miner.defaultGasPrice 0x0 ^
  --chain.vmErrorsOnRPCResponse true ^
  --wallet.accounts="0x742d349d768c5a73c9368c9b2d04e88f0d511696d98f1d3cb1c7cecd80d391f5,1000000000000000000000" ^
  --wallet.accounts="0x18ffb39958a9c3d9d885518a78393162ae9508688ca382015d07ed10ad8c2315,1000000000000000000000" ^
  --wallet.accounts="0x149a5a963103ac553c26368edafc55e6a3bc7634ef1ddd2bd869fc7f5c98133b,1000000000000000000000"

pause
