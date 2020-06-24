# pylint: disable=abstract-method
"""
Progress Tab Serializers
"""

from rest_framework import serializers


class ProgressTabSerializer(serializers.Serializer):
    """
    Serializer
    """
    test = serializers.BooleanField()
