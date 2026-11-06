"""Build assets.bin for seq2: 64 KB header page (magic 'HAST' +
offset/length per asset), then each asset at a 64 KB boundary.
Order: 0=strike_layers.mjpeg 1=flight_out_layers.mjpeg
2=flight_home_layers.mjpeg 3=plate.jpg. All bird-only LAYERS + plate.
Flash with: esptool write_flash 0xD10000 assets.bin"""
import struct, os
PAGE = 64 * 1024
SRC = os.path.expanduser('~/workspace/heron/seq2-layers/device')
NAMES = ['strike_layers.mjpeg', 'flight_out_layers.mjpeg', 'flight_home_layers.mjpeg', 'plate.jpg']
blobs = [open(os.path.join(SRC, n), 'rb').read() for n in NAMES]
off, pos = [], PAGE
for b in blobs:
    off.append(pos)
    pos += (len(b) + PAGE - 1) // PAGE * PAGE
hdr = bytearray(PAGE)
struct.pack_into('<I', hdr, 0, 0x54534148)
for i, b in enumerate(blobs):
    struct.pack_into('<II', hdr, 4 + 8 * i, off[i], len(b))
out = bytearray(hdr)
for o, b in zip(off, blobs):
    out += b'\xFF' * (o - len(out))
    out += b
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets.bin'), 'wb').write(out)
print('assets.bin:', len(out), 'bytes |', ' | '.join(f'{n} @ {o} ({len(b)} B)' for n, o, b in zip(NAMES, off, blobs)))
