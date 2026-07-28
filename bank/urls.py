from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="bank/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path("", views.dashboard_view, name="dashboard"),
    path("deposit/", views.deposit_view, name="deposit"),
    path("withdraw/", views.withdraw_view, name="withdraw"),
    path("transfer/", views.transfer_view, name="transfer"),
    path("history/", views.transaction_history_view, name="transaction_history"),
    path("delete-account/", views.delete_account_view, name="delete_account"),
]
