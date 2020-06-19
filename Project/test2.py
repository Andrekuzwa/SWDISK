import itertools as iter
import more_itertools as mi
import copy

d_list = ['d1','d2','d3']
r_list = [1,2,3,4,5]
r = iter.product(r_list,d_list,repeat=1)
# print([i for i in r])
#
ps = mi.powerset(r_list)
# print([i for i in ps])
# rd = iter.product(ps,d_list)
# print([i for i in rd])
#
#

def anydup(thelist):
  seen = set()
  for x in thelist:
    if x in seen: return True
    seen.add(x)
  return False

def jebac(d_num,r_num):
    combinations = []
    deliv = [i for i in range(d_num)]
    rest = [i for i in range(r_num)]
    r_combinations = list(mi.powerset(rest))
    for i in range(len(r_combinations)-len(deliv)+1):
        temp = [r_combinations[i+j] for j in range(len(deliv))]
        temp_dict = dict(zip(deliv,temp))
        value_tuples = temp_dict.values()
        all_elements_of_values = [z for j in value_tuples for z in j]
        if sorted(all_elements_of_values) != rest:
            for key in range(len([list(temp_dict.keys())])):
                for comb in r_combinations:
                    temp_dict[list(temp_dict.keys())[-1]] = comb
                    value_tuples = temp_dict.values()
                    all_elements_of_values = [z for j in value_tuples for z in j]
                    if sorted(all_elements_of_values) == rest:
                        combinations.append(copy.deepcopy(temp_dict))
        # print(r_combinations)
    for i in combinations:
        print(i)

# combi = []
# test = iter.combinations(ps,3)
# for i in test:
#     temp = []
#     for j in i:
#         for z in j:
#             temp.append(z)
#     if sorted(temp) == r_list:
#         combi.append(i)
#
#
#
#
# # for i in combi:
# #     print(i)
#
# for i in range(4):
#     k = iter.permutations(combi[i])
#     for i in k:

#         print(i)

#
# def jebac2(d_num,r_num):
#     combinations = []
#     deliv = [i for i in range(d_num)]
#     rest = [i for i in range(r_num)]
#     r_combinations = mi.powerset(rest)
#     comb_iter = iter.combinations(r_combinations, d_num)
#     before_perm = []
#     for i in comb_iter:
#         temp = []
#         for j in i:
#             for z in j:
#                 temp.append(z)
#         if sorted(temp) == rest:
#             before_perm.append(i)
#     for i in before_perm:
#         k = iter.permutations(i)
#         for j in k:
#             combinations.append(j)
#     return combinations
#
# x = jebac2(3,4)
#
# for i in x[0]:
#     print(i)
#     print(len(i))

path = zip(*[
    (37.773097, -122.471789),
    (37.785920, -122.472693),
    (37.787815, -122.472178),
    (37.791430, -122.469763),
    (37.792547, -122.469624),
    (37.800724, -122.469460)
])
y = [2,3]

print(path)

# orders = (3,4)
#
# rc_list = []
# r_dict = {}
# for i in orders:
#     r_dict[f'r{i}'] = i
#     rc_list.append(f'r{i}')
# c_dict = {}
# for i in orders:
#     c_dict[f'c{i}'] = i
#     rc_list.append(f'c{i}')
#
# print(rc_list)
#
# for i in iter.permutations(rc_list):
#     print(i)