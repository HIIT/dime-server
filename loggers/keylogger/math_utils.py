import numpy as np

#For computing sparsity of a vector
def vec_sparsity(v):
    #
    nrows, ncols = v.shape
    if nrows > ncols:
        n = nrows
        sqrt_n = np.sqrt(n)
    else:
        n = ncols
        sqrt_n = np.sqrt(n)

    #L_1-norm
    l1 = np.linalg.norm(v,1)
    l1 = float(l1)

    #Euclidean norm, L_2-norm
    l2 = np.linalg.norm(v,2)

    #Sparsity
    if n > 0 and l1 > 0 :
        spar = (sqrt_n - (l1/l2))/(sqrt_n - 1)
    else:
        return 0.0

    return spar

#Compute cosine similarity between two vectors
def cossim(x1,x2):
	pass    

if __name__ == "__main__":
  v = np.random.randint(0,3,[5,1])
  s = vec_sparsity(v)
  print(v)
  print(s)
