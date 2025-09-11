"""
The musical sounds are generated from the sound amplitudes using
Spotify's PedalBoard library. The library contains methods to convert
sound amplitudes to aduio files such as

    - LPCM (Linear Pulse-Code Modulation)
    - MP3 Lossy compression
"""

from pedalboard.io import AudioFile

from src.tools.signals.string_synthesis import Synthesizer


async def write_monophonic_sound_file(
    audio_file_name: str,
    frequencies: list,
    time_interval: float = 0.5,
    damping: float = 0.495,
) -> None:
    """
    Function to write a monophonic sound file given a list of frequencies.
    The sound is created sequentially for the given frequency values.
    """
    synthesizer = Synthesizer()

    with AudioFile(audio_file_name, "w", synthesizer.sampling_rate) as file:
        file.write(
            synthesizer.generate_monophonic_sound(frequencies, time_interval, damping)
        )


async def write_polyphonic_sound_file(
    audio_file_name: str,
    frequencies: list,
    time_interval: float = 0.5,
    damping: float = 0.499,
) -> None:
    synthesizer = Synthesizer()

    with AudioFile(audio_file_name, "w", synthesizer.sampling_rate) as file:
        file.write(
            synthesizer.generate_polyphonic_sound(frequencies, time_interval, damping)
        )


async def write_arpeggio_sound_file(
    audio_file_name: str,
    frequencies: list,
    time_interval: float = 3.5,
    inertial_delay_interval: float = 0.25,
    damping: float = 0.499,
) -> None:
    synthesizer = Synthesizer()

    with AudioFile(audio_file_name, "w", synthesizer.sampling_rate) as file:
        file.write(
            synthesizer.generate_arpeggio_sound(
                frequencies, time_interval, inertial_delay_interval, damping
            )
        )
