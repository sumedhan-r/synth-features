"""Unit tests for temporal.py module."""

import pytest
from decimal import Decimal
from fractions import Fraction

from src.tools.utils.temporal import Time, Timeline

pytestmark = pytest.mark.unit


class TestTime:
    """Test cases for Time class."""

    def test_time_creation_with_int(self):
        """Test Time creation with integer seconds."""
        time_obj = Time(5)
        assert time_obj.seconds == Decimal("5")

    def test_time_creation_with_float(self):
        """Test Time creation with float seconds."""
        time_obj = Time(2.5)
        assert time_obj.seconds == Decimal("2.5")

    def test_time_creation_with_decimal(self):
        """Test Time creation with Decimal seconds."""
        time_obj = Time(Decimal("3.14"))
        assert time_obj.seconds == Decimal("3.14")

    def test_time_creation_with_fraction(self):
        """Test Time creation with Fraction seconds."""
        time_obj = Time(Fraction(1, 2))
        assert time_obj.seconds == Decimal("0.5")

    def test_from_milliseconds(self):
        """Test creating Time from milliseconds."""
        time_obj = Time.from_milliseconds(1500)
        assert time_obj.seconds == Decimal("1.5")

    def test_time_addition_with_time(self):
        """Test adding two Time objects."""
        time1 = Time(2)
        time2 = Time(3)
        result = time1 + time2
        assert result.seconds == Decimal("5")
        assert isinstance(result, Time)

    def test_time_addition_with_int(self):
        """Test adding integer to Time."""
        time_obj = Time(2)
        result = time_obj + 3
        assert result.seconds == Decimal("5")

    def test_time_addition_with_float(self):
        """Test adding float to Time."""
        time_obj = Time(2)
        result = time_obj + 1.5
        assert result.seconds == Decimal("3.5")

    def test_time_addition_with_decimal(self):
        """Test adding Decimal to Time."""
        time_obj = Time(2)
        result = time_obj + Decimal("1.5")
        assert result.seconds == Decimal("3.5")

    def test_time_addition_with_fraction(self):
        """Test adding Fraction to Time."""
        time_obj = Time(2)
        result = time_obj + Fraction(1, 2)
        assert result.seconds == Fraction(5, 2)  # Result is Fraction

    @pytest.mark.inheritance
    def test_time_addition_returns_same_type(self):
        """Test that Time addition returns Self type."""

        class CustomTime(Time):
            pass

        custom_time = CustomTime(2)
        result = custom_time + 3
        assert isinstance(result, CustomTime)
        assert result.seconds == Decimal("5")

    def test_get_num_samples(self):
        """Test getting number of samples from Time."""
        time_obj = Time(2)
        samples = time_obj.get_num_samples(44100)  # CD quality sample rate
        assert samples == 88200

    def test_get_num_samples_with_fractional_time(self):
        """Test getting samples with fractional time."""
        time_obj = Time(0.1)  # 100ms
        samples = time_obj.get_num_samples(44100)
        assert samples == 4410

    @pytest.mark.error_handling
    def test_time_addition_invalid_type(self):
        """Test that adding invalid type raises TypeError."""
        time_obj = Time(2)
        with pytest.raises(TypeError, match="can't add 'str'"):
            time_obj + "invalid"

    @pytest.mark.error_handling
    def test_time_creation_invalid_type(self):
        """Test that creating Time with invalid type raises TypeError."""
        with pytest.raises(TypeError, match="unsupported type 'str'"):
            Time("invalid")


class TestTimeline:
    """Test cases for Timeline class."""

    def test_timeline_creation(self):
        """Test Timeline creation with default instant."""
        timeline = Timeline()
        assert timeline.instant.seconds == Decimal("0")

    def test_timeline_creation_with_custom_instant(self):
        """Test Timeline creation with custom instant."""
        initial_time = Time(5)
        timeline = Timeline(instant=initial_time)
        assert timeline.instant.seconds == Decimal("5")

    def test_timeline_right_shift_with_int(self):
        """Test Timeline >> operator with integer."""
        timeline = Timeline()
        result = timeline >> 5
        assert timeline.instant.seconds == Decimal("5")
        assert result is timeline  # Should return self

    def test_timeline_right_shift_with_float(self):
        """Test Timeline >> operator with float."""
        timeline = Timeline()
        timeline >> 2.5
        assert timeline.instant.seconds == Decimal("2.5")

    def test_timeline_right_shift_with_time(self):
        """Test Timeline >> operator with Time object."""
        timeline = Timeline()
        time_obj = Time(3)
        timeline >> time_obj
        assert timeline.instant.seconds == Decimal("3")

    def test_timeline_right_shift_chaining(self):
        """Test chaining Timeline >> operations."""
        timeline = Timeline()
        result = timeline >> 2 >> 3 >> 1.5
        assert timeline.instant.seconds == Decimal("6.5")
        assert result is timeline

    @pytest.mark.inheritance
    def test_timeline_right_shift_returns_self_type(self):
        """Test that Timeline >> returns Self type."""

        class CustomTimeline(Timeline):
            def custom_method(self):
                return "custom"

        custom_timeline = CustomTimeline()
        result = custom_timeline >> 5
        assert isinstance(result, CustomTimeline)
        assert result.custom_method() == "custom"
        assert result.instant.seconds == Decimal("5")

    @pytest.mark.immutability
    def test_timeline_immutable_time_objects(self):
        """Test that Time objects are immutable (frozen=True)."""
        time_obj = Time(5)
        with pytest.raises(
            AttributeError
        ):  # dataclass(frozen=True) raises AttributeError
            time_obj.seconds = Decimal("10")

    def test_timeline_mutable_instant(self):
        """Test that Timeline instant can be modified."""
        timeline = Timeline()
        timeline.instant = Time(10)
        assert timeline.instant.seconds == Decimal("10")
