# Future Work & Research Areas

This document tracks planned features and research directions for the synthesizer platform.

## 1. Other Instrument Synthesis

### Wind Instruments

**Goal**: Implement physical modeling synthesis for wind instruments (brass, woodwinds)

**Instruments to support:**

- Brass: Trumpet, Trombone, French Horn, Tuba
- Woodwinds: Flute, Clarinet, Saxophone, Oboe, Bassoon

**Approach**: Likely using waveguide synthesis or similar physical modeling techniques

**Status**: Research phase - gathering references

---

### Percussion Instruments

**Goal**: Implement synthesis for both tuned and untuned percussion

**Instruments to support:**

- Tuned: Xylophone, Marimba, Vibraphone, Timpani
- Untuned: Kick, Snare, Toms, Cymbals, Hi-Hat

**Approach**: Modal synthesis or sample-based with physical modeling for resonance

**Status**: Research phase - gathering references

---

## 2. Custom DSP Solutions

**Goal**: Implement advanced audio processing and effects

**Areas to explore:**

- **Effects Processing**: Reverb, delay, chorus, flanger, phaser
- **Filtering**: Low-pass, high-pass, band-pass, notch filters
- **Dynamics**: Compression, limiting, expansion, gating
- **Spatial Audio**: 3D positioning, HRTF, binaural processing
- **Time-stretching & Pitch-shifting**: Without quality loss
- **Spectral Processing**: FFT-based effects, vocoders

**Current tools**: Using NumPy, SciPy, Pedalboard

**Status**: Research phase - exploring DSP fundamentals and implementation strategies

---

## 3. Research - Music Synthesis Fundamentals

**Goal**: Deep dive into theoretical foundations of music synthesis

**Research areas:**

- **Physical Modeling Theory**: Mass-spring systems, wave equations, resonance
- **Signal Processing Fundamentals**: Fourier analysis, convolution, filtering theory
- **Psychoacoustics**: How humans perceive sound, timbre, pitch
- **Synthesis Techniques**: Additive, subtractive, FM, granular, wavetable
- **Novel Approaches**: Machine learning for synthesis, neural audio synthesis

**Status**: Ongoing research - collecting papers, books, and experimental implementations

---

## References

### Current Implementation

- **String Synthesis**: [Real Python - Python Guitar Synthesizer](https://realpython.com/python-guitar-synthesizer/)
  - Karplus-Strong algorithm for plucked strings
  - Implementation: `tools/synthesis/physical_modeling/karplus_strong.py`

### To Be Added

See sections above for specific instrument categories and DSP areas.

---

## Database Structure Readiness

The current database schema is designed to support all instrument types:

```
Song (metadata: genre, mood, timing)
└── Track (instrument_category: strings/winds/percussion/keyboards/vocal)
    └── Measure
        └── Event (polymorphic event_data JSON)
```

**Instrument categories supported:**

- `strings` - Currently implemented
- `winds` - Ready for implementation
- `percussion` - Ready for implementation
- `keyboards` - Ready for implementation
- `vocal` - Ready for implementation

Each category can have custom `instrument_config` and `event_data` formats.
