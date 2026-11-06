/*
 * host_main.c — host proof renderer for the LINE HERON.
 * Links the SAME heron_line.c as the firmware.
 *
 *   host_heron still <behavior> <t_seconds> <out.ppm>
 *       Step a forced scene to time t inside one behavior, write PPM.
 *   host_heron loopstream
 *       Write a PPM stream (P6 frames back to back on stdout) of one
 *       compressed demo loop: every behavior once, short idle beats.
 *   host_heron sched <seed> <seconds>
 *       Print the scheduler's draw sequence (bag semantics check).
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "heron_line.h"

static uint16_t FB[HL_W * HL_H];

static void write_ppm(FILE *f)
{
    fprintf(f, "P6\n%d %d\n255\n", HL_W, HL_H);
    for (int i = 0; i < HL_W * HL_H; i++) {
        uint16_t v = FB[i];
        unsigned char r = (unsigned char)(((v >> 11) & 0x1F) << 3);
        unsigned char g = (unsigned char)(((v >> 5) & 0x3F) << 2);
        unsigned char b = (unsigned char)((v & 0x1F) << 3);
        fputc(r, f); fputc(g, f); fputc(b, f);
    }
}

static int behavior_from_name(const char *s)
{
    for (int i = 0; i < HL_NBEHAV; i++)
        if (strcmp(s, hl_behavior_name(i)) == 0) return i;
    return -1;
}

int main(int argc, char **argv)
{
    if (argc >= 2 && strcmp(argv[1], "still") == 0 && argc == 5) {
        int b = behavior_from_name(argv[2]);
        if (b < 0) { fprintf(stderr, "unknown behavior %s\n", argv[2]); return 1; }
        float t = (float)atof(argv[3]);
        hl_scene s;
        hl_scene_init(&s, FB, 7, 0);
        hl_scene_force(&s, b);
        float dt = 1.0f / 12.0f;
        if (b == HL_IDLE) { for (int i = 0; i < (int)(t * 12); i++) hl_scene_step(&s, dt); }
        else while (s.state_t < t && s.state == b) hl_scene_step(&s, dt);
        FILE *f = fopen(argv[4], "wb");
        if (!f) { perror("fopen"); return 1; }
        write_ppm(f);
        fclose(f);
        return 0;
    }
    if (argc >= 2 && strcmp(argv[1], "loopstream") == 0) {
        static const struct { int b; float secs; } SEQ[] = {
            { HL_IDLE, 1.0f }, { HL_STRIKE, 9.0f }, { HL_IDLE, 0.8f },
            { HL_STRIDE, 11.0f }, { HL_IDLE, 0.8f }, { HL_PREEN, 10.0f },
            { HL_IDLE, 0.8f }, { HL_STRETCH, 9.0f }, { HL_MISS, 10.0f },
            { HL_IDLE, 0.8f }, { HL_COURTSHIP, 11.0f }, { HL_FLIGHT, 13.0f },
            { HL_IDLE, 1.2f },
        };
        hl_scene s;
        hl_scene_init(&s, FB, 7, 0);
        float dt = 1.0f / 12.0f;
        for (unsigned i = 0; i < sizeof(SEQ) / sizeof(SEQ[0]); i++) {
            hl_scene_force(&s, SEQ[i].b);
            int frames = (int)(SEQ[i].secs * 12.0f);
            for (int k = 0; k < frames; k++) {
                hl_scene_step(&s, dt);
                write_ppm(stdout);
            }
        }
        return 0;
    }
    if (argc >= 4 && strcmp(argv[1], "sched") == 0) {
        hl_scene s;
        hl_scene_init(&s, FB, (uint32_t)strtoul(argv[2], NULL, 10), 0);
        float target = (float)atof(argv[3]);
        float dt = 1.0f;
        int last = -2;
        while (s.t_abs < target) {
            hl_scene_step(&s, dt);
            if (s.state != last) {
                printf("t=%6.0f  %s\n", (double)s.t_abs, hl_behavior_name(s.state));
                last = s.state;
            }
        }
        return 0;
    }
    fprintf(stderr, "usage: still|loopstream|sched\n");
    return 1;
}
