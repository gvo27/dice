from calculator.utils import *
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




# def test_abs_d6_minus_d4():
#     e = '1d6-1d4'
#     calc = calc_fair_dice(e, 'd6 - d4')
#     calc.apply_abs_val('d6 - d4')
#     calc.graph_2d('d6 - d4')

# def test_d6_plus_d4():
#     e = '1d6+1d4'
#     calc = calc_fair_dice(e, 'd6 + d4')
#     calc.apply_abs_val('d6 + d4')