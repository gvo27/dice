import warnings
from calc_fair_dice import *

warnings.filterwarnings("ignore")

if __name__ == '__main__':
    calc = calc_fair_dice()
    while True:
        ex = input("Enter a valid dice expression, or press enter to graph the distribution:\n")
        if ex:
            if calc.verify_expr(ex):
                calc.add_expr(ex)
            else:
                print("invalid dice expression!")
        else:
            calc.graph_2d()
            if len(calc.expr_dict) == 1:
                calc.graph_3d_with_ac()
            break
    
    print("terminated")