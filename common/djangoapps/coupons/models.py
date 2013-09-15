"""
Allow to use discount codes for payment, using Stripe
"""

# Imports #####################################################################

from django.db import models
from collections import namedtuple

from course_modes.models import CourseMode


# Constants ###################################################################

Mode = namedtuple('Mode', ['slug', 'name', 'min_price', 'suggested_prices', 'currency'])


# Functions ###################################################################

def get_base_price_for_course_id(course_id):
    mode = CourseMode.modes_for_course_dict(course_id)['pay_with_coupon']
    return {
        'value': mode.min_price,
        'currency': mode.currency
    }


# Models ######################################################################

class CouponManager(models.Manager):
    def get_price_with_coupon(self, course_id, coupon_name):
        coupon_name = coupon_name.strip()
        try:
            coupon = Coupon.objects.get(coupon_name__iexact=coupon_name)
        except Coupon.DoesNotExist:
            return get_base_price_for_course_id(course_id)
        else:
            return coupon.get_price_with_coupon(course_id)


class Coupon(models.Model):
    """
    Discount coupon which can be redeemed by users when paying for a course which
    has the mode 'pay_with_coupon'
    """
    objects = CouponManager()

    # the coupon name the user will have to enter to get the reduction
    coupon_name = models.CharField(max_length=100, unique=True)

    # price reduction that the coupon grants, in currency
    price_reduction = models.IntegerField(default=0)

    # the currency these prices are in, using lower case ISO currency codes
    currency = models.CharField(default="usd", max_length=8)

    def get_price_with_coupon(self, course_id):
        """
        Returns the price with the coupon applied

        Only applies if it uses the same currency, as we don't support currency conversion yet
        """
        price = get_base_price_for_course_id(course_id)
        if price['currency'].lower() == self.currency.lower():
            price['value'] -= self.price_reduction
        return price

    def __unicode__(self):
        return u"{} : reduction={}, currency={}".format(
            self.coupon_name, self.price_reduction, self.currency
        )




