"""
Dates Tab Views
"""

from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from edx_django_utils import monitoring as monitoring_utils
from opaque_keys.edx.keys import CourseKey

from lms.djangoapps.course_home_api.progress.v1.serializers import ProgressTabSerializer
from lms.djangoapps.courseware.courses import get_course_with_access
from lms.djangoapps.courseware.masquerade import setup_masquerade
from lms.djangoapps.courseware.access import has_access


class ProgressTabView(RetrieveAPIView):
    """
    **Use Cases**

        Request details for the Progress Tab

    **Example Requests**

        GET api/course_home/v1/progress/{course_key}

    **Response Values**

        Body consists of the following fields:

        user: (str) the username of the person accessing the progress tab
        has_access: (bool) whether the user has the ability to access the tab

    **Returns**

        * 200 on success with above fields.
        * 403 if the user is not authenticated.
        * 404 if the course is not available or cannot be seen.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = ProgressTabSerializer

    def get(self, request, *args, **kwargs):
        course_key_string = kwargs.get('course_key_string')
        course_key = CourseKey.from_string(course_key_string)

        # Enable NR tracing for this view based on course
        monitoring_utils.set_custom_metric('course_id', course_key_string)
        monitoring_utils.set_custom_metric('user_id', request.user.id)
        monitoring_utils.set_custom_metric('is_staff', request.user.is_staff)

        _, request.user = setup_masquerade(
            request,
            course_key,
            staff_access=has_access(request.user, 'staff', course_key),
            reset_masquerade_data=True
        )

        course = get_course_with_access(request.user, 'load', course_key, check_if_enrolled=False)
        access = bool(has_access(request.user, 'load', course))

        print(request.user.email)
        data = {
            'user': request.user,
            'has_access': access,
            'email': request.user.email,
        }

        serializer = self.get_serializer(data)

        return Response(serializer.data)
