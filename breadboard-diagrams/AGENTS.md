# Breadboard diagram work

- Start with README.md and the requested circuit JSON. Do not reconstruct a
  saved circuit from a chat transcript when its source files exist here.
- Keep component header definitions under parts/ separate from circuit nets,
  placement, wire routes and explanatory text under circuits/.
- Check manufacturer pin order before changing a footprint. Model every
  exposed pin, including unused pins and duplicate grounds.
- Preserve existing firmware pin assignments unless the user requests a change
  or an evidenced electrical constraint requires one. Explain that change.
- Validation must reject shorts between 5 V, logic VDD and ground; unexpected
  connections to unused GPIO; open required paths; and duplicate hole occupancy.
- Drawn crossings are not junctions. Resistors are not zero-ohm net unions.
- No motor current, supply transient, GPIO voltage or mechanical fit should be
  described as bench-tested without an actual measurement from the user.
- Run the connectivity fault tests and the circuit check after an electrical
  edit. Regenerate SVG, PNG, PDF and wiring exports from the same circuit data.
- Inspect the actual PNG and a separately rendered PDF page. Fix clipped text,
  overlapping labels, ambiguous wire endpoints and accidental-looking crossings.
- Update the committed SVG preview and preserve source, inputs, instructions
  and verification evidence in Git. Do not save only a finished raster image.
- Keep this library self-contained in this directory. Its parent repository
  contains independent tools; avoid changing unrelated files.
