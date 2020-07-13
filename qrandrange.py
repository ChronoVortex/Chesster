import qrng

def qrandrange(min: int, max: int):
    if '_backend' not in vars(qrng):
        qrng.set_backend()
    return qrng.get_random_int(min, max - 1)
