"""
Dates Tab Views
"""

from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from edx_django_utils import monitoring as monitoring_utils
from opaque_keys.edx.keys import CourseKey

from lms.djangoapps.course_home_api.progress.v1.serializers import ProgressTabSerializer
from lms.djangoapps.courseware.context_processor import user_timezone_locale_prefs
from lms.djangoapps.courseware.courses import get_course_date_blocks, get_course_with_access
from lms.djangoapps.courseware.date_summary import TodaysDate, verified_upgrade_deadline_link
from lms.djangoapps.course_home_api.dates.v1.serializers import DatesTabSerializer
from lms.djangoapps.course_home_api.toggles import course_home_mfe_dates_tab_is_active
from openedx.features.course_experience.utils import dates_banner_should_display
from openedx.features.content_type_gating.models import ContentTypeGatingConfig
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

        # leaving this commented out for ease of use
        # if not course_home_mfe_dates_tab_is_active(course_key):
        #     return Response(status=status.HTTP_404_NOT_FOUND)

        learner_is_full_access = not ContentTypeGatingConfig.enabled_for_enrollment(
            user=request.user,
            course_key=course_key,
        )

        # Enable NR tracing for this view based on course
        monitoring_utils.set_custom_metric('course_id', course_key_string)
        monitoring_utils.set_custom_metric('user_id', request.user.id)
        monitoring_utils.set_custom_metric('is_staff', request.user.is_staff)

        course = get_course_with_access(request.user, 'load', course_key, check_if_enrolled=False)
        access = bool(has_access(request.user, 'load', course))

        data = {
            'user': request.user,
            'has_access': access,
        }
        context = self.get_serializer_context()
        context['learner_is_full_access'] = learner_is_full_access
        serializer = self.get_serializer_class()(data, context=context)

        return Response(serializer.data)
