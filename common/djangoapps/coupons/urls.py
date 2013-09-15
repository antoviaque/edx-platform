from django.conf.urls import patterns, url

from coupons import views

urlpatterns = patterns('',
    url(r'^checkout/(?P<course_id>[^/]+/[^/]+/[^/]+)$', views.CouponCheckoutView.as_view(), name="pay_with_coupon"),
    url(r'^price$', 'coupons.views.price_with_coupon', name="price_with_coupon"),
)
