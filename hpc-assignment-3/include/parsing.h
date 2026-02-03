#ifndef PARSING_H

#define PARSING_H

#include "point.h"

#include <stdio.h>

// Function to parse a block of lines from the file into an array of Points

// Returns the actual number of points parsed (may be less than max_size)

// Assumes fixed format: "+01.330 -09.035 +03.489\n"
int parse_block(FILE *file, uint64_t starting_offset, Point *block, int max_size,
                uint64_t *end_offset);

#endif // PARSING_H
