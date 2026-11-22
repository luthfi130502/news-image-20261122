// news-image-20261122 — "The World in One Day" (Node 22, standard library only).
//
// The finished poster already ships in this repository as entry.png. This
// program's only job is to place that image at /output/entry.png and prove
// the copy is a real, complete PNG. It calls no other program, uses no
// network, and needs nothing installed.
//
// Local check (MAKEFUN_OUTPUT_DIR stands in for /output outside the grader):
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(outDir, { recursive: true });

const source = new URL('./entry.png', import.meta.url);
const target = join(outDir, 'entry.png');

copyFileSync(source, target);

const copied = readFileSync(target);
const pngMagic = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
if (!copied.subarray(0, 8).equals(pngMagic)) {
  throw new Error('entry.png is not a PNG (bad magic bytes)');
}
if (copied.length > 1024 * 1024) {
  throw new Error(`entry.png is ${copied.length} bytes, over the 1 MiB gate limit`);
}
if (statSync(source).size !== copied.length) {
  throw new Error('copied size does not match source entry.png');
}

// PNG IHDR: width and height are big-endian uint32 at offsets 16 and 20.
// A poster that lost its dimensions is not a shippable image.
const width = copied.readUInt32BE(16);
const height = copied.readUInt32BE(20);
if (width < 100 || height < 100) {
  throw new Error(`entry.png dimensions look wrong: ${width}x${height}`);
}

console.log(`entry image ready: ${target} (${copied.length} bytes, ${width}x${height})`);
