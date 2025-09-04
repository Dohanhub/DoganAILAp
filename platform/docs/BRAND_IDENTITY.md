
# ScenarioKit - Brand Identity Guide

## 🎨 Brand Overview

**ScenarioKit** by **DoganAI Lab** is the premier AI platform for the Kingdom of Saudi Arabia, delivering enterprise-grade artificial intelligence solutions with full regulatory compliance and Arabic-first design.

---

## 🎯 Brand Positioning

### Primary Brand Statement
*"Advanced AI Research & Deployment Platform"*  
*معمل دوغان للذكاء الاصطناعي - منصة البحث والنشر المتقدمة للذكاء الاصطناعي*

### Core Value Proposition
Empowering KSA's digital transformation through cutting-edge AI technology with full regulatory compliance, Arabic language support, and enterprise-grade security.

---

## 🌈 Color Palette

### Primary Colors
- **Deep Blue**: `#1e3a8a` (Primary brand color)
- **Royal Purple**: `#7c3aed` (Secondary accent)
- **Saudi Green**: `#059669` (KSA heritage color)
- **Gold Accent**: `#d97706` (Premium highlight)

### Gradient Combinations
- **Hero Gradient**: `linear-gradient(135deg, #1e3a8a 0%, #7c3aed 100%)`
- **Success Gradient**: `linear-gradient(135deg, #059669 0%, #10b981 100%)`
- **Warning Gradient**: `linear-gradient(135deg, #d97706 0%, #f59e0b 100%)`

### Neutral Colors
- **Dark Text**: `#1f2937` (Primary text)
- **Medium Gray**: `#6b7280` (Secondary text)
- **Light Gray**: `#f3f4f6` (Background)
- **White**: `#ffffff` (Cards/containers)

### Status Colors
- **Success**: `#10b981` (Completed scenarios)
- **Warning**: `#f59e0b` (In progress)
- **Error**: `#ef4444` (Failed operations)
- **Info**: `#3b82f6` (Information)

---

## 🔤 Typography

### Primary Font Family
**Inter** - Modern, clean, and highly readable
- Supports Arabic and English
- Excellent for digital interfaces
- Professional appearance

### Font Weights
- **Light**: 300 (Large headings)
- **Regular**: 400 (Body text)
- **Medium**: 500 (Subheadings)
- **Semibold**: 600 (Important text)
- **Bold**: 700 (Emphasis)

### Arabic Typography
**Cairo** or **Tajawal** for Arabic content
- Right-to-left (RTL) layout support
- Cultural authenticity
- High readability

---

## 🎭 Logo & Visual Identity

### Logo Concepts
1. **Gear Icon** with AI neural network overlay
2. **Hexagonal pattern** representing molecular/data structures
3. **Crescents and circuits** blending traditional and modern elements
4. **Compass rose** pointing toward digital transformation

### Logo Variations
- **Full Logo**: ScenarioKit + DoganAI Lab wordmark
- **Icon Only**: Standalone symbol for small spaces
- **Horizontal**: Wide layout for headers
- **Stacked**: Vertical layout for square spaces

### Logo Colors
- **Primary**: Deep Blue (`#1e3a8a`) on white
- **Reversed**: White on Deep Blue background
- **Monochrome**: Black for print/single color
- **Gradient**: Blue to Purple for digital

---

## 🎨 Visual Elements

### Icons & Symbols
- **Scenarios**: Hexagonal badges with industry symbols
- **AI Processing**: Animated neural network connections
- **Compliance**: Shield icons with checkmarks
- **Arabic Support**: Crescent moon integration
- **KSA Elements**: Palm tree silhouettes, traditional patterns

### Patterns & Textures
- **Circuit Board**: Subtle background patterns
- **Geometric**: Islamic-inspired mathematical patterns
- **Gradient Mesh**: Modern digital overlays
- **Grid System**: Clean, organized layouts

### Imagery Style
- **Photography**: Professional, diverse, technology-focused
- **Illustrations**: Flat design with subtle depth
- **Icons**: Outlined style with optional fills
- **Graphics**: Clean, modern, purposeful

---

## 📱 Digital Brand Applications

### Mobile App Design
```css
/* Primary Theme */
.primary-theme {
  background: linear-gradient(135deg, #1e3a8a 0%, #7c3aed 100%);
  color: #ffffff;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(30, 58, 138, 0.3);
}

/* Card Design */
.scenario-card {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

/* Arabic Support */
.rtl-layout {
  direction: rtl;
  text-align: right;
  font-family: 'Cairo', 'Tajawal', sans-serif;
}
```

### Web Platform Style
```css
/* Header Navigation */
.main-header {
  background: #1e3a8a;
  color: #ffffff;
  padding: 16px 32px;
  box-shadow: 0 2px 8px rgba(30, 58, 138, 0.2);
}

/* Dashboard Cards */
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 24px;
  padding: 32px;
}

/* Status Indicators */
.status-complete { color: #10b981; }
.status-progress { color: #f59e0b; }
.status-error { color: #ef4444; }
```

---

## 🌍 Cultural Considerations

### KSA Market Adaptation
- **Color Sensitivity**: Avoid inappropriate color combinations
- **Religious Respect**: No imagery conflicting with Islamic values
- **Cultural Symbols**: Incorporate Saudi heritage elements respectfully
- **Language Priority**: Arabic-first design with English secondary

### Regional Elements
- **Traditional Patterns**: Geometric Islamic art inspiration
- **Modern Fusion**: Blend traditional with cutting-edge technology
- **National Pride**: Subtle Saudi flag color integration
- **Professional Tone**: Respectful, authoritative, trustworthy

---

## 🎪 Brand Voice & Tone

### Voice Characteristics
- **Professional**: Expert knowledge and authority
- **Innovative**: Forward-thinking and cutting-edge
- **Trustworthy**: Reliable and compliant
- **Accessible**: Clear communication without jargon
- **Respectful**: Cultural sensitivity and inclusion

### Tone Variations
- **Technical Documentation**: Precise, detailed, instructional
- **Marketing Content**: Engaging, benefit-focused, inspiring
- **User Interface**: Helpful, guiding, encouraging
- **Executive Communications**: Strategic, results-oriented, professional

### Key Messaging
- "Transforming KSA through AI innovation"
- "العربية أولاً، الامتثال دائماً" (Arabic first, compliance always)
- "From research to production"
- "Enterprise-grade AI for the Kingdom"

---

## 📐 Layout & Spacing

### Grid System
- **Base Unit**: 8px
- **Container**: 1200px max-width
- **Margins**: 16px mobile, 32px desktop
- **Gutters**: 24px between columns

### Component Spacing
- **Tight**: 8px (related elements)
- **Normal**: 16px (standard spacing)
- **Loose**: 24px (section separation)
- **Extra Loose**: 32px+ (major sections)

---

## 🔧 Implementation Guidelines

### Design System
```css
/* CSS Custom Properties */
:root {
  /* Colors */
  --primary-blue: #1e3a8a;
  --secondary-purple: #7c3aed;
  --saudi-green: #059669;
  --gold-accent: #d97706;
  
  /* Typography */
  --font-primary: 'Inter', sans-serif;
  --font-arabic: 'Cairo', 'Tajawal', sans-serif;
  
  /* Spacing */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;
  
  /* Borders */
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
}
```

### Responsive Breakpoints
- **Mobile**: 320px - 767px
- **Tablet**: 768px - 1023px
- **Desktop**: 1024px - 1439px
- **Large**: 1440px+

---

## 📊 Brand Metrics & KPIs

### Brand Recognition
- Logo recognition rate: >80%
- Brand association with AI/KSA: >90%
- Trust rating: >4.5/5.0

### Digital Presence
- Website bounce rate: <25%
- Mobile app rating: >4.7/5.0
- Social media engagement: >5%

### Market Position
- Market share in KSA AI: Target 15%
- Enterprise adoption rate: >60%
- Regulatory compliance score: 100%

---

## ✅ Brand Checklist

### Every Design Must Include:
- [ ] Appropriate color palette usage
- [ ] Consistent typography
- [ ] Arabic language support (RTL)
- [ ] Cultural sensitivity review
- [ ] Mobile-responsive design
- [ ] Accessibility compliance (WCAG 2.1)
- [ ] Brand voice consistency
- [ ] Legal/regulatory compliance

### Quality Standards:
- [ ] High contrast ratios (4.5:1 minimum)
- [ ] Scalable vector graphics
- [ ] Cross-platform compatibility
- [ ] Performance optimization
- [ ] Security considerations

---

*This brand identity guide ensures consistent, professional, and culturally appropriate representation of ScenarioKit across all touchpoints and markets.*
