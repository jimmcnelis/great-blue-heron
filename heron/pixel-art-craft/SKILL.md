# Cartoon Craft for Generated Grid Animation

The north star is a hand-drawn cartoon that happens to be rasterized onto a small grid. The grid is a hardware constraint, never the aesthetic. This playbook adapts the classic cartoonist's craft (the 12 principles from Thomas and Johnston's The Illusion of Life, Richard Williams' Animator's Survival Kit, and limited TV animation practice) to a rig plus corpus plus tiny-model generation pipeline, and keeps grid hygiene as a supporting discipline in service of the drawn look.

## Set the north star

- Treat every frame as a drawing first and a grid second. When a choice trades pixel-art charm against drawn cartoon, choose drawn.

- Build the image from bold unbroken shapes, decisive flat color, and minimal interior detail. Never use dither patterns, chunky-pixel styling, or retro-game cues as a look.

- Judge the work at final display size before judging it zoomed in. If the silhouette does not read at display size, no amount of interior detail will save it.

- Keep the palette small and fixed. A color exists because the character design calls for it, not because a gradient wanted a midpoint.

## Direct like a cartoonist

- Pose to pose, always. Author the key poses first (the coil, the strike, the landing), then let inbetween frames serve the keys. Never let an interpolation scheme invent the acting.

- Give every major action an anticipation. The character moves a readable amount in the opposite direction before the main move: the coil before the strike, the crouch before the takeoff, the head draw-back before the swallow. Small actions get a few frames of prep, big actions get a held, deepening prep.

- Land accents on a hold. Let the strongest pose of an action sit on screen for several frames instead of drifting through it. Holds are punctuation, and the eye reads the pose during the hold.

- Keep every hold moving. A held pose that is perfectly frozen dies on screen, so keep a slow drift or settle running in the direction of the action (breath, sway, a plume still settling). Richard Williams calls this the moving hold. In a generated pipeline, low-amplitude low-frequency latent noise over a held trajectory is the moving hold, and it belongs on idle and hold segments only.

- Use squash and stretch to show weight and speed, and preserve volume while doing it. A strike elongates, a landing compresses, and the silhouette area stays roughly constant while the aspect changes.

- Add follow-through and overlapping action to everything loose. Plumes, tails, necks, and water keep moving after the body stops, and they start a beat after the body starts. The swallow finishes in the throat after the beak is still, and the landing settle outlasts the touchdown.

- Move parts along arcs, never straight lines. Heads, beak tips, wingtips, and tossed objects travel curved paths. A straight-line path between two keys is the single most reliable way to make generated motion read as mechanical mush.

- Bunch the spacing at the ends of a move (slow in and slow out), and spread it in the middle. Even spacing is dead spacing. In a latent pipeline this means anchoring playback to real recorded trajectories and damping any path that cuts across the latent space in a straight line.

- Spend timing like money. Frame counts set weight and mood: the strike fires in very few frames, the aim takes its time, idles breathe slowly. Fast actions read snappier with fewer, stronger drawings, which is why Warner Bros. shorts animated on twos feel quicker than features animated on ones.

- Exaggerate the accent past realism. Deepen the coil, lengthen the stretch, push the reaction. At small display sizes a realistic accent reads as no accent.

- Add secondary action that supports the main idea and never competes with it. Blinks, ripples, and drips are seasoning. One clear idea per beat, staged so the eye knows where to look.

## Shoot it like limited TV animation

- Hold drawings on twos during slow motion and reserve ones for the fastest accents. A 24 fps timeline does not need 24 new drawings per second, and forcing them invites mush.

- Reuse cycles for repetitive motion such as walking, then vary them with overlays (head turns, blinks, a look-back) so the loop never reads as a loop.

- Layer the character. What does not move in a beat stays exactly, provably still, the way a held cel sat under a moving one. Hanna-Barbera built characters with clean break lines (collars, neckbands) so a moving head could sit on a still body, and the same thinking tells you where a rig may split.

- Treat any shimmer in a part that should be still as a defect, not a texture. Traditional animators called that line boiling, and it came from inaccurate inbetweens. In a generated pipeline, decode noise on a held pose is boiling, and the hygiene pass below exists to kill it.

## Smear the fastest beats

- When a part moves faster than a clean inbetween can sell (roughly, when it crosses its own length in one or two frames), draw the blur instead of the part. Elongate the shape along its path for one or two frames at the peak of the move, or use multiples (the part drawn two or three times along the path).

- Credit the technique correctly. Chuck Jones standardized the smear frame at Warner Bros., most famously in The Dover Boys at Pimento University (1942), and studio heads nearly fired him for it before it became house style.

- Judge smears in motion, never in a freeze frame. A smear is supposed to look wrong when paused and invisible at speed. Gate them by playing the clip.

- Author smears as deliberate frames in the rig and corpus. A decoder will not invent a good smear, and a post-process blur reads as a rendering error, not as drawing.

## Keep the grid clean (hygiene in service of the drawing)

- Snap every decoded cell to the palette. Off-palette colors in the output are a pipeline bug, never a style.

- Build shapes from unbroken clusters of one color. A lone cell of one color stranded inside another is an orphan, and an orphan is almost always decode noise. Absorb it into the surrounding color or grow it into a real cluster.

- Protect designed micro-details from cleanup. An eye, a beak tip, or a fish eye may legitimately be a one or two cell cluster. Whitelist small clusters by role and position (attached to the head, at the silhouette edge) before running any orphan filter, and verify the whitelist on a pulled frame.

- Remove only strays that fail all protections: small connected components of a non-background color that touch neither the main subject mass nor any whitelisted detail. Reassign them to the dominant neighboring color.

- Kill single-frame flicker with a temporal rule. A cell that flips color for exactly one frame and flips back (an A-B-A pattern) during a held or slow segment is boiling. Snap it back to A. Never apply the rule across a fast accent, where one-frame shapes may be deliberate smears.

- Anti-alias sparingly and only inside the drawing. Flat storybook style forbids anti-aliasing against the background at the silhouette edge, where it reads as dirt. Inside, a buffer cell must never overpower the cluster it softens, and buffer cells must never line up in equal-width bands along an edge (that is banding, and it flattens the form).

- Keep line run-lengths rhythmic. A curve whose steps stutter (runs of 3, 1, 3 where the shape wants 3, 3, 2, 2) reads as a jaggy. In generated output the fix is upstream in the rig, so log jaggy freeze frames as rig notes instead of trying to repaint them downstream.

- Never dither. A flat shape stays flat. If a transition needs help, add one deliberate palette step, not a checkerboard.

## Measure cleanliness before claiming it

- Report palette exactness as the fraction of on-palette cells in the decoded grids (target 1.0) and the near-palette fraction in the compressed video (target at least 0.999).

- Report the orphan count per episode as isolated single cells per frame, mean and max, before and after cleanup. Count only cells that fail the whitelist, so the number means noise, not design.

- Report the boiling metric as A-B-A single-frame flips per 1,000 cell-frames inside held and idle segments, before and after the temporal pass. A good pass removes the large majority and changes nothing outside those segments.

- Report the cluster profile as a histogram of connected component sizes per color across sampled frames. Singleton share outside the whitelist should be near zero after cleanup.

- Report frame-to-frame change as the median changed-cell count, and flag any segment join whose change count exceeds three times the median. Joins are where generated episodes go to die.

- Pull gate frames from the final rendered file, not from intermediate grids: one idle stance, one fastest accent, one hold, and one action frame (flight or walk). Read the stance and the accent against the character reference, check the hold frame for stray ink or noise, and play the accent in motion before passing a smear.

## Sequence the pipeline

- Author keys and cycles in the rig, render the corpus, train the model, decode with palette snap, then run hygiene in a fixed order: orphan cleanup first, temporal deflicker second, procedural layers (ink, effects) last so cleanup can never eat a caused effect.

- Measure before and after on the same decoded grids, and keep the raw decode. If a hygiene rule hurts a pulled frame, the rule loses, not the frame.

- Park rig-level craft (new anticipation poses, authored smears, follow-through clips) as explicit next-version items in the build report. Never silently fold a re-pose into a cleanup pass.

## Sources worth rereading

- Frank Thomas and Ollie Johnston, The Illusion of Life (1981), for the 12 principles in their original form.

- Richard Williams, The Animator's Survival Kit, for timing charts, spacing, walks, and the moving hold.

- Michael Azzi, Pixel Logic, for clusters, banding, and anti-aliasing discipline at small sizes.

- Pedro Medeiros (Saint11) and the Pixelation Ramblethread tradition, for cluster-first drawing and orphan cleanup practice.

## Available connectors

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.

## Websites

- [Smear frame, Wikipedia](https://en.wikipedia.org/wiki/Smear_frame) for the history and the types of smears (elongated, multiples, duplicated). Verify any production claim against a second source before repeating it as fact.

- [Limited animation, Wikipedia](https://en.wikipedia.org/wiki/Limited_animation) for the economy techniques (holds, cycles, twos, cel layering) and their UPA and Hanna-Barbera lineage.

- [12 Principles of Animation, Omebly](https://omebly.com/blog/12-principles-of-animation/) for a quick illustrated refresher on the 12 principles before a build. Use it as a checklist prompt, not as the authority.
