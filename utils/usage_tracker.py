import json
from pathlib import Path
from datetime import datetime, timezone

FREE_TIER_LIMIT = 5


class UsageTracker:
    """
    Tracks per-user analysis counts for the free tier.

    IMPORTANT: upgrade_to_pro() does NOT process any payment. It only flips
    a local flag so the rest of the UI can be built and tested. Do not treat
    'is_pro' as proof of payment until this is wired to real Stripe webhook
    verification — a user could otherwise call upgrade_to_pro() themselves
    and get Pro access for free. Gate the actual call site, not just this
    file, once Stripe is integrated.
    """

    def __init__(self, store_path='data/usage.json'):
        self.store_path = Path(store_path)
        self.store_path.parent.mkdir(exist_ok=True)
        self._load()

    def _load(self):
        if self.store_path.exists():
            with open(self.store_path, 'r') as f:
                self._data = json.load(f)
        else:
            self._data = {}

    def _save(self):
        with open(self.store_path, 'w') as f:
            json.dump(self._data, f, indent=2)

    def _ensure_user(self, user_id):
        if user_id not in self._data:
            self._data[user_id] = {
                'analyses_used': 0,
                'is_pro': False,
                'first_seen': datetime.now(timezone.utc).isoformat(),
            }

    def get_user_usage(self, user_id):
        self._ensure_user(user_id)
        return self._data[user_id]

    def get_remaining_analyses(self, user_id):
        usage = self.get_user_usage(user_id)
        if usage.get('is_pro'):
            return None  # unlimited
        return max(0, FREE_TIER_LIMIT - usage.get('analyses_used', 0))

    def record_analysis(self, user_id):
        """Call this every time a user actually runs an analysis (EDA,
        modeling, NLP query, etc.) so the free-tier count is real, not
        just a number on the pricing page."""
        self._ensure_user(user_id)
        usage = self._data[user_id]
        if not usage.get('is_pro'):
            usage['analyses_used'] = usage.get('analyses_used', 0) + 1
        self._save()
        return self.get_remaining_analyses(user_id)

    def can_run_analysis(self, user_id):
        remaining = self.get_remaining_analyses(user_id)
        return remaining is None or remaining > 0

    def upgrade_to_pro(self, user_id):
        # See class docstring: this is a placeholder until Stripe is wired
        # up. Do not call this directly from a button click in production.
        self._ensure_user(user_id)
        self._data[user_id]['is_pro'] = True
        self._save()
