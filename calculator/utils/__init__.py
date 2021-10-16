import numpy as np

def dice_dist(n, d, p=False):
    '''
    returns a dictionary containing the probability distribution for a given dice combination, assuming fair dice
    n = number of dice
    d = number of faces on the dice
    p = probability distribution of a single dice. if left blank, assumes a fair die
    '''
    
    if n < 1:
        raise Exception('invalid input n: the number of dice cannot be less than 1')
    if d < 1:
        raise Exception('invalid input d: the number of faces cannot be less than 1')
    if not p:
        p = [1/d for _ in range(d)]
    elif sum(p) != 1:
        raise Exception('invalid input p: the total probability must equal 1')

    proba_one = {}
    for i in range(1, d + 1):
        proba_one[i] = p[i - 1]

    if n == 1:
        return proba_one
    else:
        proba_n_minus_one = dice_dist(n - 1, d)
        return add(proba_n_minus_one, proba_one)

def add(o1, o2, *args):

    def rv_add_rv(A, B):
        '''
        returns a probability distribution representing the sum of random variables a and b
        \n A, B = dictionaries containing their full probability distributions
        '''
        result = {}
        for z in range(min(A) + min(B), max(A) + max(B) + 1):
            p = 0
            for a in A:
                if (z - a) in B:
                    p += A[a] * B[z - a]      
            result[z] = p
        return result

    def rv_add_c(A, c):
        '''
        adds constant c to each key in dictionary A, but does not mutate A
        '''
        keys = A.keys()
        result = {}
        for k in keys:
            result[k + c] = A[k]
        return result

    if type(o1) == dict and type(o2) == dict:
        result = rv_add_rv(o1, o2)
    elif type(o1) == dict:
        result = rv_add_c(o1, o2)
    elif type(o2) == dict:
        result = rv_add_c(o2, o1)
    else:
        raise Exception('invalid arg types: add func only takes in dict and constant')
    
    for a in args:
        result = add(result, a)
    return result

def negative(obj):
    if type(obj) == dict:
        new_dict = {-x: obj[x] for x in obj.keys()} 
        return new_dict
    else:
        return -obj

def abs_val(obj):
    if type(obj) == dict:
        result = {} 
        for i in obj:
            if abs(i) in result:
                result[abs(i)] += obj[i]
            else:
                result[abs(i)] = obj[i]
        
    elif type(obj) == int:
        result = abs(obj)
    return result

def get_ac_hit_dist(ac_mod=8, ac_range=range(30)):
    ac_dist = add(ac_mod, dice_dist(1,20))
    ac_hit_dist = {}
    for i in ac_range:
        sum_p = np.sum([ac_dist[p] for p in ac_dist.keys() if p >= i])
        sum_p = min(sum_p, 1 - ac_dist[max(ac_dist)])
        sum_p = max(sum_p, ac_dist[min(ac_dist)])
        ac_hit_dist[i] = sum_p
    return ac_hit_dist