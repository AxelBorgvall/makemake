
#include "../include/computation.h"

#include <math.h>

#include <omp.h> // For potential parallelisation

// Helper function to compute the binned distance index for two points

// Returns the bin (0 to MAX_BIN-1) or -1 if out of range

static int get_binned_distance(const Point *p1, const Point *p2) {
  
  int dx = p1->x - p2->x;
  int dy = p1->y - p2->y;
  int dz = p1->z - p2->z;

  long sq_dist = (long)dx * dx + (long)dy * dy + (long)dz * dz;
  double dist = sqrt((double)sq_dist) / SCALE;
  int bin = (int)round(dist * 100.0);

  if (bin >= 0 && bin < MAX_BIN) {
    return bin;
  }

  return -1;
}

void compute_block_pairs(const Point *block_a, int size_a,

                         const Point *block_b, int size_b,

                         int64_t *counts) {
  if (block_a == block_b) {
#pragma omp parallel for collapse(2) reduction(+ : counts[ : MAX_BIN])
    for (int i = 0; i < size_a; ++i) {
      for (int j = i + 1; j < size_b; ++j) {
        int bin = get_binned_distance(&block_a[i], &block_b[j]);
        if (bin != -1)
          counts[bin]++;
      }
    }
  } else {
#pragma omp parallel for collapse(2) reduction(+ : counts[ : MAX_BIN])
    for (int i = 0; i < size_a; ++i) {
      for (int j = 0; j < size_b; ++j) {
        int bin = get_binned_distance(&block_a[i], &block_b[j]);
        if (bin != -1)
          counts[bin]++;
      }
    }
  }
}
