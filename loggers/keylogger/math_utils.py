import numpy as np

#For computing sparsity of a vector
def vec_sparsity(v):
    n = len(v)
    sqrt_n = np.sqrt(n)

    #L_1-norm
    l1 = np.linalg.norm(v,1)

    #Euclidean norm, L_2-norm
    l2 = np.linalg.norm(v,2)

    #Sparsity
    if n > 0:
        spar = (sqrt_n + l1/l2)/(sqrt_n - 1)
    else:
        return 1.0

    return spar

