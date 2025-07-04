from eth_abi import encode_abi

# # 构造参数类型列表，要跟 ABI 中 constructor.inputs 对应
# types = ["string", "string", "uint8", "uint256"]
# values = ["MyToken", "MTK", 18, 1000000000000000000000]
#
# data: bytes = encode_abi(types, values)
# hex_str = data.hex()
# print(hex_str)

owners = [
    "0x1111111111111111111111111111111111111111",
    "0x2222222222222222222222222222222222222222"
]
required = 2

types = ["address[]", "uint256"]
values = [owners, required]

data = encode_abi(types, values)
hex_str = data.hex()
print(hex_str)
