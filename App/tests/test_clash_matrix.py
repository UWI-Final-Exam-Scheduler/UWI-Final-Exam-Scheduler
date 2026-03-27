import pytest
from App.controllers.clash_matrix import absolute_threshold, exceeds_percentage_threshold

def test_absolute_threshold_true():
    assert absolute_threshold(6, abs_threshold=5) is True

def test_absolute_threshold_false():
    assert absolute_threshold(4, abs_threshold=5) is False

def test_exceeds_percentage_threshold_true():
    enrollment_count = {"COMP1600": 10, "MATH1140": 20}
    assert exceeds_percentage_threshold(2, enrollment_count, "COMP1600", "MATH1140", perc_thresh=0.1) is True

def test_exceeds_percentage_threshold_zero_class():
    enrollment_count = {"COMP1600": 0, "MATH1140": 20}
    assert exceeds_percentage_threshold(2, enrollment_count, "COMP1600", "MATH1140", perc_thresh=0.1) is False