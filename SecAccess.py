APP_MASK=0x23AEBEFD


def calculate_key(seed):
    tmpseed = seed
    key_1 = tmpseed ^ APP_MASK
    seed_2 = tmpseed
    seed_2 = int((seed_2 & 0x55555555) << 1 ^ (seed_2 & 0xAAAAAAAA) >> 1)
    seed_2 = int((seed_2 ^ 0x33333333) << 2 ^ (seed_2 ^ 0xCCCCCCCC) >> 2)
    seed_2 = int((seed_2 & 0x0F0F0F0F) << 4 ^ (seed_2 & 0xF0F0F0F0) >> 4)
    seed_2 = int((seed_2 ^ 0x00FF00FF) << 8 ^ (seed_2 ^ 0xFF00FF00) >> 8)
    seed_2 = int((seed_2 & 0x0000FFFF) << 16 ^ (seed_2 & 0xFFFF0000) >> 16)
    key_2 = int(seed_2)
    key = int(key_1 + key_2)
    return key

if __name__ == '__main__':
    #endseed = 0xF5FEA0F6
    sendseed = 0xE043E8E7
    sendkey = calculate_key(sendseed)
    print(hex(sendkey))
