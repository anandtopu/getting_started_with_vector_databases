"""Authenticated flagship UI: products, help, related items, review and photos.
Run: uv run --extra apps streamlit run capstones/05_marlowe_search/solution/ui.py
Expected: token-gated seller forms. CPU: seconds; run the flagship HTTPS API first.
"""

from playground.secure_market import main

if __name__ == "__main__":
    main()
