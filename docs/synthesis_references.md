# Synthesis References & Learning Resources

Comprehensive collection of resources for implementing various instrument synthesis techniques.

---

## Current Implementation

### String Instruments (Implemented)

- **[Real Python - Python Guitar Synthesizer](https://realpython.com/python-guitar-synthesizer/)**
  - Karplus-Strong algorithm for plucked strings
  - Complete Python implementation with NumPy
  - Our implementation: `tools/synthesis/physical_modeling/karplus_strong.py`

---

## Wind Instruments

### Python Libraries

- **[OpenWind](https://openwind.inria.fr/)** - INRIA's Python library for wind instrument acoustics

  - Frequential and temporal simulations for wind musical instruments
  - Computes sound by coupling reed/lips to pipe entry
  - State-of-the-art computation framework for academics and makers
  - Open source Python module

- **[Flute Physical Modelling (GitHub)](https://github.com/nbrochec/flute-physical-modelling)**
  - Jupyter notebooks for flute physical modeling
  - Python implementation of flute behavior and sound
  - Covers physical components and interactions

### Theory & Techniques

- **[Physical Modelling Synthesis - Stanford CCRMA](https://ccrma.stanford.edu/software/clm/compmus/clm-tutorials/pm.html)**

  - Tutorial on physical modeling fundamentals
  - Waveguide synthesis concepts
  - Applications to wind instruments

- **[Digital Waveguide Modeling for Wind Instruments (ResearchGate)](https://www.researchgate.net/publication/224130816_Digital_Waveguide_Modeling_for_Wind_Instruments_Building_a_State-Space_Representation_Based_on_the_Webster-Lokshin_Model)**

  - Academic paper on waveguide techniques
  - Webster-Lokshin model for wind instrument bore
  - State-space representation

- **[Synthesizing Simple Flutes - Sound on Sound](https://www.soundonsound.com/techniques/synthesizing-simple-flutes)**

  - Practical tutorial for flute synthesis
  - Subtractive synthesis approach

- **[Pan Flute Modeling](https://sound.eti.pg.gda.pl/student/eim/synteza/zwan/index_eng.htm)**

  - Specific to pan flute implementation

- **[NESS - Brass Instruments](http://www www.ness.music.ed.ac.uk/archives/systems/brass-instruments-2)**
  - Next Generation Sound Synthesis project
  - Brass instrument physical modeling

---

## Percussion Instruments

### Python Libraries & Projects

- **[DrumBlender (GitHub)](https://github.com/jorshi/drumblender)**

  - Synthesis of percussion sounds using sinusoidal modeling
  - DDSP noise synthesis
  - Neural source filter approach
  - Includes modal synthesis option

- **[synxylo (GitHub)](https://github.com/mosmeh/synxylo)**

  - Physical modeling xylophone synthesizer
  - Modal synthesis technique
  - Based on Csound's mode filter

- **[DrumGAN (GitHub)](https://github.com/SonyCSLParis/DrumGAN)**
  - Sony CSL Paris research project
  - Synthesis of drum sounds using GANs
  - Perceptual timbral conditioning

### Theory & Tutorials

- **[Percussion Synthesis - Stanford CCRMA](https://ccrma.stanford.edu/~sdill/220A-project/drums.html)**

  - Overview of percussion synthesis techniques
  - Practical implementation guidance

- **[Chapter 5: Percussion Synthesis](https://cim.mcgill.ca/~clark/nordmodularbook/nm_percussion.html)**

  - Nord Modular book chapter
  - Covers various percussion synthesis methods

- **[Modal Synthesis for Membrane Percussion (ResearchGate)](https://www.researchgate.net/publication/224082997_A_Modular_Physically_Based_Approach_to_the_Sound_Synthesis_of_Membrane_Percussion_Instruments)**

  - Academic paper on physical modeling of drums
  - Modal synthesis techniques
  - Membrane vibration modeling

- **[Modal Synthesis: Xylophone, Marimba, Glockenspiel, Bells (SuperCollider)](https://sccode.org/1-5ay)**

  - Working code example (SuperCollider, not Python)
  - Shows modal synthesis parameters

- **[Drum Synthesis - Cornell](https://vanhunteradams.com/DE1/Drum/Drum_synthesis.html)**
  - Practical tutorial on drum sound generation

---

## DSP & Audio Processing

### Python DSP Libraries

- **[pyo](https://github.com/belangeo/pyo)** - Python DSP module

  - Dedicated library for audio signal processing
  - Real-time audio synthesis and effects
  - Signal processing chains, filters, delays, synthesis generators
  - OSC and MIDI protocol support

- **[AudioLazy](https://github.com/danilobellini/audiolazy)**

  - Real-Time Expressive DSP Package for Python
  - Pure Python implementation
  - Includes comb filters, delays, and synthesis tools

- **[pysndfx](https://pypi.org/project/pysndfx/)**

  - Audio effects from EQ and compression to phasers, reverb, pitch shifters
  - Python wrapper for SoX effects

- **[SciPy Signal Processing](https://docs.scipy.org/doc/scipy/tutorial/signal.html)**
  - Filter design (FIR/IIR)
  - Convolution operations
  - Spectral analysis
  - Core DSP algorithms

### Reverb Implementation

- **[Dattorro Reverb - Python Implementation](https://www.louiscouka.com/code/datorro-reverb-implementation/)**

  - Complete Python implementation
  - Feedback delay network
  - Pre-delay, low-pass filter, all-pass diffusion

- **[Convolutional Reverb Tutorial](https://gormatevosyan.com/convolutional-reverb-how-and-why-does-it-work/)**

  - Python implementation guide
  - Explains convolution reverb theory and practice

- **[Coding a Basic Reverb Algorithm (Medium)](https://medium.com/the-seekers-project/coding-a-basic-reverb-algorithm-part-2-an-introduction-to-audio-programming-4db79dd4e325)**
  - Beginner-friendly tutorial
  - Step-by-step reverb implementation

### Filter Design & DSP

- **[Filters - PySDR Guide](https://pysdr.org/content/filters.html)**

  - Comprehensive filter tutorial using Python
  - FIR and IIR filter design
  - Practical DSP examples

- **[Linear Filters with SciPy](https://warrenweckesser.github.io/papers/weckesser-scipy-linear-filters.pdf)**

  - PDF tutorial on scipy.signal filters
  - Filter design and implementation

- **[DSP Related - Python Code Snippets](https://www.dsprelated.com/code-1/nf/Python/all.php)**
  - Collection of DSP code examples in Python

### Real-Time Audio Processing

- **[Real Time Signal Processing in Python](https://bastibe.de/2012-11-02-real-time-signal-processing-in-python.html)**

  - Blog post on low-latency audio
  - PyAudio and sounddevice usage

- **[Real-time Audio with Python (DSP Labs)](https://lcav.gitbook.io/dsp-labs/alien-voice/python)**

  - Block-based real-time processing
  - Voice transformation examples

- **[Real Time Audio Processing (University of Amsterdam)](https://staff.fnwi.uva.nl/r.vandenboomgaard/SP20162017/Python/Audio/realtimeaudio.html)**
  - Academic resource on real-time Python audio

---

## Synthesis Fundamentals & Theory

### Courses

- **[Audio Signal Processing for Music Applications - Stanford/Coursera](https://www.coursera.org/learn/audio-signal-processing)**

  - Spectral processing techniques
  - Python-based (Ubuntu environment)
  - Topics: DFT, STFT, Sinusoidal model, Harmonic model
  - Taught by Xavier Serra (UPF Barcelona)

- **[MUSIC 320: Introduction to Audio Signal Processing - Stanford CCRMA](https://ccrma.stanford.edu/courses/320/)**

  - Julius O. Smith III
  - Fourier Transform, DFT, FFT, Z-Transform
  - FIR/IIR filters, sound synthesis algorithms

- **[Introduction to Digital Audio Signal Processing (Stanford)](https://ccrma.stanford.edu/~jos/intro320/)**

  - Online materials from Music 320A&B
  - Free online textbook format

- **[EE 225D: Audio Signal Processing - UC Berkeley](https://www2.eecs.berkeley.edu/Courses/EE225D/)**

  - Speech and music processing
  - Pattern recognition, synthesis, recognition
  - Textbook: "Speech and Audio Signal Processing" by Gold, Morgan, Ellis

- **[Synthesizer Fundamentals - Berklee College of Music](https://college.berklee.edu/courses/mtec-222)**
  - Introduction to synthesizer programming
  - Sound design fundamentals

### Books (Online & Physical)

- **[Physical Audio Signal Processing - Julius O. Smith III](https://ccrma.stanford.edu/~jos/pasp/)**

  - Free online book
  - Virtual musical instruments and audio effects
  - Physical modeling, digital waveguides

- **[Spectral Audio Signal Processing - Julius O. Smith III](https://www.amazon.com/Spectral-Audio-Signal-Processing-Julius/dp/0974560731)**

  - Part of the music signal processing series
  - Available online at CCRMA website

- **[Sound Synthesis Based on Physical Models (PDF)](https://ccrma.stanford.edu/~jos/pdf/Julius-Smith-CIRMMT-Dist-Lec.pdf)**

  - Julius O. Smith III lecture notes

- **[Physical Modeling using Digital Waveguides (PDF)](https://ccrma.stanford.edu/~jos/pmudw/pmudw.pdf)**

  - Comprehensive waveguide synthesis guide

- **[Acoustics and Psychoacoustics - Howard & Angus](https://www.routledge.com/Acoustics-and-Psychoacoustics/Howard-Angus/p/book/9781138859876)**

  - Principles of human perception of sound
  - Musical timbre, pitch, loudness perception
  - Sound generation in musical instruments
  - Includes audio clips and tutorials on website

- **[Timbre: Acoustics, Perception, and Cognition - Siedenburg, Saitis, McAdams](https://link.springer.com/book/10.1007/978-3-030-14832-4)**

  - First comprehensive book on timbre perception
  - Acoustic modeling of timbre
  - Cognitive auditory neuroscience

- **[Introduction to Digital Signal Processing](https://www.worldscientific.com/worldscibooks/10.1142/6705)**
  - DSP with emphasis on audio and computer music
  - Covers sampling, filters, synthesis algorithms

### Tutorials & Blog Posts

- **[A Tutorial on Digital Sound Synthesis Techniques (ResearchGate)](https://www.researchgate.net/publication/245122776_A_Tutorial_on_Digital_Sound_Synthesis_Techniques)**

  - Academic paper covering main digital synthesis techniques
  - Fundamentals and practical applications

- **[Digital Audio Synthesis for Dummies - TrebledJ](https://trebledj.me/posts/digital-audio-synthesis-for-dummies-part-1/)**

  - Beginner-friendly introduction
  - Sampling and quantization basics

- **[Sound Synthesis Masterclass: Physical Modelling - MusicTech](https://musictech.com/guides/essential-guide/understanding-physical-modelling-synthesis/)**

  - Guide to physical modeling concepts
  - Heavy on theory with application notes

- **[Fundamentals of Psychoacoustics - MUTOR](https://mutor-2.github.io/ScienceOfMusic/units/03/)**

  - Free online resource
  - Study of hearing and sound mechanisms

- **[Digital Waveguide Models - DSP Related](https://www.dsprelated.com/freebooks/pasp/Digital_Waveguide_Models.html)**

  - Free online chapter
  - Waveguide synthesis theory

- **[Notes on Waveguide Synthesis](https://www.osar.fr/notes/waveguides/)**
  - Practical notes and implementation tips

---

## Synthesis Techniques

### Wavetable Synthesis

- **[Wavetable Synth in Python Tutorial - WolfSound](https://thewolfsound.com/sound-synthesis/wavetable-synth-in-python/)**
  - Complete Python implementation
  - Voice class with multiple oscillators
  - Practical, code-focused tutorial

### Additive Synthesis

- **[Sound Synthesis in Python - Medium](https://medium.com/@noahhradek/sound-synthesis-in-python-4e60614010da)**
  - Additive synthesis from basics
  - NumPy and SciPy implementation
  - Focus on adding signals together

### FM & Granular Synthesis

- **[pm_synth (GitHub)](https://github.com/guestdaniel/pm_synth)**

  - Real-time phase modulation and granular synthesizer
  - Python implementation
  - Readable, well-documented code

- **[Granular Synthesis - DSP Labs](https://lcav.gitbook.io/dsp-labs/granular-synthesis)**
  - Python tutorial on granular synthesis
  - Voice transformation
  - Real-time buffer processing

### Subtractive Synthesis

- **[Making A Synth With Python - Modulators](https://python.plainenglish.io/build-your-own-python-synthesizer-part-2-66396f6dad81)**

  - Tutorial series on building Python synthesizer
  - `ModulatedOscillator` and `ADSREnvelope` classes
  - Step-by-step implementation

- **[Envelopes in Sound Synthesis - WolfSound](https://thewolfsound.com/envelopes/)**

  - Ultimate guide to envelope generators
  - Theory and implementation

- **[ADSR Envelope Code - EarLevel Engineering](https://www.earlevel.com/main/2013/06/03/envelope-generators-adsr-code/)**

  - Professional C++ code (adaptable to Python)
  - Detailed ADSR implementation

- **[Jupylet Synthesizer Documentation](https://jupylet.readthedocs.io/en/latest/programmers_reference_guide/synthesis.html)**

  - Python library for synthesis
  - Subtractive, additive, FM, sample-based
  - Resonant filters, ADSR envelopes
  - Pure Python + NumPy

- **[PyTorch Audio - Oscillator and ADSR](https://docs.pytorch.org/audio/main/tutorials/oscillator_tutorial.html)**
  - oscillator_bank() and adsr_envelope()
  - Deep learning-ready synthesis

---

## Python Audio Libraries Comparison

### Synthesis-Focused

- **[pyo](https://github.com/belangeo/pyo)**

  - **Purpose**: Real-time audio synthesis and signal processing
  - Signal processing chains, generators, filters
  - OSC and MIDI support
  - Best for: Interactive audio applications, live performance

- **[Jupylet](https://jupylet.readthedocs.io/)**

  - **Purpose**: Game development + audio synthesis
  - Subtractive, additive, FM, sample-based synthesis
  - Antialiased oscillators with FM
  - ADSR envelopes (linear/non-linear)

- **[AudioLazy](https://github.com/danilobellini/audiolazy)**
  - **Purpose**: Real-time expressive DSP
  - Pure Python implementation
  - Comb filters, delays, synthesis primitives

### Analysis-Focused

- **[Librosa](https://librosa.org/)**
  - **Purpose**: Music and audio analysis
  - Feature extraction, beat detection, MIR
  - **Not for synthesis** - for analysis only

### Effects Processing

- **[Pedalboard (Spotify)](https://github.com/spotify/pedalboard)**

  - **Purpose**: Audio effects processing
  - Professional-quality effects (compression, reverb, EQ)
  - Fast C++ backend with Python bindings
  - Currently used in your project

- **[pysndfx](https://pypi.org/project/pysndfx/)**
  - **Purpose**: SoX-based audio effects
  - Reverb, phaser, EQ, compression, pitch shift

### File I/O

- **[soundfile](https://python-soundfile.readthedocs.io/)**
  - **Purpose**: Audio file reading/writing
  - WAV, FLAC, OGG support
  - Efficient file operations

### Comprehensive Lists

- **[awesome-python-audio (GitHub)](https://github.com/andreimatveyeu/awesome-python-audio)**

  - Curated list of Python audio resources
  - Libraries, tools, tutorials

- **[Python for Scientific Audio](https://project-awesome.org/faroit/awesome-python-scientific-audio)**
  - Curated list for scientific audio applications

---

## DSP Fundamentals

### SciPy Signal Processing

- **[scipy.signal Documentation](https://docs.scipy.org/doc/scipy/tutorial/signal.html)**

  - Filter design (firwin, butter, cheby, etc.)
  - Convolution (convolve, fftconvolve)
  - Spectral analysis
  - Official comprehensive resource

- **[Signal Processing Basics with scipy.signal - AskPython](https://www.askpython.com/python-modules/scipy-signal)**
  - Beginner tutorial
  - Filtering, feature extraction
  - Practical examples

### Filtering

- **[Filters - PySDR Guide](https://pysdr.org/content/filters.html)**

  - Comprehensive filter tutorial
  - FIR and IIR design
  - Python + NumPy examples
  - Excellent visualizations

- **[DSP Related - Filter Resources](https://www.dsprelated.com/freebooks/pasp/)**
  - Collection of filter articles
  - Code snippets and theory

### Convolution

- Convolution for audio: `scipy.signal.convolve()` or `scipy.signal.fftconvolve()`
  - FIR filtering = convolution with impulse response
  - Fast convolution using FFT for efficiency

---

## Advanced Topics

### Neural Audio Synthesis

- **[NSynth - Google Magenta](https://magenta.tensorflow.org/nsynth)**

  - Neural audio synthesis using WaveNet
  - Sample-level sound generation
  - Large-scale dataset of annotated musical notes
  - [GitHub: NSynth](https://github.com/magenta/nsynth)

- **[DDSP - Differentiable Digital Signal Processing](https://magenta.tensorflow.org/ddsp)**

  - Combines classical DSP with deep learning
  - Interpretable audio synthesis
  - Train models with minimal data (< 13 min of audio)
  - [GitHub: DDSP](https://github.com/magenta/ddsp)

- **[DDSP-VST](https://magenta.tensorflow.org/ddsp-vst)**
  - Real-time neural synthesizer plugin
  - Cross-platform, runs in DAWs
  - [GitHub: DDSP-VST](https://github.com/magenta/ddsp-vst)

### Psychoacoustics

- **[Acoustics and Psychoacoustics - Howard & Angus](https://www.routledge.com/Acoustics-and-Psychoacoustics/Howard-Angus/p/book/9781138859876)**

  - Comprehensive textbook
  - Musical timbre perception
  - Pitch and loudness perception
  - Includes audio clips and tutorials

- **[Timbre: Acoustics, Perception, and Cognition](https://link.springer.com/book/10.1007/978-3-030-14832-4)**

  - First comprehensive book on timbre
  - Acoustic modeling
  - Cognitive aspects

- **[Introduction to Psychoacoustics](http://www.acousticslab.org/psychoacoustics/PMFiles/Module06.htm)**
  - Free online resource
  - Hearing mechanisms
  - Sound perception basics

---

## Synthesis Technique Comparisons

### Physical Modeling

**Best for:** Strings, winds, percussion with realistic timbres
**Complexity:** High (requires physics knowledge)
**CPU:** Moderate to high
**Examples:** Karplus-Strong (strings), waveguides (winds), modal (bells/drums)

### Additive Synthesis

**Best for:** Complex, evolving timbres; bell-like sounds
**Complexity:** Low to moderate
**CPU:** High (many oscillators)
**Examples:** Organs, electric pianos, synthetic textures

### Subtractive Synthesis

**Best for:** Classic analog sounds, leads, pads, bass
**Complexity:** Low (easiest to understand)
**CPU:** Low
**Examples:** Analog synth emulation (Moog, ARP)

### FM Synthesis

**Best for:** Metallic, bell-like, complex timbres
**Complexity:** High (understanding modulation)
**CPU:** Low (efficient)
**Examples:** DX7-style sounds, electric pianos, bells

### Granular Synthesis

**Best for:** Textures, atmospheric sounds, time-stretching
**Complexity:** Moderate
**CPU:** High
**Examples:** Ambient pads, soundscapes, glitch effects

### Wavetable Synthesis

**Best for:** Modern digital sounds, EDM
**Complexity:** Moderate
**CPU:** Low
**Examples:** Serum-style synthesis, evolving pads

---

## Recommended Learning Path

### 1. Foundations (Start Here)

1. **Julius O. Smith's Online Books** (Free)

   - Start with "Physical Audio Signal Processing"
   - Then "Spectral Audio Signal Processing"

2. **Coursera: Audio Signal Processing for Music Applications**

   - Hands-on with Python
   - Structured curriculum

3. **PySDR Filters Guide**
   - Practical DSP with Python
   - Filter design fundamentals

### 2. Synthesis Techniques

1. **Additive Synthesis** - Sound Synthesis in Python (Medium)
2. **Subtractive Synthesis** - Making A Synth With Python series
3. **Wavetable Synthesis** - WolfSound tutorial
4. **FM/Granular** - pm_synth GitHub project

### 3. Instrument-Specific

1. **Winds**: OpenWind library + Stanford CCRMA tutorials
2. **Percussion**: DrumBlender + modal synthesis papers
3. **Bells/Xylophones**: synxylo project + modal synthesis

### 4. Advanced DSP

1. **Reverb**: Dattorro implementation (Python)
2. **Filters**: scipy.signal + PySDR tutorials
3. **Real-time**: sounddevice + pyo library

### 5. Cutting Edge

1. **Neural Synthesis**: DDSP (Google Magenta)
2. **ML for Audio**: NSynth dataset + models

---

## Practical Next Steps

### For Wind Instruments

1. Study OpenWind library documentation
2. Read waveguide synthesis papers
3. Implement simple flute using waveguide technique
4. Reference: Similar structure to `karplus_strong.py`

### For Percussion

1. Study modal synthesis (synxylo project)
2. Implement drum synthesis using modal techniques
3. Experiment with DrumBlender for ML approach

### For DSP/Effects

1. Start with scipy.signal filters
2. Implement Dattorro reverb (Python guide available)
3. Build effect chain using Pedalboard

### For Research

1. Take Stanford's Audio Signal Processing course
2. Read Julius O. Smith's free online books
3. Study psychoacoustics (Howard & Angus book)
4. Experiment with DDSP (combines classical + ML)

---

## Implementation Strategy for This Project

Based on current architecture (`tools/synthesis/`, `tools/instruments/`):

**Wind Instruments:**

```
tools/synthesis/physical_modeling/waveguide.py  # New
tools/instruments/winds/trumpet.py              # New
tools/instruments/winds/flute.py                # New
```

**Percussion:**

```
tools/synthesis/physical_modeling/modal.py      # New
tools/instruments/percussion/drums.py           # New
tools/instruments/percussion/tuned.py           # New (xylophone, marimba)
```

**DSP/Effects:**

```
tools/audio/effects/reverb.py                   # New
tools/audio/effects/delay.py                    # New
tools/audio/effects/filters.py                  # New
```

All instruments will work with the existing `Song → Track → Measure → Event` database structure with polymorphic `event_data` JSON fields.

---

## GitHub Repositories to Explore

- https://github.com/nbrochec/flute-physical-modelling (Flute - Python)
- https://github.com/jorshi/drumblender (Drums - Python ML)
- https://github.com/mosmeh/synxylo (Xylophone - Modal synthesis)
- https://github.com/guestdaniel/pm_synth (FM/Granular - Python)
- https://github.com/belangeo/pyo (Real-time audio - Python)
- https://github.com/danilobellini/audiolazy (DSP toolkit - Python)
- https://github.com/magenta/ddsp (Neural synthesis - Python/TensorFlow)
- https://github.com/spotify/pedalboard (Effects - Python/C++)

---

## Notes

- Most academic implementations use C++/Faust/SuperCollider
- Python implementations exist but are less common for winds/percussion
- Adapt techniques from other languages to Python + NumPy
- Physical modeling papers provide mathematical foundations
- Start with simpler techniques (modal synthesis) before complex waveguides
