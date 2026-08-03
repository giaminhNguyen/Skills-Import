// Serializers — shared read/write helpers for converting Figma node data to JSON.
// Enhanced to output ALL properties needed for accurate Figma-to-Unity conversion.

export const isMixed = (value: any) => typeof value === "symbol";

// Round floating-point pixel values to 2 decimal places.
// Figma sometimes returns values like 123.99999999999999 instead of 124.
const pixelRound = (v: number) => Math.round(v * 100) / 100;

export const toHex = (color: any) => {
  const clamp = (v: any) => Math.min(255, Math.max(0, Math.round(v * 255)));
  const [r, g, b] = [clamp(color.r), clamp(color.g), clamp(color.b)];
  return `#${[r, g, b].map((v) => v.toString(16).padStart(2, "0")).join("")}`;
};

// ── Legacy hex-string serializer (kept for backward compat with AI tools) ────

export const serializePaints = (paints: any) => {
  if (isMixed(paints)) return "mixed";

  if (!paints || !Array.isArray(paints)) return undefined;

  const result = paints
    .filter((paint: any) => paint.type === "SOLID" && "color" in paint)
    .map((paint: any) => {
      const hex = toHex(paint.color);
      const opacity = paint.opacity != null ? paint.opacity : 1;
      if (opacity === 1) return hex;
      return (
        hex +
        Math.round(opacity * 255)
          .toString(16)
          .padStart(2, "0")
      );
    });

  return result.length > 0 ? result : undefined;
};

// ── Enhanced typed paint serializer (outputs Figma REST API-compatible format) ──

const serializeColor = (color: any) => {
  if (!color) return undefined;
  return {
    r: color.r,
    g: color.g,
    b: color.b,
    a: "a" in color ? color.a : 1,
  };
};

// Convert Figma Plugin API's gradientTransform (2x3 affine matrix)
// to the three gradientHandlePositions used by the REST API.
// The matrix maps from (0,0)-(1,1) gradient space to node-local space.
// handle0 = transform * (0, 0.5)  — start point
// handle1 = transform * (1, 0.5)  — end point
// handle2 = transform * (0, 0)    — width direction control
const gradientTransformToHandlePositions = (transform: any) => {
  if (!transform || !Array.isArray(transform) || transform.length < 2) return undefined;
  const [[a, b, tx], [c, d, ty]] = transform;
  return [
    { x: pixelRound(b * 0.5 + tx), y: pixelRound(d * 0.5 + ty) },
    { x: pixelRound(a + b * 0.5 + tx), y: pixelRound(c + d * 0.5 + ty) },
    { x: pixelRound(tx), y: pixelRound(ty) },
  ];
};

export const serializePaintsTyped = (paints: any) => {
  if (isMixed(paints)) return undefined;
  if (!paints || !Array.isArray(paints)) return undefined;

  const result = paints.map((paint: any) => {
    const base: any = {
      type: paint.type,
    };

    // Only include non-default values to reduce payload
    if (paint.visible === false) base.visible = false;
    if (paint.opacity != null && paint.opacity !== 1) base.opacity = paint.opacity;

    if (paint.type === "SOLID" && "color" in paint) {
      base.color = serializeColor(paint.color);
    } else if (paint.type && paint.type.startsWith("GRADIENT_")) {
      // Gradient fills: LINEAR, RADIAL, ANGULAR, DIAMOND
      if (paint.gradientStops) {
        base.gradientStops = paint.gradientStops.map((stop: any) => ({
          position: stop.position,
          color: serializeColor(stop.color),
        }));
      }
      if (paint.gradientTransform) {
        base.gradientHandlePositions = gradientTransformToHandlePositions(paint.gradientTransform);
      }
    } else if (paint.type === "IMAGE") {
      if (paint.scaleMode) base.scaleMode = paint.scaleMode;
      if (paint.imageHash) base.imageRef = paint.imageHash;
    }

    return base;
  });

  return result.length > 0 ? result : undefined;
};

// ── Effects serializer ──────────────────────────────────────────────────────

export const serializeEffects = (effects: any) => {
  if (isMixed(effects)) return undefined;
  if (!effects || !Array.isArray(effects)) return undefined;

  const result = effects.map((effect: any) => {
    const base: any = {
      type: effect.type,
    };

    if (effect.visible === false) base.visible = false;
    if (effect.color) base.color = serializeColor(effect.color);
    if (effect.offset) {
      base.offset = { x: pixelRound(effect.offset.x), y: pixelRound(effect.offset.y) };
    }
    if (effect.radius != null) base.radius = effect.radius;
    if (effect.spread != null && effect.spread !== 0) base.spread = effect.spread;

    return base;
  });

  return result.length > 0 ? result : undefined;
};

// ── Constraints serializer ──────────────────────────────────────────────────

export const serializeConstraints = (node: any) => {
  if (!("constraints" in node) || !node.constraints) return undefined;
  return {
    horizontal: node.constraints.horizontal,
    vertical: node.constraints.vertical,
  };
};

// ── Absolute bounding box ───────────────────────────────────────────────────

export const serializeAbsoluteBoundingBox = (node: any) => {
  if ("absoluteBoundingBox" in node && node.absoluteBoundingBox) {
    const bb = node.absoluteBoundingBox;
    return {
      x: pixelRound(bb.x),
      y: pixelRound(bb.y),
      width: pixelRound(bb.width),
      height: pixelRound(bb.height),
    };
  }
  if ("absoluteRenderBounds" in node && node.absoluteRenderBounds) {
    const rb = node.absoluteRenderBounds;
    return {
      x: pixelRound(rb.x),
      y: pixelRound(rb.y),
      width: pixelRound(rb.width),
      height: pixelRound(rb.height),
    };
  }
  return undefined;
};

// ── Auto-layout properties ──────────────────────────────────────────────────

export const serializeAutoLayoutProperties = (node: any) => {
  const result: any = {};

  if ("layoutMode" in node && node.layoutMode !== "NONE") {
    result.layoutMode = node.layoutMode;
  }
  if ("primaryAxisAlignItems" in node) result.primaryAxisAlignItems = node.primaryAxisAlignItems;
  if ("counterAxisAlignItems" in node) result.counterAxisAlignItems = node.counterAxisAlignItems;
  if ("itemSpacing" in node) result.itemSpacing = node.itemSpacing;
  if ("counterAxisSpacing" in node && node.counterAxisSpacing != null) {
    result.counterAxisSpacing = node.counterAxisSpacing;
  }
  if ("layoutWrap" in node && node.layoutWrap !== "NO_WRAP") result.layoutWrap = node.layoutWrap;
  if ("paddingLeft" in node) {
    result.paddingLeft = node.paddingLeft;
    result.paddingRight = node.paddingRight;
    result.paddingTop = node.paddingTop;
    result.paddingBottom = node.paddingBottom;
  }
  if ("layoutSizingHorizontal" in node) result.layoutSizingHorizontal = node.layoutSizingHorizontal;
  if ("layoutSizingVertical" in node) result.layoutSizingVertical = node.layoutSizingVertical;

  // Per-child layout properties (present on children inside auto-layout)
  if ("layoutPositioning" in node && node.layoutPositioning !== "AUTO") {
    result.layoutPositioning = node.layoutPositioning;
  }
  if ("layoutGrow" in node && node.layoutGrow !== 0) result.layoutGrow = node.layoutGrow;
  if ("layoutAlign" in node && node.layoutAlign !== "INHERIT") result.layoutAlign = node.layoutAlign;

  return Object.keys(result).length > 0 ? result : undefined;
};

// ── Stroke properties ───────────────────────────────────────────────────────

const serializeStrokeProperties = (node: any) => {
  const result: any = {};

  if ("strokeWeight" in node && !isMixed(node.strokeWeight) && node.strokeWeight > 0) {
    result.strokeWeight = node.strokeWeight;
  }
  if ("strokeAlign" in node) result.strokeAlign = node.strokeAlign;
  if ("strokeTopWeight" in node) {
    result.individualStrokeWeights = {
      top: node.strokeTopWeight,
      right: node.strokeRightWeight,
      bottom: node.strokeBottomWeight,
      left: node.strokeLeftWeight,
    };
  }
  if ("dashPattern" in node && node.dashPattern && node.dashPattern.length > 0) {
    result.strokeDashes = [...node.dashPattern];
  }

  return Object.keys(result).length > 0 ? result : undefined;
};

// ── Corner radii ────────────────────────────────────────────────────────────

const serializeCornerRadii = (node: any) => {
  if ("rectangleCornerRadii" in node && node.rectangleCornerRadii) {
    const [tl, tr, br, bl] = node.rectangleCornerRadii;
    if (tl > 0 || tr > 0 || br > 0 || bl > 0) {
      return [tl, tr, br, bl];
    }
  }
  return undefined;
};

// ── Text style (flat object matching FigmaTextStyle JSON) ───────────────────

const resolveLineHeightPx = (node: any) => {
  if (isMixed(node.lineHeight)) return undefined;
  const lh = node.lineHeight;
  if (!lh || lh.unit === "AUTO") return undefined;
  if (lh.unit === "PIXELS") return lh.value;
  if (lh.unit === "PERCENT" && !isMixed(node.fontSize)) {
    return (node.fontSize * lh.value) / 100;
  }
  return undefined;
};

const resolveLetterSpacingPx = (node: any) => {
  if (isMixed(node.letterSpacing)) return 0;
  const ls = node.letterSpacing;
  if (!ls || ls.value === 0) return 0;
  if (ls.unit === "PIXELS") return ls.value;
  if (ls.unit === "PERCENT" && !isMixed(node.fontSize)) {
    return (node.fontSize * ls.value) / 100;
  }
  return 0;
};

export const serializeTextStyle = (node: any) => {
  const style: any = {};

  if (!isMixed(node.fontName) && node.fontName) {
    style.fontFamily = node.fontName.family;
    style.fontPostScriptName = node.fontName.style
      ? `${node.fontName.family}-${node.fontName.style.replace(/\s+/g, "")}`
      : undefined;
  } else if (isMixed(node.fontName)) {
    style.fontFamily = "mixed";
  }

  style.fontWeight = isMixed(node.fontWeight) ? 400 : (node.fontWeight ?? 400);
  style.fontSize = isMixed(node.fontSize) ? 12 : (node.fontSize ?? 12);

  if (!isMixed(node.textAlignHorizontal)) style.textAlignHorizontal = node.textAlignHorizontal;
  if (!isMixed(node.textAlignVertical)) style.textAlignVertical = node.textAlignVertical;

  const letterSpacingPx = resolveLetterSpacingPx(node);
  if (letterSpacingPx !== 0) style.letterSpacing = pixelRound(letterSpacingPx);

  const lineHeightPx = resolveLineHeightPx(node);
  if (lineHeightPx != null) style.lineHeightPx = pixelRound(lineHeightPx);

  if (!isMixed(node.lineHeight) && node.lineHeight && node.lineHeight.unit === "PERCENT") {
    style.lineHeightPercent = node.lineHeight.value;
  }

  if ("textAutoResize" in node) style.textAutoResize = node.textAutoResize;

  if (!isMixed(node.textDecoration) && node.textDecoration && node.textDecoration !== "NONE") {
    style.textDecoration = node.textDecoration;
  }

  if (!isMixed(node.textCase) && node.textCase && node.textCase !== "ORIGINAL") {
    style.textCase = node.textCase;
  }

  if ("textTruncation" in node && node.textTruncation !== "DISABLED") {
    style.textTruncation = node.textTruncation;
  }

  return style;
};

// ── Relative bounds (kept for backward compat) ──────────────────────────────

export const getBounds = (node: any) => {
  if ("x" in node && "y" in node && "width" in node && "height" in node) {
    return {
      x: pixelRound(node.x),
      y: pixelRound(node.y),
      width: pixelRound(node.width),
      height: pixelRound(node.height),
    };
  }

  return undefined;
};

// ── Legacy styles sub-object (kept for backward compat with AI tools) ───────

export const serializeStyles = async (node: any) => {
  const styles: any = {};

  if ("fills" in node) {
    if (node.fillStyleId && typeof node.fillStyleId === "string") {
      const style = await figma.getStyleByIdAsync(node.fillStyleId);
      if (style) styles.fillStyle = style.name;
    }
    const fills = serializePaints(node.fills);
    if (fills !== undefined) styles.fills = fills;
  }

  if ("strokes" in node) {
    if (node.strokeStyleId && typeof node.strokeStyleId === "string") {
      const style = await figma.getStyleByIdAsync(node.strokeStyleId);
      if (style) styles.strokeStyle = style.name;
    }
    const strokes = serializePaints(node.strokes);
    if (strokes !== undefined) styles.strokes = strokes;
  }

  if ("cornerRadius" in node) {
    const cr = isMixed(node.cornerRadius) ? "mixed" : node.cornerRadius;
    if (cr !== 0) styles.cornerRadius = cr;
  }

  if ("paddingLeft" in node) {
    styles.padding = {
      top: node.paddingTop,
      right: node.paddingRight,
      bottom: node.paddingBottom,
      left: node.paddingLeft,
    };
  }

  return styles;
};

export const serializeLineHeight = (lineHeight: any) => {
  if (isMixed(lineHeight)) return "mixed";

  if (!lineHeight || lineHeight.unit === "AUTO") return undefined;

  return { value: lineHeight.value, unit: lineHeight.unit };
};

export const serializeLetterSpacing = (letterSpacing: any) => {
  if (isMixed(letterSpacing)) return "mixed";

  if (!letterSpacing || letterSpacing.value === 0) return undefined;

  return { value: letterSpacing.value, unit: letterSpacing.unit };
};

// ── Legacy text serializer (augmented with top-level style) ─────────────────

export const serializeText = async (node: any, base: any) => {
  let fontFamily: any;
  let fontStyle: any;

  if (typeof node.fontName === "symbol") {
    fontFamily = "mixed";
    fontStyle = "mixed";
  } else if (node.fontName) {
    fontFamily = node.fontName.family;
    fontStyle = node.fontName.style;
  }

  const textStyleName =
    node.textStyleId && typeof node.textStyleId === "string"
      ? ((await figma.getStyleByIdAsync(node.textStyleId))?.name ?? undefined)
      : undefined;

  return Object.assign({}, base, {
    characters: node.characters,
    // Top-level "style" object matching FigmaTextStyle JSON property names
    style: serializeTextStyle(node),
    // Legacy "styles" sub-object for backward compat
    styles: Object.assign({}, base.styles, {
      ...(textStyleName ? { textStyle: textStyleName } : {}),
      fontSize: isMixed(node.fontSize) ? "mixed" : node.fontSize,
      fontFamily,
      fontStyle,
      fontWeight: isMixed(node.fontWeight) ? "mixed" : node.fontWeight,
      textDecoration: isMixed(node.textDecoration)
        ? "mixed"
        : node.textDecoration !== "NONE"
          ? node.textDecoration
          : undefined,
      lineHeight: serializeLineHeight(node.lineHeight),
      letterSpacing: serializeLetterSpacing(node.letterSpacing),
      textAlignHorizontal: isMixed(node.textAlignHorizontal)
        ? "mixed"
        : node.textAlignHorizontal,
    }),
  });
};

// ── Main enhanced node serializer ───────────────────────────────────────────

export const serializeNode = async (node: any): Promise<any> => {
  const styles = await serializeStyles(node);

  // Build base with identity and backward-compat fields
  const base: any = {
    id: node.id,
    name: node.name,
    type: node.type,
    bounds: getBounds(node),
    styles,
  };

  // ── Absolute bounding box (critical for Unity positioning accuracy) ──
  const absoluteBB = serializeAbsoluteBoundingBox(node);
  if (absoluteBB) base.absoluteBoundingBox = absoluteBB;

  // ── Visual properties (only include non-defaults to reduce payload) ──
  if ("visible" in node && node.visible === false) base.visible = false;
  if ("opacity" in node && node.opacity !== 1) base.opacity = node.opacity;
  if ("blendMode" in node && node.blendMode !== "PASS_THROUGH") base.blendMode = node.blendMode;
  if ("rotation" in node && node.rotation !== 0) base.rotation = pixelRound(node.rotation);
  if ("isMask" in node && node.isMask) base.isMask = true;
  if ("clipsContent" in node && node.clipsContent) base.clipsContent = true;

  // ── Constraints ──
  const constraints = serializeConstraints(node);
  if (constraints) base.constraints = constraints;

  // ── Fills (typed objects for Unity, hex strings in styles for AI tools) ──
  if ("fills" in node) {
    const typedFills = serializePaintsTyped(node.fills);
    if (typedFills) base.fills = typedFills;
  }

  // ── Strokes (typed objects + stroke properties) ──
  if ("strokes" in node) {
    const typedStrokes = serializePaintsTyped(node.strokes);
    if (typedStrokes) base.strokes = typedStrokes;
  }
  const strokeProps = serializeStrokeProperties(node);
  if (strokeProps) Object.assign(base, strokeProps);

  // ── Effects ──
  if ("effects" in node) {
    const effects = serializeEffects(node.effects);
    if (effects) base.effects = effects;
  }

  // ── Corner radius ──
  if ("cornerRadius" in node) {
    const cr = isMixed(node.cornerRadius) ? 0 : node.cornerRadius;
    if (cr > 0) base.cornerRadius = cr;
  }
  const cornerRadii = serializeCornerRadii(node);
  if (cornerRadii) base.cornerRadii = cornerRadii;

  // ── Auto-layout properties ──
  const layoutProps = serializeAutoLayoutProperties(node);
  if (layoutProps) Object.assign(base, layoutProps);

  // ── Component ID for INSTANCE nodes ──
  if (node.type === "INSTANCE") {
    try {
      const mainComponent = await node.getMainComponentAsync();
      if (mainComponent) base.componentId = mainComponent.id;
    } catch {
      // Deleted component or permission issue — skip
    }
  }

  // ── TEXT nodes ──
  if (node.type === "TEXT") return serializeText(node, base);

  // ── Children ──
  if ("children" in node) {
    return Object.assign({}, base, {
      children: await Promise.all(node.children.map((child: any) => serializeNode(child))),
    });
  }

  return base;
};

// ── Style deduplication (for get_document / get_design_context) ──────────────

export const deduplicateStyles = (tree: any): { tree: any; globalVars: Record<string, any> | undefined } => {
  const counts = new Map<string, number>();
  const countWalk = (node: any) => {
    if (!node || typeof node !== "object") return;
    // Count both legacy styles.fills and top-level fills
    const s = node.styles;
    if (s) {
      if (Array.isArray(s.fills)) counts.set(JSON.stringify(s.fills), (counts.get(JSON.stringify(s.fills)) ?? 0) + 1);
      if (Array.isArray(s.strokes)) counts.set(JSON.stringify(s.strokes), (counts.get(JSON.stringify(s.strokes)) ?? 0) + 1);
    }
    if (Array.isArray(node.fills)) counts.set("f:" + JSON.stringify(node.fills), (counts.get("f:" + JSON.stringify(node.fills)) ?? 0) + 1);
    if (Array.isArray(node.strokes)) counts.set("s:" + JSON.stringify(node.strokes), (counts.get("s:" + JSON.stringify(node.strokes)) ?? 0) + 1);
    if (Array.isArray(node.children)) node.children.forEach(countWalk);
  };
  countWalk(tree);

  let counter = 0;
  const keyToRef = new Map<string, string>();
  const refs: Record<string, any> = {};
  for (const [key, count] of counts) {
    if (count > 1) {
      const ref = `s${++counter}`;
      keyToRef.set(key, ref);
      refs[ref] = key.startsWith("f:") || key.startsWith("s:") ? JSON.parse(key.slice(2)) : JSON.parse(key);
    }
  }
  if (keyToRef.size === 0) return { tree, globalVars: undefined };

  const replaceWalk = (node: any): any => {
    if (!node || typeof node !== "object") return node;
    let result = node;
    const s = node.styles;
    if (s) {
      let newStyles = s;
      if (Array.isArray(s.fills)) {
        const ref = keyToRef.get(JSON.stringify(s.fills));
        if (ref) newStyles = { ...newStyles, fills: ref };
      }
      if (Array.isArray(s.strokes)) {
        const ref = keyToRef.get(JSON.stringify(s.strokes));
        if (ref) newStyles = { ...newStyles, strokes: ref };
      }
      if (newStyles !== s) result = { ...node, styles: newStyles };
    }
    // Also deduplicate top-level fills/strokes
    if (Array.isArray(node.fills)) {
      const ref = keyToRef.get("f:" + JSON.stringify(node.fills));
      if (ref) result = { ...result, fills: ref };
    }
    if (Array.isArray(node.strokes)) {
      const ref = keyToRef.get("s:" + JSON.stringify(node.strokes));
      if (ref) result = { ...result, strokes: ref };
    }
    if (Array.isArray(node.children)) {
      const newChildren = node.children.map(replaceWalk);
      result = { ...result, children: newChildren };
    }
    return result;
  };

  return { tree: replaceWalk(tree), globalVars: { styles: refs } };
};

export const serializeVariableValue = (value: any) => {
  if (typeof value !== "object" || value === null) return value;

  if ("type" in value && value.type === "VARIABLE_ALIAS") {
    return { type: "VARIABLE_ALIAS", id: value.id };
  }

  if ("r" in value && "g" in value && "b" in value) {
    return {
      type: "COLOR",
      r: value.r,
      g: value.g,
      b: value.b,
      a: "a" in value ? value.a : 1,
    };
  }

  return value;
};
