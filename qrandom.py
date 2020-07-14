"""
Based on quantumrandom 1.9.0
https://pypi.org/project/quantumrandom/
"""

import math
import requests
try:
    import json
except ImportError:
    import simplejson as json

DATA_TYPES = ['uint16', 'hex16']
MAX_LEN = 1024
INT_BITS = 16

class Qrandom():
    def __init__(self):
        self.cached_generator = self.qrand_generator()
    
    def get_data(self, data_type='uint16', array_length=1, block_size=1):
        """Fetch data from the ANU Quantum Random Numbers JSON API."""
        print('Requesting data from qrng.anu.edu.au')
        if data_type not in DATA_TYPES:
            raise ValueError('data_type must be one of {}'.format(DATA_TYPES))
        if array_length > MAX_LEN:
            raise ValueError('array_length cannot be larger than {}'.format(MAX_LEN))
        if block_size > MAX_LEN:
            raise ValueError('block_size cannot be larger than {}'.format(MAX_LEN))
        url = 'https://qrng.anu.edu.au/API/jsonI.php?length={}&type={}&size={}'.format(
            array_length, data_type, block_size)
        data = json.loads(requests.get(url).content.decode())
        assert data['success'] is True, data
        assert data['length'] == array_length, data
        return data['data']

    def qrand_generator(self, data_type='uint16', cache_size=MAX_LEN):
        """Generator for numbers. Caches numbers to avoid latency."""
        while 1:
            for n in self.get_data(data_type, cache_size, cache_size):
                yield n
    
    def qrng_next(self):
        """Return cached numbers."""
        res = next(self.cached_generator, None)
        if res == None: # Old generator is empty, create a new one
            self.cached_generator = self.qrand_generator()
            return next(self.cached_generator)
        else:
            return res
    
    def randint(self, min: int, max: int):
        """Return an int between min and max. If given, takes from generator instead.
        This can be useful to reuse the same qrand_generator() instance over multiple calls."""
        rand_range = max - min
        if rand_range < 0:
            raise ValueError('max is less than min.')
        if rand_range == 0:
            return min
        
        source_bits = int(math.ceil(math.log(rand_range + 1, 2)))
        source_size = int(math.ceil(source_bits / float(INT_BITS)))
        source_max = 2 ** (source_size * INT_BITS) - 1
        
        modulos = source_max / rand_range
        too_big = modulos * rand_range
        while True:
            num = 0
            for x in range(source_size):
                num <<= INT_BITS
                num += self.qrng_next()
            if num >= too_big:
                continue
            else:
                return int(math.floor(num / modulos) + min)

# Test random generation to see if there might be a bias
if __name__ == '__main__':
    qrandom_inst = Qrandom()
    TEST_MAX = 65536
    EXPECTED_AVG = (TEST_MAX - 1)/2
    
    print('Testing random 16-bit integer generation...\n')
    for _ in range(3):
        avg = 0
        for i in range(5000):
            new_element_weight = 1/(i+1)
            avg_current_weight = 1 - new_element_weight
            avg = avg_current_weight*avg + new_element_weight*qrandom_inst.randint(0, TEST_MAX)
        
        print(f'Average result: {avg}')
        print(f'Deviation from expected average: {(avg - EXPECTED_AVG)/EXPECTED_AVG:.2%}\n')
        
    input('Tests complete. Press [Enter] to exit.\n')
