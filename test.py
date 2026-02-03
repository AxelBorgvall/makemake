import numpy as np
import time
import timeit
import numpy as np

n = 1
# NumPy
setup_np = "import numpy as np; n=100; a=np.random.rand(n); b=np.random.rand(n)"
print("numpy",timeit.timeit("a + b", setup=setup_np, number=10000))

# List
setup_ls = "import numpy as np; n=100; a=np.random.rand(n).tolist(); b=np.random.rand(n).tolist()"
print("list",timeit.timeit("[a[i]+b[i] for i in range(n)]", setup=setup_ls, number=10000))