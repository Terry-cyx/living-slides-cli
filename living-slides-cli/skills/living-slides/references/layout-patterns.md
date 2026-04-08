# Layout Patterns

20 proven slide layouts. Pick the one that matches the content type.

## Layout Selection Matrix

| Content Type | Use Layout | Focal Rule |
|-------------|-----------|-----------|
| Opening / Section divider | Hero | Oversized title |
| Big insight / headline metric | Big Number | Single number ≥ 120px |
| 3-4 features | Grid-3 or Grid-4 | Icon + label + desc |
| KPI dashboard | Metrics-4 | Number + label cards |
| Compare 2 options | Split | 50/50 vertical split |
| Timeline / process | Horizontal Flow | Numbered steps + arrows |
| Data trend | Chart-Focus | Chart 60%, text 40% |
| Data comparison | Bar/Column Chart | No pie unless 2-5 clear segments |
| Customer quote | Quote | Huge quotes + attribution |
| Team introduction | Card Grid | Photo + name + title |
| Pricing | Pricing-3 | 3 cards, middle highlighted |
| Architecture / system | Diagram | Boxes + arrows with labels |
| Full-image / brand moment | Full Bleed | Image + gradient overlay |
| Call to action / closing | CTA | Headline + action button |
| Q&A / end | Minimal | Large text, lots of space |
| Agenda / TOC | Numbered List | 3-6 items, numbered |
| Problem statement | Hero Minimal | Problem in large text, red accent |
| Solution reveal | Split with Visual | Text left, visual right |
| Comparison matrix | Feature Table | Checkmarks/Xs in grid |
| Traction / growth | Chart + Metrics | Line chart + 2-3 callouts |

---

## 1. Hero (Title Slide)

```html
<section class="slide layout-hero">
    <div class="slide-header">
        <span class="eyebrow">ACME INC</span>
        <span class="eyebrow">APRIL 2026</span>
    </div>
    <div class="slide-body">
        <h1 class="slide-title animate-in" style="font-size: var(--text-5xl); max-width: 18ch;">
            The biggest shift in AI presentations since PowerPoint
        </h1>
        <p class="subtitle animate-in">How living-slides lets you edit AI-generated decks visually</p>
    </div>
    <div class="slide-footer">
        <span>by Terry</span>
        <span>1</span>
    </div>
</section>
```

**Rules**: Title fills upper-left 70%. Subtitle 1 line max. No decorative elements.

## 2. Big Number

```html
<section class="slide">
    <div class="slide-header">
        <span class="eyebrow">TRACTION</span>
    </div>
    <div class="slide-body" style="justify-content: center; align-items: center; text-align: center;">
        <div class="animate-in" style="font-size: 240px; font-weight: 900; line-height: 1; background: linear-gradient(135deg, var(--color-primary), var(--color-accent)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: var(--tracking-tight);">
            10,000+
        </div>
        <p class="animate-in" style="font-size: var(--text-xl); color: var(--color-fg-muted); margin-top: var(--s-4);">
            Active users in first 6 months
        </p>
    </div>
    <div class="slide-footer"><span></span><span>3</span></div>
</section>
```

**Rules**: Single number, 180-240px font size. Max 1 line of supporting text below.

## 3. Feature Grid (3 columns)

```html
<section class="slide">
    <div class="slide-header"><span class="eyebrow">WHAT WE BUILT</span></div>
    <div class="slide-body">
        <h2 class="slide-title animate-in">Three pillars of our platform</h2>
        <div class="layout-grid-3">
            <div class="card animate-in">
                <div style="font-size: var(--text-xl); margin-bottom: var(--s-2);">🚀</div>
                <h3>Fast Deploy</h3>
                <p style="font-size: var(--text-sm);">Ship in seconds, not hours</p>
            </div>
            <div class="card animate-in">
                <div style="font-size: var(--text-xl); margin-bottom: var(--s-2);">🔒</div>
                <h3>Enterprise Security</h3>
                <p style="font-size: var(--text-sm);">SOC 2 Type II certified</p>
            </div>
            <div class="card animate-in">
                <div style="font-size: var(--text-xl); margin-bottom: var(--s-2);">📊</div>
                <h3>Real-time Analytics</h3>
                <p style="font-size: var(--text-sm);">Live data, instant insights</p>
            </div>
        </div>
    </div>
    <div class="slide-footer"><span></span><span>4</span></div>
</section>
```

**Rules**: 3 cards only (not 4). Each card: icon (1 line) → h3 (1 line) → description (1-2 lines).

## 4. Metrics Dashboard (4 columns)

```html
<section class="slide">
    <div class="slide-header"><span class="eyebrow">Q1 RESULTS</span></div>
    <div class="slide-body">
        <h2 class="slide-title animate-in">Revenue up 42% year-over-year</h2>
        <div class="layout-grid-4">
            <div class="card card-metric animate-in">
                <div class="value">$2.4M</div>
                <div class="label">Revenue</div>
            </div>
            <div class="card card-metric animate-in">
                <div class="value">+42%</div>
                <div class="label">YoY Growth</div>
            </div>
            <div class="card card-metric animate-in">
                <div class="value">94</div>
                <div class="label">NPS Score</div>
            </div>
            <div class="card card-metric animate-in">
                <div class="value">1.8%</div>
                <div class="label">Churn</div>
            </div>
        </div>
    </div>
    <div class="slide-footer"><span></span><span>5</span></div>
</section>
```

**Rules**: ALWAYS lead with an insight headline, not "Q1 Metrics". 4 cards max. Use gradient text for numbers.

## 5. Split (Two Column)

```html
<section class="slide">
    <div class="slide-header"><span class="eyebrow">PROBLEM</span></div>
    <div class="slide-body layout-split">
        <div class="animate-in">
            <h2 class="slide-title">The old way is broken</h2>
            <p style="margin-top: var(--s-3);">PowerPoint takes hours to design, can't be version-controlled, and AI can't generate it natively.</p>
        </div>
        <div class="animate-in" style="background: var(--color-bg-elevated); border: 1px solid var(--color-border); border-radius: var(--radius-xl); padding: var(--s-5); aspect-ratio: 4/3;">
            <!-- Visual, screenshot, or chart -->
        </div>
    </div>
    <div class="slide-footer"><span></span><span>6</span></div>
</section>
```

**Rules**: 50/50 or 40/60. Text on one side, visual on the other. NEVER text on both sides.

## 6. Quote / Testimonial

```html
<section class="slide">
    <div class="slide-header"><span class="eyebrow">CUSTOMER VOICE</span></div>
    <div class="slide-body" style="justify-content: center; padding: 0 var(--s-7);">
        <div style="position: absolute; top: var(--s-6); left: var(--s-7); font-size: 200px; color: var(--color-primary); opacity: 0.2; line-height: 1; font-family: Georgia, serif;">"</div>
        <blockquote class="animate-in" style="font-size: var(--text-2xl); font-weight: 500; line-height: var(--lh-snug); max-width: 24ch; position: relative; z-index: 1;">
            living-slides changed how our marketing team works with AI.
        </blockquote>
        <div class="animate-in" style="margin-top: var(--s-5); display: flex; align-items: center; gap: var(--s-3);">
            <div style="width: 48px; height: 48px; border-radius: 50%; background: var(--color-primary);"></div>
            <div>
                <div style="font-weight: 600;">Sarah Chen</div>
                <div style="color: var(--color-fg-subtle); font-size: var(--text-sm);">CMO, TechCorp</div>
            </div>
        </div>
    </div>
    <div class="slide-footer"><span></span><span>7</span></div>
</section>
```

**Rules**: Quote ≤ 24 characters per line. Decorative " mark behind. Attribution small.

## 7. Pricing (3 tiers)

```html
<section class="slide">
    <div class="slide-header"><span class="eyebrow">PRICING</span></div>
    <div class="slide-body">
        <h2 class="slide-title animate-in">Simple, transparent pricing</h2>
        <div class="layout-grid-3" style="align-items: stretch;">
            <!-- Tier 1 -->
            <div class="card animate-in">
                <h3>Basic</h3>
                <div style="font-size: var(--text-3xl); font-weight: 800; margin: var(--s-3) 0;">$9<span style="font-size: var(--text-base); color: var(--color-fg-muted);">/mo</span></div>
                <ul style="list-style: none; display: flex; flex-direction: column; gap: var(--s-2); font-size: var(--text-sm);">
                    <li>✓ 10 decks/month</li>
                    <li>✓ Basic templates</li>
                    <li>✓ Email support</li>
                </ul>
            </div>
            <!-- Tier 2 (HIGHLIGHTED) -->
            <div class="card animate-in" style="border-color: var(--color-primary); transform: scale(1.05); position: relative; box-shadow: var(--shadow-md), 0 0 0 1px var(--color-primary);">
                <div style="position: absolute; top: -12px; left: 50%; transform: translateX(-50%); background: var(--color-primary); color: white; font-size: var(--text-xs); padding: 4px 12px; border-radius: var(--radius-full); font-weight: 600;">MOST POPULAR</div>
                <h3>Pro</h3>
                <div style="font-size: var(--text-3xl); font-weight: 800; margin: var(--s-3) 0;">$29<span style="font-size: var(--text-base); color: var(--color-fg-muted);">/mo</span></div>
                <ul style="list-style: none; display: flex; flex-direction: column; gap: var(--s-2); font-size: var(--text-sm);">
                    <li>✓ Unlimited decks</li>
                    <li>✓ All templates</li>
                    <li>✓ AI refinement</li>
                    <li>✓ Priority support</li>
                </ul>
            </div>
            <!-- Tier 3 -->
            <div class="card animate-in">
                <h3>Enterprise</h3>
                <div style="font-size: var(--text-3xl); font-weight: 800; margin: var(--s-3) 0;">Custom</div>
                <ul style="list-style: none; display: flex; flex-direction: column; gap: var(--s-2); font-size: var(--text-sm);">
                    <li>✓ Everything in Pro</li>
                    <li>✓ SSO / SAML</li>
                    <li>✓ Dedicated CSM</li>
                    <li>✓ SLA guarantees</li>
                </ul>
            </div>
        </div>
    </div>
    <div class="slide-footer"><span></span><span>8</span></div>
</section>
```

**Rules**: 3 tiers only. Middle one highlighted (scale 1.05 + primary border + badge). Parallel feature lists.

## 8. Comparison Matrix

```html
<section class="slide">
    <div class="slide-header"><span class="eyebrow">VS. COMPETITION</span></div>
    <div class="slide-body">
        <h2 class="slide-title animate-in">Only living-slides delivers all four</h2>
        <table class="animate-in" style="width: 100%; border-collapse: collapse; margin-top: var(--s-3);">
            <thead>
                <tr>
                    <th style="text-align: left; padding: var(--s-2); font-size: var(--text-sm); color: var(--color-fg-subtle); font-weight: 600;">Feature</th>
                    <th style="padding: var(--s-2); font-size: var(--text-sm); color: var(--color-primary); font-weight: 700;">living-slides</th>
                    <th style="padding: var(--s-2); font-size: var(--text-sm); color: var(--color-fg-subtle);">PowerPoint</th>
                    <th style="padding: var(--s-2); font-size: var(--text-sm); color: var(--color-fg-subtle);">Gamma</th>
                </tr>
            </thead>
            <tbody>
                <tr style="border-top: 1px solid var(--color-border);">
                    <td style="padding: var(--s-3) var(--s-2); font-size: var(--text-base);">AI-native generation</td>
                    <td style="text-align: center; color: var(--color-success);">✓</td>
                    <td style="text-align: center; color: var(--color-error);">✗</td>
                    <td style="text-align: center; color: var(--color-success);">✓</td>
                </tr>
                <!-- More rows -->
            </tbody>
        </table>
    </div>
    <div class="slide-footer"><span></span><span>9</span></div>
</section>
```

**Rules**: Max 6 rows. Put your product in a highlighted column. Use ✓ / ✗, not text.

## 9. Chart Focus

```html
<section class="slide">
    <div class="slide-header"><span class="eyebrow">GROWTH</span></div>
    <div class="slide-body">
        <h2 class="slide-title animate-in">Revenue tripled in 6 months</h2>
        <div class="animate-in" style="flex: 1; position: relative; margin-top: var(--s-3);">
            <canvas id="growthChart"></canvas>
        </div>
    </div>
    <div class="slide-footer">
        <span style="font-size: var(--text-xs);">Source: Internal analytics, Q4 2025</span>
        <span>10</span>
    </div>
</section>
```

**Rules**: Chart fills 60-70% of slide. Headline states the insight, not the topic. Source citation in footer.

## 10. CTA Closing

```html
<section class="slide">
    <div class="slide-header"><span class="eyebrow">NEXT STEPS</span></div>
    <div class="slide-body" style="justify-content: center; align-items: flex-start; gap: var(--s-5);">
        <h2 class="slide-title animate-in" style="font-size: var(--text-4xl); max-width: 18ch;">
            Ready to try living-slides?
        </h2>
        <div class="animate-in" style="display: flex; gap: var(--s-3);">
            <button style="background: var(--color-primary); color: white; border: none; padding: var(--s-3) var(--s-5); font-size: var(--text-base); font-weight: 600; border-radius: var(--radius-full); cursor: pointer;">
                Start Free Trial →
            </button>
            <button style="background: transparent; color: var(--color-fg); border: 1px solid var(--color-border); padding: var(--s-3) var(--s-5); font-size: var(--text-base); font-weight: 600; border-radius: var(--radius-full); cursor: pointer;">
                Book Demo
            </button>
        </div>
        <p class="animate-in" style="font-size: var(--text-sm); color: var(--color-fg-subtle); margin-top: var(--s-3);">
            hello@living-slides.com · github.com/Terry-cyx/living-slides
        </p>
    </div>
    <div class="slide-footer"><span></span><span>11</span></div>
</section>
```

**Rules**: One primary CTA, one secondary. Contact info in footnote. No walls of text.

---

## Anti-Patterns (Never Do)

- ❌ Centered paragraphs longer than 2 lines
- ❌ Title + 7+ bullets
- ❌ 5 columns of content (4 is the max)
- ❌ Pie chart with >5 slices
- ❌ Multiple competing focal points
- ❌ Background image + content without overlay
- ❌ Decorative elements larger than content elements
- ❌ Icons used decoratively (only functional icons with meaning)
