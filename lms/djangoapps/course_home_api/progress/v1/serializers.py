# pylint: disable=abstract-method
"""
Progress Tab Serializers
"""

from rest_framework import serializers


class ProgressTabSerializer(serializers.Serializer):
    """
    Serializer
    """
    user = serializers.CharField()
    has_access = serializers.BooleanField()
    email = serializers.CharField()
