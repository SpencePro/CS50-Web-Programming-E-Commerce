from django.urls import path
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

app_name = "auctions"

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("create/", views.create_listing, name="create"),
    path("listing/<int:id>/", views.listing_view, name="listing"),
    path("watchlist/", views.display_watchlist, name="watchlist"),
    path("add/<int:id>/", views.add_to_watchlist, name="add"),
    path("remove/<int:id>/", views.remove_from_watchlist, name="remove"),
    path("comment/<int:id>/", views.add_comment, name="comment"),
    path("bid/<int:id>/", views.bid, name="bid"),
    path("end/<int:id>/", views.end_auction, name="end"),
    path("categories/", views.categories, name="categories"),
    path("sales/", views.display_sales, name="sales"),
    path("purchases/", views.display_purchases, name="purchases"),
]

urlpatterns += staticfiles_urlpatterns()