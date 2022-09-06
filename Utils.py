import smartpy as sp

class Math:
    @staticmethod
    def pow(base, exponent):
        """
            Calculate the power (base ** exponent) by use exponentiation by squaring
        """
        return sp.michelson(
            """
            DUP;
            PUSH nat 0;
            COMPARE;
            NEQ;
            LOOP
            {
                PUSH nat 0;
                PUSH nat 2;
                DUP 3;
                EDIV;
                IF_NONE
                {
                    UNIT;
                    FAILWITH;
                }
                {
                    CDR;
                };
                COMPARE;
                NEQ;
                IF
                {
                    SWAP;
                    DUP;
                    DUG 2;
                    DIG 3;
                    MUL;
                    DUG 2;
                }
                {};
                PUSH nat 1;
                SWAP;
                LSR;
                SWAP;
                DUP;
                MUL;
                SWAP;
                DUP;
                PUSH nat 0;
                COMPARE;
                NEQ;
            };
            DROP 2;
            """,
            [sp.TNat, sp.TNat, sp.TNat],
            [sp.TNat]
        )(exponent, base, 1)

        """
            The inlined michelson above is an optimized version of the code below.
        """
        """
        result = sp.local(generate_var('result'), 1)
        base = sp.local(generate_var('base'), base)
        exponent = sp.local(generate_var('exponent'), exponent)

        with sp.while_(exponent.value != 0):
            with sp.if_((exponent.value % 2) != 0):
                result.value *= base.value

            exponent.value = exponent.value >> 1 # Equivalent to exponent.value / 2
            base.value *= base.value

        return result.value
        """

    @staticmethod
    def median(submissions):
        """
            Returns the sorted middle, or the average of the two middle
            indexed items if the array has an even number of elements.
        """
        hist = sp.local(generate_var('hist'), {})
        with sp.for_(generate_var("x"), submissions) as x:
            with sp.if_(hist.value.contains(x)):
                hist.value[x] += 1
            with sp.else_():
                hist.value[x] = 1

        submissions_size = sp.compute(sp.len(submissions))
        result = sp.local(generate_var('result'), sp.nat(0))
        half = sp.local(generate_var('half'), submissions_size / 2)
        use_average = sp.local(generate_var('use_average'), half.value * 2 == submissions_size)
        i = sp.local(generate_var('i'), 0)
        with sp.for_(generate_var("x"), hist.value.items()) as x:
            with sp.if_(use_average.value):
                with sp.if_(i.value < half.value):
                    result.value = x.key
                    i.value += x.value
                    with sp.if_(i.value > half.value):
                        use_average.value = False
                with sp.else_():
                    result.value += x.key
                    result.value /= 2
                    use_average.value = False
                    i.value += x.value
            with sp.else_():
                with sp.if_(i.value <= half.value):
                    result.value = x.key
                    i.value += x.value

        return result.value

class Bytes:
    @staticmethod
    def of_string(text):
        b = sp.pack(text)
        # Remove (packed prefix), (Data identifier) and (string length)
        # - Packed prefix: 0x05 (1 byte)
        # - Data identifier: (string = 0x01) (1 byte)
        # - String length (4 bytes)
        return sp.slice(b, 6, sp.as_nat(sp.len(b) - 6)).open_some("Could not encode string to bytes.")

    @staticmethod
    def of_nat(number):
        sp.verify(number < 64, "(number) must be lower than 64")
        b = sp.pack(number)
        # Remove (packed prefix), (Data identifier)
        # - Packed prefix: 0x05 (1 byte)
        # - Data identifier: (int = 0x00) (1 byte)
        return sp.slice(b, 2, sp.as_nat(sp.len(b) - 2)).open_some("Could not encode nat to bytes.")

class String:
    @staticmethod
    def ends_with(text, postfix):
        """Check if a string ends with a given postfix"""
        return sp.michelson(
            """
            DUP;
            SIZE;
            DUP 3;
            SIZE;
            SWAP;
            PAIR;
            DUP;
            UNPAIR;
            COMPARE;
            GE;
            IF
            {
                UNPAIR;
                DUP 2;
                SWAP;
                SUB;
                ABS; # ABS is secure here because we already validated that (text length is greater or equal to postfix)
                SLICE;
                IF_NONE
                {
                    DROP;
                    PUSH bool False;
                }
                {
                    COMPARE;
                    EQ;
                };
            }
            {
                DROP 3;
                PUSH bool False;
            };
            """,
            [sp.TString, sp.TString],
            [sp.TBool]
        )(text, postfix)

        """
            The inlined michelson above is an optimized version of the code below.
        """
        """
        text_len = sp.local(generate_var(), sp.len(text))
        postfix_len = sp.local(generate_var(), sp.len(postfix))

        res = sp.local(generate_var(), False)
        with sp.if_(text_len.value >= postfix_len.value):
            sliceRes = sp.slice(text, sp.as_nat(text_len.value - postfix_len.value), postfix_len.value)
            with sliceRes.match_cases() as arg:
                with arg.match('Some') as r:
                    res.value = postfix == r

        return res.value
        """

    @staticmethod
    def starts_with(text, prefix):
        """Check if a string starts with a given prefix"""
        return sp.michelson(
            """
            DUP;
            SIZE;
            DIG 2;
            SWAP;
            PUSH nat 0;
            SLICE;
            IF_NONE
                {
                    DROP;
                    PUSH bool False;
                }
                {
                    COMPARE;
                    EQ;
                };
            """,
            [sp.TString, sp.TString],
            [sp.TBool]
        )(prefix, text)

        """
            The inlined michelson above is an optimized version of the code below.
        """
        """
            res = sp.local(generate_var(), False)
            sliceRes = sp.slice(text, 0, sp.len(prefix))
            with sliceRes.match_cases() as arg:
                with arg.match('Some') as r:
                    res.value = prefix == r
            return res.value
        """

    @staticmethod
    def split(s, sep):
        """Split a string into tokens"""
        prev_idx = sp.local(generate_var(), 0)
        res = sp.local(generate_var(), [])
        with sp.for_(generate_var(), sp.range(0, sp.len(s))) as idx:
            with sp.if_(sp.slice(s, idx, 1).open_some() == sep):
                res.value.push(sp.slice(s, prev_idx.value, sp.as_nat(idx - prev_idx.value)).open_some())
                prev_idx.value = idx + 1
        with sp.if_(sp.len(s) > 0):
            res.value.push(sp.slice(s, prev_idx.value, sp.as_nat(sp.len(s) - prev_idx.value)).open_some())
        return res.value.rev()

    @staticmethod
    def of_int(number):
        """Convert an int into a string"""
        c = sp.map({ x : str(x) for x in range(0, 10) })
        negative = number < 0
        x   = sp.local(generate_var(), abs(number))
        arr = sp.local(generate_var(), [])

        with sp.if_(x.value == 0):
            arr.value.push('0')
        with sp.while_(0 < x.value):
            arr.value.push(c[x.value % 10])
            x.value //= 10

        result = sp.local(generate_var(), sp.concat(arr.value))
        with sp.if_(negative):
            result.value = "-" + result.value

        return result.value

    @staticmethod
    def of_bytes(b):
        # Encode the string length
        # Each utf-8 char is represented by 2 nibble (1 byte)
        lengthBytes = sp.local("lengthBytes", Bytes.of_nat(sp.len(b)))
        with sp.while_(sp.len(lengthBytes.value) < 4):
            lengthBytes.value = sp.bytes("0x00") + lengthBytes.value
        # Append (packed prefix) + (Data identifier) + (string length) + (string bytes)
        # - Packed prefix: 0x05 (1 byte)
        # - Data identifier: (string = 0x01) (1 byte)
        # - String length (4 bytes)
        # - String bytes
        packedBytes = sp.concat([sp.bytes("0x05"), sp.bytes("0x01"), lengthBytes.value, b])
        return sp.unpack(packedBytes, sp.TString).open_some("Could not decode bytes to string")


class Int:
    @staticmethod
    def of_string(s):
        """Convert a string into a int"""
        c = sp.map({str(x) : x for x in range(0, 10)})

        negative = String.starts_with(s, "-")
        text = sp.local(generate_var(), s)
        with sp.if_(negative):
            text.value = sp.slice(s, 1, sp.as_nat(sp.len(s) - 1)).open_some("")

        res = sp.local(generate_var(), 0)
        with sp.for_(generate_var(), sp.range(0, sp.len(text.value))) as idx:
            res.value = 10 * res.value + c[sp.slice(text.value, idx, 1).open_some()]

        with sp.if_(negative):
            res.value *= -1

        return res.value

class Address:
    @staticmethod
    def is_kt1(address):
        """Check if address is an originated contract"""
        return (sp.address("KT1XvNYseNDJJ6Kw27qhSEDF8ys8JhDopzfG") >= address) & (sp.address("KT18amZmM5W7qDWVt2pH6uj7sCEd3kbzLrHT") <= address)
        """
        Inlined michelson version

        return sp.michelson(
            '''
            DUP;
            PUSH address "KT1XvNYseNDJJ6Kw27qhSEDF8ys8JhDopzfG"; # Highest KT1
            COMPARE;
            GE;
            IF
                {
                    # Input address is less than or equal to the highest KT1
                    PUSH address "KT18amZmM5W7qDWVt2pH6uj7sCEd3kbzLrHT"; # Lowest KT1
                    COMPARE;
                    LE;
                }
                {
                    # Input address is not a KT1 address
                    DROP;
                    PUSH bool False;
                };
            ''',
            [sp.TAddress],
            [sp.TBool]
        )(address)
        """

"""
    ###################################################
    The methods bellow are not smart contract utilities
    ###################################################
"""

latest_var_id = 0
def generate_var(postfix = None):
    """
        Generate a variable name
    """
    global latest_var_id

    id = "utils_%s%s" % (latest_var_id, ("_" + postfix if postfix is not None else ""))
    latest_var_id += 1

    return id
