
# Imports #####################################################################

import json
import stripe

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic.base import View
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from mitxmako.shortcuts import render_to_response

from coupons.models import get_base_price_for_course_id, Coupon
from courseware.access import has_access
from student.models import CourseEnrollment
from student.views import course_from_id


# Functions ###################################################################

def pay_with_token(user, course_id, token, coupon_name=None):
    """
    Process a pre-made Stripe payment token, including a coupon reduction
    """
    if not token:
        return False

    stripe.api_key = settings.STRIPE_KEY_SECRET
    price = Coupon.objects.get_price_with_coupon(course_id, coupon_name)
    description = '{},{}'.format(user.email, course_id)
    if coupon_name:
        description += ',coupon={}'.format(coupon_name)
    try:
        stripe.Charge.create(
            amount=price['value']*100,
            currency=price['currency'].lower(),
            card=token,
            description=description
        )
        return True
    except stripe.CardError:
        return False



# Views #######################################################################

class CouponCheckoutView(View):

    @method_decorator(login_required)
    def get(self, request, course_id, error=None):
        if CourseEnrollment.enrollment_mode_for_user(request.user, course_id) == 'pay_with_coupon':
            return redirect(reverse('dashboard'))
        price = get_base_price_for_course_id(course_id)

        context = {
            "course_id": course_id,
            "price": price,
            "course_name": course_from_id(course_id).display_name,
            "error": error,
        }
        return render_to_response("coupons/pay_with_coupon.html", context)

    @method_decorator(login_required)
    def post(self, request, course_id):
        payment_token = request.POST.get('payment_token')
        coupon_name = request.POST.get('coupon')
        user = request.user
        course = course_from_id(course_id)

        error_msg = ''
        if not payment_token:
            error_msg = _("Payment required")
        if not pay_with_token(user, course_id, payment_token, coupon_name=coupon_name):
            error_msg = _("Payment denied")
        if not has_access(user, course, 'enroll'):
            error_msg = _("Enrollment is closed")

        if error_msg != '':
            return self.get(request, course_id, error=error_msg)

        enrollment = CourseEnrollment.enroll(user, course_id)
        try:
            coupon = Coupon.objects.get(coupon_name__iexact=coupon_name)
        except Coupon.DoesNotExist:
            pass
        else:
            enrollment.coupon = coupon
            enrollment.save()

        return redirect(reverse('dashboard'))


def price_with_coupon(request):
    coupon_name = request.GET['coupon']
    course_id = request.GET['course_id']
    price = Coupon.objects.get_price_with_coupon(course_id, coupon_name)
    return HttpResponse(json.dumps({'price': price}))

