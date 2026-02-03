
#include "../include/parsing.h"
#include <stdio.h>
#include <string.h> // For potential line length checks, though format is fixed

#define LINE_LEN 24

int parse_block(FILE *file, uint64_t starting_offset, Point *block, int max_size,
                uint64_t *end_offset) {

  /*
  starting offset is from where it reads. Always resets filepointer to start.
  end offset is where the pointer is at read end.
  */

  // set position in file
  if (fseek(file, (long)starting_offset, SEEK_SET) != 0) {
    // Error seeking; could add errno check, but assume file is seekable
    *end_offset = starting_offset;
    return 0;
  }

  int count = 0;
  char line[LINE_LEN + 1];       // +1 for null terminator
  *end_offset = starting_offset; // Default if no progress

  while (count < max_size && fgets(line, sizeof(line), file) != NULL) {
    // Assume fixed format; skip if line is too short (though input is valid)
    if (strlen(line) < LINE_LEN) {
      continue;
    }

    // Parse x coordinate: positions 0-6: [sign][d][d].[d][d][d]
    int sign_x = (line[0] == '+') ? 1 : -1;
    int int_part_x = (line[1] - '0') * 10 + (line[2] - '0');
    int dec_part_x =
        (line[4] - '0') * 100 + (line[5] - '0') * 10 + (line[6] - '0');
    block[count].x = sign_x * (int_part_x * SCALE + dec_part_x);

    // Parse y coordinate: positions 8-14: space[sign][d][d].[d][d][d]
    int sign_y = (line[8] == '+') ? 1 : -1;
    int int_part_y = (line[9] - '0') * 10 + (line[10] - '0');
    int dec_part_y =
        (line[12] - '0') * 100 + (line[13] - '0') * 10 + (line[14] - '0');
    block[count].y = sign_y * (int_part_y * SCALE + dec_part_y);

    // Parse z coordinate: positions 16-22: space[sign][d][d].[d][d][d]
    int sign_z = (line[16] == '+') ? 1 : -1;
    int int_part_z = (line[17] - '0') * 10 + (line[18] - '0');
    int dec_part_z =
        (line[20] - '0') * 100 + (line[21] - '0') * 10 + (line[22] - '0');
    block[count].z = sign_z * (int_part_z * SCALE + dec_part_z);

    count++;
    *end_offset = ftell(file); // Update after successful parse
  }

  return count;
}
