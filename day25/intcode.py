def get_instructions(opcode):
    opc_list = [opcode % 100]
    opcode = opcode // 100

    while len(opc_list) < 4:
        opc_list.append(opcode % 10)
        opcode = opcode // 10

    if opc_list[0] not in list(range(1, 10)) + [99] \
            or not all(opc_list[i] in range(3) for i in (1, 2)) \
            or opc_list[3] not in (0, 2):
        raise Exception('Wrong opcode or mode.')

    return opc_list


def get_value(list_, i, default=0):
    try:
        el = list_[i]
    except IndexError:
        el = default
    finally:
        return el


def extend_list(list_, i):
    try:
        el = list_[i]
    except IndexError:
        list_ = list_ + [0] * (i - len(list_) + 1)
    finally:
        return list_


def process_instructions(data, inputs, relative_base=0):
    def get_index(idx, mode):
        if mode == 1:
            raise Exception('Wrong mode.')
        return data[idx] if mode == 0 else data[idx] + relative_base

    def get_param(idx, mode):
        if mode == 1:
            return data[idx]
        new_idx = get_index(idx, mode)
        return get_value(data, new_idx)

    i = 0
    output = []

    while i < len(data):
        opcode = get_instructions(data[i])

        if opcode[0] in (1, 2, 5, 6, 7, 8):
            param1 = get_param(i + 1, opcode[1])
            param2 = get_param(i + 2, opcode[2])
            if opcode[0] in (1, 2, 7, 8):
                index3 = get_index(i + 3, opcode[3])
        if opcode[0] in (4, 9):
            param1 = get_param(i + 1, opcode[1])

        if opcode[0] in (1, 2):
            data = extend_list(data, index3)
            data[index3] = param1 + param2 if opcode[0] == 1 else param1 * param2
            i += 4
        elif opcode[0] == 3:
            if not len(inputs):
                new_input = yield output
                output = []
                if new_input is not None:
                    inputs += new_input
            index1 = get_index(i + 1, opcode[1])
            data = extend_list(data, index1)
            data[index1] = inputs.pop(0)
            i += 2

        elif opcode[0] == 4:
            output.append(param1)
            i += 2
        elif opcode[0] == 5:
            i = i + 3 if param1 == 0 else param2
        elif opcode[0] == 6:
            i = param2 if param1 == 0 else i + 3
        elif opcode[0] == 7:
            data = extend_list(data, index3)
            data[index3] = 1 if param1 < param2 else 0
            i += 4
        elif opcode[0] == 8:
            data = extend_list(data, index3)
            data[index3] = 1 if param1 == param2 else 0
            i += 4
        elif opcode[0] == 9:
            relative_base += param1
            i += 2
        elif opcode[0] == 99:
            yield output, None
        else:
            raise Exception('Wrong opcode.')
