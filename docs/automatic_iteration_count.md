# Automatic Iteration Count — Full Derivation

Two quantities need to be derived from scratch:

1. **The shrink factor $s$** — how much the circumradius scales down per transformation step
2. **The epsilon threshold $\varepsilon/R$** — when the innermost polygon is visually indistinguishable

Once both are in hand, the required iteration count falls out of a single logarithm.

---

## Part 1 — The Shrink Factor

### Setup

Place a regular $n$-gon centered at the origin with circumradius $R$. Two adjacent vertices sit at angles $\varphi$ and $\varphi + 2\pi/n$:

$$p_1 = R \begin{pmatrix} \cos\varphi \\ \sin\varphi \end{pmatrix}, \qquad p_2 = R \begin{pmatrix} \cos(\varphi + 2\pi/n) \\ \sin(\varphi + 2\pi/n) \end{pmatrix}$$

### One transformation step

`transform_polygon` moves every vertex a fraction $t$ of the way toward the next:

$$p' = (1-t)\, p_1 + t\, p_2$$

The new circumradius is $R' = |p'|$. Expanding $|p'|^2$:

$$|p'|^2 = |(1-t)\,p_1 + t\,p_2|^2 = (1-t)^2|p_1|^2 + 2t(1-t)\,(p_1 \cdot p_2) + t^2|p_2|^2$$

### Substituting known quantities

Both vertices lie on the circumcircle, so $|p_1|^2 = |p_2|^2 = R^2$.

The dot product between them:

$$p_1 \cdot p_2 = R^2 \cos\!\left(\frac{2\pi}{n}\right)$$

Substituting:

$$|p'|^2 = R^2\!\left[(1-t)^2 + 2t(1-t)\cos\!\left(\tfrac{2\pi}{n}\right) + t^2\right]$$

### Simplifying the bracket

Expand $(1-t)^2 + t^2$:

$$(1-t)^2 + t^2 = 1 - 2t + 2t^2 = 1 - 2t(1-t)$$

So the bracket becomes:

$$1 - 2t(1-t) + 2t(1-t)\cos\!\left(\tfrac{2\pi}{n}\right) = 1 - 2t(1-t)\!\left(1 - \cos\tfrac{2\pi}{n}\right)$$

### The shrink factor

$$R' = R\,\sqrt{1 - 2t(1-t)\!\left(1 - \cos\tfrac{2\pi}{n}\right)}$$

Therefore:

$$\boxed{s = \frac{R'}{R} = \sqrt{1 - 2t(1-t)\!\left(1 - \cos\tfrac{2\pi}{n}\right)}}$$

Since $1 - \cos(2\pi/n) > 0$ for all $n \geq 3$, and $2t(1-t) > 0$ for $t \in (0,1)$, the radicand is always strictly less than $1$, so $s < 1$ always. The polygon strictly shrinks with every step.

### After $k$ steps

$$R_k = R \cdot s^k$$

### Sanity check

Square ($n = 4$), $t = 0.5$:

$$s = \sqrt{1 - 2 \cdot 0.5 \cdot 0.5 \cdot \left(1 - \cos\tfrac{\pi}{2}\right)} = \sqrt{1 - 0.5 \cdot 1} = \sqrt{0.5} = \frac{1}{\sqrt{2}} \approx 0.707$$

Bisecting a square's sides produces a square rotated $45°$ and scaled by $1/\sqrt{2}$. ✓

### Implementation

```python
def shrink_factor(n: int, t: float) -> float:
    angle = 2 * math.pi / n
    return math.sqrt(1 - 2*t*(1-t)*(1 - math.cos(angle)))
```

---

## Part 2 — The Epsilon Threshold

The iteration should stop the moment the innermost polygon becomes visually
indistinguishable. The criterion: when the circumradius of the innermost polygon
drops below **half the line width** in data-space. At that point the stroke itself
is wider than the shape it traces, and further iterations are invisible.

### Step 1 — figure size in pixels

$$w_{px} = w_{in} \cdot \text{dpi}, \qquad h_{px} = h_{in} \cdot \text{dpi}$$

```python
width  = figure_width  * dpi
height = figure_height * dpi
```

`dpi` is a software quantity — pixels allocated per inch in the rendered buffer.
It has nothing to do with the physical PPI of the display. We are reasoning about
the rendered pixel buffer, not the physical screen. `figure_width`/`figure_height`
are plain numbers here, not a constructed Figure — nothing below needs a live
Matplotlib object.

### Step 2 — axes area in pixels

$$w_{ax} = w_{px} \cdot b_w, \qquad h_{ax} = h_{px} \cdot b_h$$

where $b_w,\, b_h$ are the axes width and height fractions from Matplotlib's
default subplot layout.

```python
axes_width_fraction = (
    plt.rcParams["figure.subplot.right"] - plt.rcParams["figure.subplot.left"]
)
axes_height_fraction = (
    plt.rcParams["figure.subplot.top"] - plt.rcParams["figure.subplot.bottom"]
)
axes_width  = width  * axes_width_fraction
axes_height = height * axes_height_fraction
```

Reading `plt.rcParams` directly (instead of a constructed Axes' `get_position()`)
gives the same fractions `plt.subplots()` would produce with no custom layout
adjustments — which is all `render_polygons` ever does — but without needing a
Figure/Axes to exist yet. So this entire derivation can be evaluated **before
any figure is created at all**, not merely before a polygon is drawn.

### Step 3 — line width in pixels

Matplotlib specifies `linewidth` in **points**, where $1\,\text{pt} = \tfrac{1}{72}\,\text{in}$.
Converting to pixels:

$$\ell_{px} = \frac{\text{linewidth}}{72} \cdot \text{dpi}$$

```python
lw_pixels = (linewidth * dpi) / 72
```

### Step 4 — half the line width in pixels

The stroke extends $\ell_{px}/2$ pixels on each side of the mathematical edge.
The polygon becomes invisible when its circumradius in pixels is smaller than that half-width:

$$\varepsilon_{px} = \frac{\ell_{px}}{2}$$

```python
eps_pixels = lw_pixels / 2
```

### Step 5 — one pixel in data-space

The starting polygon has circumradius $R$, centered at the origin, spanning $2R$
across both axes. One pixel in data-space is therefore:

$$\delta = \frac{2R}{\min(w_{ax},\, h_{ax})}$$

We take the minimum to use the coarser axis — the conservative choice.

### Step 6 — $\varepsilon$ in data-space

$$\varepsilon = \varepsilon_{px} \cdot \delta = \frac{\ell_{px}}{2} \cdot \frac{2R}{\min(w_{ax},\, h_{ax})}$$

### Step 7 — $\varepsilon/R$ and the cancellation of $R$

Dividing both sides by $R$:

$$\frac{\varepsilon}{R} = \frac{\ell_{px}}{2} \cdot \frac{2}{\min(w_{ax},\, h_{ax})} = \frac{\ell_{px}}{\min(w_{ax},\, h_{ax})}$$

$$\boxed{\frac{\varepsilon}{R} = \frac{\ell_{px}}{\min(w_{ax},\, h_{ax})}}$$

$R$ cancels completely. The threshold depends only on figure geometry and line width.
Scaling the polygon up or down changes the axis limits proportionally, so the pixel
journey from full size to invisible is always the same length.

```python
eps_over_R = (lw_pixels / 2) * (2.0 / min(axes_width, axes_height))
```

### Step 8 — solving for $k$

Everything up to here (Steps 1–7) is Matplotlib-specific — it's the only part
that needs to know about figure size, DPI, or line width in points. This step
isn't: given $\varepsilon/R$ from *any* source, the iteration count follows
from `shrink_factor` alone. That's why it lives as its own backend-agnostic
function rather than being fused into the pixel-geometry code above — a
different rendering backend only needs to supply its own $\varepsilon/R$ and
can reuse this step unchanged.

We want the smallest $k$ such that $s^k \leq \varepsilon/R$:

$$s^k \leq \frac{\varepsilon}{R}$$

Taking logarithms of both sides:

$$k \cdot \log s \leq \log\!\left(\frac{\varepsilon}{R}\right)$$

Since $\log s < 0$ (because $s < 1$), dividing flips the inequality:

$$k \geq \frac{\log(\varepsilon/R)}{\log s}$$

Both $\log(\varepsilon/R)$ and $\log s$ are negative, so their ratio is positive.
Taking the ceiling gives the smallest valid integer:

$$\boxed{k = \left\lceil \frac{\log(\varepsilon/R)}{\log s} \right\rceil}$$

```python
s = shrink_factor(n, t)
return math.ceil(math.log(eps_over_R) / math.log(s))
```

### Full implementation

Split across two functions, matching the Matplotlib-specific/backend-agnostic
boundary from Step 8: `matplotlib_eps_over_r` (`itero.plotting._matplotlib`)
does Steps 1–7, `iterations_until_imperceptible` (`itero.plotting`, no
Matplotlib import at all) does Step 8.

```python
def matplotlib_eps_over_r(
    figure_width: float, figure_height: float,
    dpi: float = 100.0, linewidth: float = 1.5,
) -> float:
    width  = figure_width  * dpi
    height = figure_height * dpi

    axes_width_fraction = (
        plt.rcParams["figure.subplot.right"] - plt.rcParams["figure.subplot.left"]
    )
    axes_height_fraction = (
        plt.rcParams["figure.subplot.top"] - plt.rcParams["figure.subplot.bottom"]
    )
    axes_width  = width  * axes_width_fraction
    axes_height = height * axes_height_fraction

    lw_pixels  = (linewidth * dpi) / 72
    eps_pixels = lw_pixels / 2
    return eps_pixels * 2 / min(axes_width, axes_height)


def iterations_until_imperceptible(n: int, t: float, eps_over_r: float) -> int:
    s = shrink_factor(n, t)
    return math.ceil(math.log(eps_over_r) / math.log(s))
```

---

## Putting it all together

```python
eps_over_r = matplotlib_eps_over_r(*figure_size, linewidth=1.5)
k          = iterations_until_imperceptible(n=5, t=0.2, eps_over_r=eps_over_r)
sequence   = iterate_polygon(Polygon.regular(5), t=0.2, iterations=k)

fig = render_polygons(sequence, figure_size, ...)
```

The iteration count is derived analytically from plain figure parameters —
no figure needs to exist yet to compute it. `render_polygons` only builds and
populates a figure once `k` (and every other input) is already known-good, in
a single step. No test renders, no magic constants, no guessing, and no
orphaned figure if something upstream turns out to be invalid.