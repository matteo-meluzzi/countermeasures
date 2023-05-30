import random
from timeit import timeit
import numpy as np
from dataclasses import dataclass
from texttable import Texttable
from latextable import draw_latex

# https://stackoverflow.com/questions/10321978/integer-to-bitfield-as-a-list
def bitfield(n):
    return [1 if digit=='1' else 0 for digit in bin(n)[2:][::-1]]

def square_and_multiply(base, exponent, modulus):
    exponent = bitfield(exponent)
    k = len(exponent)
    a = 1
    for i in range(k-1, -1, -1):
        a = np.power(a, 2) % modulus
        if exponent[i] == 1:
            a = (a * base) % modulus
    return a


def square_and_multiply_always(base, exponent, modulus):
    exponent = bitfield(exponent)
    k = len(exponent)
    r = [1, base]
    i = k - 1
    t = 0
    while i >= 0:
        r[0] = (r[0] * r[t]) % modulus
        t = np.bitwise_xor(t, exponent[i])
        i = i - 1 + t
    return r[0]

def montgomey_ladder(base, exponent, modulus):
    exponent = bitfield(exponent)
    k = len(exponent)
    r = [1, base]
    for i in range(k-1, -1, -1):
        r[1-exponent[i]] = (r[0] * r[1]) % modulus
        r[exponent[i]] = np.power(r[exponent[i]], 2) % modulus
    return r[0]

def double_check(base, exponent, modulus):
    return np.power(base, exponent) % modulus

def check_correctness():
    for base in range(1, 100):
        for exponent in range(1, 10):
            for modulus in range(base + 1, 100):
                truth = double_check(base, exponent, modulus)
                
                sm = square_and_multiply(base, exponent, modulus)
                sma = square_and_multiply_always(base, exponent, modulus)
                ml = montgomey_ladder(base, exponent, modulus)

                if sm != truth or sma != truth or ml != truth:
                    print("WRONG RESULT FOUND:")
                    print("base", base, "exponent", exponent, "modulus", modulus)
                    print("true", truth, "sm", sm, "sma", sma, "ml", ml)
                    exit(-1)

# check_correctness()

# def print_random_list(name, n):
#     xs = [random.randint(1, 2**30) for i in range(n)]
#     print(name, "=", xs)
 
# print_random_list("bases", 10)
# print_random_list("exponents", 10)
# print_random_list("modula", 10)

bases = [874088031, 654219561, 581145891, 515538649, 123672988, 193775270, 636222177, 519429476, 954528579, 97585336]
exponents = [712044996, 89651962, 504043517, 617162220, 37484123, 307598947, 1013848518, 903876060, 852813366, 393665172]
modula = [1069812326, 945732073, 981409780, 667481943, 820131954, 674312893, 893303139, 822744699, 468183196, 275005389]

@dataclass
class TimingResult:
    eq: str
    sm: float
    ml: float
    sma: float

results = []

count = 0
for base in bases:
    for exponent in exponents:
        for modulus in modula:
            if modulus < base:
                continue
            count += 1

            reps = 10

            sm = timeit(lambda: square_and_multiply(base, exponent, modulus), number=reps)
            sma = timeit(lambda: square_and_multiply_always(base, exponent, modulus), number=reps)
            ml = timeit(lambda: montgomey_ladder(base, exponent, modulus), number=reps)

            result = TimingResult(f"\({base}^{{{exponent}}} \mod {modulus}\)", 1.0, ml/sm, sma/sm)
            results.append(result)
            if count == 20:
                break
        if count == 20:
            break
    if count == 20:
        break

# Create LaTeX table
table = Texttable()
table.set_cols_align(["l", "r", "r", "r"])
table.set_cols_valign(["m", "m", "m", "m"])

# Define table headers
headers = ['Exponentiation', 'Square and Multiply', 'Montgomery Ladder', 'Square and Multiply Always']
table.header(headers)

# Add rows to the table
for result in results:
    table.add_row([result.eq, result.sm, result.ml, result.sma])

# Generate the LaTeX code for the table
print(draw_latex(table, caption="A comparison of rocket features."))

mls = [x.ml for x in results]
ml_avg = np.mean(mls)

smas = [x.sma for x in results]
sma_avg = np. mean(smas)

print("montgomery ladder average:", ml_avg)
print("square and multiply average:", sma_avg)

ml_std = np.std(mls)
sma_std = np.std(smas)
print("montgomery ladder std:", ml_std)
print("square and multiply std:", sma_std)
