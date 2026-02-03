
#ifndef POINT_H

#define POINT_H

#include <stdint.h>

// Fixed-point scaling for coordinates: multiply by SCALE to store as integer
#define SCALE 1000

// Maximum distance ~sqrt(3*20^2) ≈ 34.64, binned to 0.01 precision
#define MAX_BIN 3465 // 0.00 to 34.64 * 100

// Struct for a 3D point with fixed-point integer coordinates
typedef struct {
  int16_t x, y, z; // Scaled values: e.g., +01.330 -> +1330
} Point;

#endif // POINT_H
