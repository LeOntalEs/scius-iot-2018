import json
from collections import OrderedDict

# all_colors = [18, 62, 97, 110, 150, 170]
# all_colors = [[0, 30, 105, 163]]
# # all_colors = [1,2,]
all_colors = [0, 3698, 4232, 6050, 11250, 25312]


def f(c, all_prob, unique, d, md):
    if not c:
        c = []
    if d == md:
        all_prob.append(c)
        v = "({})".format(', '.join(str(x) for x in sorted(c)))
        if not v in unique:
            unique.append(v)
    else:
        for x in all_colors:
            _c = c + [x]
            f(_c, all_prob, unique, d+1, md)

if __name__ == '__main__':
    k = dict()
    unique = list()
    all_prob = list()
    f([], all_prob, unique, 0, 4)
    idxs = {c: i for i, c in enumerate(unique)}
    print(len(idxs))
    for c in all_prob:
        sorted_c = sorted(c)
        kc1 = "({})".format(', '.join(str(x) for x in c))
        kc2 = "({})".format(', '.join(str(x) for x in sorted_c))
        k[kc1] = idxs[kc2]
    k = OrderedDict(sorted(k.items(), key=lambda x: x[1]))

    with open('cindex.json', 'w+') as fp:
        json.dump(k, fp, indent=2)
