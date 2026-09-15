# Workflow: Asset Integration

## Goal

Bring art, animation, VFX, audio, UI, or data assets into the runtime project with correct import settings, naming, references, budgets, and platform behavior.

## Steps

1. Identify asset type, source, intended runtime use, target platforms, and ownership.
2. Inspect project naming/folder/import conventions.
3. Validate source dimensions/topology/bones/channels/sample rates/format as relevant.
4. Configure import settings using project presets when available.
5. Validate runtime references and dependency direction.
6. Check compression, LOD, streaming, mipmaps, shader/material variants, animation compression, or audio settings as relevant.
7. Test representative runtime use, including loading/unloading or pooling where relevant.
8. Compare against performance and memory budgets.
9. Document exceptions to standard import rules.

## Asset-type focus

- **3D:** scale, axis, topology, materials, LODs, skeleton, bounds.
- **Animation:** skeleton compatibility, root motion, clips, compression, events/curves.
- **Texture:** dimensions, color space, mipmaps, compression, streaming, atlas policy.
- **VFX:** shader variants, overdraw, particle count, bounds, platform fallback.
- **Audio:** sample rate, channels, compression, streaming/decompression policy, loudness conventions.
- **UI:** resolution strategy, atlasing, font/glyph coverage, localization expansion.

## Integration gate

The asset is integrated when it imports reproducibly, renders/plays correctly in its target context, has no broken dependencies, and fits relevant content/performance budgets.
