# App icon design (Sailfish OS)

Design guidance for launcher icons of workspace apps, so that they belong to
the original Jolla/Sailfish OS icon family. Supplied by the maintainer
(Misja Hoebe, 2026-11-08); referenced from the [principles](principles.md).
Links checked 2026-11-08. Section 10 adds packaging facts verified on Swell.

## 1. Objective

Create an application icon that belongs naturally within the original Jolla/Sailfish OS visual language.

The primary references are the original Jolla application icons, including Phone, Messages, Gallery, Media Player, Browser and Settings.

The design should reflect the distinctive character of Jolla rather than generic contemporary mobile icon conventions.

**The authoritative design artifact must be a genuine, editable SVG.** All raster previews and exports must be generated from that SVG.

This document distinguishes three kinds of guidance:

- **[Official]** Explicitly supported by Jolla/Sailfish documentation.
- **[Observed]** Characteristics identifiable in original Jolla icon examples.
- **[Recommendation]** Design or implementation guidance for workspace apps, not an official Jolla requirement.

Do not treat observations or recommendations as mandatory Sailfish design rules.

## 2. Primary references

### Official Sailfish OS resources

**App Icons — Design Guidelines**

https://sailfishos.org/design/icons/

The official entry point for the icon story and downloadable templates.

**Sailfish OS Apps Icon Story**

https://sailfishos.org/content/uploads/2018/11/48_SAILFISH-APPS-ICON-STORY.pdf

The most important source for understanding the icon shape system.

Explains:

- Why one universal background shape was rejected.
- How rectangular and circular geometry were combined.
- How rotations and combinations produced sixteen base shapes.
- The relationship between base shapes and visual metaphors.
- Historical icon dimensions and vector boundary considerations.

**Official App Icon Template and Library**

https://sailfishos.org/content/uploads/files/Sailfish-Apps-icon-template.zip

Use the original template geometry and inspect the included icon examples.

### Historical design philosophy

**Martin Schüle — Design insights: How we design Sailfish OS**

Jolla Blog, 13 April 2015

https://blog.jolla.com/design-insights-sailfish-os/

Written by Jolla's Chief Designer. Describes the company's design philosophy and multidisciplinary approach.

**The Next Web — How Jolla's personality won the audience at Slush**

24 November 2012

https://thenextweb.com/news/rock-and-roll-with-your-friends-how-jollas-personality-won-the-audience-at-slush

Includes contemporary comments from Martin Schüle and senior designer Jaakko Roppola.

This article primarily concerns the Sailfish user interface and interaction model, rather than the detailed construction of launcher icons. It provides historical context, not additional icon specifications.

## 3. Jolla's design philosophy

**[Official — Martin Schüle, 2015]**

Jolla described five foundational design principles:

### Simple

Make complex user experiences simpler.

For icon design, this suggests a clear visual idea and avoiding unnecessary complexity. It does not require strict minimalism.

### Aesthetic

Design should be balanced, beautiful and aesthetically pleasing.

Visual proportions, color relationships and composition deserve deliberate attention.

### Natural

Designs should look and feel natural, including their behavior, interaction and material qualities.

Organic or flowing forms are therefore not inherently inconsistent with the Sailfish philosophy.

### Magical

Design should provide positive surprise, innovation or a personal sensation.

An icon may have a distinctive, playful or unexpected quality. Functional recognizability need not eliminate personality.

### Holistic

Design should connect user needs, technology and business requirements.

An icon should be considered within the larger operating-system experience rather than as an isolated graphic.

**Important distinction:** These are Jolla's general design principles. The source does not prescribe their exact application to icon geometry, color or gradients.

## 4. The distinctive Sailfish icon shape system

**[Official — Apps Icon Story]**

The original icon system deliberately avoids a single universal background shape.

Jolla's reasoning was that one shape cannot accommodate every visual metaphor equally well. A fixed shape may force compromises or draw attention away from the intended metaphor.

Instead, the designers developed a family of sixteen base shapes by combining and transforming rectangular and circular geometry.

This system serves two purposes:

1. Establishing a recognizable visual family.
2. Allowing individual icons to use a shape appropriate to their purpose.

### Design implications

- Select a base shape from the official template library.
- Use its exact vector geometry.
- Consider the relationship between the outer silhouette and the internal visual metaphor.
- Do not assume that every application should use the same shape.
- Do not substitute a generic rounded rectangle for an official template.

**[Recommendation]** Choose the base shape early in the process, since its geometry should inform the internal composition.

## 5. Outer silhouette, background and visual boundaries

### The outer silhouette

**[Official]** The base shape establishes the icon's background geometry.

The Icon Story also describes an inset outline intended to guide the placement of the internal visual metaphor.

The historical design specification uses an 86 × 86 px icon area and an approximately 0.3 px gap at each side for vector boundaries and smooth antialiasing.

The documentation explicitly indicates that there should otherwise be no general internal padding requirement.

### Background and border regions

**[Observed]** Many original Jolla icons retain visible background areas around their central motifs.

Examples:

- Phone uses a green outer silhouette surrounding the handset.
- Messages uses a darker turquoise background around its speech bubble.
- Media Player places its playback metaphor within a larger colored composition.
- Gallery uses overlapping colored shapes against an orange-red base.

These visible regions contribute to the visual structure.

However:

**A clearly visible border of uniform thickness is not an official requirement.**

Do not automatically add a stroke, decorative frame or mandatory inset margin.

**[Recommendation]** Treat the background as an active part of the composition. Its color and exposed area should complement the foreground metaphor.

## 6. Graphic metaphors and abstraction

**[Official]** The Icon Story explicitly emphasizes the relationship between base shapes and visual metaphors.

The selected shape should support the metaphor rather than distract from it.

**[Observed]** Original Jolla icons frequently employ recognizable objects or concepts simplified into bold graphic compositions.

Examples include a handset, speech bubble, flower-like motif, clock and playback symbol.

The level of abstraction varies across the icon family.

### Design approach

**[Recommendation]**

- Start with one clear visual metaphor.
- Identify its most characteristic shape or relationship.
- Remove detail that does not contribute to recognition.
- Consider both positive and negative space.
- Preserve enough visual weight to remain legible at launcher size.
- Allow asymmetry where it improves expression or balance.

Do not confuse abstraction with extreme simplification.

A successful icon may contain several forms, provided they create a coherent graphic idea.

## 7. Color, layering and gradients

### Color

**[Official]** The Icon Story explicitly introduces color as part of the icon construction process.

It does not prescribe a universal palette, maximum number of colors or flat-color-only approach.

**[Observed]** Original Jolla icons often employ vivid color combinations, with foreground and background elements clearly differentiated.

### Layering and overlapping shapes

**[Observed]** The Gallery icon is an especially useful reference.

Its overlapping, petal-like forms create a unified motif through geometric relationships and color interactions.

Some original icons also use nested forms or layered graphic elements.

**[Recommendation]**

- Let each significant form have a clear purpose.
- Use overlapping shapes when they improve the visual metaphor.
- Preserve the intended geometry of intersections.
- Use transparency where appropriate, but do not assume it is required.
- Avoid adding layers solely to make the illustration more elaborate.

### Gradients and dimensionality

Neither the Icon Story nor the cited design blog establishes a prohibition on gradients, shading or dimensional effects.

**[Recommendation]** Begin with a composition whose geometry is convincing on its own. Introduce gradients or tonal differences only when they materially improve the design.

This is a workflow preference, not a documented Jolla rule.

Avoid excessive decorative effects that undermine clarity or make the icon visually inconsistent with its intended reference set.

The objective is not necessarily flatness, but controlled visual expression.

## 8. Visual character of the original Jolla icons

**[Observed — synthesis, not an official specification]**

Several qualities recur in the original icon family:

- Distinctive outer silhouettes.
- Clear and recognizable graphic metaphors.
- Confident use of color.
- Carefully balanced foreground and background.
- Rounded and geometric forms, sometimes combined with organic curves.
- Selective use of layering and visual depth.
- Individuality within a shared design system.

The icons are not entirely uniform.

Some are highly abstract, while others are comparatively literal. Some have substantial visible background regions; others use much of the available area.

**[Recommendation]** Aim for family resemblance rather than mechanical uniformity.

An icon should feel related to the original Jolla applications without copying any one icon's composition.

## 9. SVG-first design and implementation

**[Workspace requirement — not an official Jolla design rule]**

The SVG is the authoritative source throughout the design process.

This is essential to ensure reproducibility, editability and correct packaging.

### Required workflow

1. Obtain and inspect the official Sailfish template archive.
2. Select an official base shape.
3. Copy or reference its exact vector geometry.
4. Construct the internal graphic directly using SVG geometry.
5. Maintain all important shapes as editable vector elements.
6. Render previews from the SVG.
7. Evaluate and revise the SVG itself.
8. Generate required raster exports from the approved SVG.

### SVG requirements

- Genuine vector paths and primitives.
- No embedded PNG or JPEG.
- No external raster dependencies.
- Correct transparency outside the silhouette.
- Valid SVG structure and coordinate system.
- Reliable rendering with the intended Sailfish build tools.
- Editable foreground and background shapes.
- Controlled clipping and compositing.

An SVG that merely embeds a raster illustration is not an acceptable final deliverable.

### Geometry and intersections

**[Recommendation]** For compositions with overlapping shapes, use explicit layering and carefully constructed paths.

Avoid automatically merging neighboring shapes or forcing them to share boundaries when the intended design requires intersections.

Where two paths genuinely share a boundary, use consistent geometry to avoid visible seams.

## 10. Dimensions and packaging

**[Official — historical specification]**

The Icon Story documents an 86 × 86 px design size for the original Jolla devices, with the small vector-boundary gap described above.

This is a historical design specification.

**[Workspace requirement]** Confirm the current icon sizes, packaging paths and SVG-rendering capabilities required by the target Sailfish OS SDK and application packaging system.

Do not assume that the historical 86 px reference is the only required export dimension.

Maintain one scalable SVG source and derive any required sizes from it.

**[Verified — Swell, SDK target 5.1.0.11, 2026-11-07]**

- The SDK app template and the Harbour validator expect PNGs at 86, 108, 128
  and 172 px, in `icons/<size>x<size>/harbour-<app>.png`, installed to
  `/usr/share/icons/hicolor/<size>x<size>/apps/`. The validator reports "All
  needed icons found" when they are present.
- Keep the SVG next to them (`icons/harbour-<app>.svg`); the packaging does
  not install it.
- Check that an SVG is a real vector before using it: an SVG that only wraps
  a PNG renders correctly but cannot be edited, and an SVG exported beside
  the PNGs may not match them. Render it and compare.
- After an icon change on a device, the launcher keeps showing the old icon
  until lipstick restarts (`systemctl --user restart lipstick`, which needs
  the device owner's approval), even though the installed PNGs are new.

## 11. Validation

Evaluate the design against the original Jolla icons, preferably using the actual SVGs from the official icon library.

### Visual review

- Does the icon belong naturally among the original Jolla applications?
- Does its base shape support its visual metaphor?
- Is the primary motif recognizable at launcher size?
- Are the visual proportions balanced?
- Do color and layering reinforce the composition?
- Does the icon have its own identity without becoming stylistically disconnected?

### Technical review

- Does the SVG render correctly?
- Is the official silhouette preserved?
- Are all foreground elements genuine vectors?
- Are intersections and overlapping regions correct?
- Are there unintended gaps, seams or clipping artifacts?
- Do exported PNGs accurately reflect the SVG?
- Does the asset work with the target Sailfish packaging pipeline?
- Has the maintainer seen it in the launcher on a device?

### Review principle

**Do not approve a design solely because it looks attractive at high resolution.**

Inspect it at actual launcher size and alongside original Jolla icons.

## 12. Expected deliverables

1. **Editable SVG source** based on an official Sailfish template.
2. **Launcher-size PNG** rendered from that SVG.
3. **High-resolution PNG** rendered from the same SVG.
4. **Brief design rationale** identifying the selected base shape, visual metaphor and color relationships.
5. **Technical validation notes** confirming SVG integrity and packaging compatibility.

The SVG must exist from the first meaningful design iteration and remain the source of truth throughout.

## 13. Guiding design philosophy

The original Jolla icon language should not be reduced to a checklist of flat colors, uniform borders or geometric primitives.

Its distinctive quality lies in the combination of a flexible shape system, meaningful visual metaphors, aesthetic balance and individual expression.

The goal is to create an icon that feels naturally part of the original Jolla family while retaining its own character.

**Use the official shape system as the foundation. Let the visual metaphor determine the composition. Apply color and layering with purpose. Preserve the design as genuine vector geometry from the beginning.**

