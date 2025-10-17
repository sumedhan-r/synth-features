from dataclasses import dataclass
from functools import cache
from itertools import cycle
from typing import Iterator, Sequence

import numpy as np

from src.tools.instruments.strings.plucked import PluckedStringInstrument
from src.tools.synthesis.input.noise import BurstGenerator, WhiteNoise
from src.tools.instruments.strings.chord import Chord
from src.tools.utils.temporal import Hertz, Time
from src.tools.utils.processing import remove_dc, normalize
from src.tools.instruments.strings.stroke import StrokeDirection, StrokeVelocity
from src.api.core.constant import AUDIO_CD_SAMPLING_RATE


# keyword_only here implies all class attributes are keyword arguments,
# thus circumventing invalid arg listing in __init__ during Inheritance.
# Ordering : (self, *, burst_generator, sampling_rate)
# Reference - https://www.trueblade.com/blogs/news/python-3-10-new-dataclass-features
@dataclass(frozen=True, kw_only=True)
class Synthesizer:
    """
    This is a class defined for a string synthesizer that models the plucking of
    a string using the Karplus-Strong Algorithm. The sound is modeled based on
        - Burst generator as input
        - Delay line to model phase shift as reflected wave components in string (these undergo interference)
        - Low pass filter to simulate decay of high frequency components leaving the base frequency of string
        - Cumulator that adds the decayed high frequency components across time

    The low pass filter and cumulator is represented using Moving Average since the
    two are similar, although a Virtual Low pass filter can be used for the Algorithm
    as well.

    The musical sounds are generated from the sound amplitudes using Spotify's PedalBoard
    library. The library contains methods to convert sound amplitudes to aduio files such as

        - LPCM (Linear Pulse-Code Modulation)
        - MP3 Lossy compression
    """

    burst_generator: BurstGenerator = WhiteNoise()
    sampling_rate: int = AUDIO_CD_SAMPLING_RATE

    @cache
    def _vibrate(
        self, frequency: Hertz, duration: Time, damping: float = 0.5
    ) -> np.ndarray:
        assert 0 < damping <= 0.5

        def feedback_loop() -> Iterator[float]:
            buffer = self.burst_generator(
                num_samples=round(self.sampling_rate / frequency),
                sampling_rate=self.sampling_rate,
            )

            # Buffer samples are cycled in an infinite loop for decay modeling
            for i in cycle(range(buffer.size)):
                yield (current_sample := buffer[i])
                next_sample = buffer[(i + 1) % buffer.size]

                # Moving average is used here to model Low-pass filter and
                # Cumulator combination
                buffer[i] = (current_sample + next_sample) * damping

        # Takes only a finite number of samples based on duration interval for synthesis
        return normalize(
            remove_dc(
                np.fromiter(
                    feedback_loop(),
                    np.float64,
                    duration.get_num_samples(self.sampling_rate),
                )
            )
        )

    def _polyphonic_overlay(self, sounds: Sequence[np.ndarray]) -> np.ndarray:
        """
        This function returns the overlap of multiple monotones, allowing
        for interference between the monotones. Polyphonic sounds exist in
        chords and similar stacked note sound compositions.

        The overlap of monotonic sounds must only be performed after removing
        DC bias and normalizing. This is because:
            - DC bias will get cumulated and sound amplitudes will grow beyond
            acceptable volume thresholds, making sound processing difficult
            - Normalizing polyphonic sounds might create unintended consequences
            of diminishing chords that would start becoming inaudible.
        """

        return np.sum(sounds, axis=0)

    def _arpeggio_overlay(
        self, sounds: Sequence[np.ndarray], delay: Time
    ) -> np.ndarray:
        """
        This function returns the simulated sound of an arpeggio given a set of
        monotones. Arpeggiated sounds represent a realistic string instrument
        strumming pattern as well.

        The string instrument has n strings. When the n strings are played at a
        time instance, there exists a small delay between the pluck of one string
        and the pluck of the consecutive string. This delay factor is used for the
        arpeggiated sound simulation. Monotonic sounds are arranged sequentially
        with an incremental addition of delay to each monotone.
        """

        num_delay_samples = delay.get_num_samples(self.sampling_rate)

        # Num samples is calculated as the max value in the monotonic sound
        # input along with delay sample count. This could cause destructive
        # interference in the final arpeggio simulated sound if the monotones
        # are of unequal sample size.
        num_samples = max(
            i * num_delay_samples + sound.size for i, sound in enumerate(sounds)
        )

        samples = np.zeros(num_samples, dtype=np.float64)

        for i, sound in enumerate(sounds):
            offset = i * num_delay_samples
            samples[offset : offset + sound.size] += sound
        return samples

    def generate_monophonic_sound(
        self,
        frequencies: list,
        time_interval: float = 0.5,
        damping: float = 0.495,
    ) -> np.ndarray:
        duration = Time(seconds=time_interval)
        num_samples = duration.get_num_samples(self.sampling_rate)

        sound = np.zeros(len(frequencies) * num_samples, dtype=np.float64)

        for i, frequency in enumerate(frequencies):
            vibration = self._vibrate(frequency, duration, damping)
            sound[i * num_samples : i * num_samples + len(vibration)] = vibration

        return sound

    def generate_polyphonic_sound(
        self,
        frequencies: list,
        time_interval: float = 0.5,
        damping: float = 0.499,
    ) -> np.ndarray:
        duration = Time(seconds=time_interval)

        sounds = [
            self._vibrate(frequency, duration, damping) for frequency in frequencies
        ]

        return normalize(self._polyphonic_overlay(sounds))

    def generate_arpeggio_sound(
        self,
        frequencies: list,
        time_interval: float = 3.5,
        inertial_delay_interval: float = 0.25,
        damping: float = 0.499,
    ) -> np.ndarray:
        delay = Time.from_milliseconds(40)

        # Check if frequencies are ordered from high to low (natural arpeggio order)
        is_high_to_low = all(
            frequencies[i] >= frequencies[i + 1] for i in range(len(frequencies) - 1)
        )

        sounds = []

        for i, frequency in enumerate(frequencies):
            # Lower frequency strings have higher inertia, so they get longer duration
            # If frequencies are low-to-high, invert the index for duration calculation
            duration_index = i if is_high_to_low else (len(frequencies) - 1 - i)
            duration = Time(time_interval + inertial_delay_interval * duration_index)
            sounds.append(self._vibrate(frequency, duration, damping))

        return normalize(self._arpeggio_overlay(sounds, delay))


# keyword_only here implies all class attributes are keyword arguments,
# thus circumventing invalid arg listing in __init__ during Inheritance.
# Ordering : (self, instrument, *, burst_generator, sampling_rate)
# Reference - https://www.trueblade.com/blogs/news/python-3-10-new-dataclass-features
@dataclass(frozen=True, kw_only=True)
class StringSynthesizer(Synthesizer):
    instrument: PluckedStringInstrument

    @cache
    def strum_strings(
        self, chord: Chord, velocity: StrokeVelocity, vibration: Time | None = None
    ) -> np.ndarray:
        """
        Function that simulates playing a String instrument by strumming a set of
        strings. Chord is constructed using the self.arpeggio_overlay() method,
        which is the realistic chord simulation method.
        """

        if vibration is None:
            vibration = self.instrument.vibration

        if velocity.stroke_direction is StrokeDirection.UP:
            stroke = self.instrument.upstroke
        else:
            stroke = self.instrument.downstroke

        sounds = tuple(
            self._vibrate(pitch.frequency, vibration, self.instrument.damping)
            for pitch in stroke(chord)
        )

        return self._arpeggio_overlay(sounds, velocity.delay)
