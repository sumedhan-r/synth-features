from dataclasses import dataclass
from itertools import cycle
from typing import Iterator

import numpy as np

from src.tools.signals.burst import BurstGenerator, WhiteNoise
from src.tools.utils.temporal import Hertz, Time
from src.api.core.constant import AUDIO_CD_SAMPLING_RATE


@dataclass(frozen=True)
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
    """

    burst_generator: BurstGenerator = WhiteNoise()
    sampling_rate: int = AUDIO_CD_SAMPLING_RATE

    def vibrate(
        self, frequency: Hertz, duration: Time, damping: float = 0.5
    ) -> np.ndarray:
        assert 0 < damping <= 0.5

        def feedback_loop() -> Iterator[float]:
            buffer = self.burst_generator(
                num_samples=round(self.sampling_rate / frequency),
                sampling_rate=self.sampling_rate
            )

            # Buffer samples are cycled in an infinite loop for decay modeling
            for i in cycle(range(buffer.size)):
                yield (current_sample := buffer[i])
                next_sample = buffer[(i + 1) % buffer.size]

                # Moving average is used here to model Low-pass filter and 
                # Cumulator combination
                buffer[i] = (current_sample + next_sample) * damping
        
        # Takes only a finite number of samples based on duration interval for synthesis
        return np.fromiter(
            feedback_loop(),
            np.float64,
            duration.get_num_samples(self.sampling_rate),
        )
