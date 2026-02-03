#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

int main(int argc, char *argv[]) {

  if (argc != 5 || strcmp(argv[1], "-n") != 0 || strcmp(argv[3], "-o") != 0) {
    fprintf(stderr, "Usage: %s -n <num_points> -o <output_file>\n", argv[0]);
    fprintf(stderr, "Example: %s -n 100 -o data/cells.txt\n", argv[0]);
    return 1;
  }

  int num_points;
  char *endptr;
  num_points = strtol(argv[2], &endptr, 10);

  if (*endptr != '\0' || num_points <= 0 || num_points > (1LL << 32) - 1) {
    fprintf(stderr, "Invalid number of points: %s\n", argv[2]);
    return 1;
  }

  char *output_file = argv[4];
  FILE *file = fopen(output_file, "w");

  if (!file) {
    fprintf(stderr, "Failed to open output file: %s\n", output_file);
    return 1;
  }

  srand(time(NULL)); // Seed random number generator

  for (int i = 0; i < num_points; ++i) {

    double x =
        (rand() / (double)RAND_MAX) * 20.0 - 10.0; // Uniform in[ -10, 10 ]

    double y = (rand() / (double)RAND_MAX) * 20.0 - 10.0;

    double z = (rand() / (double)RAND_MAX) * 20.0 - 10.0;

    // Format each coordinate: sign + two digits . three digits

    char x_str[8], y_str[8], z_str[8];

    char sign_x = (x >= 0) ? '+' : '-';

    double abs_x = fabs(x);

    sprintf(x_str + 1, "%06.3f", abs_x); // +1 to skip sign position

    x_str[0] = sign_x;

    char sign_y = (y >= 0) ? '+' : '-';

    double abs_y = fabs(y);

    sprintf(y_str + 1, "%06.3f", abs_y);

    y_str[0] = sign_y;

    char sign_z = (z >= 0) ? '+' : '-';

    double abs_z = fabs(z);

    sprintf(z_str + 1, "%06.3f", abs_z);

    z_str[0] = sign_z;

    // Write the line

    fprintf(file, "%s %s %s\n", x_str, y_str, z_str);
  }

  fclose(file);

  printf("Generated %d points in %s\n", num_points, output_file);

  return 0;
}
