# Simple Bank System — Django Project

A basic banking web app built with Django. Users can register, log in, deposit,
withdraw, transfer money to other users, and view their transaction history.

## What it does

- User registration & login (built on Django's own auth system)
- Every user automatically gets one bank Account when they register
- Deposit money
- Withdraw money (blocked if balance is insufficient)
- Transfer money to another user by account number
- Transaction history — a full audit log of every movement
- Django Admin panel to view all accounts/transactions as a "bank staff" view

## Project structure

```
bankapp/
├── manage.py                  # Django's command-line tool
├── bankproject/                # Project-level settings
│   ├── settings.py            # DB config, installed apps, login redirects
│   └── urls.py                # Root URL routing -> includes bank.urls
└── bank/                       # The actual app (all the business logic)
    ├── models.py               # Account & Transaction tables
    ├── forms.py                # Register/Deposit/Withdraw/Transfer forms
    ├── views.py                # The logic: what happens on each action
    ├── urls.py                 # /register /login /deposit /withdraw /transfer /history
    ├── admin.py                # Registers models with Django Admin
    └── templates/bank/         # HTML pages (simple, no frontend framework)
```

## How to run it

```bash
cd bankapp
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # optional, for /admin access
python manage.py runserver
```

Then open http://127.0.0.1:8000/ in your browser.

## The data model (2 tables)

**Account** — one per User (`OneToOneField`)
- `account_number` (auto-generated, unique)
- `account_type` (Savings / Current)
- `balance`

**Transaction** — many per Account (`ForeignKey`)
- `transaction_type` (Deposit / Withdraw / Transfer Sent / Transfer Received)
- `amount`
- `balance_after` (snapshot of balance right after this transaction — makes
  the history page trivial to render, and gives you an audit trail even if
  `balance` were ever wrong)
- `reference` — a shared ID that links the two rows created during a
  transfer (one "TRANSFER_OUT" on the sender's account, one "TRANSFER_IN"
  on the receiver's), so you can trace both halves of a transfer.

## How to explain this in an interview

**"Walk me through what happens when a user deposits money."**
> The user submits the deposit form → Django validates the amount server-side
> using a Form class → inside a `db_transaction.atomic()` block, I increase
> the account's balance AND create a Transaction record. Wrapping both in
> `atomic()` means if either write fails, both are rolled back — the balance
> and the ledger can never drift out of sync.

**"How does a transfer work between two different users?"**
> A transfer touches two Account rows at once, so I do the whole thing inside
> one atomic transaction: debit the sender, create a `TRANSFER_OUT`
> transaction, credit the receiver, create a `TRANSFER_IN` transaction. Both
> transaction rows share the same `reference` UUID so they're traceable as
> one logical event even though they live on two different accounts.

**"How do you prevent someone from withdrawing more money than they have?"**
> Before touching the database, I compare the requested amount to
> `account.balance` in the view and reject it with an error message if it's
> too high. That check happens server-side, not just in the browser, so it
> can't be bypassed.

**"Why did you use Django's built-in User model instead of building your own auth?"**
> Rolling your own authentication (password hashing, sessions, login
> throttling) is a well-known source of security bugs. Django's `auth` app is
> battle-tested, so I extended it with a one-to-one `Account` model instead
> of reinventing user management.

**"What would you add to make this production-ready?"**
> - Database-level row locking (`select_for_update()`) on the accounts during
>   transfers, to prevent race conditions if two requests hit at once
> - Two-factor authentication and stronger password policies
> - Rate limiting on login/transfer endpoints
> - Proper decimal/currency handling and multi-currency support
> - A real audit/compliance log separate from the user-facing history
> - API layer (Django REST Framework) if a mobile app needed to consume it
> - Automated tests (pytest / Django TestCase) for every view

## Key Django concepts this project demonstrates

- Models & relationships (`OneToOneField`, `ForeignKey`)
- Django Forms & server-side validation
- Authentication (`login_required`, Django's auth views)
- Database transactions (`transaction.atomic()`) for data integrity
- Django Admin customization
- Template inheritance (`base.html` + `{% block %}`)
- Django messages framework (success/error banners)
