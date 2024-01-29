import math
import random
cap = 4
prob_of_noise = 0.1


def generate_noise(msg):
    wrong_flg = random.uniform(0, 1)
    if wrong_flg > prob_of_noise:
        return msg
    rate_of_wrong = random.uniform(0, 0.07)
    #rate_of_wrong = 1
    for i in range(math.floor(rate_of_wrong*len(msg))):
        pos = random.randint(0, len(msg)-1)
        replace = chr(random.randint(32, 126))
        msg = msg[:pos] + replace + msg[pos+1:]
    return msg


def generate_sum(msg):
    partition = math.ceil(len(msg)/16)
    data = [[] for m in range(partition)]
    start, count = 0, 0
    while count < partition:
        for c in msg[start:start+16]:
            if not data[count] or len(data[count][-1]) == cap:
                data[count].append([ord(c)])
            else:
                data[count][-1].append(ord(c))
        while len(data[count][-1]) != cap:
            data[count][-1].append(0)
        count += 1
        start += 16

    row_sums = [[] for m in range(partition)]
    for k in range(partition):
        for lst in data[k]:
            row_sums[k].append(sum(lst))

    col_sums = [[] for m in range(partition)]
    for k in range(partition):
        for j in range(cap):
            col_sum = 0
            for lst in data[k]:
                col_sum += lst[j]
            col_sums[k].append(col_sum)

    return data, row_sums, col_sums


def translation(data):
    s = ''
    for p in data:
        for r in p:
            for c in r:
                if c == 0:
                    break
                s += chr(c)
    return s


def correct_wrong_message(wrong_msg, row_sums, col_sums):
    data, row, col = generate_sum(wrong_msg)
    for k in range(len(data)):
        wrong_row = []
        for i in range(len(row[k])):
            if row[k][i] != row_sums[k][i]:
                wrong_row.append(i)

        wrong_col = []
        for j in range(len(col[k])):
            if col[k][j] != col_sums[k][j]:
                wrong_col.append(j)

        if len(wrong_row) > 1 and len(wrong_col) > 1:
            return None

        for i in wrong_row:
            for j in wrong_col:
                if len(wrong_row) < len(wrong_col):
                    other = 0
                    for t in range(len(data[k])):
                        if t != i:
                            other += data[k][t][j]
                    data[k][i][j] = col_sums[k][j] - other
                else:
                    other = sum(data[k][i]) - data[k][i][j]
                    data[k][i][j] = row_sums[k][i] - other

    correct_msg = translation(data)
    return correct_msg


def error_correction(msg):
    d, r, c = generate_sum(msg)
    wrong_msg = generate_noise(msg)
    if wrong_msg != msg:
        correction = correct_wrong_message(wrong_msg, r, c)
        return correction
    return wrong_msg


if __name__ == '__main__':
    msg = 'I love ics so much! What about you? Do you think so?'
    d, r, c = generate_sum(msg)
    for i in range(50):
        wrong_msg = generate_noise(msg)
        if wrong_msg != msg:
            print(wrong_msg)
            correction = correct_wrong_message(wrong_msg, r, c)
            print(correction)
