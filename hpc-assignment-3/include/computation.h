#ifndef COMPUTATION_H

#define COMPUTATION_H

#include "point.h"

#include <stdint.h>

// Function to compute distances for all unique pairs between two blocks of
// points

// Increments the global or provided counts array for binned frequencies

// For block_a == block_b, only computes i < j pairs to avoid double-counting

void compute_block_pairs(const Point *block_a, int size_a,

                         const Point *block_b, int size_b,

                         int64_t *counts); // Use int64_t for large frequencies

#endif // COMPUTATION_H
