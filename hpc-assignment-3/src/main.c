#include <inttypes.h>
#include <omp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "../include/computation.h"
#include "../include/parsing.h"
#include "../include/point.h"

#define LINE_LEN 24
#define DEFAULT_BLOCKSIZE 10000

int main(int argc, char *argv[]) {

  int threads = 1;
  int blocksize = DEFAULT_BLOCKSIZE;
  char *fpath = "./cells";

  // Parse command-line arguments
  for (int i = 1; i < argc; i++) {
    if (strcmp(argv[i], "-t") == 0 && i + 1 < argc) {
      threads = atoi(argv[i + 1]);
      i++;

    } else if (strncmp(argv[i], "-t", 2) == 0) {
      threads = atoi(argv[i] + 2);

    } else if (strcmp(argv[i], "-n") == 0 && i + 1 < argc) {
      blocksize = atoi(argv[i + 1]);
      i++;

    } else if (strncmp(argv[i], "-n", 2) == 0) {
      blocksize = atoi(argv[i] + 2);

    } else if (strcmp(argv[i], "-f") == 0 && i + 1 < argc) {
      fpath = argv[i + 1];

      i++;

    } else {
      fprintf(stderr, "Unknown argument: %s\n", argv[i]);
      return 1;
    }
  }

  // Set OpenMP threads
  omp_set_num_threads(threads);

  printf("number of threads = %d\nblocksize = %d\nfilepath=%s", threads,
         blocksize, fpath);

  // Open the input file
  FILE *file = fopen(fpath, "r");
  if (!file) {
    fprintf(stderr, "Error: Could not open file '%s'\n", fpath);
    return 1;
  }

  // Count total number of points by reading lines
  uint64_t total_points = 0;
  char line[LINE_LEN + 1];
  while (fgets(line, sizeof(line), file) != NULL) {
    if (strlen(line) < LINE_LEN) {
      continue;
    }
    total_points++;
  }

  // Rewind to beginning for processing
  rewind(file);

  if (total_points > 4294967296ULL) {
    fprintf(stderr, "Error: Too many points (exceeds uint64_t)\n");
    fclose(file);
    return 1;
  }

  // Compute number of blocks
  int num_blocks = (total_points + blocksize - 1) / blocksize;

  // Allocate reusable blocks (two for A and B; check memory roughly)
  size_t block_mem = (size_t)blocksize * sizeof(Point);
  if (block_mem > 2 * 1024 * 1024 * 2) { // Rough check: <4 MiB for two blocks
    fprintf(stderr, "Error: Blocksize too large for memory limit\n");
    fclose(file);
    return 1;
  }

  printf("Number of lines=%" PRIu64 "\nNumber of blocks=%d\n", total_points,
         num_blocks);

  // Define blocks
  Point *block_a = malloc(block_mem);

  Point *block_b = malloc(block_mem);

  if (!block_a || !block_b) {
    fprintf(stderr, "Error: Failed to allocate blocks\n");
    free(block_a);
    free(block_b);
    fclose(file);
    return 1;
  }

  // Initialise counts array
  int64_t counts[MAX_BIN];
  memset(counts, 0, sizeof(counts));

  // Block iteration: nested loops over blocks A <= B
  uint64_t dummy_end;
  for (int ba = 0; ba < num_blocks; ba++) { // loop over block a

    int size_a = (ba + 1) * blocksize > total_points
                     ? total_points - ba * blocksize
                     : blocksize;
    uint64_t offset_a = (uint64_t)ba * blocksize * LINE_LEN;
    int parsed_a = parse_block(file, offset_a, block_a, size_a, &dummy_end);
    if (parsed_a != size_a) {
      fprintf(stderr,
              "Warning: Parsed fewer points than expected for block %d\n", ba);
    }

    for (int bb = ba; bb < num_blocks; bb++) { // loop over block b
      if (ba == bb) {
        // A == B: just compare block_a with itself
        compute_block_pairs(block_a, size_a, block_a, size_a, counts);
        continue;
      }
      printf("\rA:%d, B:%d", ba, bb);
      int size_b = (bb + 1) * blocksize > total_points
                       ? total_points - bb * blocksize
                       : blocksize;
      uint64_t offset_b = (uint64_t)bb * blocksize * LINE_LEN;
      int parsed_b = parse_block(file, offset_b, block_b, size_b, &dummy_end);
      if (parsed_b != size_b) {
        fprintf(stderr,
                "Warning: Parsed fewer points than expected for block %d\n",
                bb);
      }

      compute_block_pairs(block_a, size_a, block_b, size_b, counts);
    }
  }
  printf("\n");
  // Output sorted non-zero frequencies
  for (int bin = 0; bin < MAX_BIN; bin++) {
    if (counts[bin] > 0) {
      int whole = bin / 100;
      int frac = bin % 100;
      printf("%02d.%02d %lld\n", whole, frac, counts[bin]);
    }
  }

  // Cleanup
  free(block_a);
  free(block_b);
  fclose(file);

  return 0;
}
