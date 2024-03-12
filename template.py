def split_into_blocks(number, num_blocks):
    block_size = 32
    mask = (1 << block_size) - 1  # Create a mask with 32 bits set to 1

    blocks = []
    for i in range(0, 32*blocks, block_size):
        block = (number & mask)
        blocks.append(block)
        number >>= block_size

    return
