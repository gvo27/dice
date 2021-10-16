import numpy as np
import regex as re
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D

class calc_fair_dice:

    def __init__(self):
        self.expr_dict = {}
    
    def add_expr(self, expr):
        self.verify_expr(expr)
        self.expr_dict[expr] = self.calc_expr(expr)
    
    def get_dist(self, name):
        if name in self.expr_dict:
            return self.expr_dict[name]
        else:
            raise Exception('error: dice name not in database')
    
    def calc_expr(self, expr):
        result = []
        splitter = re.compile('(?:(?:[0-9]+[dD][0-9]+)|(?:(?<=\W)[0-9]+(?!\w)))|(?:[-])', flags=re.I)
        split_expr = splitter.findall(expr)
        next_neg = False
        for term in split_expr:
            
            if re.search('[dD]', term, flags=re.I):
                nums = list(map(int, re.findall('[0-9]+', term)))
                r = dice_dist(nums[0], nums[1])
            elif re.search('[0-9]', term):
                r = int(term)
            elif re.search('[-]', term):
                next_neg = not next_neg
                continue
            
            if next_neg:
                next_neg = False
                result.append(negative(r))
            else:
                result.append(r)
        
        final = 0
        for i in range(len(result)):
            final = add(result[i], final)
        return final
    
    def apply_abs_val(self, name):
        self.expr_dict[name] = abs_val(self.get_dist(name))

    def verify_expr(self, expr):
        return True
    
    def graph_2d(self):
        keys = self.expr_dict.keys()
        for k in keys:
            d = self.get_dist(k)
            plt.bar(d.keys(), d.values(), alpha=0.5)

        plt.legend(keys)
        plt.xlabel('Result')
        plt.ylabel('Probability')
        plt.show()
    
    def graph_3d_with_ac(self, ac_mod=8, ac_range=range(30)):
        for name in self.expr_dict.keys():
            ac_hit_dist = get_ac_hit_dist(ac_mod, ac_range)
            dist = self.get_dist(name)

            ac = np.array(list(ac_hit_dist.keys()))
            dmg = np.array(list(dist.keys()))
            ac_mesh, dmg_mesh = np.meshgrid(ac, dmg)

            P_ac = np.array(list(ac_hit_dist.values()))
            P_dmg = np.array(list(dist.values()))

            z = np.array([[p_ac * p_dmg for p_ac in P_ac] for p_dmg in P_dmg])

            fig = plt.figure()
            ax = fig.gca(projection='3d')
            surf = ax.plot_surface(ac_mesh, dmg_mesh, z, rstride=1, cstride=1, cmap=cm.coolwarm, linewidth=0, antialiased=False)

            ax.set_xlabel('enemy AC')
            ax.set_ylabel('dmg')
            ax.set_zlabel('probability')

            plt.title(name)
            plt.show()

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


# def test_abs_d6_minus_d4():
#     e = '1d6-1d4'
#     calc = calc_fair_dice(e, 'd6 - d4')
#     calc.apply_abs_val('d6 - d4')
#     calc.graph_2d('d6 - d4')

# def test_d6_plus_d4():
#     e = '1d6+1d4'
#     calc = calc_fair_dice(e, 'd6 + d4')
#     calc.apply_abs_val('d6 + d4')